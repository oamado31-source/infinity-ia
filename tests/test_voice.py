# SPDX-License-Identifier: Apache-2.0
"""ADR-0127: push-to-talk session, capture helpers and STT wrapper (synthetic; no microphone)."""
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.voice.capture import (  # noqa: E402
    CaptureError, audio_devices, resolve_device, speech_level,
)
from infinity_ai.voice.session import (  # noqa: E402
    CANCEL, CANCELLED, FAILED, REC, START, STOP, TEXT, VoiceSession,
)
from infinity_ai.voice.stt import (  # noqa: E402
    FakeStt, SttError, WhisperCppStt, clean_transcript, vocabulary_prompt,
)

TURBO = Path('~/.infinity-ai/models/ggml-large-v3-turbo-q5_0.bin').expanduser()


def write_wav(path: Path, amplitude: int, seconds: float = 0.5) -> Path:
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        n = int(16000 * seconds)
        w.writeframes(b''.join(struct.pack('<h', int(amplitude * math.sin(i / 8)))
                               for i in range(n)))
    return path


class FakeRecorder:
    opened = 0

    def __init__(self, folder: Path, amplitude: int = 3000, fail: bool = False) -> None:
        self.folder, self.amplitude, self.fail = folder, amplitude, fail
        self.path: Path | None = None
        self.cancelled = False

    def start(self) -> None:
        if self.fail:
            raise CaptureError('no permission')
        FakeRecorder.opened += 1
        self.path = write_wav(self.folder / f'rec{FakeRecorder.opened}.wav', self.amplitude)

    def stop(self) -> Path:
        return self.path

    def cancel(self) -> None:
        self.cancelled = True
        if self.path:
            self.path.unlink(missing_ok=True)


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class SessionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.recorders: list[FakeRecorder] = []
        FakeRecorder.opened = 0
        self.clock = Clock()

    def session(self, outputs=('Quem governa Amn?',), amplitude=3000, fail=False):
        def factory():
            r = FakeRecorder(self.folder, amplitude, fail)
            self.recorders.append(r)
            return r
        self.stt = FakeStt(list(outputs))
        return VoiceSession(factory, self.stt, max_seconds=20, clock=self.clock,
                            prompt=lambda: 'Amn, Athkatla.')

    def test_press_record_stop_gives_text_and_deletes_the_audio(self):
        s = self.session()
        self.assertEqual(FakeRecorder.opened, 0)               # REQ-VOICE-001: closed until START
        self.assertEqual([u.state for u in s.handle('p1', START)], [REC])
        self.clock.now = 2.5
        (done,) = s.handle('p1', STOP)
        self.assertEqual((done.state, done.text), (TEXT, 'Quem governa Amn?'))
        self.assertAlmostEqual(done.audio_s, 2.5)
        self.assertEqual(self.stt.calls[0][1], 'Amn, Athkatla.')
        self.assertFalse(self.recorders[0].path.exists())
        self.assertNotIn('Quem', done.summary())               # the log has no transcript
        self.assertEqual(s.handle('p1', STOP), [])              # a repeated STOP changes nothing
        self.assertEqual(s.handle('p1', START), [])             # nor a late repeat of the press

    def test_stop_or_cancel_without_a_press_does_nothing(self):
        s = self.session()
        self.assertEqual(s.handle('p1', STOP) + s.handle('p1', CANCEL) + s.handle('x', 'OPEN'),
                         [])
        self.assertEqual(FakeRecorder.opened, 0)

    def test_cancel_discards_the_recording(self):
        s = self.session()
        s.handle('p1', START)
        (u,) = s.handle('p1', CANCEL)
        self.assertEqual(u.state, CANCELLED)
        self.assertTrue(self.recorders[0].cancelled)
        self.assertEqual(self.stt.calls, [])

    def test_a_new_press_replaces_an_unfinished_one(self):
        s = self.session()
        s.handle('p1', START)
        states = [u.state for u in s.handle('p2', START)]
        self.assertEqual(states, [CANCELLED, REC])
        self.assertEqual(s.handle('p1', STOP), [])
        self.assertEqual(s.handle('p2', STOP)[0].state, TEXT)

    def test_time_limit_stops_by_itself(self):
        s = self.session()
        s.handle('p1', START)
        self.clock.now = 19.9
        self.assertEqual(s.tick(), [])
        self.clock.now = 20.0
        (u,) = s.tick()
        self.assertEqual((u.state, u.reason), (TEXT, 'LIMIT'))
        self.assertFalse(s.recording)

    def test_failures_are_reported_and_audio_is_still_deleted(self):
        cases = (('MIC', dict(fail=True)), ('SILENCE', dict(amplitude=20)),
                 ('EMPTY', dict(outputs=('[Música]',))), ('STT', dict(outputs=(SttError('x'),))))
        for reason, kw in cases:
            with self.subTest(reason=reason):
                self.recorders.clear()
                s = self.session(**kw)
                updates = s.handle(f'p-{reason}', START) + s.handle(f'p-{reason}', STOP)
                self.assertEqual((updates[-1].state, updates[-1].reason), (FAILED, reason))
                for r in self.recorders:
                    self.assertTrue(r.path is None or not r.path.exists())
                self.assertFalse(s.recording)


