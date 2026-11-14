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
from infinity_ai.dialogue.validate import retry_hint, validate_reply  # noqa: E402

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

    def test_trait_with_the_subject_left_out(self):
        """qwen3:30b-a3b, 2026-11-14: traits in a later clause without the name."""
        ctx = context(OWNER)
        for speech in ('Lehtinan? Dono da taverna. Não fala muito, mas é bom com os clientes.',
                       'Lehtinan? Dono da Coroa. Não fala muito com os clientes.',
                       'Lehtinan é o dono. Ele bebe demais.',
                       'O dono é Lehtinan, mas é avarento.'):
            with self.subTest(speech=speech):
                self.assertEqual(third_party_claim(speech, ctx), 'TRAIT')
        for speech in ('Lehtinan? Dono da taverna. Não me importo com ele.',
                       'É Lehtinan. É o que sei.',
                       'Lehtinan é o dono. Fala com ele.',
                       'Lehtinan é o dono. Acho que é avarento.',
                       'Não falo muito com ninguém. Lehtinan é o dono.',
                       'Moro em Athkatla. É bom aqui.'):
            with self.subTest(speech=speech):
                self.assertIsNone(third_party_claim(speech, ctx))

    def test_numbers_follow_what_one_knows(self):
        speech = 'Amn é governado pelo Conselho dos Seis! Eles decidem tudo há décadas!'
        self.assertEqual(third_party_claim(speech, context(COUNCIL_POPULAR)), 'NUMBER')
        self.assertIsNone(third_party_claim(speech, context(COUNCIL_STUDIED)))
        self.assertIsNone(third_party_claim('Governam Amn há muito tempo.', context(COUNCIL_POPULAR)))
        # CR-2026-006: "acho" does not make a number or a duration acceptable.
        self.assertEqual(third_party_claim('O Conselho governa Amn há séculos, eu acho.',
                                           context(COUNCIL_POPULAR)), 'NUMBER')
        self.assertIsNone(third_party_claim('Acho que Lehtinan é um cara duro.', context(OWNER)))
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



class RetryHintTests(unittest.TestCase):
    """The retry explains what to fix in Portuguese, without internal codes."""

    def test_hint_explains_each_refusal(self):
        hint = retry_hint(('THIRD_PARTY:ROLE',))
        self.assertIn('papel ou função que não está no que você sabe', hint)
        self.assertIn('diga que não sabe', hint)
        self.assertNotIn('THIRD_PARTY', hint)
        self.assertIn('trabalha', retry_hint(('SELF_CLAIM:WORK',)))
        self.assertIn('posse, cargo ou parentesco', retry_hint(('SELF_CLAIM',)))
        self.assertIn('(Gorion, Khalid)', retry_hint(('UNKNOWN_NAMES:Gorion,Khalid',)))
        both = retry_hint(('UNKNOWN_FACT_IDS:F6', 'THIRD_PARTY:NUMBER'))
        self.assertIn('cite só ids', both)
        self.assertIn('número, idade ou tempo', both)
        self.assertIn('não seguiu as regras', retry_hint(('ALGO_NOVO',)))
        self.assertIn('repetiu a pergunta', retry_hint(('ECHO',)))

    def test_echo_of_the_question_is_refused(self):
        def raw(speech):
            return json.dumps({'speech': speech, 'used_facts': [], 'unknown': False},
                              ensure_ascii=False)
        ctx = context(COUNCIL_POPULAR)
        self.assertIn('ECHO', validate_reply(raw('E quem é então?'), ctx, 'E quem é então?').reasons)
        self.assertIn('ECHO', validate_reply(raw('E quem é, então?!'), ctx, 'e quem é então').reasons)
        self.assertNotIn('ECHO', validate_reply(raw('Quem governa? O Conselho dos Seis.'), ctx,
                                                'Quem governa?').reasons)
        self.assertNotIn('ECHO', validate_reply(raw('E quem é então?'), ctx).reasons)

    def test_engine_sends_the_hint_on_retry(self):
        import tempfile
        from infinity_ai.dialogue.context import Catalog
        from infinity_ai.dialogue.engine import DialogueEngine, ResidentRequest
        from infinity_ai.dialogue.llm import FakeProvider
        from infinity_ai.state.store import ROOT_BRANCH, CampaignStore
        good = json.dumps({'speech': 'Não trabalho aqui, só passo.', 'used_facts': [],
                           'unknown': False}, ensure_ascii=False)
        with tempfile.TemporaryDirectory() as d:
            store = CampaignStore.open(Path(d) / 'c.sqlite3', 'lab')
            try:
                provider = FakeProvider([
                    json.dumps({'speech': 'O taverneiro é Garoll.', 'used_facts': [],
                                'unknown': False}, ensure_ascii=False), good])
                engine = DialogueEngine(store, provider, Catalog.load())
                result = engine.respond_resident(
                    ResidentRequest('npc:cre-x', 'Campesino(a)', 'Quem é o taverneiro?',
                                    'AR0406', False),
                    residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10)
            finally:
                store.close()
        self.assertEqual(len(provider.calls), 2)
        retry = provider.calls[1][-1]['content']
        self.assertTrue(retry.startswith('A resposta anterior foi recusada:'), retry)
        self.assertNotIn('THIRD_PARTY', retry)
        self.assertNotIn('UNKNOWN_NAMES', retry)
        self.assertEqual(result.speech, 'Não trabalho aqui, só passo.')

if __name__ == '__main__':
    unittest.main()
