# SPDX-License-Identifier: Apache-2.0
"""ADR-0137 (P3b): one of OUR creature files built from a curated sheet of another game.

A sheet (local only, CR-2026-030: the numbers come from a community database consulted per entity)
gives who the creature is: race, class, sex, alignment, level, hit points, armor class, THAC0,
attacks, abilities, saving throws, morale, experience value, gold and equipment by name. A living
CRE of the build gives the body (it is copied, never edited in place). The result keeps the base's
spell-memorization table, empties spells and effects, drops the base's scripts and dialogue (the
creature talks through our box, ADR-0136 D5: neutral, no combat), and lays out a new item table and
slot table with the sheet's items, found in the build by the same name (strref). Optional: the
sheet's seven body colors (gradient indices of the build's palette) and a few embedded effects, such
as the vision look (translucent, with a pale glow) that the campaign gives the dead.

Pure: the lab tool reads the base, the dialog.tlk name and the items, and deploys the bytes.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

from .gateway import ActionError, make_template

SHEET_SCHEMA = 'infinity-ai.creature-sheet.v1'
RACES = {'HUMAN': 1, 'ELF': 2, 'HALF_ELF': 3, 'DWARF': 4, 'HALFLING': 5, 'GNOME': 6, 'HALF_ORC': 7}
CLASSES = {'MAGE': 1, 'FIGHTER': 2, 'CLERIC': 3, 'THIEF': 4, 'BARD': 5, 'PALADIN': 6,
           'DRUID': 11, 'RANGER': 12}
GENDERS = {'MALE': 1, 'FEMALE': 2}
ALIGNMENTS = {'LAWFUL_GOOD': 0x11, 'LAWFUL_NEUTRAL': 0x12, 'LAWFUL_EVIL': 0x13,
              'NEUTRAL_GOOD': 0x21, 'NEUTRAL': 0x22, 'NEUTRAL_EVIL': 0x23,
              'CHAOTIC_GOOD': 0x31, 'CHAOTIC_NEUTRAL': 0x32, 'CHAOTIC_EVIL': 0x33}
# CRE V1.0 item slots (BG2): index of the slot word in the slot table.
SLOTS = {'HELMET': 0, 'ARMOR': 1, 'SHIELD': 2, 'GLOVES': 3, 'RING_LEFT': 4, 'RING_RIGHT': 5,
         'AMULET': 6, 'BELT': 7, 'BOOTS': 8, 'WEAPON1': 9, 'WEAPON2': 10, 'WEAPON3': 11,
         'WEAPON4': 12, 'CLOAK': 17}
SLOT_WORDS = 40                      # 38 slots + selected weapon + selected weapon ability
NEUTRAL_EA = 128
HEADER_SIZE = 0x2D4
ITEM_SIZE = 0x14
MEMINFO_SIZE = 0x10
EMPTY_SLOT = 0xFFFF
COLOR_FIELDS = ('metal', 'minor', 'major', 'skin', 'leather', 'armor', 'hair')   # CRE 0x2C..0x32
EFFECT_SIZE = 0x108                  # embedded EFF V2 (CRE effect version 1)
OP_GLOW_PULSE, OP_TRANSLUCENCY = 50, 66
TIMING_PERMANENT = 9


@dataclass(frozen=True)
class Sheet:
    sheet_id: str
    name: str
    race: int
    klass: int
    gender: int
    alignment: int
    level: int
    hp: int
    ac: int
    thac0: int
    attacks: int
    xp_value: int
    gold: int
    morale: int
    abilities: tuple[int, int, int, int, int, int]   # str, dex, con, int, wis, cha
    saves: tuple[int, int, int, int, int]            # death, wands, poly, breath, spells
    items: tuple[tuple[str, str], ...]                # (slot, item name)
    colors: tuple[int, ...] | None = None              # COLOR_FIELDS order, or keep the base's


@dataclass(frozen=True)
class Effect:
    """One embedded effect on the creature itself, permanent."""
    opcode: int
    param1: int = 0
    param2: int = 0


def vision_effects(fade: int = 128, rgb: tuple[int, int, int] = (200, 220, 255),
                   speed: int = 30) -> tuple[Effect, ...]:
    """The look of a vision: translucent (0 = solid, 255 = invisible) with a slow pale glow over the
    whole body (location 255)."""
    if not 0 < fade < 255 or not all(0 <= c <= 255 for c in rgb) or not 0 < speed < 256:
        raise ActionError('BAD_EFFECT')
    red, green, blue = rgb
    return (Effect(OP_TRANSLUCENCY, fade),
            Effect(OP_GLOW_PULSE, red << 8 | green << 16 | blue << 24, 0xFF | speed << 16))


def _effect_bytes(effect: Effect) -> bytes:
    if not (isinstance(effect, Effect) and 0 <= effect.opcode < 1000
            and 0 <= effect.param1 < 2**32 and 0 <= effect.param2 < 2**32):
        raise ActionError('BAD_EFFECT')
    raw = bytearray(EFFECT_SIZE)
    struct.pack_into('<IIIIII', raw, 0x08, effect.opcode, 1, 0, effect.param1, effect.param2,
                     TIMING_PERMANENT)                 # target: self; power 0
    struct.pack_into('<HH', raw, 0x24, 100, 0)         # always applies
    return bytes(raw)


def _int(doc: dict, key: str, low: int, high: int) -> int:
    value = doc.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ActionError(f'BAD_SHEET_{key.upper()}')
    return value


def parse_sheet(doc: object) -> Sheet:
    """A complete, plausible sheet, or ActionError naming the first bad field."""
    if not isinstance(doc, dict) or doc.get('schema') != SHEET_SCHEMA:
        raise ActionError('BAD_SHEET')
    if not isinstance(doc.get('sheet_id'), str) or not isinstance(doc.get('name'), str) \
            or not doc['name'].strip():
        raise ActionError('BAD_SHEET_NAME')
    for key, table in (('race', RACES), ('class', CLASSES), ('gender', GENDERS),
                       ('alignment', ALIGNMENTS)):
        if doc.get(key) not in table:
            raise ActionError(f'BAD_SHEET_{key.upper()}')
    abilities = doc.get('abilities') or {}
    saves = doc.get('saves') or {}
    if not isinstance(abilities, dict) or not isinstance(saves, dict):
        raise ActionError('BAD_SHEET')
    raw_items = doc.get('items') or []
    if not isinstance(raw_items, list):
        raise ActionError('BAD_SHEET_ITEMS')
    items = []
    for item in raw_items:
        if not isinstance(item, dict) or item.get('slot') not in SLOTS \
                or not isinstance(item.get('name'), str) or not item['name'].strip() \
                or item['slot'] in {s for s, _ in items}:
            raise ActionError('BAD_SHEET_ITEMS')
        items.append((item['slot'], item['name'].strip()))
    colors = None
    if doc.get('colors') is not None:
        if not isinstance(doc['colors'], dict) or set(doc['colors']) != set(COLOR_FIELDS):
            raise ActionError('BAD_SHEET_COLORS')
        colors = tuple(_int(doc['colors'], k, 0, 255) for k in COLOR_FIELDS)
    return Sheet(
        doc['sheet_id'], doc['name'].strip(), RACES[doc['race']], CLASSES[doc['class']],
        GENDERS[doc['gender']], ALIGNMENTS[doc['alignment']],
        _int(doc, 'level', 1, 40), _int(doc, 'hp', 1, 999), _int(doc, 'ac', -20, 10),
        _int(doc, 'thac0', -10, 20), _int(doc, 'attacks', 1, 5), _int(doc, 'xp_value', 0, 10**7),
        _int(doc, 'gold', 0, 10**6), _int(doc, 'morale', 0, 20),
        tuple(_int(abilities, k, 1, 25) for k in ('str', 'dex', 'con', 'int', 'wis', 'cha')),
        tuple(_int(saves, k, 1, 20) for k in ('death', 'wands', 'poly', 'breath', 'spells')),
        tuple(items), colors)


def build_creature(base: bytes, sheet: Sheet, *, script_name: str, name_strref: int,
                   animation: int, items: dict[str, str],
                   effects: tuple[Effect, ...] = ()) -> bytes:
    """Our creature file: the base's body with the sheet's identity, colors and equipment.
    `items`: slot -> ITM resref of the build (only the sheet's items found by name);
    `effects`: embedded on the creature (for instance `vision_effects()`)."""
    data = bytearray(make_template(base, script_name))   # our name; refuses a dead base
    if len(data) < HEADER_SIZE:
        raise ActionError('BAD_SOURCE_CRE')
    meminfo_off, meminfo_n = struct.unpack_from('<II', data, 0x2A8)
    meminfo = bytes(data[meminfo_off:meminfo_off + MEMINFO_SIZE * meminfo_n])
    if len(meminfo) != MEMINFO_SIZE * meminfo_n:
        raise ActionError('BAD_SOURCE_CRE')
    for slot, resref in items.items():
        if slot not in SLOTS or not isinstance(resref, str) or not 1 <= len(resref) <= 8:
            raise ActionError('BAD_ITEM')
    effect_table = b''.join(_effect_bytes(e) for e in effects)
    head = data[:HEADER_SIZE]
    struct.pack_into('<II', head, 0x08, name_strref, name_strref)    # long and short name
    struct.pack_into('<I', head, 0x14, sheet.xp_value)
    struct.pack_into('<I', head, 0x1C, sheet.gold)
    struct.pack_into('<I', head, 0x20, 0)                            # alive, no state
    struct.pack_into('<hh', head, 0x24, sheet.hp, sheet.hp)
    struct.pack_into('<I', head, 0x28, animation)
    if sheet.colors is not None:
        head[0x2C:0x33] = bytes(sheet.colors)
    head[0x33] = 1                                                   # effects are EFF V2
    struct.pack_into('<hh', head, 0x46, 10, 10)    # unarmored: the engine adds armor and Dex
    head[0x52], head[0x53] = sheet.thac0 & 0xFF, sheet.attacks
    head[0x54:0x59] = bytes(sheet.saves)
    head[0x234:0x237] = bytes((sheet.level, 0, 0))
    head[0x237] = sheet.gender
    st, dex, con, it, wis, cha = sheet.abilities
    head[0x238:0x23F] = bytes((st, 0, it, wis, dex, con, cha))
    head[0x23F] = sheet.morale
    struct.pack_into('<I', head, 0x244, 0)                           # no kit
    head[0x248:0x270] = bytes(40)                                    # no AI scripts
    head[0x270], head[0x271], head[0x272], head[0x273] = NEUTRAL_EA, 1, sheet.race, sheet.klass
    head[0x275], head[0x27B] = sheet.gender, sheet.alignment
    head[0x2CC:0x2D4] = bytes(8)                                     # no game dialogue
    order = [s for s in SLOTS if s in items]
    table = b''.join(items[s].upper().encode('ascii').ljust(8, b'\0')
                     + struct.pack('<HHHHI', 0, 1, 0, 0, 1) for s in order)   # identified
    slots = [EMPTY_SLOT] * SLOT_WORDS
    for index, slot in enumerate(order):
        slots[SLOTS[slot]] = index
    slots[38], slots[39] = (0 if 'WEAPON1' in items else 1000), 0    # selected weapon, ability
    meminfo_at = HEADER_SIZE
    items_at = meminfo_at + len(meminfo)
    slots_at = items_at + len(table)
    end = slots_at + 2 * SLOT_WORDS
    struct.pack_into('<IIIIIIIIIII', head, 0x2A0,   # 0x2A0..0x2CB; 0x2CC is the dialogue
                     meminfo_at, 0,               # known spells
                     meminfo_at, meminfo_n,       # memorization info (kept)
                     items_at, 0,                 # memorized spells
                     slots_at, items_at, len(order),
                     end, len(effects))           # effects, after the slots
    return bytes(head) + meminfo + table + struct.pack(f'<{SLOT_WORDS}H', *slots) + effect_table
