# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the minimap of an area as a MOS V1.

Measured in the game's rooms (2026-11-27): the minimap is the area at 1/6.4 (1280x960 -> 200x150,
1024x768 -> 160x120), in blocks of 64x64, each block with a 256-colour palette. Ours uses one fixed
palette (6 x 7 x 6 levels) for every block; a minimap needs no more.
"""
from __future__ import annotations

import struct

from . import AreaError

BLOCK = 64
SCALE = 6.4
_R, _G, _B = 6, 7, 6
PALETTE = [(r * 255 // (_R - 1), g * 255 // (_G - 1), b * 255 // (_B - 1))
           for r in range(_R) for g in range(_G) for b in range(_B)]


def minimap_size(width_px: int, height_px: int) -> tuple[int, int]:
    return max(1, round(width_px / SCALE)), max(1, round(height_px / SCALE))


def _index(r: int, g: int, b: int) -> int:
    return (round(r * (_R - 1) / 255) * _G + round(g * (_G - 1) / 255)) * _B \
        + round(b * (_B - 1) / 255)


def build_mos(rgb: bytes, width: int, height: int) -> bytes:
    if len(rgb) != width * height * 3:
        raise AreaError('BAD_PICTURE', f'{len(rgb)} bytes for {width}x{height}')
    mw, mh = minimap_size(width, height)
    small = []
    for y in range(mh):
        y0, y1 = y * height // mh, max(y * height // mh + 1, (y + 1) * height // mh)
        for x in range(mw):
            x0, x1 = x * width // mw, max(x * width // mw + 1, (x + 1) * width // mw)
            acc, n = [0, 0, 0], 0
            for yy in range(y0, y1, 2):
                row = yy * width
                for xx in range(x0, x1, 2):
                    o = (row + xx) * 3
                    acc[0] += rgb[o]
                    acc[1] += rgb[o + 1]
                    acc[2] += rgb[o + 2]
                    n += 1
            small.append(_index(acc[0] // n, acc[1] // n, acc[2] // n))
    cols, rows = -(-mw // BLOCK), -(-mh // BLOCK)
    blocks = cols * rows
    pal = b''.join(bytes((b, g, r, 0)) for r, g, b in PALETTE).ljust(1024, b'\0')
    pixels = bytearray()
    offsets = []
    for by in range(rows):
        for bx in range(cols):
            offsets.append(len(pixels))
            for y in range(by * BLOCK, min(mh, (by + 1) * BLOCK)):
                pixels += bytes(small[y * mw + bx * BLOCK: y * mw + min(mw, (bx + 1) * BLOCK)])
    header = b'MOS V1  ' + struct.pack('<HHHHII', mw, mh, cols, rows, BLOCK, 0x18)
    return header + pal * blocks + struct.pack(f'<{blocks}I', *offsets) + bytes(pixels)


def read_mos_size(data: bytes) -> tuple[int, int]:
    if data[:8] != b'MOS V1  ':
        raise AreaError('BAD_MOS', 'not a MOS V1')
    return struct.unpack_from('<HH', data, 8)
