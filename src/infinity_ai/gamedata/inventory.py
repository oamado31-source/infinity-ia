# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 area inventory: which areas exist in this build and the names the game itself shows.

Read from the player's own install (S0, game data) and written only to a local directory outside
the repository (REQ-CANON-004). Names come from the world map (WMP) resolved in the game's own
dialog.tlk for the configured language; an area that is not on the world map keeps no name.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .formats import (
    AREA_TYPE, BIFF_FILE_ENTRY_SIZE, BIFF_HEADER_SIZE, CRE_IDENTITY_SIZE, CRE_TYPE,
    TLK_ENTRY_SIZE, TLK_HEADER_SIZE, WMP_TYPE, decode_tlk_string, parse_are_actors,
    parse_biff_files, parse_biff_header, parse_cre_identity, parse_key, parse_tlk_entry,
    parse_tlk_header, parse_wmp, tlk_entry_offset,
)
from .source import ByteSource, GameDataError

INVENTORY_SCHEMA = 'infinity-ai.area-inventory.v1'
RESIDENTS_SCHEMA = 'infinity-ai.residents.v1'
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LOCAL_DIR = Path.home() / '.infinity-ai' / 'knowledge'
_MAX_FILE = 64 * 1024 * 1024


@dataclass(frozen=True)
class AreaRecord:
    resref: str
    display_name: str | None
    on_worldmap: bool
    worldmap_number: int | None = None
    caption_strref: int | None = None
    in_override: bool = False


@dataclass(frozen=True)
class AreaInventory:
    build_fingerprint: str
    language: str
    areas: tuple[AreaRecord, ...]
    worldmaps: tuple[int, ...] = field(default_factory=tuple)
    generated_at: str = ''

    def names(self) -> dict[str, str]:
        return {a.resref: a.display_name for a in self.areas if a.display_name}

    def resrefs(self) -> frozenset[str]:
        return frozenset(a.resref for a in self.areas)

    def to_json(self) -> dict:
        return {
            'schema': INVENTORY_SCHEMA, 'build_fingerprint': self.build_fingerprint,
            'language': self.language, 'generated_at': self.generated_at,
            'source': {'class': 'S0_PRIMARY', 'kind': 'GAME_DATA_LOCAL',
                       'resources': ['chitin.key', '*.ARE', 'WMP', f'lang/{self.language}/dialog.tlk']},
            'worldmaps': list(self.worldmaps),
            'areas': [a.__dict__ for a in self.areas],
        }


def _read_whole(source: ByteSource, path: str) -> bytes:
    size = source.size(path)
    if size is None:
        raise GameDataError(f'missing {path}')
    if size > _MAX_FILE:
        raise GameDataError(f'{path} too large ({size} bytes)')
    return source.read(path, 0, size)


class _Resources:
    """Fetch resources by resref/type: override folder first, then the BIF listed in the KEY."""

    def __init__(self, source: ByteSource) -> None:
        self.source = source
        self.key = parse_key(_read_whole(source, 'chitin.key'))
        self._bif_tables: dict[int, dict] = {}

    def _bif_table(self, bif_index: int) -> dict:
        if bif_index not in self._bif_tables:
            bif = self.key.bifs[bif_index]
            header = parse_biff_header(self.source.read(bif.path, 0, BIFF_HEADER_SIZE))
            table = self.source.read(bif.path, header.files_offset,
                                     BIFF_FILE_ENTRY_SIZE * header.file_count)
            self._bif_tables[bif_index] = parse_biff_files(table, header.file_count)
        return self._bif_tables[bif_index]

    def locate(self, resref: str, type_: int, ext: str,
               override: set[str]) -> tuple[str, int, int | None] | None:
        """(path, offset, size) without reading; size None for override files (caller sizes)."""
        if resref.upper() in override:
            return f'override/{resref}.{ext}', 0, None
        entry = self.key.find(resref, type_)
        if entry is None or entry.bif_index >= len(self.key.bifs):
            return None
        file = self._bif_table(entry.bif_index).get(entry.file_index)
        if file is None or file.size > _MAX_FILE:
            return None
        return self.key.bifs[entry.bif_index].path, file.offset, file.size

    def get(self, resref: str, type_: int, ext: str) -> bytes | None:
        override = f'override/{resref}.{ext}'
        if self.source.size(override) is not None:
            return _read_whole(self.source, override)
        entry = self.key.find(resref, type_)
        if entry is None or entry.bif_index >= len(self.key.bifs):
            return None
        file = self._bif_table(entry.bif_index).get(entry.file_index)
        if file is None or file.size > _MAX_FILE:
            return None
        return self.source.read(self.key.bifs[entry.bif_index].path, file.offset, file.size)


