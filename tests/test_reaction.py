# SPDX-License-Identifier: Apache-2.0
"""ADR-0125: encounter reaction (DMG Table 59 + PHB Table 6), decided by code, once per session."""
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import Catalog, build_resident_context  # noqa: E402
from infinity_ai.dialogue.engine import system_prompt  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.personality.reaction import (  # noqa: E402
    REACTION_EVENT, TABLE_59, charisma_adjustment, classify_conduct, lookup, reaction_for,
    resolve_reaction,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

PACK = load_partition(1369)


class TableTests(unittest.TestCase):
    def test_table_59_rows_and_columns(self):
        self.assertEqual(sorted(TABLE_59), list(range(2, 21)))
        self.assertEqual(lookup(2, 'FRIENDLY'), 'FRIENDLY')
        self.assertEqual(lookup(2, 'HOSTILE'), 'FLIGHT')
        self.assertEqual(lookup(20, 'FRIENDLY'), 'HOSTILE')
        self.assertEqual((lookup(7, 'FRIENDLY'), lookup(8, 'FRIENDLY')), ('FRIENDLY', 'INDIFFERENT'))
        self.assertEqual(lookup(7, 'INDIFFERENT'), 'INDIFFERENT')
        self.assertEqual(lookup(12, 'INDIFFERENT'), 'CAUTIOUS')
        self.assertEqual((lookup(15, 'INDIFFERENT'), lookup(16, 'THREATENING')),
                         ('THREATENING', 'HOSTILE'))
        self.assertEqual(lookup(4, 'THREATENING'), 'CAUTIOUS')
        self.assertEqual(lookup(19, 'FRIENDLY'), 'HOSTILE')
        self.assertEqual(lookup(-3, 'INDIFFERENT'), 'FRIENDLY')     # totals clamp to 2..20
        self.assertEqual(lookup(31, 'INDIFFERENT'), 'HOSTILE')

    def test_charisma_adjustment_and_sign(self):
        self.assertEqual([charisma_adjustment(c) for c in (3, 8, 12, 13, 16, 18)],
                         [-5, 0, 0, 1, 5, 7])
        self.assertEqual(charisma_adjustment(None), 0)
        plain = resolve_reaction('INDIFFERENT', 10, random.Random(4))
        charming = resolve_reaction('INDIFFERENT', 16, random.Random(4))
        self.assertEqual(charming.dice, plain.dice)
        self.assertEqual(charming.total, plain.total - 5)          # +5 improves: subtracted

    def test_conduct_from_the_opening_words(self):
        self.assertEqual(classify_conduct('Olá, bom dia!'), 'FRIENDLY')
        self.assertEqual(classify_conduct('Quem governa Amn?'), 'INDIFFERENT')
        self.assertEqual(classify_conduct('Me diga agora, senão vai se arrepender.'),
                         'THREATENING')
        self.assertEqual(classify_conduct('Seu idiota, fale logo!'), 'HOSTILE')
        self.assertEqual(classify_conduct('Conte ou te machuco.'), 'THREATENING')
        self.assertEqual(classify_conduct(''), 'INDIFFERENT')


class EventTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def react(self, session=0, text='Quem governa Amn?', key='npc:cre-bernard', chr_=None):
        return reaction_for(self.store, ROOT_BRANCH, key=key, session=session,
                            opening_text=text, charisma=chr_, charisma_of='jaheira',
                            world_seed='w', game_time=100)

    def test_once_per_session_and_deterministic(self):
        first = self.react(text='Olá!')
        again = self.react(text='Seu idiota!', chr_=18)          # same session: not re-rolled
        self.assertTrue(again.reused)
        self.assertEqual((again.disposition, again.dice, again.conduct),
                         (first.disposition, first.dice, 'FRIENDLY'))
        other = self.react(session=1, text='Olá!')               # new session: new encounter
        self.assertFalse(other.reused)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        twin = CampaignStore.open(Path(tmp.name) / 'twin.sqlite3', 'lab')
        self.addCleanup(twin.close)
        same = reaction_for(twin, ROOT_BRANCH, key='npc:cre-bernard', session=0,
                            opening_text='Olá!', charisma=None, charisma_of='jaheira',
                            world_seed='w', game_time=100)
        self.assertEqual((same.dice, same.disposition), (first.dice, first.disposition))

    def test_event_carries_no_text(self):
        self.react(text='Seu idiota, quem governa Amn?')
        events = self.store.visible_events(ROOT_BRANCH, REACTION_EVENT)
        self.assertEqual(len(events), 1)
        payload = json.dumps(events[0].payload, ensure_ascii=False)
        self.assertNotIn('idiota', payload)
        self.assertNotIn('governa', payload)
        self.assertEqual(events[0].payload['rule'], 'DMG2e-T59+PHB2e-T6')
        self.assertIsNone(reaction_for(self.store, ROOT_BRANCH, key='', session=0,
                                       opening_text='x', charisma=None, charisma_of='',
                                       world_seed='w', game_time=1))


class DispositionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        council = PACK.get('org:council-of-six')
        bernard = PACK.get('rel:bernard-manages-copper-coronet')
        self.known = (
            ('org:council-of-six', council.title, council.summary, council.layers),
            ('rel:bernard-manages-copper-coronet', bernard.title, bernard.summary,
             bernard.layers, 'RESTRICTED', bernard.subject_id))

    def ctx(self, disposition):
        return build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:cre-x',
            display_name='Salvanas', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, also_known=self.known,
            disposition=disposition).context

    def test_what_each_disposition_tells(self):
        friendly = self.ctx('FRIENDLY')
        self.assertEqual((len(friendly.knowledge), len(friendly.restricted_knowledge)), (1, 1))
        cautious = self.ctx('CAUTIOUS')
        self.assertEqual((len(cautious.knowledge), len(cautious.restricted_knowledge)), (1, 0))
        self.assertNotIn('Bernard', cautious.vocabulary)
        for closed in ('THREATENING', 'HOSTILE', 'FLIGHT'):
            context = self.ctx(closed)
            self.assertEqual((context.knowledge, context.restricted_knowledge), ((), ()))
            self.assertNotIn('Conselho', context.vocabulary)
        self.assertIn('Disposição neste encontro: você desconfia do jogador', system_prompt(cautious))
        self.assertNotIn('Disposição neste encontro', system_prompt(self.ctx(None)))


if __name__ == '__main__':
    unittest.main()
