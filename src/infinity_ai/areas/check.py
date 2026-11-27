# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the checker of an area of ours (REQ-MAP-007, 009, 010).

It reads back the files the recipe made, as the engine would, and refuses with a named error:
`AREA_NAME`, `PAGE_NAME`, `WED_OVERLAYS`, `MAP_SIZE`, `TILE_COUNT`, `ENTRANCE_BLOCKED`,
`NO_PATH`, `MISSING_REF`, `WALL_OUTSIDE`. Warnings: `NO_WALLS`, `BIG_AREA`, `WALL_BASELINE`
(a wall whose first two points, its baseline, are not its foot). `existing` holds the
build's resource names (all types), when the caller can read them, so nothing of ours collides.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from . import AreaError
from .are import read_are_summary
from .maps import CELL_H, CELL_W, IMPASSABLE, map_size, read_bmp
from .recipe import MAX_TILES, Recipe
from .tis import page_name, read_tis
from .wed import OVERLAYS, read_wed


@dataclass
class AreaReport:
    errors: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[tuple[str, str]] = field(default_factory=list)

    def error(self, code: str, detail: str) -> None:
        self.errors.append((code, detail))

    def warn(self, code: str, detail: str) -> None:
        self.warnings.append((code, detail))

    @property
    def ok(self) -> bool:
        return not self.errors


def _cell(x: int, y: int) -> tuple[int, int]:
    return x // CELL_W, y // CELL_H


def check_area(recipe: Recipe, files: dict[str, bytes],
               existing: set[str] | frozenset[str] | None = None) -> AreaReport:
    r = AreaReport()
    name = recipe.area
    existing = {n.upper() for n in (existing or ())}
    pages = sorted(n[:-5] for n in files if n.endswith('.PVRZ'))
    if name in existing:
        r.error('AREA_NAME', f'{name} já existe na build')
    for p in pages:
        if p in existing:
            r.error('PAGE_NAME', f'a página {p} já existe na build')
    try:
        are = read_are_summary(files[f'{name}.ARE'])
        wed = read_wed(files[f'{name}.WED'])
        tiles = read_tis(files[f'{name}.TIS'])
    except (KeyError, AreaError) as exc:
        r.error('MISSING_REF', f'arquivo ausente ou ilegível: {exc}')
        return r
    if len(wed.overlays) != OVERLAYS:
        r.error('WED_OVERLAYS', f'{len(wed.overlays)} camadas, precisa de {OVERLAYS}')
    if are['wed'] != name:
        r.error('MISSING_REF', f'o ARE aponta para o WED {are["wed"]}')
    if not wed.overlays or wed.overlays[0][2] != name:
        r.error('MISSING_REF', 'o WED não aponta para o TIS da área')
    if are['script'] and are['script'] not in existing:
        r.error('MISSING_REF', f'script {are["script"]}')
    for t, (page, _x, _y) in enumerate(tiles):
        if page_name(name, page) not in pages:
            r.error('MISSING_REF', f'o tile {t} aponta para a página {page}, que não existe')
            break
    if len(tiles) != recipe.width * recipe.height:
        r.error('TILE_COUNT', f'{len(tiles)} tiles, precisa de {recipe.width * recipe.height}')
    mw, mh = map_size(recipe.width_px, recipe.height_px)
    codes: list[int] = []
    for suffix in ('SR', 'HT', 'LM'):
        try:
            w, h, _bpp, px = read_bmp(files[f'{name}{suffix}.BMP'])
        except (KeyError, AreaError) as exc:
            r.error('MISSING_REF', f'{suffix}: {exc}')
            continue
        if (w, h) != (mw, mh):
            r.error('MAP_SIZE', f'{suffix} tem {w}x{h}, precisa de {mw}x{mh}')
        if suffix == 'SR':
            codes = px
    for wall in wed.walls:
        if len(wall.points) < 3 or any(not (0 <= x < recipe.width_px and 0 <= y < recipe.height_px)
                                       for x, y in wall.points):
            r.error('WALL_OUTSIDE', f'parede com {len(wall.points)} pontos ou fora da área')
    for k, wall in enumerate(wed.walls):
        if len(wall.points) >= 3 and not _baseline_at_foot(wall.points):
            r.warn('WALL_BASELINE', f'parede {k}: os dois primeiros pontos (a linha de base) '
                                    'não estão no pé da parede; quem estiver atrás não some')
    if not wed.walls:
        r.warn('NO_WALLS', 'a área não tem paredes: ninguém some atrás de nada')
    if recipe.width > MAX_TILES or recipe.height > MAX_TILES:
        r.warn('BIG_AREA', f'{recipe.width}x{recipe.height} tiles')
    if len(codes) == mw * mh:
        _walkable(r, recipe, codes, mw, mh)
    return r


def _baseline_at_foot(points) -> bool:
    """The baseline (the first two points) is the foot when no other point of the wall lies
    below it on the picture (a turned part's front corner is left out of the outline)."""
    (ax, ay), (bx, by) = points[0], points[1]
    if ax == bx:
        return False
    for px, py in points[2:]:
        if py > ay + (by - ay) * (px - ax) / (bx - ax) + 2:
            return False
    return True


def _walkable(r: AreaReport, recipe: Recipe, codes: list[int], mw: int, mh: int) -> None:
    def passable(c: tuple[int, int]) -> bool:
        i, j = c
        return 0 <= i < mw and 0 <= j < mh and codes[j * mw + i] not in IMPASSABLE

    points = [('entrada', p) for p in recipe.entrances] + [('passagem', p)
                                                            for p in recipe.passages]
    blocked = False
    for kind, p in points:
        if not passable(_cell(p.x, p.y)):
            r.error('ENTRANCE_BLOCKED', f'{kind} {p.point_id} ({p.x}, {p.y}) cai onde não se anda')
            blocked = True
    if blocked or len(points) < 2:
        return
    start = _cell(points[0][1].x, points[0][1].y)
    seen, queue = {start}, deque([start])
    while queue:
        i, j = queue.popleft()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                n = (i + di, j + dj)
                if n not in seen and passable(n):
                    seen.add(n)
                    queue.append(n)
    for kind, p in points[1:]:
        if _cell(p.x, p.y) not in seen:
            r.error('NO_PATH', f'não há caminho até {kind} {p.point_id}')
