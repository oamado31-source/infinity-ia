# SPDX-License-Identifier: Apache-2.0
"""CR-2026-013: the TOPIC kind (customs, coins, speech, religion) known by the regional rules."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.canon.gate import CanonStatus, assess  # noqa: E402
from infinity_ai.canon.pack import CanonError, KIND_PREFIX  # noqa: E402
from infinity_ai.memory.common_knowledge import identity_knowledge  # noqa: E402
from test_canon import TempKnowledge  # noqa: E402

SCHEMA = ROOT / 'src/infinity_ai/canon/schemas/canon_entry_v1.schema.json'


def topic(**change):
    doc = {'schema': 'infinity-ai.canon-entry.v1', 'id': 'topic:test-coins', 'kind': 'TOPIC',
           'partition_year_dr': 1369, 'title': 'Moedas de teste',
           'summary': 'Costume de teste conhecido em Amn.', 'valid_from_dr': 1369,
           'valid_to_dr': 1370, 'date_precision': 'RANGE', 'region_id': 'region:amn',
           'area_resrefs': [], 'source_refs': [{'source_id': 'lands-of-intrigue',
                                                'locator': 'Livro Dois, p. 13'}],
           'verification_status': 'SOURCE_CHECKED', 'access_scope': 'COMMON_REGIONAL',
           'knowledge_layers': {'POPULAR': 'Costume de teste.', 'INFORMED': 'Detalhe de teste.'},
           'curation': {'curated_by': 'claude-code', 'curated_at': '2026-11-15',
                        'checked_by': 'mantenedor', 'checked_at': '2026-11-15'}}
    doc.update(change)
    return doc


class TopicTests(TempKnowledge):
    def build(self, pack):
        return frozenset(a for e in pack.entries.values() for a in e.area_resrefs)

    def test_a_topic_loads_passes_the_gate_and_is_known_by_region(self):
        self.add(topic(), 'topics', 'test-coins')
        pack = self.load()
        self.assertEqual(pack.get('topic:test-coins').kind, 'TOPIC')
        self.assertIs(assess(pack, 'topic:test-coins', campaign_year=1369,
                             build_areas=self.build(pack)).status, CanonStatus.CANON_OK)
        resident, _ = identity_knowledge(pack, homeland=None, home='region:athkatla',
                                         campaign_year=1369, build_areas=self.build(pack))
        self.assertIn('topic:test-coins', resident)
        stranger, popular = identity_knowledge(pack, homeland='region:tethyr',
                                               home='region:tethyr', campaign_year=1369,
                                               build_areas=self.build(pack))
        self.assertNotIn('topic:test-coins', stranger)
        self.assertIn('topic:test-coins', popular)          # CR-2026-021: Amn is next door
        _, visited = identity_knowledge(pack, homeland='region:tethyr', home='region:tethyr',
                                        campaign_year=1369, build_areas=self.build(pack),
                                        visited=('region:amn',))
        self.assertIn('topic:test-coins', visited)          # travel: the popular core only

    def test_a_topic_needs_a_region_and_has_no_areas(self):
        for change in ({'region_id': None}, {'area_resrefs': ['AR0406']},
                       {'id': 'event:test-coins'}):
            with self.subTest(change=change):
                self.setUp()
                self.add(topic(**change), 'topics', 'test-coins')
                with self.assertRaises(CanonError):
                    self.load()

    def test_a_topic_is_not_a_relationship_end(self):
        rel = json.loads((self.root / 'periods/1369-DR/relationships/'
                          'lehtinan-owns-copper-coronet.json').read_text(encoding='utf-8'))
        rel.update(id='rel:test-topic', object_id='topic:test-coins')
        self.add(topic(), 'topics', 'test-coins')
        self.add(rel, 'relationships', 'test-topic')
        with self.assertRaises(CanonError):
            self.load()

    def test_schema_knows_the_kind(self):
        self.assertEqual(KIND_PREFIX['TOPIC'], 'topic')
        try:
            import jsonschema
        except ImportError:
            self.skipTest('jsonschema not installed')
        schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
        jsonschema.validate(topic(), schema)
        for change in ({'region_id': None}, {'area_resrefs': ['AR0406']}):
            with self.subTest(change=change), self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(topic(**change), schema)


if __name__ == '__main__':
    unittest.main()
