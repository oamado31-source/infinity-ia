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
- ADR-0138: a quest may declare who must be on the map while it runs (`presence`); the presence
  director (`quests/presence.py`) asks the action gateway for it. The quest file only declares.
- ADR-0140: a step may be done when a presence of the quest falls (`defeated`: its count in the game
  drops to zero without the quest removing it), and a presence may have several copies.
- ADR-0139: a step may be done by arriving somewhere (`arrive`, optionally only at night), steps may
  require others first (`after`), and a talk step may name its own area. Arrival steps are recorded
  by the service's observer, with their journal line on the box's next reply.
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
_CRE = re.compile(r'IA[A-Z0-9]{1,6}')
_OWN_NAME = re.compile(r'INFAI_[A-Z0-9_]{1,26}')
START_ACCEPTED, END_RESOLVED = 'ACCEPTED', 'RESOLVED'
TALK, ARRIVE, DEFEATED = 'TALK', 'ARRIVE', 'DEFEATED'
WHEN_ANY, WHEN_NIGHT = 'ANY', 'NIGHT'
JOURNAL_SHOWN = 'NarrativeQuestJournalShown'


@dataclass(frozen=True)
class Step:
    step_id: str
    npc_id: str | None                 # TALK: the person to ask; ARRIVE: None
    cues: tuple[str, ...]
    fact: str | None                   # TALK: what that person may tell; ARRIVE: None
    journal: str
    kind: str = TALK
    area: str | None = None            # ARRIVE: where; TALK: optional, where the person is
    night: bool = False                # ARRIVE: only at night (ADR-0139 D1)
    after: tuple[str, ...] = ()        # steps that must be done first
    presence_id: str | None = None     # DEFEATED (ADR-0140): the presence whose count falls to 0


@dataclass(frozen=True)
class Presence:
    """ADR-0138: one of our creatures that must be in an area while the quest is between two
    points: from `start` (ACCEPTED or a step id done) until `end` (RESOLVED or a step id done)."""
    presence_id: str
    cre: str                  # our creature file (IA*)
    name: str                 # the script name inside it (INFAI_*)
    area: str
    start: str
    end: str
    x: int = -1               # -1: near the party leader (D2)
    y: int = -1
    facing: int = 0
    when: str = WHEN_ANY      # ADR-0139: ANY, or NIGHT (only at night; gone at dawn, D2)
    copies: int = 1           # ADR-0140: how many, created one at a time up to this count


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
    presence: tuple[Presence, ...] = ()


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


def _presence(raw: object, step_ids: set[str]) -> tuple[Presence, ...] | None:
    """The quest's presence list (ADR-0138), strictly; None drops the whole quest."""
    if raw is None:
        return ()
    if not isinstance(raw, list):
        return None
    points = {START_ACCEPTED} | step_ids, {END_RESOLVED} | step_ids
    out: list[Presence] = []
    for item in raw:
        if not isinstance(item, dict):
            return None
        pid, cre, name, area = (item.get('presence_id'), item.get('cre'), item.get('name'),
                                item.get('area'))
        start, end = item.get('from', START_ACCEPTED), item.get('until', END_RESOLVED)
        x, y, facing = item.get('x', -1), item.get('y', -1), item.get('facing', 0)
        when = item.get('when', WHEN_ANY)
        copies = item.get('copies', 1)
        numbers = (x, y, facing, copies)
        if not (isinstance(pid, str) and _ID.fullmatch(pid) and isinstance(cre, str)
                and _CRE.fullmatch(cre) and isinstance(name, str) and _OWN_NAME.fullmatch(name)
                and isinstance(area, str) and _AREA.fullmatch(area)
                and start in points[0] and end in points[1] and start != end
                and all(isinstance(n, int) and not isinstance(n, bool) for n in numbers)
                and -1 <= x <= 32767 and -1 <= y <= 32767 and (x < 0) == (y < 0)
                and 0 <= facing <= 15 and when in (WHEN_ANY, WHEN_NIGHT) and 1 <= copies <= 8):
            return None
        if pid in {o.presence_id for o in out} or name in {o.name for o in out}:
            return None
        out.append(Presence(pid, cre, name, area, start, end, x, y, facing, when, copies))
    return tuple(out)


