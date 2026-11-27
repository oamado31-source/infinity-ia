# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the plan of an area as a WED V1.3.

Measured in the game's rooms (2026-11-27): five overlays are always declared; only the first has
a size (the area, one tile per cell), the empty ones point at the end of the tile data. Walls are
polygons (flags 1 = the picture is drawn over a creature behind it; height -1), grouped by the
engine's 640x480 cells (`wall groups`, ceil(width/640) x ceil(height/480)). A group holds every
polygon whose bounding box meets its cell: in the lab's round trip this is the game's groups or
more (a polygon that only touches a cell's edge), never fewer. No doors here: they
come with the hatch of the ship's hold (ADR-0149, D4).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

from . import AreaError

TILE = 64
OVERLAYS = 5
HEADER, OVERLAY, SECONDARY, TILEMAP, POLYGON = 0x20, 0x18, 0x14, 0x0A, 0x12
GROUP_W, GROUP_H = 640, 480
WALL_FLAGS = 0x01


@dataclass(frozen=True)
class Wall:
    points: tuple[tuple[int, int], ...]
    flags: int = WALL_FLAGS
    height: int = -1

    def bbox(self) -> tuple[int, int, int, int]:
        if not self.points:
            return 0, 0, 0, 0
        xs, ys = [p[0] for p in self.points], [p[1] for p in self.points]
        return min(xs), max(xs), min(ys), max(ys)


@dataclass(frozen=True)
class WedInfo:
    overlays: tuple[tuple[int, int, str], ...]       # (width, height, TIS) of each overlay
    lookup: tuple[int, ...]                          # the base overlay's tile of each cell
    walls: tuple[Wall, ...]
    groups: tuple[tuple[int, ...], ...]              # polygon indices of each wall group
    doors: int


def group_grid(w_tiles: int, h_tiles: int) -> tuple[int, int]:
    return (-(-w_tiles * TILE // GROUP_W), -(-h_tiles * TILE // GROUP_H))


def _groups(walls: list[Wall], w_tiles: int, h_tiles: int) -> list[list[int]]:
    gx, gy = group_grid(w_tiles, h_tiles)
    out = []
    for j in range(gy):
        for i in range(gx):
            x0, y0 = i * GROUP_W, j * GROUP_H
            out.append([k for k, w in enumerate(walls) if w.points
                        and w.bbox()[0] < x0 + GROUP_W and w.bbox()[1] >= x0
                        and w.bbox()[2] < y0 + GROUP_H and w.bbox()[3] >= y0])
    return out


def build_wed(tis_name: str, w_tiles: int, h_tiles: int, walls: list[Wall], *,
              strict: bool = True) -> bytes:
    """`strict=False` only for the lab's round trip of a game room, which may hold polygons
    of fewer than three points (AR1607 does)."""
    if not 0 < w_tiles <= 255 or not 0 < h_tiles <= 255:
        raise AreaError('AREA_SIZE', f'{w_tiles}x{h_tiles} tiles')
    for w in walls:
        if strict and len(w.points) < 3:
            raise AreaError('WALL_OUTSIDE', 'a wall needs three points')
    cells = w_tiles * h_tiles
    o_overlays = HEADER
    o_secondary = o_overlays + OVERLAY * OVERLAYS
    o_doors = o_secondary + SECONDARY
    o_tilemap = o_doors                                     # no doors
    o_lookup = o_tilemap + TILEMAP * cells
    o_door_cells = o_lookup + 2 * cells
    groups = _groups(walls, w_tiles, h_tiles)
    o_groups = o_door_cells
    o_polygons = o_groups + 4 * len(groups)
    o_poly_lookup = o_polygons + POLYGON * len(walls)
    n_lookup = sum(len(g) for g in groups)
    o_vertices = o_poly_lookup + 2 * n_lookup
    out = bytearray(b'WED V1.3')
    out += struct.pack('<IIIIII', OVERLAYS, 0, o_overlays, o_secondary, o_doors, o_door_cells)
    out += struct.pack('<HH8sHHII', w_tiles, h_tiles, tis_name.upper().encode('ascii'), 0, 0,
                       o_tilemap, o_lookup)
    for _ in range(OVERLAYS - 1):
        out += struct.pack('<HH8sHHII', 0, 0, b'', 0, 0, o_lookup, o_door_cells)
    out += struct.pack('<IIIII', len(walls), o_polygons, o_vertices, o_groups, o_poly_lookup)
    for c in range(cells):
        out += struct.pack('<HHhB3x', c, 1, -1, 0)
    out += struct.pack(f'<{cells}H', *range(cells))
    start = 0
    for g in groups:
        out += struct.pack('<HH', start, len(g))
        start += len(g)
    vertex = 0
    for w in walls:
        x0, x1, y0, y1 = w.bbox()
        out += struct.pack('<IIBbHHHH', vertex, len(w.points), w.flags, w.height, x0, x1, y0, y1)
        vertex += len(w.points)
    for g in groups:
        out += struct.pack(f'<{len(g)}H', *g)
    for w in walls:
        for x, y in w.points:
            out += struct.pack('<HH', x, y)
    return bytes(out)


def read_wed(data: bytes) -> WedInfo:
    if data[:8] != b'WED V1.3' or len(data) < HEADER:
        raise AreaError('BAD_WED', 'no header')
    n_over, n_doors, o_over, o_sec, _o_doors, _o_cells = struct.unpack_from('<IIIIII', data, 8)
    overlays = []
    lookup: tuple[int, ...] = ()
    for i in range(n_over):
        w, h, tis, _u, _m, o_map, o_look = struct.unpack_from('<HH8sHHII', data,
                                                              o_over + OVERLAY * i)
        overlays.append((w, h, tis.split(b'\0')[0].decode('latin-1').upper()))
        if i == 0:
            cells = []
            for c in range(w * h):
                start, _count, _sec, _mask = struct.unpack_from('<HHhB', data, o_map + TILEMAP * c)
                cells.append(struct.unpack_from('<H', data, o_look + 2 * start)[0])
            lookup = tuple(cells)
    n_poly, o_poly, o_vert, o_groups, o_plook = struct.unpack_from('<IIIII', data, o_sec)
    walls = []
    for k in range(n_poly):
        sv, nv, fl, ht = struct.unpack_from('<IIBb', data, o_poly + POLYGON * k)
        pts = tuple(struct.unpack_from('<HH', data, o_vert + 4 * (sv + j)) for j in range(nv))
        walls.append(Wall(pts, fl, ht))
    groups = []
    if overlays:
        gx, gy = group_grid(overlays[0][0], overlays[0][1])
        for g in range(gx * gy):
            start, n = struct.unpack_from('<HH', data, o_groups + 4 * g)
            groups.append(tuple(struct.unpack_from(f'<{n}H', data, o_plook + 2 * start)))
    return WedInfo(tuple(overlays), lookup, tuple(walls), tuple(groups), n_doors)
