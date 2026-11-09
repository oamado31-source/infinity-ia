# SPDX-License-Identifier: Apache-2.0
"""Read-only access to a local game install (REQ-CANON-004: reference, never copy into the repo).

Paths are relative to the game root with '/' separators. Implementations only read; nothing here
can write to the install.
"""
from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


class GameDataError(ValueError):
    """Unexpected or unsupported game file content."""


class ByteSource(Protocol):
    def size(self, path: str) -> int | None:
        """File size in bytes, or None if the file does not exist."""
        ...

    def read(self, path: str, offset: int, length: int) -> bytes: ...

    def read_many(self, requests: Sequence[tuple[str, int, int]]) -> list[bytes]: ...

    def list_dir(self, path: str, suffix: str) -> list[str]:
        """File names (not paths) in a directory ending with `suffix` (case-insensitive)."""
        ...


class FileSystemSource:
    """For running on the machine that holds the install (and for tests)."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)

    def _path(self, path: str) -> Path:
        rel = Path(*[p for p in path.replace('\\', '/').split('/') if p not in ('', '.')])
        if '..' in rel.parts:
            raise GameDataError(f'path escapes the game root: {path!r}')
        direct = self._root / rel
        if direct.exists():
            return direct
        # Windows installs are case-insensitive; match each component case-insensitively.
        current = self._root
        for part in rel.parts:
            matches = [c for c in current.iterdir() if c.name.lower() == part.lower()] \
                if current.is_dir() else []
            if not matches:
                return direct
            current = matches[0]
        return current

    def size(self, path: str) -> int | None:
        p = self._path(path)
        return p.stat().st_size if p.is_file() else None

    def read(self, path: str, offset: int, length: int) -> bytes:
        if offset < 0 or length < 0:
            raise GameDataError('negative offset or length')
        with self._path(path).open('rb') as fh:
            fh.seek(offset)
            data = fh.read(length)
        if len(data) != length:
            raise GameDataError(f'short read in {path} at {offset}+{length}')
        return data

    def read_many(self, requests: Sequence[tuple[str, int, int]]) -> list[bytes]:
        return [self.read(p, o, n) for p, o, n in requests]

    def list_dir(self, path: str, suffix: str) -> list[str]:
        d = self._path(path)
        if not d.is_dir():
            return []
        return sorted(n for n in os.listdir(d) if n.lower().endswith(suffix.lower()))
