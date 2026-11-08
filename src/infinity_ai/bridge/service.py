# SPDX-License-Identifier: Apache-2.0
"""SPEC-001 read-only bridge service (application layer).

The service checks, in this order and before touching the adapter: request shape and read-only
operation (REQ-BRIDGE-003), validated session identity (REQ-BRIDGE-001), allowlist, purpose and
audience ACL (REQ-BRIDGE-004). Only then it reads, and any missing data or adapter failure becomes
UNKNOWN, never an asserted state (REQ-BRIDGE-002/005). It exposes no write method at all.
"""
from __future__ import annotations

import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from .domain import (
    AdapterReading, Allowlist, Audience, Coverage, Evidence, ObservationEnvelope, Reason,
    SessionIdentity, Status, audience_may_see,
)

READ_OPERATION = 'read'
_REQUEST_KEYS = frozenset({'operation', 'field', 'purpose', 'audience'})


class ReadOnlyAdapter(Protocol):
    """Port implemented by the synthetic simulator now and by a real EEex adapter after P2."""

    def handshake(self) -> SessionIdentity: ...

    def read(self, field: str) -> AdapterReading: ...


@dataclass(frozen=True)
class SessionCheck:
    ok: bool
    reasons: tuple[Reason, ...]


def compare_identity(pinned: SessionIdentity, live: SessionIdentity) -> SessionCheck:
    reasons: list[Reason] = []
    if (live.campaign_id, live.branch_id) != (pinned.campaign_id, pinned.branch_id):
        reasons.append(Reason.CAMPAIGN_MISMATCH)
    if live.build_fingerprint != pinned.build_fingerprint:
        reasons.append(Reason.BUILD_MISMATCH)
    if live.modpack_hash != pinned.modpack_hash:
        reasons.append(Reason.MODPACK_MISMATCH)
    if live.adapter_version != pinned.adapter_version:
        reasons.append(Reason.ADAPTER_MISMATCH)
    if live.host_epoch != pinned.host_epoch:
        reasons.append(Reason.EPOCH_MISMATCH)
    return SessionCheck(not reasons, tuple(reasons))


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


class ReadOnlyBridge:
    def __init__(self, pinned: SessionIdentity, allowlist: Allowlist, adapter: ReadOnlyAdapter,
                 *, clock: Callable[[], str] = _utc_now,
                 id_factory: Callable[[], str] = lambda: str(uuid.uuid4()),
                 evidence: Evidence = Evidence.SYNTHETIC) -> None:
        """`evidence` labels envelopes that carry no reading (refusals, failures) so a real
        lab session is never recorded as SYNTHETIC. Readings keep the adapter's own label."""
        if allowlist.build_fingerprint != pinned.build_fingerprint:
            raise ValueError('Allowlist is pinned to a different build')
        self._pinned = pinned
        self._allowlist = allowlist
        self._adapter = adapter
        self._clock = clock
        self._new_id = id_factory
        self._evidence = evidence
        self._check = SessionCheck(False, (Reason.SESSION_NOT_VALIDATED,))

    @property
    def session_check(self) -> SessionCheck:
        return self._check

    def connect(self) -> SessionCheck:
        """Handshake with the host. Any failure leaves the session blocked (fail closed)."""
        try:
            live = self._adapter.handshake()
        except Exception:  # adapter or transport failure must not open the session
            self._check = SessionCheck(False, (Reason.ADAPTER_UNAVAILABLE,))
        else:
            self._check = compare_identity(self._pinned, live)
        return self._check

    def handle(self, request: Any) -> ObservationEnvelope:
        if not isinstance(request, Mapping):
            return self._refuse('<invalid>', '', None, Status.BLOCKED_CAPABILITY,
                                Reason.MALFORMED_REQUEST)
        field = request.get('field')
        field = field if isinstance(field, str) and field else '<invalid>'
        purpose = request.get('purpose')
        purpose = purpose if isinstance(purpose, str) else ''
        audience = _parse_audience(request.get('audience'))

        if request.get('operation') != READ_OPERATION:
            return self._refuse(field, purpose, audience, Status.BLOCKED_CAPABILITY,
                                Reason.WRITE_FORBIDDEN)
        if set(request) - _REQUEST_KEYS or field == '<invalid>' or not purpose \
                or audience is None:
            return self._refuse(field, purpose, audience, Status.BLOCKED_CAPABILITY,
                                Reason.MALFORMED_REQUEST)
        if not self._check.ok:
            return self._refuse(field, purpose, audience, Status.BLOCKED_CAPABILITY,
                                self._check.reasons[0])

        policy = self._allowlist.policy_for(field)
        if policy is None:
            return self._refuse(field, purpose, audience, Status.BLOCKED_CAPABILITY,
                                Reason.FIELD_NOT_ALLOWLISTED)
        if purpose not in policy.purposes:
            return self._refuse(field, purpose, audience, Status.DENIED, Reason.ACL_PURPOSE,
                                policy.visibility)
        if not audience_may_see(audience, policy.visibility):
            return self._refuse(field, purpose, audience, Status.DENIED, Reason.ACL_AUDIENCE,
                                policy.visibility)

        try:
            reading = self._adapter.read(field)
        except Exception:
            return self._refuse(field, purpose, audience, Status.UNKNOWN,
                                Reason.ADAPTER_UNAVAILABLE, policy.visibility)
        if not isinstance(reading, AdapterReading):
            return self._refuse(field, purpose, audience, Status.UNKNOWN,
                                Reason.ADAPTER_UNAVAILABLE, policy.visibility)
        if reading.host_epoch != self._pinned.host_epoch:
            self._check = SessionCheck(False, (Reason.EPOCH_MISMATCH,))
            return self._refuse(field, purpose, audience, Status.BLOCKED_CAPABILITY,
                                Reason.EPOCH_MISMATCH, policy.visibility)
        if not isinstance(reading.value, str) or not reading.value \
                or reading.coverage is Coverage.NONE:
            return self._refuse(field, purpose, audience, Status.UNKNOWN, Reason.NOT_OBSERVED,
                                policy.visibility, reading.evidence)
        return self._envelope(field, purpose, audience, Status.OBSERVED, Reason.NONE,
                              reading.value, reading.coverage, policy.visibility,
                              reading.evidence)

    def _refuse(self, field: str, purpose: str, audience: Audience | None, status: Status,
                reason: Reason, visibility=None,
                evidence: Evidence | None = None) -> ObservationEnvelope:
        return self._envelope(field, purpose, audience, status, reason, None, Coverage.NONE,
                              visibility, evidence or self._evidence)

    def _envelope(self, field, purpose, audience, status, reason, value, coverage, visibility,
                  evidence) -> ObservationEnvelope:
        return ObservationEnvelope(
            observation_id=self._new_id(), timestamp=self._clock(), session=self._pinned,
            field=field, purpose=purpose, audience=audience, status=status, reason=reason,
            value=value, coverage=coverage, visibility=visibility, evidence=evidence)


def _parse_audience(raw: Any) -> Audience | None:
    try:
        return Audience(raw)
    except ValueError:
        return None
