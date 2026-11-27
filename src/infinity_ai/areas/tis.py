# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the area picture as a TIS V2 and its PVRZ pages.

A TIS V2 (the EE's) holds, per 64x64 tile, 12 bytes: the page and the tile's x, y in it. A page
is a PVRZ: the uncompressed size (dword) and a zlib-compressed PVR3 texture, DXT1 here. The page
name comes from the TIS name: its first letter, its last four characters and the page number in
two digits (measured in the lab: AR0310 -> A031000). Our TIS names have six characters (`IA` and
four digits), so our pages are `I` + four digits + two digits, and no page of the game starts
with `I` (measured 2026-11-27). Pages are powers of two up to 1024, as the game's (1024x512 for
AR0515).
"""
from __future__ import annotations

import struct
import zlib

from . import AreaError
from .dxt import decode_dxt1, decode_dxt5, encode_dxt1

TILE = 64
PAGE_TILES = 16                # 16x16 tiles = a 1024x1024 page at most
TIS_HEADER = 0x18
PVR3 = 0x03525650
FMT_DXT1, FMT_DXT5 = 7, 11
NO_PAGE = 0xFFFFFFFF


def page_name(tis_name: str, page: int) -> str:
    tis_name = tis_name.upper()
    if len(tis_name) < 5 or not 0 <= page <= 99:
        raise AreaError('PAGE_NAME', f'{tis_name} page {page}')
    return f'{tis_name[0]}{tis_name[-4:]}{page:02d}'


def _pow2(n: int) -> int:
    p = 64
    while p < n:
        p *= 2
    return p


def write_pvrz(rgb: bytes, width: int, height: int) -> bytes:
    data = encode_dxt1(rgb, width, height)
    header = struct.pack('<IIQIIIIIIIII', PVR3, 0, FMT_DXT1, 0, 0, height, width, 1, 1, 1, 1, 0)
    raw = header + data
    return struct.pack('<I', len(raw)) + zlib.compress(raw, 9)


def read_pvrz(data: bytes) -> tuple[int, int, bytes]:
    """(width, height, RGB) of a page."""
    if len(data) < 8:
        raise AreaError('BAD_PVRZ', 'too short')
    raw = zlib.decompress(data[4:])
    if len(raw) < 52:
        raise AreaError('BAD_PVRZ', 'no header')
    version, _f, fmt, _cs, _ct, height, width, _d, _s, _fa, _m, meta = \
        struct.unpack_from('<IIQIIIIIIIII', raw, 0)
    if version != PVR3 or fmt not in (FMT_DXT1, FMT_DXT5):
        raise AreaError('BAD_PVRZ', f'version {version:#x} format {fmt}')
    body = raw[52 + meta:]
    decode = decode_dxt1 if fmt == FMT_DXT1 else decode_dxt5
    return width, height, decode(body, width, height)


def build_tis(name: str, rgb: bytes, w_tiles: int, h_tiles: int
              ) -> tuple[bytes, dict[str, bytes]]:
    """(TIS file, {page name: PVRZ}) for a picture of w_tiles x h_tiles tiles, row by row."""
    if len(rgb) != w_tiles * TILE * h_tiles * TILE * 3:
        raise AreaError('BAD_PICTURE', f'{len(rgb)} bytes for {w_tiles}x{h_tiles} tiles')
    stride = w_tiles * TILE * 3
    count = w_tiles * h_tiles
    entries = bytearray()
    pages: dict[str, bytes] = {}
    for first in range(0, count, PAGE_TILES * PAGE_TILES):
        tiles = range(first, min(count, first + PAGE_TILES * PAGE_TILES))
        n = len(tiles)
        pw = _pow2(min(n, PAGE_TILES) * TILE)
        ph = _pow2(((n + PAGE_TILES - 1) // PAGE_TILES) * TILE)
        page = bytearray(pw * ph * 3)
        index = first // (PAGE_TILES * PAGE_TILES)
        for k, t in enumerate(tiles):
            px, py = (k % PAGE_TILES) * TILE, (k // PAGE_TILES) * TILE
            sx, sy = (t % w_tiles) * TILE, (t // w_tiles) * TILE
            for row in range(TILE):
                src = (sy + row) * stride + sx * 3
                dst = ((py + row) * pw + px) * 3
                page[dst:dst + TILE * 3] = rgb[src:src + TILE * 3]
            entries += struct.pack('<III', index, px, py)
        pages[page_name(name, index)] = write_pvrz(bytes(page), pw, ph)
    header = b'TIS V1  ' + struct.pack('<IIII', count, 12, TIS_HEADER, TILE)
    return header + bytes(entries), pages


def read_tis(data: bytes) -> list[tuple[int, int, int]]:
    """The (page, x, y) of every tile of a TIS V2 file."""
    if data[:8] != b'TIS V1  ' or len(data) < TIS_HEADER:
        raise AreaError('BAD_TIS', 'no header')
    count, size, offset, dim = struct.unpack_from('<IIII', data, 8)
    if size != 12 or dim != TILE or len(data) < offset + 12 * count:
        raise AreaError('BAD_TIS', f'tile size {size}, dimension {dim}')
    return [struct.unpack_from('<III', data, offset + 12 * i) for i in range(count)]


def render_tis(entries: list[tuple[int, int, int]], pages: dict[int, tuple[int, int, bytes]],
               w_tiles: int, h_tiles: int, lookup: list[int] | None = None) -> bytes:
    """The picture (RGB) from tile entries and decoded pages {page: (w, h, rgb)}; `lookup` maps
    each cell to its tile (the WED's), cell order when absent. A missing page draws black."""
    width = w_tiles * TILE
    out = bytearray(width * h_tiles * TILE * 3)
    for cell in range(w_tiles * h_tiles):
        t = lookup[cell] if lookup else cell
        if t >= len(entries):
            continue
        page, px, py = entries[t]
        if page == NO_PAGE or page not in pages:
            continue
        pw, _ph, prgb = pages[page]
        cx, cy = (cell % w_tiles) * TILE, (cell // w_tiles) * TILE
        for row in range(TILE):
            src = ((py + row) * pw + px) * 3
            dst = ((cy + row) * width + cx) * 3
            out[dst:dst + TILE * 3] = prgb[src:src + TILE * 3]
    return bytes(out)
