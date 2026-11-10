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
  A creature the game data places in a region's areas (ADR-0116) is an *established* resident:
  it holds the region's common knowledge from the pin on, without waiting for the threshold.
- INQUIRY (ADR-0116): a party member hears a local who legitimately holds an entry use it in a
  validated reply (`share_knowledge`). Only companions in the party, in range and in line of sight
  of the speaker learn, and only the entries actually used. Party members never learn by time
  spent in a place, and a companion never teaches another companion.

Acquisition is recorded once per NPC/entry/branch with a snapshot of the summary, so later pack
corrections never rewrite what the NPC learned. No LLM is involved.
"""
from __future__ import annotations

import hashlib
import re
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
SHARED_EVENT = 'KnowledgeShared'
HOSTILE_ALLEGIANCE = 200   # EA.IDS: 200 and above are enemies
HUMANOID = 1               # GENERAL.IDS


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
    established: bool = False   # placed by the game data: counts from the pin (ADR-0116)


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


def _is_region(pack: CanonPack, region_id: str) -> bool:
    region = pack.get(region_id)
    return region is not None and region.kind == 'REGION'


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


def placement_regions(pack: CanonPack, area: str) -> list[str]:
    """Most specific pack regions listing `area` (an ancestor of another match is dropped)."""
    matches = [e.id for e in pack.entries.values()
               if e.kind == 'REGION' and area.upper() in {a.upper() for a in e.area_resrefs}]
    return sorted(r for r in matches
                  if not any(r != o and r in region_chain(pack, o) for o in matches))


def residents_as_stays(pack: CanonPack, residents: Mapping[str, object],
                       build_fingerprint: str) -> dict[str, tuple[Residence, ...]]:
    """Established stays for creatures the game places in the pack's regions (ADR-0116).

    `residents` maps npc_id -> an object with `areas`, `cre_resref`, `allegiance` and `general`
    (gamedata.Resident). Only non-hostile humanoids are locals."""
    out: dict[str, tuple[Residence, ...]] = {}
    for npc_id, resident in residents.items():
        if getattr(resident, 'allegiance', 0) >= HOSTILE_ALLEGIANCE \
                or getattr(resident, 'general', HUMANOID) != HUMANOID:
            continue                      # enemies, animals and monsters are not locals
        stays = {}
        for area in getattr(resident, 'areas', ()):
            for region in placement_regions(pack, area):
                stays.setdefault(region, Residence(
                    region, 0, f'GAME_DATA:{area}#{getattr(resident, "cre_resref", "")}'
                               f'@{build_fingerprint[:19]}', established=True))
        if stays:
            out[npc_id] = tuple(stays[r] for r in sorted(stays))
    return out


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
        if region is None or region.kind != 'REGION' or not stay.evidence.strip() \
                or stay.established:
            continue
        if isinstance(stay.since_game_time, bool) or not isinstance(stay.since_game_time, int):
            continue
        start = max(stay.since_game_time, anchor_time)
        spent = time_outside_party(events, npc_id, start, at_game_time)
        totals[stay.region_id] = max(totals.get(stay.region_id, 0), spent)
    return totals


def _anchor_time(events: list[Event], pin: Event) -> int | None:
    """Game time the pin counts from: its own, else the last observation before it, else (a pin
    made on an empty campaign, before the game was observed) the first observation after it."""
    if pin.game_time is not None:
        return pin.game_time
    before = [e.game_time for e in events if e.seq < pin.seq and e.game_time is not None]
    if before:
        return max(before)
    after = [e.game_time for e in events if e.seq > pin.seq and e.game_time is not None]
    return after[0] if after else None


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
    settled = {npc: {st.region_id for st in stays if st.established and st.evidence.strip()
                     and _is_region(pack, st.region_id)}
               for npc, stays in residents.items()}
    granted: list[CanonKnowledge] = []
    with store.transaction():
        for npc_id in sorted(set(first_seen) | set(backgrounds) | set(residents)):
            known = memory.known_canon(npc_id, branch_id)
            origin = set(valid_background(pack, backgrounds.get(npc_id, ()), all_sources))
            established = settled.get(npc_id, set())
            resided = established | {r for r, t in lived.get(npc_id, {}).items() if t >= threshold}
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
                            basis, region = KnowledgeBasis.RESIDENCE, r
                            trigger_event = pin if r in established else trigger
                            break
                if basis is None:
                    refusals.append(Refusal(npc_id, entry.id, 'NO_CHANNEL'))
                    continue
                game_time = at_game_time if trigger_event is trigger \
                    else (trigger_event.game_time or anchor)
                k, new = memory.record_canon_knowledge(
                    npc_id=npc_id, branch_id=branch_id, game_time=game_time, basis=basis,
                    region_id=region, entry_id=entry.id, pack_year_dr=pack.year_dr,
                    pack_revision=pack.revision, pin_event_id=pin.event_id,
                    trigger_event_id=trigger_event.event_id, title=entry.title,
                    summary=entry.summary, layers=entry.layers)
                if new:
                    granted.append(k)
    return AcquisitionReport('OK', tuple(granted), tuple(refusals), lived)


@dataclass(frozen=True)
class ShareReport:
    status: str
    granted: tuple[CanonKnowledge, ...] = ()
    refusals: tuple[Refusal, ...] = ()
    event: Event | None = None


_TITLE_WORD = re.compile(r"[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'-]{2,}")


# Common nouns that, where the person is, mean the place itself (ADR-0120 lab adjustment):
# "o dono dessa taverna" names the Copper Coronet; "o reino" names Amn; "a cidade", Athkatla.
PLACE_NOUNS = ('taverna', 'estalagem', 'hospedaria', 'estabelecimento', 'casa', 'bar', 'local',
               'lugar')
CITY_NOUNS = ('cidade',)
REALM_NOUNS = ('reino', 'país', 'nação')
_SPOKEN_WORD = re.compile(r"[\wÀ-ÖØ-öø-ÿ'-]+")


def local_aliases(pack: CanonPack, area: str | None) -> dict[str, str]:
    """Common noun -> title of what it means where `area` is: the PLACE entry of the area, the
    city (most specific pack region with a parent) and the realm (its top region)."""
    if not area:
        return {}
    aliases: dict[str, str] = {}
    places = sorted(e.title for e in pack.entries.values() if e.kind == 'PLACE'
                    and area.upper() in {a.upper() for a in e.area_resrefs})
    if places:
        aliases.update({noun: places[0] for noun in PLACE_NOUNS})
    regions = placement_regions(pack, area)
    chain = region_chain(pack, regions[0]) if regions else []
    if len(chain) > 1:
        aliases.update({noun: pack.get(chain[0]).title for noun in CITY_NOUNS})
    if chain:
        aliases.update({noun: pack.get(chain[-1]).title for noun in REALM_NOUNS})
    return aliases


def _with_aliases(text: str, aliases: Mapping[str, str] | None) -> str:
    if not aliases:
        return text
    words = {w.lower() for w in _SPOKEN_WORD.findall(text)}
    return ' '.join([text] + sorted({title for noun, title in aliases.items() if noun in words}))


def mentioned_in(entry: CanonEntry, speech: str,
                 aliases: Mapping[str, str] | None = None) -> bool:
    """True when the speech names the entry: any capitalised word of its title (3+ letters), or a
    common noun that means it where the person is (`aliases`, see `local_aliases`)."""
    words = {w.lower() for w in _SPOKEN_WORD.findall(_with_aliases(speech, aliases))}
    return any(w.lower() in words for w in _TITLE_WORD.findall(entry.title))


def identity_knowledge(pack: CanonPack, *, homeland: str | None, home: str | None,
                       campaign_year: int, build_areas: frozenset[str] | None,
                       standing: str = 'HABITANTE') -> tuple[list[str], list[str]]:
    """ADR-0117/0120: what is public where the NPC comes from and where it is, by standing.

    Returns (full, popular_only). Homeland (identity origin): the region and its sub-regions, as
    ORIGIN. Where it is (home): a resident knows the region and its ancestors, as RESIDENCE; a
    traveler knows only the popular core of the place itself (the home region and below); an
    outsider knows nothing of it. Same eligibility as the other channels (COMMON_REGIONAL, gate
    CANON_OK; the caller checks the pin). Computed when the person speaks, never stored."""
    full, popular = [], []
    for entry in sorted(pack.entries.values(), key=lambda e: e.id):
        if entry.access_scope != COMMON_SCOPE:
            continue
        chain = region_chain(pack, home_region(entry))
        local = bool(home) and home in chain                  # the place itself and below
        from_homeland = bool(homeland) and _is_region(pack, homeland) and homeland in chain
        from_home = bool(home) and home_region(entry) in region_chain(pack, home)
        if standing == 'HABITANTE':
            bucket = full if (from_homeland or from_home) else None
        elif local:
            bucket = popular if standing == 'VIAJANTE' else None
        else:
            bucket = full if from_homeland else None
        if bucket is None:
            continue
        gate = assess(pack, entry.id, campaign_year=campaign_year, build_areas=build_areas)
        if gate.status is CanonStatus.CANON_OK:
            bucket.append(entry.id)
    return full, popular


def identity_entries(pack: CanonPack, *, homeland: str | None, home: str | None,
                     campaign_year: int, build_areas: frozenset[str] | None) -> list[str]:
    """ADR-0117: a resident's homeland and home knowledge (see `identity_knowledge`)."""
    return identity_knowledge(pack, homeland=homeland, home=home, campaign_year=campaign_year,
                              build_areas=build_areas)[0]


