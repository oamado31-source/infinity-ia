# SPDX-License-Identifier: Apache-2.0
"""ADR-0147, phase 1: the blind sample hides which model wrote which answer."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('blind_sample',
                                              ROOT / 'tools' / 'dialogue-eval' / 'blind_sample.py')
blind = importlib.util.module_from_spec(spec)
sys.modules['blind_sample'] = blind
spec.loader.exec_module(blind)


def report(model, prefix):
    return {'model': model, 'cases': [
        {'id': f'c{i}', 'question': f'pergunta {i}', 'speaker': {'npc_id': 'npc:x'},
         'history': [], 'runs': [{'speech': f'{prefix} {i}'}]} for i in range(20)]}


class BlindSampleTests(unittest.TestCase):
    def test_sheet_never_names_the_models_and_the_key_maps_back(self):
        sheet, key = blind.build(report('qwen3:30b-a3b', 'local'),
                                 report('claude-haiku-5-5', 'nuvem'), 15, 1)
        self.assertNotIn('qwen', sheet)
        self.assertNotIn('claude', sheet)
        self.assertEqual(len(key['cases']), 15)
        for c in key['cases']:
            self.assertEqual(sorted(c['order']), ['a', 'b'])
            n = c['id'][1:]
            block = sheet.split(f'## {c["n"]}. ')[1].split('## ')[0]
            first = 'local' if c['order'][0] == 'a' else 'nuvem'
            self.assertIn(f'**Resposta 1:** {first} {n}', block)
        orders = {tuple(c['order']) for c in key['cases']}
        self.assertEqual(len(orders), 2)       # the order varies from case to case


if __name__ == '__main__':
    unittest.main()
