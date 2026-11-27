# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the area recipe (`infinity-ai.area-recipe.v1`), read strictly.

A recipe says how to produce an area of ours without any game byte: its name and kind, its size
in tiles, the floor, the regions (what is drawn and what can be walked), the walls, the entrances,
the points the quests use, the light and who made it. The picture is `procedural` (drawn by code)
in this version; `render` (Blender) is reserved for phase 3 of SPEC-014.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import AreaError
from .maps import TERRAIN
from .tis import TILE

SCHEMA = 'infinity-ai.area-recipe.v1'
AREA_NAME = re.compile(r'IA\d{4}')
_ID = re.compile(r'[a-z0-9][a-z0-9-]{0,47}')
KINDS = ('interior', 'underground', 'exterior')
DRAWS = ('planks', 'stone-floor', 'wall-face', 'wall-top', 'pillar')
MAX_TILES = 128
_KEYS = {'schema', 'area', 'title', 'version', 'kind', 'size', 'floor', 'picture', 'regions',
         'walls', 'entrances', 'passages', 'light', 'provenance'}


@dataclass(frozen=True)
class Shape:
    """A rectangle (x, y, w, h) or a polygon, in area pixels.

    As a wall, the first two points are its baseline (the foot of the wall): the engine draws the
    wall over a creature that stands above that line (lab, 2026-11-27: a rectangle that began
    with its top edge hid no one). A rectangle starts at its bottom edge, as the game's walls."""
    rect: tuple[int, int, int, int] | None
    polygon: tuple[tuple[int, int], ...] | None

    def points(self) -> tuple[tuple[int, int], ...]:
        if self.polygon:
            return self.polygon
        x, y, w, h = self.rect
        return ((x, y + h - 1), (x + w - 1, y + h - 1), (x + w - 1, y), (x, y))

    def contains(self, px: float, py: float) -> bool:
        if self.rect:
            x, y, w, h = self.rect
            return x <= px < x + w and y <= py < y + h
        inside, pts = False, self.polygon
        for i, (x1, y1) in enumerate(pts):
            x2, y2 = pts[i - 1]
            if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
                inside = not inside
        return inside


@dataclass(frozen=True)
class Region:
    region_id: str
    shape: Shape
    terrain: str | None
    draw: str | None


@dataclass(frozen=True)
class Point:
    point_id: str
    x: int
    y: int
    facing: int = 0


@dataclass(frozen=True)
class Recipe:
    area: str
    title: str
    version: int
    kind: str
    width: int                       # tiles
    height: int
    floor_terrain: str
    floor_draw: str
    seed: int
    regions: tuple[Region, ...]
    walls: tuple[tuple[str, Shape], ...]
    entrances: tuple[Point, ...]
    passages: tuple[Point, ...]
    light: tuple[int, int, int]
    provenance: dict

    @property
    def width_px(self) -> int:
        return self.width * TILE

    @property
    def height_px(self) -> int:
        return self.height * TILE


def _int(v: object, lo: int, hi: int) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _shape(raw: dict, where: str, w: int, h: int) -> Shape:
    if ('rect' in raw) == ('polygon' in raw):
        raise AreaError('RECIPE', f'{where}: rect ou polygon, um dos dois')
    if 'rect' in raw:
        r = raw['rect']
        if not (isinstance(r, list) and len(r) == 4 and all(_int(v, 0, 32767) for v in r)
                and r[2] > 0 and r[3] > 0):
            raise AreaError('RECIPE', f'{where}: rect = [x, y, largura, altura]')
        if r[0] + r[2] > w or r[1] + r[3] > h:
            raise AreaError('WALL_OUTSIDE', f'{where}: fora da área')
        return Shape(tuple(r), None)
    p = raw['polygon']
    if not (isinstance(p, list) and len(p) >= 3 and all(
            isinstance(q, list) and len(q) == 2 and _int(q[0], 0, w - 1) and _int(q[1], 0, h - 1)
            for q in p)):
        raise AreaError('WALL_OUTSIDE', f'{where}: polígono com 3 pontos ou mais, dentro da área')
    return Shape(None, tuple((q[0], q[1]) for q in p))