def relationship_entries(pack: CanonPack, *, npc_id: str, affiliations: Iterable[str],
                         campaign_year: int, build_areas: frozenset[str] | None) -> list[str]:
    """ADR-0119: restricted relational facts require an explicit NPC affiliation or allowlist,
    or being one of the relation's parties (subject or object): Lehtinan knows that Bernard runs
    the Copper Coronet for him.

    Merely being in the same area is never enough. Affiliations are curated and versioned with
    the NPC identity; every edge still has to pass the campaign-year/build/source canon gate.
    Public relationships use COMMON_REGIONAL and the existing ORIGIN/RESIDENCE/INQUIRY paths.
    """
    held = set(affiliations)
    out = []
    for entry in sorted(pack.entries.values(), key=lambda e: e.id):
        if entry.kind != 'RELATIONSHIP' or entry.access_scope != 'RESTRICTED':
            continue
        eligible = npc_id in (entry.subject_id, entry.object_id) or (
            entry.audience == 'AFFILIATED' and bool(held & set(entry.eligible_affiliations))
        ) or (
            entry.audience == 'EXPLICIT_NPCS' and npc_id in entry.allowed_npc_ids
        )
        if not eligible:
            continue
        gate = assess(pack, entry.id, campaign_year=campaign_year, build_areas=build_areas)
        if gate.status is CanonStatus.CANON_OK:
            out.append(entry.id)
    return out

