# SPDX-License-Identifier: Apache-2.0
"""ADR-0126: morale check in dialogue (DMG ch. 9, Tables 49-50), decided by code."""
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
from infinity_ai.personality.identity import CURATION_SCHEMA, load_curations  # noqa: E402
from infinity_ai.personality.morale import (  # noqa: E402
    MORALE_EVENT, base_morale, classify_trigger, ethical_axis, modifiers, morale_for,
    resolve_morale,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

PACK = load_partition(1369)


class RuleTests(unittest.TestCase):
    def test_base_morale_by_role_and_curation(self):
        self.assertEqual(base_morale('GUARD'), 12)
        self.assertEqual(base_morale('FIGHTER'), 12)
        self.assertEqual(base_morale('PATRON'), 7)
        self.assertEqual(base_morale(None), 7)
        self.assertEqual(base_morale('PATRON', curated=14), 14)
        self.assertEqual(base_morale('GUARD', curated=99), 12)          # out of range ignored

    def test_modifiers_apply_once(self):
        self.assertEqual(modifiers(ethical='LAWFUL', text='Por favor, te pago bem.'),
                         (('lawful', 1), ('favored', 2)))
        self.assertEqual(modifiers(ethical='CHAOTIC', text='Fale ou eu te mato!'),
                         (('chaotic', -1), ('poorly_treated', -4)))
        self.assertEqual(modifiers(ethical=None, text='Quem governa?'), ())
        self.assertEqual(modifiers(ethical=None, text='Conte ou te machuco.',
                                   trigger='INTIMIDATION'), (('poorly_treated', -4),))
        self.assertEqual(ethical_axis(0x11), 'LAWFUL')
        self.assertEqual(ethical_axis(None, {'alignment_initial': {'ethical': 'CHAOTIC'}}),
                         'CHAOTIC')
        self.assertIsNone(ethical_axis(None))

    def test_hold_at_or_below_morale_yield_above(self):
        for seed in range(40):
            result = resolve_morale('BRIBE', 7, (('favored', 2),), random.Random(seed))
            self.assertEqual(result.morale, 9)
            self.assertEqual(result.outcome, 'HOLD' if result.total <= 9 else 'YIELD')

    def test_triggers(self):
        self.assertEqual(classify_trigger('Te pago 10 moedas se me disser.'), 'BRIBE')
        self.assertEqual(classify_trigger('Fale ou eu te mato!'), 'INTIMIDATION')
        self.assertEqual(classify_trigger('Me ajude a roubar o Lehtinan.', ['Lehtinan']),
                         'BETRAYAL')
        self.assertIsNone(classify_trigger('Me ajude a roubar o Lehtinan.', []))   # not tied
        self.assertIsNone(classify_trigger('Quem governa Amn?', ['Lehtinan']))


class EventTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def check(self, trigger='BRIBE', session=0, base=7):
        return morale_for(self.store, ROOT_BRANCH, key='npc:cre-x', session=session,
                          trigger=trigger, base=base, mods=(('favored', 2),), world_seed='w',
                          game_time=10)

    def test_once_per_trigger_per_session_without_text(self):
        first = self.check()
        again = self.check(base=20)                      # same trigger, same session: reused
        self.assertTrue(again.reused)
        self.assertEqual((again.outcome, again.dice, again.morale),
                         (first.outcome, first.dice, first.morale))
        self.assertFalse(self.check(trigger='INTIMIDATION').reused)
        self.assertFalse(self.check(session=1).reused)
        events = self.store.visible_events(ROOT_BRANCH, MORALE_EVENT)
        self.assertEqual(len(events), 3)
        self.assertEqual(set(events[0].payload), {'npc_key', 'session', 'trigger', 'outcome',
                                                  'dice', 'base', 'modifiers', 'morale',
                                                  'total', 'rule', 'policy'})


class CurationTests(unittest.TestCase):
    def test_curated_morale_is_read_and_checked(self):
        with tempfile.TemporaryDirectory() as d:
            base = {'schema': CURATION_SCHEMA, 'npc_id': 'npc:x', 'occupation': None,
                    'origin_region': None, 'places_visited': [], 'self_facts': [],
                    'curation': {'checked_by': 'mantenedor', 'checked_at': '2026-11-13'}}
            (Path(d) / 'x.json').write_text(json.dumps({**base, 'morale': 15}))
            self.assertEqual(load_curations(PACK, Path(d))['npc:x'].morale, 15)
            (Path(d) / 'x.json').write_text(json.dumps({**base, 'morale': 30}))
            self.assertEqual(load_curations(PACK, Path(d)), {})


class EffectTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        bernard = PACK.get('rel:bernard-manages-copper-coronet')
        self.known = (('rel:bernard-manages-copper-coronet', bernard.title, bernard.summary,
                       bernard.layers, 'RESTRICTED', bernard.subject_id),)

    def ctx(self, morale):
        return build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:cre-x',
            display_name='Salvanas', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, also_known=self.known,
            disposition='CAUTIOUS', morale=morale).context

    def test_yield_tells_what_caution_hid_and_hold_keeps_it(self):
        self.assertEqual(len(self.ctx(None).restricted_knowledge), 0)
        self.assertEqual(len(self.ctx(('BETRAYAL', 'HOLD')).restricted_knowledge), 0)
        gave_in = self.ctx(('BETRAYAL', 'YIELD'))
        self.assertEqual(len(gave_in.restricted_knowledge), 1)
        prompt = system_prompt(gave_in)
        self.assertIn('Você cedeu ao pedido contra quem você serve', prompt)
        self.assertNotIn('Disposição neste encontro', prompt)       # no contradicting refusal
        self.assertIn('Você não simpatiza com o jogador', prompt)
        self.assertIn('não se deixa comprar', system_prompt(self.ctx(('BRIBE', 'HOLD'))))


if __name__ == '__main__':
    unittest.main()
