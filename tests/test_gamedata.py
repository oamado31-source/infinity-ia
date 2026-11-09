# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 game data readers and inventory, on synthetic binaries built here (never game files)."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.gamedata.formats import (  # noqa: E402
    AREA_TYPE, NO_STRREF, WMP_TYPE, parse_biff_header, parse_key, parse_tlk_header, parse_wmp,
)
from infinity_ai.gamedata.inventory import (  # noqa: E402
    INVENTORY_SCHEMA, build_inventory, load_local_names, write_inventory,
)
from infinity_ai.gamedata.source import FileSystemSource, GameDataError  # noqa: E402


def build_key(bifs, resources):
    header = 24
    bif_table = header
    names_off = bif_table + 12 * len(bifs)
    names = b''
    entries = b''
    for name in bifs:
        raw = name.encode('latin-1') + b'\0'
        entries += struct.pack('<IIHH', 0, names_off + len(names), len(raw), 0)
        names += raw
    res_off = names_off + len(names)
    res = b''.join(struct.pack('<8sHI', r.encode('latin-1'), t, (b << 20) | f)
                   for r, t, b, f in resources)
    return b'KEY V1  ' + struct.pack('<4I', len(bifs), len(resources), bif_table, res_off) + \
        entries + names + res


def build_biff(files):
    table_off = 20
    data_off = table_off + 16 * len(files)
    table, blob = b'', b''
    for index, type_, data in files:
        table += struct.pack('<IIIHH', index, data_off + len(blob), len(data), type_, 0)
        blob += data
    return b'BIFFV1  ' + struct.pack('<3I', len(files), 0, table_off) + table + blob


def build_tlk(strings):
    entries_end = 18 + 26 * len(strings)
    entries, blob = b'', b''
    for s in strings:
        raw = s.encode('utf-8')
        entries += struct.pack('<H8sIIII', 1, b'', 0, 0, len(blob), len(raw))
        blob += raw
    return b'TLK V1  ' + struct.pack('<HII', 0, len(strings), entries_end) + entries + blob


def build_wmp(maps):
    out_maps, out_areas = b'', b''
    areas_base = 16 + 0xB8 * len(maps)
    for number, name_strref, areas in maps:
        off = areas_base + len(out_areas)
        m = bytearray(0xB8)
        struct.pack_into('<2I', m, 0x10, number, name_strref)
        struct.pack_into('<2I', m, 0x20, len(areas), off)
        out_maps += bytes(m)
        for resref, caption, tooltip in areas:
            a = bytearray(0xF0)
            a[0:8] = resref.encode('latin-1').ljust(8, b'\0')
            struct.pack_into('<2I', a, 0x40, caption, tooltip)
            out_areas += bytes(a)
    return b'WMAPV1.0' + struct.pack('<2I', len(maps), 16) + out_maps + out_areas


