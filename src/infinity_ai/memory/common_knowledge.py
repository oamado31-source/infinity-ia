# SPDX-License-Identifier: Apache-2.0
"""ADR-0114: how an NPC comes to hold common regional knowledge from the pinned canon pack.

Only entries with access_scope COMMON_REGIONAL that pass the canon gate (CANON_OK) on a branch
whose pack pin matches are eligible, through one of these deterministic channels:

- ORIGIN: the NPC's curated background region (with a checked S0/S1 source). Covers the region
  and its sub-regions. Valid for any NPC, in the party or not.
- RESIDENCE: an NPC *outside the party* lived in a region (curated stay with evidence) for at
  least `threshold` game time, counted only after the current pin (a new revision never teaches
  retroactively, ADR-0059 item 3) and only while the NPC was not in the party. Covers the region
  and its ancestors: living in Athkatla teaches what is public in Amn, living elsewhere in Amn does
  not teach what is specific to Athkatla.
- INQUIRY (reserved, not granted yet): an observed active act by a party member, such as asking a
  local who holds the knowledge or researching it. Party members never learn by time spent in a
  place: being in Athkatla for days without asking about the Council teaches nothing, and asking
  another companion who was only "there" does not count either.

Acquisition is recorded once per NPC/entry/branch with a snapshot of the summary, so later pack
corrections never rewrite what the NPC learned. No LLM is involved.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from ..canon.gate import CanonStatus, assess
from ..canon.pack import CanonEntry, CanonPack, Source, load_sources
from ..canon.pin import PinStatus, active_pin, check_pin
from ..state.store import CampaignStore, Event
from .model import CanonKnowledge, KnowledgeBasis
from .store import MemoryStore

COMMON_SCOPE = 'COMMON_REGIONAL'
DEFAULT_RESIDENCE_THRESHOLD = 7200  # one game day if 300 = 1 hour; unit not yet confirmed in the lab
STRONG_CLASSES = frozenset({'S0_PRIMARY', 'S1_LICENSED'})


@dataclass(frozen=True)
class BackgroundRegion:
    """A curated persona background (ORIGIN channel)."""
    region_id: str
    source_id: str
    locator: str
    checked_by: str
    checked_at: str


@dataclass(frozen=True)
class Residence:
    """A curated stay of an NPC outside the party (RESIDENCE channel).

    `evidence` says how the stay is known (for example the area where the game places the
    creature); a stay without evidence is ignored."""
    region_id: str
    since_game_time: int
    evidence: str


@dataclass(frozen=True)
class Refusal:
    npc_id: str
    entry_id: str
    reason: str


@dataclass(frozen=True)
class AcquisitionReport:
    status: str
    granted: tuple[CanonKnowledge, ...] = ()
    refusals: tuple[Refusal, ...] = field(default_factory=tuple)
    residence: Mapping[str, Mapping[str, int]] = field(default_factory=dict)


def home_region(entry: CanonEntry) -> str | None:
    return entry.id if entry.kind == 'REGION' else entry.region_id


def region_chain(pack: CanonPack, region_id: str | None) -> list[str]:
    """region_id followed by its ancestors in the pack (cycle-safe)."""
    chain: list[str] = []
    while region_id and region_id not in chain:
        region = pack.get(region_id)
        if region is None or region.kind != 'REGION':
            break
        chain.append(region_id)
        region_id = region.region_id
    return chain


def valid_background(pack: CanonPack, regions: Iterable[BackgroundRegion],
                     sources: Mapping[str, Source]) -> list[str]:
    """Background regions that are in the pack and backed by a checked S0/S1 source."""
    ok = []
    for b in regions:
        region, source = pack.get(b.region_id), sources.get(b.source_id)
        if region is None or region.kind != 'REGION' or source is None:
            continue
        if source.source_class not in STRONG_CLASSES or not b.locator.strip():
            continue
        if b.checked_by and b.checked_at:
            ok.append(b.region_id)
    return ok


def time_outside_party(events: Iterable[Event], npc_id: str, start: int, end: int) -> int:
    """Game time in [start, end) during which `npc_id` was not a party member."""
    if end <= start:
        return 0
    in_party, clock, total = False, start, 0
    for event in events:
        if event.event_type != 'PartyChanged':
            continue
        t = event.game_time
        if t is not None and t > clock:
            until = min(t, end)
            if not in_party:
                total += until - clock
            clock = until
            if clock >= end:
                return total
        in_party = npc_id in (event.payload.get('members') or ())
    return total + (end - clock if not in_party else 0)


def residence_time(pack: CanonPack, events: list[Event], npc_id: str,
                   stays: Iterable[Residence], *, anchor_time: int,
                   at_game_time: int) -> dict[str, int]:
    """Time each region counts for the RESIDENCE channel (after the pin, outside the party)."""
    totals: dict[str, int] = {}
    for stay in stays:
        region = pack.get(stay.region_id)
        if region is None or region.kind != 'REGION' or not stay.evidence.strip():
            continue
        if isinstance(stay.since_game_time, bool) or not isinstance(stay.since_game_time, int):
            continue
        start = max(stay.since_game_time, anchor_time)
        spent = time_outside_party(events, npc_id, start, at_game_time)
        totals[stay.region_id] = max(totals.get(stay.region_id, 0), spent)
    return totals


def _anchor_time(events: list[Event], pin: Event) -> int | None:
    if pin.game_time is not None:
        return pin.game_time
    before = [e.game_time for e in events if e.seq < pin.seq and e.game_time is not None]
    return max(before) if before else None


def acquire_common_knowledge(store: CampaignStore, branch_id: str, pack: CanonPack, *,
                             campaign_year: int, build_areas: frozenset[str] | None,
                             backgrounds: Mapping[str, Iterable[BackgroundRegion]] | None = None,
                             residents: Mapping[str, Iterable[Residence]] | None = None,
                             threshold: int = DEFAULT_RESIDENCE_THRESHOLD,
                             at_game_time: int,
                             sources: Mapping[str, Source] | None = None) -> AcquisitionReport:
    """Grant what the rule allows now; returns typed refusals for everything else."""
    pin_status = check_pin(store, branch_id, pack)
    if pin_status is not PinStatus.MATCH:
        return AcquisitionReport(pin_status.value)
    if isinstance(at_game_time, bool) or not isinstance(at_game_time, int) or at_game_time < 0:
        return AcquisitionReport('UNKNOWN_TIME')
    pin = active_pin(store, branch_id, pack.year_dr)
    events = store.visible_events(branch_id)
    timed = [e for e in events if e.game_time is not None and e.game_time <= at_game_time]
    anchor = _anchor_time(events, pin)
    if not timed or anchor is None:
        return AcquisitionReport('NO_OBSERVATION')
    trigger = timed[-1]

    eligible: dict[str, CanonEntry] = {}
    refusals: list[Refusal] = []
    for entry in sorted(pack.entries.values(), key=lambda e: e.id):
        if entry.access_scope != COMMON_SCOPE:
            continue
        gate = assess(pack, entry.id, campaign_year=campaign_year, build_areas=build_areas)
        if gate.status is not CanonStatus.CANON_OK:
            refusals.append(Refusal('*', entry.id, f'GATE_{gate.status.value}'))
        elif not home_region(entry):
            refusals.append(Refusal('*', entry.id, 'NO_REGION'))
        else:
            eligible[entry.id] = entry

    backgrounds = backgrounds or {}
    residents = residents or {}
    memory = MemoryStore(store)
    all_sources = sources if sources is not None else (load_sources() if backgrounds else {})
    first_seen: dict[str, Event] = {}
    for e in events:
        if e.event_type == 'PartyChanged':
            for npc in e.payload.get('members') or ():
                first_seen.setdefault(npc, e)
    lived = {npc: residence_time(pack, events, npc, stays, anchor_time=anchor,
                                 at_game_time=at_game_time)
             for npc, stays in residents.items()}
    granted: list[CanonKnowledge] = []
    with store.transaction():
        for npc_id in sorted(set(first_seen) | set(backgrounds) | set(residents)):
            known = memory.known_canon(npc_id, branch_id)
            origin = set(valid_background(pack, backgrounds.get(npc_id, ()), all_sources))
            resided = {r for r, t in lived.get(npc_id, {}).items() if t >= threshold}
            for entry in eligible.values():
                if entry.id in known:
                    continue
                home = home_region(entry)
                chain = region_chain(pack, home)
                basis = region = trigger_event = None
                if origin & set(chain):
                    basis, region = KnowledgeBasis.ORIGIN, next(r for r in chain if r in origin)
                    trigger_event = first_seen.get(npc_id, pin)
                else:
                    for r in sorted(resided):
                        if home in region_chain(pack, r):
                            basis, region, trigger_event = KnowledgeBasis.RESIDENCE, r, trigger
                            break
                if basis is None:
                    refusals.append(Refusal(npc_id, entry.id, 'NO_CHANNEL'))
                    continue
                game_time = (trigger_event.game_time or anchor) if basis is KnowledgeBasis.ORIGIN \
                    else at_game_time
                k, new = memory.record_canon_knowledge(
                    npc_id=npc_id, branch_id=branch_id, game_time=game_time, basis=basis,
                    region_id=region, entry_id=entry.id, pack_year_dr=pack.year_dr,
                    pack_revision=pack.revision, pin_event_id=pin.event_id,
                    trigger_event_id=trigger_event.event_id, title=entry.title,
                    summary=entry.summary)
                if new:
                    granted.append(k)
    return AcquisitionReport('OK', tuple(granted), tuple(refusals), lived)
