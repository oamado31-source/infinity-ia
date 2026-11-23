# SPDX-License-Identifier: Apache-2.0
"""ADR-0138: who must be on the map is decided by the quest, through the action gateway.

A curated quest declares its presences (`presence` in the quest file): one of our creatures, an
area, and the two points of the quest between which it must be there. At each reading of the game
the director compares what the quest wants with what the branch holds:
- it must be there and is not, and the party is in that area: SPAWN (ENTER);
- it must no longer be there, the quest put it there, and the party is in that area: DESPAWN
  (LEAVE; the engine only removes in the loaded area);
- the party elsewhere: nothing (the creature stays in the save like any other).
ADR-0140: the director asks the game to count (read only) before trusting the branch, keeps
several copies, and sees a presence's defeat when its count falls to zero.
ADR-0139: a NIGHT presence is wanted only at night; at dawn it is no longer wanted, and the quest
removes what it placed when the party is in the area (D2).

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
    CONFIRMED, COUNT, DESPAWN, FAILED, REQUESTED, SPAWN, ActionError, ActionReceipt,
    ActionRequest, count_request, creature_counts, despawn_request, owned_creatures,
    record_requested, record_result, spawn_request,
)
from ..state.store import CampaignStore
from .clock import is_night
from .narrative import (
    DEFEATED, END_RESOLVED, START_ACCEPTED, WHEN_NIGHT, NarrativeQuest, Presence, QuestState,
    mark_step, state_of,
)

POLICY = 'adr-0138-quest-presence-v1'
SUSPENDED, RESUMED = 'QuestPresenceSuspended', 'QuestPresenceResumed'
ENTER, LEAVE = 'ENTER', 'LEAVE'
VERIFY, DEFEAT_WATCH, DEFEAT = 'VERIFY', 'DEFEAT_WATCH', 'DEFEAT'   # ADR-0140
COUNT_RULES = (VERIFY, DEFEAT_WATCH)
ENTRY_EVENTS = ('AreaEntered', 'SessionStarted', 'BranchForked')
WATCH_EVERY = 90          # game-time ticks between counts while a defeat is awaited (~6 s)


def wanted(state: QuestState, presence: Presence, game_time: int | None = None) -> bool:
    """Between its two points of the quest; a NIGHT presence only at night (ADR-0139)."""
    if presence.when == WHEN_NIGHT and not is_night(game_time):
        return False
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
    placed_by_quest: bool = False  # what is there now was created by this presence
    fresh: bool = False            # the game told the count after the last entry or load
    count: int = 0                 # how many the game last said are in the presence's area
    filled: bool = False           # the count reached `copies` after the quest created them
    last_count_at: int | None = None   # game time of the last COUNT of this name


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
    told = [e for e in events if e.event_type == CONFIRMED and e.game_time is not None
            and e.payload.get('name') == presence.name]
    last_out = max((e.seq for e in told if e.payload.get('op') == DESPAWN), default=-1)
    placed = any(e.payload.get('op') == SPAWN and _cause_of(e.payload) == key
                 and e.seq > last_out for e in told)
    first_spawn = min((e.seq for e in told if e.payload.get('op') == SPAWN
                       and _cause_of(e.payload) == key), default=None)
    filled = first_spawn is not None and any(
        e.seq >= first_spawn and e.payload.get('op') in (SPAWN, COUNT)
        and isinstance(e.payload.get('observed'), int)
        and e.payload['observed'] >= presence.copies for e in told)
    entries = [e.seq for t in ENTRY_EVENTS for e in store.visible_events(branch_id, t)]
    fresh = bool(told) and told[-1].seq > max(entries, default=-1)
    area, count = creature_counts(store, branch_id).get(presence.name, (presence.area, 0))
    counts = [e.game_time for e in told if e.payload.get('op') == COUNT]
    return PresenceStatus('SUSPENDED' if suspended else 'PENDING' if pending else None, placed,
                          fresh, count if area == presence.area else 0, filled,
                          counts[-1] if counts else None)


@dataclass(frozen=True)
class Decision:
    quest_id: str
    presence: Presence
    rule: str                      # ENTER, LEAVE, VERIFY, DEFEAT_WATCH or DEFEAT
    step_id: str | None = None     # DEFEAT: the step it does

    def cause(self) -> dict:
        return {'policy': POLICY, 'quest_id': self.quest_id,
                'presence_id': self.presence.presence_id, 'rule': self.rule}


def decide(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest], *,
           area: str | None, game_time: int | None = None
           ) -> tuple[Decision | None, tuple[str, ...]]:
    """The one thing the quests want now in the party's area, and the presences held back
    ("quest/presence=SUSPENDED|PENDING") for the log. ADR-0140 (D1): before acting on what the
    branch believes, the game is asked to count, once after each entry or load and whenever the
    branch's word is older than that; a presence awaiting its defeat is counted every few seconds,
    and its fall to zero is the defeat (never recreated once its copies were all there)."""
    if not area:
        return None, ()
    held: list[str] = []
    for quest in quests.values():
        for presence in quest.presence:
            if presence.area != area:
                continue
            state = state_of(store, branch_id, quest.quest_id)
            fall = next((s for s in quest.steps if s.kind == DEFEATED
                         and s.presence_id == presence.presence_id), None)
            fallen = fall is not None and fall.step_id in state.steps_done
            window = wanted(state, presence, game_time)
            want = window and not fallen
            status = status_of(store, branch_id, quest.quest_id, presence)
            # the quest closing the presence's window is a removal (LEAVE), never a defeat
            awaiting = window and fall is not None and not fallen and state.accepted \
                and not state.resolved and set(fall.after) <= state.steps_done \
                and status.placed_by_quest and status.filled
            if not want and not awaiting and not (status.placed_by_quest and status.count > 0):
                continue
            if status.blocked:
                held.append(f'{quest.quest_id}/{presence.presence_id}={status.blocked}')
                continue
            if awaiting:
                if status.fresh and status.count == 0:
                    return Decision(quest.quest_id, presence, DEFEAT, fall.step_id), tuple(held)
                due = not status.fresh or status.last_count_at is None or (
                    game_time is not None and game_time - status.last_count_at >= WATCH_EVERY)
                if due:
                    return Decision(quest.quest_id, presence, DEFEAT_WATCH), tuple(held)
                continue
            if want:
                if not status.fresh:
                    return Decision(quest.quest_id, presence, VERIFY), tuple(held)
                if status.count < presence.copies and not (fall is not None and status.filled):
                    return Decision(quest.quest_id, presence, ENTER), tuple(held)
                continue
            if status.placed_by_quest and status.count > 0:   # never what the maintainer placed
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


@dataclass(frozen=True)
class _QuestRef:
    """What recording a step needs of a quest: its id."""
    quest_id: str


class Transport(Protocol):
    """Takes one request to the game and brings back the module's last answer (or None)."""

    def send(self, req: ActionRequest) -> ActionReceipt | None: ...


