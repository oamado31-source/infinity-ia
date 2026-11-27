# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the area recipe, the test room and every named error of the checker."""
import copy
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.areas import AreaError  # noqa: E402
from infinity_ai.areas.build import build_area_files, manifest  # noqa: E402
from infinity_ai.areas.check import check_area  # noqa: E402
from infinity_ai.areas.maps import search_map  # noqa: E402
from infinity_ai.areas.recipe import parse_recipe  # noqa: E402

RECIPE = ROOT / 'knowledge' / 'areas' / 'ia0090-sala-de-teste.json'
SCHEMA = ROOT / 'knowledge' / 'areas' / 'area-recipe.v1.schema.json'


def doc():
    return json.loads(RECIPE.read_text(encoding='utf-8'))


def codes(report):
    return [c for c, _ in report.errors]


class TestRoomTests(unittest.TestCase):
    def test_the_schema_accepts_the_test_room(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest('jsonschema not installed')
        jsonschema.validate(doc(), json.loads(SCHEMA.read_text(encoding='utf-8')))

    def test_the_test_room_builds_and_passes_with_no_warning(self):
        recipe = parse_recipe(doc())
        files = build_area_files(recipe)
        self.assertEqual(sorted(files), ['I009000.PVRZ', 'IA0090.ARE', 'IA0090.MOS',
                                         'IA0090.TIS', 'IA0090.WED', 'IA0090HT.BMP',
                                         'IA0090LM.BMP', 'IA0090SR.BMP'])
        report = check_area(recipe, files, {'AR0310', 'A031000'})
        self.assertEqual((report.errors, report.warnings), ([], []))

    def test_the_same_recipe_gives_the_same_bytes_and_a_traceable_manifest(self):
        recipe = parse_recipe(doc())
        a, b = build_area_files(recipe), build_area_files(recipe)
        self.assertEqual(a, b)
        m = json.loads(manifest(RECIPE.read_bytes(), recipe, a))
        self.assertEqual(m['area'], 'IA0090')
        self.assertEqual(sorted(m['files']), sorted(a))
        self.assertEqual(len(m['recipe_sha256']), 64)

    def test_the_pillar_blocks_and_hides(self):
        recipe = parse_recipe(doc())
        from infinity_ai.areas.build import terrain_codes
        mw, _mh, sr = terrain_codes(recipe)
        self.assertEqual(sr[(340 // 12) * mw + 384 // 16], 0)      # the pillar's foot
        self.assertEqual(sr[(300 // 12) * mw + 384 // 16], 2)      # behind it: wood
        self.assertEqual(sr[(500 // 12) * mw + 384 // 16], 2)      # the entrance
        # the wall's baseline (its first two points) is the pillar's foot (lab, 2026-11-27)
        self.assertEqual([s.points() for _i, s in recipe.walls][0][:2], ((352, 375), (415, 375)))


_BUILT = {}


class CheckerErrorTests(unittest.TestCase):
    def built(self, d=None):
        """The test room (built once, copied per test) or a changed recipe."""
        if d is not None:
            recipe = parse_recipe(d)
            return recipe, build_area_files(recipe)
        if not _BUILT:
            recipe = parse_recipe(doc())
            _BUILT['r'], _BUILT['f'] = recipe, build_area_files(recipe)
        return _BUILT['r'], dict(_BUILT['f'])

    def test_area_name_taken_or_not_ours(self):
        recipe, files = self.built()
        self.assertIn('AREA_NAME', codes(check_area(recipe, files, {'IA0090'})))
        d = doc()
        d['area'] = 'AR0090'
        with self.assertRaises(AreaError) as cm:
            parse_recipe(d)
        self.assertEqual(cm.exception.code, 'AREA_NAME')

    def test_page_name_taken(self):
        recipe, files = self.built()
        self.assertIn('PAGE_NAME', codes(check_area(recipe, files, {'I009000'})))

    def test_wed_overlays(self):
        recipe, files = self.built()
        wed = bytearray(files['IA0090.WED'])
        struct.pack_into('<I', wed, 8, 4)
        files['IA0090.WED'] = bytes(wed)
        self.assertIn('WED_OVERLAYS', codes(check_area(recipe, files)))

    def test_map_size(self):
        recipe, files = self.built()
        files['IA0090SR.BMP'] = search_map([2] * (40 * 40), 40, 40)
        self.assertIn('MAP_SIZE', codes(check_area(recipe, files)))

    def test_tile_count(self):
        recipe, files = self.built()
        tis = bytearray(files['IA0090.TIS'])
        struct.pack_into('<I', tis, 8, 100)
        files['IA0090.TIS'] = bytes(tis)
        self.assertIn('TILE_COUNT', codes(check_area(recipe, files)))

    def test_entrance_blocked(self):
        d = doc()
        d['entrances'][0].update(x=384, y=560)                       # on the south border
        recipe, files = self.built(d)
        self.assertIn('ENTRANCE_BLOCKED', codes(check_area(recipe, files)))

    def test_no_path(self):
        d = doc()
        d['regions'].append({'id': 'divisoria', 'rect': [32, 400, 704, 24], 'terrain': 'wall'})
        d['passages'].append({'id': 'fundo', 'x': 200, 'y': 200})
        recipe, files = self.built(d)
        self.assertIn('NO_PATH', codes(check_area(recipe, files)))

    def test_missing_ref(self):
        recipe, files = self.built()
        are = bytearray(files['IA0090.ARE'])
        are[8:16] = b'AR0310\0\0'
        files['IA0090.ARE'] = bytes(are)
        self.assertIn('MISSING_REF', codes(check_area(recipe, files)))
        recipe, files = self.built()
        del files['I009000.PVRZ']
        self.assertIn('MISSING_REF', codes(check_area(recipe, files)))

    def test_wall_outside(self):
        d = doc()
        d['walls'].append({'id': 'fora', 'rect': [700, 500, 200, 200]})
        with self.assertRaises(AreaError) as cm:
            parse_recipe(d)
        self.assertEqual(cm.exception.code, 'WALL_OUTSIDE')

    def test_no_walls_and_big_area_are_warnings(self):
        d = copy.deepcopy(doc())
        d['walls'] = []
        recipe, files = self.built(d)
        report = check_area(recipe, files)
        self.assertTrue(report.ok)
        self.assertEqual([c for c, _ in report.warnings], ['NO_WALLS'])

    def test_a_wall_whose_baseline_is_its_top_is_warned(self):
        d = doc()
        d['walls'] = [{'id': 'pilar', 'polygon': [[352, 192], [415, 192], [415, 375], [352, 375]]}]
        recipe, files = self.built(d)
        self.assertIn('WALL_BASELINE', [c for c, _ in check_area(recipe, files).warnings])

    def test_unknown_fields_and_render_are_refused_for_now(self):
        d = doc()
        d['picture'] = {'kind': 'render'}
        with self.assertRaises(AreaError):
            parse_recipe(d)
        d = doc()
        d['extra'] = 1
        with self.assertRaises(AreaError):
            parse_recipe(d)


if __name__ == '__main__':
    unittest.main()
