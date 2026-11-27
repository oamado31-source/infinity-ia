# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 area inventory: which areas exist in this build and the names the game itself shows.

Read from the player's own install (S0, game data) and written only to a local directory outside
the repository (REQ-CANON-004). Names come from the world map (WMP) resolved in the game's own
dialog.tlk for the configured language; an area that is not on the world map keeps no name.
"""
from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .formats import (
    AREA_TYPE, BIFF_FILE_ENTRY_SIZE, BIFF_HEADER_SIZE, CRE_IDENTITY_SIZE, CRE_TYPE, DLG_TYPE,
    BIFF_TILESET_ENTRY_SIZE, ITM_TYPE, STO_TYPE, TIS_TYPE, TLK_ENTRY_SIZE, TLK_HEADER_SIZE, WMP_TYPE, decode_tlk_string,
    parse_are_actors, parse_biff_files, parse_biff_header, parse_biff_tilesets, parse_cre_dialog, parse_cre_identity,
    parse_dlg_store_refs, parse_itm_summary, parse_key, parse_sto, parse_tlk_entry,
    parse_tlk_header, parse_wmp, tlk_entry_offset,
)
from .source import ByteSource, GameDataError

INVENTORY_SCHEMA = 'infinity-ai.area-inventory.v1'
RESIDENTS_SCHEMA = 'infinity-ai.residents.v1'
STORES_SCHEMA = 'infinity-ai.stores.v1'
SPL_TYPE = 0x3EE
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
        self._tileset_tables: dict[int, dict] = {}

    def _bif_table(self, bif_index: int) -> dict:
        if bif_index not in self._bif_tables:
            bif = self.key.bifs[bif_index]
            header = parse_biff_header(self.source.read(bif.path, 0, BIFF_HEADER_SIZE))
            table = self.source.read(bif.path, header.files_offset,
                                     BIFF_FILE_ENTRY_SIZE * header.file_count)
            self._bif_tables[bif_index] = parse_biff_files(table, header.file_count)
        return self._bif_tables[bif_index]

    def _tileset_table(self, bif_index: int) -> dict:
        if bif_index not in self._tileset_tables:
            bif = self.key.bifs[bif_index]
            header = parse_biff_header(self.source.read(bif.path, 0, BIFF_HEADER_SIZE))
            table = self.source.read(bif.path,
                                     header.files_offset + BIFF_FILE_ENTRY_SIZE * header.file_count,
                                     BIFF_TILESET_ENTRY_SIZE * header.tileset_count)
            self._tileset_tables[bif_index] = parse_biff_tilesets(table, header.tileset_count)
        return self._tileset_tables[bif_index]

    def tis(self, resref: str) -> bytes | None:
        """ADR-0149: a TIS as a file (with its 24-byte header): from the override as it is, or
        from the BIF's tileset table, where it is stored without a header."""
        override = f'override/{resref}.tis'
        if self.source.size(override) is not None:
            return _read_whole(self.source, override)
        entry = self.key.find(resref, TIS_TYPE)
        if entry is None or entry.bif_index >= len(self.key.bifs):
            return None
        ts = self._tileset_table(entry.bif_index).get(entry.tileset_index)
        if ts is None or ts.tile_count * ts.tile_size > _MAX_FILE:
            return None
        body = self.source.read(self.key.bifs[entry.bif_index].path, ts.offset,
                                ts.tile_count * ts.tile_size)
        header = b'TIS V1  ' + struct.pack('<IIII', ts.tile_count, ts.tile_size, 0x18, 64)
        return header + body

    def locate(self, resref: str, type_: int, ext: str,
               override: set[str]) -> tuple[str, int, int | None] | None:
        """(path, offset, size) without reading; size None for override files (caller sizes).
        A TIS is never in the file table (ADR-0149: use `tis`)."""
        if resref.upper() in override:
            return f'override/{resref}.{ext}', 0, None
        if type_ == TIS_TYPE:
            return None
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
        if type_ == TIS_TYPE:
            return self.tis(resref)
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


# ADR-0132: ITM item categories, grouped by what a seller would call them.
ITEM_CATEGORIES = {
    'ARMAS': {5, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 44, 57,
              69},
    'ARMADURAS': {2, 7},
    'ESCUDOS': {12, 41},
    'JOIAS': {1, 10, 34},
    'POCOES': {9},
    'PERGAMINHOS': {11},
    'ROUPAS': {3, 4, 6, 32},
    'VARINHAS': {35},
}


