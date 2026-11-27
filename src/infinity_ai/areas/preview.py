# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: draw an area (ours or the game's) from its files, for a local preview.

`render_area` takes a function that fetches a resource by name and type and returns the picture,
optionally with the search map (impassable cells tinted red) and the walls (outlined in yellow)
drawn over it. The picture of a game area is game data: previews stay in ~/.infinity-ai/previews,
never in the repository (CR-2026-030).
"""
from __future__ import annotations

from typing import Callable

from . import AreaError
from .maps import CELL_H, CELL_W, IMPASSABLE, read_bmp
from .tis import TILE, read_pvrz, read_tis, render_tis
from .wed import read_wed

Fetch = Callable[[str, str], 'bytes | None']        # (resref, extension) -> bytes


def render_area(area: str, fetch: Fetch, *, search: bool = False, walls: bool = False
                ) -> tuple[int, int, bytes]:
    from .are import read_are_summary
    are = fetch(area, 'are')
    if are is None:
        raise AreaError('MISSING_REF', f'{area}.ARE')
    wed_name = read_are_summary(are)['wed']
    wed_data = fetch(wed_name, 'wed')
    if wed_data is None:
        raise AreaError('MISSING_REF', f'{wed_name}.WED')
    wed = read_wed(wed_data)
    w_tiles, h_tiles, tis_name = wed.overlays[0]
    tis_data = fetch(tis_name, 'tis')
    if tis_data is None:
        raise AreaError('MISSING_REF', f'{tis_name}.TIS')
    entries = read_tis(tis_data)
    pages = {}
    for page in sorted({e[0] for e in entries if e[0] != 0xFFFFFFFF}):
        data = fetch(f'{tis_name[0]}{tis_name[-4:]}{page:02d}', 'pvrz')
        if data is not None:
            pages[page] = read_pvrz(data)
    rgb = bytearray(render_tis(entries, pages, w_tiles, h_tiles, list(wed.lookup)))
    width, height = w_tiles * TILE, h_tiles * TILE
    if search:
        sr = fetch(f'{wed_name}SR', 'bmp')
        if sr is not None:
            mw, mh, _bpp, codes = read_bmp(sr)
            for y in range(height):
                j = min(mh - 1, y // CELL_H)
                for x in range(width):
                    if codes[j * mw + min(mw - 1, x // CELL_W)] in IMPASSABLE:
                        o = (y * width + x) * 3
                        rgb[o] = min(255, rgb[o] // 2 + 128)
                        rgb[o + 1] //= 2
                        rgb[o + 2] //= 2
    if walls:
        for wall in wed.walls:
            pts = list(wall.points)
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                steps = max(abs(x2 - x1), abs(y2 - y1), 1)
                for s in range(steps + 1):
                    x, y = x1 + (x2 - x1) * s // steps, y1 + (y2 - y1) * s // steps
                    if 0 <= x < width and 0 <= y < height:
                        o = (y * width + x) * 3
                        rgb[o:o + 3] = b'\xff\xe0\x20'
    return width, height, bytes(rgb)
