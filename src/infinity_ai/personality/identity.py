# SPDX-License-Identifier: Apache-2.0
"""ADR-0117 / SPEC-006 layer P0: who an NPC is (name, home, role, origin, places it has been).

Sources, by precedence: maintainer curation (`knowledge/npcs/`) > the game's own data (local
inventory: name, area, race, gender, class, role words in the game name) > a deterministic
generation for generic people (closed vocabularies + regions of the pinned canon pack only).
Nothing here names other people, family or events, and nothing is written to the game.

The result is rendered as short "SOBRE VOCÊ" facts for the dialogue context; the NPC may only
say about itself what those facts say.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from ..canon.pack import CanonPack

IDENTITY_SCHEMA = 'infinity-ai.npc-identity.v1'
CURATION_SCHEMA = 'infinity-ai.npc-identity-curation.v1'
POLICY = 'spec-006-identity-v1'
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CURATION_DIR = ROOT / 'knowledge' / 'npcs'
MAX_FACT = 200
AFFILIATION_PATTERN = re.compile(r'^place:[a-z0-9-]{1,64}:[A-Z][A-Z0-9_]{0,31}$')

GAME_DATA, CURATED, GENERATED = 'GAME_DATA', 'CURATED', 'GENERATED'

# ADR-0120: local standing. A resident knows the place; a traveler (same realm, passing through)
# knows only its popular core; an outsider (distant land) knows nothing of it, only its homeland.
HABITANTE, VIAJANTE, FORASTEIRO = 'HABITANTE', 'VIAJANTE', 'FORASTEIRO'
STANDINGS = (HABITANTE, VIAJANTE, FORASTEIRO)
# Chance that a generic person of this role is not a resident (design tuning, ADR-0120).
AWAY_CHANCE = {'TRAVELER': 1.0, 'SAILOR': 0.6, 'PATRON': 0.3, 'MERCHANT': 0.3, 'FIGHTER': 0.2,
               'COMMONER': 0.05, 'PEASANT': 0.05}
OUTSIDER_SHARE = 1 / 3        # of those away, how many come from a distant land

# Role words found in the game's own display names (pt_BR), written by us: prefix -> role.
ROLE_PATTERNS: tuple[tuple[str, str], ...] = (
    ('guarda', 'GUARD'), ('leao de chacara', 'GUARD'), ('soldado', 'GUARD'),
    ('cliente', 'PATRON'), ('bebado', 'PATRON'), ('frequentador', 'PATRON'),
    ('meretriz', 'WORKER'), ('garcon', 'WORKER'), ('criado', 'WORKER'), ('anunciador', 'WORKER'),
    ('taverneir', 'INNKEEPER'), ('estalajadeir', 'INNKEEPER'),
    ('nobre', 'NOBLE'), ('lorde', 'NOBLE'), ('dama', 'NOBLE'),
    ('campones', 'PEASANT'), ('campesin', 'COMMONER'), ('plebeu', 'COMMONER'),
    ('mendig', 'BEGGAR'), ('mercador', 'MERCHANT'), ('comerciante', 'MERCHANT'),
    ('vendedor', 'MERCHANT'), ('garot', 'CHILD'), ('menin', 'CHILD'),
    ('viajante', 'TRAVELER'), ('marinheiro', 'SAILOR'), ('gladiador', 'FIGHTER'),
)
# (masculine, feminine) descriptions of a role, used when no curated occupation exists.
ROLE_TEXT = {
    'GUARD': ('guarda', 'guarda'), 'PATRON': ('frequentador da casa', 'frequentadora da casa'),
    'WORKER': ('quem trabalha na casa', 'quem trabalha na casa'),
    'INNKEEPER': ('dono da casa', 'dona da casa'), 'NOBLE': ('nobre', 'nobre'),
    'PEASANT': ('camponês', 'camponesa'), 'COMMONER': ('gente do povo', 'gente do povo'),
    'BEGGAR': ('quem vive de esmolas', 'quem vive de esmolas'),
    'MERCHANT': ('comerciante', 'comerciante'), 'CHILD': ('criança da cidade', 'criança da cidade'),
    'TRAVELER': ('viajante', 'viajante'), 'SAILOR': ('marinheiro', 'marinheira'),
    'FIGHTER': ('lutador', 'lutadora'),
}
# Occupations a generic person may draw, by role (closed vocabulary, masculine/feminine).
OCCUPATIONS = {
    'COMMONER': (('carregador', 'carregadora'), ('lavrador', 'lavradora'),
                 ('artesão', 'artesã'), ('pescador', 'pescadora'), ('ajudante de ferreiro',
                                                                    'ajudante de ferreiro')),
    'PEASANT': (('lavrador', 'lavradora'), ('pastor', 'pastora'), ('colhedor', 'colhedora')),
    'PATRON': (('carregador do porto', 'carregadora do porto'), ('artesão', 'artesã'),
               ('mercador de passagem', 'mercadora de passagem'), ('mercenário', 'mercenária'),
               ('escriturário', 'escriturária')),
    'BEGGAR': (('ex-soldado', 'ex-soldado'), ('ex-marinheiro', 'ex-marinheira'),
               ('ex-carregador', 'ex-carregadora')),
    'MERCHANT': (('vendedor de tecidos', 'vendedora de tecidos'),
                 ('vendedor de especiarias', 'vendedora de especiarias')),
}
RACE_TEXT = {1: ('humano', 'humana'), 2: ('elfo', 'elfa'), 3: ('meio-elfo', 'meio-elfa'),
             4: ('anão', 'anã'), 5: ('halfling', 'halfling'), 6: ('gnomo', 'gnoma'),
             7: ('meio-orc', 'meio-orc')}
CLASS_TEXT = {1: ('mago', 'maga'), 2: ('guerreiro', 'guerreira'), 3: ('clérigo', 'clériga'),
              4: ('ladrão', 'ladra'), 5: ('bardo', 'barda'), 6: ('paladino', 'paladina'),
              11: ('druida', 'druida'), 12: ('patrulheiro', 'patrulheira'), 20: ('monge', 'monja')}


def _plain(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower())
                   if not unicodedata.combining(c))


DEFAULT_WISDOM = 10
DEFAULT_INTELLIGENCE = 10


@dataclass(frozen=True)
class KnowledgeTier:
    """ADR-0117 matrix: how well a person understands what it knows, and how it talks about it."""
    level: int          # 1 rudimentar .. 5 sábio (Wisdom)
    name: str
    informed: bool      # INFORMED layer (attention, experience, trade)
    studied: str        # STUDIED layer: 'NONE', 'PARTIAL' (first sentence) or 'FULL' (Intelligence)
    style: str          # how it speaks and reasons, for the prompt


TIER_STYLES = {
    1: ('rudimentar', 'fala de forma muito simples e curta, com frases soltas; repete o que ouviu '
                      'sem explicar; diante de assunto complicado diz que não entende disso'),
    2: ('comum', 'fala de forma curta e concreta, liga o assunto à própria vida e admite sem '
                 'rodeios quando não sabe'),
    3: ('atento', 'fala com clareza, dá um detalhe prático ou um conselho, relaciona o que sabe e '
                  'diz até onde vai o seu conhecimento'),
    4: ('perspicaz', 'fala de forma elaborada e ponderada, explica causas e consequências do que '
                     'sabe e separa o que sabe do que apenas supõe'),
    5: ('sábio', 'fala com profundidade e nuance, vê o quadro geral, liga lugares e grupos e pode '
                 'devolver uma pergunta; nunca especula além do que sabe'),
}


def _score(value: int | None, default: int) -> int:
    return value if isinstance(value, int) and 1 <= value <= 25 else default


def knowledge_tier(wisdom: int | None, intelligence: int | None = None) -> KnowledgeTier:
    """Wisdom sets the tier (understanding and speech); Intelligence unlocks studied knowledge."""
    w = _score(wisdom, DEFAULT_WISDOM)
    i = _score(intelligence, DEFAULT_INTELLIGENCE)
    level = 1 if w <= 6 else 2 if w <= 10 else 3 if w <= 14 else 4 if w <= 17 else 5
    if (level >= 5 and i >= 12) or i >= 17:
        studied = 'FULL'
    elif (level >= 4 and i >= 10) or i >= 14:
        studied = 'PARTIAL'
    else:
        studied = 'NONE'
    name, style = TIER_STYLES[level]
    # Intelligence unlocks STUDIED, never the experience-based INFORMED layer.
    return KnowledgeTier(level, name, level >= 3, studied, style)


def popular_only(tier: KnowledgeTier) -> KnowledgeTier:
    """ADR-0120: what a traveler knows of the place it passes through, the popular core only,
    whatever its Wisdom (a rudimentary person still keeps just the first sentence)."""
    return KnowledgeTier(min(tier.level, 2), tier.name, False, 'NONE', tier.style)


def layered_text(summary: str, layers: Mapping[str, str] | None, tier: KnowledgeTier) -> str:
    """What this person knows of an entry: popular core, then informed, then studied layers.

    Without curated layers, the summary's first sentence is the popular core and the rest is
    informed knowledge."""
    layers = dict(layers or {})
    if not layers:
        sentences = re.split(r'(?<=[.!?])\s+', summary.strip())
        layers = {'POPULAR': sentences[0], 'INFORMED': ' '.join(sentences[1:])}
    popular = layers.get('POPULAR', '')
    parts = [first_sentences(popular, 1) if tier.level == 1 else popular]
    if tier.informed and layers.get('INFORMED'):
        parts.append(layers['INFORMED'])
    if tier.studied != 'NONE' and layers.get('STUDIED'):
        parts.append(layers['STUDIED'] if tier.studied == 'FULL'
                     else first_sentences(layers['STUDIED'], 1))
    return ' '.join(p for p in parts if p)


def first_sentences(text: str, count: int | None) -> str:
    if count is None:
        return text
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return ' '.join(parts[:count])


def role_from_name(display_name: str | None) -> str | None:
    """Role suggested by the game's own name ("Guarda da Coroa de Cobre" -> GUARD)."""
    name = _plain(display_name or '')
    return next((role for prefix, role in ROLE_PATTERNS if name.startswith(prefix)), None)


