# SPDX-License-Identifier: Apache-2.0
"""CR-2026-014: what fills the prompt is chosen by closeness, never alphabetically nor by the
player's words."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import MAX_KNOWLEDGE, Catalog, build_resident_context  # noqa: E402
from infinity_ai.memory.common_knowledge import context_order  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

PACK = load_partition(1369)
BERNARD = 'npc:cre-bernard'


def order(npc_id=BERNARD, area='AR0406', home='region:athkatla'):
    return context_order(PACK, PACK.entries, npc_id=npc_id, area=area, home_region=home)


class OrderTests(unittest.TestCase):
    def test_own_ties_then_the_place_then_the_city_then_the_realm(self):
        ranked = order()
        self.assertEqual(ranked[0], 'rel:bernard-manages-copper-coronet')    # restricted tie
        self.assertEqual(set(ranked[1:3]), {'place:copper-coronet',
                                            'rel:lehtinan-owns-copper-coronet'})
        pos = {e: i for i, e in enumerate(ranked)}
        self.assertLess(pos['region:athkatla'], pos['region:amn'])           # city, then realm,
        self.assertLess(pos['region:amn'], pos['region:faerun'])             # then the world,
        self.assertLess(pos['region:faerun'], pos['region:tethyr'])          # then off the chain

    def test_levels_take_turns_so_the_city_does_not_fill_the_prompt(self):
        top = order()[:12]
        self.assertIn('org:council-of-six', top)                             # city
        self.assertIn('org:cowled-wizards', top)                             # realm
        self.assertLess(sum(e.startswith('place:') for e in top), 4)

    def test_standing_things_before_events_and_recent_events_first(self):
        pos = {e: i for i, e in enumerate(order())}
        self.assertLess(pos['org:cowled-wizards'], pos['event:coast-plague'])
        self.assertLess(pos['topic:amnian-currency'], pos['event:coast-plague'])
        self.assertLess(pos['event:baldurs-gate-crisis'], pos['event:coast-plague'])   # 1368, 1345
        self.assertLess(pos['event:coast-plague'], pos['event:magic-ban-of-king-dhanar'])

    def test_pure_and_deterministic(self):
        self.assertEqual(order(), order())
        self.assertEqual(sorted(order()), sorted(PACK.entries))
        self.assertEqual(context_order(PACK, reversed(sorted(PACK.entries)), npc_id=BERNARD,
                                       area='AR0406', home_region='region:athkatla'), order())


class PromptTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def ctx(self, ranked):
        known = tuple((e.id, e.title, e.summary, e.layers, e.access_scope, e.subject_id,
                       e.secrecy) for e in PACK.entries.values())
        return build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id=BERNARD,
            display_name='Bernard', residence_areas=('AR0406',), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, also_known=known, order=ranked).context

    def test_the_tavern_and_the_tie_reach_the_prompt_before_old_history(self):
        context = self.ctx(tuple(order()))
        ids = [k.event_id for k in context.knowledge + context.restricted_knowledge]
        self.assertEqual(len(ids), MAX_KNOWLEDGE)
        for entry in ('rel:bernard-manages-copper-coronet', 'place:copper-coronet',
                      'rel:lehtinan-owns-copper-coronet', 'region:athkatla',
                      'org:council-of-six', 'org:cowled-wizards'):
            self.assertIn(f'canon:{entry}', ids)
        self.assertNotIn('canon:event:magic-ban-of-king-dhanar', ids)

    def test_without_an_order_ties_first_and_events_last(self):
        context = self.ctx(())
        ids = [k.event_id for k in context.knowledge + context.restricted_knowledge]
        self.assertIn('canon:rel:bernard-manages-copper-coronet', ids)
        self.assertIn('canon:place:copper-coronet', ids)
        self.assertFalse(any(i.startswith('canon:event:') for i in ids))


if __name__ == '__main__':
    unittest.main()