def _step(s: object, earlier: set[str]) -> Step | None:
    """One step, strictly: TALK (a person, cues, a fact) or ARRIVE (an area, maybe at night).
    `after` may only name earlier steps, so the order can never loop."""
    if not isinstance(s, dict):
        return None
    sid, journal, after = s.get('step_id'), _text(s.get('journal'), MAX_JOURNAL), s.get('after', [])
    if not isinstance(sid, str) or not _ID.fullmatch(sid) or sid in earlier or journal is None \
            or not isinstance(after, list) or not all(isinstance(a, str) and a in earlier
                                                      for a in after):
        return None
    after = tuple(dict.fromkeys(after))
    if 'defeated' in s:                        # ADR-0140: checked against the presences later
        fell = s['defeated']
        if not isinstance(fell, dict) or set(fell) != {'presence'} \
                or not isinstance(fell['presence'], str) or not _ID.fullmatch(fell['presence']) \
                or any(k in s for k in ('npc_id', 'cues', 'fact', 'arrive')):
            return None
        return Step(sid, None, (), None, journal, DEFEATED, None, False, after, fell['presence'])
    if 'arrive' in s:
        where = s['arrive']
        if not isinstance(where, dict) or set(where) - {'area', 'night'} \
                or not isinstance(where.get('area'), str) or not _AREA.fullmatch(where['area']) \
                or not isinstance(where.get('night', False), bool) \
                or any(k in s for k in ('npc_id', 'cues', 'fact')):
            return None
        return Step(sid, None, (), None, journal, ARRIVE, where['area'],
                    where.get('night', False), after)
    npc, cues, fact, area = s.get('npc_id'), _cues(s.get('cues')), \
        _text(s.get('fact'), MAX_FACT), s.get('area')
    if not isinstance(npc, str) or not _NPC.fullmatch(npc) or None in (cues, fact) \
            or (area is not None and (not isinstance(area, str) or not _AREA.fullmatch(area))):
        return None
    return Step(sid, npc, cues, fact, journal, TALK, area, False, after)


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
    steps: list[Step] = []
    for s in raw_steps:
        step = _step(s, {x.step_id for x in steps})
        if step is None:
            return None
        steps.append(step)
    fields = (_text(doc.get('title'), 80), giver.get('npc_id'), _cues(giver.get('offer_cues')),
              _text(giver.get('offer_fact'), MAX_FACT), _cues(giver.get('accept_cues')),
              _text(giver.get('waiting_fact'), MAX_FACT),
              _text(giver.get('accept_journal'), MAX_JOURNAL), _cues(turn_in.get('cues')),
              _text(turn_in.get('fact'), MAX_FACT), _text(turn_in.get('journal'), MAX_JOURNAL))
    talkers = [s.npc_id for s in steps if s.kind == TALK]
    if None in fields or not isinstance(fields[1], str) or not _NPC.fullmatch(fields[1]) \
            or fields[1] in talkers or len(talkers) != len(set(talkers)):
        return None
    title, giver_id, offer_cues, offer_fact, accept_cues, waiting, accept_journal, \
        turn_cues, turn_fact, turn_journal = fields
    presence = _presence(doc.get('presence'), {s.step_id for s in steps})
    if presence is None:
        return None
    fallen = [s.presence_id for s in steps if s.kind == DEFEATED]
    if any(f not in {p.presence_id for p in presence} for f in fallen) \
            or len(fallen) != len(set(fallen)):
        return None
    return NarrativeQuest(qid, title, area, giver_id, offer_cues, offer_fact, accept_cues,
                          waiting, accept_journal, tuple(steps), turn_cues, turn_fact,
                          turn_journal, doc['milestone'], presence)


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
        step_of = {s.npc_id: s for s in quest.steps if s.kind == TALK}
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
            elif st.accepted and not st.resolved and set(step.after) <= st.steps_done \
                    and (step.area is None or area == step.area) and says(text, step.cues):
                mark(STEP_DONE, step.step_id)
                facts.append(step.fact)
                journal.append(step.journal)
        states.append(f'{quest.quest_id}={state_of(store, branch_id, quest.quest_id).label()}')
    return QuestTurn(tuple(facts), tuple(journal), tuple(changes), tuple(milestones),
                     tuple(states))