_WORD = re.compile(r"[\wÀ-ÖØ-öø-ÿ]{4,}")
_STOP = frozenset({'para', 'como', 'mais', 'muito', 'pela', 'pelo', 'onde', 'quem', 'isso', 'esse',
                   'essa', 'este', 'esta', 'mas', 'não', 'são', 'sobre', 'todo', 'toda', 'tudo',
                   'aqui', 'você', 'eles', 'elas', 'também', 'ainda', 'depois', 'entre', 'quando',
                   'cidade', 'terra', 'lugar', 'gente', 'coisa', 'estou', 'sou', 'porque', 'muita'})


def _content_words(text: str, exclude: str = '') -> set[str]:
    skip = {w.lower() for w in _WORD.findall(exclude)} | _STOP | _ALIAS_NOUNS
    return {w.lower() for w in _WORD.findall(text)} - skip


_ALIAS_NOUNS = frozenset(PLACE_NOUNS + CITY_NOUNS + REALM_NOUNS)


def heard(entry: CanonEntry, known_text: str | None, speech: str, question: str = '',
          aliases: Mapping[str, str] | None = None, minimum: int = 1) -> str | None:
    """Why listeners did not learn `entry` from this answer, or None when they did.

    The entry must be named in the speech, or in the question it answers ("Quem é o dono dessa
    taverna?" + "É Lehtinan."), counting the local common nouns (`aliases`). With `known_text`,
    the speech must also carry some of what the speaker knows: when the name came only from the
    question, that content must be in the speech itself, so a bare "não sei" teaches nothing."""
    in_speech = mentioned_in(entry, speech, aliases)
    in_question = bool(question) and mentioned_in(entry, question, aliases)
    if not (in_speech or in_question):
        return 'NOT_SPOKEN'
    if known_text is None:
        return None
    said = f'{speech} {question}' if in_speech else speech
    shared = _content_words(known_text, entry.title) & _content_words(said, entry.title)
    return None if len(shared) >= minimum else 'NOT_CONVEYED'


def conveyed(entry: CanonEntry, known_text: str, speech: str, minimum: int = 1,
             question: str = '') -> bool:
    """The speech names the entry *and* carries some of what the speaker knows about it: at
    least `minimum` content word of the known text besides the title and generic words. Saying "I'm from
    Athkatla" names Athkatla but teaches nothing about it. The question the answer replies to
    counts as context ("Quem governa Amn?" + "O Conselho dos Seis.")."""
    if not mentioned_in(entry, speech):
        return False
    shared = _content_words(known_text, entry.title) & \
        _content_words(f'{speech} {question}', entry.title)
    return len(shared) >= minimum


