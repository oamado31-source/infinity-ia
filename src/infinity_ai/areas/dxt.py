# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: DXT1 (BC1) compression of RGB pictures, and DXT1/DXT5 decoding.

An area picture has no transparency, so pages are written as DXT1 in four-colour mode. The
encoder is a plain range fit: the block's darkest and brightest colours (by luminance) are the
endpoints, and each pixel takes the nearest of the four colours between them. Pictures are
`bytes` of packed RGB, row by row; width and height are multiples of 4.
"""
from __future__ import annotations

import struct

from . import AreaError


def _to565(r: int, g: int, b: int) -> int:
    return ((r * 31 + 127) // 255) << 11 | ((g * 63 + 127) // 255) << 5 | ((b * 31 + 127) // 255)


def _from565(c: int) -> tuple[int, int, int]:
    r, g, b = (c >> 11) & 31, (c >> 5) & 63, c & 31
    return (r << 3 | r >> 2, g << 2 | g >> 4, b << 3 | b >> 2)


def _palette(c0: int, c1: int) -> list[tuple[int, int, int]]:
    a, b = _from565(c0), _from565(c1)
    if c0 > c1:
        return [a, b, tuple((2 * x + y) // 3 for x, y in zip(a, b)),
                tuple((x + 2 * y) // 3 for x, y in zip(a, b))]
    return [a, b, tuple((x + y) // 2 for x, y in zip(a, b)), (0, 0, 0)]


def _encode_block(px: list[tuple[int, int, int]]) -> bytes:
    lum = [r * 299 + g * 587 + b * 114 for r, g, b in px]
    hi, lo = px[lum.index(max(lum))], px[lum.index(min(lum))]
    c0, c1 = _to565(*hi), _to565(*lo)
    if c0 == c1:
        return struct.pack('<HHI', c0, c1, 0)
    if c0 < c1:
        c0, c1 = c1, c0
    pal = _palette(c0, c1)
    bits = 0
    for i, (r, g, b) in enumerate(px):
        best = min(range(4), key=lambda k: (pal[k][0] - r) ** 2 + (pal[k][1] - g) ** 2
                   + (pal[k][2] - b) ** 2)
        bits |= best << (2 * i)
    return struct.pack('<HHI', c0, c1, bits)


def encode_dxt1(rgb: bytes, width: int, height: int) -> bytes:
    """Blocks of 4x4, left to right and top to bottom, 8 bytes each."""
    if width % 4 or height % 4 or len(rgb) != width * height * 3:
        raise AreaError('BAD_PICTURE', f'{width}x{height} with {len(rgb)} bytes')
    out = bytearray()
    stride = width * 3
    for by in range(0, height, 4):
        for bx in range(0, width, 4):
            px = []
            for y in range(by, by + 4):
                row = y * stride + bx * 3
                px.extend((rgb[row + 3 * k], rgb[row + 3 * k + 1], rgb[row + 3 * k + 2])
                          for k in range(4))
            out += _encode_block(px)
    return bytes(out)


def decode_dxt1(data: bytes, width: int, height: int) -> bytes:
    return _decode(data, width, height, 8)


def decode_dxt5(data: bytes, width: int, height: int) -> bytes:
    """The colour part only (the alpha block is skipped): previews show areas opaque."""
    return _decode(data, width, height, 16)


def _decode(data: bytes, width: int, height: int, block: int) -> bytes:
    bw, bh = (width + 3) // 4, (height + 3) // 4
    if len(data) < bw * bh * block:
        raise AreaError('BAD_TEXTURE', f'{len(data)} bytes for {width}x{height}')
    out = bytearray(width * height * 3)
    pos = 0
    for by in range(bh):
        for bx in range(bw):
            c0, c1, bits = struct.unpack_from('<HHI', data, pos + block - 8)
            # DXT5 colour blocks always use four colours
            pal = _palette(c0, c1) if block == 8 else _four(c0, c1)
            pos += block
            for i in range(16):
                x, y = bx * 4 + i % 4, by * 4 + i // 4
                if x < width and y < height:
                    o = (y * width + x) * 3
                    out[o:o + 3] = bytes(pal[(bits >> (2 * i)) & 3])
    return bytes(out)


def _four(c0: int, c1: int) -> list[tuple[int, int, int]]:
    a, b = _from565(c0), _from565(c1)
    return [a, b, tuple((2 * x + y) // 3 for x, y in zip(a, b)),
            tuple((x + 2 * y) // 3 for x, y in zip(a, b))]
