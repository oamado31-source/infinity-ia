# SPDX-License-Identifier: Apache-2.0
"""ADR-0137 (P3b): one of OUR creature files built from a curated sheet of another game.

A sheet (local only, CR-2026-030: the numbers come from a community database consulted per entity)
gives who the creature is: race, class, sex, alignment, level, hit points, armor class, THAC0,
attacks, abilities, saving throws, morale, experience value, gold and equipment by name. A living
CRE of the build gives the body (it is copied, never edited in place). The result keeps the base's
spell-memorization table, empties spells and effects, drops the base's scripts and dialogue (the
creature talks through our box, ADR-0136 D5: neutral, no combat), and lays out a new item table and
slot table with the sheet's items, found in the build by the same name (strref) and the slot's item
type, a resref pinned in the local sheet when several remain (ADR-0141), backpack items and
campaign items carried (`carry`, ADR-0141: the diary in Kalessia's backpack). Optional: the
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
INVENTORY = 'INVENTORY'               # ADR-0141: the 16 backpack slots, filled in order
INVENTORY_SLOTS = tuple(range(21, 37))
SLOT_WORDS = 40                      # 38 slots + selected weapon + selected weapon ability
BASE_RACE = 'BASE'                   # ADR-0141: keep the body's race and general (giant-kin...)
# ADR-0141 (D4): the item types (ITM 0x1C) each slot takes; INVENTORY takes any.
WEAPON_TYPES = frozenset({15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 44,
                          57, 69})
SLOT_TYPES = {'HELMET': {7}, 'ARMOR': {2}, 'SHIELD': {12}, 'GLOVES': {6},
              'RING_LEFT': {10}, 'RING_RIGHT': {10}, 'AMULET': {1}, 'BELT': {3}, 'BOOTS': {4},
              'CLOAK': {32}, **{f'WEAPON{i}': WEAPON_TYPES for i in range(1, 5)}}
NEUTRAL_EA = 128
ENEMY_EA = 255                       # ADR-0142: born hostile
SOUNDSET, SOUNDSET_SLOTS = 0xA4, 100  # CRE V1.0: the lines said on select, attack, death...
# ADR-0142: the five script slots of a CRE V1.0, by name, and the meminfo spell types.
SCRIPT_SLOTS = {'override': 0x248, 'class': 0x250, 'race': 0x258, 'general': 0x260,
                'default': 0x268}
SPELL_TYPES = {'PRIEST': 0, 'WIZARD': 1, 'INNATE': 2}
KNOWN_SIZE, MEMORIZED_SIZE = 0x0C, 0x0C
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
    natural_ac: int = 10                               # ADR-0141: AC without armor items
    str_extra: int = 0                                 # ADR-0141: exceptional strength (18/xx)
    pinned: tuple[tuple[str, str, str], ...] = ()      # ADR-0141: (slot, name, resref) fixed locally
    scripts: tuple[tuple[str, str], ...] = ()          # ADR-0142: (slot, BCS name) of the build
    spells: tuple[tuple[str, int], ...] = ()           # ADR-0142: (SPL resref, memorized count)
    silent: bool = False                               # no lines of the body's soundset (lab)


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
        if doc.get(key) not in table and not (key == 'race' and doc.get(key) == BASE_RACE):
            raise ActionError(f'BAD_SHEET_{key.upper()}')
    abilities = doc.get('abilities') or {}
    saves = doc.get('saves') or {}
    if not isinstance(abilities, dict) or not isinstance(saves, dict):
        raise ActionError('BAD_SHEET')
    raw_items = doc.get('items') or []
    if not isinstance(raw_items, list):
        raise ActionError('BAD_SHEET_ITEMS')
    items, pinned = [], []
    for item in raw_items:
        slot, resref = (item.get('slot'), item.get('resref')) if isinstance(item, dict) \
            else (None, None)
        if not isinstance(item, dict) or (slot not in SLOTS and slot != INVENTORY) \
                or not isinstance(item.get('name'), str) or not item['name'].strip() \
                or (slot != INVENTORY and slot in {s for s, _ in items}) \
                or (resref is not None and (not isinstance(resref, str)
                                            or not 1 <= len(resref) <= 8
                                            or not resref.isalnum())):
            raise ActionError('BAD_SHEET_ITEMS')
        items.append((slot, item['name'].strip()))
        if resref is not None:
            pinned.append((slot, item['name'].strip(), resref.upper()))
    if sum(1 for s, _ in items if s == INVENTORY) > len(INVENTORY_SLOTS):
        raise ActionError('BAD_SHEET_ITEMS')
    colors = None
    if doc.get('colors') is not None:
        if not isinstance(doc['colors'], dict) or set(doc['colors']) != set(COLOR_FIELDS):
            raise ActionError('BAD_SHEET_COLORS')
        colors = tuple(_int(doc['colors'], k, 0, 255) for k in COLOR_FIELDS)
    scripts = []
    raw_scripts = doc.get('scripts') or {}
    if not isinstance(raw_scripts, dict):
        raise ActionError('BAD_SHEET_SCRIPTS')
    for slot, name in raw_scripts.items():
        if slot not in SCRIPT_SLOTS or not isinstance(name, str) or not 1 <= len(name) <= 8 \
                or not name.replace('_', '').replace('#', '').isalnum():
            raise ActionError('BAD_SHEET_SCRIPTS')
        scripts.append((slot, name.upper()))
    spells = []
    raw_spells = doc.get('spells') or []
    if not isinstance(raw_spells, list):
        raise ActionError('BAD_SHEET_SPELLS')
    for spell in raw_spells:
        ref = spell.get('resref') if isinstance(spell, dict) else None
        count = spell.get('count', 1) if isinstance(spell, dict) else None
        if not isinstance(ref, str) or not 1 <= len(ref) <= 8 or not ref.isalnum() \
                or isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 9 \
                or ref.upper() in {r for r, _ in spells}:
            raise ActionError('BAD_SHEET_SPELLS')
        spells.append((ref.upper(), count))
    sounds = doc.get('sounds')
    if sounds not in (None, 'silent'):
        raise ActionError('BAD_SHEET_SOUNDS')
    natural_ac = _int(doc, 'natural_ac', -10, 10) if 'natural_ac' in doc else 10
    str_extra = _int(doc, 'str_extra', 0, 100) if 'str_extra' in doc else 0
    return Sheet(
        doc['sheet_id'], doc['name'].strip(),
        0 if doc['race'] == BASE_RACE else RACES[doc['race']], CLASSES[doc['class']],
        GENDERS[doc['gender']], ALIGNMENTS[doc['alignment']],
        _int(doc, 'level', 1, 40), _int(doc, 'hp', 1, 999), _int(doc, 'ac', -20, 10),
        _int(doc, 'thac0', -10, 20), _int(doc, 'attacks', 1, 5), _int(doc, 'xp_value', 0, 10**7),
        _int(doc, 'gold', 0, 10**6), _int(doc, 'morale', 0, 20),
        tuple(_int(abilities, k, 1, 25) for k in ('str', 'dex', 'con', 'int', 'wis', 'cha')),
        tuple(_int(saves, k, 1, 20) for k in ('death', 'wands', 'poly', 'breath', 'spells')),
        tuple(items), colors, natural_ac, str_extra, tuple(pinned), tuple(scripts), tuple(spells),
        sounds == 'silent')


def choose_item(slot: str, name: str, candidates: list[tuple[str, int]],
                pinned: str | None = None) -> str:
    """ADR-0141 (D4): the build's item for a sheet item. `candidates`: (resref, ITM type) of the
    items whose identified name is the sheet's. Only types the slot takes count; with more than
    one left, the local sheet must pin a resref (ITEM_AMBIGUOUS lists nothing by itself: the
    lab tool prints the candidates). A pinned resref must be one of the candidates."""
    allowed = SLOT_TYPES.get(slot)
    fit = [(ref.upper(), typ) for ref, typ in candidates if allowed is None or typ in allowed]
    if pinned is not None:
        if pinned.upper() not in {ref for ref, _ in fit}:
            raise ActionError('ITEM_PIN_MISMATCH')
        return pinned.upper()
    if not fit:
        raise ActionError('ITEM_NOT_FOUND')
    if len(fit) > 1:
        raise ActionError('ITEM_AMBIGUOUS')
    return fit[0][0]


def build_creature(base: bytes, sheet: Sheet, *, script_name: str, name_strref: int,
                   animation: int, items: dict[str, str] | list[tuple[str, str]],
                   effects: tuple[Effect, ...] = (), carry: tuple[str, ...] = (),
                   spell_info: dict[str, tuple[str, int]] | None = None,
                   hostile: bool = False) -> bytes:
    """Our creature file: the base's body with the sheet's identity, colors and equipment.
    `items`: slot -> ITM resref of the build (only the sheet's items found by name);
    `effects`: embedded on the creature (for instance `vision_effects()`);
    `carry` (ADR-0141): campaign items put in the backpack after the sheet's own, identified and
    droppable (they fall when the creature falls);
    `spell_info` (ADR-0142): SPL resref -> (PRIEST|WIZARD|INNATE, level 1..9), read from the build
    by the lab tool, for the sheet's spells; `hostile` (ADR-0142): born an enemy (EA 255)."""
    data = bytearray(make_template(base, script_name))   # our name; refuses a dead base
    if len(data) < HEADER_SIZE:
        raise ActionError('BAD_SOURCE_CRE')
    meminfo_off, meminfo_n = struct.unpack_from('<II', data, 0x2A8)
    meminfo = bytearray(data[meminfo_off:meminfo_off + MEMINFO_SIZE * meminfo_n])
    if len(meminfo) != MEMINFO_SIZE * meminfo_n:
        raise ActionError('BAD_SOURCE_CRE')
    known, memorized = _spell_tables(sheet, meminfo, meminfo_n, spell_info or {})
    pairs = list(items.items()) if isinstance(items, dict) else list(items)
    pairs += [(INVENTORY, ref) for ref in carry]
    worn = [s for s, _ in pairs if s != INVENTORY]
    if len(worn) != len(set(worn)) or sum(1 for s, _ in pairs if s == INVENTORY) \
            > len(INVENTORY_SLOTS):
        raise ActionError('BAD_ITEM')
    for slot, resref in pairs:
        if (slot not in SLOTS and slot != INVENTORY) or not isinstance(resref, str) \
                or not 1 <= len(resref) <= 8:
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
    struct.pack_into('<hh', head, 0x46, sheet.natural_ac, sheet.natural_ac)  # + armor and Dex
    head[0x52], head[0x53] = sheet.thac0 & 0xFF, sheet.attacks
    head[0x54:0x59] = bytes(sheet.saves)
    head[0x234:0x237] = bytes((sheet.level, 0, 0))
    head[0x237] = sheet.gender
    st, dex, con, it, wis, cha = sheet.abilities
    head[0x238:0x23F] = bytes((st, sheet.str_extra, it, wis, dex, con, cha))
    head[0x23F] = sheet.morale
    struct.pack_into('<I', head, 0x244, 0)                           # no kit
    head[0x248:0x270] = bytes(40)                                    # no AI scripts...
    for slot, name in sheet.scripts:                                 # ...but the game's own (ADR-0142)
        head[SCRIPT_SLOTS[slot]:SCRIPT_SLOTS[slot] + 8] = name.encode('ascii').ljust(8, b'\0')
    head[0x270], head[0x273] = (ENEMY_EA if hostile else NEUTRAL_EA), sheet.klass
    if sheet.race:                         # BASE keeps the body's race and general (ADR-0141)
        head[0x271], head[0x272] = 1, sheet.race
    head[0x275], head[0x27B] = sheet.gender, sheet.alignment
    head[0x2CC:0x2D4] = bytes(8)                                     # no game dialogue
    if sheet.silent:            # the body's lines are someone else's voice (lab, 2026-11-24)
        head[SOUNDSET:SOUNDSET + 4 * SOUNDSET_SLOTS] = b'\xff' * (4 * SOUNDSET_SLOTS)
    worn_of = dict((s, r) for s, r in pairs if s != INVENTORY)
    order = [(SLOTS[s], worn_of[s]) for s in SLOTS if s in worn_of]
    order += list(zip(INVENTORY_SLOTS, [r for s, r in pairs if s == INVENTORY]))
    table = b''.join(ref.upper().encode('ascii').ljust(8, b'\0')
                     + struct.pack('<HHHHI', 0, 1, 0, 0, 1) for _, ref in order)   # identified
    slots = [EMPTY_SLOT] * SLOT_WORDS
    for index, (word, _) in enumerate(order):
        slots[word] = index
    slots[38], slots[39] = (0 if 'WEAPON1' in worn_of else 1000), 0  # selected weapon, ability
    known_at = HEADER_SIZE
    meminfo_at = known_at + len(known)
    memorized_at = meminfo_at + len(meminfo)
    items_at = memorized_at + len(memorized)
    slots_at = items_at + len(table)
    end = slots_at + 2 * SLOT_WORDS
    struct.pack_into('<IIIIIIIIIII', head, 0x2A0,   # 0x2A0..0x2CB; 0x2CC is the dialogue
                     known_at, len(known) // KNOWN_SIZE,                 # known spells
                     meminfo_at, meminfo_n,                             # memorization info
                     memorized_at, len(memorized) // MEMORIZED_SIZE,    # memorized spells
                     slots_at, items_at, len(order),
                     end, len(effects))           # effects, after the slots
    return bytes(head) + known + bytes(meminfo) + memorized + table \
        + struct.pack(f'<{SLOT_WORDS}H', *slots) + effect_table


def _spell_tables(sheet: Sheet, meminfo: bytearray, meminfo_n: int,
                  info: dict[str, tuple[str, int]]) -> tuple[bytes, bytes]:
    """ADR-0142: the known and memorized spell tables for the sheet's spells, and the base's
    memorization entries updated in place (how many per level, where they start). Without spells,
    the base's entries are kept with nothing memorized."""
    by_slot: dict[tuple[int, int], list[tuple[str, int]]] = {}
    for ref, count in sheet.spells:
        if ref not in info or info[ref][0] not in SPELL_TYPES or not 1 <= info[ref][1] <= 9:
            raise ActionError('UNKNOWN_SPELL')
        kind, level = info[ref]
        by_slot.setdefault((SPELL_TYPES[kind], level - 1), []).append((ref, count))
    known = b''.join(ref.encode('ascii').ljust(8, b'\0')
                     + struct.pack('<HH', level - 1, SPELL_TYPES[kind])
                     for ref, (kind, level) in ((r, info[r]) for r, _ in sheet.spells))
    memorized = b''
    used: set[tuple[int, int]] = set()
    for i in range(meminfo_n):
        at = i * MEMINFO_SIZE
        level, _, _, kind = struct.unpack_from('<HHHH', meminfo, at)
        mine = by_slot.get((kind, level), [])
        total = sum(c for _, c in mine)
        if mine:
            used.add((kind, level))
        struct.pack_into('<HHHHII', meminfo, at, level, total, total, kind,
                         len(memorized) // MEMORIZED_SIZE, total)
        for ref, count in mine:
            memorized += (ref.encode('ascii').ljust(8, b'\0') + struct.pack('<I', 1)) * count
    if set(by_slot) - used:
        raise ActionError('NO_SPELL_SLOT')          # the body has no memorization for that level
    return known, memorized
