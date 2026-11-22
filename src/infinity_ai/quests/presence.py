# SPDX-License-Identifier: Apache-2.0
"""ADR-0138: who must be on the map is decided by the quest, through the action gateway.

A curated quest declares its presences (`presence` in the quest file): one of our creatures, an
area, and the two points of the quest between which it must be there. At each reading of the game
the director compares what the quest wants with what the branch holds:
- it must be there and is not, and the party is in that area: SPAWN (ENTER);
- it must no longer be there, the quest put it there, and the party is in that area: DESPAWN
  (LEAVE; the engine only removes in the loaded area);
- the party elsewhere: nothing (the creature stays in the save like any other).

Never twice blindly (doc. 26): one action at a time; a request the game did not confirm (DENIED or
UNCERTAIN) suspends that presence on the branch until the maintainer resumes it, after looking at
the game; a request recorded without a result (the service stopped while waiting) blocks it too.
A refusal for the wrong area does not suspend: the module did nothing, the party had just left.
Only the quest's code and the maintainer dispatch; never the language model or the player's text,
which only move the quest by its existing rules (D1). Events carry the cause, never player text.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..actions.gateway import (
    CONFIRMED, FAILED, REQUESTED, SPAWN, ActionError, ActionReceipt, ActionRequest,
    despawn_request, owned_creatures, record_requested, record_result, spawn_request,
)
from ..state.store import CampaignStore
from .narrative import END_RESOLVED, START_ACCEPTED, NarrativeQuest, Presence, QuestState, state_of

POLICY = 'adr-0138-quest-presence-v1'
SUSPENDED, RESUMED = 'QuestPresenceSuspended', 'QuestPresenceResumed'
ENTER, LEAVE = 'ENTER', 'LEAVE'


def wanted(state: QuestState, presence: Presence) -> bool:
    """Between its two points of the quest."""
    started = state.accepted if presence.start == START_ACCEPTED \
        else presence.start in state.steps_done
    ended = state.resolved if presence.end == END_RESOLVED else presence.end in state.steps_done
    return started and not ended


def _cause_of(payload: dict) -> tuple[str, str] | None:
    cause = payload.get('cause')
    if isinstance(cause, dict) and cause.get('policy') == POLICY:
        return cause.get('quest_id'), cause.get('presence_id')
    return None


@dataclass(frozen=True)
class PresenceStatus:
    blocked: str | None = None     # why nothing may be asked now: SUSPENDED or PENDING
    placed_by_quest: bool = False  # the creature now present was created by this presence


def status_of(store: CampaignStore, branch_id: str, quest_id: str,
              presence: Presence) -> PresenceStatus:
    key = (quest_id, presence.presence_id)
    events = sorted((e for t in (REQUESTED, CONFIRMED, FAILED, SUSPENDED, RESUMED)
                     for e in store.visible_events(branch_id, t)), key=lambda e: e.seq)
    last_resume = max((e.seq for e in events if e.event_type == RESUMED
                       and (e.payload.get('quest_id'), e.payload.get('presence_id')) == key),
                      default=-1)
    suspended = any(e.event_type == SUSPENDED and e.seq > last_resume
                    and (e.payload.get('quest_id'), e.payload.get('presence_id')) == key
                    for e in events)
    answered = {e.payload.get('action_id') for e in events if e.event_type in (CONFIRMED, FAILED)}
    pending = any(e.event_type == REQUESTED and e.seq > last_resume
                  and _cause_of(e.payload) == key and e.payload.get('action_id') not in answered
                  for e in events)
    spawns = [e for e in events if e.event_type == CONFIRMED and e.game_time is not None
              and e.payload.get('name') == presence.name]
    placed = bool(spawns) and spawns[-1].payload.get('op') == SPAWN \
        and _cause_of(spawns[-1].payload) == key
    return PresenceStatus('SUSPENDED' if suspended else 'PENDING' if pending else None, placed)


@dataclass(frozen=True)
class Decision:
    quest_id: str
    presence: Presence
    rule: str                      # ENTER or LEAVE

    def cause(self) -> dict:
        return {'policy': POLICY, 'quest_id': self.quest_id,
                'presence_id': self.presence.presence_id, 'rule': self.rule}


def decide(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest], *,
           area: str | None) -> tuple[Decision | None, tuple[str, ...]]:
    """The one action the quests want now in the party's area, and the presences held back
    ("quest/presence=SUSPENDED|PENDING") for the log."""
    if not area:
        return None, ()
    owned = owned_creatures(store, branch_id)
    held: list[str] = []
    for quest in quests.values():
        for presence in quest.presence:
            if presence.area != area:
                continue
            want = wanted(state_of(store, branch_id, quest.quest_id), presence)
            here = owned.get(presence.name) == area
            if want == here:
                continue
            status = status_of(store, branch_id, quest.quest_id, presence)
            if status.blocked:
                held.append(f'{quest.quest_id}/{presence.presence_id}={status.blocked}')
                continue
            if want:
                return Decision(quest.quest_id, presence, ENTER), tuple(held)
            if status.placed_by_quest:     # never remove what the maintainer placed
                return Decision(quest.quest_id, presence, LEAVE), tuple(held)
    return None, tuple(held)


def record_suspended(store: CampaignStore, branch_id: str, decision: Decision, reason: str, *,
                     game_time: int | None, key: str, host_epoch: int = 0,
                     evidence: str = 'LAB_OBSERVED') -> None:
    payload = {'quest_id': decision.quest_id, 'presence_id': decision.presence.presence_id,
               'rule': decision.rule, 'reason': reason, 'policy': POLICY}
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=host_epoch, event_type=SUSPENDED,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
                           evidence=evidence,
                           idempotency_key=f'presence|{branch_id}|{decision.quest_id}|'
                                           f'{decision.presence.presence_id}|suspended|{key}')


def record_resumed(store: CampaignStore, branch_id: str, quest_id: str, presence_id: str, *,
                   game_time: int | None, key: str, host_epoch: int = 0,
                   evidence: str = 'LAB_OBSERVED') -> None:
    """The maintainer looked at the game and lets the presence act again (D3)."""
    payload = {'quest_id': quest_id, 'presence_id': presence_id, 'policy': POLICY}
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=host_epoch, event_type=RESUMED,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
                           evidence=evidence,
                           idempotency_key=f'presence|{branch_id}|{quest_id}|{presence_id}|'
                                           f'resumed|{key}')


class Transport(Protocol):
    """Takes one request to the game and brings back the module's last answer (or None)."""

    def send(self, req: ActionRequest) -> ActionReceipt | None: ...


