# SPDX-License-Identifier: Apache-2.0
"""Dialogue regression cases: well-formed, and the checker works with a fake model (no Ollama)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.evaluation import (  # noqa: E402
    CaseError, ask, check_answer, load_cases, required_passes, run_case,
)
from infinity_ai.dialogue.llm import FakeProvider  # noqa: E402

PACK = load_partition(1369)


def reply(speech, used=(), unknown=False):
    return json.dumps({'speech': speech, 'used_facts': list(used), 'unknown': unknown},
                      ensure_ascii=False)


def case(cases, case_id):
    return next(c for c in cases if c.id == case_id)


class CaseFileTests(unittest.TestCase):
    def test_shipped_cases_load(self):
        cases = load_cases(PACK)
        self.assertGreaterEqual(len(cases), 13)
        self.assertEqual(len({c.id for c in cases}), len(cases))

    def test_bad_cases_are_refused(self):
        good = {'id': 'x', 'question': 'Oi?', 'speaker': {'kind': 'resident', 'npc_id': 'npc:x'},
                'checks': {'status': ['OK']}}
        for over in ({'speaker': {'kind': 'goblin', 'npc_id': 'npc:x'}},
                     {'checks': {'adivinhar': True}},
                     {'checks': {'uses': ['org:nao-existe']}},
                     {'speaker': {'kind': 'resident', 'npc_id': 'npc:x', 'standing': 'TURISTA'}},
                     {'question': ''}):
            with self.subTest(over=over), tempfile.TemporaryDirectory() as d:
                path = Path(d) / 'c.json'
                path.write_text(json.dumps({'schema': 'infinity-ai.dialogue-eval-cases.v1',
                                            'cases': [{**good, **over}]}), encoding='utf-8')
                with self.assertRaises(CaseError):
                    load_cases(PACK, path)

    def test_two_of_three(self):
        self.assertEqual(required_passes(3), 2)
        self.assertEqual(required_passes(6), 4)
        self.assertEqual(required_passes(1), 1)


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.cases = load_cases(PACK)

    def test_contexts_are_built_with_the_real_code(self):
        provider = FakeProvider([reply('Não sei.', unknown=True)])
        ask(case(self.cases, 'frequentador-conhece-bernard'), PACK, provider)
        self.assertIn('Bernard', provider.calls[0][0]['content'])        # restricted, by REGULAR
        provider = FakeProvider([reply('Não sei.', unknown=True)])
        ask(case(self.cases, 'sem-vinculo-bernard'), PACK, provider)
        self.assertNotIn('Bernard coordena', provider.calls[0][0]['content'])
        provider = FakeProvider([reply('Não sei.', unknown=True)])
        ask(case(self.cases, 'companheiro-rudimentar-sem-duracao'), PACK, provider)
        prompt = provider.calls[0][0]['content']
        self.assertIn('Conselho dos Seis', prompt)
        self.assertNotIn('décadas', prompt)                               # rudimentary layer
        provider = FakeProvider([reply('Não sei.', unknown=True)])
        ask(case(self.cases, 'conversa-e-quem-e'), PACK, provider)
        self.assertEqual([m['role'] for m in provider.calls[0]],
                         ['system', 'user', 'assistant', 'user'])

    def test_right_answer_passes_and_wrong_answer_fails(self):
        council = case(self.cases, 'habitante-comum-conselho')
        good = ask(council, PACK, FakeProvider([reply('É o Conselho dos Seis, gente sem rosto.')]))
        self.assertEqual(check_answer(council, PACK, good), ())
        # A slip the validator lets through but the case forbids (the informed layer).
        slip = 'O Conselho dos Seis; quem revela os nomes acaba na tortura.'
        bad = ask(council, PACK, FakeProvider([reply(slip)]))
        self.assertIn('citou "tortura"', check_answer(council, PACK, bad))
        copied = ask(council, PACK, FakeProvider(
            [reply('É quem governa Amn; ninguém sabe quem são os seis conselheiros.')]))
        self.assertTrue(any(f.startswith('copiou a camada')
                            for f in check_answer(council, PACK, copied)))

    def test_case_result_needs_two_of_three(self):
        council = case(self.cases, 'habitante-comum-conselho')
        slip = reply('O Conselho dos Seis; quem revela os nomes acaba na tortura.')
        answers = [reply('É o Conselho dos Seis.'), slip, slip]
        result = run_case(council, PACK, FakeProvider(answers), runs=3)
        self.assertEqual((result.passes, result.passed), (1, False))
        self.assertTrue(run_case(council, PACK, FakeProvider(
            [reply('É o Conselho dos Seis.')] * 3), runs=3).passed)


if __name__ == '__main__':
    unittest.main()
