# SPDX-License-Identifier: Apache-2.0
"""ADR-0133: trust by event (SPEC-009 phase 4b), from what the campaign already records.

Trust is qualitative and directed: what one person (`npc_key`) feels about the player's group.
It changes only by recorded game events, never by the player's words (ADR-0131 item 6):

- DESCONFIADO: an intimidation or a betrayal (ADR-0126 morale checks, any outcome), or a
  hostile encounter reaction (ADR-0125). It stays until a later rule brings it back.
- CONFIANTE: knowing the group for real. A friendly or indifferent reaction in at least
  `SESSIONS_FOR_TRUST` different game sessions and `TURNS_FOR_TRUST` conversation turns in
  all, with nothing hostile since. Trust from acquaintance only opens the person's OWN
  confidences (`own_only`); secrets about the house or others need a curated milestone.
- A bribe moves nothing: money buys giving in (YIELD), not trust.
- INTIMO: no automatic rule yet (curated quest milestones, ADR-0095/0096, come later).

Each change is one `NpcTrustRevised` event, idempotent by rule and cause; `trust_of` reads the
latest one of the branch. Pure, deterministic, no decay (ADR-0101 item 13).
"""
from __future__ import annotations

from dataclasses import dataclass

from ..dialogue.disclosure import CONFIANTE, DESCONFIADO, NEUTRO
from ..dialogue.recall import TURN_EVENT
from ..state.store import CampaignStore
from .morale import BETRAYAL, INTIMIDATION, MORALE_EVENT
from .reaction import REACTION_EVENT

TRUST_EVENT = 'NpcTrustRevised'
POLICY = 'adr-0133-trust-v1'
TARGET = 'party'
SESSIONS_FOR_TRUST = 3
TURNS_FOR_TRUST = 6
GOOD_REACTIONS = frozenset({'FRIENDLY', 'INDIFFERENT'})
HOSTILE_REACTIONS = frozenset({'HOSTILE'})
RULE_ACQUAINTANCE, RULE_COERCION, RULE_HOSTILITY = 'ACQUAINTANCE', 'COERCION', 'HOSTILITY'


@dataclass(frozen=True)
class Trust:
    level: str                 # DESCONFIADO, NEUTRO, CONFIANTE (INTIMO later)
    rule: str | None = None    # what made it so; None while NEUTRO by default
    own_only: bool = False     # CONFIANTE from acquaintance opens only the person's own secrets


def trust_of(store: CampaignStore, branch_id: str, key: str) -> Trust:
    """The person's current trust in the group, from the latest `NpcTrustRevised` of the branch."""
    if not key:
        return Trust(NEUTRO)
    latest = None
    for event in store.visible_events(branch_id, TRUST_EVENT):
        if event.payload.get('npc_key') == key and event.payload.get('target') == TARGET:
            latest = event
    if latest is None:
        return Trust(NEUTRO)
    p = latest.payload
    return Trust(p['level'], p.get('rule'), bool(p.get('own_only')))


def _history(store: CampaignStore, branch_id: str, key: str) -> list:
    """This person's reactions, morale checks and turns, in recorded order."""
    events = []
    for event_type in (REACTION_EVENT, MORALE_EVENT, TURN_EVENT):
        events += [e for e in store.visible_events(branch_id, event_type)
                   if e.payload.get('npc_key') == key]
    return sorted(events, key=lambda e: e.seq)


def assess(events: list) -> tuple[Trust, tuple[str, ...]]:
    """The trust these events justify, and the ids of the events that caused it. Pure."""
    level, cause = NEUTRO, ()
    sessions: set[tuple] = set()
    turns = 0
    for e in events:
        p = e.payload
        hostile = (e.event_type == MORALE_EVENT and p.get('trigger') in (INTIMIDATION, BETRAYAL)) \
            or (e.event_type == REACTION_EVENT and p.get('disposition') in HOSTILE_REACTIONS)
        if hostile:
            rule = RULE_COERCION if e.event_type == MORALE_EVENT else RULE_HOSTILITY
            return Trust(DESCONFIADO, rule), (e.event_id,)
        if e.event_type == REACTION_EVENT and p.get('disposition') in GOOD_REACTIONS:
            sessions.add((p.get('launch', ''), p.get('session')))
        elif e.event_type == TURN_EVENT:
            turns += 1
        if level == NEUTRO and len(sessions) >= SESSIONS_FOR_TRUST and turns >= TURNS_FOR_TRUST:
            level, cause = CONFIANTE, (e.event_id,)
    if level == CONFIANTE:
        return Trust(CONFIANTE, RULE_ACQUAINTANCE, own_only=True), cause
    return Trust(NEUTRO), ()


def revise_trust(store: CampaignStore, branch_id: str, key: str, *, game_time: int | None,
                 host_epoch: int = 0, evidence: str = 'LAB_OBSERVED') -> Trust:
    """Record a change of trust when the events justify one; return the current trust."""
    if not key:
        return Trust(NEUTRO)
    current = trust_of(store, branch_id, key)
    wanted, cause = assess(_history(store, branch_id, key))
    if wanted.level == NEUTRO or (wanted.level, wanted.rule) == (current.level, current.rule):
        return current
    payload = {'npc_key': key, 'target': TARGET, 'level': wanted.level, 'rule': wanted.rule,
               'own_only': wanted.own_only, 'cause': list(cause), 'policy': POLICY}
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=host_epoch, event_type=TRUST_EVENT,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
                           evidence=evidence,
                           idempotency_key=f'trust|{branch_id}|{key}|{wanted.rule}|{",".join(cause)}')
    return wanted
