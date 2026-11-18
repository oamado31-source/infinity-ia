# SPDX-License-Identifier: Apache-2.0
"""SPEC-011 / ADR-0135: narrative quests, curated by the project, carried by the dialogue box.

A narrative quest happens only in conversations: nothing is written to the game.

- The code decides everything: that the giver offers (the player asks for work or help), that the
  player accepted, that a step was done (the player asked the step's person about its subject),
  that the quest is resolved (the player came back to the giver with every step done). The model
  only voices the curated fact each person receives for that turn.
- Every change is one event per branch, idempotent, without the player's text (ADR-0107): an older
  save reloaded opens another branch and the quest is where it was at that point.
- Resolution records the quest's milestone (`QuestMilestoneObserved`, source OVERLAY, ADR-0134);
  curations say what it does to trust (rule MILESTONE).
- A step's fact never reaches a prompt before the quest is accepted (REQ-QUEST-006).
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from ..state.store import CampaignStore
from .milestones import record_overlay_milestone

QUEST_SCHEMA = 'infinity-ai.narrative-quest.v1'
POLICY = 'spec-011-narrative-quest-v1'
OFFERED, ACCEPTED = 'NarrativeQuestOffered', 'NarrativeQuestAccepted'
STEP_DONE, RESOLVED = 'NarrativeQuestStepDone', 'NarrativeQuestResolved'
QUEST_EVENTS = (OFFERED, ACCEPTED, STEP_DONE, RESOLVED)
DEFAULT_QUEST_DIR = Path(__file__).resolve().parents[3] / 'knowledge' / 'quests'
MAX_FACT, MAX_JOURNAL = 400, 200

_ID = re.compile(r'[a-z0-9][a-z0-9-]{0,47}')
_NPC = re.compile(r'npc:[a-z0-9_#*-]{1,40}')
_AREA = re.compile(r'[A-Z0-9]{1,8}')


@dataclass(frozen=True)
class Step:
    step_id: str
    npc_id: str
    cues: tuple[str, ...]
    fact: str
    journal: str


@dataclass(frozen=True)
class NarrativeQuest:
    quest_id: str
    title: str
    area: str | None
    giver: str
    offer_cues: tuple[str, ...]
    offer_fact: str
    accept_cues: tuple[str, ...]
    waiting_fact: str
    accept_journal: str
    steps: tuple[Step, ...]
    turn_in_cues: tuple[str, ...]
    turn_in_fact: str
    turn_in_journal: str
    milestone: str


def _norm(text: str) -> str:
    return unicodedata.normalize('NFC', (text or '').lower())


def says(text: str, cues: tuple[str, ...]) -> bool:
    """A cue is a whole word or phrase; ending in `*` it is the start of a word ("furt*")."""
    low = _norm(text)
    for cue in cues:
        stem = cue[:-1] if cue.endswith('*') else cue
        tail = '' if cue.endswith('*') else r'\b'
        if re.search(r'\b' + re.escape(_norm(stem)) + tail, low):
            return True
    return False


def _cues(raw: object) -> tuple[str, ...] | None:
    if not isinstance(raw, list) or not raw or not all(
            isinstance(c, str) and c.strip() and len(c) <= 40 for c in raw):
        return None
    return tuple(c.strip() for c in raw)


def _text(raw: object, limit: int) -> str | None:
    return raw.strip() if isinstance(raw, str) and 0 < len(raw.strip()) <= limit else None


def parse_quest(doc: object) -> NarrativeQuest | None:
    """A checked, strictly valid quest, or None."""
    if not isinstance(doc, dict) or doc.get('schema') != QUEST_SCHEMA:
        return None
    check = doc.get('curation') or {}
    if check.get('status') != 'CHECKED' or not check.get('checked_by') or not check.get('checked_at'):
        return None
    qid, area = doc.get('quest_id'), doc.get('area')
    giver, turn_in = doc.get('giver'), doc.get('turn_in')
    if not isinstance(qid, str) or not _ID.fullmatch(qid) or not isinstance(giver, dict) \
            or not isinstance(turn_in, dict) or (area is not None and (
                not isinstance(area, str) or not _AREA.fullmatch(area))):
        return None
    if doc.get('milestone') != f'quest:{qid}:RESOLVED':
        return None
    raw_steps = doc.get('steps')
    if not isinstance(raw_steps, list) or not raw_steps:
        return None
    steps = []
    for s in raw_steps:
        if not isinstance(s, dict):
            return None
        sid, npc = s.get('step_id'), s.get('npc_id')
        cues, fact, journal = _cues(s.get('cues')), _text(s.get('fact'), MAX_FACT), \
            _text(s.get('journal'), MAX_JOURNAL)
        if not isinstance(sid, str) or not _ID.fullmatch(sid) or not isinstance(npc, str) \
                or not _NPC.fullmatch(npc) or None in (cues, fact, journal) \
                or sid in {x.step_id for x in steps}:
            return None
        steps.append(Step(sid, npc, cues, fact, journal))
    fields = (_text(doc.get('title'), 80), giver.get('npc_id'), _cues(giver.get('offer_cues')),
              _text(giver.get('offer_fact'), MAX_FACT), _cues(giver.get('accept_cues')),
              _text(giver.get('waiting_fact'), MAX_FACT),
              _text(giver.get('accept_journal'), MAX_JOURNAL), _cues(turn_in.get('cues')),
              _text(turn_in.get('fact'), MAX_FACT), _text(turn_in.get('journal'), MAX_JOURNAL))
    if None in fields or not isinstance(fields[1], str) or not _NPC.fullmatch(fields[1]) \
            or any(s.npc_id == fields[1] for s in steps):
        return None
    title, giver_id, offer_cues, offer_fact, accept_cues, waiting, accept_journal, \
        turn_cues, turn_fact, turn_journal = fields
    return NarrativeQuest(qid, title, area, giver_id, offer_cues, offer_fact, accept_cues,
                          waiting, accept_journal, tuple(steps), turn_cues, turn_fact,
                          turn_journal, doc['milestone'])


def load_quests(base: Path = DEFAULT_QUEST_DIR) -> dict[str, NarrativeQuest]:
    out: dict[str, NarrativeQuest] = {}
    for path in sorted(Path(base).glob('*.json')):
        try:
            quest = parse_quest(json.loads(path.read_text(encoding='utf-8')))
        except (OSError, ValueError):
            continue
        if quest is not None and quest.quest_id not in out:
            out[quest.quest_id] = quest
    return out


@dataclass(frozen=True)
class QuestState:
    offered: bool = False
    accepted: bool = False
    steps_done: frozenset[str] = frozenset()
    resolved: bool = False

    def label(self) -> str:
        if self.resolved:
            return 'RESOLVIDA'
        if self.accepted:
            return f'ACEITA({len(self.steps_done)})'
        return 'OFERECIDA' if self.offered else 'NOVA'


def state_of(store: CampaignStore, branch_id: str, quest_id: str) -> QuestState:
    seen = {t: [] for t in QUEST_EVENTS}
    for event_type in QUEST_EVENTS:
        seen[event_type] = [e for e in store.visible_events(branch_id, event_type)
                            if e.payload.get('quest_id') == quest_id]
    return QuestState(bool(seen[OFFERED]), bool(seen[ACCEPTED]),
                      frozenset(e.payload.get('step_id') for e in seen[STEP_DONE]),
                      bool(seen[RESOLVED]))


@dataclass(frozen=True)
class QuestTurn:
    facts: tuple[str, ...] = ()        # what this person may tell this turn (SOBRE VOCÊ)
    journal: tuple[str, ...] = ()      # lines for the box: "(Diário: ...)"
    changes: tuple[str, ...] = ()      # "quest_id:EVENT" recorded now, for the log
    milestones: tuple[str, ...] = ()   # milestones recorded now
    states: tuple[str, ...] = ()       # "quest_id=LABEL" of the quests this person is part of


def _record(store, branch_id, event_type, quest, *, game_time, host_epoch, evidence,
            step_id: str | None = None) -> None:
    payload = {'quest_id': quest.quest_id, 'policy': POLICY}
    key = f'nquest|{branch_id}|{quest.quest_id}|{event_type}'
    if step_id is not None:
        payload['step_id'] = step_id
        key += f'|{step_id}'
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=host_epoch, event_type=event_type,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
                           evidence=evidence, idempotency_key=key)


def advance(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest], *,
            speaker: str, text: str, area: str | None, game_time: int | None,
            host_epoch: int = 0, evidence: str = 'LAB_OBSERVED',
            closed: bool = False) -> QuestTurn:
    """Move every quest this person is part of by what the player said; return its facts.
    `closed`: the person's encounter disposition tells nothing (threatening, hostile, fleeing,
    ADR-0125). Then no quest moves and no fact is given: an offer recorded but never said would
    leave the quest ahead of the conversation (lab, 2026-11-18)."""
    facts: list[str] = []
    journal: list[str] = []
    changes: list[str] = []
    milestones: list[str] = []
    states: list[str] = []
    for quest in quests.values():
        step_of = {s.npc_id: s for s in quest.steps}
        if speaker != quest.giver and speaker not in step_of:
            continue
        if quest.area is not None and area != quest.area:
            continue
        st = state_of(store, branch_id, quest.quest_id)
        if closed:
            states.append(f'{quest.quest_id}={st.label()}')
            continue

        def mark(event_type: str, step_id: str | None = None) -> None:
            _record(store, branch_id, event_type, quest, game_time=game_time,
                    host_epoch=host_epoch, evidence=evidence, step_id=step_id)
            changes.append(f'{quest.quest_id}:{event_type}')

        if speaker == quest.giver:
            if st.resolved:
                facts.append(quest.turn_in_fact)
            elif not st.offered:
                if says(text, quest.offer_cues):
                    mark(OFFERED)
                    facts.append(quest.offer_fact)
            elif not st.accepted:
                facts.append(quest.offer_fact)
                if says(text, quest.accept_cues):
                    mark(ACCEPTED)
                    facts.append(quest.waiting_fact)
                    journal.append(quest.accept_journal)
            elif st.steps_done >= {s.step_id for s in quest.steps} \
                    and says(text, quest.turn_in_cues):
                mark(RESOLVED)
                record_overlay_milestone(store, branch_id, quest.milestone,
                                         quest_id=quest.quest_id, game_time=game_time,
                                         host_epoch=host_epoch, evidence=evidence)
                milestones.append(quest.milestone)
                facts.append(quest.turn_in_fact)
                journal.append(quest.turn_in_journal)
            else:
                facts.append(quest.waiting_fact)
        else:
            step = step_of[speaker]
            if step.step_id in st.steps_done:
                facts.append(step.fact)
            elif st.accepted and not st.resolved and says(text, step.cues):
                mark(STEP_DONE, step.step_id)
                facts.append(step.fact)
                journal.append(step.journal)
        states.append(f'{quest.quest_id}={state_of(store, branch_id, quest.quest_id).label()}')
    return QuestTurn(tuple(facts), tuple(journal), tuple(changes), tuple(milestones),
                     tuple(states))


def with_journal(speech: str, journal: tuple[str, ...]) -> str:
    """The reply with the box's journal lines (REQ-QUEST-009); nothing goes to the game journal."""
    lines = ' '.join(f'(Diário: {line})' for line in journal)
    return f'{speech} {lines}' if lines else speech
