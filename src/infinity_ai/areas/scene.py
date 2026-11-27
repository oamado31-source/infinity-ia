# SPDX-License-Identifier: Apache-2.0
"""ADR-0150: a scene of ours (`infinity-ai.area-scene.v1`) and what the area takes from it.

The scene is what the Blender script renders: the picture size, the game's camera, the parts of
the room (in metres), the lights and the named points. Besides the picture, the area takes from
the scene, by the camera's math (`camera.py`), the search map (each part's foot, with its
terrain), the walls (each part that hides what stands behind it) and the entrances and passage
points (the markers). The part kinds and sizes here follow the Blender script's.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

from . import AreaError
from .camera import Box, Camera, footprint, occluder, project_points
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
    'column': ('obstacle', True), 'hammock': ('open-obstacle', True),
    'table': ('open-obstacle', True), 'bench': ('open-obstacle', False),
    'chest': ('open-obstacle', False), 'floor-hatch': ('open-obstacle', False),
    'table-setting': (None, False),       # sits on a table: the table blocks and hides
    'partition': ('wall', True), 'rug': (None, False), 'bed': ('obstacle', True),
    'chair': ('open-obstacle', False), 'wardrobe': ('obstacle', True), 'window': (None, False),
    # ADR-0151, the upper deck: the ship's outline, the sea, a raised deck and its stairs are
    # drawn as polygons (see _areas); the rest stand on the deck or on the raised deck
    'ship-deck': (None, False), 'water': (None, False), 'raised-deck': (None, False),
    'stairs': (None, False), 'door': (None, False), 'rigging': (None, False),
    'wheel': ('open-obstacle', False), 'capstan': ('obstacle', True),
    'rope-coil': ('open-obstacle', False), 'lantern-post': ('obstacle', True),
    'grating-hatch': ('open-obstacle', False), 'rope-ladder': (None, False),
    'rowboat': (None, False), 'boarding-net': (None, False),
}
# the order the search map is painted in: floors, the ship, what stands on the deck, the raised
# deck (its body, then its top), the stairs, what stands up there, the raised deck's rails
ORDER_FLOOR, ORDER_HULL, ORDER_DECK, ORDER_PART = 0, 1, 2, 3
ORDER_RAISED, ORDER_RAISED_TOP, ORDER_STAIRS, ORDER_ON_RAISED, ORDER_RAISED_RAIL = 4, 5, 6, 7, 8


@dataclass(frozen=True)
class ScenePart:
    kind: str
    part_id: str
    boxes: tuple[Box, ...]
    terrain: str | None
    occludes: bool
    areas: tuple = ()          # (order, terrain, ((x, y, z), ...)): polygons of the search map


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
        if p.get('axis', 'x') == 'y':
            return (Box(p['x'], p['y'] + lean / 2, w + 0.1, abs(lean) + 0.2, p['h']),)
        return (Box(p['x'] + lean / 2, p['y'], abs(lean) + 0.2, w + 0.1, p['h']),)
    if kind == 'hammock':
        return (Box(p['x'], p['y'], p.get('length', 2.0) + 0.1, p.get('w', 0.8), 1.4,
                    p.get('turn', 0.0)),)
    if kind == 'table':
        return (Box(p['x'], p['y'], p.get('w', 3.0), p.get('d', 0.9), p.get('h', 0.75), turn),)
    if kind == 'bench':
        return (Box(p['x'], p['y'], p.get('w', 2.8), p.get('d', 0.3), p.get('h', 0.45), turn),)
    if kind == 'chest':
        return (Box(p['x'], p['y'], p.get('w', 0.8), p.get('d', 0.5), p.get('h', 0.55), turn),)
    if kind == 'partition':
        t, L = 0.15, p['length']
        cuts = sorted(tuple(g) for g in p.get('gaps', []))
        spans, start = [], 0.0
        for a, b in cuts:
            spans.append((start, a))
            start = b
        spans.append((start, L))
        out = []
        for a, b in spans:
            if b - a < 0.01:
                continue
            m = (a + b) / 2
            if p['axis'] == 'x':
                out.append(Box(p['x'] + m, p['y'], b - a, t, p.get('h', 2.4)))
            else:
                out.append(Box(p['x'], p['y'] + m, t, b - a, p.get('h', 2.4)))
        return tuple(out)
    if kind == 'bed':
        return (Box(p['x'], p['y'], p.get('length', 2.0) + 0.1, p.get('w', 1.0) + 0.05, 1.4,
                    turn),)
    if kind == 'chair':
        return (Box(p['x'], p['y'], 0.45, 0.45, 1.05, turn),)
    if kind == 'wardrobe':
        return (Box(p['x'], p['y'], p.get('w', 1.0), p.get('d', 0.5), p.get('h', 1.9), turn),)
    if kind == 'capstan':
        return (Box(p['x'], p['y'], 0.9, 0.9, 0.92),)
    if kind == 'wheel':
        return (Box(p['x'], p['y'], 0.5, 1.2, 1.6),)
    if kind == 'rope-coil':
        r = p.get('r', 0.35)
        return (Box(p['x'], p['y'], 2 * r, 2 * r, 0.25),)
    if kind == 'lantern-post':
        return (Box(p['x'], p['y'], 0.2, 0.2, p.get('h', 2.4)),)
    if kind == 'grating-hatch':
        return (Box(p['x'], p['y'], p.get('w', 1.6) + 0.24, p.get('d', 1.4) + 0.24, 0.3),)
    if kind == 'floor-hatch':
        return (Box(p['x'], p['y'], p.get('w', 1.1) + 0.24, p.get('d', 1.1) + 0.24, 0.16, turn),)
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


def _shrink(pts, d):
    """A convex outline moved `d` metres inwards (towards its centre, along each point's way)."""
    cx = sum(x for x, _y in pts) / len(pts)
    cy = sum(y for _x, y in pts) / len(pts)
    out = []
    for x, y in pts:
        vx, vy = x - cx, y - cy
        n = (vx * vx + vy * vy) ** 0.5 or 1.0
        out.append((x - vx / n * d, y - vy / n * d))
    return out


def _areas(kind: str, p: dict) -> tuple:
    """The search-map polygons of the parts drawn as outlines (in room metres, with height)."""
    if kind == 'ship-deck':
        outline = [tuple(q) for q in p['outline']]
        inner = _shrink(outline, p.get('rail', 0.25))
        return ((ORDER_HULL, 'wall', tuple((x, y, 0.0) for x, y in outline)),
                (ORDER_DECK, 'wood', tuple((x, y, 0.0) for x, y in inner)))
    if kind == 'raised-deck':
        x0, x1, y0, y1, h = p['x0'], p['x1'], p['y0'], p['y1'], p['h']
        ground = [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0)]
        top = [(x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)]
        r = p.get('rail', 0.2)
        inner = [(x0 + r, y0 + r, h), (x1 - r, y0 + r, h), (x1 - r, y1 - r, h),
                 (x0 + r, y1 - r, h)]
        rails = []                                   # the rails on its top, but the stairs' gap
        g0, g1 = p.get('gap', (0.0, 0.0))
        for a, b in ((y0, g0), (g1, y1)) if g1 > g0 else ((y0, y1),):
            if b - a > 0.05:
                rails.append((ORDER_RAISED_RAIL, 'wall', ((x0, a, h), (x0 + r, a, h),
                                                          (x0 + r, b, h), (x0, b, h))))
        rails.append((ORDER_RAISED_RAIL, 'wall', ((x0, y0, h), (x1, y0, h), (x1, y0 + r, h),
                                                  (x0, y0 + r, h))))
        rails.append((ORDER_RAISED_RAIL, 'wall', ((x0, y1 - r, h), (x1, y1 - r, h), (x1, y1, h),
                                                  (x0, y1, h))))
        # its body (the front faces between the ground and the top) blocks, the top is walked
        return ((ORDER_RAISED, 'wall', tuple(ground)), (ORDER_RAISED, 'wall', tuple(top)),
                (ORDER_RAISED, 'wall', ((x0, y0, 0.0), (x0, y0, h), (x0, y1, h), (x0, y1, 0.0))),
                (ORDER_RAISED, 'wall', ((x0, y0, 0.0), (x1, y0, 0.0), (x1, y0, h), (x0, y0, h))),
                (ORDER_RAISED_TOP, 'wood', tuple(inner))) + tuple(rails)
    if kind == 'rowboat':
        L, B, f = p.get('length', 6.0), p.get('beam', 2.0), p.get('floor', -2.15)
        local = [(-L / 2, -B / 2 * 0.85), (L * 0.18, -B / 2), (L / 2, 0.0), (L * 0.18, B / 2),
                 (-L / 2, B / 2 * 0.85)]
        a = math.radians(p.get('turn', 0.0))
        pts = [(p['x'] + u * math.cos(a) - v * math.sin(a), p['y'] + u * math.sin(a)
                + v * math.cos(a)) for u, v in local]
        inner = _shrink(pts, 0.25)
        return ((ORDER_HULL, 'wall', tuple((x, y, f) for x, y in pts)),
                (ORDER_DECK, 'wood', tuple((x, y, f) for x, y in inner)))
    if kind == 'rope-ladder' and 'from_z' in p:
        # climbing it, and only it: from its foot in the boat (`reach` metres out, under the
        # ladder) up over the rail onto the deck, as wide as the ladder (`half` each side)
        x, y, z0 = p['x'], p['y'], p['from_z']
        # the way up may be wider than the ladder (a boarding net hangs beside it: `climb_half`)
        out, onto = p.get('reach', 0.6), p.get('onto', 0.6)
        half = p.get('climb_half', p.get('half', 0.3))
        return ((ORDER_STAIRS, 'wood', ((x - half, y - out, z0), (x + half, y - out, z0),
                                        (x + half, y + onto, 0.0), (x - half, y + onto, 0.0))),)
    if kind == 'stairs':
        x0, x1, y, w, h = p['x0'], p['x1'], p['y'], p.get('w', 1.0), p['h']
        return ((ORDER_STAIRS, 'wood', ((x0, y - w / 2, 0.0), (x1 + 0.3, y - w / 2, h),
                                        (x1 + 0.3, y + w / 2, h), (x0, y + w / 2, 0.0))),)
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
    # ADR-0151: on an open deck nothing blocks the sight; what blocks the way stays blocked
    open_sight = doc.get('open_sight') is True

    def sight(terrain):
        return 'open-obstacle' if open_sight and terrain in ('obstacle', 'wall') else terrain
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
        terrain = sight(terrain)
        if p.get('walk') is True:                    # e.g. a low part you may step over
            terrain = None
        floor = p.get('floor', 0.0)                  # standing on a raised deck
        if floor:
            boxes = tuple(Box(b.x, b.y, b.w, b.d, b.h, b.turn, max(b.z, floor), floor)
                          for b in boxes)
        try:
            areas = tuple((o, sight(t), pts) for o, t, pts in _areas(kind, p))
        except (KeyError, TypeError) as exc:
            raise AreaError('SCENE', f'parts[{i}] ({kind}): falta {exc}') from None
        parts.append(ScenePart(kind, p.get('id', f'{kind}-{i}'), boxes, terrain, occludes,
                               areas))
    markers = []
    for i, m in enumerate(doc.get('markers', [])):
        if not (isinstance(m, dict) and isinstance(m.get('id'), str) and _ID.fullmatch(m['id'])
                and _num(m.get('x')) and _num(m.get('y'))
                and isinstance(m.get('facing', 0), int) and 0 <= m.get('facing', 0) <= 15):
            raise AreaError('SCENE', f'markers[{i}]: id, x, y (metros), facing 0-15')
        u, v = camera.project(m['x'], m['y'], m.get('z', 0.0))
        markers.append(Point(m['id'], round(u), round(v), m.get('facing', 0)))
    if not markers:
        raise AreaError('NO_ENTRANCE', 'a cena precisa de um marcador para a entrada')
    return Scene(area, w, h, camera, tuple(parts), tuple(markers))