def item_category(item_type: int) -> str:
    return next((c for c, types in ITEM_CATEGORIES.items() if item_type in types), 'OUTROS')


@dataclass(frozen=True)
class Offer:
    """ADR-0132: what a person sells, merged from the stores its dialogue opens (local only)."""
    place: str                                   # the store's name ("Coroa de Cobre")
    kinds: tuple[str, ...]                       # STORE, TAVERN, INN, TEMPLE
    rooms: tuple[tuple[str, int], ...] = ()      # (PEASANT|MERCHANT|NOBLE|ROYAL, price)
    drinks: tuple[tuple[str, int], ...] = ()     # (name, price)
    items: tuple[tuple[str, int, str], ...] = ()  # (name, price with the markup, category)
    cures: tuple[tuple[str, int], ...] = ()      # (spell name, price)

    def to_json(self) -> dict:
        return {'place': self.place, 'kinds': list(self.kinds),
                'rooms': [list(r) for r in self.rooms], 'drinks': [list(d) for d in self.drinks],
                'items': [list(i) for i in self.items], 'cures': [list(c) for c in self.cures]}

    @classmethod
    def from_json(cls, doc: dict) -> Offer:
        return cls(str(doc.get('place') or ''), tuple(doc.get('kinds') or ()),
                   tuple((str(t), int(p)) for t, p in doc.get('rooms') or ()),
                   tuple((str(n), int(p)) for n, p in doc.get('drinks') or ()),
                   tuple((str(n), int(p), str(c)) for n, p, c in doc.get('items') or ()),
                   tuple((str(n), int(p)) for n, p in doc.get('cures') or ()))


@dataclass(frozen=True)
class StoreInventory:
    build_fingerprint: str
    language: str
    offers: dict[str, Offer]                     # npc_id -> what it sells
    generated_at: str = ''

    def to_json(self) -> dict:
        return {'schema': STORES_SCHEMA, 'build_fingerprint': self.build_fingerprint,
                'language': self.language, 'generated_at': self.generated_at,
                'source': {'class': 'S0_PRIMARY', 'kind': 'GAME_DATA_LOCAL',
                           'resources': ['chitin.key', '*.CRE', '*.DLG', '*.STO', '*.ITM',
                                         '*.SPL', f'lang/{self.language}/dialog.tlk']},
                'offers': {k: v.to_json() for k, v in sorted(self.offers.items())}}


