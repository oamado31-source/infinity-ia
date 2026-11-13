# SPDX-License-Identifier: Apache-2.0
"""ADR-0124: what an NPC remembers of earlier conversations with the player, without any text.

Each answered turn records one `NpcConversationTurn` event: who spoke (`npc_key`), in which
conversation (one box opening, ADR-0123) and which pack entries the person used in its validated
speech. Nothing the player or the NPC said is stored. Recall reads the events visible on the
branch (save/load respected) and gives the number of earlier conversations, when the last one was
and the most recent subjects.

People without a script name share one id across copies on the map, so they are remembered by
the game's instance in this session only (`<id>@<session>#<instance>`): after the game is
reopened they are someone else. Official, curated people and companions are remembered always.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..state.store import CampaignStore, Event

TURN_EVENT = 'NpcConversationTurn'
MAX_SUBJECTS = 4
DAY = 7200          # game-time units in one day (SPEC-003 lab evidence)


@dataclass(frozen=True)
class Recall:
    conversations: int                 # earlier conversations (the current one excluded)
    last_game_time: int | None
    subjects: tuple[str, ...]          # entry ids, most recent first
    event_ids: tuple[str, ...]         # events behind this recall (for fact ids)

    def __bool__(self) -> bool:
        return self.conversations > 0


NO_RECALL = Recall(0, None, (), ())


def npc_key(speaker_id: str, *, stable: bool, session_seq: int | None,
            instance: int | None) -> str:
    """Who is remembered: the person itself when it is unique (script name, curated, companion),
    otherwise this copy on the map in this game session only."""
    if not speaker_id:
        return ''
    if stable:
        return speaker_id
    if session_seq is None or instance is None:
        return ''                                   # cannot tell copies apart: remember nothing
    return f'{speaker_id}@{session_seq}#{instance}'


def record_turn(store: CampaignStore, branch_id: str, *, key: str, speaker_id: str,
                conversation_id: str | None, req_id: str, entries: Iterable[str],
                game_time: int, host_epoch: int, evidence: str = 'LAB_OBSERVED') -> Event | None:
    """One idempotent event per answered turn; ids and game time only, never text."""
    if not key or not conversation_id or not req_id:
        return None
    payload = {'npc_key': key, 'speaker_id': speaker_id, 'conversation_id': conversation_id,
               'req_id': req_id, 'entries': sorted(dict.fromkeys(entries))}
    with store.transaction():
        event, _ = store.append_event(
            branch_id=branch_id, host_epoch=host_epoch, event_type=TURN_EVENT,
            category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
            evidence=evidence, idempotency_key=f'talk-turn|{branch_id}|{req_id}')
    return event


def recall(store: CampaignStore, branch_id: str, key: str, *, at_game_time: int | None,
           exclude_conversation: str | None = None) -> Recall:
    if not key:
        return NO_RECALL
    turns = [e for e in store.visible_events(branch_id, TURN_EVENT)
             if e.payload.get('npc_key') == key
             and e.payload.get('conversation_id') != exclude_conversation
             and (at_game_time is None or e.game_time is None or e.game_time <= at_game_time)]
    if not turns:
        return NO_RECALL
    conversations = {e.payload.get('conversation_id') for e in turns}
    subjects: list[str] = []
    for event in reversed(turns):                    # most recent first
        for entry in event.payload.get('entries') or ():
            if entry not in subjects:
                subjects.append(entry)
    times = [e.game_time for e in turns if e.game_time is not None]
    return Recall(len(conversations), max(times) if times else None,
                  tuple(subjects[:MAX_SUBJECTS]), tuple(e.event_id for e in turns))


def days_ago(last_game_time: int | None, now: int | None) -> int | None:
    if last_game_time is None or now is None:
        return None
    return max(0, (now - last_game_time) // DAY)


def recall_lines(rec: Recall, titles: dict[str, str], now: int | None) -> tuple[tuple[str, str], ...]:
    """(event id, sentence) "SOBRE VOCÊ" facts for the prompt; empty without earlier talks."""
    if not rec:
        return ()
    days = days_ago(rec.last_game_time, now)
    when = '' if days is None else (', a última hoje' if days == 0 else
                                    f', a última há {days} dia' + ('s' if days > 1 else ''))
    times = 'uma vez' if rec.conversations == 1 else f'{rec.conversations} vezes'
    anchor = rec.event_ids[-1]
    lines = [(f'recall:{anchor}', f'Você já conversou com o jogador antes ({times}{when}).')]
    named = [titles[e] for e in rec.subjects if titles.get(e)]
    if named:
        lines.append((f'recall:{anchor}:assuntos', 'Vocês falaram sobre: ' + ', '.join(named) + '.'))
    return tuple(lines)
