# SPDX-License-Identifier: Apache-2.0
"""ADR-0138: who must be on the map is decided by the quest, through the action gateway.

A curated quest declares its presences (`presence` in the quest file): one of our creatures, an
area, and the two points of the quest between which it must be there. At each reading of the game
the director compares what the quest wants with what the branch holds:
- it must be there and is not, and the party is in that area: SPAWN (ENTER);
- it must no longer be there, the quest put it there, and the party is in that area: DESPAWN
  (LEAVE; the engine only removes in the loaded area);
- the party elsewhere: nothing (the creature stays in the save like any other).
ADR-0142: a presence with `hostile_from` is made hostile (SET_HOSTILE) once that point of the quest is
reached and all its copies are there; never twice after the same creation.
ADR-0140: the director asks the game to count (read only) before trusting the branch, keeps
several copies, and sees a presence's defeat when its count falls to zero.
ADR-0144: a presence with `leave: ESCAPE` walks to the nearest exit and vanishes there (the game's
EscapeArea()) instead of vanishing on the spot; a quest's giver may call for help over its head
(CALL, display only) in its area, on entering and every few minutes, until the quest is accepted.
ADR-0139: a NIGHT presence is wanted only at night; at dawn it is no longer wanted, and the quest
removes what it placed when the party is in the area (D2).
ADR-0148: a presence `from: START` is wanted before the offer (a giver who is a person of ours); a
presence with `walk_to` walks there once created; a resolved quest with a reward pays it once
(REWARD), and an unconfirmed payment is held, never sent again.

Never twice blindly (doc. 26): one action at a time; a request the game did not confirm (DENIED or
UNCERTAIN) suspends that presence on the branch until the maintainer resumes it, after looking at
the game; a request recorded without a result (the service stopped while waiting) blocks it too.
A refusal for the wrong area does not suspend: the module did nothing, the party had just left.
Only the quest's code and the maintainer dispatch; never the language model or the player's text,
which only move the quest by its existing rules (D1). Events carry the cause, never player text.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from typing import Protocol

from ..actions.gateway import (
    CALL, CONFIRMED, COUNT, DONE, FAILED, REMOVALS, REQUESTED, REWARD, SET_HOSTILE, SPAWN,
    ActionError, ActionReceipt, ActionRequest, call_request, count_request, creature_counts,
    despawn_request, PassageEntry, check_passage, escape_request, hostile_request,
    owned_creatures, record_requested, record_result, reward_request, spawn_request,
)
from ..state.store import CampaignStore
from .clock import is_night
from .narrative import (
    ARRIVE, DEFEATED, END_RESOLVED, LEAVE_ESCAPE, START_ACCEPTED, START_BEGIN, WHEN_NIGHT,
    NarrativeQuest, Presence, QuestState, mark_step, state_of,
)

POLICY = 'adr-0138-quest-presence-v1'
SUSPENDED, RESUMED = 'QuestPresenceSuspended', 'QuestPresenceResumed'
ENTER, LEAVE = 'ENTER', 'LEAVE'
VERIFY, DEFEAT_WATCH, DEFEAT = 'VERIFY', 'DEFEAT_WATCH', 'DEFEAT'   # ADR-0140
HOSTILE = 'HOSTILE'                                                   # ADR-0142
COUNT_RULES = (VERIFY, DEFEAT_WATCH)
ENTRY_EVENTS = ('AreaEntered', 'SessionStarted', 'BranchForked')
WATCH_EVERY = 90          # game-time ticks between counts while a defeat is awaited (~6 s)


def wanted(state: QuestState, presence: Presence, game_time: int | None = None) -> bool:
    """Between its two points of the quest; a NIGHT presence only at night (ADR-0139)."""
    if presence.when == WHEN_NIGHT and not is_night(game_time):
        return False
    started = True if presence.start == START_BEGIN \
        else state.accepted if presence.start == START_ACCEPTED \
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
    made_hostile: bool = False     # ADR-0142: a SET_HOSTILE confirmed after the last creation


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
    last_out = max((e.seq for e in told if e.payload.get('op') in REMOVALS), default=-1)
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
    last_spawn = max((e.seq for e in told if e.payload.get('op') == SPAWN), default=-1)
    hostile = any(e.payload.get('op') == SET_HOSTILE and e.seq > last_spawn for e in told)
    return PresenceStatus('SUSPENDED' if suspended else 'PENDING' if pending else None, placed,
                          fresh, count if area == presence.area else 0, filled,
                          counts[-1] if counts else None, hostile)


@dataclass(frozen=True)
class Decision:
    quest_id: str
    presence: Presence
    rule: str                      # ENTER, LEAVE, VERIFY, DEFEAT_WATCH, DEFEAT or HOSTILE
    step_id: str | None = None     # DEFEAT: the step it does
    count: int = 1                 # ENTER (ADR-0143): the missing copies, created together

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
    and its fall to zero is the defeat (never recreated once its copies were all there).
    ADR-0143: the missing copies are asked in one request; HOSTILE comes before the others."""
    if not area:
        return None, ()
    held: list[str] = []
    found: list[Decision] = []
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
            turn = presence.hostile_from is not None and window and status.count > 0 \
                and status.fresh and not status.made_hostile and (
                    state.accepted if presence.hostile_from == START_ACCEPTED
                    else presence.hostile_from in state.steps_done)
            if turn and status.filled:                  # ADR-0142: they fight from now on
                found.append(Decision(quest.quest_id, presence, HOSTILE))
                continue
            if awaiting:
                if status.fresh and status.count == 0:
                    found.append(Decision(quest.quest_id, presence, DEFEAT, fall.step_id))
                    continue
                due = not status.fresh or status.last_count_at is None or (
                    game_time is not None and game_time - status.last_count_at >= WATCH_EVERY)
                if due:
                    found.append(Decision(quest.quest_id, presence, DEFEAT_WATCH))
                continue
            if want:
                if not status.fresh:
                    found.append(Decision(quest.quest_id, presence, VERIFY))
                    continue
                if status.count < presence.copies and not (fall is not None and status.filled):
                    found.append(Decision(quest.quest_id, presence, ENTER,
                                          count=presence.copies - status.count))
                continue
            if status.placed_by_quest and status.count > 0:   # never what the maintainer placed
                found.append(Decision(quest.quest_id, presence, LEAVE))
    # ADR-0143 (D3): a presence turning hostile goes before any other's count, so every presence
    # a step turns fights from the cycles right after it
    first = next((d for d in found if d.rule == HOSTILE), found[0] if found else None)
    return first, tuple(held)


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
    if decision.rule == HOSTILE:
        return hostile_request(p.name, p.area, owned=set(owned_creatures(store, branch_id)))
    if decision.rule == ENTER:
        req = spawn_request(p.cre, p.area, x=p.x, y=p.y, facing=p.facing, templates=templates,
                            count=decision.count, to_x=p.walk_x, to_y=p.walk_y)
        if req.name != p.name:                     # the file holds another name of ours
            raise ActionError('TEMPLATE_NAME_MISMATCH')
        return req
    owned = set(owned_creatures(store, branch_id))
    if p.leave == LEAVE_ESCAPE:                    # ADR-0144: out by the nearest exit
        return escape_request(p.name, p.area, owned=owned)
    return despawn_request(p.name, p.area, owned=owned)



