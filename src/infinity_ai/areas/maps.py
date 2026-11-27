# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the search, height and light maps of an area (BMP).

Measured in the game's rooms (2026-11-27): each map has one pixel per 16x12 of the area (width/16
x height/12, rounded up). The search map (`SR`) and the height map (`HT`) have 4 bits and 16
colours, the light map (`LM`) 8 bits and 256. The search map holds the game's terrain codes
(IESDP); a flat floor has height 8; an interior's light is a warm grey.
"""
from __future__ import annotations

import struct

from . import AreaError

CELL_W, CELL_H = 16, 12
# terrain codes of the search map (IESDP); the impassable ones block movement
TERRAIN = {'obstacle': 0, 'sand': 1, 'wood': 2, 'stone': 4, 'grass': 5, 'water': 6,
           'open-obstacle': 8, 'wall': 10, 'snow': 12}
# 'obstacle' (0) blocks movement and sight; 'open-obstacle' (8) blocks movement only (bars,
# nets, barrels: you see past them)
IMPASSABLE = frozenset({0, 6, 8, 10, 13})
FLAT = 8
# the 16 standard colours (the engine reads the index, not the colour)
VGA16 = [(0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
         (0, 128, 128), (192, 192, 192), (128, 128, 128), (255, 0, 0), (0, 255, 0),
         (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
GREYS16 = [(min(255, i * 16),) * 3 for i in range(16)]


def map_size(width_px: int, height_px: int) -> tuple[int, int]:
    return -(-width_px // CELL_W), -(-height_px // CELL_H)


def build_bmp(pixels: list[int], width: int, height: int, bpp: int,
              palette: list[tuple[int, int, int]]) -> bytes:
    """An uncompressed, bottom-up BMP of 4 or 8 bits per pixel."""
    if bpp not in (4, 8) or len(pixels) != width * height or len(palette) > (1 << bpp):
        raise AreaError('BAD_MAP', f'{width}x{height} {bpp} bits')
    if any(not 0 <= p < len(palette) for p in pixels):
        raise AreaError('BAD_MAP', 'a pixel outside the palette')
    row_bytes = ((width * bpp + 31) // 32) * 4
    body = bytearray()
    for y in range(height - 1, -1, -1):
        row = pixels[y * width:(y + 1) * width]
        if bpp == 8:
            line = bytes(row)
        else:
            line = bytes((row[i] << 4) | (row[i + 1] if i + 1 < width else 0)
                         for i in range(0, width, 2))
        body += line.ljust(row_bytes, b'\0')
    colours = len(palette)
    pal = b''.join(bytes((b, g, r, 0)) for r, g, b in palette)
    offset = 14 + 40 + len(pal)
    header = b'BM' + struct.pack('<IHHI', offset + len(body), 0, 0, offset)
    info = struct.pack('<IiiHHIIiiII', 40, width, height, 1, bpp, 0, len(body), 0, 0, colours, 0)
    return header + info + pal + bytes(body)


def read_bmp(data: bytes) -> tuple[int, int, int, list[int]]:
    """(width, height, bits, pixels top to bottom) of a 4- or 8-bit BMP."""
    if data[:2] != b'BM' or len(data) < 54:
        raise AreaError('BAD_MAP', 'not a BMP')
    offset = struct.unpack_from('<I', data, 10)[0]
    width, height = struct.unpack_from('<ii', data, 18)
    bpp = struct.unpack_from('<H', data, 28)[0]
    if bpp not in (4, 8):
        raise AreaError('BAD_MAP', f'{bpp} bits')
    bottom_up, height = height > 0, abs(height)
    row_bytes = ((width * bpp + 31) // 32) * 4
    rows = []
    for r in range(height):
        line = data[offset + r * row_bytes: offset + (r + 1) * row_bytes]
        if bpp == 8:
            rows.append(list(line[:width]))
        else:
            px = []
            for b in line:
                px += [b >> 4, b & 15]
            rows.append(px[:width])
    if bottom_up:
        rows.reverse()
    return width, height, bpp, [p for row in rows for p in row]


def search_map(codes: list[int], width: int, height: int) -> bytes:
    return build_bmp(codes, width, height, 4, VGA16)


def height_map(width: int, height: int) -> bytes:
    return build_bmp([FLAT] * (width * height), width, height, 4, GREYS16)


def light_map(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    palette = [rgb] + [(i, i, i) for i in range(1, 256)]
    return build_bmp([0] * (width * height), width, height, 8, palette)
