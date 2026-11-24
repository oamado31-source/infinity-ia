# SPDX-License-Identifier: Apache-2.0
"""ADR-0146: an area of ours, copied from a room of the build (lab only).

A BG2:EE area is a set of files named after it: the ARE (what is in it), the WED (its drawing,
which points to a TIS by name), the MOS (the minimap) and three BMP (search, light and height
maps). An area of ours (`IA` and four digits) copies those of a room of the build under our name;
the WED keeps pointing to the original TIS, which is not copied. In the ARE of ours, nothing of
the game acts: no creatures, no spawn points, no area script, no containers (no loot copied) and
no passage of the game (its travel regions are dropped; our way in and out is the gateway's
TRAVEL). The bytes are game data (CR-2026-030): they go only to the lab's override.
"""
from __future__ import annotations

import re
import struct

from .gateway import ActionError

AREA_NAME = re.compile(r'IA\d{4}')
ARE_SIGNATURE = b'AREAV1.0'
WED_REF = 0x08                    # ARE V1.0: the area's WED resref
ACTORS_COUNT = 0x58               # word
REGIONS_COUNT = 0x5A              # word
SPAWNS_COUNT = 0x64               # dword
CONTAINERS_COUNT = 0x74           # word
ITEMS_COUNT = 0x76                # word
SCRIPT_REF = 0x94                 # the area script resref
COPIED_SUFFIXES = (('', 'ARE'), ('', 'WED'), ('', 'MOS'), ('SR', 'BMP'), ('LM', 'BMP'),
                   ('HT', 'BMP'))


def our_area_name(name: str) -> str:
    name = (name or '').upper()
    if not AREA_NAME.fullmatch(name):
        raise ActionError('NOT_OUR_AREA')
    return name


def make_area(source: bytes, name: str) -> bytes:
    """The ARE of ours: the room as it is drawn, with nothing of the game acting in it."""
    name = our_area_name(name)
    if source[:8] != ARE_SIGNATURE or len(source) < SCRIPT_REF + 8:
        raise ActionError('BAD_SOURCE_ARE')
    d = bytearray(source)
    d[WED_REF:WED_REF + 8] = name.encode('ascii').ljust(8, b'\0')
    struct.pack_into('<H', d, ACTORS_COUNT, 0)
    struct.pack_into('<H', d, REGIONS_COUNT, 0)
    struct.pack_into('<I', d, SPAWNS_COUNT, 0)
    struct.pack_into('<H', d, CONTAINERS_COUNT, 0)
    struct.pack_into('<H', d, ITEMS_COUNT, 0)
    d[SCRIPT_REF:SCRIPT_REF + 8] = b'\0' * 8
    return bytes(d)


def copied_files(source_area: str, name: str) -> tuple[tuple[str, str, str], ...]:
    """(source resref, our resref, type) of every file the copy needs; the TIS is not copied."""
    name = our_area_name(name)
    return tuple((source_area.upper() + suffix, name + suffix, kind)
                 for suffix, kind in COPIED_SUFFIXES)
