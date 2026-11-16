# SPDX-License-Identifier: Apache-2.0
"""CR-2026-021: someone of a realm knows the popular core of the realm next door, not its cities."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.canon.pack import CanonError, load_partition  # noqa: E402
from infinity_ai.memory.common_knowledge import identity_knowledge  # noqa: E402
from test_canon import TempKnowledge  # noqa: E402

PACK = load_partition(1369)


class NeighborTests(TempKnowledge):
    def manifest(self, pairs):
        path = self.root / 'periods' / '1369-DR' / 'manifest.json'
        doc = json.loads(path.read_text(encoding='utf-8'))
        if pairs is None:
            doc.pop('realm_neighbors', None)
        else:
            doc['realm_neighbors'] = pairs
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')

    def known(self, pack, **kw):
        build = frozenset(a for e in pack.entries.values() for a in e.area_resrefs)
        return identity_knowledge(pack, campaign_year=1369, build_areas=build, **kw)

    def test_the_curated_pairs_are_symmetric(self):
        self.assertEqual(PACK.neighbors['region:amn'],
                         frozenset({'region:tethyr', 'region:sword-coast', 'region:calimshan'}))
        self.assertEqual(PACK.neighbors['region:tethyr'],
                         frozenset({'region:amn', 'region:calimshan'}))
        self.assertEqual(PACK.neighbors['region:sword-coast'], frozenset({'region:amn'}))

    def test_only_realms_below_the_root_can_be_neighbours(self):
        for pairs in ([['region:amn', 'region:athkatla']], [['region:amn', 'region:faerun']],
                      [['region:amn', 'region:nowhere']], [['region:amn']], 'region:amn'):
            with self.subTest(pairs=pairs):
                self.manifest(pairs)
                with self.assertRaises(CanonError):
                    self.load()

    def test_the_pairs_are_part_of_the_pinned_revision(self):
        self.manifest(None)
        without = self.load()
        self.manifest([['region:amn', 'region:tethyr']])
        self.assertNotEqual(without.revision, self.load().revision)
        self.assertEqual(without.neighbors, {})

    def test_the_realm_next_door_gives_its_popular_core_only(self):
        full, popular = self.known(PACK, homeland=None, home='region:athkatla')
        self.assertIn('region:tethyr', popular)
        self.assertIn('event:tethyr-reclamation-wars-end', popular)
        self.assertNotIn('region:tethyr', full)

    def test_not_the_cities_of_the_realm_next_door(self):
        full, popular = self.known(PACK, homeland='region:tethyr', home='region:tethyr')
        self.assertIn('region:amn', popular)
        for city in ('region:athkatla', 'region:murann', 'org:council-of-six'):
            with self.subTest(city=city):
                self.assertNotIn(city, full + popular)

    def test_a_neighbour_of_a_neighbour_is_not_next_door(self):
        full, popular = self.known(PACK, homeland='region:tethyr', home='region:tethyr')
        self.assertNotIn('region:sword-coast', full + popular)

    def test_without_pairs_nothing_changes(self):
        self.manifest(None)
        pack = self.load()
        full, popular = self.known(pack, homeland=None, home='region:athkatla')
        self.assertNotIn('region:tethyr', full + popular)
