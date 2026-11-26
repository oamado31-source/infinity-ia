# SPDX-License-Identifier: Apache-2.0
"""CR-2026-035: the curated persona (who the person is) goes to the prompt, names nobody and
is never a fact; the curation may correct Intelligence and Wisdom (ADR-0147 D2)."""
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
from infinity_ai.dialogue.llm import FakeProvider  # noqa: E402
from infinity_ai.personality.identity import (  # noqa: E402
    knowledge_tier, load_curations, valid_character,
)

PACK = load_partition(1369)
REPLY = '{"speech": "O que vai beber?", "used_facts": [], "unknown": false}'
BERNARD = {'kind': 'resident', 'npc_id': 'npc:eval-funcionario', 'name': 'Bernard', 'wis': 9,
           'int': 9, 'occupation': 'taverneiro da Coroa de Cobre',
           'affiliations': ['place:copper-coronet:STAFF']}
PERSONA = 'Taverneiro ocupado e prático. Quer a conta paga. Com estranhos, é direto.'


class PersonaTests(unittest.TestCase):
    def test_short_and_naming_nobody(self):
        self.assertTrue(valid_character(PERSONA))
        self.assertFalse(valid_character('Respeita Hendak acima de todos.'))
        self.assertFalse(valid_character('Despreza a gente de Amn.'))
        self.assertFalse(valid_character('x' * 241))
        self.assertFalse(valid_character(''))
        self.assertFalse(valid_character(12))

    def system(self, speaker):
        provider = FakeProvider([REPLY])
        ask(Case('t', '', speaker, 'Como vai o movimento hoje?', {}), PACK, provider,
            Catalog.load())
        return provider.calls[0][0]['content']

    def test_the_persona_goes_to_the_prompt_as_a_way_of_being(self):
        prompt = self.system({**BERNARD, 'persona': PERSONA})
        self.assertIn('Seu jeito de ser: ' + PERSONA, prompt)
        self.assertIn('não é fato para contar', prompt)
        self.assertNotIn('Seu jeito de ser', self.system(BERNARD))

    def test_shipped_curations_all_keep_their_persona(self):
        curations = load_curations(PACK)
        with_persona = {n for n, c in curations.items() if c.character}
        self.assertEqual(len(with_persona), 28)          # + Doran Vell (ADR-0148)
        for doc in sorted((ROOT / 'knowledge' / 'npcs').glob('*.json')):
            data = json.loads(doc.read_text(encoding='utf-8'))
            if 'persona' in data:
                self.assertIn(data['npc_id'], curations, doc.name)   # an invalid one would drop

    def test_an_invalid_persona_drops_the_curation(self):
        base = {'schema': 'infinity-ai.npc-identity-curation.v1', 'occupation': 'guarda',
                'curation': {'checked_by': 'mantenedor', 'checked_at': '2026-11-25'}}
        with tempfile.TemporaryDirectory() as tmp:
            for name, persona in (('ok', PERSONA), ('bad', 'Odeia Lehtinan.')):
                (Path(tmp) / f'{name}.json').write_text(json.dumps(
                    {**base, 'npc_id': f'npc:{name}', 'persona': persona}), encoding='utf-8')
            curations = load_curations(PACK, Path(tmp))
        self.assertEqual(curations['npc:ok'].character, PERSONA)
        self.assertNotIn('npc:bad', curations)

    def test_corrected_scores_lift_the_owner_out_of_rudimentary(self):
        lehtinan = load_curations(PACK)['npc:lehtinan']
        self.assertEqual((lehtinan.intelligence, lehtinan.wisdom), (13, 12))
        self.assertEqual(knowledge_tier(6, 9).name, 'rudimentar')      # the game's numbers
        self.assertEqual(knowledge_tier(lehtinan.wisdom, lehtinan.intelligence).name, 'atento')


if __name__ == '__main__':
    unittest.main()