def request_for(decision: Decision, store: CampaignStore, branch_id: str, *,
                templates: dict[str, str]) -> ActionRequest:
    p = decision.presence
    if decision.rule in COUNT_RULES:
        return count_request(p.name, p.area)
    if decision.rule == ENTER:
        req = spawn_request(p.cre, p.area, x=p.x, y=p.y, facing=p.facing, templates=templates)
        if req.name != p.name:                     # the file holds another name of ours
            raise ActionError('TEMPLATE_NAME_MISMATCH')
        return req
    return despawn_request(p.name, p.area, owned=set(owned_creatures(store, branch_id)))


def dispatch(store: CampaignStore, branch_id: str, decision: Decision, *, transport: Transport,
             templates: dict[str, str], game_time: int | None, host_epoch: int = 0) -> str:
    """Ask the game for the decision once. Returns HOST_CONFIRMED, DENIED, UNCERTAIN or
    REFUSED:<code> (the gateway refused before the game); anything but HOST_CONFIRMED suspends.
    DEFEAT asks nothing: the count already said zero, and the step is recorded (ADR-0140)."""
    if decision.rule == DEFEAT:
        quest_state = state_of(store, branch_id, decision.quest_id)
        if decision.step_id not in quest_state.steps_done:
            mark_step(store, branch_id, _QuestRef(decision.quest_id), decision.step_id,
                      game_time=game_time, host_epoch=host_epoch)
        return 'DEFEATED'
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


__all__ = ['ENTER', 'LEAVE', 'VERIFY', 'DEFEAT_WATCH', 'DEFEAT', 'SUSPENDED', 'RESUMED', 'Decision', 'PresenceStatus', 'Transport',
           'decide', 'dispatch', 'record_resumed', 'record_suspended', 'request_for', 'status_of',
           'wanted']
