# SPDX-License-Identifier: Apache-2.0
"""ADR-0150: a scene of ours (`infinity-ai.area-scene.v1`) and what the area takes from it.

The scene is what the Blender script renders: the picture size, the game's camera, the parts of
the room (in metres), the lights and the named points. Besides the picture, the area takes from
the scene, by the camera's math (`camera.py`), the search map (each part's foot, with its
terrain), the walls (each part that hides what stands behind it) and the entrances and passage
points (the markers). The part kinds and sizes here follow the Blender script's.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import AreaError
from .camera import Box, Camera, footprint, occluder
from .recipe import Point, Region, Shape

SCHEMA = 'infinity-ai.area-scene.v1'
_ID = re.compile(r'[a-z0-9][a-z0-9-]{0,47}')
# kind -> (terrain of its foot, hides what is behind it)
KINDS = {
    'plank-floor': ('wood', False), 'hull-wall': ('wall', False), 'crate': ('obstacle', True),
    'bale': ('obstacle', True), 'barrel': ('open-obstacle', True), 'post': ('obstacle', True),
    'mast': ('obstacle', True), 'ladder': ('open-obstacle', False),
    'cage': ('open-obstacle', True), 'lantern': (None, False), 'net-rack': ('open-obstacle', True),
    'sack': ('open-obstacle', False), 'checker-floor': ('wood', False), 'box': ('obstacle', True),
    'column': ('obstacle', True),
}


@dataclass(frozen=True)
class ScenePart:
    kind: str
    part_id: str
    boxes: tuple[Box, ...]
    terrain: str | None
    occludes: bool


@dataclass(frozen=True)
class Scene:
    area: str
    width: int
    height: int
    camera: Camera
    parts: tuple[ScenePart, ...]
    markers: tuple[Point, ...]


def _num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _boxes(kind: str, p: dict) -> tuple[Box, ...]:
    """The part as boxes, with the sizes the Blender script builds."""
    turn, z = p.get('turn', 0.0), p.get('z', 0.0)
    if kind in ('plank-floor', 'checker-floor'):
        w, d = (p['w'], p['d']) if kind == 'plank-floor' else (p.get('cells', 10),) * 2
        return (Box(p['x'] + w / 2, p['y'] + d / 2, w, d, 0.0),)
    if kind == 'hull-wall':
        t, length = 0.3, p['length']
        if p['axis'] == 'x':
            return (Box(p['x'] + length / 2, p['y'], length, t, p['h']),)
        return (Box(p['x'], p['y'] + length / 2, t, length, p['h']),)
    if kind in ('crate', 'box'):
        s = p.get('s', 1.0)
        return (Box(p['x'], p['y'], p.get('w', s), p.get('d', s), p.get('h', s), turn, z),)
    if kind == 'bale':
        return (Box(p['x'], p['y'], p.get('w', 0.9), p.get('d', 0.7), p.get('h', 0.6), turn, z),)
    if kind == 'barrel':
        r, h = p.get('r', 0.30) * 1.12, p.get('h', 0.9)
        if p.get('lying'):
            return (Box(p['x'], p['y'], 2 * r, h, 2 * r, turn, z),)
        return (Box(p['x'], p['y'], 2 * r, 2 * r, h, turn, z),)
    if kind == 'post':
        s = p.get('s', 0.3)
        return (Box(p['x'], p['y'], s, s, p['h']),)
    if kind in ('mast', 'column'):
        r = p.get('r', 0.3 if kind == 'mast' else 0.25)
        return (Box(p['x'], p['y'], 2 * r, 2 * r, p['h']),)
    if kind == 'ladder':
        lean, w = p.get('lean', 0.35), p.get('w', 0.6)
        return (Box(p['x'] + lean / 2, p['y'], lean + 0.2, w + 0.1, p['h']),)
    if kind == 'net-rack':
        return (Box(p['x'], p['y'], p.get('length', 1.6) + 0.1, 0.3, p.get('h', 1.9), turn),)
    if kind == 'cage':
        x0, y0, x1, y1, h = p['x0'], p['y0'], p['x1'], p['y1'], p.get('h', 2.2)
        out = []
        if 'x' in p.get('sides', 'xy'):
            out.append(Box((x0 + x1) / 2, y0, x1 - x0, 0.2, h))
        if 'y' in p.get('sides', 'xy'):
            out.append(Box(x1, (y0 + y1) / 2, 0.2, y1 - y0, h))
        return tuple(out)
    if kind == 'sack':
        return (Box(p['x'], p['y'], 0.7, 0.56, 0.42),)
    return ()


def parse_scene(doc: object) -> Scene:
    if not isinstance(doc, dict) or doc.get('schema') != SCHEMA:
        raise AreaError('SCENE', f'schema precisa ser {SCHEMA}')
    area, w, h, cam = doc.get('area'), doc.get('width'), doc.get('height'), doc.get('camera')
    if not (isinstance(area, str) and re.fullmatch(r'IA\d{4}', area)):
        raise AreaError('AREA_NAME', f'{area!r}')
    if not (isinstance(w, int) and isinstance(h, int) and w % 64 == 0 and h % 64 == 0
            and 0 < w <= 16320 and 0 < h <= 16320):
        raise AreaError('AREA_SIZE', 'width e height em pixels, múltiplos de 64')
    if not (isinstance(cam, dict) and all(_num(cam.get(k)) for k in
                                          ('elevation', 'px_per_m', 'turn', 'u0', 'v0'))):
        raise AreaError('SCENE', 'camera = {elevation, px_per_m, turn, u0, v0}')
    camera = Camera(float(cam['elevation']), float(cam['px_per_m']), float(cam['turn']),
                    float(cam['u0']), float(cam['v0']))
    parts = []
    for i, p in enumerate(doc.get('parts', [])):
        kind = p.get('kind') if isinstance(p, dict) else None
        if kind not in KINDS:
            raise AreaError('SCENE', f'parts[{i}]: peça desconhecida {kind!r}')
        try:
            boxes = _boxes(kind, p)
        except (KeyError, TypeError) as exc:
            raise AreaError('SCENE', f'parts[{i}] ({kind}): falta {exc}') from None
        terrain, occludes = KINDS[kind]
        if p.get('walk') is True:                    # e.g. a low part you may step over
            terrain = None
        parts.append(ScenePart(kind, p.get('id', f'{kind}-{i}'), boxes, terrain, occludes))
    markers = []
    for i, m in enumerate(doc.get('markers', [])):
        if not (isinstance(m, dict) and isinstance(m.get('id'), str) and _ID.fullmatch(m['id'])
                and _num(m.get('x')) and _num(m.get('y'))
                and isinstance(m.get('facing', 0), int) and 0 <= m.get('facing', 0) <= 15):
            raise AreaError('SCENE', f'markers[{i}]: id, x, y (metros), facing 0-15')
        u, v = camera.project(m['x'], m['y'])
        markers.append(Point(m['id'], round(u), round(v), m.get('facing', 0)))
    if not markers:
        raise AreaError('NO_ENTRANCE', 'a cena precisa de um marcador para a entrada')
    return Scene(area, w, h, camera, tuple(parts), tuple(markers))


def _clip(poly: list[tuple[int, int]], w: int, h: int) -> tuple[tuple[int, int], ...]:
    return tuple((min(max(x, 0), w - 1), min(max(y, 0), h - 1)) for x, y in poly)


def scene_regions(scene: Scene) -> tuple[Region, ...]:
    """The search map's regions, in drawing order: the floor first, then every part's foot.
    Anything outside the floor stays the recipe's floor terrain (the void: obstacle)."""
    out = []
    for part in scene.parts:
        if part.terrain is None:
            continue
        for k, box in enumerate(part.boxes):
            if box.z > 0:
                continue                            # a part on a part: its foot is the one below
            poly = _clip(footprint(scene.camera, box), scene.width, scene.height)
            out.append(Region(f'{part.part_id}-{k}', Shape(None, poly), part.terrain, None))
    floors = [r for r in out if r.terrain == 'wood']
    return tuple(floors + [r for r in out if r.terrain != 'wood'])


def scene_walls(scene: Scene) -> tuple[tuple[str, Shape], ...]:
    out = []
    for part in scene.parts:
        if not part.occludes:
            continue
        for k, box in enumerate(part.boxes):
            poly = _clip(occluder(scene.camera, box), scene.width, scene.height)
            if len(set(poly)) >= 3:
                out.append((f'{part.part_id}-{k}', Shape(None, poly)))
    return tuple(out)
