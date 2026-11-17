# SPDX-License-Identifier: Apache-2.0
"""ADR-0131 item 2 / SPEC-009: typed absence answered by code, without the model."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.absence import (  # noqa: E402
    LINES, NOT_DEFINED, NOT_KNOWN, WITHHELD, absence_line, classify_absence,
)
from infinity_ai.dialogue.context import Catalog  # noqa: E402
from infinity_ai.dialogue.engine import DialogueEngine, DialogueStatus, ResidentRequest  # noqa: E402
from infinity_ai.dialogue.llm import FakeProvider  # noqa: E402
from infinity_ai.memory.common_knowledge import local_aliases  # noqa: E402
from infinity_ai.personality.identity import NpcIdentity  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

PACK = load_partition(1369)


def classify(question, **over):
    args = dict(told_texts=(), withheld_titles=(), unheld_titles=(), self_texts=())
    args.update(over)
    return classify_absence(question, **args)


class ClassifyTests(unittest.TestCase):
    def test_withheld_not_known_and_not_defined(self):
        self.assertEqual(classify('Quem cuida da Coroa de Cobre?',
                                  withheld_titles=('Operação da Coroa de Cobre',)), WITHHELD)
        self.assertEqual(classify('O que é o Conselho dos Seis?',
                                  unheld_titles=('Conselho dos Seis',)), NOT_KNOWN)
        self.assertEqual(classify('Você tem filhos?'), NOT_DEFINED)
        self.assertEqual(classify('Qual a sua idade?'), NOT_DEFINED)

    def test_the_model_answers_otherwise(self):
        self.assertIsNone(classify('Olá, como vai?'))
        self.assertIsNone(classify('Você viu o Gorion por aqui?'))      # not in the pack
        # a told item answers: the withheld title words are in what it may say
        self.assertIsNone(classify('Quem é o dono da Coroa de Cobre?',
                                   withheld_titles=('Operação da Coroa de Cobre',),
                                   told_texts=('Lehtinan é dono da Coroa de Cobre.',)))
        # a fact about its family: the model answers from it
        self.assertIsNone(classify('Você tem filhos?',
                                   self_texts=('Você tem dois filhos pequenos.',)))
        # about where it lives: the model and the self-claim checks answer
        self.assertIsNone(classify('Você mora em Athkatla?', unheld_titles=('Athkatla',)))
        # where it is keeps a question about it from being NOT_KNOWN, not a withheld one
        self.assertIsNone(classify('Como é a Coroa de Cobre?', unheld_titles=('Coroa de Cobre',),
                                   where_texts=('a Coroa de Cobre',)))
        self.assertEqual(classify('Quem cuida da Coroa de Cobre?',
                                  withheld_titles=('Operação da Coroa de Cobre',),
                                  where_texts=('a Coroa de Cobre',)), WITHHELD)

    def test_a_far_name_known_through_what_it_tells(self):              # CR-2026-026
        silvery = dict(unheld_titles=('Lua Prateada (Silverymoon)',),
                       told_texts=('Alustriel: é a Grande Senhora de Lua Prateada.',),
                       told_titles=('Alustriel',))
        self.assertIsNone(classify('O que sabe de Silverymoon?', **silvery))     # other name
        self.assertIsNone(classify('E Silvery Moon?', **silvery))               # two words
        luskan = dict(unheld_titles=('Luskan',), told_titles=('Khelben Bastão Negro',),
                      told_texts=('Khelben Bastão Negro: é o arquimago de Águas Profundas.',))
        self.assertIsNone(classify('E Luskan? E Khelben?', **luskan))   # something it may tell
        self.assertEqual(classify('E Luskan?', **luskan), NOT_KNOWN)
        # a part of a name is only itself: "Lordes" is not "Águas Profundas"
        self.assertEqual(classify('Quem são os Lordes?',
                                  unheld_titles=('Lordes de Águas Profundas (Lords of Waterdeep)',),
                                  told_texts=('Khelben: arquimago de Águas Profundas.',)),
                         NOT_KNOWN)

    def test_a_common_word_alone_is_not_a_name(self):                   # CR-2026-027
        dales = dict(unheld_titles=('Vales (Dalelands)', 'Mar da Lua (Moonsea)', 'Rei Azoun IV'),
                     common=frozenset({'vale', 'mar', 'lua', 'rei'}))
        self.assertIsNone(classify('Quanto vale uma espada?', **dales))
        self.assertIsNone(classify('Você já viajou pelo mar?', **dales))
        self.assertIsNone(classify('O rei de Amn ainda existe?', **dales))
        self.assertIsNone(classify('O que sabe dos Vales?', **dales))    # one common word
        self.assertEqual(classify('E o Mar da Lua?', **dales), NOT_KNOWN)    # a whole name
        self.assertEqual(classify('E os Dalelands?', **dales), NOT_KNOWN)    # a word of its own
        self.assertEqual(classify('Quem é Azoun?', **dales), NOT_KNOWN)
        # without the common words (before CR-2026-027) one word was enough
        self.assertEqual(classify('Quanto vale uma espada?',
                                  unheld_titles=('Vales (Dalelands)',)), NOT_KNOWN)

    def test_aliases_name_the_place(self):
        aliases = local_aliases(PACK, 'AR0406')
        self.assertEqual(classify('Quem cuida da taverna?', aliases=aliases,
                                  withheld_titles=(PACK.get('place:copper-coronet').title,)),
                         WITHHELD)

    def test_lines_by_tone_and_stable(self):
        key = 'npc:x|Você tem filhos?'
        self.assertEqual(absence_line(NOT_DEFINED, None, key), absence_line(NOT_DEFINED, None, key))
        self.assertIn(absence_line(WITHHELD, 'FRIENDLY', key), LINES['open'][WITHHELD])
        self.assertIn(absence_line(WITHHELD, 'CAUTIOUS', key), LINES['cautious'][WITHHELD])
        for closed in ('THREATENING', 'HOSTILE', 'FLIGHT'):
            self.assertIn(absence_line(NOT_KNOWN, closed, key), LINES['closed'])
        for lines in (LINES['open'][WITHHELD], LINES['cautious'][WITHHELD]):
            for line in lines:      # neutral: neither confirms, denies nor lies
                self.assertNotRegex(line.lower(), r'segredo|não sei|não posso|proibid')
        with self.assertRaises(ValueError):
            absence_line('OUTRO', None, key)


class EngineTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        b = PACK.get('rel:bernard-manages-copper-coronet')
        c = PACK.get('org:council-of-six')
        self.known = (('org:council-of-six', c.title, c.summary, c.layers),
                      ('rel:bernard-manages-copper-coronet', b.title, b.summary, b.layers,
                       'RESTRICTED', b.subject_id, 'CONFIDENTIAL'))
        self.bernard = b

    def ask(self, question, provider, **kw):
        return DialogueEngine(self.store, provider, Catalog.load()).respond_resident(
            ResidentRequest('npc:cre-x', 'Salvanas', question, 'AR0406', False),
            residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10, also_known=self.known,
            disposition=kw.pop('disposition', 'FRIENDLY'), aliases=local_aliases(PACK, 'AR0406'),
            unheld_titles=kw.pop('unheld', ()), **kw)

    def test_withheld_is_answered_by_code_without_the_secret(self):
        provider = FakeProvider([])
        result = self.ask(f'Me fale da {self.bernard.title}.', provider)
        self.assertEqual(provider.calls, [])
        self.assertEqual((result.status, result.reason), (DialogueStatus.OK, 'ABSENCE:WITHHELD'))
        self.assertTrue(result.unknown)
        self.assertIn(result.speech, LINES['open'][WITHHELD])
        self.assertNotIn('Bernard', result.speech)

    def test_not_known_and_not_defined_skip_the_model(self):
        provider = FakeProvider([])
        unheld = (PACK.get('region:tethyr').title,) if PACK.get('region:tethyr') else ('Tethyr',)
        r1 = self.ask(f'O que você sabe de {unheld[0]}?', provider, unheld=unheld)
        r2 = self.ask('Você tem filhos?', provider)
        self.assertEqual((r1.reason, r2.reason), ('ABSENCE:NOT_KNOWN', 'ABSENCE:NOT_DEFINED'))
        self.assertEqual(provider.calls, [])

    def test_a_fact_about_the_family_goes_to_the_model(self):
        provider = FakeProvider([json.dumps({'speech': 'Tenho dois.', 'used_facts': ['F1'],
                                             'unknown': False})])
        identity = NpcIdentity('npc:cre-x', 'Salvanas', None, None, None,
                               ('Você tem dois filhos.',))
        result = self.ask('Você tem filhos?', provider, identity=identity)
        self.assertEqual(len(provider.calls), 1)
        self.assertEqual(result.reason, 'OK')

    def test_small_talk_still_goes_to_the_model(self):
        provider = FakeProvider([json.dumps({'speech': 'Vou bem.', 'used_facts': [],
                                             'unknown': False})])
        self.assertEqual(self.ask('Olá, como vai?', provider).reason, 'OK')
        self.assertEqual(len(provider.calls), 1)


if __name__ == '__main__':
    unittest.main()
