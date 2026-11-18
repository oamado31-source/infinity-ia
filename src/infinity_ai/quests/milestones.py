# SPDX-License-Identifier: Apache-2.0
"""ADR-0134: quest milestones from an allowlisted, read-only look at game variables.

The first slice of ADR-0095 (allowlisted read-only observation) and ADR-0096 (curated, versioned
meaning per build):

- A local catalog, outside the repository (the variable names are game data and spoilers, REQ-
  CANON-004 and ADR-0095 item 6), ties each opaque `probe_id` to one GLOBAL variable, and each
  milestone (`semantic_id`, like `quest:coronet-slaves:RESOLVED`) to typed predicates over probes.
- The in-game box reads only the catalog's variables, only when the player sends a question, and
  sends `{probe_id: value or null}`; null means the variable does not exist (never "0").
- `evaluate` is pure and deterministic. A missing probe is UNKNOWN, never false; two milestones of
  one exclusive group true together are AMBIGUOUS; another build or a catalog not yet CURATED
  (meaning proven in the game by the maintainer) blocks everything.
- A MAPPED milestone becomes one `QuestMilestoneObserved` event per branch, without raw values. A
  later reading that no longer meets it does not undo it (`BLOCKED_TRANSITION`, logged only).
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from ..state.store import CampaignStore, Event

CATALOG_SCHEMA = 'infinity-ai.quest-catalog.v1'
MILESTONE_EVENT = 'QuestMilestoneObserved'
POLICY = 'adr-0134-milestones-v1'
DEFAULT_CATALOG = Path.home() / '.infinity-ai' / 'quests' / 'catalog.json'

CURATED, REVIEW_PENDING, REVOKED = 'CURATED', 'REVIEW_PENDING', 'REVOKED'
CATALOG_STATUSES = (CURATED, REVIEW_PENDING, REVOKED)
MAPPED, NOT_MET, UNKNOWN, AMBIGUOUS = 'MAPPED', 'NOT_MET', 'UNKNOWN', 'AMBIGUOUS'
BLOCKED_BUILD, BLOCKED_MAPPING = 'BLOCKED_BUILD', 'BLOCKED_MAPPING'
OPS = ('eq', 'in', 'ge')
SCOPES = ('GLOBAL',)              # D3: global variables only in the first slice
MAX_PROBES = 16
VALUE_MIN, VALUE_MAX = -2**31, 2**31 - 1

PROBE_ID = re.compile(r'[a-z0-9][a-z0-9-]{0,31}')
VARIABLE_NAME = re.compile(r'[A-Za-z0-9_#-]{1,32}')
SEMANTIC_ID = re.compile(r'quest:[a-z0-9][a-z0-9-]{0,47}:[A-Z][A-Z_]{0,31}')


@dataclass(frozen=True)
class Probe:
    probe_id: str
    name: str            # the game variable; local only, never in a prompt, log or event
    scope: str = 'GLOBAL'


@dataclass(frozen=True)
class Predicate:
    probe_id: str
    op: str
    values: tuple[int, ...]

    def holds(self, value: int) -> bool:
        if self.op == 'eq':
            return value == self.values[0]
        if self.op == 'in':
            return value in self.values
        return value >= self.values[0]          # ge


@dataclass(frozen=True)
class Rule:
    semantic_id: str
    predicates: tuple[Predicate, ...]
    exclusive_group: str | None = None


@dataclass(frozen=True)
class Catalog:
    revision: str
    build_fingerprint: str
    status: str
    probes: tuple[Probe, ...]
    rules: tuple[Rule, ...]
    digest: str = ''


@dataclass(frozen=True)
class Assertion:
    semantic_id: str
    status: str
    probes: tuple[str, ...] = ()


def _int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or not VALUE_MIN <= value <= VALUE_MAX:
        return None
    return value


def parse_catalog(doc: object) -> Catalog | None:
    """A strictly valid catalog, or None (anything odd blocks the whole catalog)."""
    if not isinstance(doc, dict) or doc.get('schema') != CATALOG_SCHEMA:
        return None
    revision, build, status = doc.get('revision'), doc.get('build_fingerprint'), doc.get('status')
    if not isinstance(revision, str) or not revision or not isinstance(build, str) or not build \
            or status not in CATALOG_STATUSES:
        return None
    raw_probes, raw_rules = doc.get('probes'), doc.get('rules')
    if not isinstance(raw_probes, list) or not isinstance(raw_rules, list) \
            or len(raw_probes) > MAX_PROBES:
        return None
    probes: dict[str, Probe] = {}
    for p in raw_probes:
        if not isinstance(p, dict):
            return None
        pid, name, scope = p.get('probe_id'), p.get('name'), p.get('scope', 'GLOBAL')
        if not isinstance(pid, str) or not PROBE_ID.fullmatch(pid) or pid in probes \
                or not isinstance(name, str) or not VARIABLE_NAME.fullmatch(name) \
                or scope not in SCOPES:
            return None
        probes[pid] = Probe(pid, name, scope)
    rules: list[Rule] = []
    seen: set[str] = set()
    for r in raw_rules:
        if not isinstance(r, dict):
            return None
        sid, group, raw_preds = r.get('semantic_id'), r.get('exclusive_group'), r.get('all')
        if not isinstance(sid, str) or not SEMANTIC_ID.fullmatch(sid) or sid in seen \
                or (group is not None and (not isinstance(group, str) or not group)) \
                or not isinstance(raw_preds, list) or not raw_preds:
            return None
        predicates = []
        for q in raw_preds:
            if not isinstance(q, dict) or q.get('probe_id') not in probes or q.get('op') not in OPS:
                return None
            raw_values = q.get('values')
            if not isinstance(raw_values, list) or not raw_values:
                return None
            values = tuple(_int(v) for v in raw_values)
            if any(v is None for v in values) or (q['op'] != 'in' and len(values) != 1):
                return None
            predicates.append(Predicate(q['probe_id'], q['op'], values))
        seen.add(sid)
        rules.append(Rule(sid, tuple(predicates), group))
    digest = 'sha256:' + hashlib.sha256(json.dumps(doc, sort_keys=True, ensure_ascii=False)
                                        .encode('utf-8')).hexdigest()
    return Catalog(revision, build, status, tuple(probes.values()), tuple(rules), digest)


def load_catalog(path: Path = DEFAULT_CATALOG) -> Catalog | None:
    """The local catalog, or None when there is none or it is not valid."""
    try:
        doc = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return parse_catalog(doc)


def evaluate(catalog: Catalog | None, probes: Mapping[str, int | None] | None,
             build_fingerprint: str) -> tuple[Assertion, ...]:
    """Each milestone of the catalog against one reading. Pure and deterministic."""
    if catalog is None:
        return ()
    if catalog.build_fingerprint != build_fingerprint:
        return tuple(Assertion(r.semantic_id, BLOCKED_BUILD) for r in catalog.rules)
    if catalog.status != CURATED:
        return tuple(Assertion(r.semantic_id, BLOCKED_MAPPING) for r in catalog.rules)
    reading = probes or {}
    out: list[Assertion] = []
    for rule in catalog.rules:
        used = tuple(dict.fromkeys(p.probe_id for p in rule.predicates))
        values = [reading.get(p.probe_id) for p in rule.predicates]
        if any(v is None for v in values):
            out.append(Assertion(rule.semantic_id, UNKNOWN, used))
        elif all(p.holds(v) for p, v in zip(rule.predicates, values)):
            out.append(Assertion(rule.semantic_id, MAPPED, used))
        else:
            out.append(Assertion(rule.semantic_id, NOT_MET, used))
    groups: dict[str, list[int]] = {}
    for i, rule in enumerate(catalog.rules):
        if rule.exclusive_group and out[i].status == MAPPED:
            groups.setdefault(rule.exclusive_group, []).append(i)
    for indexes in groups.values():
        if len(indexes) > 1:
            for i in indexes:
                out[i] = Assertion(out[i].semantic_id, AMBIGUOUS, out[i].probes)
    return tuple(out)


def milestones_of(store: CampaignStore, branch_id: str) -> dict[str, Event]:
    """The milestones this branch has seen, by semantic id (the first event of each)."""
    out: dict[str, Event] = {}
    for event in store.visible_events(branch_id, MILESTONE_EVENT):
        out.setdefault(event.payload.get('semantic_id'), event)
    return out


@dataclass(frozen=True)
class Observation:
    recorded: tuple[str, ...]       # new milestones recorded now
    held: tuple[str, ...]           # every milestone of the branch, sorted
    regressed: tuple[str, ...]      # held, but this reading no longer meets them (not undone)
    unclear: tuple[str, ...]        # AMBIGUOUS this reading (nothing recorded)


def record_milestones(store: CampaignStore, branch_id: str, catalog: Catalog | None,
                      assertions: tuple[Assertion, ...], *, game_time: int | None,
                      host_epoch: int = 0, evidence: str = 'LAB_OBSERVED') -> Observation:
    """Record each MAPPED milestone once per branch; report what the branch holds."""
    held = milestones_of(store, branch_id)
    recorded = []
    for a in assertions:
        if a.status != MAPPED or a.semantic_id in held or catalog is None:
            continue
        payload = {'semantic_id': a.semantic_id, 'source': 'GAME',
                   'mapping_revision': catalog.revision,
                   'catalog_digest': catalog.digest, 'probes': list(a.probes), 'policy': POLICY}
        with store.transaction():
            event, _ = store.append_event(
                branch_id=branch_id, host_epoch=host_epoch, event_type=MILESTONE_EVENT,
                category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
                evidence=evidence, idempotency_key=f'milestone|{branch_id}|{a.semantic_id}')
        held[a.semantic_id] = event
        recorded.append(a.semantic_id)
    regressed = tuple(sorted(a.semantic_id for a in assertions
                             if a.status == NOT_MET and a.semantic_id in held))
    unclear = tuple(sorted(a.semantic_id for a in assertions if a.status == AMBIGUOUS))
    return Observation(tuple(recorded), tuple(sorted(held)), regressed, unclear)


def record_overlay_milestone(store: CampaignStore, branch_id: str, semantic_id: str, *,
                             quest_id: str, game_time: int | None, host_epoch: int = 0,
                             evidence: str = 'LAB_OBSERVED') -> Event:
    """SPEC-011: a milestone reached by a narrative quest of ours (source OVERLAY), not read from
    the game. Same event and key as a game milestone: once per branch."""
    if not SEMANTIC_ID.fullmatch(semantic_id):
        raise ValueError('bad semantic id')
    payload = {'semantic_id': semantic_id, 'source': 'OVERLAY', 'quest_id': quest_id,
               'policy': POLICY}
    with store.transaction():
        event, _ = store.append_event(
            branch_id=branch_id, host_epoch=host_epoch, event_type=MILESTONE_EVENT,
            category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
            evidence=evidence, idempotency_key=f'milestone|{branch_id}|{semantic_id}')
    return event