def arrival_plan(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest], *,
                 area: str | None, game_time: int | None, templates: dict[str, str]
                 ) -> tuple[tuple[Decision, ActionRequest], ...]:
    """ADR-0145: the creations the quests need in areas the party is not in now, for the module
    to make the moment one of them loads. Each request's `count` is how many must be there; a
    presence already filled, held, awaiting its defeat or meant for another time is left out."""
    out: list[tuple[Decision, ActionRequest]] = []
    for quest in quests.values():
        for p in quest.presence:
            if p.area == area:
                continue
            state = state_of(store, branch_id, quest.quest_id)
            # entering p.area will do that area's arrival steps (ADR-0139): count them as done,
            # so a presence that starts on arriving is planned before the party walks in
            arriving = {s.step_id for s in quest.steps if s.kind == ARRIVE and s.area == p.area
                        and set(s.after) <= state.steps_done
                        and (not s.night or is_night(game_time))}
            if state.accepted and not state.resolved:
                state = replace(state, steps_done=state.steps_done | arriving)
            fall = next((s for s in quest.steps if s.kind == DEFEATED
                         and s.presence_id == p.presence_id), None)
            if not wanted(state, p, game_time) or (fall is not None
                                                   and fall.step_id in state.steps_done):
                continue
            status = status_of(store, branch_id, quest.quest_id, p)
            if status.blocked or status.filled or status.count >= p.copies:
                continue
            try:
                req = spawn_request(p.cre, p.area, x=p.x, y=p.y, facing=p.facing,
                                    templates=templates, count=p.copies, to_x=p.walk_x,
                                    to_y=p.walk_y)
            except ActionError:
                continue
            if req.name == p.name:
                out.append((Decision(quest.quest_id, p, ENTER, count=p.copies), req))
    return tuple(out)


