# SPDX-License-Identifier: Apache-2.0
"""ADR-0132: what a person sells comes from the game's stores; a seller never denies it.

Every byte and value here is made up for the test (REQ-CANON-004): no game data in the repo.
"""
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.dialogue.context import Catalog, DialogueContext, Persona, build_resident_context  # noqa: E402
from infinity_ai.dialogue.engine import DialogueEngine, DialogueStatus, ResidentRequest  # noqa: E402
from infinity_ai.dialogue.llm import FakeProvider  # noqa: E402
from infinity_ai.dialogue.offers import (  # noqa: E402
    denied_offer, offer_facts, offer_line, offered,
)
from infinity_ai.dialogue.validate import retry_hint, validate_reply  # noqa: E402
from infinity_ai.gamedata.formats import (  # noqa: E402
    GameDataError, parse_cre_dialog, parse_dlg_store_refs, parse_itm_summary, parse_sto,
)
from infinity_ai.gamedata.inventory import (  # noqa: E402
    Offer, StoreInventory, _merge_stores, load_local_offers, write_inventory,
)
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

TAVERN = Offer('Taverna de Teste', ('INN',), rooms=(('PEASANT', 2), ('MERCHANT', 7)),
               drinks=(('Cerveja da Casa', 2), ('Vinho Tinto', 5)),
               items=(('Flecha Comum', 0, 'ARMAS'), ('Pedra de Funda', 1, 'ARMAS'),
                      ('Adaga Simples', 3, 'ARMAS'), ('Espada de Ferro', 20, 'ARMAS'),
                      ('Espada de Ferro +2', 900, 'ARMAS'), ('Flecha Comum +1', 30, 'ARMAS'),
                      ('Escudo de Pinho', 6, 'ESCUDOS')))


def cre(dialog: bytes) -> bytes:
    data = bytearray(0x2D4)
    data[:8] = b'CRE V1.0'
    data[0x2CC:0x2CC + len(dialog)] = dialog
    return bytes(data)


def dlg(*actions: str) -> bytes:
    head = bytearray(0x30)
    head[:8] = b'DLG V1.0'
    table_at = len(head)
    texts_at = table_at + 8 * len(actions)
    table, blob = b'', b''
    for a in actions:
        raw = a.encode('latin-1')
        table += struct.pack('<II', texts_at + len(blob), len(raw))
        blob += raw
    struct.pack_into('<II', head, 0x28, table_at, len(actions))
    return bytes(head) + table + blob


def sto(*, kind=2, name=7, flags=0x41, markup=150, items=(b'XSWORD',), drinks=((9, 2),),
        rooms=(0x3, 2, 7, 11, 15)) -> bytes:
    head = bytearray(0x9C)
    head[:8] = b'STORV1.0'
    struct.pack_into('<IiII', head, 0x08, kind, name, flags, markup)
    items_at = len(head)
    drinks_at = items_at + 28 * len(items)
    body = b''.join(ref.ljust(8, b'\0') + bytes(20) for ref in items)
    body += b''.join(bytes(8) + struct.pack('<Iii', strref, price, 0) for strref, price in drinks)
    struct.pack_into('<II', head, 0x34, items_at, len(items))
    struct.pack_into('<II', head, 0x4C, drinks_at, len(drinks))
    struct.pack_into('<IIIII', head, 0x5C, *rooms)
    struct.pack_into('<II', head, 0x70, drinks_at + 20 * len(drinks), 0)
    return bytes(head) + body


def itm(name=11, price=20, item_type=20) -> bytes:
    data = bytearray(0x38)
    data[:4] = b'ITM '
    struct.pack_into('<II', data, 0x08, 0xFFFFFFFF, name)
    struct.pack_into('<H', data, 0x1C, item_type)
    struct.pack_into('<I', data, 0x34, price)
    return bytes(data)


