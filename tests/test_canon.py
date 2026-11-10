# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 canon pack, gate, pin and dialogue area names (synthetic + the real 1369 DR partition)."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.gate import CanonStatus, assess  # noqa: E402
from infinity_ai.canon.pack import KNOWLEDGE_ROOT, CanonError, load_partition  # noqa: E402
from infinity_ai.canon.pin import PinStatus, check_pin, pin_pack  # noqa: E402
from infinity_ai.dialogue.context import UNNAMED_AREA, Catalog  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

try:
    import jsonschema
except ImportError:
    jsonschema = None

CITY = frozenset({'AR0300', 'AR0602'})


def entry(**over):
    doc = {'schema': 'infinity-ai.canon-entry.v1', 'id': 'event:test', 'kind': 'EVENT',
           'partition_year_dr': 1369, 'title': 'Teste', 'summary': 'Resumo nosso, curto.',
           'valid_from_dr': None, 'valid_to_dr': None, 'date_precision': 'YEAR_ONLY',
           'region_id': 'region:athkatla', 'area_resrefs': [],
           'source_refs': [{'source_id': 'grand-history-of-the-realms', 'locator': 'p. 149'}],
           'verification_status': 'SOURCE_CHECKED', 'access_scope': 'CANON_REFERENCE',
           'curation': {'curated_by': 't', 'curated_at': '2026-11-09', 'checked_by': 'm',
                        'checked_at': '2026-11-09'}}
    doc.update(over)
    return doc


