#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ADR-0150: render the scene of an area recipe with Blender (headless, on the Mac).

  python tools/area-author/render_area.py knowledge/areas/ia0004-porao.json
  BLENDER=/path/to/Blender python tools/area-author/render_area.py RECIPE

Writes ~/.infinity-ai/areas/<AREA>/picture.png (never the repository) and checks its size against
the recipe. Then `build_new_area.py` turns it into the area's files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.areas import AreaError  # noqa: E402
from infinity_ai.areas.png import read_png  # noqa: E402
from infinity_ai.areas.recipe import parse_recipe  # noqa: E402

OUT = Path.home() / '.infinity-ai' / 'areas'
BLENDER = Path.home() / 'Applications' / 'Blender.app' / 'Contents' / 'MacOS' / 'Blender'
SCRIPT = ROOT / 'tools' / 'area-author' / 'blender' / 'infai_render.py'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('recipe', type=Path)
    ap.add_argument('--out', type=Path, default=OUT)
    args = ap.parse_args()
    try:
        recipe = parse_recipe(json.loads(args.recipe.read_text(encoding='utf-8')),
                              args.recipe.parent)
    except (OSError, ValueError, AreaError) as exc:
        print(f'recusado: {getattr(exc, "code", "RECIPE")}: {getattr(exc, "detail", exc)}')
        return 2
    if recipe.scene_path is None:
        print('recusado: a receita não tem cena para renderizar (picture.kind = procedural)')
        return 2
    blender = Path(os.environ.get('BLENDER', BLENDER))
    if not blender.exists():
        print(f'Blender não encontrado em {blender} (ou defina BLENDER)')
        return 2
    out = args.out / recipe.area
    out.mkdir(parents=True, exist_ok=True)
    png = out / 'picture.png'
    png.unlink(missing_ok=True)          # a failed render must not leave the old picture
    run = subprocess.run([str(blender), '-b', '--factory-startup', '--python-exit-code', '1',
                          '--python', str(SCRIPT), '--',
                          str(recipe.scene_path), str(png)], capture_output=True, text=True)
    if run.returncode != 0 or not png.exists():
        print(run.stdout[-2000:], run.stderr[-2000:])
        return 1
    w, h, _rgb = read_png(png.read_bytes())
    if (w, h) != (recipe.width_px, recipe.height_px):
        print(f'o desenho saiu {w}x{h}, a receita pede {recipe.width_px}x{recipe.height_px}')
        return 1
    print(f'{recipe.area}: {png} ({w}x{h}, sha256 '
          f'{hashlib.sha256(png.read_bytes()).hexdigest()[:12]}…)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
