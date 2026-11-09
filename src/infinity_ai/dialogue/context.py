# SPDX-License-Identifier: Apache-2.0
"""SPEC-004 deterministic dialogue context: what an NPC may say comes only from its recall.

REQ-VOICE-005: the context is built from `MemoryStore.recall` (NPC, branch, time, audience
already enforced) and rendered as numbered facts. Area codes never reach the text; unknown areas
are presented as unnamed places. Only companions currently in the party can be talked to.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..memory.model import RecallStatus
from ..memory.store import MemoryStore
from ..state.store import CampaignStore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PERSONA_DIR = ROOT / 'knowledge' / 'personas'
DEFAULT_AREA_NAMES = ROOT / 'knowledge' / 'areas' / 'bg2ee-area-names.pt_BR.json'
UNNAMED_AREA = 'um lugar que você não sabe nomear'
MAX_FACTS = 20
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


@dataclass(frozen=True)
class ContextResult:
    status: ContextStatus
    reason: str
    context: DialogueContext | None = None


@dataclass
class Catalog:
    personas: dict[str, Persona] = field(default_factory=dict)
    area_names: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, persona_dir: Path = DEFAULT_PERSONA_DIR,
             area_names: Path = DEFAULT_AREA_NAMES) -> Catalog:
        personas = {}
        for path in sorted(Path(persona_dir).glob('*.json')):
            doc = json.loads(path.read_text(encoding='utf-8'))
            personas[doc['npc_id']] = Persona(doc['npc_id'], doc['display_name'],
                                              tuple(doc.get('style', ())),
                                              frozenset(doc.get('vocabulary', ())),
                                              doc.get('fallback') or GENERIC_FALLBACK)
        areas = json.loads(Path(area_names).read_text(encoding='utf-8')).get('areas', {})
        return cls(personas, dict(areas))

    def persona(self, npc_id: str) -> Persona:
        if npc_id in self.personas:
            return self.personas[npc_id]
        name = npc_id.split(':', 1)[-1].capitalize()
        return Persona(npc_id, name, (), frozenset({name}))

    def display(self, npc_id: str) -> str:
        return self.persona(npc_id).display_name

    def area(self, resref: str | None) -> str:
        return self.area_names.get(resref or '', UNNAMED_AREA)


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
    return ContextResult(ContextStatus.OK, 'OK', DialogueContext(
        catalog.persona(npc_id), numbered, frozenset(vocabulary), companions))
