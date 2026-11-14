# SPDX-License-Identifier: Apache-2.0
"""ADR-0127: one push-to-talk exchange, driven by the box's START/STOP/CANCEL signals.

IDLE -> REC -> (TRANSCRIBING) -> TEXT | FAILED, or CANCELLED. The microphone opens only on START
(REQ-VOICE-001); the recording is deleted in every outcome; the transcript is text to review
(REQ-VOICE-002). Pure logic over a `Recorder` and an `SttProvider`, so it is tested with fakes.
"""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .capture import CaptureError, Recorder, discard, speech_level
from .stt import SttError, SttProvider

START, STOP, CANCEL = 'START', 'STOP', 'CANCEL'
ACTIONS = (START, STOP, CANCEL)
REC, TEXT, FAILED, CANCELLED = 'REC', 'TEXT', 'FAILED', 'CANCELLED'
DEFAULT_MIN_LEVEL = 150.0     # RMS of 16-bit audio; quiet room noise stays below (tuned in the lab)


@dataclass(frozen=True)
class VoiceUpdate:
    """What the box must show for `ptt_id`; `text` only with TEXT. Logged without the text."""
    ptt_id: str
    state: str
    text: str = ''
    reason: str = ''
    audio_s: float = 0.0
    stt_s: float = 0.0
    level: float = 0.0

    def summary(self) -> str:
        return (f'ptt={self.ptt_id} estado={self.state} motivo={self.reason or "-"} '
                f'duracao={self.audio_s:.1f}s stt={self.stt_s:.1f}s nivel={self.level:.0f} '
                f'chars={len(self.text)}')


class VoiceSession:
    def __init__(self, recorder_factory: Callable[[], Recorder], stt: SttProvider, *,
                 max_seconds: float = 20.0, min_level: float = DEFAULT_MIN_LEVEL,
                 prompt: Callable[[], str] = lambda: '',
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.recorder_factory, self.stt = recorder_factory, stt
        self.max_seconds, self.min_level = max_seconds, min_level
        self.prompt, self.clock = prompt, clock
        self.ptt_id: str | None = None
        self._recorder: Recorder | None = None
        self._started = 0.0
        self.done: set[str] = set()      # ids already finished: a late repeat changes nothing

    @property
    def recording(self) -> bool:
        return self._recorder is not None

    def handle(self, ptt_id: str, action: str) -> list[VoiceUpdate]:
        if action not in ACTIONS or not ptt_id or ptt_id in self.done:
            return []
        out: list[VoiceUpdate] = []
        if action == START:
            if self.ptt_id == ptt_id:
                return []                              # the same press seen twice
            if self.recording:                         # a new press replaces an unfinished one
                out.append(self._cancel())
            return out + [self._start(ptt_id)]
        if ptt_id != self.ptt_id or not self.recording:
            return []
        return [self._stop()] if action == STOP else [self._cancel()]

    def tick(self) -> list[VoiceUpdate]:
        """Stop by itself at the time limit (the box may never send STOP)."""
        if self.recording and self.clock() - self._started >= self.max_seconds:
            return [self._stop(reason='LIMIT')]
        return []

    def _start(self, ptt_id: str) -> VoiceUpdate:
        self.ptt_id = ptt_id
        recorder = self.recorder_factory()
        try:
            recorder.start()
        except CaptureError:
            self._finish()
            return VoiceUpdate(ptt_id, FAILED, reason='MIC')
        self._recorder, self._started = recorder, self.clock()
        return VoiceUpdate(ptt_id, REC)

    def _cancel(self) -> VoiceUpdate:
        ptt_id, recorder = self.ptt_id or '', self._recorder
        if recorder is not None:
            recorder.cancel()
        self._finish()
        return VoiceUpdate(ptt_id, CANCELLED)

    def _stop(self, reason: str = '') -> VoiceUpdate:
        ptt_id, recorder = self.ptt_id or '', self._recorder
        audio_s = self.clock() - self._started
        wav: Path | None = None
        try:
            wav = recorder.stop()
            level = speech_level(wav)
            if level < self.min_level:
                return VoiceUpdate(ptt_id, FAILED, reason='SILENCE', audio_s=audio_s, level=level)
            began = self.clock()
            text = self.stt.transcribe(wav, prompt=self.prompt())
            stt_s = self.clock() - began
            if not text:
                return VoiceUpdate(ptt_id, FAILED, reason='EMPTY', audio_s=audio_s, stt_s=stt_s,
                                   level=level)
            return VoiceUpdate(ptt_id, TEXT, text, reason, audio_s, stt_s, level)
        except CaptureError:
            return VoiceUpdate(ptt_id, FAILED, reason='MIC', audio_s=audio_s)
        except SttError:
            return VoiceUpdate(ptt_id, FAILED, reason='STT', audio_s=audio_s)
        finally:
            discard(wav)
            self._finish()

    def _finish(self) -> None:
        if self.ptt_id:
            self.done.add(self.ptt_id)
        self._recorder, self.ptt_id = None, None
