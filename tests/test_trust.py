# SPDX-License-Identifier: Apache-2.0
"""ADR-0133: trust by event (SPEC-009 phase 4b)."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.dialogue.context import Catalog, build_resident_context  # noqa: E402
from infinity_ai.dialogue.recall import TURN_EVENT  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.personality.morale import MORALE_EVENT  # noqa: E402
from infinity_ai.personality.reaction import REACTION_EVENT  # noqa: E402
from infinity_ai.personality.trust import (  # noqa: E402
    TRUST_EVENT, assess, revise_trust, trust_of,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

KEY = 'npc:x'


def ev(seq, kind, **payload):
    return SimpleNamespace(seq=seq, event_id=f'e{seq}', event_type=kind,
                           payload={'npc_key': KEY, **payload})


def acquaintance(sessions=3, turns=6, disposition='FRIENDLY'):
    out, seq = [], 0
    for s in range(sessions):
        seq += 1
        out.append(ev(seq, REACTION_EVENT, session=s, launch='L1', disposition=disposition))
        for _ in range(turns // sessions):
            seq += 1
            out.append(ev(seq, TURN_EVENT))
    return out


class AssessTests(unittest.TestCase):
    def test_three_good_sessions_and_six_turns_make_trust_for_own_secrets(self):
        trust, cause = assess(acquaintance())
        self.assertEqual((trust.level, trust.rule, trust.own_only), ('CONFIANTE', 'ACQUAINTANCE', True))
        self.assertTrue(cause)
        self.assertEqual(assess(acquaintance(sessions=2, turns=6))[0].level, 'NEUTRO')
        self.assertEqual(assess(acquaintance(sessions=3, turns=3))[0].level, 'NEUTRO')
        self.assertEqual(assess(acquaintance(disposition='INDIFFERENT'))[0].level, 'CONFIANTE')
        self.assertEqual(assess(acquaintance(disposition='CAUTIOUS'))[0].level, 'NEUTRO')

    def test_coercion_and_hostility_bring_distrust_but_a_bribe_does_not(self):
        events = acquaintance() + [ev(99, MORALE_EVENT, trigger='INTIMIDATION', outcome='HOLD')]
        self.assertEqual(assess(events)[0].level, 'DESCONFIADO')
        self.assertEqual(assess(events)[0].rule, 'COERCION')
        betrayal = [ev(1, MORALE_EVENT, trigger='BETRAYAL', outcome='YIELD')]
        self.assertEqual(assess(betrayal)[0].level, 'DESCONFIADO')
        hostile = [ev(1, REACTION_EVENT, session=0, disposition='HOSTILE')]
        self.assertEqual(assess(hostile)[0].rule, 'HOSTILITY')
        bribe = acquaintance(sessions=2) + [ev(99, MORALE_EVENT, trigger='BRIBE', outcome='YIELD')]
        self.assertEqual(assess(bribe)[0].level, 'NEUTRO')


class StoreTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def add(self, kind, n, **payload):
        self.store.append_event(branch_id=ROOT_BRANCH, host_epoch=0, event_type=kind,
                                category='CAMPAIGN_OBSERVATION', game_time=n,
                                payload={'npc_key': KEY, **payload}, evidence='LAB_OBSERVED',
                                idempotency_key=f'{kind}|{n}')

    def test_revision_is_recorded_once_and_read_back(self):
        self.assertEqual(trust_of(self.store, ROOT_BRANCH, KEY).level, 'NEUTRO')
        n = 0
        for s in range(3):
            n += 1
            self.add(REACTION_EVENT, n, session=s, launch='L', disposition='FRIENDLY')
            for _ in range(2):
                n += 1
                self.add(TURN_EVENT, n)
        for _ in range(2):
            self.assertEqual(revise_trust(self.store, ROOT_BRANCH, KEY, game_time=n).level, 'CONFIANTE')
        revisions = self.store.visible_events(ROOT_BRANCH, TRUST_EVENT)
        self.assertEqual(len(revisions), 1)
        self.assertEqual(trust_of(self.store, ROOT_BRANCH, KEY).own_only, True)
        self.add(MORALE_EVENT, n + 1, trigger='INTIMIDATION', outcome='HOLD')
        self.assertEqual(revise_trust(self.store, ROOT_BRANCH, KEY, game_time=n + 1).level, 'DESCONFIADO')
        self.assertEqual(trust_of(self.store, ROOT_BRANCH, KEY).rule, 'COERCION')


class DomainTests(unittest.TestCase):
    """D2: trust from acquaintance opens the person's own confidences, not the house's."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def ids(self, trust, own_only):
        known = (('rel:own', 'Dívida de Teste', 'O Teste deve dinheiro.', {}, 'RESTRICTED', KEY, 'CONFIDENTIAL'),
                 ('rel:house', 'Segredo da Casa', 'A casa esconde algo.', {}, 'RESTRICTED', 'npc:y', 'CONFIDENTIAL'),
                 ('rel:work', 'Rotina da Casa', 'A casa abre cedo.', {}, 'RESTRICTED', 'npc:y', 'PROFESSIONAL'))
        context = build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id=KEY, display_name='Teste',
            residence_areas=('AR0406',), area='AR0406', dead=False, branch_id=ROOT_BRANCH,
            at_game_time=10, also_known=known, trust=trust, trust_own_only=own_only).context
        return {k.event_id for k in context.knowledge + context.restricted_knowledge}

    def test_acquaintance_opens_only_own_secrets_and_distrust_closes_house_business(self):
        self.assertEqual(self.ids('NEUTRO', False), {'canon:rel:work'})
        self.assertEqual(self.ids('CONFIANTE', True), {'canon:rel:own', 'canon:rel:work'})
        self.assertEqual(self.ids('CONFIANTE', False),
                         {'canon:rel:own', 'canon:rel:house', 'canon:rel:work'})
        self.assertEqual(self.ids('DESCONFIADO', True), set())

    def test_a_distrustful_person_does_not_recall_a_withheld_topic(self):
        # Lab, 2026-11-17: Unger had told the group about the arena; distrustful later, the
        # recall line still named it, and the model talked about it.
        known = (('rel:work', 'Arena da Casa', 'A casa tem uma arena.', {}, 'RESTRICTED', 'npc:y',
                  'PROFESSIONAL'),)
        lines = (('recall:e1', 'Você já conversou com o jogador antes (uma vez).'),
                 ('recall:e1:assuntos', 'Vocês falaram sobre: Arena da Casa, Athkatla.'))

        def context(trust):
            return build_resident_context(
                MemoryStore(self.store), self.store, Catalog.load(), npc_id=KEY,
                display_name='Teste', residence_areas=('AR0406',), area='AR0406', dead=False,
                branch_id=ROOT_BRANCH, at_game_time=10, also_known=known, trust=trust,
                recall_lines=lines, question='Me fala sobre a arena dos fundos!').context

        distrustful = context('DESCONFIADO')
        texts = [f.text for f in distrustful.facts]
        self.assertIn('Vocês falaram sobre: Athkatla.', texts)
        self.assertFalse(any('Arena' in text for text in texts))
        self.assertEqual(distrustful.absence, 'WITHHELD')
        self.assertIn('Vocês falaram sobre: Arena da Casa, Athkatla.',
                      [f.text for f in context('NEUTRO').facts])


if __name__ == '__main__':
    unittest.main()
