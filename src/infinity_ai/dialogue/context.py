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

from ..memory.common_knowledge import SHARED_EVENT, BackgroundRegion
from ..memory.model import KnowledgeBasis
from ..personality.identity import (HABITANTE, KnowledgeTier, NpcIdentity, em,
                                    knowledge_tier, layered_text, popular_only)
from ..personality.style import (
    orientation_from_game_alignment, orientation_from_profile, style_from_profile,
)
from ..memory.model import RecallStatus
from ..memory.store import MemoryStore
from ..state.store import CampaignStore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PERSONA_DIR = ROOT / 'knowledge' / 'personas'
DEFAULT_AREA_NAMES = ROOT / 'knowledge' / 'areas' / 'bg2ee-area-names.pt_BR.json'
UNNAMED_AREA = 'um lugar que você não sabe nomear'
CLOSED_DISPOSITIONS = frozenset({'THREATENING', 'HOSTILE', 'FLIGHT'})   # ADR-0125: tells nothing
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
    subject_id: str | None = None


@dataclass(frozen=True)
class DialogueContext:
    persona: Persona
    facts: tuple[Fact, ...]
    vocabulary: frozenset[str]
    companions: tuple[str, ...]
    knowledge: tuple[Fact, ...] = ()
    resident_of: str | None = None   # set for a person met in the game (ADR-0116): where
    orientation: str | None = None   # SPEC-006 alignment orientation, when a profile applies
    occupation: str | None = None    # ADR-0117 identity: what the person does, when known
    manner: str | None = None        # ADR-0117 Wisdom tier: how the person speaks and reasons
    restricted_knowledge: tuple[Fact, ...] = ()  # ADR-0119: role/affiliation-bound facts
    standing: str | None = None      # ADR-0120: HABITANTE, VIAJANTE or FORASTEIRO (residents)
    staff: bool = False              # ADR-0119/0120: a curated STAFF tie to a place (may say it works there)
    home_names: tuple[str, ...] = ()  # CR-2026-004: a resident may say it is from these places
    disposition: str | None = None    # ADR-0125: encounter reaction (FRIENDLY .. HOSTILE, FLIGHT)
    morale: tuple[str, str] | None = None  # ADR-0126: (trigger, HOLD|YIELD) of this line


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
RESIDENT_FALLBACK = 'Hum? Disso eu não sei.'


def _heard_from(entry_id: str, npc_id: str, shared: list, catalog: Catalog | None) -> str:
    """" (você ouviu isso de Bernard, na Coroa de Cobre)": the latest time this companion heard
    the entry from someone whose name was recorded (ADR-0124), or '' (older records)."""
    for event in reversed(shared):
        payload = event.payload
        name = (payload.get('speaker_name') or '').strip()
        if name and entry_id in (payload.get('entries') or ()) \
                and npc_id in (payload.get('listeners') or ()):
            area = payload.get('area')
            place = catalog.area(area) if catalog is not None and area else UNNAMED_AREA
            where = '' if place == UNNAMED_AREA else f', {em(place)}'
            return f' (você ouviu isso de {name}{where})'
    return ''


def _knowledge_items(memory: MemoryStore, npc_id: str, branch_id: str, at_game_time: int | None,
                     vocabulary: set[str], tier: KnowledgeTier | None = None,
                     store: CampaignStore | None = None, catalog: Catalog | None = None
                     ) -> tuple[RecallStatus, str, tuple[Fact, ...]]:
    """What the companion acquired; with a known `tier` (ADR-0117), only the layers it reaches.
    ADR-0124: what it heard by INQUIRY says from whom and where, when the record has it."""
    status, reason, held = memory.recall_common(npc_id=npc_id, branch_id=branch_id,
                                                at_game_time=at_game_time,
                                                purpose='npc_dialogue',
                                                audience='NARRATIVE_CONTEXT')
    if status is not RecallStatus.OK:
        return status, reason, ()
    knowledge = []
    shared = [e for e in store.visible_events(branch_id, SHARED_EVENT)
              if at_game_time is None or e.game_time is None or e.game_time <= at_game_time] \
        if store is not None else []
    for i, k in enumerate(held[:MAX_KNOWLEDGE], 1):
        text = layered_text(k.summary, k.layers, tier) if tier is not None else k.summary
        source = _heard_from(k.entry_id, npc_id, shared, catalog)
        if source:
            vocabulary |= set(_NAME.findall(source))
        knowledge.append(Fact(f'K{i}', f'canon:{k.entry_id}', f'{k.title}{source}: {text}',
                              k.game_time))
        vocabulary |= set(_NAME.findall(k.title)) | set(_NAME.findall(text))
    return status, reason, tuple(knowledge)


