# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: a picture drawn by code, for tests and the test room.

Deterministic (a small linear congruential generator seeded by the recipe), so the same recipe
always gives the same picture and the same files. Styles: wooden planks, stone floor, the face of
a stone wall, the dark top of a wall, and a stone pillar seen from the game's angle (a light top
and a shaded front, with a soft shadow on the floor).
"""
from __future__ import annotations

from .recipe import Recipe, Shape


class _Rand:
    def __init__(self, seed: int) -> None:
        self.state = (seed * 2654435761 + 12345) & 0xFFFFFFFF

    def next(self, n: int) -> int:
        self.state = (self.state * 1103515245 + 12345) & 0x7FFFFFFF
        return (self.state >> 8) % n


def _clamp(v: float) -> int:
    return 0 if v < 0 else 255 if v > 255 else int(v)


class Canvas:
    def __init__(self, width: int, height: int) -> None:
        self.width, self.height = width, height
        self.rgb = bytearray(width * height * 3)

    def put(self, x: int, y: int, c: tuple[float, float, float]) -> None:
        o = (y * self.width + x) * 3
        self.rgb[o], self.rgb[o + 1], self.rgb[o + 2] = _clamp(c[0]), _clamp(c[1]), _clamp(c[2])

    def get(self, x: int, y: int) -> tuple[int, int, int]:
        o = (y * self.width + x) * 3
        return self.rgb[o], self.rgb[o + 1], self.rgb[o + 2]


def _bbox(shape: Shape, width: int, height: int) -> tuple[int, int, int, int]:
    xs = [p[0] for p in shape.points()]
    ys = [p[1] for p in shape.points()]
    return max(0, min(xs)), min(width - 1, max(xs)), max(0, min(ys)), min(height - 1, max(ys))


def _cells(shape: Shape, cv: Canvas):
    x0, x1, y0, y1 = _bbox(shape, cv.width, cv.height)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if shape.rect or shape.contains(x + 0.5, y + 0.5):
                yield x, y, x0, x1, y0, y1


def _planks(cv: Canvas, shape: Shape, rnd: _Rand) -> None:
    rows: dict[int, tuple[int, list[int]]] = {}
    for x, y, *_ in _cells(shape, cv):
        r = y // 24
        if r not in rows:
            tone = rnd.next(36) - 18
            ends, pos = [], -rnd.next(160)
            while pos < cv.width:
                pos += 96 + rnd.next(160)
                ends.append(pos)
            rows[r] = (tone, ends)
        tone, ends = rows[r]
        grain = ((x * 7 + y * 13) % 11) - 5
        c = 118 + tone + grain, 80 + tone * 0.7 + grain * 0.6, 46 + tone * 0.4
        if y % 24 in (0, 23) or any(abs(x - e) < 1 for e in ends):
            c = c[0] * 0.55, c[1] * 0.55, c[2] * 0.55
        cv.put(x, y, c)


def _stone_floor(cv: Canvas, shape: Shape, rnd: _Rand) -> None:
    tones: dict[tuple[int, int], int] = {}
    for x, y, *_ in _cells(shape, cv):
        key = (x // 48 + (y // 36) % 2, y // 36)
        if key not in tones:
            tones[key] = rnd.next(30) - 15
        t = tones[key] + ((x * 5 + y * 3) % 7) - 3
        c = 104 + t, 100 + t, 94 + t
        if y % 36 == 0 or (x + 24 * ((y // 36) % 2)) % 48 == 0:
            c = 62, 58, 54
        cv.put(x, y, c)


def _wall_face(cv: Canvas, shape: Shape, rnd: _Rand) -> None:
    for x, y, x0, x1, y0, y1 in _cells(shape, cv):
        depth = (y - y0) / max(1, y1 - y0)
        t = ((x // 40 + (y // 20) % 2) * 37 + (y // 20) * 11) % 17 - 8
        c = (92 + t) * (1.05 - 0.35 * depth), (88 + t) * (1.05 - 0.35 * depth), \
            (84 + t) * (1.05 - 0.35 * depth)
        if y % 20 == 0 or (x + 20 * ((y // 20) % 2)) % 40 == 0:
            c = c[0] * 0.6, c[1] * 0.6, c[2] * 0.6
        cv.put(x, y, c)


def _wall_top(cv: Canvas, shape: Shape, rnd: _Rand) -> None:
    for x, y, *_ in _cells(shape, cv):
        t = (x * 3 + y * 5) % 5
        cv.put(x, y, (38 + t, 34 + t, 32 + t))


def _pillar(cv: Canvas, shape: Shape, rnd: _Rand) -> None:
    x0, x1, y0, y1 = _bbox(shape, cv.width, cv.height)
    top = y0 + max(8, (x1 - x0) * 3 // 8)
    # a soft shadow on the floor, to the lower right of the pillar's foot
    for y in range(y1 + 1, min(cv.height, y1 + 28)):
        for x in range(x0 + 10, min(cv.width, x1 + 26)):
            f = 0.62 + 0.38 * ((y - y1) / 28)
            r, g, b = cv.get(x, y)
            cv.put(x, y, (r * f, g * f, b * f))
    for x, y, *_ in _cells(shape, cv):
        across = (x - x0) / max(1, x1 - x0)
        if y < top:
            c = 158 - 20 * across, 152 - 20 * across, 144 - 20 * across
        else:
            light = 1.15 - 0.6 * across - 0.15 * (y - top) / max(1, y1 - top)
            c = 112 * light, 108 * light, 102 * light
            if (y - top) % 30 == 0:
                c = c[0] * 0.7, c[1] * 0.7, c[2] * 0.7
        cv.put(x, y, c)


STYLES = {'planks': _planks, 'stone-floor': _stone_floor, 'wall-face': _wall_face,
          'wall-top': _wall_top, 'pillar': _pillar}


def draw(recipe: Recipe) -> bytes:
    """The recipe's picture (RGB, row by row), width_px x height_px."""
    cv = Canvas(recipe.width_px, recipe.height_px)
    rnd = _Rand(recipe.seed)
    whole = Shape((0, 0, recipe.width_px, recipe.height_px), None)
    STYLES[recipe.floor_draw](cv, whole, rnd)
    for region in recipe.regions:
        if region.draw:
            STYLES[region.draw](cv, region.shape, rnd)
    return bytes(cv.rgb)
