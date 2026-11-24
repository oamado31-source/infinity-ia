# SPDX-License-Identifier: Apache-2.0
"""ADR-0146: an area of ours copied from a room of the build, and the passages into and out of it."""
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

from infinity_ai.actions.areas import copied_files, make_area  # noqa: E402
from infinity_ai.actions.gateway import (  # noqa: E402
    ActionError, PassageEntry, check_passage, parse_receipt, render_passage_plan, where_request,
)
from infinity_ai.quests.narrative import advance, mark_step, parse_quest  # noqa: E402
from infinity_ai.quests.presence import open_passages  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

try:
    import lupa  # type: ignore
except ImportError:  # pragma: no cover
    lupa = None

DOC = json.loads((ROOT / 'knowledge' / 'quests' / 'sarevok-diary.pt_BR.json').read_text())
IN = PassageEntry('abcdef0123', 'AR0300', 3000, 3000, 'IA0001', 351, 753, 10)


def are(actors=3, regions=1, spawns=2, containers=4):
    d = bytearray(b'AREAV1.0' + b'AR0310\0\0' + b'\0' * 0x200)
    struct.pack_into('<H', d, 0x58, actors)
    struct.pack_into('<H', d, 0x5A, regions)
    struct.pack_into('<I', d, 0x64, spawns)
    struct.pack_into('<HH', d, 0x74, containers, 9)
    d[0x94:0x9C] = b'AR0310\0\0'
    return bytes(d)


class AreaTests(unittest.TestCase):
    def test_our_copy_keeps_the_drawing_and_drops_what_acts(self):
        d = make_area(are(), 'ia0001')
        self.assertEqual(d[0x08:0x10], b'IA0001\0\0')                 # its own WED name
        self.assertEqual(struct.unpack_from('<HH', d, 0x58), (0, 0))  # no creatures, no passage
        self.assertEqual(struct.unpack_from('<I', d, 0x64)[0], 0)     # no spawn point
        self.assertEqual(struct.unpack_from('<HH', d, 0x74), (0, 0))  # no loot copied
        self.assertEqual(d[0x94:0x9C], b'\0' * 8)                     # no area script
        self.assertEqual(len(d), len(are()))
        self.assertEqual([f for _, f, _ in copied_files('ar0310', 'IA0001')],
                         ['IA0001', 'IA0001', 'IA0001', 'IA0001SR', 'IA0001LM', 'IA0001HT'])
        for bad in ('AR0310', 'IA01', 'XX0001', ''):
            with self.assertRaises(ActionError):
                make_area(are(), bad)
        with self.assertRaises(ActionError):
            make_area(b'WEDV1.3' + b'\0' * 300, 'IA0001')


class GatewayTests(unittest.TestCase):
    def test_passages_only_into_or_out_of_ours(self):
        self.assertIn('to = "IA0001", to_x = 351', render_passage_plan([IN]))
        back = PassageEntry('0123456789', 'IA0001', 230, 850, 'AR0300', 3000, 3000)
        self.assertEqual(check_passage(back), back)
        for bad in (PassageEntry('abcdef0123', 'AR0300', 1, 1, 'AR0400', 1, 1),   # game to game
                    PassageEntry('abcdef0123', 'IA0001', 1, 1, 'IA0001', 1, 1),   # nowhere
                    PassageEntry('abc', 'AR0300', 1, 1, 'IA0001', 1, 1),
                    PassageEntry('abcdef0123', 'AR0300', -5, 1, 'IA0001', 1, 1),
                    PassageEntry('abcdef0123', 'AR0300', 1, 1, 'IA0001', 1, 1, 16)):
            with self.assertRaises(ActionError):
                render_passage_plan([bad])

    def test_where_reads_the_leaders_point(self):
        req = where_request('ar0300', action_id='abcdef0123')
        self.assertEqual((req.op, req.area), ('WHERE', 'AR0300'))
        line = ('INFAI-ACT {"schema":"infinity-ai.act.v1","action_id":"abcdef0123",'
                '"status":"DONE","observed":1,"reason":null,"before":1,"seen":null,'
                '"seen_before":null,"x":3012,"y":2987}')
        self.assertEqual((parse_receipt(line).x, parse_receipt(line).y), (3012, 2987))
        self.assertIsNone(parse_receipt(line.replace('"x":3012', '"x":-1')))