def build_resident_context(memory: MemoryStore, store: CampaignStore, catalog: Catalog, *,
                           npc_id: str, display_name: str, residence_areas: tuple[str, ...],
                           area: str | None, dead: bool, branch_id: str,
                           at_game_time: int | None,
                           profile: dict | None = None,
                           identity: NpcIdentity | None = None,
                           also_known: tuple[tuple, ...] = (),
                           wisdom: int | None = None,
                           intelligence: int | None = None,
                           game_alignment: int | None = None,
                           popular_only_ids: frozenset[str] = frozenset(),
                           recall_lines: tuple[tuple[str, str], ...] = (),
                           disposition: str | None = None,
                           morale: tuple[str, str] | None = None) -> ContextResult:
    """A person the player addresses in the game (ADR-0116, SPEC-006): no party memories.

    Anyone alive in the current area may talk; only what the person acquired (ADR-0114/0116,
    e.g. a local placed by the game data) reaches CONHECIMENTO GERAL. A SPEC-006 `profile`, when
    given, sets the speaking style and the alignment orientation; it never adds facts. An ADR-0117
    `identity` becomes the "SOBRE VOCÊ" facts (F-items): all the person may say about itself.
    `also_known` = (entry_id, title, summary, layers[, access_scope[, subject_id]]). Public entries
    join CONHECIMENTO GERAL; RESTRICTED entries join a separate section and require an explicit
    affiliation/allowlist. Wisdom and Intelligence set
    how deeply it understands each subject and how it speaks (`knowledge_tier`), not how many
    subjects it knows."""
    if dead:
        return ContextResult(ContextStatus.DENIED, 'SPEAKER_DEAD')
    if area is None:
        return ContextResult(ContextStatus.DENIED, 'NPC_NOT_PRESENT')
    if residence_areas and area.upper() not in {a.upper() for a in residence_areas}:
        return ContextResult(ContextStatus.DENIED, 'NPC_NOT_PRESENT')
    name = display_name.strip() or npc_id.split(':', 1)[-1].capitalize()
    style = style_from_profile(profile) if profile else RESIDENT_STYLE
    orientation = orientation_from_profile(profile) if profile else \
        orientation_from_game_alignment(game_alignment)
    persona = Persona(npc_id, name, style, frozenset({name}), RESIDENT_FALLBACK)
    place = catalog.area(area)
    vocabulary = {name} | set(name.split()) | {w for w in place.split() if w[:1].isupper()}
    facts: tuple[Fact, ...] = ()
    if identity is not None:
        facts = tuple(Fact(f'F{i}', f'identity:{npc_id}:{i}', text, at_game_time or 0)
                      for i, text in enumerate(identity.self_facts, 1))
        for text in identity.self_facts + identity.regions_named:
            vocabulary |= set(_NAME.findall(text))
    facts = _with_recall(facts, recall_lines, at_game_time, vocabulary)   # ADR-0124
    # ADR-0120: a traveler or outsider was placed here by the game, but does not live here: its
    # game-placed RESIDENCE does not count (what it heard by INQUIRY or brought from home does).
    standing = identity.standing if identity is not None else HABITANTE
    away = frozenset({KnowledgeBasis.RESIDENCE}) if standing != HABITANTE else frozenset()
    status, reason, held = memory.recall_common(npc_id=npc_id, branch_id=branch_id,
                                                at_game_time=at_game_time,
                                                purpose='npc_dialogue',
                                                audience='NARRATIVE_CONTEXT',
                                                exclude_basis=away)
    if status is not RecallStatus.OK:
        return ContextResult(ContextStatus.DENIED, reason)
    tier = knowledge_tier(wisdom, intelligence)
    shallow = popular_only(tier)
    subjects = {k.entry_id: (k.title, k.summary, k.layers, 'COMMON_REGIONAL', None) for k in held}
    for item in also_known:
        entry_id, t, s, layers = item[:4]
        scope = item[4] if len(item) > 4 else 'COMMON_REGIONAL'
        subject_id = item[5] if len(item) > 5 else None
        learned = subjects.get(entry_id)
        if learned is None:
            subjects[entry_id] = (t, s, layers, scope, subject_id)
        else:
            # A learned entry keeps its snapshot, but takes who it is about from the pack; and
            # if learned before layers existed (same checked summary), the layers restate it.
            new_layers = layers if not learned[2] and learned[1] == s else learned[2]
            subjects[entry_id] = (learned[0], learned[1], new_layers, learned[3],
                                  learned[4] or subject_id)
    knowledge, restricted = [], []
    # ADR-0125: what the person is willing to tell in this encounter, decided by code.
    tells_public = disposition not in CLOSED_DISPOSITIONS
    tells_restricted = tells_public and disposition != 'CAUTIOUS'
    if morale is not None and morale[1] == 'YIELD':     # ADR-0126: gave in, tells what it holds
        tells_public = tells_restricted = True
    for i, entry_id in enumerate(sorted(subjects)[:MAX_KNOWLEDGE], 1):
        t, s, layers, scope, subject_id = subjects[entry_id]
        if not (tells_restricted if scope == 'RESTRICTED' else tells_public):
            continue
        learned_here = entry_id in popular_only_ids and not any(
            k.entry_id == entry_id for k in held)
        text = layered_text(s, layers, shallow if learned_here else tier)
        fact = Fact(f'K{i}', f'canon:{entry_id}', f'{t}: {text}', at_game_time or 0, subject_id)
        (restricted if scope == 'RESTRICTED' else knowledge).append(fact)
        vocabulary |= set(_NAME.findall(t)) | set(_NAME.findall(text))
    return ContextResult(ContextStatus.OK, 'OK', DialogueContext(
        persona, facts, frozenset(vocabulary), (), tuple(knowledge),
        identity.place if identity and identity.place else place, orientation,
        identity.occupation if identity else None, tier.style, tuple(restricted), standing,
        any(a.endswith(':STAFF') for a in identity.affiliations) if identity else False,
        identity.home_names if identity else (), disposition, morale))


