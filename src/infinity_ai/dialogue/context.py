# SPDX-License-Identifier: Apache-2.0
"""SPEC-004 deterministic dialogue context: what an NPC may say comes only from its recall.

REQ-VOICE-005: the context is built from `MemoryStore.recall` (NPC, branch, time, audience
already enforced) and rendered as numbered facts. Common regional knowledge the NPC acquired
under ADR-0114 (`MemoryStore.recall_common`) is rendered separately as K-items, from the snapshot
taken at acquisition; canon the NPC has not acquired never reaches the context. Area codes never
reach the text; unknown areas are presented as unnamed places. Companions currently in the party
are talked to through the overlay; anyone alive met in the game through the in-game box
(ADR-0116), shaped by a SPEC-006 profile and holding only the common knowledge it acquired.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..memory.common_knowledge import BackgroundRegion
from ..personality.style import orientation_from_profile, style_from_profile
from ..memory.model import RecallStatus
from ..memory.store import MemoryStore
from ..state.store import CampaignStore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PERSONA_DIR = ROOT / 'knowledge' / 'personas'
DEFAULT_AREA_NAMES = ROOT / 'knowledge' / 'areas' / 'bg2ee-area-names.pt_BR.json'
UNNAMED_AREA = 'um lugar que você não sabe nomear'
MAX_FACTS = 20
MAX_KNOWLEDGE = 12
_NAME = re.compile(r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'-]*")
GENERIC_FALLBACK = 'Hum... não sei bem o que dizer agora.'


class ContextStatus(str, Enum):
    OK = 'OK'
    DENIED = 'DENIED'


@dataclass(frozen=True)
class Persona:
    npc_id: str
    display_name: str
    style: tuple[str, ...]
    vocabulary: frozenset[str]
    fallback: str = GENERIC_FALLBACK
    background: tuple[BackgroundRegion, ...] = ()


@dataclass(frozen=True)
class Fact:
    fact_id: str
    event_id: str
    text: str
    game_time: int


@dataclass(frozen=True)
class DialogueContext:
    persona: Persona
    facts: tuple[Fact, ...]
    vocabulary: frozenset[str]
    companions: tuple[str, ...]
    knowledge: tuple[Fact, ...] = ()
    resident_of: str | None = None   # set for a person met in the game (ADR-0116): where
    orientation: str | None = None   # SPEC-006 alignment orientation, when a profile applies


@dataclass(frozen=True)
class ContextResult:
    status: ContextStatus
    reason: str
    context: DialogueContext | None = None


@dataclass
class Catalog:
    personas: dict[str, Persona] = field(default_factory=dict)
    area_names: dict[str, str] = field(default_factory=dict)
    game_area_names: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, persona_dir: Path = DEFAULT_PERSONA_DIR,
             area_names: Path = DEFAULT_AREA_NAMES,
             game_area_names: dict[str, str] | None = None) -> Catalog:
        """`game_area_names`: names read from the local install (SPEC-005 inventory, S0); they
        take precedence over the provisional curated names."""
        personas = {}
        for path in sorted(Path(persona_dir).glob('*.json')):
            doc = json.loads(path.read_text(encoding='utf-8'))
            personas[doc['npc_id']] = Persona(doc['npc_id'], doc['display_name'],
                                              tuple(doc.get('style', ())),
                                              frozenset(doc.get('vocabulary', ())),
                                              doc.get('fallback') or GENERIC_FALLBACK,
                                              _background(doc))
        areas = json.loads(Path(area_names).read_text(encoding='utf-8')).get('areas', {})
        return cls(personas, dict(areas), dict(game_area_names or {}))

    def backgrounds(self) -> dict[str, tuple[BackgroundRegion, ...]]:
        return {n: p.background for n, p in self.personas.items() if p.background}

    def persona(self, npc_id: str) -> Persona:
        if npc_id in self.personas:
            return self.personas[npc_id]
        name = npc_id.split(':', 1)[-1].capitalize()
        return Persona(npc_id, name, (), frozenset({name}))

    def display(self, npc_id: str) -> str:
        return self.persona(npc_id).display_name

    def area(self, resref: str | None) -> str:
        key = resref or ''
        return self.game_area_names.get(key) or self.area_names.get(key, UNNAMED_AREA)


def _background(doc: dict) -> tuple[BackgroundRegion, ...]:
    """Curated ORIGIN regions; incomplete records are dropped (the rule rechecks the source)."""
    out = []
    for b in doc.get('background_regions') or ():
        try:
            out.append(BackgroundRegion(b['region_id'], b['source_id'], b['locator'],
                                        (b.get('curation') or {}).get('checked_by', ''),
                                        (b.get('curation') or {}).get('checked_at', '')))
        except (KeyError, TypeError):
            continue
    return tuple(out)


def current_companions(store: CampaignStore, branch_id: str) -> tuple[str, ...] | None:
    changes = store.visible_events(branch_id, 'PartyChanged')
    return tuple(changes[-1].payload['members']) if changes else None


def _names(npc_ids: list[str], catalog: Catalog) -> str:
    names = [catalog.display(n) for n in npc_ids]
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' e ' + names[-1]


def _render(claim_type: str, payload: dict, catalog: Catalog) -> list[str]:
    if claim_type == 'AreaEntered':
        return [f'O grupo entrou em {catalog.area(payload.get("area"))}.']
    if claim_type == 'PartyChanged':
        members = list(payload.get('members') or [])
        previous = payload.get('previous')
        if previous is None:
            return [f'O grupo era formado por você e {_names(members, catalog)}.' if members
                    else 'Você estava sem companheiros.']
        lines = []
        joined = [m for m in members if m not in previous]
        left = [m for m in previous if m not in members]
        if joined:
            lines.append(f'{_names(joined, catalog)} entrou no grupo.' if len(joined) == 1
                         else f'{_names(joined, catalog)} entraram no grupo.')
        if left:
            lines.append(f'{_names(left, catalog)} saiu do grupo.' if len(left) == 1
                         else f'{_names(left, catalog)} saíram do grupo.')
        return lines
    return []


RESIDENT_STYLE = ('direto e desconfiado de estranhos', 'fala como gente da cidade')
RESIDENT_FALLBACK = 'Hum? Disso eu não sei, forasteiro.'


def _knowledge_items(memory: MemoryStore, npc_id: str, branch_id: str, at_game_time: int | None,
                     vocabulary: set[str]) -> tuple[RecallStatus, str, tuple[Fact, ...]]:
    status, reason, held = memory.recall_common(npc_id=npc_id, branch_id=branch_id,
                                                at_game_time=at_game_time,
                                                purpose='npc_dialogue',
                                                audience='NARRATIVE_CONTEXT')
    if status is not RecallStatus.OK:
        return status, reason, ()
    knowledge = []
    for i, k in enumerate(held[:MAX_KNOWLEDGE], 1):
        knowledge.append(Fact(f'K{i}', f'canon:{k.entry_id}', f'{k.title}: {k.summary}',
                              k.game_time))
        vocabulary |= set(_NAME.findall(k.title)) | set(_NAME.findall(k.summary))
    return status, reason, tuple(knowledge)


def build_resident_context(memory: MemoryStore, store: CampaignStore, catalog: Catalog, *,
                           npc_id: str, display_name: str, residence_areas: tuple[str, ...],
                           area: str | None, dead: bool, branch_id: str,
                           at_game_time: int | None,
                           profile: dict | None = None) -> ContextResult:
    """A person the player addresses in the game (ADR-0116, SPEC-006): no party memories.

    Anyone alive in the current area may talk; only what the person acquired (ADR-0114/0116,
    e.g. a local placed by the game data) reaches CONHECIMENTO GERAL. A SPEC-006 `profile`, when
    given, sets the speaking style and the alignment orientation; it never adds facts."""
    if dead:
        return ContextResult(ContextStatus.DENIED, 'SPEAKER_DEAD')
    if area is None:
        return ContextResult(ContextStatus.DENIED, 'NPC_NOT_PRESENT')
    if residence_areas and area.upper() not in {a.upper() for a in residence_areas}:
        return ContextResult(ContextStatus.DENIED, 'NPC_NOT_PRESENT')
    name = display_name.strip() or npc_id.split(':', 1)[-1].capitalize()
    style = style_from_profile(profile) if profile else RESIDENT_STYLE
    orientation = orientation_from_profile(profile) if profile else None
    persona = Persona(npc_id, name, style, frozenset({name}), RESIDENT_FALLBACK)
    place = catalog.area(area)
    vocabulary = {name} | {w for w in place.split() if w[:1].isupper()}
    status, reason, knowledge = _knowledge_items(memory, npc_id, branch_id, at_game_time,
                                                 vocabulary)
    if status is not RecallStatus.OK:
        return ContextResult(ContextStatus.DENIED, reason)
    return ContextResult(ContextStatus.OK, 'OK', DialogueContext(
        persona, (), frozenset(vocabulary), (), knowledge, place, orientation))


def build_context(memory: MemoryStore, store: CampaignStore, catalog: Catalog, *, npc_id: str,
                  branch_id: str, at_game_time: int | None) -> ContextResult:
    companions = current_companions(store, branch_id)
    if companions is None:
        return ContextResult(ContextStatus.DENIED, 'PARTY_UNKNOWN')
    if npc_id not in companions:
        return ContextResult(ContextStatus.DENIED, 'NPC_NOT_PRESENT')
    recalled = memory.recall(npc_id=npc_id, branch_id=branch_id, at_game_time=at_game_time,
                             purpose='npc_dialogue', audience='NARRATIVE_CONTEXT')
    if recalled.status is not RecallStatus.OK:
        return ContextResult(ContextStatus.DENIED, recalled.reason)

    facts: list[Fact] = []
    vocabulary = set(catalog.persona(npc_id).vocabulary) | {catalog.display(npc_id)}
    for item in recalled.items:
        for text in _render(item.claim_type, item.claim_payload, catalog):
            facts.append(Fact('', item.experience.claim_event_id, text, item.experience.game_time))
        for member in (item.claim_payload.get('members') or []) + \
                (item.claim_payload.get('previous') or []):
            vocabulary |= catalog.persona(member).vocabulary | {catalog.display(member)}
        if item.claim_type == 'AreaEntered':
            vocabulary |= {w for w in catalog.area(item.claim_payload.get('area')).split()
                           if w[:1].isupper()}
    for member in companions:
        vocabulary |= catalog.persona(member).vocabulary | {catalog.display(member)}
    facts = facts[-MAX_FACTS:]
    numbered = tuple(Fact(f'F{i}', f.event_id, f.text, f.game_time)
                     for i, f in enumerate(facts, 1))

    status, reason, knowledge = _knowledge_items(memory, npc_id, branch_id, at_game_time,
                                                 vocabulary)
    if status is not RecallStatus.OK:
        return ContextResult(ContextStatus.DENIED, reason)
    return ContextResult(ContextStatus.OK, 'OK', DialogueContext(
        catalog.persona(npc_id), numbered, frozenset(vocabulary), companions, knowledge))
