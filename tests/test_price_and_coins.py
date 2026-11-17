# SPDX-License-Identifier: Apache-2.0
"""CR-2026-028: coin words and concrete prices need backing in what the person knows (lab,
2026-11-17: Bernard, asked "Quanto vale uma boa espada aqui?"). Bernard's store sells weapons, so
"tenho uma no estoque" is true for him; a seller offering what it sells must keep passing."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.dialogue.context import DialogueContext, Fact, Persona  # noqa: E402
from infinity_ai.dialogue.validate import retry_hint, validate_reply  # noqa: E402

LAB_REPLY = ('A espada de qualidade custa 150 a 200 golds, dependendo da qualidade. '
             'Eu tenho uma no estoque, mas é de segunda mão.')
LAB_QUESTION = 'Quanto vale uma boa espada aqui?'
COINS = Fact('K1', 'canon:topic:amnian-currency',
             'Moedas amnianas: O danter de ouro e o fandar de cobre são as moedas do dia a dia.', 0)


def bernard(occupation='taverneiro da Coroa de Cobre',
            facts=('Você serve bebida no balcão da Coroa de Cobre e conhece bem a freguesia da '
                   'casa.',), knowledge=(COINS,)):
    persona = Persona('npc:cre-bernard', 'Bernard', (), frozenset({'Bernard'}), '...')
    return DialogueContext(
        persona, tuple(Fact(f'F{i}', f'identity:npc:cre-bernard:{i}', t, 0)
                       for i, t in enumerate(facts, 1)),
        frozenset({'Bernard', 'Coroa', 'Cobre', 'Athkatla', 'Amn'}), (), knowledge=knowledge,
        resident_of='a Coroa de Cobre, nas Favelas', occupation=occupation,
        standing='HABITANTE', staff=True)


def reasons(speech, question=LAB_QUESTION, **kw):
    raw = json.dumps({'speech': speech, 'used_facts': [], 'unknown': False}, ensure_ascii=False)
    return validate_reply(raw, bernard(**kw), question).reasons


class LabReplyTests(unittest.TestCase):
    def test_the_lab_reply_is_refused_for_coin_and_price(self):
        found = reasons(LAB_REPLY)
        self.assertIn('UNBACKED_DETAIL:golds', found)
        self.assertIn('UNBACKED_DETAIL:PRICE', found)
        self.assertFalse(any(r.startswith('SELF_CLAIM') for r in found), found)  # true for him

    def test_the_retry_hint_is_plain_portuguese(self):
        hint = retry_hint(reasons(LAB_REPLY))
        self.assertIn('preço', hint)
        self.assertIn('moedas', hint)
        self.assertNotRegex(hint, r'UNBACKED|PRICE|golds')
        self.assertIsNone(re.search(r'\b[A-Z_]{4,}\b', hint))

    def test_the_price_hint_does_not_push_a_seller_to_deny_or_not_know(self):
        # Maintainer, 2026-11-17: a seller never says it does not offer what it sells, nor that
        # it does not know. The price hint asks only to drop the numbers.
        hint = retry_hint(('UNBACKED_DETAIL:PRICE',))
        self.assertNotIn('não sabe', hint)
        self.assertNotIn('não vend', hint)

    def test_a_seller_offering_what_it_sells_passes(self):
        for speech, question in (
                ('Temos cerveja, sim, e quartos lá em cima. Quer um?', 'Tem quarto e cerveja?'),
                ('Tenho cerveja à venda e um quarto livre esta noite.', 'Tem quarto e cerveja?'),
                ('Posso te vender uma caneca agora mesmo.', 'Tem quarto e cerveja?'),
                ('Eu tenho uma no estoque, mas é de segunda mão.', LAB_QUESTION),
                ('Tenho espadas no balcão, sim. Quer ver?', LAB_QUESTION)):
            with self.subTest(speech):
                self.assertEqual(reasons(speech, question), ())

    def test_the_offer_without_the_invented_numbers_passes(self):
        for speech in ('Tenho uma boa espada no estoque. Venha ao balcão e acertamos o preço.',
                       'Uma espada boa não sai barata, mas tenho uma aqui. Paga em danter de '
                       'ouro?'):
            with self.subTest(speech):
                self.assertEqual(reasons(speech), ())


class CoinWordTests(unittest.TestCase):
    def test_english_coin_words_and_table_abbreviations_need_backing(self):
        cases = {'Pago em gold, se quiser.': 'gold',
                 'Isso sai por umas moedas de silver.': 'silver',
                 'Uns 200 po, talvez.': 'po',
                 'Acho que uns 50gp.': 'gp'}
        for speech, word in cases.items():
            with self.subTest(speech):
                self.assertIn('UNBACKED_DETAIL:' + word, reasons(speech))

    def test_a_coin_word_the_player_used_is_backed(self):
        found = reasons('Gold? Aqui ninguém fala assim; é danter.', 'Quanto é em gold?')
        self.assertFalse(any(r.startswith('UNBACKED_DETAIL') for r in found), found)

    def test_portuguese_coins_backed_by_the_currency_item(self):
        self.assertEqual(reasons('Moedas de ouro e de cobre: o danter e o fandar.'), ())
        self.assertIn('UNBACKED_DETAIL:prata', reasons('Moedas de prata, sim.'))
        self.assertIn('UNBACKED_DETAIL:ouro', reasons('Peças de ouro, sim.', knowledge=()))


class PriceTests(unittest.TestCase):
    def test_an_amount_of_money_without_backing_is_refused(self):
        for speech in ('Custa 150, mais ou menos.', 'Uns 150 a 200 danters.',
                       'Dez peças de ouro, no mínimo.', 'Sai por 30 fandars.',
                       'Cobro 5 moedas por noite.'):
            with self.subTest(speech):
                self.assertIn('UNBACKED_DETAIL:PRICE', reasons(speech))

    def test_a_price_in_what_the_person_knows_or_the_player_said_passes(self):
        beer = Fact('F2', 'identity:npc:cre-bernard:2',
                    'Uma caneca de cerveja da casa custa 2 fandars.', 0)
        self.assertNotIn('UNBACKED_DETAIL:PRICE',
                         reasons('A cerveja custa 2 fandars.', 'Quanto é a cerveja?',
                                 facts=(beer.text,)))
        self.assertNotIn('UNBACKED_DETAIL:PRICE',
                         reasons('10 moedas? É pouco para isso.', 'Te pago 10 moedas.'))

    def test_other_numbers_are_not_prices(self):
        for speech in ('Moro aqui há 3 anos.', 'Vale a pena, mas custa caro.',
                       'Não sei o preço de espadas.', 'Tem 2 ferreiros no bairro, acho.'):
            with self.subTest(speech):
                self.assertNotIn('UNBACKED_DETAIL:PRICE', reasons(speech))


if __name__ == '__main__':
    unittest.main()


class StorePriceTests(unittest.TestCase):
    """ADR-0132 + CR-2026-028: the store's prices in the seller's facts back what it says."""

    def test_store_prices_back_the_seller_and_invented_ones_are_refused(self):
        from infinity_ai.dialogue.offers import offer_facts
        from infinity_ai.gamedata.inventory import Offer
        offer = Offer('Taverna de Teste', ('INN',), rooms=(('PEASANT', 2),),
                      drinks=(('Cerveja da Casa', 2),),
                      items=(('Espada de Ferro', 20, 'ARMAS'),))
        question = 'Quanto custa uma espada?'
        facts = tuple(Fact(f'F{i}', f'offer:x:{i}', t, 0)
                      for i, t in enumerate(offer_facts(offer, question), 1))
        persona = Persona('npc:x', 'Taverneiro', 'curto', frozenset({'Taverneiro'}), 'Hum?')
        context = DialogueContext(persona, facts, frozenset({'Taverneiro', 'Espada', 'Ferro'}), (),
                                  offer=offer)

        def reply(speech):
            return validate_reply(json.dumps({'speech': speech, 'used_facts': [], 'unknown': False}),
                                  context, question)
        self.assertTrue(reply('A Espada de Ferro custa 20 peças de ouro.').ok)
        refused = reply('A Espada de Ferro custa 150 a 200 golds.')
        self.assertIn('UNBACKED_DETAIL:PRICE', refused.reasons)
        self.assertTrue(any(r.startswith('UNBACKED_DETAIL:') and 'golds' in r for r in refused.reasons))
