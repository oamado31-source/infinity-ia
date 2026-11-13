# SPDX-License-Identifier: Apache-2.0
"""ADR-0121: an opinion passes; a fact about someone else needs the speaker's knowledge."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.dialogue.claims import third_party_claim  # noqa: E402
from infinity_ai.dialogue.context import DialogueContext, Fact, Persona  # noqa: E402
from infinity_ai.dialogue.validate import validate_reply  # noqa: E402

OWNER = ('Proprietário da Coroa de Cobre: Lehtinan é o proprietário da Coroa de Cobre, uma '
         'taverna de Athkatla.')
COUNCIL_POPULAR = 'Conselho dos Seis: É quem governa Amn; ninguém sabe quem são os seis conselheiros.'
COUNCIL_STUDIED = COUNCIL_POPULAR + ' Governam Amn há cerca de três décadas.'
AMN = 'Amn: Nação mercantil do sul da Costa da Espada, onde a riqueza vale mais que tudo.'
BERNARD = ('Bernard administra a Coroa de Cobre para Lehtinan: Bernard coordena o atendimento e a '
           'operação cotidiana da Coroa de Cobre em nome de Lehtinan.')


def context(*knowledge, facts=('Você vive em Athkatla e está na Coroa de Cobre.',),
            restricted=(), name='Campesino(a)'):
    def items(prefix, texts):
        return tuple(Fact(f'{prefix}{i}', f'x:{prefix}{i}', t, 0) for i, t in enumerate(texts, 1))
    texts = facts + knowledge + restricted
    vocabulary = frozenset(w for t in texts for w in re.findall(r"[A-ZÀ-Ý][\wÀ-ÿ'-]+", t))
    return DialogueContext(Persona('npc:x', name, (), frozenset({name}), '...'),
                           items('F', facts), vocabulary | {name}, (), items('K', knowledge),
                           restricted_knowledge=items('R', restricted), standing='HABITANTE')


class ThirdPartyTests(unittest.TestCase):
    def test_role(self):
        ctx = context(OWNER)
        self.assertEqual(third_party_claim('O taverneiro é Lehtinan, dono da Coroa de Cobre.',
                                           ctx), 'ROLE')
        self.assertIsNone(third_party_claim('O dono é Lehtinan.', ctx))
        self.assertIsNone(third_party_claim('Lehtinan é o proprietário daqui.', ctx))
        # A regular who knows the restricted edge may call Bernard the one running the house.
        regular = context(OWNER, restricted=(BERNARD,))
        self.assertIsNone(third_party_claim('Bernard é o gerente, cuida de tudo.', regular))
        self.assertEqual(third_party_claim('Bernard é o gerente.', context(OWNER, BERNARD.replace(
            'administra', 'conhece').replace('coordena o atendimento e', 'vê'))), 'ROLE')

    def test_trait_is_refused_but_an_opinion_passes(self):
        ctx = context(OWNER)
        self.assertEqual(third_party_claim('Lehtinan? Cara duro, mas bem-humorado.', ctx), 'TRAIT')
        self.assertEqual(third_party_claim('Lehtinan é muito rico.', ctx), 'TRAIT')
        self.assertIsNone(third_party_claim('Acho que Lehtinan é um cara duro.', ctx))
        self.assertIsNone(third_party_claim('Não confio no Lehtinan.', ctx))
        self.assertIsNone(third_party_claim('Cruel! Eles governam Amn, mas ninguém sabe quem são!',
                                            context(COUNCIL_POPULAR)))
        self.assertIsNone(third_party_claim('A Coroa de Cobre é uma taverna de Athkatla.', ctx))

    def test_numbers_follow_what_one_knows(self):
        speech = 'Amn é governado pelo Conselho dos Seis! Eles decidem tudo há décadas!'
        self.assertEqual(third_party_claim(speech, context(COUNCIL_POPULAR)), 'NUMBER')
        self.assertIsNone(third_party_claim(speech, context(COUNCIL_STUDIED)))
        self.assertIsNone(third_party_claim('Governam Amn há muito tempo.', context(COUNCIL_POPULAR)))
        twenty = ('Você vive em Athkatla e está na Coroa de Cobre.', 'Você vive aqui há 20 anos.')
        twelve = ('Você vive em Athkatla e está na Coroa de Cobre.', 'Você vive aqui há 12 anos.')
        self.assertIsNone(third_party_claim('Vivo aqui há 20 anos.', context(facts=twenty)))
        self.assertEqual(third_party_claim('Vivo aqui há 20 anos.', context(facts=twelve)), 'NUMBER')

    def test_general_rule_needs_a_backing(self):
        speech = 'Governa quem tem dinheiro e coragem de usá-lo.'
        self.assertIsNone(third_party_claim(speech, context(COUNCIL_POPULAR, AMN)))
        self.assertEqual(third_party_claim(speech, context(COUNCIL_POPULAR)), 'GENERAL')

    def test_lab_answers_that_were_approved_still_pass(self):
        ctx = context(OWNER, COUNCIL_POPULAR, restricted=(BERNARD,))
        for speech in ('Estou aqui sempre que posso. Bernard cuida do dia-a-dia.',
                       'É o Conselho dos Seis. Ninguém sabe quem são eles.',
                       'Moro em Athkatla, sim.', 'É Lehtinan. Não me pergunte mais nada.',
                       'O dono da taverna é Lehtinan. Não sei se ele sabe quem são os conselheiros.'):
            with self.subTest(speech=speech):
                self.assertIsNone(third_party_claim(speech, ctx))

    def test_validator_reports_the_rule(self):
        raw = json.dumps({'speech': 'O taverneiro é Lehtinan.', 'used_facts': [],
                          'unknown': False}, ensure_ascii=False)
        self.assertIn('THIRD_PARTY:ROLE', validate_reply(raw, context(OWNER)).reasons)


if __name__ == '__main__':
    unittest.main()