class QuestTests(unittest.TestCase):
    def test_the_gangplank_opens_when_gregor_has_told(self):
        quest = parse_quest(copy.deepcopy(DOC))
        self.assertEqual([p.passage_id for p in quest.passages], ['farol', 'saida-da-caverna'])
        bad = copy.deepcopy(DOC)
        bad['passages'][0]['to'] = 'AR0400'                              # game to game
        self.assertIsNone(parse_quest(bad))
        with tempfile.TemporaryDirectory() as tmp:
            store = CampaignStore.open(Path(tmp) / 'c.sqlite3', 'lab')
            self.addCleanup(store.close)
            quests = {quest.quest_id: quest}
            for i, text in enumerate(('Que fantasma?', 'Vamos ajudar.'), 1):
                advance(store, ROOT_BRANCH, quests, speaker='npc:drunk1', text=text,
                        area='AR0406', game_time=10 * i)
            self.assertEqual(open_passages(store, ROOT_BRANCH, quests), ())
            for step in ('cativeiro', 'carcereiros-cairam', 'gregor-conta'):
                mark_step(store, ROOT_BRANCH, quest, step, game_time=50)
            opened = open_passages(store, ROOT_BRANCH, quests)
            self.assertEqual(sorted((e.area, e.to) for e in opened),
                             [('AR0300', 'IA0001'), ('IA0001', 'AR0300')])
            self.assertEqual(len({e.passage_id for e in opened}), 2)


@unittest.skipIf(lupa is None, 'lupa not installed')
class ModuleTests(unittest.TestCase):
    def setUp(self):
        from test_actions import ENGINE, MODULE
        self.lua = lupa.LuaRuntime()
        self.lua.execute(ENGINE)
        self.lua.execute(MODULE.read_text(encoding='utf-8'))
        self.g = self.lua.globals()
        self.lua.execute('area = { m_resref = { get = function() return "AR0300" end }, '
                         'sprites = {} }; leader.m_pArea = area; leader.m_pos = { x = 100, y = 100 }')
        self.g.files['INFAIDOR'] = render_passage_plan([IN])

    def tick(self, ms=300):
        self.g.clock = self.g.clock + ms
        self.g.INFAI_ACT_Tick()

    def queued(self):
        return [self.g.queued[i] for i in range(1, len(self.g.queued) + 1)]

    def test_standing_at_the_gangplank_takes_the_party(self):
        self.tick()
        self.tick(400)                                        # the plan is read on arriving
        self.lua.execute('leader.m_pos = { x = 3010, y = 2990 }')
        self.tick(400)
        self.tick(400)
        self.assertEqual(self.queued(), [])                    # standing still: not a second yet
        self.tick(1200)
        self.assertEqual(self.queued(), ['LeaveAreaLUA("IA0001","",[351.753],10)'])
        self.tick(1200)
        self.assertEqual(len(self.queued()), 1)                # once, until it leaves the point

    def test_never_with_an_enemy_alive_in_the_area(self):
        self.lua.execute("""
          local foe = { m_scriptName = { get = function() return "Rato" end }, m_pos = { x = 0, y = 0 },
                        m_baseStats = { m_generalState = 0 }, m_typeAI = { m_EnemyAlly = 255 } }
          table.insert(area.sprites, foe)""")
        self.tick()
        self.tick(400)
        self.lua.execute('leader.m_pos = { x = 3000, y = 3000 }')
        for _ in range(6):
            self.tick(600)
        self.assertEqual(self.queued(), [])


if __name__ == '__main__':
    unittest.main()
