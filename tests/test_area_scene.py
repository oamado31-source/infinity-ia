# SPDX-License-Identifier: Apache-2.0
"""ADR-0150: a rendered area: the scene, what the area takes from it, the PNG Blender writes."""
import json
import struct
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.areas import AreaError  # noqa: E402
from infinity_ai.areas.build import build_area_files, terrain_codes  # noqa: E402
from infinity_ai.areas.camera import Box, Camera, occluder  # noqa: E402
from infinity_ai.areas.check import check_area  # noqa: E402
from infinity_ai.areas.maps import CELL_H, CELL_W, IMPASSABLE  # noqa: E402
from infinity_ai.areas.png import read_png, write_png  # noqa: E402
from infinity_ai.areas.recipe import parse_recipe  # noqa: E402
from infinity_ai.areas.scene import parse_scene, scene_regions, scene_walls  # noqa: E402

AREAS = ROOT / 'knowledge' / 'areas'
RECIPE = AREAS / 'ia0004-porao.json'
SCENE = AREAS / 'scenes' / 'ia0004-porao.json'


def scene_doc():
    return json.loads(SCENE.read_text(encoding='utf-8'))


class SceneTests(unittest.TestCase):
    def test_the_hold_scene_reads_and_its_marker_lands_on_the_picture(self):
        sc = parse_scene(scene_doc())
        self.assertEqual((sc.area, sc.width, sc.height), ('IA0004', 960, 768))
        self.assertEqual(sc.markers[0].point_id, 'pe-da-escada')
        self.assertEqual((sc.markers[0].x, sc.markers[0].y), (737, 241))

    def test_the_floor_comes_first_and_parts_block_after_it(self):
        regions = scene_regions(parse_scene(scene_doc()))
        self.assertEqual(regions[0].terrain, 'wood')
        self.assertTrue(all(r.terrain != 'wood' for r in regions[1:]))

    def test_parts_that_hide_become_walls_with_their_foot_as_baseline(self):
        walls = scene_walls(parse_scene(scene_doc()))
        self.assertGreater(len(walls), 10)
        for _id, shape in walls:
            (ax, ay), (bx, by) = shape.polygon[:2]
            self.assertLess(ax, bx)

    def test_unknown_parts_and_markerless_scenes_are_refused(self):
        d = scene_doc()
        d['parts'].append({'kind': 'dragon', 'x': 1, 'y': 1})
        with self.assertRaises(AreaError):
            parse_scene(d)
        d = scene_doc()
        d['markers'] = []
        with self.assertRaises(AreaError) as cm:
            parse_scene(d)
        self.assertEqual(cm.exception.code, 'NO_ENTRANCE')

    def test_a_stacked_part_hides_from_the_ground_up(self):
        cam = Camera(45, 40, 45, 400, 600)
        low = occluder(cam, Box(0, 0, 1, 1, 1))
        stacked = occluder(cam, Box(0, 0, 1, 1, 0.8, z=1.0))
        self.assertEqual(low[:2], stacked[:2])                  # the same foot
        self.assertLess(min(v for _u, v in stacked), min(v for _u, v in low))