def request_for(decision: Decision, store: CampaignStore, branch_id: str, *,
                templates: dict[str, str]) -> ActionRequest:
    p = decision.presence
    if decision.rule == ENTER:
        req = spawn_request(p.cre, p.area, x=p.x, y=p.y, facing=p.facing, templates=templates)
        if req.name != p.name:                     # the file holds another name of ours
            raise ActionError('TEMPLATE_NAME_MISMATCH')
        return req
    return despawn_request(p.name, p.area, owned=set(owned_creatures(store, branch_id)))


def dispatch(store: CampaignStore, branch_id: str, decision: Decision, *, transport: Transport,
             templates: dict[str, str], game_time: int | None, host_epoch: int = 0) -> str:
    """Ask the game for the decision once. Returns HOST_CONFIRMED, DENIED, UNCERTAIN or
    REFUSED:<code> (the gateway refused before the game); anything but HOST_CONFIRMED suspends."""
    try:
        req = request_for(decision, store, branch_id, templates=templates)
        record_requested(store, branch_id, req, game_time=game_time, host_epoch=host_epoch,
                         cause=decision.cause())
    except ActionError as exc:
        record_suspended(store, branch_id, decision, exc.code, game_time=game_time,
                         key=f'refused-{exc.code}-{game_time}', host_epoch=host_epoch)
        return f'REFUSED:{exc.code}'
    receipt = transport.send(req)
    state = record_result(store, branch_id, req, receipt, game_time=game_time,
                          host_epoch=host_epoch, cause=decision.cause())
    if state != 'HOST_CONFIRMED':
        reason = (receipt.reason if receipt is not None and receipt.reason else state)
        if state == 'DENIED' and reason == 'WRONG_AREA':
            return state      # the module did nothing: the party left before the request arrived
        record_suspended(store, branch_id, decision, reason, game_time=game_time,
                         key=req.action_id, host_epoch=host_epoch)
    return state


__all__ = ['ENTER', 'LEAVE', 'SUSPENDED', 'RESUMED', 'Decision', 'PresenceStatus', 'Transport',
           'decide', 'dispatch', 'record_resumed', 'record_suspended', 'request_for', 'status_of',
           'wanted']
