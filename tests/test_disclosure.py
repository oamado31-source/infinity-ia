# SPDX-License-Identifier: Apache-2.0
"""ADR-0131 / SPEC-009: per-item disclosure decided by code before the prompt, with secrecy
classes. Items without a class must keep the ADR-0125/0126 behaviour exactly."""
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.canon.pack import CanonError, load_partition  # noqa: E402
from infinity_ai.dialogue.context import Catalog, build_resident_context  # noqa: E402
from infinity_ai.dialogue.disclosure import (  # noqa: E402
    ABSOLUTE, CONFIANTE, CONFIDENTIAL, DESCONFIADO, FACTION_SECRET, INTIMO, NEUTRO, PERSONAL,
    PROFESSIONAL, PUBLIC, WITHHOLD, decide, secrecy_of,
)
from infinity_ai.dialogue.engine import system_prompt  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402
from test_canon import TempKnowledge  # noqa: E402

PACK = load_partition(1369)
DISPOSITIONS = (None, 'FRIENDLY', 'INDIFFERENT', 'CAUTIOUS', 'THREATENING', 'HOSTILE', 'FLIGHT')


def old_rule(scope, disposition, morale):
    """ADR-0125/0126 as implemented before ADR-0131 (context.py)."""
    tells_public = disposition not in ('THREATENING', 'HOSTILE', 'FLIGHT')
    tells_restricted = tells_public and disposition != 'CAUTIOUS'
    if morale == 'YIELD':
        tells_public = tells_restricted = True
    return tells_restricted if scope == 'RESTRICTED' else tells_public


class DecisionTests(unittest.TestCase):
    def test_items_without_a_class_keep_the_old_rule(self):
        for scope, disposition, morale in itertools.product(
                ('COMMON_REGIONAL', 'CANON_REFERENCE', 'RESTRICTED'), DISPOSITIONS,
                (None, 'HOLD', 'YIELD')):
            with self.subTest(scope=scope, disposition=disposition, morale=morale):
                d = decide('x', access_scope=scope, disposition=disposition,
                           morale_outcome=morale)
                self.assertEqual(d.allowed, old_rule(scope, disposition, morale))
                self.assertTrue(d.reason)

    def test_default_class_by_scope(self):
        self.assertEqual(secrecy_of('COMMON_REGIONAL'), PUBLIC)
        self.assertEqual(secrecy_of('RESTRICTED'), PROFESSIONAL)
        self.assertEqual(secrecy_of('RESTRICTED', CONFIDENTIAL), CONFIDENTIAL)
        with self.assertRaises(ValueError):
            secrecy_of('RESTRICTED', 'SEGREDO')
        with self.assertRaises(ValueError):
            decide('x', access_scope='RESTRICTED', trust='AMIGO')

    def test_friendly_is_not_consent_for_a_confidence(self):
        d = decide('x', access_scope='RESTRICTED', secrecy=CONFIDENTIAL, disposition='FRIENDLY')
        self.assertEqual((d.mode, d.reason), (WITHHOLD, 'TRUST_REQUIRED'))
        trusted = decide('x', access_scope='RESTRICTED', secrecy=CONFIDENTIAL,
                         disposition='FRIENDLY', trust=CONFIANTE)
        self.assertTrue(trusted.allowed)
        hostile = decide('x', access_scope='RESTRICTED', secrecy=CONFIDENTIAL,
                         disposition='HOSTILE', trust=INTIMO)
        self.assertEqual(hostile.reason, 'CLOSED_DISPOSITION')

    def test_giving_in_never_opens_the_protected_classes(self):
        for cls in (CONFIDENTIAL, FACTION_SECRET, ABSOLUTE):
            with self.subTest(cls=cls):
                d = decide('x', access_scope='RESTRICTED', secrecy=cls,
                           disposition='THREATENING', morale_outcome='YIELD')
                self.assertFalse(d.allowed)
        for cls in (PERSONAL, PROFESSIONAL):
            self.assertTrue(decide('x', access_scope='RESTRICTED' if cls == PROFESSIONAL
                                   else 'COMMON_REGIONAL', secrecy=cls,
                                   disposition='HOSTILE', morale_outcome='YIELD').allowed)

    def test_faction_secret_only_to_members_and_absolute_never(self):
        self.assertEqual(decide('x', access_scope='RESTRICTED', secrecy=FACTION_SECRET,
                                disposition='FRIENDLY', trust=INTIMO).reason, 'NOT_A_MEMBER')
        self.assertTrue(decide('x', access_scope='RESTRICTED', secrecy=FACTION_SECRET,
                               disposition='FRIENDLY', listener_member=True).allowed)
        d = decide('x', access_scope='RESTRICTED', secrecy=ABSOLUTE, disposition='FRIENDLY',
                   morale_outcome='YIELD', trust=INTIMO, listener_member=True)
        self.assertEqual((d.mode, d.reason), (WITHHOLD, 'ABSOLUTE'))

    def test_distrust_keeps_the_professional_items(self):
        self.assertEqual(decide('x', access_scope='RESTRICTED', disposition='FRIENDLY',
                                trust=DESCONFIADO).reason, 'TRUST_REQUIRED')
        self.assertTrue(decide('x', access_scope='COMMON_REGIONAL', disposition='FRIENDLY',
                               trust=DESCONFIADO).allowed)
        self.assertTrue(decide('x', access_scope='RESTRICTED', disposition='FRIENDLY',
                               trust=NEUTRO).allowed)


