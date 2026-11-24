#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ADR-0146 (lab only): copy a room of the build as an area of ours (IA and four digits).

  python tools/windows-lab/build_area.py --source AR0310 --name IA0001            # what it would do
  python tools/windows-lab/build_area.py --source AR0310 --name IA0001 --apply    # game closed

Reads the ARE, WED, MOS and the three BMP of the room from the build, writes them to the VM's
override under our name (the ARE without creatures, spawn points, area script, containers or the
game's passages; the WED still points to the room's TIS, which is not copied). The bytes are game
data (CR-2026-030): they go only to the lab's override, never to the repository.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.actions.areas import copied_files, make_area, our_area_name  # noqa: E402
from infinity_ai.actions.gateway import ActionError  # noqa: E402
from infinity_ai.gamedata.inventory import _read_located, _Resources  # noqa: E402
from lab_ssh import SshByteSource, put_override_file, run_ps, ssh_from_env  # noqa: E402

TYPES = {'ARE': (0x3F2, 'are'), 'WED': (0x3E9, 'wed'), 'MOS': (0x3EC, 'mos'), 'BMP': (0x001, 'bmp')}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--source', required=True, help='a room of the build (e.g. AR0310)')
    ap.add_argument('--name', required=True, help='our area name (IA and four digits)')
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--apply', action='store_true', help='write to the override (game closed)')
    args = ap.parse_args()
    try:
        name = our_area_name(args.name)
    except ActionError as exc:
        print(f'recusado: {exc.code}')
        return 2
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    source = SshByteSource(ssh, args.game_root)
    res = _Resources(source)
    files: dict[str, bytes] = {}
    for src_ref, our_ref, kind in copied_files(args.source, name):
        type_id, ext = TYPES[kind]
        loc = res.locate(src_ref, type_id, ext, set())
        if loc is None:
            if kind == 'BMP':
                print(f'sem {src_ref}.{kind} na build (opcional)')
                continue
            print(f'recusado: {src_ref}.{kind} nao existe na build')
            return 2
        data = _read_located(source, {src_ref: loc})[src_ref]
        if kind == 'ARE':
            try:
                data = make_area(data, name)
            except ActionError as exc:
                print(f'recusado: {exc.code}')
                return 2
        files[f'{our_ref}.{kind}'] = data
        print(f'{src_ref}.{kind} -> {our_ref}.{kind} ({len(data)} bytes)')
    if not args.apply:
        print('(nada gravado; use --apply com o jogo fechado)')
        return 0
    running = run_ps(ssh, "(Get-Process -Name Baldur,InfinityLoader -ErrorAction SilentlyContinue"
                          " | Measure-Object).Count", timeout=60).strip()
    if running != '0':
        print('feche o jogo antes: o motor so acha arquivos do override presentes na abertura')
        return 2
    for fname, data in files.items():
        put_override_file(ssh, args.game_root, fname, data)
        print(f'gravado: override\\{fname}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
