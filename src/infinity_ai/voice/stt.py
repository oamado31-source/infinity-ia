# SPDX-License-Identifier: Apache-2.0
"""ADR-0127: local speech-to-text behind a small port; the first provider is whisper.cpp.

The transcript is text for the player to review (REQ-VOICE-002), never a command.
"""
from __future__ import annotations

import json
import re
import shutil
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

MAX_PROMPT_CHARS = 400
# Whisper marks for non-speech ("[Música]", "(risos)", "♪") and video-subtitle phrases it invents
# on noise. "Obrigado" is not here: a player may say it; silence is caught by the audio level.
_MARKS = re.compile(r'\[[^\]]*\]|\([^)]*\)|[♪♫*]+')
_SUBTITLE_HALLUCINATIONS = re.compile(
    r'legendas? (?:pela|por) comunidade|amara\.org|inscreva-se no canal|'
    r'obrigado por assistir|até o próximo vídeo', re.I)


class SttError(RuntimeError):
    """The STT failed or heard nothing usable."""


class SttProvider(Protocol):
    name: str

    def transcribe(self, wav: Path, *, prompt: str = '') -> str:
        ...


def clean_transcript(raw: str) -> str:
    """One line of what was said, without Whisper's marks; '' when nothing usable remains."""
    text = _MARKS.sub(' ', raw or '')
    text = ' '.join(text.split()).strip(' -')
    if _SUBTITLE_HALLUCINATIONS.search(text) or not re.search(r'[A-Za-zÀ-ÿ]', text):
        return ''
    return text


def vocabulary_prompt(names: Iterable[str]) -> str:
    """Proper names that bias the STT toward the right spelling ("Athkatla", "Lehtinan")."""
    seen: list[str] = []
    for n in names:
        n = ' '.join(str(n).split())
        if n and n not in seen:
            seen.append(n)
    out = ''
    for n in seen:
        piece = (', ' if out else '') + n
        if len(out) + len(piece) > MAX_PROMPT_CHARS:
            break
        out += piece
    return out + '.' if out else ''


class WhisperCppStt:
    """`whisper-cli` (whisper.cpp) on a 16 kHz mono WAV, Portuguese, no timestamps."""

    def __init__(self, model: Path, *, binary: str = 'whisper-cli', language: str = 'pt',
                 timeout_s: float = 60.0, threads: int = 4) -> None:
        self.model = Path(model).expanduser()
        self.binary = shutil.which(binary) or binary
        self.language, self.timeout_s, self.threads = language, timeout_s, threads
        self.name = f'whisper.cpp:{self.model.name}'

    def command(self, wav: Path, prompt: str = '') -> list[str]:
        cmd = [self.binary, '-m', str(self.model), '-l', self.language, '-nt', '-np',
               '-t', str(self.threads), '-f', str(wav)]
        if prompt:
            cmd += ['--prompt', prompt]
        return cmd

    def transcribe(self, wav: Path, *, prompt: str = '') -> str:
        if not self.model.is_file():
            raise SttError(f'model not found: {self.model}')
        try:
            done = subprocess.run(self.command(wav, prompt), capture_output=True, text=True,
                                  timeout=self.timeout_s)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SttError(f'whisper-cli failed: {type(exc).__name__}') from exc
        if done.returncode != 0:
            raise SttError(f'whisper-cli exit {done.returncode}')
        return clean_transcript(done.stdout)


def multipart(fields: dict[str, str], file_field: str, wav: Path) -> tuple[bytes, str]:
    """multipart/form-data body (standard library only) with one WAV file."""
    boundary = uuid.uuid4().hex
    out = bytearray()
    for name, value in fields.items():
        out += (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'
                f'{value}\r\n').encode('utf-8')
    out += (f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; '
            f'filename="ptt.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode('ascii')
    out += wav.read_bytes() + f'\r\n--{boundary}--\r\n'.encode('ascii')
    return bytes(out), f'multipart/form-data; boundary={boundary}'


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class WhisperServerStt:
    """S1i latency: `whisper-server` (whisper.cpp) kept running on a loopback port with the model
    loaded, so a press does not pay the model load of `whisper-cli` (~0.95 s -> ~0.5 s for a short
    phrase). Same model, language and vocabulary prompt. Started on first use; when it cannot
    start or answer, the press falls back to `whisper-cli` and the server is tried again later."""

    def __init__(self, model: Path, *, binary: str = 'whisper-server', language: str = 'pt',
                 timeout_s: float = 60.0, threads: int = 4,
                 fallback: SttProvider | None = None) -> None:
        self.model = Path(model).expanduser()
        self.binary = shutil.which(binary) or binary
        self.language, self.timeout_s, self.threads = language, timeout_s, threads
        self.fallback = fallback or WhisperCppStt(model, language=language, timeout_s=timeout_s,
                                                  threads=threads)
        self.name = f'whisper.cpp-server:{self.model.name}'
        self._proc: subprocess.Popen | None = None
        self._url = ''
        self._lock = threading.Lock()

    def command(self, port: int) -> list[str]:
        return [self.binary, '-m', str(self.model), '-l', self.language, '-nt',
                '-t', str(self.threads), '--host', '127.0.0.1', '--port', str(port)]

    def start(self, wait_s: float = 30.0) -> bool:
        """Start the server (if needed) and wait until it answers. True when it is up."""
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                return True
            if not self.model.is_file():
                return False
            port = _free_port()
            try:
                self._proc = subprocess.Popen(self.command(port), stdin=subprocess.DEVNULL,
                                              stdout=subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)
            except OSError:
                self._proc = None
                return False
            self._url = f'http://127.0.0.1:{port}'
            end = time.monotonic() + wait_s
            while time.monotonic() < end and self._proc.poll() is None:
                try:
                    with urllib.request.urlopen(self._url + '/', timeout=1):
                        return True
                except OSError:
                    time.sleep(0.2)
            self.stop()
            return False

    def stop(self) -> None:
        proc, self._proc = self._proc, None
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()

    def transcribe(self, wav: Path, *, prompt: str = '') -> str:
        if not self.start():
            return self.fallback.transcribe(wav, prompt=prompt)
        fields = {'response_format': 'json', 'temperature': '0.0'}
        if prompt:
            fields['prompt'] = prompt
        body, kind = multipart(fields, 'file', wav)
        request = urllib.request.Request(self._url + '/inference', data=body,
                                         headers={'Content-Type': kind})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                text = json.loads(response.read().decode('utf-8')).get('text')
        except (OSError, ValueError, urllib.error.URLError):
            self.stop()                        # started again on the next press
            return self.fallback.transcribe(wav, prompt=prompt)
        if not isinstance(text, str):
            raise SttError('whisper-server returned no text')
        return clean_transcript(text)


class FakeStt:
    """For tests: returns the given transcripts in order (an Exception instance is raised)."""

    name = 'fake'

    def __init__(self, outputs: Iterable[str | Exception]) -> None:
        self.outputs = list(outputs)
        self.calls: list[tuple[Path, str]] = []

    def transcribe(self, wav: Path, *, prompt: str = '') -> str:
        self.calls.append((wav, prompt))
        out = self.outputs.pop(0)
        if isinstance(out, Exception):
            raise out
        return clean_transcript(out)
