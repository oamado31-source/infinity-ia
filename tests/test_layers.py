# SPDX-License-Identifier: Apache-2.0
"""ADR-0147: which layer answers (code, the local model or Claude), and the code answers."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import Catalog  # noqa: E402
from infinity_ai.dialogue.evaluation import Case, ask  # noqa: E402
from infinity_ai.dialogue.layers import (  # noqa: E402
    CLAUDE, CODE, FAREWELL, GREETING, LOCAL, NAME, OCCUPATION, PLACE, LayerPolicy, choose_layer,
    code_line, may_refine, mood, simple_intent, simple_line,
)
from infinity_ai.dialogue.llm import (  # noqa: E402
    BudgetedProvider, FakeProvider, LlmError, MonthlyBudget,
)
from infinity_ai.personality.identity import load_curations  # noqa: E402

OK_REPLY = '{"speech": "Isso eu não sei dizer.", "used_facts": [], "unknown": true}'
BAD_REPLY = 'não é json'
BERNARD = {'kind': 'resident', 'npc_id': 'npc:eval-funcionario', 'name': 'Bernard', 'wis': 9,
           'int': 9, 'occupation': 'taverneiro da Coroa de Cobre',
           'affiliations': ['place:copper-coronet:STAFF'],
           'self_facts': ['Você serve bebida no balcão da Coroa de Cobre.']}


class ChooseLayerTests(unittest.TestCase):
    def test_d1_by_intelligence_and_wisdom(self):
        self.assertEqual(choose_layer(9, 9), LOCAL)
        self.assertEqual(choose_layer(13, 13), LOCAL)
        self.assertEqual(choose_layer(None, None), LOCAL)        # not read: the middle
        self.assertEqual(choose_layer(6, 7), CODE)               # both up to 7
        self.assertEqual(choose_layer(6, 9), LOCAL)              # only one low (Hendak)
        self.assertEqual(choose_layer(10, 17), CLAUDE)           # either from 15 (Firkra)
        self.assertEqual(choose_layer(17, 13), CLAUDE)           # Tamoko

    def test_d6_by_the_reaction(self):
        self.assertEqual(choose_layer(9, 9, disposition='FRIENDLY'), CLAUDE)
        self.assertEqual(choose_layer(9, 9, disposition='INDIFFERENT'), LOCAL)
        for negative in ('CAUTIOUS', 'THREATENING', 'HOSTILE', 'FLIGHT'):
            self.assertEqual(choose_layer(17, 16, disposition=negative), LOCAL)
            self.assertFalse(may_refine(negative))
        self.assertEqual(choose_layer(5, 6, disposition='FRIENDLY'), CODE)
        self.assertTrue(may_refine('FRIENDLY'))
        self.assertTrue(may_refine(None))

    def test_a_companion_counts_by_trust(self):
        self.assertEqual(mood(None, 'CONFIANTE', companion=True), 'FRIENDLY')
        self.assertEqual(mood(None, 'INTIMO', companion=True), 'FRIENDLY')
        self.assertEqual(mood(None, 'DESCONFIADO', companion=True), 'CAUTIOUS')
        self.assertIsNone(mood(None, 'NEUTRO', companion=True))
        self.assertEqual(mood('HOSTILE', 'INTIMO'), 'HOSTILE')    # a resident: its reaction


class SimpleQuestionTests(unittest.TestCase):
    def test_only_a_whole_simple_question(self):
        self.assertEqual(simple_intent('Qual é o seu nome?'), NAME)
        self.assertEqual(simple_intent('Como você se chama?'), NAME)
        self.assertEqual(simple_intent('Quem é você?'), NAME)
        self.assertEqual(simple_intent('Olá!'), GREETING)
        self.assertEqual(simple_intent('Bom dia, amigo.'), GREETING)
        self.assertEqual(simple_intent('Tchau'), FAREWELL)
        self.assertEqual(simple_intent('O que você faz aqui?'), OCCUPATION)
        self.assertEqual(simple_intent('Onde estamos?'), PLACE)
        self.assertIsNone(simple_intent('Olá, quem governa Amn?'))
        self.assertIsNone(simple_intent('Qual é o nome do dono da taverna?'))

    def test_lines_from_what_is_curated(self):
        kw = dict(occupation='taverneiro', place='a Coroa de Cobre', level=2, key='k')
        self.assertIn('Bernard', simple_line(NAME, name='Bernard', disposition=None, **kw))
        self.assertIsNone(simple_line(NAME, name='Plebeu', disposition=None, **kw))
        self.assertNotIn('Bernard', simple_line(NAME, name='Bernard', disposition='HOSTILE', **kw))
        self.assertEqual(simple_line(OCCUPATION, name='Bernard', disposition=None, **kw),
                         'Sou taverneiro.')
        self.assertEqual(simple_line(PLACE, name='Bernard', disposition=None, **kw),
                         'Estamos na Coroa de Cobre.')
        self.assertIsNone(simple_line(OCCUPATION, name='X', disposition=None,
                                      occupation=None, place=None, level=2, key='k'))
        full = simple_line(NAME, name='Bernard', disposition=None,
                           **{**kw, 'level': 4})
        self.assertIn('Sou taverneiro.', full)

    def test_the_code_layer_says_only_a_first_sentence(self):
        known = ('Athkatla é a capital de Amn. Os Magos Encapuzados cobram licença.',)
        line, unknown = code_line('E Athkatla?', known, disposition=None, key='k')
        self.assertEqual(line, 'Hum... Athkatla é a capital de Amn.')
        self.assertFalse(unknown)
        line, unknown = code_line('Quem governa Calimshan?', known, disposition=None, key='k')
        self.assertTrue(unknown)
        self.assertNotIn('Calimshan', line)


class EngineLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_partition(1369)
        cls.catalog = Catalog.load()

    def ask(self, question, speaker=None, local=(OK_REPLY,), claude=None):
        local = FakeProvider(list(local), model='qwen3:30b-a3b')
        cloud = FakeProvider(list(claude), model='claude-haiku-5-5') if claude is not None \
            else None
        case = Case('t', '', speaker or BERNARD, question, {})
        response = ask(case, self.pack, local, self.catalog, LayerPolicy(claude=cloud))
        return response, local, cloud

    def test_a_simple_question_never_calls_a_model(self):
        response, local, cloud = self.ask('Qual é o seu nome?', claude=[OK_REPLY])
        self.assertIn('Bernard', response.speech)
        self.assertEqual(response.model, 'code')
        self.assertEqual((local.calls, cloud.calls), ([], []))

    def test_a_simple_mind_answers_by_code(self):
        speaker = {**BERNARD, 'wis': 5, 'int': 6}
        response, local, cloud = self.ask('Quem governa Calimshan?', speaker, claude=[OK_REPLY])
        self.assertEqual(response.model, 'code')
        self.assertEqual((local.calls, cloud.calls), ([], []))

    def test_a_sharp_mind_goes_to_claude_with_the_same_prompt(self):
        speaker = {**BERNARD, 'wis': 16}
        response, local, cloud = self.ask('Quem governa Amn?', speaker, claude=[OK_REPLY])
        self.assertEqual(response.model, 'claude-haiku-5-5')
        self.assertEqual(local.calls, [])
        self.assertIn('LAYER:CLAUDE', response.flags)
        # what Claude receives is what the local model would: the same filtered prompt
        _, alone, _ = self.ask('Quem governa Amn?', speaker)
        self.assertEqual(cloud.calls[0], alone.calls[0])

    def test_claude_unavailable_falls_to_the_local_model(self):
        speaker = {**BERNARD, 'disposition': 'FRIENDLY'}
        response, local, cloud = self.ask('Quem governa Amn?', speaker,
                                          claude=[LlmError('sem rede')])
        self.assertEqual(response.model, 'qwen3:30b-a3b')
        self.assertEqual(len(local.calls), 1)
        self.assertIn('LAYER:LOCAL', response.flags)

    def test_refinement_goes_up_once_but_never_for_a_negative_reaction(self):
        response, local, cloud = self.ask('Quem governa Amn?', local=(BAD_REPLY, BAD_REPLY),
                                          claude=[OK_REPLY])
        self.assertEqual(response.model, 'claude-haiku-5-5')
        self.assertIn('REFINE:CLAUDE', response.flags)
        speaker = {**BERNARD, 'disposition': 'CAUTIOUS'}
        response, local, cloud = self.ask('Quem governa Amn?', speaker,
                                          local=(BAD_REPLY, BAD_REPLY), claude=[OK_REPLY])
        self.assertEqual(cloud.calls, [])
        self.assertEqual(response.status.value, 'FALLBACK')

    def test_without_claude_nothing_goes_up(self):
        speaker = {**BERNARD, 'wis': 18, 'disposition': 'FRIENDLY'}
        response, local, _ = self.ask('Quem governa Amn?', speaker)
        self.assertEqual(response.model, 'qwen3:30b-a3b')
        self.assertIn('LAYER:LOCAL', response.flags)

    def test_a_curated_way_of_talking_keeps_simple_questions_with_the_model(self):
        speaker = {**BERNARD, 'speech': 'fala arrastada de bêbado'}
        case = Case('t', '', speaker, 'Qual é o seu nome?', {})
        local = FakeProvider([OK_REPLY], model='qwen3:30b-a3b')
        ask(case, self.pack, local, self.catalog, LayerPolicy())
        self.assertEqual(len(local.calls), 1)


class BudgetTests(unittest.TestCase):
    def test_over_the_cap_claude_is_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            budget = MonthlyBudget(Path(tmp) / 'usage.json', 0.001, month=lambda: '2026-11')

            class Inner:
                model = 'claude-haiku-5-5'
                last_usage = {}

                def generate(self, messages):
                    self.last_usage = {'input_tokens': 10_000, 'output_tokens': 0}
                    return OK_REPLY

            provider = BudgetedProvider(Inner(), budget)
            self.assertEqual(provider.generate([]), OK_REPLY)
            self.assertAlmostEqual(budget.spent(), 0.001)
            with self.assertRaises(LlmError):
                provider.generate([])
            doc = json.loads((Path(tmp) / 'usage.json').read_text())
            self.assertEqual(set(doc), {'2026-11'})          # money only, by month


class CurationMindTests(unittest.TestCase):
    def test_the_curation_may_correct_the_scores(self):
        pack = load_partition(1369)
        base = {'schema': 'infinity-ai.npc-identity-curation.v1', 'occupation': 'gladiador',
                'curation': {'checked_by': 'mantenedor', 'checked_at': '2026-11-24'}}
        with tempfile.TemporaryDirectory() as tmp:
            for name, mind in (('ok', {'wis': 14, 'int': 12}), ('bad', {'wis': 40}),
                               ('none', None)):
                doc = {**base, 'npc_id': f'npc:{name}'}
                if mind is not None:
                    doc['mind'] = mind
                (Path(tmp) / f'{name}.json').write_text(json.dumps(doc), encoding='utf-8')
            curations = load_curations(pack, Path(tmp))
        self.assertEqual((curations['npc:ok'].wisdom, curations['npc:ok'].intelligence), (14, 12))
        self.assertNotIn('npc:bad', curations)
        self.assertIsNone(curations['npc:none'].wisdom)


if __name__ == '__main__':
    unittest.main()
