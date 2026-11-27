#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ADR-0149 (lab only): draw any area of the lab build (the game's or ours) to a local PNG.

  python tools/windows-lab/area_preview.py AR0310                 # the picture
  python tools/windows-lab/area_preview.py AR0310 --map           # + impassable cells and walls
  python tools/windows-lab/area_preview.py AR0310 --roundtrip     # rewrite it with our writers

The picture of a game area is game data: the PNG goes to ~/.infinity-ai/previews, never to the
repository (CR-2026-030). --roundtrip rewrites the room's picture, search map and walls with our
writers and compares them with the game's (same tiles within the DXT1 error, same search map,
same walls; wall groups that hold the game's): the lab check of ADR-0149.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.areas.maps import read_bmp, search_map  # noqa: E402
from infinity_ai.areas.png import write_png  # noqa: E402
from infinity_ai.areas.preview import render_area  # noqa: E402
from infinity_ai.areas.tis import build_tis, read_pvrz, read_tis, render_tis  # noqa: E402
from infinity_ai.areas.wed import build_wed, read_wed  # noqa: E402
from infinity_ai.gamedata.inventory import _Resources  # noqa: E402
from lab_ssh import SshByteSource, ssh_from_env  # noqa: E402

TYPES = {'are': 0x3F2, 'wed': 0x3E9, 'tis': 0x3EB, 'pvrz': 0x404, 'bmp': 0x001, 'mos': 0x3EC}
OUT = Path.home() / '.infinity-ai' / 'previews'


def psnr(a: bytes, b: bytes) -> float:
    err = sum((x - y) ** 2 for x, y in zip(a, b)) / max(1, len(a))
    return 99.0 if err == 0 else 10 * math.log10(255 * 255 / err)


def roundtrip(area: str, fetch) -> bool:
    w, h, game_rgb = render_area(area, fetch)
    wed = read_wed(fetch(area, 'wed'))
    w_tiles, h_tiles, _tis = wed.overlays[0]
    tis, pages = build_tis('IA9999', game_rgb, w_tiles, h_tiles)
    decoded = {i: read_pvrz(data) for i, (_n, data) in enumerate(sorted(pages.items()))}
    ours = render_tis(read_tis(tis), decoded, w_tiles, h_tiles)
    quality = psnr(game_rgb, ours)
    sw, sh, _bpp, codes = read_bmp(fetch(f'{area}SR', 'bmp'))
    sr_same = read_bmp(search_map(codes, sw, sh))[3] == codes
    again = read_wed(build_wed('IA9999', w_tiles, h_tiles, list(wed.walls), strict=False))
    walls_same = [x.points for x in again.walls] == [x.points for x in wed.walls]
    groups_cover = all(set(g) <= set(o) for g, o in zip(wed.groups, again.groups))
    extra = sum(len(set(o) - set(g)) for g, o in zip(wed.groups, again.groups))
    print(f'{area}: desenho {quality:.1f} dB, mapa de busca igual={sr_same}, '
          f'paredes iguais={walls_same}, grupos contêm os do jogo={groups_cover} '
          f'({len(wed.walls)} paredes, {len(wed.groups)} grupos, {extra} a mais)')
    return quality >= 30 and sr_same and walls_same and groups_cover


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('areas', nargs='+')
    ap.add_argument('--map', action='store_true')
    ap.add_argument('--roundtrip', action='store_true')
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    args = ap.parse_args()
    source = SshByteSource(ssh_from_env('INFINITY_LAB_SSH'), args.game_root)
    res = _Resources(source)

    def fetch(ref: str, ext: str) -> bytes | None:
        return res.get(ref.upper(), TYPES[ext], ext)

    ok = True
    for area in (a.upper() for a in args.areas):
        if args.roundtrip:
            ok &= roundtrip(area, fetch)
            continue
        w, h, rgb = render_area(area, fetch, search=args.map, walls=args.map)
        OUT.mkdir(parents=True, exist_ok=True)
        out = OUT / f'{area}{"-mapa" if args.map else ""}.png'
        out.write_bytes(write_png(rgb, w, h))
        print(f'{area}: {w}x{h} -> {out}')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
