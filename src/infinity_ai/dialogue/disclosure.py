# SPDX-License-Identifier: Apache-2.0
"""ADR-0131 / SPEC-009: what a person tells, decided per item by code, before any prompt.

Order: eligibility (done before this module: the item is held, valid for the time and branch, and
the ACL let it through) -> secrecy class -> relational state (encounter disposition, trust, morale)
-> depth (the existing knowledge layers). A withheld item never reaches the model: not its text,
not its id. The decision is pure and deterministic, and every outcome carries a reason code.

An item without a class keeps the behaviour from before the class existed (ADR-0125/0126):
public scopes count as PUBLIC and RESTRICTED as PROFESSIONAL, so a friendly or indifferent person
tells both, a cautious one keeps the professional ones, a threatening, hostile or fleeing one tells
nothing, and giving in (YIELD) opens what the disposition hid. Classes above PROFESSIONAL never
open by reaction or morale.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..canon.pack import SECRECY

POLICY_VERSION = 'adr-0131-v1'

PUBLIC, PERSONAL, PROFESSIONAL, CONFIDENTIAL, FACTION_SECRET, ABSOLUTE = SECRECY
ALLOW_FULL, ALLOW_SUMMARY, ALLOW_PUBLIC_ONLY = 'ALLOW_FULL', 'ALLOW_SUMMARY', 'ALLOW_PUBLIC_ONLY'
WITHHOLD, UNKNOWN = 'WITHHOLD', 'UNKNOWN'
# Qualitative, directed trust (observer -> listener). The first cut is neutral for everyone.
DESCONFIADO, NEUTRO, CONFIANTE, INTIMO = 'DESCONFIADO', 'NEUTRO', 'CONFIANTE', 'INTIMO'
TRUST_LEVELS = (DESCONFIADO, NEUTRO, CONFIANTE, INTIMO)
CLOSED_DISPOSITIONS = frozenset({'THREATENING', 'HOSTILE', 'FLIGHT'})   # ADR-0125: tells nothing
GIVES_UNDER_PRESSURE = frozenset({PUBLIC, PERSONAL, PROFESSIONAL})       # what YIELD may open


@dataclass(frozen=True)
class Decision:
    entry_id: str
    secrecy: str
    mode: str          # ALLOW_FULL | ALLOW_SUMMARY | ALLOW_PUBLIC_ONLY | WITHHOLD | UNKNOWN
    reason: str        # audit code, never the item's text

    @property
    def allowed(self) -> bool:
        return self.mode in (ALLOW_FULL, ALLOW_SUMMARY, ALLOW_PUBLIC_ONLY)


def secrecy_of(access_scope: str | None, secrecy: str | None = None) -> str:
    """The item's class: the curated one, or the default by scope (absent class = old rule)."""
    if secrecy is not None:
        if secrecy not in SECRECY:
            raise ValueError(f'unknown secrecy class {secrecy!r}')
        return secrecy
    return PROFESSIONAL if access_scope == 'RESTRICTED' else PUBLIC


def decide(entry_id: str, *, access_scope: str | None, secrecy: str | None = None,
           disposition: str | None = None, morale_outcome: str | None = None,
           trust: str = NEUTRO, listener_member: bool = False) -> Decision:
    """One item, one decision. `disposition` is the ADR-0125 encounter reaction (None = not
    resolved: open), `morale_outcome` HOLD/YIELD of this line (ADR-0126), `trust` the directed
    trust of the speaker in the listener, `listener_member` whether the listener is an eligible
    member of the organization a FACTION_SECRET belongs to."""
    if trust not in TRUST_LEVELS:
        raise ValueError(f'unknown trust {trust!r}')
    cls = secrecy_of(access_scope, secrecy)
    gave_in = morale_outcome == 'YIELD'
    closed = disposition in CLOSED_DISPOSITIONS

    def out(mode: str, reason: str) -> Decision:
        return Decision(entry_id, cls, mode, reason)

    if cls == ABSOLUTE:
        return out(WITHHOLD, 'ABSOLUTE')
    if cls == FACTION_SECRET:
        return out(ALLOW_FULL, 'MEMBER') if listener_member and not closed \
            else out(WITHHOLD, 'NOT_A_MEMBER' if not listener_member else 'CLOSED_DISPOSITION')
    if cls == CONFIDENTIAL:
        if trust not in (CONFIANTE, INTIMO):
            return out(WITHHOLD, 'TRUST_REQUIRED')
        return out(WITHHOLD, 'CLOSED_DISPOSITION') if closed else out(ALLOW_FULL, 'TRUSTED')
    # PUBLIC, PERSONAL, PROFESSIONAL: the encounter disposition decides; giving in opens them.
    if gave_in:
        return out(ALLOW_FULL, 'GAVE_IN')
    if closed:
        return out(WITHHOLD, 'CLOSED_DISPOSITION')
    if cls == PROFESSIONAL:
        if disposition == 'CAUTIOUS':
            return out(WITHHOLD, 'CAUTIOUS')
        if trust == DESCONFIADO:
            return out(WITHHOLD, 'TRUST_REQUIRED')
    return out(ALLOW_FULL, 'OPEN')
