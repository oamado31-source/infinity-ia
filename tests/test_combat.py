# SPDX-License-Identifier: Apache-2.0
"""ADR-0142: enemies that fight — the game's own scripts and spells, born hostile, and hostile
from a point of the quest (SET_HOSTILE through the gateway)."""
import copy
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.actions.creatures import ENEMY_EA, NEUTRAL_EA, build_creature, parse_sheet  # noqa: E402
from infinity_ai.actions.gateway import (  # noqa: E402
    COUNT, SET_HOSTILE, SPAWN, ActionError, ActionReceipt,
)
from infinity_ai.quests.narrative import advance, parse_quest  # noqa: E402
from infinity_ai.quests.presence import (  # noqa: E402
    COUNT_RULES, DEFEAT_WATCH, ENTER, HOSTILE, VERIFY, WATCH_EVERY, decide, dispatch,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402
from test_creatures import SHEET, base_cre  # noqa: E402

MAGE = dict(SHEET, **{'class': 'MAGE'}, items=[],
            scripts={'class': 'MAGE5', 'race': 'GPSHOUT', 'default': 'WTASIGHT'},
            spells=[{'resref': 'SPWI112', 'count': 2}, {'resref': 'SPWI205', 'count': 2},
                    {'resref': 'SPWI212', 'count': 1}])
INFO = {'SPWI112': ('WIZARD', 1), 'SPWI205': ('WIZARD', 2), 'SPWI212': ('WIZARD', 2)}


def body_with_spell_levels():
    """A body whose memorization entries are priest 1-7, wizard 1-9 and innate, as in BG2."""
    d = bytearray(base_cre())
    mem_at, mem_n = struct.unpack_from('<II', d, 0x2A8)
    kinds = [(lvl, 0) for lvl in range(7)] + [(lvl, 1) for lvl in range(9)] + [(0, 2)]
    for i, (level, kind) in enumerate(kinds[:mem_n]):
        struct.pack_into('<HHHHII', d, mem_at + 16 * i, level, 0, 0, kind, 0, 0)
    return bytes(d)


class BuildTests(unittest.TestCase):
    def build(self, sheet=MAGE, **kw):
        return build_creature(body_with_spell_levels(), parse_sheet(sheet),
                              script_name='INFAI_TESTE', name_strref=20381, animation=0x6210,
                              items={}, spell_info=INFO, **kw)

    def test_scripts_spells_and_side(self):
        d = self.build()
        self.assertEqual([d[o:o + 8].rstrip(b'\0').decode() for o in range(0x248, 0x270, 8)],
                         ['', 'MAGE5', 'GPSHOUT', '', 'WTASIGHT'])
        self.assertEqual(d[0x270], NEUTRAL_EA)
        self.assertEqual(self.build(hostile=True)[0x270], ENEMY_EA)
        known_at, known_n, mem_at, mem_n, memd_at, memd_n = struct.unpack_from('<IIIIII', d, 0x2A0)
        known = [(d[known_at + 12 * i:known_at + 12 * i + 8].rstrip(b'\0').decode(),
                  *struct.unpack_from('<HH', d, known_at + 12 * i + 8)) for i in range(known_n)]
        self.assertEqual(known, [('SPWI112', 0, 1), ('SPWI205', 1, 1), ('SPWI212', 1, 1)])
        memorized = [d[memd_at + 12 * i:memd_at + 12 * i + 8].rstrip(b'\0').decode()
                     for i in range(memd_n)]
        self.assertEqual(memorized, ['SPWI112', 'SPWI112', 'SPWI205', 'SPWI205', 'SPWI212'])
        entries = [struct.unpack_from('<HHHHII', d, mem_at + 16 * i) for i in range(mem_n)]
        wizard1 = next(e for e in entries if e[3] == 1 and e[0] == 0)
        wizard2 = next(e for e in entries if e[3] == 1 and e[0] == 1)
        self.assertEqual((wizard1[1], wizard1[4], wizard1[5]), (2, 0, 2))   # two at index 0
        self.assertEqual((wizard2[1], wizard2[4], wizard2[5]), (3, 2, 3))   # three from index 2
        for e in entries:
            if e not in (wizard1, wizard2):
                self.assertEqual((e[1], e[5]), (0, 0))
        for flag_at in range(memd_n):
            self.assertEqual(struct.unpack_from('<I', d, memd_at + 12 * flag_at + 8)[0], 1)

    def test_bad_scripts_and_spells(self):
        for change, code in ((lambda s: s.update(scripts={'pocket': 'X'}), 'BAD_SHEET_SCRIPTS'),
                             (lambda s: s.update(scripts={'class': 'MAGE 5'}), 'BAD_SHEET_SCRIPTS'),
                             (lambda s: s.update(spells=[{'resref': 'SPWI112', 'count': 0}]),
                              'BAD_SHEET_SPELLS'),
                             (lambda s: s['spells'].append({'resref': 'SPWI112'}),
                              'BAD_SHEET_SPELLS')):
            doc = copy.deepcopy(MAGE)
            change(doc)
            with self.assertRaises(ActionError) as ctx:
                parse_sheet(doc)
            self.assertEqual(ctx.exception.code, code)
        with self.assertRaises(ActionError) as ctx:                 # unknown to the build
            build_creature(body_with_spell_levels(), parse_sheet(MAGE), script_name='INFAI_T',
                           name_strref=1, animation=0x6210, items={}, spell_info={})
        self.assertEqual(ctx.exception.code, 'UNKNOWN_SPELL')
        with self.assertRaises(ActionError) as ctx:                 # no wizard level 9 slot
            build_creature(base_cre(), parse_sheet(MAGE), script_name='INFAI_T', name_strref=1,
                           animation=0x6210, items={}, spell_info=dict(INFO, SPWI112=('WIZARD', 9)))
        self.assertEqual(ctx.exception.code, 'NO_SPELL_SLOT')


DOC = json.loads((ROOT / 'knowledge' / 'quests' / 'bernard-brooch.pt_BR.json').read_text())
CELL = {'presence_id': 'celula', 'cre': 'IATESTE', 'name': 'INFAI_TESTE', 'area': 'AR0406',
        'copies': 2, 'hostile_from': 'ask-yarin'}


class Game:
    def __init__(self):
        self.here, self.hostile, self.writes = 0, 0, []

    def send(self, req):
        if req.op == COUNT:
            return ActionReceipt(req.action_id, 'DONE', self.here, None, self.here)
        self.writes.append(req.op)
        if req.op == SET_HOSTILE:
            self.hostile = self.here
            return ActionReceipt(req.action_id, 'DONE', self.hostile, None, self.here)
        before = self.here
        self.here = before + req.count if req.op == SPAWN else 0
        return ActionReceipt(req.action_id, 'DONE', self.here, None, before,
                             40 + self.here, 40 + before)


class HostileFromTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        doc = copy.deepcopy(DOC)
        doc['presence'] = [CELL]
        self.quest = parse_quest(doc)
        self.quests = {self.quest.quest_id: self.quest}
        self.game, self.t = Game(), 100

    def say(self, who, text):
        self.t += 10
        advance(self.store, ROOT_BRANCH, self.quests, speaker=who, text=text, area='AR0406',
                game_time=self.t)

    def rules(self):
        out = []
        for _ in range(8):
            self.t += 1
            decision, _ = decide(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                                 game_time=self.t)
            if decision is None:
                break
            dispatch(self.store, ROOT_BRANCH, decision, transport=self.game,
                     templates={'IATESTE': 'INFAI_TESTE'}, game_time=self.t)
            out.append(decision.rule)
        return out

    def test_the_cell_turns_hostile_at_its_step_once(self):
        self.assertIsNone(parse_quest(dict(copy.deepcopy(DOC), presence=[
            dict(CELL, hostile_from='passo-inventado')])))
        self.say('npc:cre-bernard', 'Tem trabalho?')
        self.say('npc:cre-bernard', 'Aceito.')
        self.assertEqual(self.rules(), [VERIFY, ENTER])                 # both, neutral for now
        self.assertEqual(self.game.hostile, 0)
        self.say('npc:yarin', 'Quem furtou o broche de Bernard?')        # the step is done
        self.assertEqual(self.rules(), [HOSTILE])
        self.assertEqual(self.game.hostile, 2)
        self.assertEqual(self.rules(), [])                              # never twice
        self.assertNotIn(HOSTILE, COUNT_RULES)
        self.assertEqual(self.game.writes, [SPAWN, SET_HOSTILE])



class Many:
    """Several of our names at once, with the area's total (ADR-0143)."""

    def __init__(self):
        self.here, self.hostile, self.writes, self.other = {}, {}, [], 40

    def send(self, req):
        n = self.here.get(req.name, 0)
        total = self.other + sum(self.here.values())
        if req.op == COUNT:
            return ActionReceipt(req.action_id, 'DONE', n, None, n, total)
        self.writes.append((req.op, req.name, req.count))
        if req.op == SET_HOSTILE:
            self.hostile[req.name] = n
            return ActionReceipt(req.action_id, 'DONE', n, None, n, total)
        self.here[req.name] = n + req.count if req.op == SPAWN else 0
        return ActionReceipt(req.action_id, 'DONE', self.here[req.name], None, n,
                             self.other + sum(self.here.values()), total)


LEADER = {'presence_id': 'lider', 'cre': 'IALIDER', 'name': 'INFAI_LIDER', 'area': 'AR0406',
          'hostile_from': 'ask-yarin'}
GUARDS = {'presence_id': 'guardas', 'cre': 'IAGUARDA', 'name': 'INFAI_GUARDA', 'area': 'AR0406',
          'copies': 3, 'hostile_from': 'ask-yarin'}
FALLS = [{'step_id': 'lider-caiu', 'defeated': {'presence': 'lider'}, 'journal': 'O líder caiu.'},
         {'step_id': 'guardas-cairam', 'defeated': {'presence': 'guardas'},
          'journal': 'Os guardas caíram.'}]


class TogetherTests(unittest.TestCase):
    """ADR-0143: the copies come in one request, and every presence a step turns goes hostile
    before anyone's defeat is watched (lab S2d: the agents turned 25 s after Kalessia)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        doc = copy.deepcopy(DOC)
        doc['presence'] = [LEADER, GUARDS]
        doc['steps'] = doc['steps'] + FALLS
        quest = parse_quest(doc)
        self.quests = {quest.quest_id: quest}
        self.game, self.t = Many(), 100

    def say(self, who, text):
        self.t += 10
        advance(self.store, ROOT_BRANCH, self.quests, speaker=who, text=text, area='AR0406',
                game_time=self.t)

    def rules(self, limit=3):
        out = []
        for _ in range(limit):
            self.t += 1
            decision, _ = decide(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                                 game_time=self.t)
            if decision is None:
                break
            dispatch(self.store, ROOT_BRANCH, decision, transport=self.game,
                     templates={'IALIDER': 'INFAI_LIDER', 'IAGUARDA': 'INFAI_GUARDA'},
                     game_time=self.t)
            out.append((decision.rule, decision.presence.presence_id))
        return out

    def test_copies_together_and_hostile_before_any_watch(self):
        self.say('npc:cre-bernard', 'Tem trabalho?')
        self.say('npc:cre-bernard', 'Aceito.')
        self.rules(limit=8)
        self.assertIn((SPAWN, 'INFAI_GUARDA', 3), self.game.writes)    # all three at once
        self.assertEqual(self.game.here, {'INFAI_LIDER': 1, 'INFAI_GUARDA': 3})
        self.say('npc:yarin', 'Quem furtou o broche de Bernard?')
        self.t += WATCH_EVERY                                          # both watches are due
        self.assertEqual(self.rules(), [(HOSTILE, 'lider'), (HOSTILE, 'guardas'),
                                        (DEFEAT_WATCH, 'lider')])
        self.assertEqual(self.game.hostile, {'INFAI_LIDER': 1, 'INFAI_GUARDA': 3})
        self.assertEqual([w for w in self.game.writes if w[0] == SPAWN],
                         [(SPAWN, 'INFAI_LIDER', 1), (SPAWN, 'INFAI_GUARDA', 3)])

    def test_a_creation_the_area_does_not_show_is_not_believed(self):
        """Lab S2d: ours seemed to rise, the area's total did not; the presence is held."""
        game = self.game
        real = game.send

        def lying(req):
            receipt = real(req)
            if req.op == SPAWN:
                return ActionReceipt(receipt.action_id, 'DONE', receipt.observed, None,
                                     receipt.before, receipt.seen_before, receipt.seen_before)
            return receipt
        game.send = lying
        self.say('npc:cre-bernard', 'Tem trabalho?')
        self.say('npc:cre-bernard', 'Aceito.')
        self.assertEqual(self.rules(limit=8), [(VERIFY, 'lider'), (ENTER, 'lider'),
                                               (VERIFY, 'guardas'), (ENTER, 'guardas')])
        decision, held = decide(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                                game_time=self.t)
        self.assertIsNone(decision)                                     # never asked twice
        self.assertEqual(sorted(h.split('/')[1] for h in held),
                         ['guardas=SUSPENDED', 'lider=SUSPENDED'])

if __name__ == '__main__':
    unittest.main()