class HelperTests(unittest.TestCase):
    LISTING = '''[AVFoundation indev @ 0x1] AVFoundation video devices:
[AVFoundation indev @ 0x1] [0] FaceTime HD Camera
[AVFoundation indev @ 0x1] AVFoundation audio devices:
[AVFoundation indev @ 0x1] [0] Microfone do iPhone
[AVFoundation indev @ 0x1] [1] Microfone (MacBook Pro)
[AVFoundation indev @ 0x1] [2] krisp microphone'''

    def test_device_choice_prefers_the_built_in_microphone(self):
        devices = audio_devices(self.LISTING)
        self.assertEqual(devices, [(0, 'Microfone do iPhone'), (1, 'Microfone (MacBook Pro)'),
                                   (2, 'krisp microphone')])
        self.assertEqual(resolve_device(devices, None), 1)
        self.assertEqual(resolve_device(devices, '2'), 2)
        self.assertEqual(resolve_device(devices, 'krisp'), 2)
        with self.assertRaises(CaptureError):
            resolve_device(devices, 'USB')
        with self.assertRaises(CaptureError):
            resolve_device([], None)

    def test_speech_level_separates_silence(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertLess(speech_level(write_wav(Path(d) / 'a.wav', 20)), 150)
            self.assertGreater(speech_level(write_wav(Path(d) / 'b.wav', 3000)), 1000)

    def test_clean_transcript(self):
        self.assertEqual(clean_transcript(' Quem governa Amn? \n'), 'Quem governa Amn?')
        self.assertEqual(clean_transcript('[Música] Olá (risos) ♪'), 'Olá')
        self.assertEqual(clean_transcript('Obrigado.'), 'Obrigado.')    # a player may say it
        for junk in ('[Música]', '...', '', 'Legendas pela comunidade Amara.org'):
            with self.subTest(junk=junk):
                self.assertEqual(clean_transcript(junk), '')

    def test_vocabulary_prompt(self):
        self.assertEqual(vocabulary_prompt(['Amn', 'Athkatla', 'Amn', ' Coroa  de Cobre ']),
                         'Amn, Athkatla, Coroa de Cobre.')
        self.assertEqual(vocabulary_prompt([]), '')
        self.assertLessEqual(len(vocabulary_prompt(['Nome%d' % i for i in range(200)])), 401)

    def test_whisper_command(self):
        stt = WhisperCppStt(Path('/m/ggml.bin'), binary='/bin/whisper-cli')
        self.assertEqual(stt.command(Path('/t/a.wav'), 'Amn.'),
                         ['/bin/whisper-cli', '-m', '/m/ggml.bin', '-l', 'pt', '-nt', '-np',
                          '-t', '4', '-f', '/t/a.wav', '--prompt', 'Amn.'])
        self.assertNotIn('--prompt', stt.command(Path('/t/a.wav')))
        with self.assertRaises(SttError):
            stt.transcribe(Path('/t/a.wav'))                  # model missing


@unittest.skipUnless(shutil.which('whisper-cli') and shutil.which('say') and TURBO.is_file()
                     and shutil.which('ffmpeg'), 'whisper-cli, say, ffmpeg or model missing')
class WhisperSmokeTests(unittest.TestCase):
    def test_a_synthetic_phrase_is_transcribed(self):
        with tempfile.TemporaryDirectory() as d:
            aiff, wav = Path(d) / 'q.aiff', Path(d) / 'q.wav'
            subprocess.run(['say', '-v', 'Luciana', '-o', str(aiff), 'Quem governa Amn?'],
                           check=True)
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(aiff),
                            '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', str(wav)], check=True)
            text = WhisperCppStt(TURBO).transcribe(wav, prompt=vocabulary_prompt(['Amn']))
        self.assertIn('governa', text.lower())   # how a synthetic voice says "Amn" varies


if __name__ == '__main__':
    unittest.main()
