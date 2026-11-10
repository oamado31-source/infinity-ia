# SPDX-License-Identifier: Apache-2.0
"""Parsers for Infinity Engine (Enhanced Edition) file formats used by the area inventory.

KEY V1, BIFF V1, TLK V1, WMP V1.0, ARE V1.0 actors and CRE V1.0 identity, following the
community documentation (IESDP). Pure functions over bytes, strict bounds checks, no writes. Only
uncompressed BIFF V1 is supported (the format used by the EE games); anything else raises
GameDataError.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

from .source import GameDataError

CRE_TYPE = 0x3F1
AREA_TYPE = 0x3F2
WMP_TYPE = 0x3F7
NO_STRREF = 0xFFFFFFFF
_MAX_ENTRIES = 1_000_000


def _resref(raw: bytes) -> str:
    return raw.split(b'\0', 1)[0].decode('latin-1').strip().upper()


def _need(data: bytes, offset: int, length: int, what: str) -> None:
    if offset < 0 or length < 0 or offset + length > len(data):
        raise GameDataError(f'{what} out of bounds ({offset}+{length} > {len(data)})')


# ---- KEY V1 ----------------------------------------------------------------------------------

@dataclass(frozen=True)
class BifEntry:
    index: int
    path: str
    length: int


@dataclass(frozen=True)
class KeyResource:
    resref: str
    type: int
    bif_index: int
    file_index: int


@dataclass(frozen=True)
class KeyFile:
    bifs: tuple[BifEntry, ...]
    resources: tuple[KeyResource, ...]

    def find(self, resref: str, type_: int) -> KeyResource | None:
        resref = resref.upper()
        return next((r for r in self.resources if r.type == type_ and r.resref == resref), None)

    def of_type(self, type_: int) -> list[KeyResource]:
        return [r for r in self.resources if r.type == type_]


def parse_key(data: bytes) -> KeyFile:
    _need(data, 0, 24, 'KEY header')
    if data[:8] != b'KEY V1  ':
        raise GameDataError('not a KEY V1 file')
    n_bif, n_res, off_bif, off_res = struct.unpack_from('<4I', data, 8)
    if n_bif > 10_000 or n_res > _MAX_ENTRIES:
        raise GameDataError('implausible KEY counts')
    _need(data, off_bif, 12 * n_bif, 'KEY bif table')
    _need(data, off_res, 14 * n_res, 'KEY resource table')
    bifs = []
    for i in range(n_bif):
        length, name_off, name_len, _location = struct.unpack_from('<IIHH', data, off_bif + 12 * i)
        _need(data, name_off, name_len, 'KEY bif name')
        name = data[name_off:name_off + name_len].split(b'\0', 1)[0].decode('latin-1')
        bifs.append(BifEntry(i, name.replace('\\', '/').lstrip(':/'), length))
    resources = []
    for i in range(n_res):
        raw, type_, locator = struct.unpack_from('<8sHI', data, off_res + 14 * i)
        resources.append(KeyResource(_resref(raw), type_, locator >> 20, locator & 0x3FFF))
    return KeyFile(tuple(bifs), tuple(resources))


# ---- BIFF V1 ---------------------------------------------------------------------------------

BIFF_HEADER_SIZE = 20
BIFF_FILE_ENTRY_SIZE = 16


@dataclass(frozen=True)
class BiffHeader:
    file_count: int
    tileset_count: int
    files_offset: int


@dataclass(frozen=True)
class BiffFile:
    file_index: int
    offset: int
    size: int
    type: int


def parse_biff_header(data: bytes) -> BiffHeader:
    _need(data, 0, BIFF_HEADER_SIZE, 'BIFF header')
    if data[:8] != b'BIFFV1  ':
        raise GameDataError('not an uncompressed BIFF V1 file')
    n_files, n_tiles, off_files = struct.unpack_from('<3I', data, 8)
    if n_files > _MAX_ENTRIES:
        raise GameDataError('implausible BIFF file count')
    return BiffHeader(n_files, n_tiles, off_files)


def parse_biff_files(data: bytes, count: int) -> dict[int, BiffFile]:
    _need(data, 0, BIFF_FILE_ENTRY_SIZE * count, 'BIFF file table')
    files = {}
    for i in range(count):
        locator, offset, size, type_, _unknown = struct.unpack_from('<IIIHH', data,
                                                                     BIFF_FILE_ENTRY_SIZE * i)
        files[locator & 0x3FFF] = BiffFile(locator & 0x3FFF, offset, size, type_)
    return files


# ---- TLK V1 ----------------------------------------------------------------------------------

TLK_HEADER_SIZE = 18
TLK_ENTRY_SIZE = 26


@dataclass(frozen=True)
class TlkHeader:
    language_id: int
    count: int
    strings_offset: int


def parse_tlk_header(data: bytes) -> TlkHeader:
    _need(data, 0, TLK_HEADER_SIZE, 'TLK header')
    if data[:8] != b'TLK V1  ':
        raise GameDataError('not a TLK V1 file')
    lang, count, off = struct.unpack_from('<HII', data, 8)
    if count > 10 * _MAX_ENTRIES:
        raise GameDataError('implausible TLK count')
    return TlkHeader(lang, count, off)


def tlk_entry_offset(strref: int) -> int:
    return TLK_HEADER_SIZE + TLK_ENTRY_SIZE * strref


def parse_tlk_entry(data: bytes) -> tuple[int, int]:
    """(offset relative to the string data, length) of one 26-byte entry."""
    _need(data, 0, TLK_ENTRY_SIZE, 'TLK entry')
    _flags, _sound, _volume, _pitch, offset, length = struct.unpack('<H8sIIII', data)
    return offset, length


def decode_tlk_string(raw: bytes) -> str:
    return raw.decode('utf-8', errors='replace').replace('\r\n', '\n').strip()


# ---- WMP V1.0 --------------------------------------------------------------------------------

WMP_MAP_SIZE = 0xB8
WMP_AREA_SIZE = 0xF0


@dataclass(frozen=True)
class WorldMapArea:
    resref: str
    caption_strref: int | None
    tooltip_strref: int | None
    flags: int


@dataclass(frozen=True)
class WorldMap:
    number: int
    name_strref: int | None
    areas: tuple[WorldMapArea, ...]


def _strref(value: int) -> int | None:
    return None if value in (NO_STRREF, 0xFFFFFFFE) else value


def parse_wmp(data: bytes) -> tuple[WorldMap, ...]:
    _need(data, 0, 16, 'WMP header')
    if data[:8] != b'WMAPV1.0':
        raise GameDataError('not a WMP V1.0 file')
    n_maps, off_maps = struct.unpack_from('<2I', data, 8)
    if n_maps > 64:
        raise GameDataError('implausible WMP map count')
    _need(data, off_maps, WMP_MAP_SIZE * n_maps, 'WMP map table')
    maps = []
    for m in range(n_maps):
        base = off_maps + WMP_MAP_SIZE * m
        number, name_strref = struct.unpack_from('<2I', data, base + 0x10)
        n_areas, off_areas = struct.unpack_from('<2I', data, base + 0x20)
        if n_areas > 10_000:
            raise GameDataError('implausible WMP area count')
        _need(data, off_areas, WMP_AREA_SIZE * n_areas, 'WMP area table')
        areas = []
        for a in range(n_areas):
            ab = off_areas + WMP_AREA_SIZE * a
            resref = _resref(data[ab:ab + 8])
            flags, = struct.unpack_from('<I', data, ab + 0x30)
            caption, tooltip = struct.unpack_from('<2I', data, ab + 0x40)
            areas.append(WorldMapArea(resref, _strref(caption), _strref(tooltip), flags))
        maps.append(WorldMap(number, _strref(name_strref), tuple(areas)))
    return tuple(maps)


# ---- ARE V1.0 (actors) and CRE V1.0 (identity) -------------------------------------------------

ARE_ACTOR_SIZE = 0x110
CRE_IDENTITY_SIZE = 0x2D4
ACTOR_CRE_ATTACHED = 0x1


@dataclass(frozen=True)
class AreaActor:
    actor_name: str
    cre_resref: str
    flags: int
    embedded: bytes | None = None   # CRE stored inside the ARE (flag bit 0), if any


@dataclass(frozen=True)
class CreatureIdentity:
    name_strref: int | None
    script_name: str      # death variable; '' when unset
    allegiance: int       # EA byte (2 = PC ... 255 = enemy)
    general: int = 1      # GENERAL.IDS (1 = humanoid, 2 = animal, 255 = monster)
    race: int = 0         # RACE.IDS
    klass: int = 0        # CLASS.IDS
    gender: int = 0       # GENDER.IDS (1 = male, 2 = female)
    alignment: int = 0    # ALIGNMEN.IDS (0x11 LG ... 0x33 CE)
    wisdom: int = 0       # ability score (0 = not read)
    intelligence: int = 0  # ability score (0 = not read)


def parse_are_actors(data: bytes) -> tuple[AreaActor, ...]:
    _need(data, 0, 0x5C, 'ARE header')
    if data[:8] != b'AREAV1.0':
        raise GameDataError('not an ARE V1.0 file')
    offset, = struct.unpack_from('<I', data, 0x54)
    count, = struct.unpack_from('<H', data, 0x58)
    _need(data, offset, ARE_ACTOR_SIZE * count, 'ARE actor table')
    actors = []
    for i in range(count):
        base = offset + ARE_ACTOR_SIZE * i
        name = data[base:base + 32].split(b'\0', 1)[0].decode('latin-1').strip()
        flags, = struct.unpack_from('<I', data, base + 0x28)
        cre = _resref(data[base + 0x80:base + 0x88])
        embedded = None
        if flags & ACTOR_CRE_ATTACHED:
            cre_off, cre_size = struct.unpack_from('<2I', data, base + 0x88)
            if cre_size >= CRE_IDENTITY_SIZE and cre_off + cre_size <= len(data):
                embedded = data[cre_off:cre_off + cre_size]
        actors.append(AreaActor(name, cre, flags, embedded))
    return tuple(actors)


def parse_cre_identity(data: bytes) -> CreatureIdentity:
    _need(data, 0, CRE_IDENTITY_SIZE, 'CRE header')
    if data[:8] != b'CRE V1.0':
        raise GameDataError('not a CRE V1.0 file')
    name, = struct.unpack_from('<I', data, 0x08)
    script = data[0x280:0x2A0].split(b'\0', 1)[0].decode('latin-1').strip()
    if script.lower() == 'none':
        script = ''
    return CreatureIdentity(_strref(name), script, data[0x270], data[0x271], data[0x272],
                            data[0x273], data[0x275], data[0x27B], data[0x23B], data[0x23A])
