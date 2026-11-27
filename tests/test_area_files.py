# SPDX-License-Identifier: Apache-2.0
"""ADR-0149: the files of a new area, written by us, read back; and the TIS of the BIF's tileset
table. Synthetic data only (never game files)."""
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.areas import AreaError  # noqa: E402
from infinity_ai.areas.are import Entrance, build_are, read_are_summary  # noqa: E402
from infinity_ai.areas.dxt import decode_dxt1, encode_dxt1  # noqa: E402
from infinity_ai.areas.maps import build_bmp, map_size, read_bmp  # noqa: E402
from infinity_ai.areas.mos import build_mos, minimap_size, read_mos_size  # noqa: E402
from infinity_ai.areas.png import write_png  # noqa: E402
from infinity_ai.areas.tis import (  # noqa: E402
    build_tis, page_name, read_pvrz, read_tis, render_tis,
)
from infinity_ai.areas.wed import Wall, build_wed, group_grid, read_wed  # noqa: E402
from infinity_ai.gamedata.formats import TIS_TYPE  # noqa: E402
from infinity_ai.gamedata.inventory import _Resources  # noqa: E402
from infinity_ai.gamedata.source import FileSystemSource  # noqa: E402
from test_gamedata import build_key  # noqa: E402


def gradient(w, h):
    return bytes(v for y in range(h) for x in range(w)
                 for v in (x * 255 // max(1, w - 1), y * 255 // max(1, h - 1), (x + y) % 256))


def psnr(a, b):
    err = sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)
    return 99.0 if err == 0 else 10 * math.log10(255 * 255 / err)


class DxtTests(unittest.TestCase):
    def test_a_solid_block_comes_back_exactly_in_565(self):
        rgb = bytes((80, 120, 40) * 16)
        out = decode_dxt1(encode_dxt1(rgb, 4, 4), 4, 4)
        self.assertEqual(set(zip(out[0::3], out[1::3], out[2::3])), {(82, 121, 41)})

    def test_a_smooth_picture_survives_compression(self):
        rgb = gradient(64, 64)
        self.assertGreater(psnr(rgb, decode_dxt1(encode_dxt1(rgb, 64, 64), 64, 64)), 30)

    def test_the_four_colour_mode_is_always_used(self):
        data = encode_dxt1(gradient(32, 32), 32, 32)
        for i in range(0, len(data), 8):
            c0, c1 = struct.unpack_from('<HH', data, i)
            self.assertGreaterEqual(c0, c1)

    def test_size_must_be_blocks(self):
        with self.assertRaises(AreaError):
            encode_dxt1(bytes(3 * 6 * 4), 6, 4)


class TisTests(unittest.TestCase):
    def test_page_names_follow_the_tis_name(self):
        self.assertEqual(page_name('IA0090', 0), 'I009000')
        self.assertEqual(page_name('AR0310', 1), 'A031001')

    def test_a_small_area_fits_one_power_of_two_page(self):
        rgb = gradient(12 * 64, 9 * 64)
        tis, pages = build_tis('IA0090', rgb, 12, 9)
        self.assertEqual(list(pages), ['I009000'])
        w, h, page = read_pvrz(pages['I009000'])
        self.assertEqual((w, h), (1024, 512))
        entries = read_tis(tis)
        self.assertEqual(len(entries), 108)
        self.assertEqual(entries[13], (0, 64 * 13, 0))
        self.assertEqual(entries[16], (0, 0, 64))
        back = render_tis(entries, {0: (w, h, page)}, 12, 9)
        self.assertGreater(psnr(rgb, back), 30)

    def test_a_larger_area_takes_more_pages(self):
        tis, pages = build_tis('IA0091', bytes(17 * 64 * 17 * 64 * 3), 17, 17)
        self.assertEqual(sorted(pages), ['I009100', 'I009101'])
        self.assertEqual(read_tis(tis)[256], (1, 0, 0))


class WedTests(unittest.TestCase):
    def test_five_overlays_one_tile_per_cell_and_walls_in_their_groups(self):
        walls = [Wall(((352, 192), (415, 192), (415, 375), (352, 375))),
                 Wall(((700, 500), (760, 500), (760, 560)))]
        info = read_wed(build_wed('IA0090', 12, 9, walls))
        self.assertEqual(len(info.overlays), 5)
        self.assertEqual(info.overlays[0], (12, 9, 'IA0090'))
        self.assertEqual(info.overlays[1:], ((0, 0, ''),) * 4)
        self.assertEqual(info.lookup, tuple(range(108)))
        self.assertEqual([w.points for w in info.walls], [w.points for w in walls])
        self.assertEqual(group_grid(12, 9), (2, 2))
        self.assertEqual(info.groups, ((0,), (), (), (1,)))
        self.assertEqual(info.doors, 0)

    def test_a_wall_needs_three_points(self):
        with self.assertRaises(AreaError) as cm:
            build_wed('IA0090', 2, 2, [Wall(((0, 0), (10, 10)))])
        self.assertEqual(cm.exception.code, 'WALL_OUTSIDE')


class MapTests(unittest.TestCase):
    def test_map_size_is_one_pixel_per_16x12(self):
        self.assertEqual(map_size(768, 576), (48, 48))
        self.assertEqual(map_size(1856, 2240), (116, 187))

    def test_bmp_round_trip_4_and_8_bits(self):
        px = [i % 16 for i in range(7 * 5)]
        self.assertEqual(read_bmp(build_bmp(px, 7, 5, 4, [(0, 0, 0)] * 16)), (7, 5, 4, px))
        px8 = [i % 200 for i in range(9 * 3)]
        self.assertEqual(read_bmp(build_bmp(px8, 9, 3, 8, [(0, 0, 0)] * 256)), (9, 3, 8, px8))

    def test_minimap_is_the_area_at_one_in_6_4(self):
        self.assertEqual(minimap_size(1280, 960), (200, 150))
        self.assertEqual(minimap_size(768, 576), (120, 90))
        mos = build_mos(gradient(128, 128), 128, 128)
        self.assertEqual(read_mos_size(mos), (20, 20))


class AreTests(unittest.TestCase):
    def test_an_empty_room_with_its_entrance(self):
        data = build_are('IA0090', 'interior', [Entrance('Entrada', 384, 500, 8)])
        self.assertEqual(len(data), 0x11C + 0x68 + 0x90 + 0xE4)
        s = read_are_summary(data)
        self.assertEqual((s['wed'], s['type'], s['script']), ('IA0090', 0, ''))
        self.assertEqual(s['entrances'], (Entrance('Entrada', 384, 500, 8),))
        self.assertEqual([s[k] for k in ('actors', 'regions', 'spawns', 'containers', 'items',
                                         'ambients', 'doors', 'animations')], [0] * 8)
        songs = struct.unpack_from('<I', data, 0xBC)[0]
        self.assertEqual(struct.unpack_from('<10I', data, songs), (0,) * 5 + (0xFFFFFFFF,) * 5)

    def test_only_our_names(self):
        with self.assertRaises(AreaError) as cm:
            build_are('AR0310', 'interior', [Entrance('E', 1, 1)])
        self.assertEqual(cm.exception.code, 'AREA_NAME')


class PngTests(unittest.TestCase):
    def test_png_signature_and_size(self):
        png = write_png(bytes(2 * 3 * 3), 2, 3)
        self.assertTrue(png.startswith(b'\x89PNG'))
        self.assertEqual(struct.unpack('>II', png[16:24]), (2, 3))


def build_biff_with_tiles(files, tilesets):
    """BIFF V1 with a file table and a tileset table (TIS without header)."""
    head = 20
    tiles_off = head + 16 * len(files)
    data_off = tiles_off + 20 * len(tilesets)
    table, tset, blob = b'', b'', b''
    for index, type_, data in files:
        table += struct.pack('<IIIHH', index, data_off + len(blob), len(data), type_, 0)
        blob += data
    for index, count, data in tilesets:
        tset += struct.pack('<IIIIHH', index << 14, data_off + len(blob), count, 12, TIS_TYPE, 0)
        blob += data
    return b'BIFFV1  ' + struct.pack('<3I', len(files), len(tilesets), head) + table + tset + blob


class TilesetTableTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / 'data').mkdir()
        tiles = struct.pack('<6I', 0, 0, 0, 0, 64, 0)
        (root / 'data' / 'AREA.bif').write_bytes(build_biff_with_tiles(
            [(0, 0x004, b'OggS-not-a-tis')], [(1, 2, tiles)]))
        (root / 'chitin.key').write_bytes(build_key(['data\\AREA.bif'], [
            ('SND01', 0x004, 0, 0), ('AR0001', TIS_TYPE, 0, 1 << 14)]))
        self.res = _Resources(FileSystemSource(root))

    def test_a_tis_comes_from_the_tileset_table_with_its_header(self):
        data = self.res.tis('AR0001')
        self.assertTrue(data.startswith(b'TIS V1  '))
        self.assertEqual(read_tis(data), [(0, 0, 0), (0, 64, 0)])
        self.assertEqual(self.res.get('AR0001', TIS_TYPE, 'tis'), data)

    def test_a_tis_is_never_taken_from_the_file_table(self):
        self.assertIsNone(self.res.locate('AR0001', TIS_TYPE, 'tis', set()))
        self.assertEqual(self.res.get('SND01', 0x004, 'wav'), b'OggS-not-a-tis')


if __name__ == '__main__':
    unittest.main()
