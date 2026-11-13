# SPDX-License-Identifier: Apache-2.0
"""Fixed set of dialogue cases, checked against the local model before each PR.

Each case builds the speaker's context with the real code (identity, standing, regional and
relational knowledge, Wisdom/Intelligence tier, conversation turns), asks one question through
the `DialogueEngine` and checks the answer: allowed status, entries used, words required or
forbidden, `unknown`, length, no copy of the knowledge layer, accepted on the first attempt.
The model varies, so a case runs several times and passes when enough runs pass (2 of 3 by
default). CI only checks the cases and the checker with a fake model; real runs use Ollama.
"""
from __future__ import annotations

import difflib
import json
import re
import math
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from ..bridge.domain import (
    Audience, Coverage, Evidence, ObservationEnvelope, Reason, SessionIdentity, Status,
    Visibility,
)
from ..canon.pack import CanonPack
from ..canon.pin import pin_pack
from ..memory.common_knowledge import (
    home_region, identity_knowledge, mentioned_in, relationship_entries,
)
from ..memory.model import KnowledgeBasis
from ..memory.store import MemoryStore
from ..personality.reaction import DISPOSITIONS
from ..personality.identity import (
    STANDINGS, build_identity, knowledge_tier, layered_text, popular_only,
)
from ..state.recorder import ObservationRecorder
from ..state.store import ROOT_BRANCH, CampaignStore
from .context import Catalog
from .engine import DialogueEngine, DialogueRequest, DialogueResponse, ResidentRequest
from .llm import LlmProvider

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CASES = ROOT / 'tests' / 'dialogue_eval' / 'cases.pt_BR.json'
CASES_SCHEMA = 'infinity-ai.dialogue-eval-cases.v1'
CHECK_KEYS = frozenset({'status', 'uses', 'mentions_any', 'mentions_none', 'matches_none',
                        'unknown', 'max_chars', 'not_copy_of', 'first_try'})
KINDS = ('resident', 'companion')
COPY_LIMIT = 0.85
GAME_TIME = 1000
CAMPAIGN_YEAR = 1369


class CaseError(ValueError):
    """A case file that does not describe a valid case."""


@dataclass(frozen=True)
class Case:
    id: str
    description: str
    speaker: dict
    question: str
    checks: dict
    history: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class RunResult:
    passed: bool
    status: str
    speech: str
    flags: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class CaseResult:
    case: Case
    runs: tuple[RunResult, ...]
    required: int

    @property
    def passes(self) -> int:
        return sum(r.passed for r in self.runs)

    @property
    def passed(self) -> bool:
        return self.passes >= self.required

    @property
    def fallbacks(self) -> int:
        return sum(r.status == 'FALLBACK' for r in self.runs)


def required_passes(runs: int) -> int:
    """At least two thirds of the runs (2 of 3)."""
    return max(1, math.ceil(runs * 2 / 3))


def load_cases(pack: CanonPack, path: Path = DEFAULT_CASES) -> tuple[Case, ...]:
    doc = json.loads(Path(path).read_text(encoding='utf-8'))
    if doc.get('schema') != CASES_SCHEMA:
        raise CaseError(f'schema must be {CASES_SCHEMA}')
    cases, seen = [], set()
    for raw in doc.get('cases') or []:
        case = Case(raw.get('id', ''), raw.get('description', ''), raw.get('speaker') or {},
                    raw.get('question', ''), raw.get('checks') or {},
                    tuple(tuple(t) for t in raw.get('history') or ()))
        _check_case(case, pack)
        if case.id in seen:
            raise CaseError(f'duplicate case id {case.id}')
        seen.add(case.id)
        cases.append(case)
    if not cases:
        raise CaseError('no cases')
    return tuple(cases)