def em(place: str) -> str:
    """Portuguese "em" + place, contracting the article: "a Coroa de Cobre" -> "na Coroa de Cobre"."""
    for article, contracted in (('as ', 'nas '), ('os ', 'nos '), ('a ', 'na '), ('o ', 'no ')):
        if place.startswith(article):
            return contracted + place[len(article):]
    return 'em ' + place


def por(place: str) -> str:
    """Portuguese "por" + place: "a Coroa de Cobre" -> "pela Coroa de Cobre"."""
    for article, contracted in (('as ', 'pelas '), ('os ', 'pelos '), ('a ', 'pela '),
                                ('o ', 'pelo ')):
        if place.startswith(article):
            return contracted + place[len(article):]
    return 'por ' + place


def _gendered(pair: tuple[str, str], gender: int) -> str:
    return pair[1] if gender == 2 else pair[0]


@dataclass(frozen=True)
class Curation:
    npc_id: str
    occupation: str | None
    origin_region: str | None
    years_here: int | None
    places_visited: tuple[str, ...]
    self_facts: tuple[str, ...]
    affiliations: tuple[str, ...] = ()
    standing: str | None = None          # ADR-0120; None = not curated (game data decides)
    morale: int | None = None            # ADR-0126: curated base morale (2..20), else Table 49


