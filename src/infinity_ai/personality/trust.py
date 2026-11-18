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
- MILESTONE (ADR-0134): a curated quest milestone the branch has seen sets the level the person's
  curation names for it (INTIMO, CONFIANTE or DESCONFIADO). Trust from a milestone is not
  `own_only`: it opens the house's or others' secrets too (ADR-0133 D2). It also takes a person
  out of DESCONFIADO (D5): events count in recorded order, the latest decisive one wins.

Each change is one `NpcTrustRevised` event, idempotent by rule and cause; `trust_of` reads the
latest one of the branch. Pure, deterministic, no decay (ADR-0101 item 13).
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..dialogue.disclosure import CONFIANTE, DESCONFIADO, INTIMO, NEUTRO
from ..dialogue.recall import TURN_EVENT
from ..state.store import CampaignStore
from ..quests.milestones import MILESTONE_EVENT
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
RULE_MILESTONE = 'MILESTONE'
MILESTONE_LEVELS = frozenset({DESCONFIADO, CONFIANTE, INTIMO})


@dataclass(frozen=True)
class Trust:
    level: str                 # DESCONFIADO, NEUTRO, CONFIANTE, INTIMO
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


def _history(store: CampaignStore, branch_id: str, key: str,
             effects: Mapping[str, str] | None = None) -> list:
    """This person's reactions, morale checks and turns, and the branch's milestones its
    curation names, in recorded order."""
    events = []
    for event_type in (REACTION_EVENT, MORALE_EVENT, TURN_EVENT):
        events += [e for e in store.visible_events(branch_id, event_type)
                   if e.payload.get('npc_key') == key]
    if effects:
        events += [e for e in store.visible_events(branch_id, MILESTONE_EVENT)
                   if e.payload.get('semantic_id') in effects]
    return sorted(events, key=lambda e: e.seq)


def assess(events: list, effects: Mapping[str, str] | None = None
           ) -> tuple[Trust, tuple[str, ...]]:
    """The trust these events justify, and the ids of the events that caused it. Pure.
    `effects`: semantic id of a milestone -> the level the person's curation gives it."""
    effects = effects or {}
    trust, cause = Trust(NEUTRO), ()
    sessions: set[tuple] = set()
    turns = 0
    for e in events:
        p = e.payload
        hostile = (e.event_type == MORALE_EVENT and p.get('trigger') in (INTIMIDATION, BETRAYAL)) \
            or (e.event_type == REACTION_EVENT and p.get('disposition') in HOSTILE_REACTIONS)
        if hostile:
            rule = RULE_COERCION if e.event_type == MORALE_EVENT else RULE_HOSTILITY
            trust, cause = Trust(DESCONFIADO, rule), (e.event_id,)
            continue
        if e.event_type == MILESTONE_EVENT:
            level = effects.get(p.get('semantic_id'))
            if level in MILESTONE_LEVELS:
                trust, cause = Trust(level, RULE_MILESTONE), (e.event_id,)
            continue
        if e.event_type == REACTION_EVENT and p.get('disposition') in GOOD_REACTIONS:
            sessions.add((p.get('launch', ''), p.get('session')))
        elif e.event_type == TURN_EVENT:
            turns += 1
        if trust.level == NEUTRO and len(sessions) >= SESSIONS_FOR_TRUST \
                and turns >= TURNS_FOR_TRUST:
            trust, cause = Trust(CONFIANTE, RULE_ACQUAINTANCE, own_only=True), (e.event_id,)
    return trust, cause


def revise_trust(store: CampaignStore, branch_id: str, key: str, *, game_time: int | None,
                 host_epoch: int = 0, evidence: str = 'LAB_OBSERVED',
                 effects: Mapping[str, str] | None = None) -> Trust:
    """Record a change of trust when the events justify one; return the current trust."""
    if not key:
        return Trust(NEUTRO)
    current = trust_of(store, branch_id, key)
    wanted, cause = assess(_history(store, branch_id, key, effects), effects)
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