def entries_named(pack: CanonPack, held: Iterable[str], speech: str,
                  known_texts: Mapping[str, str] | None = None, question: str = '',
                  aliases: Mapping[str, str] | None = None) -> list[str]:
    """Entries the speaker holds that the speech names (and, with `known_texts`, conveys),
    whether or not the model declared them. Only the speech itself counts as naming here: a
    name in the question alone is not enough to add an entry the model did not declare."""
    out = []
    for entry_id in sorted(set(held)):
        entry = pack.get(entry_id)
        if entry is None or entry.access_scope != COMMON_SCOPE \
                or not mentioned_in(entry, speech, aliases):
            continue
        if known_texts is not None and heard(entry, known_texts.get(entry_id, ''), speech,
                                             question, aliases) is not None:
            continue
        out.append(entry_id)
    return out


def share_knowledge(store: CampaignStore, branch_id: str, pack: CanonPack, *, speaker: str,
                    listeners: Iterable[str], used_entry_ids: Iterable[str], req_id: str,
                    host_epoch: int, at_game_time: int, speech: str | None = None,
                    also_held: Iterable[str] = (), known_texts: Mapping[str, str] | None = None,
                    question: str = '', evidence: str = 'LAB_OBSERVED',
                    aliases: Mapping[str, str] | None = None) -> ShareReport:
    """INQUIRY (ADR-0116): companions who heard `speaker` use an entry learn that entry.

    The speaker must be outside the party (a companion never teaches another companion) and hold
    each entry on this branch now, or know it from its homeland or home (`also_held`, ADR-0117);
    each listener must be a party member. With `speech`, an entry
    the model claims to have used but the speech never names is refused (`NOT_SPOKEN`): listeners
    only learn what they actually heard. The speech itself is not stored. One `KnowledgeShared`
    event (no player or NPC text) is the trigger;
    re-running the same `req_id` grants nothing new.
    """
    pin_status = check_pin(store, branch_id, pack)
    if pin_status is not PinStatus.MATCH:
        return ShareReport(pin_status.value)
    if isinstance(at_game_time, bool) or not isinstance(at_game_time, int) or at_game_time < 0:
        return ShareReport('UNKNOWN_TIME')
    party = set()
    for e in store.visible_events(branch_id, 'PartyChanged'):
        if e.game_time is None or e.game_time <= at_game_time:
            party = set(e.payload.get('members') or ())
    if speaker in party:
        return ShareReport('SPEAKER_IN_PARTY', (), (Refusal(speaker, '*', 'SPEAKER_IN_PARTY'),))
    memory = MemoryStore(store)
    held = set(memory.known_canon(speaker, branch_id, at_game_time)) | set(also_held)
    refusals: list[Refusal] = []
    entries = []
    for entry_id in dict.fromkeys(used_entry_ids):
        entry = pack.get(entry_id)
        if entry_id not in held or entry is None or entry.access_scope != COMMON_SCOPE:
            refusals.append(Refusal(speaker, entry_id, 'SPEAKER_DOES_NOT_KNOW'))
        elif speech is not None and (why := heard(
                entry, known_texts.get(entry_id, '') if known_texts is not None else None,
                speech, question, aliases)) is not None:
            refusals.append(Refusal(speaker, entry_id, why))
        else:
            entries.append(entry)
    hearers = []
    for npc in sorted(set(listeners)):
        if npc == speaker or npc not in party:
            refusals.append(Refusal(npc, '*', 'NOT_A_LISTENER'))
        else:
            hearers.append(npc)
    if not entries or not hearers:
        return ShareReport('NOTHING_SHARED', (), tuple(refusals))
    pin = active_pin(store, branch_id, pack.year_dr)
    key = 'shared|' + hashlib.sha256(f'{branch_id}|{req_id}'.encode()).hexdigest()
    granted: list[CanonKnowledge] = []
    with store.transaction():
        event, _ = store.append_event(
            branch_id=branch_id, host_epoch=host_epoch, event_type=SHARED_EVENT,
            category='CAMPAIGN_OBSERVATION', game_time=at_game_time,
            payload={'speaker': speaker, 'listeners': hearers,
                     'entries': [e.id for e in entries], 'pack_revision': pack.revision},
            evidence=evidence, idempotency_key=key)
        for npc in hearers:
            known = memory.known_canon(npc, branch_id)
            for entry in entries:
                if entry.id in known:
                    continue
                region = home_region(entry) or ''
                k, new = memory.record_canon_knowledge(
                    npc_id=npc, branch_id=branch_id, game_time=at_game_time,
                    basis=KnowledgeBasis.INQUIRY, region_id=region, entry_id=entry.id,
                    pack_year_dr=pack.year_dr, pack_revision=pack.revision,
                    pin_event_id=pin.event_id, trigger_event_id=event.event_id,
                    title=entry.title, summary=entry.summary, layers=entry.layers)
                if new:
                    granted.append(k)
    return ShareReport('OK', tuple(granted), tuple(refusals), event)