def _check_case(case: Case, pack: CanonPack) -> None:
    where = f'case {case.id or "?"}'
    if not case.id or not case.question:
        raise CaseError(f'{where}: id and question are required')
    s = case.speaker
    if s.get('kind') not in KINDS or not str(s.get('npc_id', '')).startswith('npc:'):
        raise CaseError(f'{where}: speaker kind/npc_id')
    if s.get('disposition') is not None and s['disposition'] not in DISPOSITIONS:
        raise CaseError(f'{where}: unknown disposition {s["disposition"]}')
    if s.get('standing') is not None and s['standing'] not in STANDINGS:
        raise CaseError(f'{where}: unknown standing {s["standing"]}')
    for region in (s.get('home'), s.get('origin')):
        if region is not None and pack.get(region) is None:
            raise CaseError(f'{where}: region {region} not in the pack')
    for entry in list(s.get('knows') or ()) + list(case.checks.get('uses') or ()):
        if pack.get(entry) is None:
            raise CaseError(f'{where}: entry {entry} not in the pack')
    unknown_checks = set(case.checks) - CHECK_KEYS
    if unknown_checks:
        raise CaseError(f'{where}: unknown checks {sorted(unknown_checks)}')
    copy_of = case.checks.get('not_copy_of')
    if copy_of is not None and pack.get(copy_of) is None:
        raise CaseError(f'{where}: entry {copy_of} not in the pack')
    if any(len(t) != 2 for t in case.history):
        raise CaseError(f'{where}: each history turn is [question, answer]')


def check_answer(case: Case, pack: CanonPack, response: DialogueResponse) -> tuple[str, ...]:
    """What the answer got wrong for this case (empty = passed)."""
    c, speech = case.checks, response.speech or ''
    low = speech.lower()
    failures = []
    if c.get('status') and response.status.value not in c['status']:
        failures.append(f'status {response.status.value}')
    for entry_id in c.get('uses') or ():
        declared = f'canon:{entry_id}' in response.used_event_ids
        if not declared and not mentioned_in(pack.get(entry_id), speech):
            failures.append(f'não usou {entry_id}')
    words = c.get('mentions_any') or ()
    if words and not any(w.lower() in low for w in words):
        failures.append(f'não citou nenhuma de {list(words)}')
    for w in c.get('mentions_none') or ():
        if w.lower() in low:
            failures.append(f'citou "{w}"')
    for pattern in c.get('matches_none') or ():       # regex, e.g. a claim but not its denial
        if re.search(pattern, speech, re.I):
            failures.append(f'casou /{pattern}/')
    if 'unknown' in c and response.unknown is not c['unknown']:
        failures.append(f'unknown={response.unknown}')
    if c.get('max_chars') and len(speech) > c['max_chars']:
        failures.append(f'{len(speech)} caracteres')
    if c.get('not_copy_of'):
        entry = pack.get(c['not_copy_of'])
        popular = (entry.layers or {}).get('POPULAR') or entry.summary
        ratio = difflib.SequenceMatcher(None, popular.lower(), low).ratio()
        if ratio >= COPY_LIMIT:
            failures.append(f'copiou a camada ({ratio:.2f})')
    if c.get('first_try') and any(f.startswith('attempt') for f in response.flags):
        failures.append('precisou de nova tentativa')
    return tuple(failures)


def _build_areas(pack: CanonPack) -> frozenset[str]:
    return frozenset(a for e in pack.entries.values() for a in e.area_resrefs)


def ask(case: Case, pack: CanonPack, provider: LlmProvider,
        catalog: Catalog | None = None) -> DialogueResponse:
    """One answer to the case, from a fresh temporary campaign."""
    catalog = catalog or Catalog.load()
    with tempfile.TemporaryDirectory() as tmp:
        store = CampaignStore.open(Path(tmp) / 'eval.sqlite3', 'eval')
        try:
            if case.speaker['kind'] == 'companion':
                return _ask_companion(case, pack, provider, catalog, store)
            return _ask_resident(case, pack, provider, catalog, store)
        finally:
            store.close()


