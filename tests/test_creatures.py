# SPDX-License-Identifier: Apache-2.0
"""ADR-0137 (P3b): our creature file built from a curated sheet (synthetic base and sheet)."""
import copy
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.actions.creatures import (  # noqa: E402
    COLOR_FIELDS, EFFECT_SIZE, INVENTORY_SLOTS, SHEET_SCHEMA, SLOT_WORDS, Effect, build_creature,
    choose_item, parse_sheet, vision_effects,
)
from infinity_ai.actions.gateway import ActionError  # noqa: E402
from infinity_ai.personality.identity import load_curations  # noqa: E402
from infinity_ai.canon.pack import load_partition  # noqa: E402

SHEET = {
    'schema': SHEET_SCHEMA, 'sheet_id': 'teste:clériga', 'game': 'BG1', 'name': 'Clériga de Teste',
    'race': 'HUMAN', 'class': 'CLERIC', 'gender': 'FEMALE', 'alignment': 'NEUTRAL_EVIL',
    'level': 10, 'hp': 70, 'ac': -5, 'thac0': 9, 'attacks': 1, 'xp_value': 5000, 'gold': 125,
    'morale': 16, 'abilities': {'str': 17, 'dex': 16, 'con': 15, 'int': 13, 'wis': 18, 'cha': 14},
    'saves': {'death': 6, 'wands': 10, 'poly': 9, 'breath': 10, 'spells': 11},
    'items': [{'slot': 'ARMOR', 'name': 'Armadura de Teste'},
              {'slot': 'WEAPON1', 'name': 'Maça de Teste'},
              {'slot': 'SHIELD', 'name': 'Escudo de Teste'}],
}


def base_cre():
    """A living commoner laid out like the lab's base: header, 17 memorization entries, one item,
    40 slot words; scripts, a dialogue and a non-neutral allegiance to be replaced."""
    head = bytearray(0x2D4)
    head[:8] = b'CRE V1.0'
    struct.pack_into('<II', head, 0x08, 111, 112)
    struct.pack_into('<I', head, 0x28, 0x4101)
    head[0x248:0x250] = b'WANDER\0\0'
    head[0x270] = 200
    head[0x280:0x286] = b'MTEST1'
    head[0x2CC:0x2D2] = b'MTEST1'
    meminfo = bytes(range(16)) * 17
    item = b'DAGG01\0\0' + struct.pack('<HHHHI', 0, 1, 0, 0, 0)
    slots = [0xFFFF] * SLOT_WORDS
    slots[9] = 0
    meminfo_at, items_at = 0x2D4, 0x2D4 + len(meminfo)
    slots_at = items_at + len(item)
    struct.pack_into('<IIIIIIIIIII', head, 0x2A0, meminfo_at, 0, meminfo_at, 17, items_at, 0,
                     slots_at, items_at, 1, items_at, 0)
    return bytes(head) + meminfo + item + struct.pack(f'<{SLOT_WORDS}H', *slots)


class SheetTests(unittest.TestCase):
    def test_a_complete_sheet(self):
        sheet = parse_sheet(SHEET)
        self.assertEqual((sheet.race, sheet.klass, sheet.gender, sheet.alignment),
                         (1, 3, 2, 0x23))
        self.assertEqual(sheet.abilities, (17, 16, 15, 13, 18, 14))
        self.assertEqual(sheet.items[0], ('ARMOR', 'Armadura de Teste'))

    def test_bad_fields_are_named(self):
        for change, code in ((lambda d: d.update(schema='x'), 'BAD_SHEET'),
                             (lambda d: d.update(race='DRAGAO'), 'BAD_SHEET_RACE'),
                             (lambda d: d.update(hp=0), 'BAD_SHEET_HP'),
                             (lambda d: d.update(level=True), 'BAD_SHEET_LEVEL'),
                             (lambda d: d['abilities'].pop('wis'), 'BAD_SHEET_WIS'),
                             (lambda d: d['items'].append({'slot': 'ARMOR', 'name': 'x'}),
                              'BAD_SHEET_ITEMS'),
                             (lambda d: d['items'].append({'slot': 'BOLSO', 'name': 'x'}),
                              'BAD_SHEET_ITEMS'),
                             (lambda d: d.update(colors={'metal': 14}), 'BAD_SHEET_COLORS'),
                             (lambda d: d.update(colors=dict.fromkeys(COLOR_FIELDS, 256)),
                              'BAD_SHEET_METAL')):
            doc = copy.deepcopy(SHEET)
            change(doc)
            with self.assertRaises(ActionError) as ctx:
                parse_sheet(doc)
            self.assertEqual(ctx.exception.code, code)