def _merge_stores(stores: list, item_info: dict, spell_names: dict, strings: dict) -> Offer:
    """Several stores of one person (BERNARD and BERNARD2): their union, at the lowest markup."""
    markup = min(s.sell_markup for s in stores)
    names = [strings.get(s.name) for s in stores if s.name is not None]
    rooms = {}
    for s in stores:
        for tier, price in s.rooms:
            rooms[tier] = min(price, rooms.get(tier, price))
    drinks = {}
    for s in stores:
        for strref, price in s.drinks:
            name = strings.get(strref) if strref is not None else None
            if name:
                drinks[name] = min(price, drinks.get(name, price))
    items = {}
    for s in stores:
        for ref in s.items:
            info = item_info.get(ref)
            name = strings.get(info.name) if info and info.name is not None else None
            if info is None or not name:
                continue
            price = max(1, info.price * markup // 100) if info.price else 0
            items[name] = (min(price, items[name][0]) if name in items else price,
                           item_category(info.item_type))
    cures = {}
    for s in stores:
        for ref, price in s.cures:
            name = spell_names.get(ref)
            if name:
                cures[name] = min(price, cures.get(name, price))
    order = {t: i for i, t in enumerate(('PEASANT', 'MERCHANT', 'NOBLE', 'ROYAL'))}
    return Offer(next((n for n in names if n), ''), tuple(dict.fromkeys(s.kind for s in stores)),
                 tuple(sorted(rooms.items(), key=lambda r: order[r[0]])),
                 tuple(sorted(drinks.items(), key=lambda d: (d[1], d[0]))),
                 tuple(sorted(((n, p, c) for n, (p, c) in items.items()),
                              key=lambda i: (i[2], i[1], i[0]))),
                 tuple(sorted(cures.items(), key=lambda c: (c[1], c[0]))))


def build_stores(source: ByteSource, *, language: str, build_fingerprint: str,
                 residents: dict[str, Resident], now: str | None = None) -> StoreInventory:
    """ADR-0132: for each resident with a CRE file, the stores its dialogue opens, merged."""
    resources = _Resources(source)

    def over(ext: str) -> set[str]:
        return {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', f'.{ext}')}

    def fetch(refs, type_, ext, limit=None) -> dict[str, bytes]:
        overrides = over(ext)
        located = {r: loc for r in sorted(set(refs))
                   if (loc := resources.locate(r, type_, ext, overrides)) is not None}
        return _read_located(source, located, limit=limit)

    cre_of = {npc: r.cre_resref.upper() for npc, r in residents.items() if r.cre_resref}
    dialogs = {}
    for cre, data in fetch(cre_of.values(), CRE_TYPE, 'cre', CRE_IDENTITY_SIZE).items():
        try:
            dialogs[cre] = parse_cre_dialog(data).upper()
        except GameDataError:
            continue
    store_refs = {}
    for dlg, data in fetch({d for d in dialogs.values() if d}, DLG_TYPE, 'dlg').items():
        try:
            store_refs[dlg] = parse_dlg_store_refs(data)
        except GameDataError:
            continue
    stores = {}
    for ref, data in fetch({s for refs in store_refs.values() for s in refs},
                           STO_TYPE, 'sto').items():
        try:
            stores[ref] = parse_sto(data)
        except GameDataError:
            continue
    item_info = {}
    for ref, data in fetch({i for s in stores.values() for i in s.items}, ITM_TYPE, 'itm',
                           0x38).items():
        try:
            item_info[ref] = parse_itm_summary(data)
        except GameDataError:
            continue
    spell_strrefs = {}
    for ref, data in fetch({c for s in stores.values() for c, _ in s.cures}, SPL_TYPE, 'spl',
                           0x0C).items():
        if len(data) >= 0x0C:
            value = int.from_bytes(data[0x08:0x0C], 'little')
            if value not in (0xFFFFFFFF, 0xFFFFFFFE):
                spell_strrefs[ref] = value
    wanted = {s.name for s in stores.values() if s.name is not None}
    wanted |= {d for s in stores.values() for d, _ in s.drinks if d is not None}
    wanted |= {i.name for i in item_info.values() if i.name is not None}
    wanted |= set(spell_strrefs.values())
    strings = resolve_strings(source, f'lang/{language}/dialog.tlk', wanted)
    spell_names = {ref: strings[v] for ref, v in spell_strrefs.items() if v in strings}
    offers = {}
    for npc, cre in sorted(cre_of.items()):
        refs = store_refs.get(dialogs.get(cre, ''), ())
        found = [stores[r] for r in refs if r in stores and stores[r].kind != 'CONTAINER']
        if found:
            offers[npc] = _merge_stores(found, item_info, spell_names, strings)
    stamp = now or datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    return StoreInventory(build_fingerprint, language, offers, stamp)


def _install_dir(base: Path, build_fingerprint: str) -> Path:
    digest = build_fingerprint.split(':', 1)[-1]
    if not digest or not all(c in '0123456789abcdef' for c in digest.lower()):
        digest = hashlib.sha256(build_fingerprint.encode()).hexdigest()
    return base / f'install-{digest[:16].lower()}'


def write_inventory(inventory: AreaInventory | ResidentInventory | StoreInventory,
                    base_dir: Path = DEFAULT_LOCAL_DIR, *, repo_root: Path = REPO_ROOT) -> Path:
    kind = ('residents' if isinstance(inventory, ResidentInventory)
            else 'stores' if isinstance(inventory, StoreInventory) else 'areas')
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


def load_local_offers(build_fingerprint: str, language: str,
                      base_dir: Path = DEFAULT_LOCAL_DIR) -> dict[str, Offer]:
    """ADR-0132: what each person sells, from a written store inventory of this build, or {}."""
    path = _install_dir(Path(base_dir), build_fingerprint) / f'stores.{language}.json'
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding='utf-8'))
    if doc.get('schema') != STORES_SCHEMA or doc.get('build_fingerprint') != build_fingerprint:
        return {}
    out = {}
    for npc, offer in (doc.get('offers') or {}).items():
        try:
            out[npc] = Offer.from_json(offer)
        except (TypeError, ValueError):
            continue
    return out
