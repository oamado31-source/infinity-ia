# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 canon pack: one DR-year partition of curated entries plus their source records.

Loads only the requested year's directory (doc 60a: no global search across years), validates
every entry and fails closed on any problem. Summaries are our own short text; quoted passages
longer than 15 words are refused, and S0 sources need a page/chapter locator.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

KNOWLEDGE_ROOT = Path(__file__).resolve().parents[3] / 'knowledge'
ENTRY_SCHEMA = 'infinity-ai.canon-entry.v1'
SOURCE_SCHEMA = 'infinity-ai.source.v1'
LAYERS = ('POPULAR', 'INFORMED', 'STUDIED')
MAX_LAYER = 200
MAX_SUMMARY = 280
MAX_QUOTE_WORDS = 15
KIND_PREFIX = {'REGION': 'region', 'EVENT': 'event', 'ORGANIZATION': 'org', 'CHARACTER': 'char',
               'PLACE': 'place', 'RELATIONSHIP': 'rel'}
VERIFICATION = {'RESEARCH_ONLY', 'CROSS_REFERENCED', 'SOURCE_CHECKED', 'DISPUTED', 'CAMPAIGN_CANON'}
SOURCE_CLASSES = {'S0_PRIMARY', 'S1_LICENSED', 'S2_INDEXED', 'S3_COMMUNITY', 'S4_MAINTAINER_CURATED'}
RELATIONSHIP_PREDICATES = frozenset({'OWNER_OF', 'WORKS_AT', 'MANAGES_FOR', 'EMPLOYED_BY',
    'FREQUENTS', 'MEMBER_OF', 'ALLIED_WITH', 'HOSTILE_TO', 'FAMILY_OF', 'MENTORS',
    'APPRENTICE_OF', 'REPORTS_TO', 'SERVES'})
RELATIONSHIP_AUDIENCES = frozenset({'REGIONAL_PUBLIC', 'AFFILIATED', 'EXPLICIT_NPCS'})
_QUOTED = re.compile(r'"([^"]*)"|“([^”]*)”|«([^»]*)»')


