# SPDX-License-Identifier: Apache-2.0
"""CR-2026-015: someone of a realm knows the popular core of its cities, not what is inside them."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.memory.common_knowledge import identity_knowledge, realm_of  # noqa: E402
from test_canon import TempKnowledge  # noqa: E402

PACK = load_partition(1369)


def build(pack):
    return frozenset(a for e in pack.entries.values() for a in e.area_resrefs)


def known(pack, **kw):
    return identity_knowledge(pack, campaign_year=1369, build_areas=build(pack), **kw)


class SiblingTests(TempKnowledge):
    def test_realm(self):
        self.assertEqual(realm_of(PACK, 'region:athkatla'), 'region:amn')
        self.assertEqual(realm_of(PACK, 'region:murann'), 'region:amn')
        self.assertEqual(realm_of(PACK, 'region:amn'), 'region:amn')
        self.assertIsNone(realm_of(PACK, 'region:faerun'))
        self.assertIsNone(realm_of(PACK, 'region:rashemen'))

    def test_a_resident_knows_the_popular_core_of_the_other_cities(self):
        full, popular = known(PACK, homeland=None, home='region:athkatla')
        self.assertIn('region:murann', popular)
        self.assertIn('region:trademeet', popular)
        self.assertNotIn('region:murann', full)                 # the detail needs more

    def test_born_in_the_realm_also_knows_them_but_outsiders_do_not(self):
        _, popular = known(PACK, homeland='region:murann', home='region:tethyr',
                           standing='FORASTEIRO')
        self.assertIn('region:crimmor', popular)
        full, popular = known(PACK, homeland='region:tethyr', home='region:athkatla',
                              standing='FORASTEIRO')
        self.assertNotIn('region:crimmor', set(full) | set(popular))
        full, popular = known(PACK, homeland='region:tethyr', home='region:athkatla',
                              standing='VIAJANTE')
        self.assertNotIn('region:crimmor', set(full) | set(popular))

    def test_only_the_city_itself_not_what_is_inside_it(self):
        doc = json.loads((self.root / 'periods/1369-DR/places/copper-coronet.json').read_text(
            encoding='utf-8'))
        doc.update(id='place:moonmaiden-hall', title='Salão da Donzela da Lua',
                   region_id='region:murann', area_resrefs=[],
                   summary='Templo de teste em Murann.',
                   knowledge_layers={'POPULAR': 'Templo de teste em Murann.'})
        self.add(doc, 'places', 'moonmaiden-hall')
        pack = self.load()
        full, popular = known(pack, homeland=None, home='region:athkatla')
        self.assertIn('region:murann', popular)
        self.assertNotIn('place:moonmaiden-hall', set(full) | set(popular))
        _, popular = known(pack, homeland='region:tethyr', home='region:tethyr',
                           standing='FORASTEIRO', visited=('region:murann',))
        self.assertIn('place:moonmaiden-hall', popular)         # been there: it does


if __name__ == '__main__':
    unittest.main()