def arrive(store: CampaignStore, branch_id: str, quests: dict[str, NarrativeQuest], *,
           area: str | None, game_time: int | None, night: bool, host_epoch: int = 0,
           evidence: str = 'LAB_OBSERVED') -> tuple[str, ...]:
    """ADR-0139: arrival steps done now that the party is in `area` ("quest_id:step_id").
    Only for an accepted, unresolved quest, with the steps of `after` done, and at night when
    the step asks for it. Recorded once per branch, like any step; no game write."""
    done: list[str] = []
    if not area:
        return ()
    for quest in quests.values():
        if quest.area is not None and area != quest.area:
            continue
        for step in quest.steps:
            st = state_of(store, branch_id, quest.quest_id)
            if not st.accepted or st.resolved:
                break
            if step.kind != ARRIVE or step.step_id in st.steps_done or step.area != area \
                    or (step.night and not night) or not set(step.after) <= st.steps_done:
                continue
            _record(store, branch_id, STEP_DONE, quest, game_time=game_time,
                    host_epoch=host_epoch, evidence=evidence, step_id=step.step_id)
            done.append(f'{quest.quest_id}:{step.step_id}')
    return tuple(done)


def mark_step(store: CampaignStore, branch_id: str, quest: NarrativeQuest, step_id: str, *,
              game_time: int | None, host_epoch: int = 0, evidence: str = 'LAB_OBSERVED') -> None:
    """A step done by code without a conversation (ADR-0140: the defeat seen by the count)."""
    _record(store, branch_id, STEP_DONE, quest, game_time=game_time, host_epoch=host_epoch,
            evidence=evidence, step_id=step_id)


def pending_journal(store: CampaignStore, branch_id: str,
                    quests: dict[str, NarrativeQuest]) -> tuple[tuple[str, str, str], ...]:
    """Steps done without a conversation (arrival, ADR-0139; defeat, ADR-0140) whose journal line
    the box has not shown yet: (quest_id, step_id, line)."""
    shown = {(e.payload.get('quest_id'), e.payload.get('step_id'))
             for e in store.visible_events(branch_id, JOURNAL_SHOWN)}
    out: list[tuple[str, str, str]] = []
    for e in store.visible_events(branch_id, STEP_DONE):
        quest = quests.get(e.payload.get('quest_id'))
        step = next((s for s in quest.steps if s.step_id == e.payload.get('step_id')), None) \
            if quest else None
        if step is not None and step.kind in (ARRIVE, DEFEATED) \
                and (quest.quest_id, step.step_id) not in shown:
            out.append((quest.quest_id, step.step_id, step.journal))
    return tuple(out)


def mark_journal_shown(store: CampaignStore, branch_id: str,
                       items: tuple[tuple[str, str, str], ...], *, game_time: int | None,
                       host_epoch: int = 0, evidence: str = 'LAB_OBSERVED') -> None:
    for quest_id, step_id, _ in items:
        with store.transaction():
            store.append_event(branch_id=branch_id, host_epoch=host_epoch,
                               event_type=JOURNAL_SHOWN, category='CAMPAIGN_OBSERVATION',
                               game_time=game_time, evidence=evidence,
                               payload={'quest_id': quest_id, 'step_id': step_id,
                                        'policy': POLICY},
                               idempotency_key=f'nquest|{branch_id}|{quest_id}|journal|{step_id}')


def with_journal(speech: str, journal: tuple[str, ...]) -> str:
    """The reply with the box's journal lines (REQ-QUEST-009); nothing goes to the game journal."""
    lines = ' '.join(f'(Diário: {line})' for line in journal)
    return f'{speech} {lines}' if lines else speech