class CanonError(ValueError):
    def __init__(self, problems: list[str]) -> None:
        super().__init__('; '.join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    source_class: str
    setting_year_dr: int | None
    bibliographic_status: str


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    locator: str


@dataclass(frozen=True)
class CanonEntry:
    id: str
    kind: str
    partition_year_dr: int
    title: str
    summary: str
    valid_from_dr: int | None
    valid_to_dr: int | None
    date_precision: str
    region_id: str | None
    area_resrefs: tuple[str, ...]
    source_refs: tuple[SourceRef, ...]
    verification_status: str
    access_scope: str
    # ADR-0117: the summary's facts split by how hard they are to know (POPULAR / INFORMED /
    # STUDIED), restated in our words; never facts beyond the checked summary.
    layers: Mapping[str, str] = field(default_factory=dict)
    # ADR-0119: typed graph edge metadata; only RELATIONSHIP entries populate these fields.
    subject_id: str | None = None
    predicate: str | None = None
    object_id: str | None = None
    context_id: str | None = None
    audience: str | None = None
    eligible_affiliations: tuple[str, ...] = ()
    allowed_npc_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CanonPack:
    year_dr: int
    coverage_status: str
    entries: dict[str, CanonEntry] = field(default_factory=dict)
    sources: dict[str, Source] = field(default_factory=dict)
    revision: str = ''

    def get(self, entry_id: str) -> CanonEntry | None:
        return self.entries.get(entry_id)


def load_sources(root: Path = KNOWLEDGE_ROOT) -> dict[str, Source]:
    sources, problems = {}, []
    for path in sorted((root / 'sources').glob('*.json')):
        doc = json.loads(path.read_text(encoding='utf-8'))
        if doc.get('schema') != SOURCE_SCHEMA or doc.get('source_class') not in SOURCE_CLASSES:
            problems.append(f'{path.name}: invalid source record')
            continue
        sources[doc['source_id']] = Source(doc['source_id'], doc['title'], doc['source_class'],
                                           doc.get('setting_year_dr'),
                                           doc.get('bibliographic_status', 'TO_CONFIRM'))
    if problems:
        raise CanonError(problems)
    return sources


def _check_entry(doc: dict, year: int, sources: dict[str, Source], name: str) -> list[str]:
    problems = []
    required = ('id', 'kind', 'partition_year_dr', 'title', 'summary', 'source_refs',
                'verification_status', 'area_resrefs', 'access_scope', 'date_precision')
    missing = [k for k in required if k not in doc]
    if doc.get('schema') != ENTRY_SCHEMA or missing:
        return [f'{name}: not a canon entry v1 (missing {missing})']
    if doc['partition_year_dr'] != year:
        problems.append(f'{name}: partition year {doc["partition_year_dr"]} in the {year} directory')
    if KIND_PREFIX.get(doc['kind']) != doc['id'].split(':', 1)[0]:
        problems.append(f'{name}: id prefix does not match kind')
    relation_fields = ('subject_id', 'predicate', 'object_id', 'context_id', 'audience',
                       'eligible_affiliations', 'allowed_npc_ids')
    if doc['kind'] == 'RELATIONSHIP':
        entity_id = re.compile(r'^(npc|region|event|org|char|place):[a-z0-9-]{1,64}$')
        affiliation_id = re.compile(r'^place:[a-z0-9-]{1,64}:[A-Z][A-Z0-9_]{0,31}$')
        npc_id = re.compile(r'^npc:[a-z0-9-]{1,64}$')
        for field_name in ('subject_id', 'object_id'):
            if not isinstance(doc.get(field_name), str) or not entity_id.fullmatch(doc[field_name]):
                problems.append(f'{name}: invalid relationship {field_name}')
        if doc.get('context_id') is not None and (not isinstance(doc['context_id'], str)
                                                   or not entity_id.fullmatch(doc['context_id'])):
            problems.append(f'{name}: invalid relationship context_id')
        if doc.get('predicate') not in RELATIONSHIP_PREDICATES:
            problems.append(f'{name}: unknown relationship predicate')
        if doc.get('audience') not in RELATIONSHIP_AUDIENCES:
            problems.append(f'{name}: unknown relationship audience')
        affiliations, allowed = doc.get('eligible_affiliations') or [], doc.get('allowed_npc_ids') or []
        if not isinstance(affiliations, list) or any(not isinstance(x, str) or not affiliation_id.fullmatch(x) for x in affiliations):
            problems.append(f'{name}: invalid eligible_affiliations')
        if not isinstance(allowed, list) or any(not isinstance(x, str) or not npc_id.fullmatch(x) for x in allowed):
            problems.append(f'{name}: invalid allowed_npc_ids')
        if doc.get('access_scope') == 'COMMON_REGIONAL' and doc.get('audience') != 'REGIONAL_PUBLIC':
            problems.append(f'{name}: COMMON_REGIONAL relationships must be REGIONAL_PUBLIC')
        elif doc.get('access_scope') == 'RESTRICTED':
            if doc.get('audience') == 'AFFILIATED' and not affiliations:
                problems.append(f'{name}: AFFILIATED relationship needs eligible_affiliations')
            if doc.get('audience') == 'EXPLICIT_NPCS' and not allowed:
                problems.append(f'{name}: EXPLICIT_NPCS relationship needs allowed_npc_ids')
            if doc.get('audience') == 'REGIONAL_PUBLIC':
                problems.append(f'{name}: restricted relationship cannot be REGIONAL_PUBLIC')
        elif doc.get('access_scope') not in ('CANON_REFERENCE', 'COMMON_REGIONAL'):
            problems.append(f'{name}: unsupported relationship access_scope')
    elif any(field_name in doc for field_name in relation_fields):
        problems.append(f'{name}: relationship metadata on a non-RELATIONSHIP entry')
    if doc['verification_status'] not in VERIFICATION:
        problems.append(f'{name}: unknown verification status')
    layers = doc.get('knowledge_layers')
    if layers is not None and (not isinstance(layers, dict) or not set(layers) <= set(LAYERS)
                               or 'POPULAR' not in layers
                               or not all(isinstance(v, str) and 0 < len(v) <= MAX_LAYER
                                          for v in layers.values())):
        problems.append(f'{name}: knowledge_layers must map POPULAR/INFORMED/STUDIED to short text')
    summary = doc['summary']
    if not isinstance(summary, str) or len(summary) > MAX_SUMMARY:
        problems.append(f'{name}: summary longer than {MAX_SUMMARY} characters')
    else:
        for groups in _QUOTED.findall(summary):
            quoted = next(g for g in groups if g is not None)
            if len(quoted.split()) > MAX_QUOTE_WORDS:
                problems.append(f'{name}: quoted passage over {MAX_QUOTE_WORDS} words')
    if doc['verification_status'] != 'RESEARCH_ONLY' and not summary.strip():
        problems.append(f'{name}: checked entries need a summary')
    curation = doc.get('curation') or {}
    if doc['verification_status'] in ('SOURCE_CHECKED', 'CAMPAIGN_CANON') and not (
            curation.get('checked_by') and curation.get('checked_at')):
        problems.append(f'{name}: checked status needs curation.checked_by and checked_at')
    lo, hi = doc.get('valid_from_dr'), doc.get('valid_to_dr')
    if lo is not None and hi is not None and lo > hi:
        problems.append(f'{name}: valid_from_dr after valid_to_dr')
    refs = doc['source_refs']
    if not refs:
        problems.append(f'{name}: at least one source is required')
    for ref in refs:
        source = sources.get(ref.get('source_id'))
        if source is None:
            problems.append(f'{name}: unknown source {ref.get("source_id")}')
        elif source.source_class == 'S0_PRIMARY' and not str(ref.get('locator', '')).strip():
            problems.append(f'{name}: S0 source {source.source_id} needs a page/chapter locator')
    return problems


def _revision(entries: list[dict], used_sources: list[dict]) -> str:
    canonical = json.dumps({'entries': entries, 'sources': used_sources}, sort_keys=True,
                           separators=(',', ':'), ensure_ascii=False)
    return 'sha256:' + hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def load_partition(year_dr: int, root: Path = KNOWLEDGE_ROOT) -> CanonPack:
    """Load and validate exactly one year partition; raises CanonError on any problem."""
    period = root / 'periods' / f'{year_dr}-DR'
    manifest_path = period / 'manifest.json'
    if not manifest_path.is_file():
        raise CanonError([f'no partition for {year_dr} DR'])
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('year_dr') != year_dr:
        raise CanonError(['manifest year does not match its directory'])
    sources = load_sources(root)
    docs, problems, entries = [], [], {}
    for path in sorted(period.glob('*/*.json')):
        doc = json.loads(path.read_text(encoding='utf-8'))
        rel = str(path.relative_to(period))
        found = _check_entry(doc, year_dr, sources, rel)
        if doc.get('id') in entries:
            found.append(f'{rel}: duplicate id {doc["id"]}')
        problems += found
        if found:
            continue
        docs.append(doc)
        entries[doc['id']] = CanonEntry(
            doc['id'], doc['kind'], doc['partition_year_dr'], doc['title'], doc['summary'],
            doc.get('valid_from_dr'), doc.get('valid_to_dr'), doc['date_precision'],
            doc.get('region_id'), tuple(doc['area_resrefs']),
            tuple(SourceRef(r['source_id'], r.get('locator', '')) for r in doc['source_refs']),
            doc['verification_status'], doc['access_scope'],
            MappingProxyType(dict(doc.get('knowledge_layers') or {})),
            doc.get('subject_id'), doc.get('predicate'), doc.get('object_id'),
            doc.get('context_id'), doc.get('audience'),
            tuple(doc.get('eligible_affiliations') or ()), tuple(doc.get('allowed_npc_ids') or ()))
    for entry in entries.values():
        if entry.kind == 'RELATIONSHIP':
            for endpoint in (entry.subject_id, entry.object_id, entry.context_id):
                if endpoint and not endpoint.startswith('npc:') and endpoint not in entries:
                    problems.append(f'{entry.id}: unresolved relationship endpoint {endpoint}')
    if problems:
        raise CanonError(problems)
    used = sorted({r.source_id for e in entries.values() for r in e.source_refs})
    used_docs = [json.loads((root / 'sources' / f'{s}.json').read_text(encoding='utf-8'))
                 for s in used]
    return CanonPack(year_dr, manifest.get('coverage_status', 'EMPTY'), entries,
                     {s: sources[s] for s in used}, _revision(sorted(docs, key=lambda d: d['id']),
                                                              used_docs))