class SchemaTests(TempKnowledge):
    def rel(self, name, **change):
        path = self.root / 'periods' / '1369-DR' / 'relationships' / f'{name}.json'
        doc = json.loads(path.read_text(encoding='utf-8'))
        doc.update(change)
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')

    def test_a_class_loads_and_is_optional(self):
        self.assertIsNone(PACK.get('rel:bernard-manages-copper-coronet').secrecy)
        self.rel('bernard-manages-copper-coronet', secrecy=CONFIDENTIAL)
        self.assertEqual(self.load().get('rel:bernard-manages-copper-coronet').secrecy,
                         CONFIDENTIAL)

    def test_inconsistent_or_unknown_classes_are_refused(self):
        for name, value in (('bernard-manages-copper-coronet', 'SEGREDO'),
                            ('bernard-manages-copper-coronet', PUBLIC),
                            ('lehtinan-owns-copper-coronet', CONFIDENTIAL)):
            with self.subTest(name=name, value=value):
                self.setUp()
                self.rel(name, secrecy=value)
                with self.assertRaises(CanonError):
                    self.load()


class ContextTests(unittest.TestCase):
    """A withheld item never reaches the prompt: not its text, not its id."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        council = PACK.get('org:council-of-six')
        bernard = PACK.get('rel:bernard-manages-copper-coronet')
        self.public = ('org:council-of-six', council.title, council.summary, council.layers)
        self.bernard = bernard

    def ctx(self, secrecy=None, *, disposition='FRIENDLY', morale=None, trust=NEUTRO):
        b = self.bernard
        known = (self.public, ('rel:bernard-manages-copper-coronet', b.title, b.summary,
                               b.layers, 'RESTRICTED', b.subject_id, secrecy))
        return build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:cre-x',
            display_name='Salvanas', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, also_known=known,
            disposition=disposition, morale=morale, trust=trust).context

    def test_confidential_item_stays_out_of_the_prompt(self):
        context = self.ctx(CONFIDENTIAL)
        self.assertEqual((len(context.knowledge), len(context.restricted_knowledge)), (1, 0))
        prompt = system_prompt(context)
        self.assertNotIn(self.bernard.summary, prompt)
        self.assertNotIn('bernard-manages', prompt)
        withheld = [d for d in context.disclosure if not d.allowed]
        self.assertEqual([(d.entry_id, d.reason) for d in withheld],
                         [('rel:bernard-manages-copper-coronet', 'TRUST_REQUIRED')])

    def test_yield_and_trust_through_the_context(self):
        threatened = self.ctx(CONFIDENTIAL, disposition='THREATENING',
                              morale=('INTIMIDATION', 'YIELD'))
        self.assertEqual(len(threatened.restricted_knowledge), 0)
        self.assertEqual(len(threatened.knowledge), 1)           # public opens on giving in
        self.assertEqual(len(self.ctx(CONFIDENTIAL, trust=CONFIANTE).restricted_knowledge), 1)
        self.assertEqual(len(self.ctx(None).restricted_knowledge), 1)   # no class: as before


if __name__ == '__main__':
    unittest.main()