class RenderedRecipeTests(unittest.TestCase):
    def recipe(self):
        return parse_recipe(json.loads(RECIPE.read_text(encoding='utf-8')), RECIPE.parent)

    def test_the_schema_accepts_both_recipes(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest('jsonschema not installed')
        schema = json.loads((AREAS / 'area-recipe.v1.schema.json').read_text(encoding='utf-8'))
        for name in ('ia0004-porao.json', 'ia0090-sala-de-teste.json'):
            jsonschema.validate(json.loads((AREAS / name).read_text(encoding='utf-8')), schema)

    def test_the_hold_needs_its_picture_then_passes_the_checker(self):
        r = self.recipe()
        with self.assertRaises(AreaError) as cm:
            build_area_files(r)
        self.assertEqual(cm.exception.code, 'NO_PICTURE')
        files = build_area_files(r, bytes(r.width_px * r.height_px * 3))
        report = check_area(r, files, {'AR0300'})
        self.assertEqual((report.errors, report.warnings), ([], []))

    def test_the_entrance_at_the_ladder_is_walkable_and_the_mast_is_not(self):
        r = self.recipe()
        mw, _mh, codes = terrain_codes(r)
        e = r.entrances[0]
        self.assertNotIn(codes[(e.y // CELL_H) * mw + e.x // CELL_W], IMPASSABLE)
        sc = parse_scene(scene_doc())
        u, v = sc.camera.project(12, 4)                       # the mast's centre
        self.assertIn(codes[(int(v) // CELL_H) * mw + int(u) // CELL_W], IMPASSABLE)

    def test_scene_and_recipe_must_agree(self):
        d = json.loads(RECIPE.read_text(encoding='utf-8'))
        d['size'] = {'width': 16, 'height': 12}
        with self.assertRaises(AreaError) as cm:
            parse_recipe(d, RECIPE.parent)
        self.assertEqual(cm.exception.code, 'SCENE')
        d = json.loads(RECIPE.read_text(encoding='utf-8'))
        d['entrances'] = [{'name': 'Escada', 'marker': 'nenhum'}]
        with self.assertRaises(AreaError):
            parse_recipe(d, RECIPE.parent)


class PngTests(unittest.TestCase):
    def test_round_trip(self):
        rgb = bytes(range(256)) * 3 * 4
        self.assertEqual(read_png(write_png(rgb, 32, 32)), (32, 32, rgb))

    def test_filtered_rgba_as_blender_may_write(self):
        w, h = 3, 2
        rows = [[(10, 20, 30, 255), (11, 22, 33, 255), (12, 24, 36, 255)],
                [(10, 20, 30, 255), (10, 20, 30, 255), (10, 20, 30, 255)]]
        raw = b''
        prev = [0] * (w * 4)
        for f, row in zip((1, 2), rows):                # Sub, then Up
            flat = [c for px in row for c in px]
            if f == 1:
                enc = [(flat[i] - (flat[i - 4] if i >= 4 else 0)) & 255 for i in range(len(flat))]
            else:
                enc = [(flat[i] - prev[i]) & 255 for i in range(len(flat))]
            raw += bytes([f] + enc)
            prev = flat

        def chunk(k, d):
            return struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k + d))

        png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
               + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
        _w, _h, rgb = read_png(png)
        self.assertEqual(rgb, bytes(c for row in rows for px in row for c in px[:3]))


if __name__ == '__main__':
    unittest.main()


SHIP = ('ia0002-conves-superior.json', 'ia0003-conves-do-meio.json', 'ia0004-porao.json',
        'ia0005-camarotes.json')


class ShipTests(unittest.TestCase):
    """ADR-0151: the whole ship: four decks, a raised deck, a boat and the climb aboard."""

    def recipe(self, name):
        path = AREAS / name
        return parse_recipe(json.loads(path.read_text(encoding='utf-8')), path.parent)

    def cell(self, recipe, scene, x, y, z=0.0):
        mw, _mh, codes = terrain_codes(recipe)
        u, v = scene.camera.project(x, y, z)
        return codes[(int(v) // CELL_H) * mw + int(u) // CELL_W]

    def test_every_deck_passes_the_checker(self):
        for name in SHIP:
            r = self.recipe(name)
            files = build_area_files(r, bytes(r.width_px * r.height_px * 3))
            report = check_area(r, files, {'AR0300'})
            self.assertEqual((report.errors, report.warnings), ([], []), name)

    def test_the_raised_deck_is_walked_on_top_and_blocks_in_front(self):
        r = self.recipe('ia0002-conves-superior.json')
        sc = parse_scene(json.loads((AREAS / 'scenes' / 'ia0002-conves-superior.json')
                                    .read_text(encoding='utf-8')))
        self.assertNotIn(self.cell(r, sc, 22.0, 6.0, 1.8), IMPASSABLE)     # on the quarterdeck
        self.assertIn(self.cell(r, sc, 18.0, 6.0, 0.9), IMPASSABLE)        # its front face
        self.assertNotIn(self.cell(r, sc, 17.0, 6.0), IMPASSABLE)          # the deck before it
        self.assertNotIn(self.cell(r, sc, 17.1, 1.1, 0.9), IMPASSABLE)     # half way up the stairs

    def test_the_party_arrives_in_the_boat_and_climbs_aboard(self):
        r = self.recipe('ia0002-conves-superior.json')
        sc = parse_scene(json.loads((AREAS / 'scenes' / 'ia0002-conves-superior.json')
                                    .read_text(encoding='utf-8')))
        self.assertEqual(r.entrances[0].point_id, 'Barco')
        self.assertNotIn(self.cell(r, sc, 13.2, -1.25, -2.15), IMPASSABLE)  # in the boat
        self.assertIn(self.cell(r, sc, 16.0, -1.0, -2.4), IMPASSABLE)       # the sea
        self.assertNotIn(self.cell(r, sc, 12.0, 0.2, -0.6), IMPASSABLE)     # up the rope ladder
        self.assertIn(self.cell(r, sc, 8.0, 0.2, 0.0), IMPASSABLE)          # the rail elsewhere
        # the way up is the ladder and the boarding nets beside it; past them the hull is not
        # climbed (lab, 2026-11-27: the party was seen climbing the bare hull)
        self.assertNotIn(self.cell(r, sc, 11.0, 0.0, -1.0), IMPASSABLE)    # on a net
        self.assertIn(self.cell(r, sc, 9.6, 0.15, -1.0), IMPASSABLE)
        self.assertIn(self.cell(r, sc, 14.6, 0.15, -1.0), IMPASSABLE)

    def test_a_part_on_the_raised_deck_stands_at_its_height(self):
        sc = parse_scene(json.loads((AREAS / 'scenes' / 'ia0002-conves-superior.json')
                                    .read_text(encoding='utf-8')))
        wheel = next(p for p in sc.parts if p.part_id == 'leme')
        self.assertEqual(wheel.boxes[0].floor, 1.8)
        leme = next(m for m in sc.markers if m.point_id == 'leme')
        self.assertEqual((leme.x, leme.y), tuple(round(c) for c in sc.camera.project(20.8, 4.0, 1.8)))


class OpenSeaTests(unittest.TestCase):
    """ADR-0151, after the first test in game: the upper deck is bigger than the screen, handed
    over explored, and nothing on the open deck blocks the sight."""

    def test_the_explored_bitmask_size_matches_the_game(self):
        from infinity_ai.areas.are import explored_size
        # measured in a save: AR0300, AR0406, AR0069, AR0311, IA0090
        for w, h, size in ((5120, 3840, 2436), (3904, 2304, 1123), (1600, 1344, 275),
                           (832, 640, 71), (768, 576, 60)):
            self.assertEqual(explored_size(w, h), size)

    def test_the_upper_deck_is_handed_over_explored(self):
        path = AREAS / 'ia0002-conves-superior.json'
        r = parse_recipe(json.loads(path.read_text(encoding='utf-8')), path.parent)
        self.assertTrue(r.explored)
        are = build_area_files(r, bytes(r.width_px * r.height_px * 3))['IA0002.ARE']
        size, off = struct.unpack_from('<II', are, 0x9C)
        self.assertEqual(size, 618)                   # (2560/32 + 1) x (1920/32 + 1) = 4941 bits
        self.assertEqual(set(are[off:off + size]), {0xFF})

    def test_nothing_on_the_open_deck_blocks_the_sight(self):
        sc = parse_scene(json.loads((AREAS / 'scenes' / 'ia0002-conves-superior.json')
                                    .read_text(encoding='utf-8')))
        terrains = {p.terrain for p in sc.parts} | {t for p in sc.parts for _o, t, _p in p.areas}
        self.assertNotIn('obstacle', terrains)
        self.assertNotIn('wall', terrains)
        self.assertIn('open-obstacle', terrains)
