# SPDX-License-Identifier: Apache-2.0
"""SPEC-012 / CR-2026-030: curated encyclopedia records and the local census (synthetic data)."""
import copy
import json
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.encyclopedia.catalog import (  # noqa: E402
    DEFAULT_BASE, load_manifest, load_records, problems,
)
from infinity_ai.gamedata.census import (  # noqa: E402
    CENSUS_SCHEMA, CHARACTER, CREATURE, build_census, census_report, write_census,
)
from infinity_ai.gamedata.formats import AREA_TYPE, CRE_TYPE, DLG_TYPE  # noqa: E402
from infinity_ai.gamedata.source import FileSystemSource, GameDataError  # noqa: E402
from test_gamedata import build_are, build_biff, build_cre, build_key, build_tlk  # noqa: E402

try:
    import jsonschema  # type: ignore
except ImportError:  # optional, like lupa
    jsonschema = None


def schema_check(doc, schema):
    validator = jsonschema.Draft202012Validator(schema)
    return [f'{"/".join(map(str, e.path)) or "(raiz)"}: {e.message}'
            for e in validator.iter_errors(doc)]


@unittest.skipIf(jsonschema is None, 'jsonschema not installed')
class RecordTests(unittest.TestCase):
    def test_schemas_are_valid_and_the_records_pass(self):
        manifest = load_manifest()
        for cat in manifest['categories']:
            schema = json.loads((DEFAULT_BASE / cat['schema']).read_text(encoding='utf-8'))
            jsonschema.Draft202012Validator.check_schema(schema)
        self.assertEqual(problems(schema_check=schema_check), [])

    def test_every_curated_npc_has_a_record_pointing_to_its_curation(self):
        curations = {p.name: json.loads(p.read_text(encoding='utf-8'))['npc_id']
                     for p in (ROOT / 'knowledge' / 'npcs').glob('*.json')}
        pointed = {}
        for rec in load_records():
            ref = (rec.doc.get('refs') or {}).get('curation')
            if ref:
                pointed[Path(ref).name] = rec.canonical_id
        self.assertEqual(set(pointed), set(curations))

    def copy_base(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name) / 'knowledge' / 'encyclopedia'
        base.mkdir(parents=True)
        for name in ('manifest.json', 'sources.json'):
            shutil.copy(DEFAULT_BASE / name, base / name)
        shutil.copytree(DEFAULT_BASE / 'schemas', base / 'schemas')
        (base / 'characters' / 'bg2').mkdir(parents=True)
        good = json.loads((DEFAULT_BASE / 'characters' / 'bg2' / 'yarin.json').read_text())
        good.pop('refs')
        return base, good

    def write(self, base, name, doc, folder='characters/bg2'):
        (base / folder / f'{name}.json').write_text(json.dumps(doc), encoding='utf-8')

    def test_extracted_attributes_duplicates_and_broken_links_are_reported(self):
        base, good = self.copy_base()
        self.write(base, 'ok', good)
        self.assertEqual(problems(base, schema_check=schema_check), [])
        stats = copy.deepcopy(good)
        stats['canonical_id'] = 'character:teste-stats'
        stats['hit_points'] = 30                     # an extracted attribute (CR-2026-030)
        self.write(base, 'stats', stats)
        twin = copy.deepcopy(good)                   # same canonical_id as "ok"
        self.write(base, 'twin', twin)
        linked = copy.deepcopy(good)
        linked['canonical_id'] = 'character:teste-link'
        linked['relationships'] = [{'type': 'KNOWS', 'target': 'character:ninguem'},
                                   {'type': 'KNOWS', 'target': 'pending:character:depois'}]
        self.write(base, 'linked', linked)
        odd = copy.deepcopy(good)
        odd['canonical_id'] = 'character:teste-fonte'
        odd['source_refs'] = ['fonte-inventada']
        self.write(base, 'odd', odd)
        found = '\n'.join(problems(base, schema_check=schema_check))
        self.assertIn('hit_points', found)
        self.assertIn('canonical_id repetido', found)
        self.assertIn("relação para 'character:ninguem'", found)
        self.assertNotIn('depois', found)
        self.assertIn("fonte desconhecida 'fonte-inventada'", found)

    def test_category_prefix_and_directory_must_agree(self):
        base, good = self.copy_base()
        wrong = copy.deepcopy(good)
        wrong['canonical_id'] = 'creature:yarin'
        self.write(base, 'wrong', wrong)
        (base / 'items').mkdir()
        self.write(base, 'misplaced', dict(good, canonical_id='character:outro'), folder='items')
        found = '\n'.join(problems(base, schema_check=schema_check))
        self.assertIn('não começa com character:', found)
        self.assertIn('fora de characters/', found)

    def test_curated_records_need_a_summary_and_a_curation(self):
        base, good = self.copy_base()
        bare = copy.deepcopy(good)
        bare.pop('curation')
        self.write(base, 'bare', bare)
        self.assertTrue(any('curation' in p for p in problems(base, schema_check=schema_check)))


