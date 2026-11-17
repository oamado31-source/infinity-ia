# SPDX-License-Identifier: Apache-2.0
"""Etapa 3: the named people of the Copper Coronet and the arena secrets (ADR-0119, ADR-0131)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.disclosure import decide  # noqa: E402
from infinity_ai.personality.identity import load_curations  # noqa: E402

PACK = load_partition(1369)
CUR = load_curations(PACK)
STAFF, REGULAR = 'place:copper-coronet:STAFF', 'place:copper-coronet:REGULAR'


class CurationTests(unittest.TestCase):
    def test_the_house_people_are_staff_and_the_patrons_regulars(self):
        for npc in ('npc:lehtinan', 'npc:madam', 'npc:cre-copgreet', 'npc:announcer', 'npc:beast',
                    'npc:copguard1', 'npc:copguard', 'npc:guard3', 'npc:escort4'):
            self.assertIn(STAFF, CUR[npc].affiliations, npc)
        for npc in ('npc:rumar', 'npc:priss', 'npc:tiana', 'npc:yarin', 'npc:llynis', 'npc:drunk1',
                    'npc:zaviera', 'npc:amalas', 'npc:scdur', 'npc:surly'):
            self.assertEqual(CUR[npc].affiliations, (REGULAR,), npc)
        for npc in ('npc:hendak', 'npc:gpshout'):      # slaves: no tie to the house
            self.assertEqual(CUR[npc].affiliations, (), npc)
            self.assertTrue(any('escravo' in f for f in CUR[npc].self_facts), npc)


class ArenaSecretTests(unittest.TestCase):
    def test_the_arena_is_house_business_and_the_slaves_a_confidential_secret(self):
        arena, slaves = PACK.get('rel:lehtinan-runs-arena'), PACK.get('rel:arena-slaves')
        self.assertEqual((arena.secrecy, arena.eligible_affiliations), ('PROFESSIONAL', (STAFF, REGULAR)))
        self.assertEqual((slaves.secrecy, slaves.eligible_affiliations), ('CONFIDENTIAL', (STAFF,)))
        open_staff = decide(slaves.id, access_scope='RESTRICTED', secrecy='CONFIDENTIAL',
                            disposition='FRIENDLY')
        self.assertFalse(open_staff.allowed)                  # no trust yet: never told
        self.assertTrue(decide(arena.id, access_scope='RESTRICTED', secrecy='PROFESSIONAL',
                               disposition='FRIENDLY').allowed)


if __name__ == '__main__':
    unittest.main()