def resolve_strings(source: ByteSource, tlk_path: str, strrefs: set[int]) -> dict[int, str]:
    """Look up only the needed strrefs (two batched reads), not the whole dialog.tlk."""
    if not strrefs:
        return {}
    header = parse_tlk_header(source.read(tlk_path, 0, TLK_HEADER_SIZE))
    wanted = sorted(s for s in strrefs if 0 <= s < header.count)
    entries = source.read_many([(tlk_path, tlk_entry_offset(s), TLK_ENTRY_SIZE) for s in wanted])
    spans = [parse_tlk_entry(e) for e in entries]
    reads = [(s, off, n) for s, (off, n) in zip(wanted, spans) if 0 < n <= 4096]
    raws = source.read_many([(tlk_path, header.strings_offset + off, n) for _, off, n in reads])
    return {s: decode_tlk_string(raw) for (s, _, _), raw in zip(reads, raws)
            if decode_tlk_string(raw)}


def build_inventory(source: ByteSource, *, language: str, build_fingerprint: str,
                    now: str | None = None) -> AreaInventory:
    resources = _Resources(source)
    override_areas = {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.are')}
    all_areas = {r.resref for r in resources.key.of_type(AREA_TYPE)} | override_areas

    wmp_names = {r.resref for r in resources.key.of_type(WMP_TYPE)} | \
        {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.wmp')}
    on_map: dict[str, tuple[int, int | None]] = {}
    worldmap_numbers = set()
    for name in sorted(wmp_names):
        data = resources.get(name, WMP_TYPE, 'wmp')
        if data is None:
            continue
        for worldmap in parse_wmp(data):
            worldmap_numbers.add(worldmap.number)
            for area in worldmap.areas:
                strref = area.caption_strref if area.caption_strref is not None \
                    else area.tooltip_strref
                on_map.setdefault(area.resref, (worldmap.number, strref))

    strings = resolve_strings(source, f'lang/{language}/dialog.tlk',
                              {s for _, s in on_map.values() if s is not None})
    records = []
    for resref in sorted(all_areas | set(on_map)):
        number, strref = on_map.get(resref, (None, None))
        records.append(AreaRecord(resref, strings.get(strref) if strref is not None else None,
                                  resref in on_map, number, strref, resref in override_areas))
    stamp = now or datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    return AreaInventory(build_fingerprint, language, tuple(records),
                         tuple(sorted(worldmap_numbers)), stamp)


@dataclass(frozen=True)
class Resident:
    """A creature the game places in an area (S0 evidence for ADR-0116 established residents)."""
    npc_id: str               # npc:<script name in lowercase>, or npc:cre-<resref> without one
    script_name: str
    cre_resref: str
    areas: tuple[str, ...]
    display_name: str | None
    name_strref: int | None
    allegiance: int
    general: int = 1
    race: int = 0
    klass: int = 0
    gender: int = 0
    alignment: int = 0
    wisdom: int = 0
    intelligence: int = 0


@dataclass(frozen=True)
class ResidentInventory:
    build_fingerprint: str
    language: str
    residents: tuple[Resident, ...]
    areas: tuple[str, ...]
    skipped_without_script: int = 0
    generated_at: str = ''

    def to_json(self) -> dict:
        return {
            'schema': RESIDENTS_SCHEMA, 'build_fingerprint': self.build_fingerprint,
            'language': self.language, 'generated_at': self.generated_at,
            'source': {'class': 'S0_PRIMARY', 'kind': 'GAME_DATA_LOCAL',
                       'resources': ['chitin.key', '*.ARE', '*.CRE', f'lang/{self.language}/dialog.tlk']},
            'areas': list(self.areas), 'skipped_without_script': self.skipped_without_script,
            'residents': [dict(r.__dict__, areas=list(r.areas)) for r in self.residents],
        }


def resident_id_for_cre(cre_resref: str) -> str:
    """NPC id for a creature without a script name, matched by the CRE the probe reports."""
    return f'npc:cre-{cre_resref.lower()}'


def _read_located(source: ByteSource, located: dict[str, tuple[str, int, int | None]],
                  limit: int | None = None) -> dict[str, bytes]:
    """Read many located resources in one batch; override files are sized first."""
    requests, keys = [], []
    for key, (path, offset, size) in sorted(located.items()):
        if size is None:
            size = source.size(path)
            if size is None or size > _MAX_FILE:
                continue
        requests.append((path, offset, size if limit is None else min(size, limit)))
        keys.append(key)
    return dict(zip(keys, source.read_many(requests)))


def build_residents(source: ByteSource, *, language: str, build_fingerprint: str,
                    areas: set[str] | frozenset[str], now: str | None = None) -> ResidentInventory:
    """Creatures placed in `areas` by the game data, identified by their script name."""
    resources = _Resources(source)
    over_are = {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.are')}
    over_cre = {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.cre')}
    wanted = sorted({a.upper() for a in areas})
    located = {a: loc for a in wanted
               if (loc := resources.locate(a, AREA_TYPE, 'are', over_are)) is not None}
    are_data = _read_located(source, located)

    placements: dict[str, set[str]] = {}
    embedded: dict[str, bytes] = {}
    for area, data in are_data.items():
        for actor in parse_are_actors(data):
            if actor.embedded is not None:
                key = f'{area}#{actor.actor_name}'
                embedded[key] = actor.embedded
                placements.setdefault(key, set()).add(area)
            elif actor.cre_resref:
                placements.setdefault(actor.cre_resref, set()).add(area)
    cre_located = {c: loc for c in placements if c not in embedded
                   if (loc := resources.locate(c, CRE_TYPE, 'cre', over_cre)) is not None}
    cre_data = _read_located(source, cre_located, limit=CRE_IDENTITY_SIZE)
    cre_data.update(embedded)

    identities = {}
    for key, data in cre_data.items():
        try:
            identities[key] = parse_cre_identity(data)
        except GameDataError:
            continue
    strings = resolve_strings(source, f'lang/{language}/dialog.tlk',
                              {i.name_strref for i in identities.values()
                               if i.name_strref is not None})
    by_npc: dict[str, Resident] = {}
    skipped = 0
    for key, ident in sorted(identities.items()):
        if ident.script_name:
            npc_id = f'npc:{ident.script_name.lower()}'
        elif '#' not in key:
            npc_id = resident_id_for_cre(key)       # no script name: known by its CRE file
        else:
            skipped += 1                             # embedded, no script: nothing to match on
            continue
        prev = by_npc.get(npc_id)
        found = tuple(sorted(placements[key] | set(prev.areas if prev else ())))
        cre = key if '#' not in key else ''
        by_npc[npc_id] = Resident(npc_id, ident.script_name, prev.cre_resref if prev else cre,
                                  found, strings.get(ident.name_strref) if ident.name_strref
                                  is not None else None, ident.name_strref, ident.allegiance,
                                  ident.general, ident.race, ident.klass, ident.gender,
                                  ident.alignment, ident.wisdom, ident.intelligence)
    stamp = now or datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    return ResidentInventory(build_fingerprint, language, tuple(by_npc[k] for k in sorted(by_npc)),
                             tuple(sorted(are_data)), skipped, stamp)


def _install_dir(base: Path, build_fingerprint: str) -> Path:
    digest = build_fingerprint.split(':', 1)[-1]
    if not digest or not all(c in '0123456789abcdef' for c in digest.lower()):
        digest = hashlib.sha256(build_fingerprint.encode()).hexdigest()
    return base / f'install-{digest[:16].lower()}'


def write_inventory(inventory: AreaInventory | ResidentInventory,
                    base_dir: Path = DEFAULT_LOCAL_DIR, *, repo_root: Path = REPO_ROOT) -> Path:
    kind = 'residents' if isinstance(inventory, ResidentInventory) else 'areas'
    target = _install_dir(Path(base_dir), inventory.build_fingerprint) / \
        f'{kind}.{inventory.language}.json'
    resolved, repo = target.resolve(), repo_root.resolve()
    if resolved == repo or repo in resolved.parents:
        raise GameDataError('refusing to write game-derived data inside the repository')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(inventory.to_json(), ensure_ascii=False, indent=2) + '\n',
                      encoding='utf-8')
    return target


def load_local_names(build_fingerprint: str, language: str,
                     base_dir: Path = DEFAULT_LOCAL_DIR) -> dict[str, str]:
    """Area display names from a previously written inventory for this exact build, or {}."""
    path = _install_dir(Path(base_dir), build_fingerprint) / f'areas.{language}.json'
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding='utf-8'))
    if doc.get('schema') != INVENTORY_SCHEMA or doc.get('build_fingerprint') != build_fingerprint:
        return {}
    return {a['resref']: a['display_name'] for a in doc.get('areas', []) if a.get('display_name')}


def load_local_resrefs(build_fingerprint: str, language: str,
                       base_dir: Path = DEFAULT_LOCAL_DIR) -> frozenset[str] | None:
    """Area resrefs of this exact build from a written inventory, or None (gate: NO_INVENTORY)."""
    path = _install_dir(Path(base_dir), build_fingerprint) / f'areas.{language}.json'
    if not path.is_file():
        return None
    doc = json.loads(path.read_text(encoding='utf-8'))
    if doc.get('schema') != INVENTORY_SCHEMA or doc.get('build_fingerprint') != build_fingerprint:
        return None
    return frozenset(a['resref'] for a in doc.get('areas', []))


def load_local_residents(build_fingerprint: str, language: str,
                         base_dir: Path = DEFAULT_LOCAL_DIR) -> dict[str, Resident]:
    """Residents of this exact build from a written inventory (npc_id -> Resident), or {}."""
    path = _install_dir(Path(base_dir), build_fingerprint) / f'residents.{language}.json'
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding='utf-8'))
    if doc.get('schema') != RESIDENTS_SCHEMA or doc.get('build_fingerprint') != build_fingerprint:
        return {}
    out = {}
    for r in doc.get('residents', []):
        try:
            out[r['npc_id']] = Resident(r['npc_id'], r['script_name'], r['cre_resref'],
                                        tuple(r['areas']), r.get('display_name'),
                                        r.get('name_strref'), int(r['allegiance']),
                                        int(r.get('general', 1)), int(r.get('race', 0)),
                                        int(r.get('klass', 0)), int(r.get('gender', 0)),
                                        int(r.get('alignment', 0)), int(r.get('wisdom', 0)),
                                        int(r.get('intelligence', 0)))
        except (KeyError, TypeError, ValueError):
            continue
    return out
