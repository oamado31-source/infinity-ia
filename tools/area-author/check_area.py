#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: check area recipes and list every problem by name (errors block, warnings inform).

  python tools/area-author/check_area.py knowledge/areas/ia0090-sala-de-teste.json
  python tools/area-author/check_area.py --png RECIPE      # also a preview in ~/.infinity-ai/previews

Builds the area in memory from the recipe and reads the files back as the engine would. The
build's area names come from the local inventory (~/.infinity-ai, never the repository); the
lab tool `build_new_area.py` also checks every resource name of the build over SSH. Exit code 1
when any recipe has an error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.areas import AreaError  # noqa: E402
from infinity_ai.areas.build import build_area_files  # noqa: E402
from infinity_ai.areas.check import check_area  # noqa: E402
from infinity_ai.areas.png import read_png, write_png  # noqa: E402
from infinity_ai.areas.preview import render_area  # noqa: E402
from infinity_ai.areas.recipe import parse_recipe  # noqa: E402

LOCAL = Path.home() / '.infinity-ai'


def local_area_names(language: str = 'pt_BR') -> set[str]:
    found = sorted(LOCAL.glob(f'knowledge/install-*/areas.{language}.json'))
    try:
        doc = json.loads(found[-1].read_text(encoding='utf-8')) if found else {}
    except (OSError, ValueError):
        doc = {}
    return {a['resref'].upper() for a in doc.get('areas', []) if a.get('resref')}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('recipes', nargs='+', type=Path)
    ap.add_argument('--png', action='store_true', help='write a preview with the walkable map')
    args = ap.parse_args()
    existing = local_area_names()
    bad = False
    for path in args.recipes:
        try:
            recipe = parse_recipe(json.loads(path.read_text(encoding='utf-8')), path.parent)
            picture = None
            if recipe.scene_path is not None:         # ADR-0150: the rendered picture, if made
                png = LOCAL / 'areas' / recipe.area / 'picture.png'
                picture = (read_png(png.read_bytes())[2] if png.exists()
                           else bytes(recipe.width_px * recipe.height_px * 3))
            files = build_area_files(recipe, picture)
        except (OSError, ValueError, AreaError) as exc:
            code = getattr(exc, 'code', 'RECIPE')
            print(f'{path}: ERRO {code}: {getattr(exc, "detail", exc)}')
            bad = True
            continue
        report = check_area(recipe, files, existing)
        for code, detail in report.errors:
            print(f'{path}: ERRO {code}: {detail}')
        for code, detail in report.warnings:
            print(f'{path}: aviso {code}: {detail}')
        if report.ok:
            size = sum(len(d) for d in files.values())
            print(f'{path}: OK ({recipe.area}, {recipe.width}x{recipe.height} tiles, '
                  f'{len(files)} arquivos, {size} bytes)')
        bad |= not report.ok
        if args.png:
            fetch = lambda ref, ext: files.get(f'{ref.upper()}.{ext.upper()}')  # noqa: E731
            w, h, rgb = render_area(recipe.area, fetch, search=True, walls=True)
            out = LOCAL / 'previews' / f'{recipe.area}-receita.png'
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(write_png(rgb, w, h))
            print(f'  prévia: {out}')
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
