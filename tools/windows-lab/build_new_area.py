#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ADR-0149 (lab only): build a new area of ours from its recipe, check it, and install it.

  python tools/windows-lab/build_new_area.py --recipe knowledge/areas/ia0090-sala-de-teste.json
  python tools/windows-lab/build_new_area.py --recipe ... --apply      # game closed

Builds every file from the recipe (no game byte), writes them with a manifest to
~/.infinity-ai/areas/<AREA>/, and checks them against every resource name of the lab build (read
from the KEY over SSH), so no name of ours collides. With --apply, and the game closed, copies
them to the lab's override. Refuses names that are not ours.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.areas import AreaError  # noqa: E402
from infinity_ai.areas.build import build_area_files, manifest  # noqa: E402
from infinity_ai.areas.check import check_area  # noqa: E402
from infinity_ai.areas.recipe import parse_recipe  # noqa: E402
from infinity_ai.gamedata.inventory import _read_whole  # noqa: E402
from lab_ssh import SshByteSource, put_override_file, run_ps, ssh_from_env  # noqa: E402

OUT = Path.home() / '.infinity-ai' / 'areas'


def build_names(source: SshByteSource) -> set[str]:
    """Every resource name in the build's KEY (all types), upper case."""
    key = _read_whole(source, 'chitin.key')
    _n_bif, n_res, _off_bif, off_res = struct.unpack_from('<4I', key, 8)
    return {key[off_res + 14 * i: off_res + 14 * i + 8].split(b'\0')[0].decode('latin-1').upper()
            for i in range(n_res)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--recipe', required=True, type=Path)
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--out', type=Path, default=OUT)
    ap.add_argument('--apply', action='store_true', help='copy to the override (game closed)')
    args = ap.parse_args()
    raw = args.recipe.read_bytes()
    try:
        recipe = parse_recipe(json.loads(raw))
        files = build_area_files(recipe)
    except (ValueError, AreaError) as exc:
        print(f'recusado: {getattr(exc, "code", "RECIPE")}: {getattr(exc, "detail", exc)}')
        return 2
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    source = SshByteSource(ssh, args.game_root)
    report = check_area(recipe, files, build_names(source))
    for code, detail in report.errors:
        print(f'ERRO {code}: {detail}')
    for code, detail in report.warnings:
        print(f'aviso {code}: {detail}')
    if not report.ok:
        return 2
    out = args.out / recipe.area
    out.mkdir(parents=True, exist_ok=True)
    for name, data in sorted(files.items()):
        (out / name).write_bytes(data)
        print(f'{name} ({len(data)} bytes)')
    (out / 'manifest.json').write_bytes(manifest(raw, recipe, files))
    print(f'gerado em {out}')
    if not args.apply:
        print('(nada gravado na VM; use --apply com o jogo fechado)')
        return 0
    running = run_ps(ssh, "(Get-Process -Name Baldur,InfinityLoader -ErrorAction SilentlyContinue"
                          " | Measure-Object).Count", timeout=60).strip()
    if running != '0':
        print('feche o jogo antes: o motor so acha arquivos do override presentes na abertura')
        return 2
    for name, data in sorted(files.items()):
        put_override_file(ssh, args.game_root, name, data)
        print(f'gravado: override\\{name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