def load_curations(pack: CanonPack, base: Path = DEFAULT_CURATION_DIR) -> dict[str, Curation]:
    """Checked curations only; regions must exist in the pack and facts stay short."""
    out: dict[str, Curation] = {}
    for path in sorted(Path(base).glob('*.json')):
        doc = json.loads(path.read_text(encoding='utf-8'))
        check = doc.get('curation') or {}
        if doc.get('schema') != CURATION_SCHEMA or not check.get('checked_by') \
                or not check.get('checked_at'):
            continue
        regions = [doc.get('origin_region')] + list(doc.get('places_visited') or [])
        if any(r is not None and not _is_region(pack, r) for r in regions):
            continue
        facts = tuple(f for f in doc.get('self_facts') or () if isinstance(f, str)
                      and 0 < len(f) <= MAX_FACT)
        raw_affiliations = doc.get('affiliations') or []
        if not isinstance(raw_affiliations, list) or any(
                not isinstance(a, str) or not AFFILIATION_PATTERN.fullmatch(a)
                for a in raw_affiliations):
            continue
        standing = doc.get('standing')
        if standing is not None and standing not in STANDINGS:
            continue
        morale = doc.get('morale')
        if morale is not None and (isinstance(morale, bool) or not isinstance(morale, int)
                                   or not 2 <= morale <= 20):
            continue
        years = doc.get('years_here')
        out[doc['npc_id']] = Curation(
            doc['npc_id'], doc.get('occupation'), doc.get('origin_region'),
            years if isinstance(years, int) and years > 0 else None,
            tuple(doc.get('places_visited') or ()), facts,
            tuple(sorted(set(raw_affiliations))), standing, morale)
    return out


