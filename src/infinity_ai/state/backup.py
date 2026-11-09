# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 / ADR-0110: consistent backups of a campaign database and a restore check."""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .store import CampaignStore

TABLES = ('campaigns', 'branches', 'events', 'npc_experiences', 'belief_revisions',
          'belief_revision_sources')


@dataclass(frozen=True)
class BackupInfo:
    path: Path
    sha256: str
    last_seq: int
    counts: dict[str, int]


@dataclass(frozen=True)
class RestoreCheck:
    ok: bool
    integrity: str
    problems: tuple[str, ...]


def _snapshot(conn: sqlite3.Connection) -> tuple[int, dict[str, int]]:
    last_seq = conn.execute('SELECT COALESCE(MAX(seq), 0) FROM events').fetchone()[0]
    counts = {t: conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in TABLES}
    return last_seq, counts


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def backup(store: CampaignStore, dest_dir: str | Path) -> BackupInfo:
    """Online backup with sqlite3's backup API (consistent even while the store is open)."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = dest_dir / f'{store.campaign_id}-{stamp}.sqlite3'
    if path.exists():
        raise FileExistsError(path)
    target = sqlite3.connect(str(path))
    try:
        store.connection.backup(target)
        last_seq, counts = _snapshot(target)  # describe the copy itself, not the live database
    finally:
        target.close()
    return BackupInfo(path, _sha256(path), last_seq, counts)


def verify_restore(info: BackupInfo) -> RestoreCheck:
    """Open the backup read-only and check integrity, hash, counts and last event sequence."""
    problems: list[str] = []
    if _sha256(info.path) != info.sha256:
        problems.append('sha256 differs')
    conn = sqlite3.connect(f'file:{info.path}?mode=ro', uri=True)
    try:
        integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
        last_seq, counts = _snapshot(conn)
    finally:
        conn.close()
    if integrity != 'ok':
        problems.append(f'integrity_check: {integrity}')
    if last_seq != info.last_seq:
        problems.append(f'last_seq {last_seq} != {info.last_seq}')
    if counts != info.counts:
        problems.append(f'counts {counts} != {info.counts}')
    return RestoreCheck(not problems, integrity, tuple(problems))
