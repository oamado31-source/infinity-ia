# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: from a recipe to the files of an area, with a manifest of what was made.

`build_area_files` returns {file name: bytes}: ARE, WED, TIS, the PVRZ pages, MOS and the SR, HT
and LM maps, all named after the recipe's area. `manifest` records the recipe's sha256 and each
file's, so a file found later can be traced to the recipe that made it (REQ-MAP-008).
"""
from __future__ import annotations

import hashlib
import json

from . import AreaError
from .are import Entrance, build_are
from .maps import TERRAIN, height_map, light_map, map_size, search_map, CELL_H, CELL_W
from .mos import build_mos
from .procedural import draw
from .recipe import Recipe
from .tis import build_tis
from .wed import Wall, build_wed

MANIFEST_SCHEMA = 'infinity-ai.area-build.v1'


def terrain_codes(recipe: Recipe) -> tuple[int, int, list[int]]:
    """(width, height, codes) of the search map: each cell takes the terrain of the last region
    that holds its centre, else the floor's."""
    mw, mh = map_size(recipe.width_px, recipe.height_px)
    floor = TERRAIN[recipe.floor_terrain]
    shaped = [(r.shape, TERRAIN[r.terrain]) for r in recipe.regions if r.terrain]
    codes = []
    for j in range(mh):
        for i in range(mw):
            cx, cy = i * CELL_W + CELL_W / 2, j * CELL_H + CELL_H / 2
            code = floor
            for shape, c in shaped:
                if shape.contains(cx, cy):
                    code = c
            codes.append(code)
    return mw, mh, codes


def build_area_files(recipe: Recipe, picture: bytes | None = None) -> dict[str, bytes]:
    """`picture`: the RGB of a rendered recipe (ADR-0150), as Blender wrote it; a procedural
    recipe is drawn here."""
    name = recipe.area
    if picture is None and recipe.scene_path is not None:
        raise AreaError('NO_PICTURE', f'{name}: renderize a cena antes (render_area.py)')
    rgb = picture if picture is not None else draw(recipe)
    if len(rgb) != recipe.width_px * recipe.height_px * 3:
        raise AreaError('BAD_PICTURE', f'o desenho precisa ter {recipe.width_px}x{recipe.height_px}')
    tis, pages = build_tis(name, rgb, recipe.width, recipe.height)
    walls = [Wall(shape.points()) for _id, shape in recipe.walls]
    mw, mh, codes = terrain_codes(recipe)
    files = {
        f'{name}.ARE': build_are(name, recipe.kind, [Entrance(e.point_id, e.x, e.y, e.facing)
                                                     for e in recipe.entrances],
                                 explored=((recipe.width_px, recipe.height_px)
                                           if recipe.explored else None)),
        f'{name}.WED': build_wed(name, recipe.width, recipe.height, walls),
        f'{name}.TIS': tis,
        f'{name}.MOS': build_mos(rgb, recipe.width_px, recipe.height_px),
        f'{name}SR.BMP': search_map(codes, mw, mh),
        f'{name}HT.BMP': height_map(mw, mh),
        f'{name}LM.BMP': light_map(mw, mh, recipe.light),
    }
    files.update({f'{p}.PVRZ': data for p, data in pages.items()})
    return files


def manifest(recipe_bytes: bytes, recipe: Recipe, files: dict[str, bytes],
             sources: dict[str, bytes] | None = None) -> bytes:
    """`sources`: what else made the area (the scene and the rendered picture), by name."""
    doc = {
        'schema': MANIFEST_SCHEMA,
        'area': recipe.area,
        'recipe_version': recipe.version,
        'recipe_sha256': hashlib.sha256(recipe_bytes).hexdigest(),
        'sources': {n: hashlib.sha256(d).hexdigest() for n, d in sorted((sources or {}).items())},
        'files': {n: hashlib.sha256(d).hexdigest() for n, d in sorted(files.items())},
        'provenance': recipe.provenance,
    }
    return (json.dumps(doc, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
