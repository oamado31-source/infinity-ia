# SPDX-License-Identifier: Apache-2.0
"""ADR-0127: microphone capture on the host of the dialogue service, only between START and STOP.

`FfmpegRecorder` runs ffmpeg (AVFoundation on macOS) in a subprocess, writing 16 kHz mono WAV into
a private temporary directory. Nothing is recorded at rest (ADR-0107 item 4): the microphone opens
on `start()` and closes on `stop()`/`cancel()`, and the caller deletes the file after the STT.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import wave
from array import array
from pathlib import Path
from typing import Protocol

_DEVICE_LINE = re.compile(r'\[(\d+)\]\s+(.+?)\s*$')
_BUILT_IN = ('macbook', 'built-in', 'interno', 'embutido')


class CaptureError(RuntimeError):
    """The microphone could not be opened or the recording failed."""


class Recorder(Protocol):
    def start(self) -> None:
        """Open the microphone and start recording."""
        ...

    def stop(self) -> Path:
        """Close the microphone; return the recorded WAV (the caller deletes it)."""
        ...

    def cancel(self) -> None:
        """Close the microphone and delete whatever was recorded."""
        ...


def audio_devices(listing: str) -> list[tuple[int, str]]:
    """(index, name) of the audio inputs in `ffmpeg -f avfoundation -list_devices true` output."""
    out, in_audio = [], False
    for line in listing.splitlines():
        if 'audio devices' in line.lower():
            in_audio = True
            continue
        if 'video devices' in line.lower():
            in_audio = False
            continue
        m = _DEVICE_LINE.search(line) if in_audio else None
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out


def resolve_device(devices: list[tuple[int, str]], wanted: str | None) -> int:
    """The index to record from: `wanted` as an index or part of a name, else the built-in mic.

    Index 0 is not a safe default: on a Mac it may be an iPhone microphone (Continuity)."""
    if not devices:
        raise CaptureError('no audio input device')
    if wanted is not None and wanted.strip():
        w = wanted.strip()
        if w.isdigit() and any(i == int(w) for i, _ in devices):
            return int(w)
        for i, name in devices:
            if w.lower() in name.lower():
                return i
        raise CaptureError(f'audio input not found: {wanted}')
    for i, name in devices:
        if any(k in name.lower() for k in _BUILT_IN):
            return i
    return devices[0][0]


class FfmpegRecorder:
    def __init__(self, *, device: str | None = None, max_seconds: float = 20.0,
                 ffmpeg: str = 'ffmpeg') -> None:
        self.ffmpeg = shutil.which(ffmpeg) or ffmpeg
        self.wanted = device
        self.max_seconds = max_seconds
        self._proc: subprocess.Popen | None = None
        self._dir: str | None = None
        self._path: Path | None = None

    def device_index(self) -> int:
        listing = subprocess.run([self.ffmpeg, '-hide_banner', '-f', 'avfoundation',
                                  '-list_devices', 'true', '-i', ''],
                                 capture_output=True, text=True, timeout=15)
        return resolve_device(audio_devices(listing.stderr + listing.stdout), self.wanted)

    def command(self, index: int, path: Path) -> list[str]:
        # No -nostdin: "q" on stdin is how stop() ends the recording cleanly.
        return [self.ffmpeg, '-hide_banner', '-loglevel', 'error', '-y',
                '-f', 'avfoundation', '-i', f':{index}', '-t', f'{self.max_seconds:g}',
                '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', str(path)]

    def start(self) -> None:
        if self._proc is not None:
            raise CaptureError('already recording')
        index = self.device_index()
        self._dir = tempfile.mkdtemp(prefix='infai-voice-')
        os.chmod(self._dir, 0o700)
        self._path = Path(self._dir) / 'ptt.wav'
        try:
            self._proc = subprocess.Popen(self.command(index, self._path), stdin=subprocess.PIPE,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except OSError as exc:
            self._cleanup()
            raise CaptureError(f'ffmpeg failed to start: {exc}') from exc

    def _finish(self) -> None:
        proc, self._proc = self._proc, None
        if proc is None:
            return
        try:
            if proc.poll() is None:
                proc.communicate(b'q', timeout=5)      # ffmpeg closes the file cleanly on "q"
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
        except (BrokenPipeError, ValueError):
            proc.wait(timeout=5)

    def stop(self) -> Path:
        self._finish()
        path = self._path
        if path is None or not path.exists() or path.stat().st_size <= 44:
            self._cleanup()
            raise CaptureError('nothing was recorded (microphone permission?)')
        return path

    def cancel(self) -> None:
        self._finish()
        self._cleanup()

    def _cleanup(self) -> None:
        if self._dir:
            shutil.rmtree(self._dir, ignore_errors=True)
        self._dir, self._path = None, None


def discard(path: Path | None) -> None:
    """Delete a recording and its private directory (after the STT, in every outcome)."""
    if path is None:
        return
    parent = path.parent
    path.unlink(missing_ok=True)
    if parent.name.startswith('infai-voice-'):
        shutil.rmtree(parent, ignore_errors=True)


def speech_level(path: Path) -> float:
    """RMS of a 16-bit mono WAV (0..32767). Below a threshold it is silence: no STT is run, so
    Whisper cannot invent words on it."""
    with wave.open(str(path), 'rb') as w:
        if w.getsampwidth() != 2:
            raise CaptureError('expected 16-bit audio')
        frames = w.readframes(w.getnframes())
    samples = array('h')
    samples.frombytes(frames[:len(frames) - len(frames) % 2])
    if not samples:
        return 0.0
    return (sum(s * s for s in samples) / len(samples)) ** 0.5
