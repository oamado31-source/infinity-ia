# SPDX-License-Identifier: Apache-2.0
"""CR-2026-012: the Faerûn root region, regions off the game map, and what travel teaches."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.canon.gate import CanonStatus, assess  # noqa: E402
from infinity_ai.canon.pack import WORLD_REGION, load_partition  # noqa: E402
from infinity_ai.memory.common_knowledge import (  # noqa: E402
    identity_knowledge, local_aliases, region_chain,
)
from infinity_ai.personality.identity import build_identity, generate_identity  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH  # noqa: E402
from test_canon import TempKnowledge  # noqa: E402

PACK = load_partition(1369)
BUILD = frozenset(a for e in PACK.entries.values() for a in e.area_resrefs)


def off_map_region(region_id='region:waterdeep', parent=WORLD_REGION):
    doc = json.loads((ROOT / 'knowledge/periods/1369-DR/regions/faerun.json').read_text(
        encoding='utf-8'))
    doc.update(id=region_id, title='Águas Profundas', region_id=parent,
               summary='Região de teste fora do mapa do jogo.',
               knowledge_layers={'POPULAR': 'Região de teste fora do mapa do jogo.'})
    return doc


class RootTests(unittest.TestCase):
    def test_amn_and_tethyr_hang_below_the_root(self):
        self.assertEqual(region_chain(PACK, 'region:athkatla'),
                         ['region:athkatla', 'region:amn', WORLD_REGION])
        self.assertEqual(region_chain(PACK, 'region:tethyr'), ['region:tethyr', WORLD_REGION])
        self.assertIs(assess(PACK, WORLD_REGION, campaign_year=1369, build_areas=BUILD).status,
                      CanonStatus.CANON_OK)

    def test_city_and_realm_are_not_the_world(self):
        aliases = local_aliases(PACK, 'AR0406')
        self.assertEqual(aliases['cidade'], 'Athkatla')
        self.assertEqual(aliases['reino'], 'Amn')

    def test_nobody_is_from_or_lives_in_faerun(self):
        for i in range(60):
            g = generate_identity(npc_id=f'npc:generated:enc-{i}', role='PATRON', gender=1,
                                  home_region='region:athkatla', pack=PACK, world_seed='w',
                                  campaign_id='lab', branch_id=ROOT_BRANCH)
            self.assertNotEqual(g['origin_region'], WORLD_REGION)
            self.assertNotIn(WORLD_REGION, g['places_visited'])
        ident = build_identity(npc_id='npc:cre-x', name='X', pack=PACK, place='a Coroa de Cobre',
                               home_region='region:athkatla',
                               resident=SimpleNamespace(gender=1, race=1, klass=0,
                                                        display_name='X'),
                               generated={'origin_region': 'region:athkatla', 'born_here': True,
                                          'places_visited': [], 'standing': 'HABITANTE'})
        self.assertNotIn('Faerûn', ident.home_names)
        self.assertEqual(ident.home_names, ('Athkatla', 'Amn'))


class OffMapTests(TempKnowledge):
    def test_off_map_region_below_the_root_passes_the_gate(self):
        path = self.root / 'periods' / '1369-DR' / 'regions' / 'waterdeep.json'
        path.write_text(json.dumps(off_map_region(), ensure_ascii=False), encoding='utf-8')
        pack = self.load()
        self.assertIs(assess(pack, 'region:waterdeep', campaign_year=1369,
                             build_areas=BUILD).status, CanonStatus.CANON_OK)

    def test_region_without_areas_outside_the_world_stays_unmapped(self):
        path = self.root / 'periods' / '1369-DR' / 'regions' / 'nowhere.json'
        path.write_text(json.dumps(off_map_region('region:nowhere', None), ensure_ascii=False),
                        encoding='utf-8')
        pack = self.load()
        self.assertIs(assess(pack, 'region:nowhere', campaign_year=1369,
                             build_areas=BUILD).status, CanonStatus.UNMAPPED_REGION)


class TravelTests(unittest.TestCase):
    def known(self, standing='HABITANTE', homeland=None, visited=()):
        return identity_knowledge(PACK, homeland=homeland, home='region:athkatla',
                                  campaign_year=1369, build_areas=BUILD, standing=standing,
                                  visited=visited)

    def test_a_trip_gives_only_the_popular_core(self):
        full, shallow = self.known()
        self.assertNotIn('region:tethyr', full + shallow)
        full, shallow = self.known(visited=('region:tethyr',))
        self.assertIn('region:tethyr', shallow)
        self.assertIn('event:tethyr-reclamation-wars-end', shallow)
        self.assertNotIn('region:tethyr', full)

    def test_home_or_homeland_beats_a_trip(self):
        full, shallow = self.known(homeland='region:tethyr', visited=('region:tethyr',))
        self.assertIn('region:tethyr', full)
        self.assertNotIn('region:tethyr', shallow)
        full, shallow = self.known(visited=('region:athkatla', WORLD_REGION))
        self.assertIn('org:council-of-six', full)
        self.assertNotIn('org:council-of-six', shallow)

    def test_the_whole_continent_knows_the_world_level(self):
        for standing, homeland in (('HABITANTE', None), ('VIAJANTE', 'region:amn'),
                                   ('FORASTEIRO', 'region:tethyr')):
            with self.subTest(standing=standing):
                full, _ = self.known(standing, homeland)
                self.assertIn(WORLD_REGION, full)


if __name__ == '__main__':
    unittest.main()