def _ask_resident(case, pack, provider, catalog, store) -> DialogueResponse:
    s = case.speaker
    npc_id, name, area = s['npc_id'], s.get('name', s['npc_id']), s.get('area', 'AR0406')
    home = s.get('home', 'region:athkatla')
    curation = SimpleNamespace(
        occupation=s.get('occupation'), origin_region=s.get('origin'), years_here=None,
        places_visited=(), self_facts=tuple(s.get('self_facts') or ()),
        affiliations=tuple(s.get('affiliations') or ()), standing=s.get('standing'))
    resident = SimpleNamespace(gender=s.get('gender', 1), race=s.get('race', 1), klass=0,
                               display_name=name)
    identity = build_identity(npc_id=npc_id, name=name, pack=pack, place=catalog.area(area),
                              home_region=home, resident=resident, curation=curation)
    build = _build_areas(pack)
    full, shallow = identity_knowledge(pack, homeland=identity.origin_region,
                                       home=identity.home_region, campaign_year=CAMPAIGN_YEAR,
                                       build_areas=build, standing=identity.standing)
    related = relationship_entries(pack, npc_id=npc_id, affiliations=curation.affiliations,
                                   campaign_year=CAMPAIGN_YEAR, build_areas=build)
    learned = set(s.get('knows') or ())               # heard by INQUIRY: always in full
    shallow_ids = frozenset(e for e in shallow if e not in learned)
    known = sorted(set(full) | set(related) | learned | shallow_ids)
    also_known = tuple((e, pack.get(e).title, pack.get(e).summary, pack.get(e).layers,
                        pack.get(e).access_scope, pack.get(e).subject_id) for e in known)
    return DialogueEngine(store, provider, catalog).respond_resident(
        ResidentRequest(npc_id, name, case.question, area, False), residence_areas=(area,),
        branch_id=ROOT_BRANCH, at_game_time=GAME_TIME, identity=identity,
        also_known=also_known, wisdom=s.get('wis'), intelligence=s.get('int'),
        popular_only_ids=shallow_ids, history=case.history,
        disposition=s.get('disposition'))


def _envelope(field_name: str, value: str) -> ObservationEnvelope:
    return ObservationEnvelope(
        observation_id=f'eval-{field_name}', timestamp='2026-01-01T00:00:00Z',
        session=SessionIdentity('eval', 'main', 0, 'sha256:eval', 'sha256:eval', 'eval'),
        field=field_name, purpose='narrative_context', audience=Audience.PLAYER,
        status=Status.OBSERVED, reason=Reason.NONE, value=value, coverage=Coverage.FULL,
        visibility=Visibility.PARTY, evidence=Evidence.SYNTHETIC)


def _ask_companion(case, pack, provider, catalog, store) -> DialogueResponse:
    s = case.speaker
    npc_id = s['npc_id']
    members = json.dumps(sorted({npc_id.split(':', 1)[1]} | set(s.get('party') or ())))
    ObservationRecorder(store, allow_synthetic=True).observe(
        _envelope('host.current_area_id', s.get('area', 'AR0406')),
        _envelope('host.game_time', str(GAME_TIME)), _envelope('party.companion_ids', members))
    pin, _ = pin_pack(store, ROOT_BRANCH, pack, game_time=GAME_TIME)
    memory = MemoryStore(store)
    for entry_id in s.get('knows') or ():
        entry = pack.get(entry_id)
        memory.record_canon_knowledge(
            npc_id=npc_id, branch_id=ROOT_BRANCH, game_time=GAME_TIME,
            basis=KnowledgeBasis.INQUIRY, region_id=home_region(entry) or 'region:amn',
            entry_id=entry_id, pack_year_dr=pack.year_dr, pack_revision=pack.revision,
            pin_event_id=pin.event_id, trigger_event_id=pin.event_id, title=entry.title,
            summary=entry.summary, layers=entry.layers)
    return DialogueEngine(store, provider, catalog).respond(
        DialogueRequest(npc_id, case.question), branch_id=ROOT_BRANCH, at_game_time=GAME_TIME,
        wisdom=s.get('wis'), intelligence=s.get('int'), history=case.history)


def run_case(case: Case, pack: CanonPack, provider: LlmProvider, runs: int = 3,
             catalog: Catalog | None = None) -> CaseResult:
    results = []
    for _ in range(runs):
        response = ask(case, pack, provider, catalog)
        failures = check_answer(case, pack, response)
        results.append(RunResult(not failures, response.status.value, response.speech,
                                 tuple(response.flags), failures))
    return CaseResult(case, tuple(results), required_passes(runs))


def known_text(pack: CanonPack, entry_id: str, wisdom: int | None, intelligence: int | None,
               shallow: bool = False) -> str:
    """What a speaker of this tier knows of the entry (helper for writing cases)."""
    entry = pack.get(entry_id)
    tier = knowledge_tier(wisdom, intelligence)
    return layered_text(entry.summary, entry.layers, popular_only(tier) if shallow else tier)


__all__ = ['Case', 'CaseError', 'CaseResult', 'RunResult', 'ask', 'check_answer', 'known_text',
           'load_cases', 'required_passes', 'run_case']