def _is_region(pack: CanonPack, region_id: str) -> bool:
    entry = pack.get(region_id)
    return entry is not None and entry.kind == 'REGION'


def _chain(pack: CanonPack, region_id: str | None) -> list[str]:
    chain: list[str] = []
    while region_id and region_id not in chain and _is_region(pack, region_id):
        chain.append(region_id)
        region_id = pack.get(region_id).region_id
    return chain


def generate_identity(*, npc_id: str, role: str | None, gender: int, home_region: str | None,
                      pack: CanonPack, world_seed: str, campaign_id: str,
                      branch_id: str) -> dict:
    """Deterministic background for a generic person; regions come only from the pack."""
    seed = json.dumps([POLICY, world_seed, campaign_id, branch_id, npc_id], ensure_ascii=False)
    rng = random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest(), 'big'))
    regions = sorted(e.id for e in pack.entries.values() if e.kind == 'REGION')
    home_chain = _chain(pack, home_region)
    elsewhere = [r for r in regions if r not in home_chain]
    occupation = None
    vocabulary = OCCUPATIONS.get(role or 'COMMONER')     # no role in the name: an ordinary trade
    if vocabulary:
        occupation = _gendered(rng.choice(vocabulary), gender)
    if home_chain and (not elsewhere or rng.random() < 0.6):
        origin = rng.choice(home_chain)
    else:
        origin = rng.choice(elsewhere) if elsewhere else None
    born_here = origin is not None and origin == home_region
    years = None if born_here else rng.randint(1, 40)
    count = rng.randint(0, min(2, len(elsewhere)))
    visited = sorted(rng.sample([r for r in elsewhere if r != origin], k=min(
        count, len([r for r in elsewhere if r != origin]))))
    # ADR-0120: standing on its own seed, so residents keep every draw above unchanged.
    standing = HABITANTE
    away = random.Random(int.from_bytes(hashlib.sha256((seed + 'standing').encode()).digest(),
                                        'big'))
    if home_chain and away.random() < AWAY_CHANCE.get(role or 'COMMONER', 0.0):
        realm = home_chain[1:]                  # ancestors: same realm, not this very place
        if elsewhere and (not realm or away.random() < OUTSIDER_SHARE):
            standing, origin = FORASTEIRO, away.choice(elsewhere)
        elif realm:
            standing, origin = VIAJANTE, away.choice(realm)
        if standing != HABITANTE:
            born_here, years = False, None
            visited = [r for r in visited if r != origin]
    return {'occupation': occupation, 'origin_region': origin, 'years_here': years,
            'born_here': born_here, 'places_visited': visited, 'standing': standing,
            'policy': POLICY}


@dataclass(frozen=True)
class NpcIdentity:
    npc_id: str
    name: str
    place: str | None
    region_title: str | None
    occupation: str | None
    self_facts: tuple[str, ...]
    regions_named: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)
    origin_region: str | None = None     # homeland (ADR-0117): its common knowledge is known
    home_region: str | None = None       # where it is (ADR-0117): known as its standing allows
    standing: str = HABITANTE            # ADR-0120: resident, traveler or outsider
    affiliations: tuple[str, ...] = ()   # ADR-0119 curated ties to places (e.g. ...:STAFF)
    home_names: tuple[str, ...] = ()     # CR-2026-004: where it lives and the regions above it

    @property
    def source(self) -> str:
        values = set(self.provenance.values())
        return CURATED if CURATED in values else GENERATED if GENERATED in values else GAME_DATA

    def to_json(self) -> dict:
        return {'schema': IDENTITY_SCHEMA, 'npc_id': self.npc_id, 'name': self.name,
                'place': self.place, 'region': self.region_title,
                'occupation': self.occupation, 'self_facts': list(self.self_facts),
                'standing': self.standing, 'provenance': dict(self.provenance)}


