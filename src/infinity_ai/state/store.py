# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 campaign store: SQLite (stdlib), versioned migrations, append-only event log, branches.

One database file per campaign (Constitution item 5: campaigns never mix). Rows are never updated
or deleted (SQL triggers enforce it). A save restore creates a child branch; what the child sees of
its ancestors is bounded by the fork point (sequence and game time), so old history stays intact
and simply stops being part of the new timeline.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MIGRATIONS_DIR = Path(__file__).resolve().parent / 'migrations'
ROOT_BRANCH = 'main'
CATEGORIES = frozenset({'CAMPAIGN_OBSERVATION', 'CAMPAIGN_FACT', 'RECONCILIATION'})
EVIDENCE = frozenset({'SYNTHETIC', 'LAB_OBSERVED', 'POC_VERIFIED'})


class StoreError(RuntimeError):
    pass


class IdempotencyConflict(StoreError):
    """Same idempotency key, different content: never silently accepted."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


@dataclass(frozen=True)
class Event:
    seq: int
    event_id: str
    idempotency_key: str
    campaign_id: str
    branch_id: str
    host_epoch: int
    event_type: str
    category: str
    game_time: int | None
    payload: dict[str, Any]
    evidence: str
    source_observation_id: str | None
    recorded_at: str


@dataclass(frozen=True)
class LineageStep:
    """Events of `branch_id` are visible when seq <= max_seq and game_time <= max_game_time."""
    branch_id: str
    max_seq: int | None
    max_game_time: int | None

    def admits(self, seq: int, game_time: int | None) -> bool:
        if self.max_seq is not None and seq > self.max_seq:
            return False
        if self.max_game_time is not None and game_time is not None \
                and game_time > self.max_game_time:
            return False
        return True


_INSERT_COLUMNS = ('event_id, idempotency_key, campaign_id, branch_id, host_epoch, event_type, '
                   'category, game_time, payload_json, evidence, source_observation_id, recorded_at')
_EVENT_COLUMNS = 'seq, ' + _INSERT_COLUMNS


def _row_to_event(row: tuple) -> Event:
    return Event(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                 json.loads(row[9]), row[10], row[11], row[12])


def _migrate(conn: sqlite3.Connection, clock: Callable[[], str]) -> None:
    conn.execute('CREATE TABLE IF NOT EXISTS schema_migrations ('
                 'version INTEGER PRIMARY KEY, name TEXT NOT NULL, sha256 TEXT NOT NULL, '
                 'applied_at TEXT NOT NULL)')
    applied = {v: (n, h) for v, n, h in
               conn.execute('SELECT version, name, sha256 FROM schema_migrations')}
    for path in sorted(MIGRATIONS_DIR.glob('[0-9][0-9][0-9][0-9]_*.sql')):
        version = int(path.name[:4])
        sql = path.read_text(encoding='utf-8')
        digest = hashlib.sha256(sql.encode('utf-8')).hexdigest()
        if version in applied:
            if applied[version][1] != digest:
                raise StoreError(f'migration {path.name} changed after being applied')
            continue
        conn.execute('BEGIN IMMEDIATE')
        try:
            for statement in _split_sql(sql):
                conn.execute(statement)
            conn.execute('INSERT INTO schema_migrations VALUES (?, ?, ?, ?)',
                         (version, path.name, digest, clock()))
            conn.execute('COMMIT')
        except BaseException:
            conn.execute('ROLLBACK')
            raise


def _split_sql(sql: str) -> list[str]:
    """Split on ';' at statement level, keeping trigger bodies (BEGIN ... END;) whole."""
    statements, buffer = [], ''
    for line in sql.splitlines(keepends=True):
        if line.strip().startswith('--') and not buffer.strip():
            continue
        buffer += line
        if sqlite3.complete_statement(buffer):
            if buffer.strip():
                statements.append(buffer.strip())
            buffer = ''
    if buffer.strip():
        raise StoreError('incomplete SQL statement in migration')
    return statements


class CampaignStore:
    def __init__(self, conn: sqlite3.Connection, campaign_id: str,
                 clock: Callable[[], str]) -> None:
        self._conn, self.campaign_id, self._clock = conn, campaign_id, clock

    @classmethod
    def open(cls, path: str | Path, campaign_id: str, *,
             clock: Callable[[], str] = _utc_now) -> CampaignStore:
        if not isinstance(campaign_id, str) or not campaign_id:
            raise ValueError('campaign_id required')
        conn = sqlite3.connect(str(path), isolation_level=None)
        try:
            conn.execute('PRAGMA foreign_keys = ON')
            _migrate(conn, clock)
        except BaseException:
            conn.close()
            raise
        rows = conn.execute('SELECT campaign_id FROM campaigns').fetchall()
        if not rows:
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('INSERT INTO campaigns VALUES (?, ?, ?)', (campaign_id, ROOT_BRANCH, clock()))
            conn.execute("INSERT INTO branches (branch_id, campaign_id, lineage, created_at) "
                         "VALUES (?, ?, 'ROOT', ?)", (ROOT_BRANCH, campaign_id, clock()))
            conn.execute('COMMIT')
        elif [r[0] for r in rows] != [campaign_id]:
            conn.close()
            raise StoreError('database belongs to another campaign')
        return cls(conn, campaign_id, clock)

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    def now(self) -> str:
        return self._clock()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> CampaignStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        self._conn.execute('BEGIN IMMEDIATE')
        try:
            yield self._conn
        except BaseException:
            self._conn.execute('ROLLBACK')
            raise
        self._conn.execute('COMMIT')

    # ---- branches -------------------------------------------------------------------------

    def branch_exists(self, branch_id: str) -> bool:
        return self._conn.execute('SELECT 1 FROM branches WHERE branch_id = ? AND campaign_id = ?',
                                  (branch_id, self.campaign_id)).fetchone() is not None

    def fork_branch(self, *, parent_branch_id: str, fork_game_time: int, fork_epoch: int) -> str:
        if not self.branch_exists(parent_branch_id):
            raise StoreError(f'unknown branch {parent_branch_id}')
        branch_id = 'br-' + uuid.uuid4().hex[:12]
        fork_seq = self._conn.execute('SELECT COALESCE(MAX(seq), 0) FROM events').fetchone()[0]
        self._conn.execute(
            'INSERT INTO branches (branch_id, campaign_id, parent_branch_id, fork_seq, '
            "fork_game_time, fork_epoch, lineage, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, 'INFERRED_FROM_ACTIVE', ?)",
            (branch_id, self.campaign_id, parent_branch_id, fork_seq, fork_game_time, fork_epoch,
             self._clock()))
        return branch_id

    def lineage(self, branch_id: str) -> list[LineageStep]:
        """The branch itself (unbounded) and each ancestor bounded by the tightest fork point."""
        steps: list[LineageStep] = []
        current, max_seq, max_time = branch_id, None, None
        while current is not None:
            row = self._conn.execute(
                'SELECT parent_branch_id, fork_seq, fork_game_time FROM branches '
                'WHERE branch_id = ? AND campaign_id = ?', (current, self.campaign_id)).fetchone()
            if row is None:
                raise StoreError(f'unknown branch {current}')
            steps.append(LineageStep(current, max_seq, max_time))
            parent, fork_seq, fork_time = row
            if parent is not None:
                max_seq = fork_seq if max_seq is None else min(max_seq, fork_seq)
                max_time = fork_time if max_time is None else min(max_time, fork_time)
            current = parent
        return steps

    def active_branch(self) -> str:
        row = self._conn.execute('SELECT branch_id FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        return row[0] if row else ROOT_BRANCH

    # ---- events ---------------------------------------------------------------------------

    def append_event(self, *, branch_id: str, host_epoch: int, event_type: str, category: str,
                     game_time: int | None, payload: dict[str, Any], evidence: str,
                     idempotency_key: str, source_observation_id: str | None = None
                     ) -> tuple[Event, bool]:
        if category not in CATEGORIES:
            raise ValueError(f'unknown category {category}')
        if evidence not in EVIDENCE:
            raise ValueError(f'unknown evidence {evidence}')
        if not self.branch_exists(branch_id):
            raise StoreError(f'unknown branch {branch_id}')
        body = _canonical(payload)
        cursor = self._conn.execute(
            f'INSERT INTO events ({_INSERT_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '
            'ON CONFLICT (idempotency_key) DO NOTHING',
            ('ev-' + uuid.uuid4().hex, idempotency_key, self.campaign_id, branch_id, host_epoch,
             event_type, category, game_time, body, evidence, source_observation_id,
             self._clock()))
        created = cursor.rowcount == 1
        row = self._conn.execute(f'SELECT {_EVENT_COLUMNS} FROM events WHERE idempotency_key = ?',
                                 (idempotency_key,)).fetchone()
        event = _row_to_event(row)
        if not created and (event.branch_id, event.event_type, event.category, event.game_time,
                            _canonical(event.payload)) != (branch_id, event_type, category,
                                                           game_time, body):
            raise IdempotencyConflict(f'key {idempotency_key} already used for other content')
        return event, created

    def get_event(self, event_id: str) -> Event | None:
        row = self._conn.execute(f'SELECT {_EVENT_COLUMNS} FROM events WHERE event_id = ?',
                                 (event_id,)).fetchone()
        return _row_to_event(row) if row else None

    def visible_events(self, branch_id: str, event_type: str | None = None) -> list[Event]:
        steps = {s.branch_id: s for s in self.lineage(branch_id)}
        placeholders = ','.join('?' * len(steps))
        query = (f'SELECT {_EVENT_COLUMNS} FROM events WHERE campaign_id = ? '
                 f'AND branch_id IN ({placeholders})')
        params: list[Any] = [self.campaign_id, *steps]
        if event_type is not None:
            query += ' AND event_type = ?'
            params.append(event_type)
        rows = self._conn.execute(query + ' ORDER BY seq', params).fetchall()
        return [e for e in map(_row_to_event, rows)
                if steps[e.branch_id].admits(e.seq, e.game_time)]

    def is_visible(self, branch_id: str, event_id: str) -> bool:
        event = self.get_event(event_id)
        if event is None or event.campaign_id != self.campaign_id:
            return False
        step = next((s for s in self.lineage(branch_id) if s.branch_id == event.branch_id), None)
        return step is not None and step.admits(event.seq, event.game_time)

    def latest_game_time(self, branch_id: str) -> int | None:
        times = [e.game_time for e in self.visible_events(branch_id) if e.game_time is not None]
        return max(times) if times else None