class TempKnowledge(unittest.TestCase):
    """A copy of the real knowledge/ tree where tests add or break entries."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'knowledge'
        shutil.copytree(KNOWLEDGE_ROOT, self.root)

    def add(self, doc, category='events', name='test'):
        path = self.root / 'periods' / '1369-DR' / category / f'{name}.json'
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        return path

    def load(self):
        return load_partition(1369, self.root)


class PackTests(TempKnowledge):
    def test_real_partition_loads_and_revision_is_stable(self):
        pack = load_partition(1369)
        self.assertTrue({'region:amn', 'region:athkatla', 'place:copper-coronet',
                         'rel:lehtinan-owns-copper-coronet',
                         'rel:bernard-manages-copper-coronet'} <= set(pack.entries))
        self.assertEqual(pack.revision, load_partition(1369).revision)

    def test_committed_checked_entries_record_who_checked(self):
        for path in (KNOWLEDGE_ROOT / 'periods').glob('*/*/*.json'):
            doc = json.loads(path.read_text(encoding='utf-8'))
            if doc['verification_status'] in ('SOURCE_CHECKED', 'CAMPAIGN_CANON'):
                with self.subTest(path=path.name):
                    self.assertTrue(doc['curation']['checked_by'])
                    self.assertTrue(doc['curation']['checked_at'])

    def test_checked_without_checker_is_refused(self):
        self.add(entry(curation={'curated_by': 't', 'curated_at': 'x', 'checked_by': None,
                                 'checked_at': None}))
        with self.assertRaises(CanonError):
            self.load()

    def test_revision_changes_with_content(self):
        before = self.load().revision
        self.add(entry())
        self.assertNotEqual(self.load().revision, before)

    def test_curation_rules_fail_closed(self):
        long_quote = '"' + ' '.join(['palavra'] * 16) + '"'
        cases = {
            'no page for S0': entry(source_refs=[{'source_id': 'grand-history-of-the-realms',
                                                  'locator': ' '}]),
            'unknown source': entry(source_refs=[{'source_id': 'random-blog', 'locator': 'x'}]),
            'long quote': entry(summary=long_quote),
            'too long': entry(summary='x' * 281),
            'wrong partition': entry(partition_year_dr=1370),
            'prefix mismatch': entry(id='char:test'),
            'checked without summary': entry(summary=''),
            'bad validity': entry(valid_from_dr=1370, valid_to_dr=1369),
        }
        for name, doc in cases.items():
            with self.subTest(name):
                path = self.add(doc)
                with self.assertRaises(CanonError):
                    self.load()
                path.unlink()

    def test_short_quotes_are_fine(self):
        self.add(entry(summary='Chamada de "a Cidade das Moedas" nos textos.'))
        self.assertIn('event:test', self.load().entries)

    def test_other_years_are_not_loaded(self):
        (self.root / 'periods' / '1370-DR' / 'events').mkdir(parents=True)
        (self.root / 'periods' / '1370-DR' / 'manifest.json').write_text(
            json.dumps({'year_dr': 1370}), encoding='utf-8')
        self.add(entry(partition_year_dr=1369))
        bad_other = self.root / 'periods' / '1370-DR' / 'events' / 'x.json'
        bad_other.write_text('{"broken": true}', encoding='utf-8')
        self.assertIn('event:test', self.load().entries)   # 1370 is never read for 1369
        with self.assertRaises(CanonError):
            load_partition(1371, self.root)

    @unittest.skipIf(jsonschema is None, 'jsonschema not installed')
    def test_committed_entries_match_the_json_schema(self):
        schema = json.loads((ROOT / 'src/infinity_ai/canon/schemas/canon_entry_v1.schema.json')
                            .read_text(encoding='utf-8'))
        validator = jsonschema.Draft202012Validator(schema)
        for path in (KNOWLEDGE_ROOT / 'periods').glob('*/*/*.json'):
            with self.subTest(path=path.name):
                validator.validate(json.loads(path.read_text(encoding='utf-8')))
        validator.validate(entry())

    def test_relationship_entries_are_typed_graph_edges(self):
        pack = load_partition(1369)
        owner = pack.get('rel:lehtinan-owns-copper-coronet')
        self.assertEqual((owner.subject_id, owner.predicate, owner.object_id),
                         ('npc:lehtinan', 'OWNER_OF', 'place:copper-coronet'))
        self.assertEqual(owner.audience, 'REGIONAL_PUBLIC')
        private = pack.get('rel:bernard-manages-copper-coronet')
        self.assertEqual(private.audience, 'AFFILIATED')
        self.assertIn('place:copper-coronet:STAFF', private.eligible_affiliations)

    def test_maintainer_curated_source_requires_campaign_canon(self):
        source = [{'source_id': 'maintainer-curation', 'locator': 'decisão aprovada'}]
        self.add(entry(id='event:maintainer-ok', verification_status='CAMPAIGN_CANON',
                       source_refs=source), name='maintainer-ok')
        self.add(entry(id='event:maintainer-no', verification_status='SOURCE_CHECKED',
                       source_refs=source), name='maintainer-no')
        pack = self.load()
        build_areas = frozenset(a for e in pack.entries.values() for a in e.area_resrefs)
        self.assertEqual(assess(pack, 'event:maintainer-ok', campaign_year=1369,
                                build_areas=build_areas).status, CanonStatus.CANON_OK)
        self.assertEqual(assess(pack, 'event:maintainer-no', campaign_year=1369,
                                build_areas=build_areas).status, CanonStatus.WEAK_SOURCE)



class GateTests(TempKnowledge):
    def test_research_only_is_never_canon(self):
        pack = load_partition(1369)
        for entry_id, e in pack.entries.items():
            if e.verification_status not in ('SOURCE_CHECKED', 'CAMPAIGN_CANON'):
                with self.subTest(entry_id=entry_id):
                    self.assertNotEqual(assess(pack, entry_id, campaign_year=1369,
                                               build_areas=CITY).status, CanonStatus.CANON_OK)

    def test_checked_entry_in_mapped_region_is_canon(self):
        self.add(entry())
        result = assess(self.load(), 'event:test', campaign_year=1369, build_areas=CITY)
        self.assertEqual(result.status, CanonStatus.CANON_OK)

    def test_refusals(self):
        self.add(entry())
        self.add(entry(id='event:research', verification_status='RESEARCH_ONLY'), name='r')
        self.add(entry(id='event:later', valid_from_dr=1370), name='later')
        self.add(entry(id='event:fr3e', source_refs=[{'source_id': 'fr-campaign-setting-3e',
                                                      'locator': 'p. 5'}]), name='fr3e')
        self.add(entry(id='event:fr3e-dated', valid_from_dr=1360, valid_to_dr=1372,
                       source_refs=[{'source_id': 'fr-campaign-setting-3e', 'locator': 'p. 5'}]),
                 name='fr3e-dated')
        self.add(entry(id='event:nowhere', region_id='region:nowhere'), name='nowhere')
        self.add(entry(id='event:loi', source_refs=[{'source_id': 'lands-of-intrigue',
                                                     'locator': 'Livro Dois, p. 7'}]), name='loi')
        self.add(entry(id='event:loi-dated', valid_from_dr=1369, valid_to_dr=1370,
                       source_refs=[{'source_id': 'lands-of-intrigue',
                                     'locator': 'Livro Dois, p. 7'}]), name='loi-dated')
        pack = self.load()
        cases = {
            ('event:missing', 1369, CITY): CanonStatus.UNKNOWN,
            ('event:test', 1370, CITY): CanonStatus.WRONG_YEAR,
            ('event:later', 1369, CITY): CanonStatus.WRONG_YEAR,
            ('event:test', 1369, frozenset({'AR9999'})): CanonStatus.UNMAPPED_REGION,
            ('event:test', 1369, None): CanonStatus.UNKNOWN,
            ('event:research', 1369, CITY): CanonStatus.WEAK_SOURCE,
            ('event:fr3e', 1369, CITY): CanonStatus.WEAK_SOURCE,   # set in 1372, no validity
            ('event:fr3e-dated', 1369, CITY): CanonStatus.CANON_OK,
            ('event:nowhere', 1369, CITY): CanonStatus.UNKNOWN,
            ('event:loi', 1369, CITY): CanonStatus.WEAK_SOURCE,        # book's present is 1370
            ('event:loi-dated', 1369, CITY): CanonStatus.CANON_OK,
        }
        for (entry_id, year, areas), expected in cases.items():
            with self.subTest(entry_id=entry_id, year=year):
                self.assertEqual(assess(pack, entry_id, campaign_year=year,
                                        build_areas=areas).status, expected)


class PinTests(TempKnowledge):
    def test_pin_is_explicit_and_detects_changes(self):
        store = CampaignStore.open(Path(self.tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(store.close)
        pack = self.load()
        self.assertEqual(check_pin(store, ROOT_BRANCH, pack), PinStatus.NOT_PINNED)
        pin_pack(store, ROOT_BRANCH, pack)
        _, created = pin_pack(store, ROOT_BRANCH, pack)
        self.assertFalse(created)
        self.assertEqual(check_pin(store, ROOT_BRANCH, pack), PinStatus.MATCH)
        self.add(entry())
        self.assertEqual(check_pin(store, ROOT_BRANCH, self.load()), PinStatus.REVISION_CHANGED)


class DialogueAreaNameTests(unittest.TestCase):
    def test_game_names_win_then_curated_then_unnamed(self):
        catalog = Catalog.load(game_area_names={'AR0300': 'Docas'})
        self.assertEqual(catalog.area('AR0300'), 'Docas')
        self.assertEqual(catalog.area('AR0602'), 'a masmorra de Irenicus')
        self.assertEqual(catalog.area('AR9999'), UNNAMED_AREA)
        self.assertEqual(Catalog.load().area('AR0300'), UNNAMED_AREA)

    def test_curated_names_file_is_unchanged_by_game_names(self):
        before = copy.deepcopy(Catalog.load().area_names)
        Catalog.load(game_area_names={'AR0602': 'Outro nome'})
        self.assertEqual(Catalog.load().area_names, before)


if __name__ == '__main__':
    unittest.main()