class BuildTests(unittest.TestCase):
    def build(self, items=None, sheet=SHEET, effects=()):
        return build_creature(base_cre(), parse_sheet(sheet), script_name='INFAI_TESTE',
                              name_strref=11910, animation=0x6010,
                              items={'ARMOR': 'PLAT05', 'WEAPON1': 'BLUN03', 'SHIELD': 'SHLD06'}
                              if items is None else items, effects=effects)

    def test_colors_and_the_vision_look(self):
        self.assertEqual(self.build()[0x2C:0x33], base_cre()[0x2C:0x33])    # no colors: the base's
        colored = dict(SHEET, colors=dict(zip(COLOR_FIELDS, (14, 47, 197, 10, 29, 83, 136))))
        d = self.build(sheet=colored, effects=vision_effects())
        self.assertEqual(list(d[0x2C:0x33]), [14, 47, 197, 10, 29, 83, 136])
        self.assertEqual(d[0x33], 1)                                     # EFF V2 effects
        slots_at, eff_at, eff_n = (struct.unpack_from('<I', d, 0x2B8)[0],
                                   *struct.unpack_from('<II', d, 0x2C4))
        self.assertEqual((eff_at, eff_n), (slots_at + 2 * SLOT_WORDS, 2))
        self.assertEqual(len(d), eff_at + 2 * EFFECT_SIZE)
        fx = [struct.unpack_from('<IIIIII', d, eff_at + EFFECT_SIZE * i + 8) for i in range(2)]
        self.assertEqual(fx[0], (66, 1, 0, 128, 0, 9))                   # translucent, permanent
        self.assertEqual(fx[1][0], 50)                                   # glow pulse
        self.assertEqual(fx[1][3], 200 << 8 | 220 << 16 | 255 << 24)     # pale: R, G, B bytes 2..4
        self.assertEqual(fx[1][4], 0xFF | 30 << 16)                      # whole body, slow cycle
        for i in range(2):
            at = eff_at + EFFECT_SIZE * i
            self.assertEqual(d[at:at + 8], bytes(8))
            self.assertEqual(struct.unpack_from('<HH', d, at + 0x24), (100, 0))
        for bad in (lambda: vision_effects(fade=255), lambda: vision_effects(rgb=(0, 0, 300))):
            with self.assertRaises(ActionError):
                bad()
        with self.assertRaises(ActionError):
            self.build(effects=(Effect(-1),))

    def test_identity_stats_and_neutrality(self):
        d = self.build()
        u8 = lambda o: d[o]                                   # noqa: E731
        self.assertEqual(struct.unpack_from('<II', d, 0x08), (11910, 11910))
        self.assertEqual(struct.unpack_from('<I', d, 0x14)[0], 5000)
        self.assertEqual(struct.unpack_from('<I', d, 0x1C)[0], 125)
        self.assertEqual(struct.unpack_from('<I', d, 0x20)[0], 0)
        self.assertEqual(struct.unpack_from('<hh', d, 0x24), (70, 70))
        self.assertEqual(struct.unpack_from('<I', d, 0x28)[0], 0x6010)
        self.assertEqual(struct.unpack_from('<hh', d, 0x46), (10, 10))
        self.assertEqual((u8(0x52), u8(0x53)), (9, 1))
        self.assertEqual(list(d[0x54:0x59]), [6, 10, 9, 10, 11])
        self.assertEqual(u8(0x234), 10)
        self.assertEqual(list(d[0x238:0x240]), [17, 0, 13, 18, 16, 15, 14, 16])
        self.assertEqual(d[0x248:0x270], bytes(40))                     # no AI scripts
        self.assertEqual((u8(0x270), u8(0x272), u8(0x273), u8(0x275), u8(0x27B)),
                         (128, 1, 3, 2, 0x23))
        self.assertEqual(d[0x280:0x2A0], b'INFAI_TESTE'.ljust(32, b'\0'))
        self.assertEqual(d[0x2CC:0x2D4], bytes(8))                      # no game dialogue

    def test_layout_items_and_slots(self):
        d = self.build()
        (known_at, known_n, mem_at, mem_n, memorized_at, memorized_n, slots_at, items_at,
         items_n, eff_at, eff_n) = struct.unpack_from('<IIIIIIIIIII', d, 0x2A0)
        self.assertEqual((known_n, mem_n, memorized_n, items_n, eff_n), (0, 17, 0, 3, 0))
        kept = (bytes(range(2)) + bytes(4) + bytes(range(6, 8)) + bytes(8)) * 17
        self.assertEqual(d[mem_at:mem_at + 16 * 17], kept)   # level and type kept, no counts
        resrefs = [d[items_at + 20 * i:items_at + 20 * i + 8].rstrip(b'\0').decode()
                   for i in range(items_n)]
        self.assertEqual(resrefs, ['PLAT05', 'SHLD06', 'BLUN03'])        # slot order
        slots = struct.unpack_from(f'<{SLOT_WORDS}H', d, slots_at)
        self.assertEqual((slots[1], slots[2], slots[9]), (0, 1, 2))      # armor, shield, weapon
        self.assertEqual(slots[38], 0)                                   # weapon 1 selected
        self.assertEqual(len(d), slots_at + 2 * SLOT_WORDS)
        self.assertEqual(eff_at, len(d))                                 # no effects by default
        flags = struct.unpack_from('<I', d, items_at + 16)[0]
        self.assertEqual(flags & 1, 1)                                   # identified

    def test_missing_items_and_bad_bases(self):
        d = self.build(items={'ARMOR': 'PLAT05'})
        slots_at, items_at, items_n = struct.unpack_from('<III', d, 0x2B8)
        self.assertEqual(items_n, 1)
        self.assertEqual(struct.unpack_from(f'<{SLOT_WORDS}H', d, slots_at)[38], 1000)   # fist
        corpse = bytearray(base_cre())
        corpse[0x20:0x24] = (0x800).to_bytes(4, 'little')
        for base, code in ((bytes(corpse), 'DEAD_SOURCE_CRE'), (b'BAM V1  ', 'BAD_SOURCE_CRE')):
            with self.assertRaises(ActionError) as ctx:
                build_creature(base, parse_sheet(SHEET), script_name='INFAI_TESTE',
                               name_strref=1, animation=0x6010, items={})
            self.assertEqual(ctx.exception.code, code)
        with self.assertRaises(ActionError):
            build_creature(base_cre(), parse_sheet(SHEET), script_name='Tamoko', name_strref=1,
                           animation=0x6010, items={})
        # a morale at or under the body's break makes the creature flee as it is born
        timid = bytearray(base_cre())
        timid[0x240] = 7
        for morale, code in ((6, 'MORALE_BELOW_BREAK'), (7, 'MORALE_BELOW_BREAK'), (8, None)):
            sheet = parse_sheet(dict(SHEET, morale=morale))
            if code is None:
                d = build_creature(bytes(timid), sheet, script_name='INFAI_TESTE', name_strref=1,
                                   animation=0x6010, items={})
                self.assertEqual((d[0x23F], d[0x240]), (8, 7))
                continue
            with self.assertRaises(ActionError) as ctx:
                build_creature(bytes(timid), sheet, script_name='INFAI_TESTE', name_strref=1,
                               animation=0x6010, items={})
            self.assertEqual(ctx.exception.code, code)
        with self.assertRaises(ActionError):
            build_creature(base_cre(), parse_sheet(SHEET), script_name='INFAI_TESTE',
                           name_strref=1, animation=0x6010, items={'BOLSO': 'X'})