def _with_recall(facts: tuple[Fact, ...], lines: tuple[tuple[str, str], ...],
                 at_game_time: int | None, vocabulary: set[str]) -> tuple[Fact, ...]:
    """ADR-0124: earlier conversations with the player as more "SOBRE VOCÊ" facts."""
    out = list(facts)
    for event_id, text in lines:
        out.append(Fact(f'F{len(out) + 1}', event_id, text, at_game_time or 0))
        vocabulary |= set(_NAME.findall(text))
    return tuple(out)


def build_context(memory: MemoryStore, store: CampaignStore, catalog: Catalog, *, npc_id: str,
                  branch_id: str, at_game_time: int | None, wisdom: int | None = None,
                  intelligence: int | None = None,
                  recall_lines: tuple[tuple[str, str], ...] = ()) -> ContextResult:
    """A companion in the party. When the game sends its Wisdom/Intelligence (in-game box), the
    ADR-0117 matrix sets how deeply it understands what it learned and how it speaks; without
    them (overlay) the whole checked summary is used, as before."""
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
    numbered = _with_recall(numbered, recall_lines, at_game_time, vocabulary)

    tier = knowledge_tier(wisdom, intelligence) if wisdom or intelligence else None
    status, reason, knowledge = _knowledge_items(memory, npc_id, branch_id, at_game_time,
                                                 vocabulary, tier, store, catalog)
    if status is not RecallStatus.OK:
        return ContextResult(ContextStatus.DENIED, reason)
    return ContextResult(ContextStatus.OK, 'OK', DialogueContext(
        catalog.persona(npc_id), numbered, frozenset(vocabulary), companions, knowledge,
        manner=tier.style if tier is not None else None))