def build_identity(*, npc_id: str, name: str, pack: CanonPack, place: str | None,
                   home_region: str | None, resident: object | None = None,
                   curation: Curation | None = None, generated: dict | None = None
                   ) -> NpcIdentity:
    """Combine curation > game data > generated into an identity and its "SOBRE VOCÊ" facts."""
    gender = getattr(resident, 'gender', 0) if resident is not None else 0
    title = (lambda r: pack.get(r).title if r and _is_region(pack, r) else None)
    region_title = title(home_region)
    prov: dict[str, str] = {'name': GAME_DATA}
    # ADR-0120: curation > generated > resident (the game placed it here).
    if curation and getattr(curation, 'standing', None) in STANDINGS:
        standing, prov['standing'] = curation.standing, CURATED
    elif not curation and generated and generated.get('standing') in STANDINGS:
        standing, prov['standing'] = generated['standing'], GENERATED
    else:
        standing = HABITANTE
    facts = [f'Você se chama {name}.']
    if place:
        # Where it lives (the city) is not where it is (a tavern): being placed somewhere does not
        # make it live or work there; a tie to the place needs a curated affiliation (ADR-0119).
        if standing == HABITANTE:
            facts.append(f'Você vive {em(region_title)} e está {em(place)}.' if region_title
                         else f'Você está {em(place)}.')
        else:
            facts.append(f'Você está de passagem {por(region_title)} e está agora {em(place)}.'
                         if region_title else f'Você está de passagem {por(place)}.')
        prov['home'] = GAME_DATA
    occupation = None
    if curation and curation.occupation:
        occupation, prov['occupation'] = curation.occupation, CURATED
    elif generated and generated.get('occupation'):
        occupation, prov['occupation'] = generated['occupation'], GENERATED
    else:
        role = role_from_name(name) or role_from_name(getattr(resident, 'display_name', None))
        if role in ROLE_TEXT:
            occupation, prov['occupation'] = _gendered(ROLE_TEXT[role], gender), GAME_DATA
    if occupation:
        facts.append(f'Você é {occupation}.')
    race = RACE_TEXT.get(getattr(resident, 'race', 0))
    if race:
        facts.append(f'Você é {_gendered(race, gender)}.')
        prov['race'] = GAME_DATA
    klass = CLASS_TEXT.get(getattr(resident, 'klass', 0))
    if klass:
        facts.append(f'Você tem treino de {_gendered(klass, gender)}.')
        prov['class'] = GAME_DATA
    # A checked official-NPC curation is authoritative even when origin is unknown.
    # Missing curated fields stay unknown; they must not be filled by generic generation.
    source = curation
    origin = source.origin_region if source else (generated or {}).get('origin_region')
    born_here = bool((generated or {}).get('born_here')) if not source else \
        (origin is not None and origin == home_region)
    years = source.years_here if source else (generated or {}).get('years_here')
    visited = list(source.places_visited if source else (generated or {}).get('places_visited')
                   or ())
    background = CURATED if source else GENERATED
    named = [r for r in [origin] + visited if r]
    if origin and title(origin):
        if standing == FORASTEIRO:
            facts.append(f'Você é de {title(origin)}, terra distante, e não conhece bem os '
                         'costumes daqui.')
        elif standing == VIAJANTE:
            facts.append(f'Você veio de {title(origin)}.')
        elif born_here:
            facts.append('Você nasceu e cresceu aqui.')
        else:
            facts.append(f'Você veio de {title(origin)}'
                         + (f' e vive aqui há {years} anos.' if years else '.'))
        prov['origin'] = background
    if visited and all(title(r) for r in visited):
        facts.append('Você já passou por ' + ' e '.join(title(r) for r in visited) + '.')
        prov['places_visited'] = background
    if curation:
        facts.extend(curation.self_facts)
        if curation.self_facts:
            prov['self_facts'] = CURATED
    return NpcIdentity(npc_id, name, place, region_title, occupation, tuple(facts),
                       tuple(title(r) for r in named if title(r)), prov,
                       origin if origin and title(origin) else None,
                       home_region if region_title else None, standing,
                       tuple(getattr(curation, 'affiliations', ()) or ()) if curation else (),
                       tuple(title(r) for r in _chain(pack, home_region) if title(r))
                       if standing == HABITANTE else ())


IdentityFactory = Callable[[str], dict]