class FakeInstall(unittest.TestCase):
    """chitin.key + one BIF with two areas and a world map, a pt_BR dialog.tlk, an override area."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'game'
        (self.root / 'data').mkdir(parents=True)
        (self.root / 'lang' / 'pt_BR').mkdir(parents=True)
        (self.root / 'override').mkdir()
        wmp = build_wmp([(0, 2, [('AR0300', 0, NO_STRREF), ('AR0700', NO_STRREF, 1)])])
        (self.root / 'data' / 'AREAS.bif').write_bytes(build_biff([
            (0, AREA_TYPE, b'ARE-0300'), (1, AREA_TYPE, b'ARE-0602'), (2, WMP_TYPE, wmp)]))
        (self.root / 'chitin.key').write_bytes(build_key(['data\\AREAS.bif'], [
            ('AR0300', AREA_TYPE, 0, 0), ('AR0602', AREA_TYPE, 0, 1),
            ('WORLDMAP', WMP_TYPE, 0, 2)]))
        (self.root / 'lang' / 'pt_BR' / 'dialog.tlk').write_bytes(
            build_tlk(['Docas', 'Passeio', 'Mapa do mundo']))
        (self.root / 'override' / 'AR9999.ARE').write_bytes(b'ARE')
        self.source = FileSystemSource(self.root)


class FormatTests(FakeInstall):
    def test_key_and_biff(self):
        key = parse_key((self.root / 'chitin.key').read_bytes())
        self.assertEqual(key.bifs[0].path, 'data/AREAS.bif')
        self.assertEqual(key.find('worldmap', WMP_TYPE).file_index, 2)
        self.assertEqual(len(key.of_type(AREA_TYPE)), 2)
        header = parse_biff_header((self.root / 'data' / 'AREAS.bif').read_bytes())
        self.assertEqual(header.file_count, 3)

    def test_tlk_and_wmp(self):
        self.assertEqual(parse_tlk_header(build_tlk(['a', 'b'])).count, 2)
        maps = parse_wmp(build_wmp([(2, NO_STRREF, [('AR0300', 5, 6)])]))
        self.assertEqual((maps[0].number, maps[0].name_strref), (2, None))
        self.assertEqual((maps[0].areas[0].resref, maps[0].areas[0].caption_strref), ('AR0300', 5))

    def test_bad_signatures_and_bounds(self):
        for parser, data in ((parse_key, b'KEY V2  ' + bytes(16)), (parse_tlk_header, b'x' * 18),
                             (parse_biff_header, b'BIF V1.0' + bytes(12)),
                             (parse_wmp, b'WMAPV2.0' + bytes(8))):
            with self.subTest(parser=parser.__name__), self.assertRaises(GameDataError):
                parser(data)
        broken = b'KEY V1  ' + struct.pack('<4I', 5, 5, 9999, 9999)
        with self.assertRaises(GameDataError):
            parse_key(broken)

    def test_source_is_read_only_and_bounded(self):
        with self.assertRaises(GameDataError):
            self.source.read('../outside', 0, 1)
        with self.assertRaises(GameDataError):
            self.source.read('chitin.key', 0, 10_000)
        self.assertIsNone(self.source.size('missing.key'))
        self.assertEqual(self.source.size('CHITIN.KEY'), self.source.size('chitin.key'))
        self.assertFalse(any(hasattr(self.source, n) for n in ('write', 'delete', 'remove')))


class InventoryTests(FakeInstall):
    def inventory(self):
        return build_inventory(self.source, language='pt_BR', build_fingerprint='sha256:' + 'ab' * 32,
                               now='2026-11-09T00:00:00Z')

    def test_areas_and_names(self):
        inv = self.inventory()
        by = {a.resref: a for a in inv.areas}
        self.assertEqual(set(by), {'AR0300', 'AR0602', 'AR0700', 'AR9999'})
        self.assertEqual(by['AR0300'].display_name, 'Docas')
        self.assertEqual(by['AR0700'].display_name, 'Passeio')   # tooltip fallback
        self.assertIsNone(by['AR0602'].display_name)             # not on the world map: no guess
        self.assertTrue(by['AR9999'].in_override)
        self.assertEqual(inv.worldmaps, (0,))

    def test_override_world_map_wins(self):
        (self.root / 'override' / 'WORLDMAP.WMP').write_bytes(
            build_wmp([(0, 2, [('AR0602', 2, NO_STRREF)])]))
        names = self.inventory().names()
        self.assertEqual(names, {'AR0602': 'Mapa do mundo'})

    def test_write_outside_repo_and_load_by_fingerprint(self):
        inv = self.inventory()
        base = Path(self.tmp.name) / 'local-knowledge'
        path = write_inventory(inv, base)
        doc = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual((doc['schema'], doc['source']['kind']), (INVENTORY_SCHEMA, 'GAME_DATA_LOCAL'))
        self.assertEqual(load_local_names(inv.build_fingerprint, 'pt_BR', base)['AR0300'], 'Docas')
        self.assertEqual(load_local_names('sha256:' + 'cd' * 32, 'pt_BR', base), {})
        self.assertEqual(load_local_names(inv.build_fingerprint, 'en_US', base), {})

    def test_refuses_to_write_inside_the_repository(self):
        with self.assertRaises(GameDataError):
            write_inventory(self.inventory(), ROOT / 'knowledge' / 'tmp-inventory')
        self.assertFalse((ROOT / 'knowledge' / 'tmp-inventory').exists())


class RepositoryHygieneTests(unittest.TestCase):
    def test_no_game_derived_inventory_is_committed(self):
        offenders = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*.json')
                     if '.git' not in p.parts and '.venv' not in p.parts
                     and INVENTORY_SCHEMA in p.read_text(encoding='utf-8', errors='ignore')]
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