class MonsterAndBackpackTests(unittest.TestCase):
    """ADR-0141: a creature that is not a character, the backpack and the item choice."""
    JAILER = dict(SHEET, sheet_id='teste:verbeeg', race='BASE', **{'class': 'FIGHTER'},
                  alignment='NEUTRAL_EVIL', gender='MALE', level=5, hp=28, thac0=15, attacks=2,
                  natural_ac=4, str_extra=76,
                  items=[{'slot': 'WEAPON1', 'name': 'Clava', 'resref': 'BLUN01'},
                         {'slot': 'SHIELD', 'name': 'Escudo Médio'}])

    def test_new_fields_and_pins_are_strict(self):
        sheet = parse_sheet(self.JAILER)
        self.assertEqual((sheet.race, sheet.natural_ac, sheet.str_extra), (0, 4, 76))
        self.assertEqual(sheet.pinned, (('WEAPON1', 'Clava', 'BLUN01'),))
        two = dict(SHEET, items=[{'slot': 'INVENTORY', 'name': 'a'},
                                 {'slot': 'INVENTORY', 'name': 'b'}])
        self.assertEqual([s for s, _ in parse_sheet(two).items], ['INVENTORY', 'INVENTORY'])
        for change, code in (({'natural_ac': 11}, 'BAD_SHEET_NATURAL_AC'),
                             ({'str_extra': 101}, 'BAD_SHEET_STR_EXTRA'),
                             ({'race': 'GIGANTE'}, 'BAD_SHEET_RACE'),
                             ({'items': [{'slot': 'ARMOR', 'name': 'x', 'resref': 'A B'}]},
                              'BAD_SHEET_ITEMS'),
                             ({'items': [{'slot': 'INVENTORY', 'name': 'x'}] * 17},
                              'BAD_SHEET_ITEMS')):
            with self.assertRaises(ActionError) as ctx:
                parse_sheet(dict(self.JAILER, **change))
            self.assertEqual(ctx.exception.code, code)

    def test_body_race_ac_strength_backpack_and_carry(self):
        body = bytearray(base_cre())
        body[0x271], body[0x272] = 5, 113                      # a giant-kin body (ogre)
        d = build_creature(bytes(body), parse_sheet(self.JAILER), script_name='INFAI_TESTE',
                           name_strref=29887, animation=0xE251,
                           items=[('WEAPON1', 'BLUN01'), ('SHIELD', 'SHLD03'),
                                  ('INVENTORY', 'MISC01')],
                           carry=('SCRL3F',))
        self.assertEqual((d[0x271], d[0x272], d[0x273]), (5, 113, 2))   # body kept, fighter
        self.assertEqual(struct.unpack_from('<hh', d, 0x46), (4, 4))
        self.assertEqual((d[0x238], d[0x239]), (17, 76))
        slots_at, items_at, items_n = struct.unpack_from('<III', d, 0x2B8)
        refs = [d[items_at + 20 * i:items_at + 20 * i + 8].rstrip(b'\0').decode()
                for i in range(items_n)]
        self.assertEqual(refs, ['SHLD03', 'BLUN01', 'MISC01', 'SCRL3F'])
        slots = struct.unpack_from(f'<{SLOT_WORDS}H', d, slots_at)
        self.assertEqual((slots[2], slots[9], slots[INVENTORY_SLOTS[0]], slots[INVENTORY_SLOTS[1]]),
                         (0, 1, 2, 3))
        for i in (2, 3):                                        # identified, droppable
            self.assertEqual(struct.unpack_from('<I', d, items_at + 20 * i + 16)[0], 1)
        with self.assertRaises(ActionError):
            build_creature(base_cre(), parse_sheet(SHEET), script_name='INFAI_TESTE',
                           name_strref=1, animation=0x6010, items={},
                           carry=('X',) * 17)

    def test_the_item_choice_follows_the_slot_and_the_pin(self):
        swords = [('ARROPHEO', 15), ('MYBOLT', 15), ('SW1H08', 19), ('SW1H14', 19)]
        self.assertEqual(choose_item('ARMOR', 'Traje', [('CLCK09', 2)]), 'CLCK09')
        with self.assertRaises(ActionError) as ctx:                     # three fit a weapon slot
            choose_item('WEAPON1', 'Espada Curta +1', swords)
        self.assertEqual(ctx.exception.code, 'ITEM_AMBIGUOUS')
        self.assertEqual(choose_item('WEAPON1', 'Espada Curta +1', swords, 'sw1h08'), 'SW1H08')
        self.assertEqual(choose_item('INVENTORY', 'Diário', [('SCRL3F', 11)]), 'SCRL3F')
        for slot, pin, code in (('ARMOR', None, 'ITEM_NOT_FOUND'),           # no armor among them
                                ('WEAPON1', 'CLCK09', 'ITEM_PIN_MISMATCH')):
            with self.assertRaises(ActionError) as ctx:
                choose_item(slot, 'x', swords, pin)
            self.assertEqual(ctx.exception.code, code)


