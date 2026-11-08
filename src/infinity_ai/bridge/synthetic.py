# SPDX-License-Identifier: Apache-2.0
"""Synthetic adapter for SPEC-001 contract tests.

It has no connection to BG2:EE or EEex and every reading it returns is marked SYNTHETIC, so it
can never be cited as P0-P4 evidence. Fixture values are invented, not game data.
"""
from __future__ import annotations

from collections.abc import Mapping

from .domain import AdapterReading, Coverage, Evidence, SessionIdentity


class SyntheticAdapter:
    def __init__(self, identity: SessionIdentity, values: Mapping[str, str | None],
                 *, fail_handshake: bool = False, fail_reads: bool = False) -> None:
        self.identity = identity
        self.values = dict(values)
        self.fail_handshake = fail_handshake
        self.fail_reads = fail_reads
        self.calls: list[tuple[str, str | None]] = []

    def handshake(self) -> SessionIdentity:
        self.calls.append(('handshake', None))
        if self.fail_handshake:
            raise ConnectionError('synthetic handshake failure')
        return self.identity

    def read(self, field: str) -> AdapterReading:
        self.calls.append(('read', field))
        if self.fail_reads:
            raise ConnectionError('synthetic read failure')
        value = self.values.get(field)
        coverage = Coverage.FULL if value else Coverage.NONE
        return AdapterReading(value, coverage, Evidence.SYNTHETIC, self.identity.host_epoch)
