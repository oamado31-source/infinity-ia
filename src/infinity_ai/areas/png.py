# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: a minimal PNG writer (RGB, 8 bits), for local previews of areas; ADR-0150: and a
reader, for the picture Blender renders."""
from __future__ import annotations

import struct
import zlib


def write_png(rgb: bytes, width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack('>I', len(data)) + kind + data + struct.pack(
            '>I', zlib.crc32(kind + data) & 0xFFFFFFFF)

    stride = width * 3
    raw = b''.join(b'\0' + rgb[y * stride:(y + 1) * stride] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2,
                                                                0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


def read_png(data: bytes) -> tuple[int, int, bytes]:
    """(width, height, RGB) of an 8-bit RGB or RGBA PNG, not interlaced (what Blender writes)."""
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    pos, idat, head = 8, b'', None
    while pos < len(data):
        n, kind = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if kind == b'IHDR':
            head = struct.unpack('>IIBBBBB', body)
        elif kind == b'IDAT':
            idat += body
        elif kind == b'IEND':
            break
        pos += 12 + n
    if head is None:
        raise ValueError('PNG without IHDR')
    width, height, depth, ctype, _c, _f, interlace = head
    if depth != 8 or ctype not in (2, 6) or interlace:
        raise ValueError(f'PNG not supported: depth {depth}, colour type {ctype}')
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(idat)
    stride = width * bpp
    out = bytearray()
    prev = bytearray(stride)
    p = 0
    for _ in range(height):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[i] = (line[i] + pr) & 255
        prev = line
        if bpp == 3:
            out += line
        else:
            for i in range(0, stride, 4):
                out += line[i:i + 3]
    return width, height, bytes(out)
