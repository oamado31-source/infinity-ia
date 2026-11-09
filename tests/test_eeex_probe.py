# SPDX-License-Identifier: Apache-2.0
"""P2 probe checks: static allowlist of engine calls, and behaviour under a mocked engine.

The static part always runs. The behavioural part needs `lupa` (Lua 5.2, same as the game) and is
skipped when it is missing, so CI keeps its single test dependency. Neither replaces the lab run.
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.bridge.eeex_log import (  # noqa: E402
    AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD, parse_latest_snapshot, parse_snapshot_line,
)

PROBE = ROOT / 'tools' / 'eeex-probe' / 'M_INFAI.lua'
MENU = ROOT / 'tools' / 'eeex-probe' / 'INFAIP2.menu'

ALLOWED_ENGINE_CALLS = frozenset({
    'EEex_Area_GetVisible', 'EEex_Sprite_GetInPortrait', 'EEex_GameState_AddInitializedListener',
    'EEex_GameState_AddDestroyedListener', 'EEex_Menu_LoadFile',
    'EEex_Menu_AddMainFileLoadedListener', 'EEex_Menu_AddAfterMainFileReloadedListener',
    'Infinity_GetClockTicks', 'Infinity_PushMenu',
})
FORBIDDEN = re.compile(r'\b(loadlib|require|dofile|loadfile|loadstring|load|io|os|rawset|'
                       r'setmetatable|EEex_Write\w*|EEex_DoFile|Execute\w*)\b|:\s*Set\w*\s*\(')


def strip_lua(source: str) -> str:
    """Remove comments and string literals (enough for this probe; not a full Lua lexer)."""
    out, i, n = [], 0, len(source)
    while i < n:
        if source.startswith('--[[', i):
            end = source.find(']]', i)
            i = n if end < 0 else end + 2
        elif source.startswith('--', i):
            end = source.find('\n', i)
            i = n if end < 0 else end
        elif source.startswith('[[', i):
            end = source.find(']]', i)
            out.append('""')
            i = n if end < 0 else end + 2
        elif source[i] in '"\'':
            quote, i = source[i], i + 1
            while i < n and source[i] != quote:
                i += 2 if source[i] == '\\' else 1
            out.append('""')
            i += 1
        else:
            out.append(source[i])
            i += 1
    return ''.join(out)


class ProbeStaticTests(unittest.TestCase):
    def setUp(self):
        self.code = strip_lua(PROBE.read_text(encoding='utf-8'))

    def test_only_allowlisted_engine_functions(self):
        used = set(re.findall(r'\b(?:EEex|Infinity)_\w+', self.code))
        self.assertTrue(used, 'probe should call the engine')
        self.assertEqual(used - ALLOWED_ENGINE_CALLS, set())

    def test_no_forbidden_capabilities(self):
        self.assertIsNone(FORBIDDEN.search(self.code), FORBIDDEN.search(self.code))

    def test_never_assigns_to_engine_state(self):
        for line in self.code.splitlines():
            for lhs in re.findall(r'([\w.\[\]:]+)\s*=(?!=)', line):
                if line.strip().startswith(('if ', 'elseif ')):
                    continue
                with self.subTest(line=line.strip()):
                    self.assertNotIn('EngineGlobals', lhs)
                    self.assertNotRegex(lhs, r'\.m_|:')
                    root = lhs.split('.')[0].split('[')[0]
                    self.assertTrue(root.startswith(('INFAI_', 'infai_')) or root.islower(),
                                    f'unexpected assignment target {lhs}')

    def test_engine_reads_are_protected_by_pcall(self):
        source = PROBE.read_text(encoding='utf-8')
        for read in ('EEex_Area_GetVisible()', 'm_worldTime.m_gameTime',
                     'EEex_Sprite_GetInPortrait(i)'):
            index = source.index(read)
            self.assertGreater(index, source.rfind('pcall(function()', 0, index))
            self.assertNotEqual(source.rfind('pcall(function()', 0, index), -1)

    def test_menu_only_evaluates_the_tick(self):
        menu = MENU.read_text(encoding='utf-8')
        self.assertIn('name "INFAI_P2_Menu"', menu)
        self.assertEqual(re.findall(r'"([^"]*\(\))"', menu), ['INFAI_P2_Tick()'])


try:
    from lupa import lua52
except ImportError:
    lua52 = None

_MOCK_ENGINE = r'''
MOCK = { clock = 0, area = nil, game_time = 0, area_error = false, printed = {}, party = {},
         party_error = false,
         pushed = {}, loaded = {}, listeners = { main = {}, init = {}, reload = {}, destroyed = {} } }
function print(s) table.insert(MOCK.printed, s) end
function Infinity_GetClockTicks() return MOCK.clock end
function Infinity_PushMenu(name) table.insert(MOCK.pushed, name) end
function EEex_Menu_LoadFile(name) table.insert(MOCK.loaded, name) end
function EEex_Menu_AddMainFileLoadedListener(f) table.insert(MOCK.listeners.main, f) end
function EEex_Menu_AddAfterMainFileReloadedListener(f) table.insert(MOCK.listeners.reload, f) end
function EEex_GameState_AddInitializedListener(f) table.insert(MOCK.listeners.init, f) end
function EEex_GameState_AddDestroyedListener(f) table.insert(MOCK.listeners.destroyed, f) end
local function readonly(t, name)
  return setmetatable({}, { __index = t, __newindex = function() error("write to " .. name) end })
end
function EEex_Area_GetVisible()
  if MOCK.area_error then error("binding failure") end
  if MOCK.area == nil then return nil end
  return readonly({ m_resref = readonly({ get = function(self) return MOCK.area end }, "m_resref") }, "area")
end
function EEex_Sprite_GetInPortrait(i)
  if MOCK.party_error then error("portrait binding failure") end
  local name = MOCK.party[i]
  if name == nil then return nil end
  return readonly({ m_scriptName = readonly({ get = function(self) return name end }, "m_scriptName") }, "sprite")
end
local worldTime = setmetatable({}, { __index = function(_, k) if k == "m_gameTime" then return MOCK.game_time end end,
                                     __newindex = function() error("write to m_worldTime") end })
EngineGlobals = readonly({ g_pBaldurChitin = readonly({ m_pObjectGame = readonly({ m_worldTime = worldTime }, "game") }, "chitin") }, "EngineGlobals")
function MOCK.fire(kind) for _, f in ipairs(MOCK.listeners[kind]) do f() end end
'''


@unittest.skipIf(lua52 is None, 'lupa (Lua 5.2) not installed')
class ProbeBehaviourTests(unittest.TestCase):
    def setUp(self):
        self.lua = lua52.LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(_MOCK_ENGINE)
        self.lua.execute(PROBE.read_text(encoding='utf-8'))
        self.mock = self.lua.globals().MOCK
        self.tick = self.lua.globals().INFAI_P2_Tick

    def step(self, clock, **state):
        for key, value in state.items():
            self.mock[key] = value
        self.mock.clock = clock
        self.assertFalse(self.tick())

    def lines(self):
        return list(self.mock.printed.values())

    def test_registers_menu_and_listeners(self):
        self.mock.fire('main')
        self.mock.fire('init')
        self.assertEqual(list(self.mock.loaded.values()), ['INFAIP2'])
        self.assertEqual(list(self.mock.pushed.values()), ['INFAI_P2_Menu'])

    def test_main_menu_publishes_nulls_even_if_engine_time_is_zero(self):
        self.step(1000, area=None, game_time=0)
        snap = parse_snapshot_line(self.lines()[-1])
        self.assertEqual((snap.fields[AREA_FIELD], snap.fields[GAME_TIME_FIELD]), (None, None))

    def test_in_map_publishes_area_and_time(self):
        self.step(1000, area='AR0602', game_time=38974)
        snap = parse_latest_snapshot('\n'.join(self.lines()) + '\n')
        self.assertEqual(snap.fields[AREA_FIELD], 'AR0602')
        self.assertEqual(snap.fields[GAME_TIME_FIELD], '38974')

    def test_throttle_heartbeat_and_change(self):
        self.step(1000, area='AR0602', game_time=1)
        self.step(1500)                         # inside the 1 s check interval
        self.step(2100, game_time=2)            # checked, unchanged area, no heartbeat yet
        self.assertEqual(len(self.lines()), 1)
        self.step(3200, area='AR0700')          # area change: immediate
        self.assertEqual(len(self.lines()), 2)
        self.step(8300)                         # 5 s since last emit: heartbeat
        self.assertEqual(len(self.lines()), 3)

    def test_destroyed_bumps_session_and_republishes(self):
        self.step(1000, area='AR0602', game_time=1)
        self.mock.fire('destroyed')
        self.step(2100)
        snaps = [parse_snapshot_line(line) for line in self.lines()]
        self.assertEqual([s.session_seq for s in snaps], [0, 1])
        self.assertEqual([s.seq for s in snaps], [1, 2])

    def test_companions_skip_protagonist_and_none(self):
        self.lua.execute('MOCK.party = { [0] = "None", [1] = "Jaheira", [2] = "None", [4] = "Imoen" }')
        self.step(1000, area='AR0602', game_time=1)
        snap = parse_snapshot_line(self.lines()[-1])
        self.assertEqual(snap.fields[PARTY_FIELD], '["imoen","jaheira"]')

    def test_party_change_republishes_and_menu_has_no_party(self):
        self.step(1000, area=None, game_time=0)
        self.assertIsNone(parse_snapshot_line(self.lines()[-1]).fields[PARTY_FIELD])
        self.step(2100, area='AR0602', game_time=1)
        self.assertEqual(parse_snapshot_line(self.lines()[-1]).fields[PARTY_FIELD], '[]')
        self.lua.execute('MOCK.party = { [1] = "Imoen" }')
        self.step(3200)
        self.assertEqual(parse_snapshot_line(self.lines()[-1]).fields[PARTY_FIELD], '["imoen"]')
        self.assertEqual(len(self.lines()), 3)

    def test_party_binding_failure_is_null_not_empty(self):
        self.step(1000, area='AR0602', game_time=1, party_error=True)
        self.assertIsNone(parse_snapshot_line(self.lines()[-1]).fields[PARTY_FIELD])

    def test_binding_failure_becomes_null(self):
        self.step(1000, area_error=True, game_time=5)
        snap = parse_snapshot_line(self.lines()[-1])
        self.assertIsNone(snap.fields[AREA_FIELD])
        self.assertIsNone(snap.fields[GAME_TIME_FIELD])

    def test_strange_resref_is_escaped_and_rejected_by_parser(self):
        self.step(1000, area='A"\\\n', game_time=1)
        line = self.lines()[-1]
        doc = json.loads(line[len('INFAI-P2 '):])
        self.assertEqual(doc['fields'][AREA_FIELD], 'A"\\\n')
        self.assertIsNone(parse_snapshot_line(line).fields[AREA_FIELD])

    def test_probe_never_writes_engine_objects(self):
        # Mocks raise on any write; a full cycle of ticks and listeners must not trip them.
        self.mock.fire('main')
        self.mock.fire('init')
        for clock in range(0, 20000, 700):
            self.step(clock, area='AR0602' if clock > 4000 else None, game_time=clock)
        self.mock.fire('destroyed')
        self.step(21000)
        self.assertGreater(len(self.lines()), 3)


if __name__ == '__main__':
    unittest.main()