def actor_place(are: bytes, index: int, x: int, y: int, schedule: int) -> bytes:
    data = bytearray(are)
    base = struct.unpack_from('<I', data, 0x54)[0] + 0x110 * index
    struct.pack_into('<HH', data, base + 0x20, x, y)
    struct.pack_into('<I', data, base + 0x40, schedule)
    return bytes(data)


def with_dialog(cre: bytes, dialog: str) -> bytes:
    data = bytearray(cre)
    data[0x2CC:0x2CC + len(dialog)] = dialog.encode('latin-1')
    return bytes(data)


def dlg(*actions: str) -> bytes:
    head = bytearray(0x30)
    head[:8] = b'DLG V1.0'
    table_at = len(head)
    texts_at = table_at + 8 * len(actions)
    table, blob = b'', b''
    for a in actions:
        raw = a.encode('latin-1')
        table += struct.pack('<II', texts_at + len(blob), len(raw))
        blob += raw
    struct.pack_into('<II', head, 0x28, table_at, len(actions))
    return bytes(head) + table + blob


class CensusTests(unittest.TestCase):
    """Two invented areas: a tavern keeper who sells, a scripted guard, a nameless wolf, a
    commoner with a dialogue; the guard stands in both areas."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name) / 'game'
        for d in ('data', 'lang/pt_BR', 'override'):
            (root / d).mkdir(parents=True)
        tavern = build_are([('Taverneiro', 'TKEEP', None), ('Guarda', 'TGUARD', None),
                            ('Lobo', 'TWOLF', None), ('Plebeu', 'TPLEB', None),
                            ('Dragao', 'TDRAG', None)])
        tavern = actor_place(tavern, 0, 300, 400, 0xFFFFFF)
        tavern = actor_place(tavern, 1, 10, 20, 0x00FF00)
        road = actor_place(build_are([('Guarda', 'TGUARD', None)]), 0, 50, 60, 0xFFFFFF)
        (root / 'data' / 'TEST.bif').write_bytes(build_biff([
            (0, AREA_TYPE, tavern), (1, AREA_TYPE, road),
            (2, CRE_TYPE, with_dialog(build_cre(0, ''), 'TKEEPD')),
            (3, CRE_TYPE, build_cre(1, 'TGuard01')),
            (4, CRE_TYPE, build_cre(2, '', general=2)),
            (5, CRE_TYPE, with_dialog(build_cre(3, ''), 'TPLEBD')),
            (6, DLG_TYPE, dlg('StartStore("TSTORE",LastTalkedToBy())')),
            (7, DLG_TYPE, dlg('SetGlobal("x","LOCALS",1)')),
            (8, CRE_TYPE, with_dialog(build_cre(4, 'TDragon', general=2), 'TPLEBD'))]))
        (root / 'chitin.key').write_bytes(build_key(['data\\TEST.bif'], [
            ('AR9101', AREA_TYPE, 0, 0), ('AR9102', AREA_TYPE, 0, 1),
            ('TKEEP', CRE_TYPE, 0, 2), ('TGUARD', CRE_TYPE, 0, 3), ('TWOLF', CRE_TYPE, 0, 4),
            ('TPLEB', CRE_TYPE, 0, 5), ('TKEEPD', DLG_TYPE, 0, 6), ('TPLEBD', DLG_TYPE, 0, 7),
            ('TDRAG', CRE_TYPE, 0, 8)]))
        (root / 'lang' / 'pt_BR' / 'dialog.tlk').write_bytes(
            build_tlk(['Taverneiro de Teste', 'Guarda de Teste', 'Lobo', 'Plebeu de Teste',
                       'Dragão de Teste']))
        self.source = FileSystemSource(root)

    def census(self):
        return build_census(self.source, language='pt_BR', build_fingerprint='sha256:' + 'ab' * 32,
                            now='2026-11-18T00:00:00Z')

    def test_characters_creatures_places_and_stores(self):
        by = {e.entry_id: e for e in self.census().entries}
        self.assertEqual(set(by), {'npc:cre-tkeep', 'npc:tguard01', 'npc:cre-twolf',
                                   'npc:cre-tpleb', 'npc:tdragon'})
        self.assertEqual(by['npc:tdragon'].kind, CHARACTER)   # named, scripted, talks: someone
        keeper, guard, wolf = by['npc:cre-tkeep'], by['npc:tguard01'], by['npc:cre-twolf']
        self.assertEqual((keeper.kind, keeper.sells, keeper.dialog), (CHARACTER, True, 'TKEEPD'))
        self.assertEqual((keeper.appearances[0].x, keeper.appearances[0].y,
                          len(keeper.appearances[0].hours)), (300, 400, 24))
        self.assertEqual(guard.kind, CHARACTER)               # a script name makes it someone
        self.assertEqual([a.area for a in guard.appearances], ['AR9101', 'AR9102'])
        self.assertEqual(guard.appearances[0].hours, tuple(range(8, 16)))
        self.assertEqual(wolf.kind, CREATURE)                 # not humanoid
        self.assertEqual((by['npc:cre-tpleb'].kind, by['npc:cre-tpleb'].sells), (CHARACTER, False))

    def test_idempotent_local_and_never_in_the_repository(self):
        first, second = self.census(), self.census()
        self.assertEqual(first, second)
        base = Path(self.tmp.name) / 'local'
        doc = json.loads(write_census(first, base).read_text(encoding='utf-8'))
        self.assertEqual((doc['schema'], doc['source']['kind']), (CENSUS_SCHEMA, 'GAME_DATA_LOCAL'))
        self.assertEqual(len(doc['entries']), 5)
        with self.assertRaises(GameDataError):
            write_census(first, ROOT / 'knowledge' / 'tmp-census')
        self.assertFalse((ROOT / 'knowledge' / 'tmp-census').exists())

    def test_only_some_areas(self):
        census = build_census(self.source, language='pt_BR', build_fingerprint='sha256:' + 'ab' * 32,
                              areas={'AR9102', 'AR0000'}, now='2026-11-18T00:00:00Z')
        self.assertEqual(([e.entry_id for e in census.entries], census.areas),
                         (['npc:tguard01'], ('AR9102',)))

    def test_report_counts_curated_and_queues_the_rest(self):
        report = census_report(self.census(), curated={'npc:tguard01'},
                               area_names={'AR9101': 'Taverna de Teste'})
        self.assertIn('4 personagens, 1 criaturas', report)
        self.assertIn('| AR9101 | Taverna de Teste | 4 | 3 | 1 |', report)
        self.assertIn('| 1 | Taverneiro de Teste (`npc:cre-tkeep`) | AR9101 | sim | sim |', report)
        self.assertNotIn('Guarda de Teste (`npc:tguard01`)', report)   # already curated


class HygieneTests(unittest.TestCase):
    def test_no_census_is_committed(self):
        offenders = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*.json')
                     if '.git' not in p.parts and '.venv' not in p.parts
                     and CENSUS_SCHEMA in p.read_text(encoding='utf-8', errors='ignore')]
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
