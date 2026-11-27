# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the content of a new area as an ARE V1.0, written from scratch.

Only what an empty room needs: the WED name, the area type, the entrances, the song entry and an
empty rest-interruption entry. No creatures, regions, containers, spawn points, ambients, doors
or script. Measured in the game's rooms (2026-11-27): an interior has type 0, the five songs are
0 and the five alternative ones -1, both ambient volumes 100, the explored bitmask is empty.
The copies of ADR-0146 keep using `actions.areas.make_area`.
"""
from __future__ import annotations

import re
import struct
from dataclasses import dataclass

from . import AreaError

HEADER, ENTRANCE, SONGS, REST = 0x11C, 0x68, 0x90, 0xE4
AREA_TYPES = {'interior': 0x00, 'underground': 0x20, 'exterior': 0x01}
AREA_NAME = re.compile(r'IA\d{4}')


@dataclass(frozen=True)
class Entrance:
    name: str
    x: int
    y: int
    facing: int = 0


def explored_size(width_px: int, height_px: int) -> int:
    """Bytes of the explored bitmask: one bit per 32x32 pixels on a (w/32 + 1) x (h/32 + 1)
    grid (measured in a save, 2026-11-27: AR0300, AR0406, AR0069, AR0311, IA0090...)."""
    return -(-((width_px // 32 + 1) * (height_px // 32 + 1)) // 8)


def build_are(name: str, kind: str, entrances: list[Entrance], *,
              explored: tuple[int, int] | None = None) -> bytes:
    """`explored`: (width, height) in pixels to hand the area over already explored (the whole
    picture shown from the first visit, as the sea around the ship, ADR-0151)."""
    name = name.upper()
    if not AREA_NAME.fullmatch(name):
        raise AreaError('AREA_NAME', name)
    if kind not in AREA_TYPES:
        raise AreaError('AREA_KIND', kind)
    if not entrances:
        raise AreaError('NO_ENTRANCE', name)
    o_entr = HEADER
    o_after = o_entr + ENTRANCE * len(entrances)
    n_explored = explored_size(*explored) if explored else 0
    o_explored = o_after
    o_after = o_explored + n_explored
    o_songs = o_after
    o_rest = o_songs + SONGS
    end = o_rest + REST
    h = bytearray(HEADER)
    h[0:8] = b'AREAV1.0'
    h[0x08:0x10] = name.encode('ascii').ljust(8, b'\0')
    struct.pack_into('<H', h, 0x48, AREA_TYPES[kind])
    struct.pack_into('<IHHII', h, 0x54, o_entr, 0, 0, o_entr, o_entr)    # actors, regions, spawns
    struct.pack_into('<IIII', h, 0x64, 0, o_entr, len(entrances), o_after)
    struct.pack_into('<HHIIHHII', h, 0x74, 0, 0, o_after, o_after, 0, 0, o_after, o_after)
    struct.pack_into('<I', h, 0x8C, 0)                                     # variables
    struct.pack_into('<II', h, 0x9C, n_explored, o_explored if n_explored else o_songs)
    struct.pack_into('<IIIIII', h, 0xA4, 0, o_after, 0, o_after, 0, o_after)
    struct.pack_into('<IIIIII', h, 0xBC, o_songs, o_rest, end, 0, end, 0)
    body = bytearray()
    for e in entrances:
        if not 0 <= e.x <= 32767 or not 0 <= e.y <= 32767 or not 0 <= e.facing <= 15:
            raise AreaError('ENTRANCE_POINT', e.name)
        raw = e.name.encode('ascii', 'replace')[:31]
        body += raw.ljust(32, b'\0') + struct.pack('<HHH', e.x, e.y, e.facing) + bytes(66)
    songs = bytearray(SONGS)
    struct.pack_into('<5I5I', songs, 0, 0, 0, 0, 0, 0, *([0xFFFFFFFF] * 5))
    struct.pack_into('<I', songs, 0x38, 100)
    struct.pack_into('<I', songs, 0x4C, 100)
    return bytes(h) + bytes(body) + b'\xff' * n_explored + bytes(songs) + bytes(REST)


def read_are_summary(data: bytes) -> dict:
    """What the checker needs from an ARE: names, type, entrances and the counts of what acts."""
    if data[:8] != b'AREAV1.0' or len(data) < HEADER:
        raise AreaError('BAD_ARE', 'no header')
    w = lambda o: struct.unpack_from('<H', data, o)[0]     # noqa: E731
    d = lambda o: struct.unpack_from('<I', data, o)[0]     # noqa: E731
    o_entr, n_entr = d(0x68), d(0x6C)
    entrances = []
    for i in range(n_entr):
        b = data[o_entr + ENTRANCE * i: o_entr + ENTRANCE * (i + 1)]
        x, y, f = struct.unpack_from('<HHH', b, 32)
        entrances.append(Entrance(b[:32].split(b'\0')[0].decode('latin-1'), x, y, f))
    return {
        'wed': data[0x08:0x10].split(b'\0')[0].decode('latin-1').upper(),
        'type': w(0x48),
        'script': data[0x94:0x9C].split(b'\0')[0].decode('latin-1').upper(),
        'actors': w(0x58), 'regions': w(0x5A), 'spawns': d(0x64), 'containers': w(0x74),
        'items': w(0x76), 'ambients': w(0x82), 'doors': d(0xA4), 'animations': d(0xAC),
        'entrances': tuple(entrances),
    }