def _points(raw: object, where: str, key: str, w: int, h: int) -> tuple[Point, ...]:
    if not isinstance(raw, list):
        raise AreaError('RECIPE', f'{where}: precisa ser uma lista')
    out = []
    for i, p in enumerate(raw):
        if not (isinstance(p, dict) and set(p) <= {key, 'x', 'y', 'facing'}
                and isinstance(p.get(key), str) and _int(p.get('x'), 0, w - 1)
                and _int(p.get('y'), 0, h - 1) and _int(p.get('facing', 0), 0, 15)):
            raise AreaError('RECIPE', f'{where}[{i}]: {key}, x, y (dentro da área), facing 0-15')
        out.append(Point(p[key], p['x'], p['y'], p.get('facing', 0)))
    if len({p.point_id for p in out}) != len(out):
        raise AreaError('RECIPE', f'{where}: nomes repetidos')
    return tuple(out)


def parse_recipe(doc: object) -> Recipe:
    if not isinstance(doc, dict) or doc.get('schema') != SCHEMA:
        raise AreaError('RECIPE', f'schema precisa ser {SCHEMA}')
    if not set(doc) <= _KEYS:
        raise AreaError('RECIPE', f'campos desconhecidos: {sorted(set(doc) - _KEYS)}')
    area = doc.get('area')
    if not isinstance(area, str) or not AREA_NAME.fullmatch(area):
        raise AreaError('AREA_NAME', f'{area!r}: IA e quatro dígitos')
    title, version, kind = doc.get('title'), doc.get('version'), doc.get('kind')
    if not isinstance(title, str) or not 0 < len(title) <= 80 or not _int(version, 1, 9999) \
            or kind not in KINDS:
        raise AreaError('RECIPE', 'title (até 80), version (1+), kind (interior, underground, '
                                  'exterior)')
    size = doc.get('size')
    if not (isinstance(size, dict) and set(size) == {'width', 'height'}
            and _int(size['width'], 1, 255) and _int(size['height'], 1, 255)):
        raise AreaError('AREA_SIZE', 'size = {width, height} em tiles')
    tw, th = size['width'], size['height']
    w, h = tw * TILE, th * TILE
    floor = doc.get('floor')
    if not (isinstance(floor, dict) and set(floor) == {'terrain', 'draw'}
            and floor['terrain'] in TERRAIN and floor['draw'] in DRAWS):
        raise AreaError('RECIPE', f'floor = {{terrain: {sorted(TERRAIN)}, draw: {DRAWS}}}')
    picture = doc.get('picture')
    if not (isinstance(picture, dict) and picture.get('kind') == 'procedural'
            and set(picture) <= {'kind', 'seed'} and _int(picture.get('seed', 0), 0, 2 ** 31)):
        raise AreaError('RECIPE', 'picture = {kind: procedural, seed} (render na fase 3)')
    regions = []
    for i, r in enumerate(doc.get('regions', [])):
        where = f'regions[{i}]'
        if not (isinstance(r, dict) and set(r) <= {'id', 'rect', 'polygon', 'terrain', 'draw'}
                and isinstance(r.get('id'), str) and _ID.fullmatch(r['id'])
                and r.get('terrain', 'wood') in TERRAIN and r.get('draw', 'planks') in DRAWS
                and ('terrain' in r or 'draw' in r)):
            raise AreaError('RECIPE', f'{where}: id, rect ou polygon, terrain e/ou draw')
        regions.append(Region(r['id'], _shape(r, where, w, h), r.get('terrain'), r.get('draw')))
    walls = []
    for i, r in enumerate(doc.get('walls', [])):
        where = f'walls[{i}]'
        if not (isinstance(r, dict) and set(r) <= {'id', 'rect', 'polygon'}
                and isinstance(r.get('id'), str) and _ID.fullmatch(r['id'])):
            raise AreaError('RECIPE', f'{where}: id e rect ou polygon')
        walls.append((r['id'], _shape(r, where, w, h)))
    entrances = _points(doc.get('entrances'), 'entrances', 'name', w, h)
    if not entrances:
        raise AreaError('NO_ENTRANCE', 'a área precisa de uma entrada')
    passages = _points(doc.get('passages', []), 'passages', 'id', w, h)
    light = doc.get('light')
    if not (isinstance(light, dict) and set(light) == {'rgb'} and isinstance(light['rgb'], list)
            and len(light['rgb']) == 3 and all(_int(v, 0, 255) for v in light['rgb'])):
        raise AreaError('RECIPE', 'light = {rgb: [r, g, b]}')
    prov = doc.get('provenance')
    if not (isinstance(prov, dict) and isinstance(prov.get('author'), str) and prov['author']):
        raise AreaError('RECIPE', 'provenance.author')
    return Recipe(area, title, version, kind, tw, th, floor['terrain'], floor['draw'],
                  picture.get('seed', 0), tuple(regions), tuple(walls), entrances, passages,
                  tuple(light['rgb']), dict(prov))
