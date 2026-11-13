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
    AREA_TYPE, CRE_TYPE, NO_STRREF, WMP_TYPE, parse_are_actors, parse_biff_header,
    parse_cre_identity, parse_key, parse_tlk_header, parse_wmp,
)
from infinity_ai.gamedata.inventory import (  # noqa: E402
    INVENTORY_SCHEMA, RESIDENTS_SCHEMA, build_inventory, build_residents, load_local_names,
    load_local_residents, write_inventory,
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


def build_cre(name_strref, script, ea=128, general=1, race=0, klass=0, gender=0, alignment=0,
              wisdom=0, intelligence=0, charisma=0, morale=0, morale_break=0):
    c = bytearray(0x2D4)
    c[0:8] = b'CRE V1.0'
    struct.pack_into('<I', c, 0x08, name_strref)
    c[0x270] = ea
    c[0x271] = general
    c[0x272], c[0x273], c[0x275], c[0x27B] = race, klass, gender, alignment
    c[0x23B], c[0x23A] = wisdom, intelligence
    c[0x23E], c[0x23F], c[0x240] = charisma, morale, morale_break
    c[0x280:0x280 + len(script)] = script.encode('latin-1')
    return bytes(c)


def build_are(actors):
    """actors: (name, cre_resref, embedded_cre_bytes_or_None)."""
    head = bytearray(0x11C)
    head[0:8] = b'AREAV1.0'
    table_off = len(head)
    blob_off = table_off + 0x110 * len(actors)
    table, blob = b'', b''
    for name, cre, emb in actors:
        a = bytearray(0x110)
        a[0:len(name)] = name.encode('latin-1')
        a[0x80:0x80 + len(cre)] = cre.encode('latin-1')
        if emb is not None:
            struct.pack_into('<I', a, 0x28, 1)
            struct.pack_into('<2I', a, 0x88, blob_off + len(blob), len(emb))
            blob += emb
        table += bytes(a)
    struct.pack_into('<I', head, 0x54, table_off)
    struct.pack_into('<H', head, 0x58, len(actors))
    return bytes(head) + table + blob


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


class ResidentFormatTests(unittest.TestCase):
    def test_actors_and_identity(self):
        emb = build_cre(7, 'Guard01', 128)
        actors = parse_are_actors(build_are([('Bernard', 'BERNAR', None), ('Guard', '', emb)]))
        self.assertEqual([(a.actor_name, a.cre_resref, a.embedded is None) for a in actors],
                         [('Bernard', 'BERNAR', True), ('Guard', '', False)])
        ident = parse_cre_identity(build_cre(3, 'Bernard', 128, 2, race=1, klass=2, gender=1,
                                             alignment=0x22, wisdom=14, intelligence=16,
                                             charisma=17, morale=12, morale_break=6))
        self.assertEqual((ident.wisdom, ident.intelligence), (14, 16))
        self.assertEqual((ident.charisma_base, ident.morale_default, ident.morale_break_base),
                         (17, 12, 6))
        zeroed = parse_cre_identity(build_cre(4, 'ZeroStats'))
        self.assertEqual((zeroed.charisma_base, zeroed.morale_default, zeroed.morale_break_base),
                         (0, 0, 0))
        self.assertEqual((ident.name_strref, ident.script_name, ident.allegiance, ident.general),
                         (3, 'Bernard', 128, 2))
        self.assertEqual((ident.race, ident.klass, ident.gender, ident.alignment),
                         (1, 2, 1, 0x22))
        self.assertEqual(parse_cre_identity(build_cre(3, 'None')).script_name, '')
        self.assertIsNone(parse_cre_identity(build_cre(NO_STRREF, 'x')).name_strref)

    def test_bad_are_and_cre(self):
        broken = bytearray(build_are([('A', 'X', None)]))
        struct.pack_into('<H', broken, 0x58, 500)
        for parser, data in ((parse_are_actors, b'AREAV9.9' + bytes(100)),
                             (parse_are_actors, bytes(broken)),
                             (parse_cre_identity, b'CRE V1.0' + bytes(10)),
                             (parse_cre_identity, b'CRE V9.0' + bytes(0x2D4))):
            with self.subTest(parser=parser.__name__), self.assertRaises(GameDataError):
                parser(data)


class ResidentInventoryTests(unittest.TestCase):
    """AR0406 with Bernard (BIF), a commoner without script, an embedded guard; AR0300 with an
    override CRE that also stands in AR0406."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name) / 'game'
        for d in ('data', 'lang/pt_BR', 'override'):
            (root / d).mkdir(parents=True)
        coronet = build_are([('Bernard', 'BERNAR', None), ('Plebeu', 'COMMON', None),
                             ('Guarda', '', build_cre(2, 'Guard01', 128)),
                             ('Viajante', 'TRAVEL', None)])
        docks = build_are([('Viajante', 'TRAVEL', None)])
        (root / 'data' / 'AREAS.bif').write_bytes(build_biff([
            (0, AREA_TYPE, coronet), (1, AREA_TYPE, docks),
            (2, CRE_TYPE, build_cre(0, 'Bernard', gender=1, alignment=0x22)),
            (3, CRE_TYPE, build_cre(1, ''))]))
        (root / 'chitin.key').write_bytes(build_key(['data\\AREAS.bif'], [
            ('AR0406', AREA_TYPE, 0, 0), ('AR0300', AREA_TYPE, 0, 1),
            ('BERNAR', CRE_TYPE, 0, 2), ('COMMON', CRE_TYPE, 0, 3)]))
        (root / 'override' / 'TRAVEL.CRE').write_bytes(build_cre(3, 'Traveler', 128))
        (root / 'lang' / 'pt_BR' / 'dialog.tlk').write_bytes(
            build_tlk(['Bernard', 'Plebeu', 'Guarda', 'Viajante']))
        self.source = FileSystemSource(root)

    def build(self, areas=('AR0406', 'AR0300')):
        return build_residents(self.source, language='pt_BR', build_fingerprint='sha256:' + 'ab' * 32,
                               areas=set(areas), now='2026-11-09T00:00:00Z')

    def test_residents_by_script_name(self):
        inv = self.build()
        by = {r.npc_id: r for r in inv.residents}
        self.assertEqual(set(by), {'npc:bernard', 'npc:guard01', 'npc:traveler', 'npc:cre-common'})
        self.assertEqual(by['npc:cre-common'].script_name, '')
        self.assertEqual((by['npc:bernard'].display_name, by['npc:bernard'].areas,
                          by['npc:bernard'].cre_resref), ('Bernard', ('AR0406',), 'BERNAR'))
        self.assertEqual(by['npc:traveler'].areas, ('AR0300', 'AR0406'))
        self.assertEqual(by['npc:guard01'].display_name, 'Guarda')
        self.assertEqual(inv.skipped_without_script, 0)
        self.assertEqual(inv.areas, ('AR0300', 'AR0406'))

    def test_only_requested_areas_and_unknown_areas_ignored(self):
        inv = self.build(['AR0300', 'AR9999'])
        self.assertEqual([r.npc_id for r in inv.residents], ['npc:traveler'])

    def test_written_outside_repo_and_loaded_by_fingerprint(self):
        inv = self.build()
        base = Path(self.tmp.name) / 'local-knowledge'
        doc = json.loads(write_inventory(inv, base).read_text(encoding='utf-8'))
        self.assertEqual((doc['schema'], doc['source']['kind']), (RESIDENTS_SCHEMA, 'GAME_DATA_LOCAL'))
        loaded = load_local_residents(inv.build_fingerprint, 'pt_BR', base)
        self.assertEqual(loaded['npc:bernard'].areas, ('AR0406',))
        self.assertEqual(load_local_residents('sha256:' + 'cd' * 32, 'pt_BR', base), {})
        with self.assertRaises(GameDataError):
            write_inventory(inv, ROOT / 'knowledge' / 'tmp-residents')
        self.assertFalse((ROOT / 'knowledge' / 'tmp-residents').exists())


class RepositoryHygieneTests(unittest.TestCase):
    def test_no_game_derived_inventory_is_committed(self):
        offenders = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*.json')
                     if '.git' not in p.parts and '.venv' not in p.parts
                     and any(schema in p.read_text(encoding='utf-8', errors='ignore')
                             for schema in (INVENTORY_SCHEMA, RESIDENTS_SCHEMA))]
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
