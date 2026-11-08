# SPDX-License-Identifier: Apache-2.0
"""SPEC-001 domain types: pinned session identity, field policy and the observation envelope.

Pure data and rules only. Nothing here talks to BG2:EE, EEex or the network, and a synthetic
envelope is never evidence of a real capability (Constitution items 4 and 10, ADR-0108).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

ENVELOPE_SCHEMA_VERSION = 'infinity-ai.bridge.observation.v1'


class Status(str, Enum):
    OBSERVED = 'OBSERVED'
    UNKNOWN = 'UNKNOWN'
    BLOCKED_CAPABILITY = 'BLOCKED_CAPABILITY'
    DENIED = 'DENIED'


class Reason(str, Enum):
    NONE = 'NONE'
    BUILD_MISMATCH = 'BUILD_MISMATCH'
    MODPACK_MISMATCH = 'MODPACK_MISMATCH'
    ADAPTER_MISMATCH = 'ADAPTER_MISMATCH'
    EPOCH_MISMATCH = 'EPOCH_MISMATCH'
    CAMPAIGN_MISMATCH = 'CAMPAIGN_MISMATCH'
    SESSION_NOT_VALIDATED = 'SESSION_NOT_VALIDATED'
    FIELD_NOT_ALLOWLISTED = 'FIELD_NOT_ALLOWLISTED'
    WRITE_FORBIDDEN = 'WRITE_FORBIDDEN'
    MALFORMED_REQUEST = 'MALFORMED_REQUEST'
    ACL_AUDIENCE = 'ACL_AUDIENCE'
    ACL_PURPOSE = 'ACL_PURPOSE'
    ADAPTER_UNAVAILABLE = 'ADAPTER_UNAVAILABLE'
    NOT_OBSERVED = 'NOT_OBSERVED'


class Visibility(str, Enum):
    """Who may receive a field, ordered from least to most restricted."""
    PARTY = 'PARTY'
    HOST_ONLY = 'HOST_ONLY'
    SECRET = 'SECRET'


class Audience(str, Enum):
    HOST = 'HOST'
    PLAYER = 'PLAYER'
    NARRATIVE_CONTEXT = 'NARRATIVE_CONTEXT'


class Coverage(str, Enum):
    FULL = 'FULL'
    PARTIAL = 'PARTIAL'
    NONE = 'NONE'


class Evidence(str, Enum):
    """Where an observation came from. Only POC_VERIFIED can ever back a capability claim.

    LAB_OBSERVED: read from the real game in the lab environment of CR-2026-001 (Windows on ARM
    VM) while a gate is being exercised; it is real data, but not a native-build capability.
    """
    SYNTHETIC = 'SYNTHETIC'
    LAB_OBSERVED = 'LAB_OBSERVED'
    POC_VERIFIED = 'POC_VERIFIED'


# Which audiences may see which visibility level. SECRET is never projected by the bridge.
_CLEARANCE: dict[Audience, frozenset[Visibility]] = {
    Audience.HOST: frozenset({Visibility.PARTY, Visibility.HOST_ONLY}),
    Audience.PLAYER: frozenset({Visibility.PARTY}),
    Audience.NARRATIVE_CONTEXT: frozenset({Visibility.PARTY}),
}


def audience_may_see(audience: Audience, visibility: Visibility) -> bool:
    return visibility in _CLEARANCE[audience]


def _require_text(**values: str) -> None:
    missing = [name for name, value in values.items() if not isinstance(value, str) or not value]
    if missing:
        raise ValueError(f'Missing identity fields: {", ".join(missing)}')


@dataclass(frozen=True)
class SessionIdentity:
    """What the host must match before any read (REQ-BRIDGE-001)."""
    campaign_id: str
    branch_id: str
    host_epoch: int
    build_fingerprint: str
    modpack_hash: str
    adapter_version: str

    def __post_init__(self) -> None:
        _require_text(campaign_id=self.campaign_id, branch_id=self.branch_id,
                      build_fingerprint=self.build_fingerprint,
                      modpack_hash=self.modpack_hash, adapter_version=self.adapter_version)
        if isinstance(self.host_epoch, bool) or not isinstance(self.host_epoch, int) \
                or self.host_epoch < 0:
            raise ValueError('host_epoch must be a non-negative integer')


@dataclass(frozen=True)
class FieldPolicy:
    field: str
    visibility: Visibility
    purposes: frozenset[str]

    def __post_init__(self) -> None:
        _require_text(field=self.field)
        if not self.purposes:
            raise ValueError(f'Field {self.field} needs at least one allowed purpose')


@dataclass(frozen=True)
class Allowlist:
    """Pinned per build. A field absent here is BLOCKED_CAPABILITY, never guessed."""
    build_fingerprint: str
    policies: tuple[FieldPolicy, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        names = [p.field for p in self.policies]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate field policy')

    def policy_for(self, name: str) -> FieldPolicy | None:
        return next((p for p in self.policies if p.field == name), None)


@dataclass(frozen=True)
class ReadQuery:
    field: str
    purpose: str
    audience: Audience


@dataclass(frozen=True)
class AdapterReading:
    """What an adapter returns. value=None means "not observed", never "false".

    host_epoch is the epoch the host reported at read time, so a save/load between connect and
    read is caught instead of mixing epochs.
    """
    value: str | None
    coverage: Coverage
    evidence: Evidence
    host_epoch: int


@dataclass(frozen=True)
class ObservationEnvelope:
    observation_id: str
    timestamp: str
    session: SessionIdentity
    field: str
    purpose: str
    audience: Audience | None
    status: Status
    reason: Reason
    value: str | None
    coverage: Coverage
    visibility: Visibility | None
    evidence: Evidence
    schema_version: str = ENVELOPE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text(observation_id=self.observation_id, timestamp=self.timestamp,
                      field=self.field)
        if self.status is Status.OBSERVED:
            if self.value is None or self.reason is not Reason.NONE \
                    or self.coverage is Coverage.NONE:
                raise ValueError('OBSERVED needs a value, reason NONE and some coverage')
        else:
            if self.value is not None:
                raise ValueError('Only OBSERVED may carry a value')
            if self.reason is Reason.NONE:
                raise ValueError('Non-observed status needs an explicit reason')
            if self.coverage is not Coverage.NONE:
                raise ValueError('Non-observed status has no coverage')

    def to_json(self) -> dict[str, Any]:
        s = self.session
        return {
            'schema_version': self.schema_version,
            'observation_id': self.observation_id,
            'timestamp': self.timestamp,
            'campaign_id': s.campaign_id,
            'branch_id': s.branch_id,
            'host_epoch': s.host_epoch,
            'build_fingerprint': s.build_fingerprint,
            'modpack_hash': s.modpack_hash,
            'field': self.field,
            'purpose': self.purpose,
            'audience': self.audience.value if self.audience else None,
            'status': self.status.value,
            'reason': self.reason.value,
            'value': self.value,
            'coverage': self.coverage.value,
            'visibility': self.visibility.value if self.visibility else None,
            'provenance': {'adapter_version': s.adapter_version,
                           'evidence': self.evidence.value},
        }
