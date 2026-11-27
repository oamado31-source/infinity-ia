# SPDX-License-Identifier: Apache-2.0
"""ADR-0150: the game's camera, as plain math, shared by the Blender script and the checker.

An orthographic camera looking north, `elevation` degrees above the horizon, `px_per_m` pixels
per metre. A world point (x east, y north, z up, metres) lands on the picture at

    u = u0 + x * s
    v = v0 - y * s * sin(e) - z * s * cos(e)

so the ground is drawn at sin(e) of its depth and heights at cos(e). The room is turned around the
vertical axis by `turn` degrees (the game's rooms are turned about 45 degrees). Everything the area
needs besides the picture comes from here: the footprint of each part in the search map, the
outline of each part that hides what stands behind it (a wall, whose first two points are its
baseline: the two side corners of its foot, ADR-0149) and the named points of the scene.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

Point2 = tuple[float, float]


@dataclass(frozen=True)
class Camera:
    elevation: float          # degrees above the horizon
    px_per_m: float
    turn: float = 0.0         # the room's turn around the vertical axis, degrees
    u0: float = 0.0           # where the world origin lands on the picture
    v0: float = 0.0

    def _rot(self, x: float, y: float) -> Point2:
        a = math.radians(self.turn)
        return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)

    def project(self, x: float, y: float, z: float = 0.0) -> Point2:
        rx, ry = self._rot(x, y)
        e = math.radians(self.elevation)
        s = self.px_per_m
        return self.u0 + rx * s, self.v0 - ry * s * math.sin(e) - z * s * math.cos(e)

    def ground(self, u: float, v: float) -> Point2:
        """The ground point (z = 0) under a picture point."""
        e = math.radians(self.elevation)
        s = self.px_per_m
        rx, ry = (u - self.u0) / s, (self.v0 - v) / (s * math.sin(e))
        a = math.radians(-self.turn)
        return rx * math.cos(a) - ry * math.sin(a), rx * math.sin(a) + ry * math.cos(a)


@dataclass(frozen=True)
class Box:
    """A part as a box: centre on the ground, size (width, depth, height), its own turn; `z` is
    where it starts above the ground (a crate on a crate)."""
    x: float
    y: float
    w: float
    d: float
    h: float
    turn: float = 0.0
    z: float = 0.0
    floor: float = 0.0        # the height of the floor it stands on (a raised deck)

    def foot(self) -> list[Point2]:
        """The four ground corners, in the room's frame."""
        a = math.radians(self.turn)
        c, s = math.cos(a), math.sin(a)
        out = []
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            px, py = dx * self.w / 2, dy * self.d / 2
            out.append((self.x + px * c - py * s, self.y + px * s + py * c))
        return out


def _hull(points: list[Point2]) -> list[Point2]:
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o: Point2, a: Point2, b: Point2) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[Point2] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[Point2] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def footprint(cam: Camera, box: Box) -> list[tuple[int, int]]:
    """The part's foot on the picture (a polygon), for the search map, at its floor's height."""
    return [tuple(round(c) for c in cam.project(x, y, box.floor)) for x, y in box.foot()]


def project_points(cam: Camera, points) -> list[tuple[int, int]]:
    """Room points (x, y, z) on the picture."""
    return [tuple(round(c) for c in cam.project(x, y, z)) for x, y, z in points]


def occluder(cam: Camera, box: Box) -> list[tuple[int, int]]:
    """The picture outline of a part, as a wall polygon: the first two points are its baseline,
    the left and the right corners of its foot on the ground; then the outline over the top, back
    to the left. A creature above that line is behind the part (ADR-0149). A part that stands on
    another (z > 0) is drawn from the ground up, so the stack hides as one."""
    feet = [cam.project(x, y, box.floor) for x, y in box.foot()]
    tops = [cam.project(x, y, box.z + box.h) for x, y in box.foot()]
    left = min(feet, key=lambda p: (p[0], -p[1]))
    right = max(feet, key=lambda p: (p[0], p[1]))
    hull = _hull(feet + tops)
    # walk the hull from `right` to `left` over the side that does not hold the front corner
    # (screen y grows downwards, so the upper side has the smaller v)
    i_r = min(range(len(hull)), key=lambda k: (hull[k][0] - right[0]) ** 2
              + (hull[k][1] - right[1]) ** 2)
    i_l = min(range(len(hull)), key=lambda k: (hull[k][0] - left[0]) ** 2
              + (hull[k][1] - left[1]) ** 2)
    n = len(hull)
    path_a = [hull[(i_r + k) % n] for k in range((i_l - i_r) % n + 1)]
    path_b = [hull[(i_r - k) % n] for k in range((i_r - i_l) % n + 1)]

    def mean_v(path: list[Point2]) -> float:
        return sum(p[1] for p in path) / len(path)

    upper = path_a if mean_v(path_a) <= mean_v(path_b) else path_b
    ring = [left, right] + upper[1:-1]
    out: list[tuple[int, int]] = []
    for p in ring:
        q = (round(p[0]), round(p[1]))
        if not out or out[-1] != q:
            out.append(q)
    return out