class CurationTests(unittest.TestCase):
    def test_gregor_and_kalessia_are_curated_and_the_hideout_does_not_leak(self):
        curations = load_curations(load_partition(1369))
        gregor, kalessia = curations['npc:infai_gregor'], curations['npc:infai_kalessia']
        self.assertEqual((gregor.standing, gregor.origin_region), ('FORASTEIRO', 'region:baldurs-gate'))
        self.assertEqual((kalessia.standing, kalessia.origin_region), ('FORASTEIRO', 'region:sembia'))
        self.assertEqual((len(gregor.self_facts), len(kalessia.self_facts)), (3, 3))
        told = ' '.join(gregor.self_facts).lower()
        for leak in ('docas', 'esconderijo', 'kalessia'):            # comes from the quest, later
            self.assertNotIn(leak, told)

    def test_the_draft_story_waits_for_approval(self):
        doc = json.loads((ROOT / 'knowledge' / 'npcs' / 'tamoko.pt_BR.json').read_text())
        self.assertEqual(doc['npc_id'], 'npc:infai_tamoko')         # the box's id from our name
        curations = load_curations(load_partition(1369))
        if doc['curation']['status'] == 'DRAFT':
            self.assertNotIn('npc:infai_tamoko', curations)         # not used before approval
        else:
            self.assertIn('npc:infai_tamoko', curations)


if __name__ == '__main__':
    unittest.main()
