# SPDX-License-Identifier: Apache-2.0
"""ADR-0127: local speech-to-text behind a small port; the first provider is whisper.cpp.

The transcript is text for the player to review (REQ-VOICE-002), never a command.
"""
from __future__ import annotations

import re
import shutil
import subprocess
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
