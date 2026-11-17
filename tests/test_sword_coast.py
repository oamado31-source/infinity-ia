# SPDX-License-Identifier: Apache-2.0
"""Lote D: the Sword Coast, its cities and places, named in Portuguese or in English."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.gate import CanonStatus, assess  # noqa: E402
from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.memory.common_knowledge import identity_knowledge, named_in, realm_of  # noqa: E402

PACK = load_partition(1369)
BUILD = frozenset(a for e in PACK.entries.values() for a in e.area_resrefs)
LOTE_D = {e.id for e in PACK.entries.values()
          if e.region_id in ('region:sword-coast', 'region:baldurs-gate', 'region:beregost')
          or e.id == 'region:sword-coast'} - {'org:iron-throne', 'char:larloch'}   # those are lote F


def known(**kw):
    return identity_knowledge(PACK, campaign_year=1369, build_areas=BUILD, **kw)


class SwordCoastTests(unittest.TestCase):
    def test_the_lote_passes_the_gate(self):
        self.assertEqual(len(LOTE_D), 15)
        for entry_id in LOTE_D:
            with self.subTest(entry=entry_id):
                gate = assess(PACK, entry_id, campaign_year=1369, build_areas=BUILD)
                self.assertIs(gate.status, CanonStatus.CANON_OK)

    def test_a_realm_beside_amn(self):
        self.assertEqual(PACK.get('region:sword-coast').region_id, 'region:faerun')
        self.assertEqual(realm_of(PACK, 'region:baldurs-gate'), 'region:sword-coast')
        self.assertEqual(realm_of(PACK, 'region:nashkel'), 'region:amn')

    def test_either_name_finds_the_entry(self):
        """Maintainer, 2026-11-16: a player may ask in Portuguese or in English."""
        cases = {
            'place:candlekeep': ('Já esteve em Candlekeep?', 'E a Fortaleza da Vela?'),
            'region:baldurs-gate': ("Conhece Baldur's Gate?", 'E o Portão de Baldur?',
                                    'Já foi ao Portal de Baldur?', 'Baldurs Gate é longe?'),
            'region:sword-coast': ('O que sabe da Sword Coast?', 'E da Costa da Espada?'),
            'place:friendly-arm': ('E o Friendly Arm?', 'Dormiu no Braço Amigo?'),
            'org:flaming-fist': ('Quem é o Flaming Fist?', 'E o Punho Flamejante?'),
            'place:dragonspear-castle': ('Dragonspear ainda existe?', 'E a Lança do Dragão?'),
            'region:cloud-peaks': ('Já cruzou as Cloud Peaks?', 'E os Picos das Nuvens?'),
        }
        for entry_id, questions in cases.items():
            for question in questions:
                with self.subTest(question=question):
                    self.assertIn(entry_id, named_in(PACK, PACK.entries, question))

    def test_a_resident_of_beregost_knows_the_coast(self):
        full, _ = known(homeland=None, home='region:beregost')
        self.assertTrue({'region:sword-coast', 'region:beregost', 'place:ulcasters-school',
                         'place:candlekeep', 'place:friendly-arm', 'event:iron-throne-plot'} <= set(full))
        self.assertNotIn('org:flaming-fist', full)              # inside Baldur's Gate

    def test_someone_from_baldurs_gate_in_athkatla(self):
        full, popular = known(homeland='region:baldurs-gate', home='region:athkatla')
        self.assertTrue({'region:baldurs-gate', 'org:flaming-fist', 'place:elfsong-tavern'} <= set(full))
        self.assertTrue({'region:sword-coast', 'region:beregost', 'region:scornubel'} <= set(popular))
        self.assertNotIn('place:candlekeep', full + popular)     # origin knows its city and below

    def test_amn_knows_only_the_popular_core_of_the_coast_next_door(self):
        full, popular = known(homeland='region:athkatla', home='region:athkatla')
        self.assertFalse(LOTE_D & set(full))
        coast_level = {e for e in LOTE_D if e == 'region:sword-coast'
                       or (PACK.get(e).kind != 'REGION'
                           and PACK.get(e).region_id == 'region:sword-coast')}
        self.assertEqual(LOTE_D & set(popular), coast_level)    # CR-2026-021: not its cities


if __name__ == '__main__':
    unittest.main()