def _clip(poly: list[tuple[int, int]], w: int, h: int) -> tuple[tuple[int, int], ...]:
    return tuple((min(max(x, 0), w - 1), min(max(y, 0), h - 1)) for x, y in poly)


def scene_regions(scene: Scene) -> tuple[Region, ...]:
    """The search map's regions, in painting order: the floors, the ship's outline and deck,
    every part's foot, a raised deck's body and top, its stairs, what stands up there. Anything
    left is the recipe's floor terrain (the void, or the sea)."""
    out: list[tuple[int, int, Region]] = []
    n = 0
    for part in scene.parts:
        for k, (order, terrain, pts) in enumerate(part.areas):
            poly = _clip(project_points(scene.camera, pts), scene.width, scene.height)
            out.append((order, n, Region(f'{part.part_id}-a{k}', Shape(None, poly), terrain, None)))
            n += 1
        if part.terrain is None:
            continue
        for k, box in enumerate(part.boxes):
            if box.z > box.floor:
                continue                            # a part on a part: its foot is the one below
            poly = _clip(footprint(scene.camera, box), scene.width, scene.height)
            if part.terrain == 'wood':
                order = ORDER_FLOOR
            else:
                order = ORDER_ON_RAISED if box.floor else ORDER_PART
            out.append((order, n, Region(f'{part.part_id}-{k}', Shape(None, poly), part.terrain,
                                         None)))
            n += 1
    return tuple(r for _o, _n, r in sorted(out, key=lambda t: (t[0], t[1])))


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