def record_arrival(store: CampaignStore, branch_id: str, decision: Decision, req: ActionRequest,
                   receipt: ActionReceipt | None, *, game_time: int, host_epoch: int = 0,
                   arrival_made: int | None = None) -> str:
    """ADR-0145: what the module did on entering, recorded as the director would have: a SPAWN of
    the copies it created, or a COUNT when the save already held them all. Anything else (no
    answer, a refusal, a count that does not add up) holds the presence, as any ENTER would."""
    cause = decision.cause()
    if receipt is not None and receipt.status == DONE and receipt.before is not None \
            and receipt.observed is not None:
        made = receipt.observed - receipt.before
        # every presence of one arrival is made in the same instant, so the area's total rises by
        # all of them together (lab, 2026-11-24: Gregor +1 and the jailers +2, the area +3); the
        # total holds when it rose by exactly what the whole arrival made
        if arrival_made is not None and receipt.seen is not None \
                and receipt.seen_before is not None \
                and receipt.seen - receipt.seen_before == arrival_made and made >= 0:
            cause = dict(cause, arrival_made=str(arrival_made))
            receipt = ActionReceipt(receipt.action_id, receipt.status, receipt.observed,
                                    receipt.reason, receipt.before, receipt.seen,
                                    receipt.seen - made)
        if made == 0 and receipt.observed >= decision.presence.copies:
            done = count_request(req.name, req.area, action_id=req.action_id)
        elif made >= 1:
            done = replace(req, count=made)
        else:
            done = req
    else:
        done = req
    record_requested(store, branch_id, done, game_time=game_time, host_epoch=host_epoch,
                     cause=cause)
    state = record_result(store, branch_id, done, receipt, game_time=game_time,
                          host_epoch=host_epoch, cause=cause)
    if state != 'HOST_CONFIRMED':
        record_suspended(store, branch_id, decision, state, game_time=game_time,
                         key=req.action_id, host_epoch=host_epoch)
    return state


def open_passages(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest]
                  ) -> tuple[PassageEntry, ...]:
    """ADR-0146: the passages the quests have opened on this branch (accepted, not resolved, and
    their steps done), each with a stable id for the module's answers."""
    out: list[PassageEntry] = []
    for quest in quests.values():
        if not quest.passages:
            continue
        state = state_of(store, branch_id, quest.quest_id)
        if not state.accepted or state.resolved:
            continue
        for p in quest.passages:
            if set(p.after) <= state.steps_done:
                pid = hashlib.sha1(f'{quest.quest_id}|{p.passage_id}'.encode()).hexdigest()[:10]
                out.append(check_passage(PassageEntry(pid, p.area, p.x, p.y, p.to, p.to_x,
                                                      p.to_y, p.facing)))
    return tuple(out)