class FormatTests(unittest.TestCase):
    def test_the_dialogue_says_which_stores_it_opens(self):
        self.assertEqual(parse_cre_dialog(cre(b'XTALK')), 'XTALK')
        self.assertEqual(parse_cre_dialog(cre(b'None')), '')
        refs = parse_dlg_store_refs(dlg('SetGlobal("x","GLOBAL",1)', 'StartStore("xinn",LastTalkedToBy())',
                                        'StartStore("XINN2",Myself) StartStore("xinn",Myself)'))
        self.assertEqual(refs, ('XINN', 'XINN2'))
        with self.assertRaises(GameDataError):
            parse_dlg_store_refs(b'not a dialogue file at all, long enough to read..........')

    def test_a_store_lists_only_what_its_flags_say_it_sells(self):
        store = parse_sto(sto())
        self.assertEqual(store.kind, 'INN')
        self.assertEqual(store.rooms, (('PEASANT', 2), ('MERCHANT', 7)))
        self.assertEqual(store.drinks, ((9, 2),))
        self.assertEqual(store.items, ('XSWORD',))
        closed = parse_sto(sto(flags=0x00))                 # neither sells items nor drinks
        self.assertEqual((closed.items, closed.drinks), ((), ()))
        item = parse_itm_summary(itm())
        self.assertEqual((item.name, item.price, item.item_type), (11, 20, 20))

    def test_two_stores_of_one_person_merge_at_the_lowest_markup(self):
        a, b = parse_sto(sto(markup=150)), parse_sto(sto(markup=100, items=(b'XSWORD', b'XSHLD')))
        info = {'XSWORD': parse_itm_summary(itm()), 'XSHLD': parse_itm_summary(itm(12, 6, 12))}
        offer = _merge_stores([a, b], info, {}, {7: 'Taverna de Teste', 9: 'Cerveja da Casa',
                                                 11: 'Espada de Ferro', 12: 'Escudo de Pinho'})
        self.assertEqual(offer.place, 'Taverna de Teste')
        self.assertIn(('Espada de Ferro', 20, 'ARMAS'), offer.items)
        self.assertIn(('Escudo de Pinho', 6, 'ESCUDOS'), offer.items)
        self.assertEqual(offer.drinks, (('Cerveja da Casa', 2),))

    def test_the_inventory_stays_out_of_the_repository(self):
        inv = StoreInventory('sha256:' + 'ab' * 32, 'pt_BR', {'npc:x': TAVERN}, 'now')
        with tempfile.TemporaryDirectory() as tmp:
            write_inventory(inv, Path(tmp))
            self.assertEqual(load_local_offers(inv.build_fingerprint, 'pt_BR', Path(tmp)),
                             {'npc:x': TAVERN})
            self.assertEqual(load_local_offers('sha256:' + 'cd' * 32, 'pt_BR', Path(tmp)), {})
        with self.assertRaises(GameDataError):
            write_inventory(inv, ROOT / 'knowledge')


