# SPDX-License-Identifier: Apache-2.0
"""SPEC-001 / P2: read-only adapter over the EEex probe log.

The probe (`tools/eeex-probe/M_INFAI.lua`) prints `INFAI-P2 {json}` lines to the game console,
which InfinityLoader mirrors to the file named in `LogFile=`. This module parses that text and
implements the `ReadOnlyAdapter` port. The channel is one-way: nothing here can send anything to
the game. Log lines are untrusted input (any mod can print), so parsing is strict and only the
probe's allowlisted fields survive.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Protocol

from .domain import AdapterReading, Coverage, Evidence, SessionIdentity

PROBE_PREFIX = 'INFAI-P2 '
PROBE_SCHEMA = 'infinity-ai.eeex-probe.v1'
ADAPTER_VERSION = 'eeex-log-0.1+probe-v1'
AREA_FIELD = 'host.current_area_id'
GAME_TIME_FIELD = 'host.game_time'
PROBE_FIELDS = frozenset({AREA_FIELD, GAME_TIME_FIELD})

_MAX_LINE = 2048
_RESREF = re.compile(r'[A-Za-z0-9_#-]{1,8}')


class StaleLogError(RuntimeError):
    """The log has not been written recently: the game or the probe is not running."""


class NoSnapshotError(RuntimeError):
    """No valid probe line in the log."""


@dataclass(frozen=True)
class Snapshot:
    seq: int
    session_seq: int
    clock_ms: int
    fields: Mapping[str, str | None] = field(default_factory=dict)


class LogSource(Protocol):
    def fetch(self) -> tuple[str, float]:
        """Return (log text, seconds since the log was last written)."""
        ...


def _non_negative_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _normalize_field(name: str, value: object) -> str | None:
    if name == AREA_FIELD:
        return value if isinstance(value, str) and _RESREF.fullmatch(value) else None
    if name == GAME_TIME_FIELD:
        number = _non_negative_int(value)
        return None if number is None else str(number)
    return None


def parse_snapshot_line(line: str) -> Snapshot | None:
    """Parse one log line; anything that is not a well-formed probe line yields None."""
    index = line.find(PROBE_PREFIX)
    if index < 0:
        return None
    payload = line[index + len(PROBE_PREFIX):].strip()
    if not payload or len(payload) > _MAX_LINE:
        return None
    try:
        doc = json.loads(payload)
    except ValueError:
        return None
    if not isinstance(doc, dict) or doc.get('schema') != PROBE_SCHEMA:
        return None
    seq, session_seq = _non_negative_int(doc.get('seq')), _non_negative_int(doc.get('session_seq'))
    clock_ms, fields = _non_negative_int(doc.get('clock_ms')), doc.get('fields')
    if seq is None or session_seq is None or clock_ms is None or not isinstance(fields, dict):
        return None
    normalized = {name: _normalize_field(name, fields.get(name)) for name in PROBE_FIELDS}
    return Snapshot(seq, session_seq, clock_ms, MappingProxyType(normalized))


def parse_latest_snapshot(text: str) -> Snapshot | None:
    """Latest valid probe line. An unterminated last line may still be being written: skipped."""
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith(('\n', '\r')):
        lines.pop()
    for line in reversed(lines):
        snapshot = parse_snapshot_line(line)
        if snapshot is not None:
            return snapshot
    return None


class EEexLogAdapter:
    """ReadOnlyAdapter over the probe log.

    Build fingerprint and modpack hash cannot come from the game (it does not hash its files):
    the caller passes the values from a manifest collected at the start of the session.
    """

    def __init__(self, source: LogSource, *, campaign_id: str, branch_id: str,
                 build_fingerprint: str, modpack_hash: str,
                 adapter_version: str = ADAPTER_VERSION, max_age_s: float = 10.0) -> None:
        self._source = source
        self._identity = dict(campaign_id=campaign_id, branch_id=branch_id,
                              build_fingerprint=build_fingerprint, modpack_hash=modpack_hash,
                              adapter_version=adapter_version)
        self._max_age_s = max_age_s

    def _snapshot(self) -> Snapshot:
        text, age = self._source.fetch()
        if not isinstance(age, (int, float)) or age < 0 or age > self._max_age_s:
            raise StaleLogError(f'log age {age!r}s exceeds {self._max_age_s}s')
        snapshot = parse_latest_snapshot(text)
        if snapshot is None:
            raise NoSnapshotError('no probe line in log')
        return snapshot

    def handshake(self) -> SessionIdentity:
        return SessionIdentity(host_epoch=self._snapshot().session_seq, **self._identity)

    def read(self, field: str) -> AdapterReading:
        snapshot = self._snapshot()
        value = snapshot.fields.get(field) if field in PROBE_FIELDS else None
        coverage = Coverage.FULL if value is not None else Coverage.NONE
        return AdapterReading(value, coverage, Evidence.LAB_OBSERVED, snapshot.session_seq)