def call_due(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest], *,
             area: str | None, game_time: int | None) -> NarrativeQuest | None:
    """ADR-0144: a quest whose giver should call for help now: not yet accepted, the party in
    the giver's area, and no call since the last entry or load or for `every` ticks."""
    if not area or game_time is None:
        return None
    entries = [e.seq for t in ENTRY_EVENTS for e in store.visible_events(branch_id, t)]
    last_entry = max(entries, default=-1)
    for quest in quests.values():
        call = quest.call
        if call is None or call.area != area:
            continue
        st = state_of(store, branch_id, quest.quest_id)
        if st.accepted or st.resolved:
            continue
        calls = [e for e in store.visible_events(branch_id, REQUESTED)
                 if e.payload.get('op') == CALL and isinstance(e.payload.get('cause'), dict)
                 and e.payload['cause'].get('quest_id') == quest.quest_id]
        last = calls[-1] if calls else None
        if last is None or last.seq < last_entry or last.game_time is None \
                or game_time - last.game_time >= call.every:
            return quest
    return None


def dispatch_call(store: CampaignStore, branch_id: str, quest: NarrativeQuest, *,
                  transport: Transport, game_time: int, host_epoch: int = 0) -> str:
    """Ask the game for the giver's call once. Nothing is held whatever the answer: the call
    only tries again at its next turn (display only, ADR-0144)."""
    call = quest.call
    req = call_request(call.script_name, call.area, call.strref,
                       declared={(call.script_name, call.strref)})
    cause = {'policy': POLICY, 'quest_id': quest.quest_id, 'rule': CALL}
    record_requested(store, branch_id, req, game_time=game_time, host_epoch=host_epoch,
                     cause=cause)
    receipt = transport.send(req)
    return record_result(store, branch_id, req, receipt, game_time=game_time,
                         host_epoch=host_epoch, cause=cause)


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


def _reward_events(store: CampaignStore, branch_id: str, quest_id: str, event_type: str) -> list:
    return [e for e in store.visible_events(branch_id, event_type)
            if e.payload.get('op') == REWARD and isinstance(e.payload.get('cause'), dict)
            and e.payload['cause'].get('quest_id') == quest_id]


def reward_status(store: CampaignStore, branch_id: str, quest_id: str) -> str | None:
    """ADR-0148: PAID (the game confirmed), HELD (asked, not confirmed: the maintainer looks at
    the game) or None (never asked on this branch)."""
    if _reward_events(store, branch_id, quest_id, CONFIRMED):
        return 'PAID'
    return 'HELD' if _reward_events(store, branch_id, quest_id, REQUESTED) else None


def reward_due(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest]
               ) -> NarrativeQuest | None:
    """ADR-0148: a resolved quest with a reward never asked on this branch (never twice: an
    unconfirmed payment stays held)."""
    for quest in quests.values():
        if (quest.reward_gold or quest.reward_xp) \
                and state_of(store, branch_id, quest.quest_id).resolved \
                and reward_status(store, branch_id, quest.quest_id) is None:
            return quest
    return None


def dispatch_reward(store: CampaignStore, branch_id: str, quest: NarrativeQuest, *,
                    transport: Transport, area: str, game_time: int, host_epoch: int = 0) -> str:
    """Ask the game to pay once, recording the request first; returns the gateway state."""
    req = reward_request(area, gold=quest.reward_gold, xp=quest.reward_xp)
    cause = {'policy': POLICY, 'quest_id': quest.quest_id, 'rule': REWARD}
    record_requested(store, branch_id, req, game_time=game_time, host_epoch=host_epoch,
                     cause=cause)
    receipt = transport.send(req)
    return record_result(store, branch_id, req, receipt, game_time=game_time,
                         host_epoch=host_epoch, cause=cause)


__all__ = ['ENTER', 'LEAVE', 'VERIFY', 'DEFEAT_WATCH', 'DEFEAT', 'HOSTILE', 'SUSPENDED', 'RESUMED', 'Decision', 'PresenceStatus', 'Transport',
           'arrival_plan', 'call_due', 'open_passages', 'decide', 'record_arrival', 'dispatch', 'dispatch_call', 'record_resumed', 'record_suspended', 'request_for', 'status_of',
           'wanted', 'reward_due', 'reward_status', 'dispatch_reward']