class OfferTests(unittest.TestCase):
    def test_facts_say_what_is_sold_and_the_items_asked(self):
        facts = offer_facts(TAVERN, 'Vocês vendem espadas?')
        self.assertIn('quartos (camponês 2, mercador 7 peças de ouro por noite)', facts[0])
        self.assertIn('Cerveja da Casa 2', facts[0])
        self.assertIn('armas, escudos', facts[0])
        self.assertTrue(facts[1].startswith('Na sua loja, armas:'))
        self.assertIn('Espada de Ferro (20 peças de ouro)', facts[1])
        self.assertEqual(offer_facts(None, 'Vocês vendem espadas?'), [])
        self.assertEqual(offered(TAVERN), {'QUARTOS', 'BEBIDAS', 'ARMAS', 'ESCUDOS'})

    def test_lab_the_plural_finds_the_item_and_free_items_are_left_out(self):   # 2026-11-17
        line = offer_facts(TAVERN, 'E você vende espadas?')[1]
        self.assertTrue(line.startswith('Na sua loja, armas: Espada de Ferro (20 peças de ouro)'))
        self.assertNotIn('Flecha Comum', ' '.join(offer_facts(TAVERN, 'Vende flechas?')))
        self.assertIn('Pedra de Funda (1 peça de ouro)', offer_facts(TAVERN, 'Tem armas?')[1])
        self.assertNotIn('preço a combinar', ' '.join(offer_facts(TAVERN, 'Tem armas?')))

    def test_lab_an_enchanted_item_is_special_not_plus_one(self):         # 2026-11-17
        line = offer_facts(TAVERN, 'Você vende espadas?')[1]
        self.assertNotIn('+2', line)
        self.assertIn('algumas peças especiais, encantadas e de alta qualidade, bem mais caras '
                      '(a partir de 900 peças de ouro)', line)
        self.assertNotIn('+2', offer_line(TAVERN, 'Você vende espadas?'))

    def test_a_denial_of_what_is_sold_is_found(self):
        self.assertEqual(denied_offer('Não temos quartos aqui.', 'Tem quarto?', TAVERN), 'QUARTOS')
        self.assertEqual(denied_offer('Aqui não vendo armas, amigo.', 'E armas?', TAVERN), 'ARMAS')
        self.assertEqual(denied_offer('Não sei.', 'Quanto custa a cerveja?', TAVERN), 'BEBIDAS')
        self.assertIsNone(denied_offer('Temos, sim: a Cerveja da Casa custa 2.', 'Tem cerveja?',
                                       TAVERN))
        self.assertIsNone(denied_offer('Não vendo cavalos.', 'Vende cavalos?', TAVERN))
        self.assertIsNone(denied_offer('Não temos quartos.', 'Tem quarto?', None))   # no store

    def test_the_seller_line_names_the_goods(self):
        self.assertEqual(offer_line(TAVERN, 'Tem quarto?'),
                         'Temos quartos, sim: camponês 2, mercador 7 peças de ouro por noite.')
        self.assertEqual(offer_line(TAVERN, 'E cerveja?'),
                         'Temos, sim: Cerveja da Casa por 2 peças de ouro, Vinho Tinto por 5 peças de ouro.')
        self.assertEqual(offer_line(TAVERN, 'Tem vinho tinto?'), 'Temos, sim: Vinho Tinto por 5 peças de ouro.')
        self.assertIn('Espada de Ferro por 20 peças de ouro', offer_line(TAVERN, 'Tem espada?'))
        self.assertIsNone(offer_line(None, 'Tem quarto?'))


class ValidatorTests(unittest.TestCase):
    def context(self, offer=TAVERN):
        persona = Persona('npc:x', 'Taverneiro', 'curto', frozenset({'Taverneiro'}), 'Hum?')
        return DialogueContext(persona, (), frozenset({'Taverneiro'}), (), offer=offer)

    def test_denying_what_one_sells_is_refused(self):
        raw = '{"speech": "Não temos quartos.", "used_facts": [], "unknown": false}'
        verdict = validate_reply(raw, self.context(), 'Vocês têm quartos?')
        self.assertIn('SELF_CLAIM:OFFER', verdict.reasons)
        self.assertIn('você vende isso', retry_hint(verdict.reasons))
        self.assertTrue(validate_reply(raw, self.context(None), 'Vocês têm quartos?').ok)


class EngineTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def ask(self, replies, question):
        provider = FakeProvider([f'{{"speech": "{r}", "used_facts": [], "unknown": false}}'
                                 for r in replies])
        return DialogueEngine(self.store, provider, Catalog.load()).respond_resident(
            ResidentRequest('npc:x', 'Taverneiro', question, 'AR0406', False),
            residence_areas=('AR0406',), branch_id=ROOT_BRANCH, at_game_time=10, offer=TAVERN)

    def test_the_offer_reaches_the_prompt_as_a_fact(self):
        context = build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:x',
            display_name='Taverneiro', residence_areas=('AR0406',), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, question='Tem quarto?', offer=TAVERN).context
        self.assertTrue(any(f.text.startswith('Você vende na Taverna de Teste') for f in context.facts))
        self.assertIsNone(context.absence)

    def test_a_seller_that_keeps_denying_answers_with_its_goods(self):
        reply = self.ask(['Não temos quartos.', 'Não temos quartos, não.'], 'Vocês têm quartos?')
        self.assertEqual(reply.status, DialogueStatus.FALLBACK)
        self.assertEqual(reply.speech,
                         'Temos quartos, sim: camponês 2, mercador 7 peças de ouro por noite.')
        good = self.ask(['Temos, sim: camponês 2 peças de ouro.'], 'Vocês têm quartos?')
        self.assertEqual(good.status, DialogueStatus.OK)


if __name__ == '__main__':
    unittest.main()
