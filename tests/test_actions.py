# SPDX-License-Identifier: Apache-2.0
"""ADR-0136 (gate P3): the minimal gateway and the EEex action module (simulated engine)."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.actions.gateway import (  # noqa: E402
    ACT_SCHEMA, DESPAWN, PLACEHOLDER_ACT, SPAWN, TEMPLATES_SCHEMA, ActionError, ActionReceipt,
    confirmed, count_request, despawn_request, load_templates, make_template, owned_creatures,
    parse_receipt,
    record_requested, record_result, render_request, spawn_request, templates_path,
)
from infinity_ai.bridge.manifest import modpack_hash  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402
from test_eeex_probe import FORBIDDEN, strip_lua  # noqa: E402

try:
    import lupa  # type: ignore
except ImportError:
    lupa = None

MODULE = ROOT / 'tools' / 'eeex-probe' / 'M_INFAIA.lua'
MENU = ROOT / 'tools' / 'eeex-probe' / 'INFAIAM.menu'
TEMPLATES = {'IAP3TEST': 'INFAI_P3TEST', 'IATESTE': 'INFAI_TESTE'}
ALLOWED = frozenset({
    'EEex_Resource_Fetch', 'Infinity_DoFile', 'Infinity_GetClockTicks', 'EEex_Area_GetVisible',
    'EEex_Sprite_GetInPortrait', 'EEex_Area_GetAllOfTypeStringInRange',
    'EEex_Action_QueueResponseStringOnAIBase',   # queues the game's own actions only
    'EEex_Menu_AddMainFileLoadedListener', 'EEex_Menu_LoadFile', 'Infinity_PushMenu',
    'EEex_GameState_AddInitializedListener', 'EEex_Menu_AddAfterMainFileReloadedListener',
})


class GatewayTests(unittest.TestCase):
    def test_spawn_only_our_creature_files(self):
        req = spawn_request('iap3test', 'ar0406', templates=TEMPLATES, action_id='abcdef0123')
        self.assertEqual((req.op, req.cre, req.area, req.name, req.x, req.y),
                         (SPAWN, 'IAP3TEST', 'AR0406', 'INFAI_P3TEST', -1, -1))
        for kwargs, code in ((dict(cre='DPMALE'), 'NOT_OUR_TEMPLATE'),
                             (dict(cre='IANOPE'), 'UNKNOWN_TEMPLATE'), (dict(cre='a b'), 'BAD_CRE'),
                             (dict(area='AR 0406'), 'BAD_AREA'), (dict(x=10), 'BAD_POINT'),
                             (dict(x=10, y=99999), 'BAD_POINT'), (dict(facing=16), 'BAD_FACING'),
                             (dict(action_id='X'), 'BAD_ACTION_ID')):
            args = dict(cre='IAP3TEST', area='AR0406', templates=TEMPLATES)
            args.update(kwargs)
            with self.assertRaises(ActionError) as ctx:
                spawn_request(args.pop('cre'), args.pop('area'), **args)
            self.assertEqual(ctx.exception.code, code, kwargs)

    def test_despawn_only_our_creatures(self):
        owned = {'INFAI_P3TEST'}
        req = despawn_request('infai_p3test', 'AR0406', owned=owned, action_id='0123456789')
        self.assertEqual((req.op, req.name), (DESPAWN, 'INFAI_P3TEST'))
        with self.assertRaises(ActionError) as ctx:
            despawn_request('Bernard', 'AR0406', owned=owned)
        self.assertEqual(ctx.exception.code, 'NOT_OURS')
        with self.assertRaises(ActionError) as ctx:
            despawn_request('INFAI_OUTRA', 'AR0406', owned=owned)
        self.assertEqual(ctx.exception.code, 'NOT_OWNED')

    def test_request_file_has_literals_only(self):
        req = spawn_request('IAP3TEST', 'AR0406', x=100, y=200, facing=3, templates=TEMPLATES,
                            action_id='abcdef0123')
        self.assertEqual(render_request(req), (
            'INFAI_ACT_Request = {action_id = "abcdef0123", op = "SPAWN_CREATURE", '
            'area = "AR0406", name = "INFAI_P3TEST", cre = "IAP3TEST", x = 100, y = 200, '
            'facing = 3}\n'))
        bad = req.__class__('abcdef0123', SPAWN, 'AR0406', 'INFAI_P3TEST',
                            'X")DestroySelf(', 0, 0, 0)
        with self.assertRaises(ActionError):
            render_request(bad)
        self.assertIn('action_id = ""', PLACEHOLDER_ACT)

    def test_our_creature_file_carries_our_name_and_the_registry_is_local(self):
        source = bytearray(0x2D4)
        source[:8] = b'CRE V1.0'
        source[0x280:0x286] = b'DPMALE'
        made = make_template(bytes(source), 'INFAI_P3TEST')
        self.assertEqual(made[0x280:0x2A0], b'INFAI_P3TEST'.ljust(32, b'\0'))
        self.assertEqual(made[:0x280], bytes(source[:0x280]))
        with self.assertRaises(ActionError):
            make_template(bytes(source), 'Bernard')
        with self.assertRaises(ActionError):
            make_template(b'BAM V1  ', 'INFAI_P3TEST')
        corpse = bytearray(source)
        corpse[0x20:0x24] = (0x800).to_bytes(4, 'little')      # STATE_DEAD (lab: DPMALE)
        with self.assertRaises(ActionError) as ctx:
            make_template(bytes(corpse), 'INFAI_P3TEST')
        self.assertEqual(ctx.exception.code, 'DEAD_SOURCE_CRE')
        with tempfile.TemporaryDirectory() as tmp:
            build = 'sha256:' + 'ab' * 32
            path = templates_path(build, Path(tmp))
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'schema': TEMPLATES_SCHEMA, 'build_fingerprint': build,
                                        'templates': [{'resref': 'IAP3TEST',
                                                       'script_name': 'INFAI_P3TEST'},
                                                      {'resref': 'DPMALE',
                                                       'script_name': 'INFAI_X'}]}))
            self.assertEqual(load_templates(build, Path(tmp)), {'IAP3TEST': 'INFAI_P3TEST'})
            self.assertEqual(load_templates('sha256:' + 'cd' * 32, Path(tmp)), {})

    def test_receipts_are_parsed_strictly(self):
        line = 'INFO: INFAI-ACT ' + json.dumps({'schema': ACT_SCHEMA, 'action_id': 'abcdef0123',
                                                'status': 'DONE', 'observed': 1, 'reason': None})
        self.assertEqual(parse_receipt(line), ActionReceipt('abcdef0123', 'DONE', 1, None))
        with_before = line.replace('"reason": null', '"reason": null, "before": 0')
        self.assertEqual(parse_receipt(with_before).before, 0)
        for doc in ({'schema': 'x'}, {'schema': ACT_SCHEMA, 'action_id': 'abc', 'status': 'DONE'},
                    {'schema': ACT_SCHEMA, 'action_id': 'abcdef0123', 'status': 'MAYBE'},
                    {'schema': ACT_SCHEMA, 'action_id': 'abcdef0123', 'status': 'DONE',
                     'observed': True},
                    {'schema': ACT_SCHEMA, 'action_id': 'abcdef0123', 'status': 'REFUSED',
                     'reason': 'x; rm'}):
            self.assertIsNone(parse_receipt('INFAI-ACT ' + json.dumps(doc)), doc)

    def test_only_the_hosts_word_confirms_and_ownership_follows_the_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CampaignStore.open(Path(tmp) / 'c.sqlite3', 'lab')
            self.addCleanup(store.close)
            spawn = spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES, action_id='abcdef0123')
            with self.assertRaises(ActionError) as ctx:
                record_requested(store, ROOT_BRANCH, spawn, game_time=None)
            self.assertEqual(ctx.exception.code, 'NO_GAME_TIME')
            record_requested(store, ROOT_BRANCH, spawn, game_time=10)
            self.assertEqual(record_result(store, ROOT_BRANCH, spawn, None, game_time=10),
                             'UNCERTAIN')
            accepted = ActionReceipt('abcdef0123', 'ACCEPTED', None)
            self.assertFalse(confirmed(spawn, accepted))
            self.assertEqual(record_result(store, ROOT_BRANCH, spawn,
                                           ActionReceipt('abcdef0123', 'DONE', 0, None, 0),
                                           game_time=10),
                             'UNCERTAIN')               # queued, but nobody there: not done
            self.assertFalse(confirmed(spawn, ActionReceipt('abcdef0123', 'DONE', 1, None, 1)))
            self.assertEqual(record_result(store, ROOT_BRANCH, spawn,
                                           ActionReceipt('abcdef0123', 'DONE', 1, None, 0),
                                           game_time=20),
                             'HOST_CONFIRMED')
            self.assertEqual(owned_creatures(store, ROOT_BRANCH), {'INFAI_P3TEST': 'AR0406'})
            older = store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=15,
                                      fork_epoch=1)
            self.assertEqual(owned_creatures(store, older), {})        # a save from before
            gone = despawn_request('INFAI_P3TEST', 'AR0406',
                                   owned=set(owned_creatures(store, ROOT_BRANCH)),
                                   action_id='0123456789')
            self.assertEqual(record_result(store, ROOT_BRANCH, gone,
                                           ActionReceipt('0123456789', 'DONE', 0), game_time=30),
                             'HOST_CONFIRMED')
            self.assertEqual(owned_creatures(store, ROOT_BRANCH), {})
            timeless = spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                     action_id='2222222222')
            record_result(store, ROOT_BRANCH, timeless,
                          ActionReceipt('2222222222', 'DONE', 1, None, 0), game_time=None)
            self.assertEqual(owned_creatures(store, ROOT_BRANCH), {})   # off the timeline: ignored
            refused = spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES, action_id='1111111111')
            self.assertEqual(record_result(store, ROOT_BRANCH, refused,
                                           ActionReceipt('1111111111', 'REFUSED', None,
                                                         'WRONG_AREA'), game_time=40), 'DENIED')

    def test_request_file_does_not_change_the_modpack(self):
        def manifest(*files):
            return {'game': {'override_files': [{'path': p, 'sha256': h * 64} for p, h in files],
                             'weidu_log_sha256': None, 'eeex_markers': [],
                             'mod_setup_markers': []}}
        base = manifest(('override/M_INFAIA.lua', 'a'))
        self.assertEqual(modpack_hash(base), modpack_hash(manifest(
            ('override/M_INFAIA.lua', 'a'), ('override/INFAIACT.lua', 'b'))))


ENGINE = """
printed = {}
print = function(s) table.insert(printed, s) end
clock = 1000
files = {}
queued = {}
templates = { IAP3TEST = "INFAI_P3TEST" }
Infinity_GetClockTicks = function() return clock end
Infinity_DoFile = function(name) local f = files[name]; if f then load(f)() end end
Infinity_PushMenu = function() end
EEex_Resource_Fetch = function() return nil end
EngineGlobals = { dimmDump = function() end }
EEex_Menu_AddMainFileLoadedListener = function() end
EEex_Menu_LoadFile = function() end
EEex_GameState_AddInitializedListener = function() end
EEex_Menu_AddAfterMainFileReloadedListener = function() end
local function sprite(name, x, y)
  return { m_scriptName = { get = function() return name end }, m_pos = { x = x, y = y },
           m_baseStats = { m_generalState = 0 } }
end
area = { m_resref = { get = function() return "AR0406" end }, sprites = { sprite("Bernard", 5, 5) } }
leader = sprite("Player1", 100, 200)
EEex_Area_GetVisible = function() return area end
EEex_Sprite_GetInPortrait = function(i) if i == 0 then return leader end end
EEex_Area_GetAllOfTypeStringInRange = function(a) return a.sprites end
EEex_Action_QueueResponseStringOnAIBase = function(s, target)
  table.insert(queued, s)
  local cre, x, y = string.match(s, '^CreateCreature%("([^"]+)",%[(%d+)%.(%d+)%]')
  if cre and templates[cre] then table.insert(area.sprites, sprite(templates[cre], tonumber(x), tonumber(y))) end
  if s == "DestroySelf()" then
    for i, sp in ipairs(area.sprites) do if sp == target then table.remove(area.sprites, i) end end
  end
end
"""


@unittest.skipIf(lupa is None, 'lupa not installed')
class ModuleTests(unittest.TestCase):
    def setUp(self):
        self.lua = lupa.LuaRuntime()
        self.lua.execute(ENGINE)
        self.lua.execute(MODULE.read_text(encoding='utf-8'))
        self.g = self.lua.globals()

    def tick(self, ms=600):
        self.g.clock = self.g.clock + ms
        self.g.INFAI_ACT_Tick()

    def acts(self):
        out = []
        for i in range(1, len(self.g.printed) + 1):
            r = parse_receipt(self.g.printed[i])
            if r is not None:
                out.append(r)
        return out

    def serve(self, req):
        self.g.files['INFAIACT'] = render_request(req)

    def queued(self):
        return [self.g.queued[i] for i in range(1, len(self.g.queued) + 1)]

    def test_spawn_confirm_repeat_and_despawn(self):
        spawn = spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES, action_id='abcdef0123')
        self.serve(spawn)
        self.tick()
        self.assertEqual(self.queued(), ['CreateCreature("IAP3TEST",[160.230],0)'])
        self.tick(3500)
        self.assertEqual(self.acts(), [ActionReceipt('abcdef0123', 'ACCEPTED', None),
                                       ActionReceipt('abcdef0123', 'DONE', 1, None, 0)])
        self.tick(3500)                                    # same request still in the file
        self.assertEqual(len(self.queued()), 1)
        gone = despawn_request('INFAI_P3TEST', 'AR0406', owned={'INFAI_P3TEST'},
                               action_id='0123456789')
        self.serve(gone)
        self.tick()
        self.tick(3500)
        self.assertEqual(self.queued()[-1], 'DestroySelf()')
        self.assertEqual(self.acts()[-1], ActionReceipt('0123456789', 'DONE', 0, None, 1))

    def test_count_reads_without_queueing(self):
        self.serve(spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                 action_id='abcdef0123'))
        self.tick()
        self.tick(3500)
        self.serve(count_request('INFAI_P3TEST', 'AR0406', action_id='2222222222'))
        self.tick()
        self.assertEqual(self.acts()[-1], ActionReceipt('2222222222', 'DONE', 1, None, 1))
        self.assertEqual(len(self.queued()), 1)                         # nothing queued
        for i in range(1, len(self.g.area.sprites) + 1):                 # it falls: a corpse
            sp = self.g.area.sprites[i]
            if sp.m_scriptName.get() == 'INFAI_P3TEST':
                sp.m_baseStats.m_generalState = 0x800 | 0x1
        self.serve(count_request('INFAI_P3TEST', 'AR0406', action_id='6666666666'))
        self.tick()
        self.assertEqual(self.acts()[-1], ActionReceipt('6666666666', 'DONE', 0, None, 0))
        self.serve(count_request('INFAI_NINGUEM', 'AR0406', action_id='4444444444'))
        self.tick()
        self.assertEqual(self.acts()[-1], ActionReceipt('4444444444', 'DONE', 0, None, 0))
        self.serve(count_request('INFAI_P3TEST', 'AR0300', action_id='5555555555'))
        self.tick()
        self.assertEqual(self.acts()[-1].reason, 'WRONG_AREA')

    def test_refusals(self):
        self.g.files['INFAIACT'] = ('INFAI_ACT_Request = {action_id = "abcdef0123", '
                                    'op = "DESPAWN", area = "AR0406", name = "Bernard", '
                                    'cre = "", x = -1, y = -1, facing = 0}')
        self.tick()
        self.assertEqual(self.acts()[-1].reason, 'BAD_REQUEST')        # not one of ours
        elsewhere = spawn_request('IAP3TEST', 'AR0300', templates=TEMPLATES, action_id='1111111111')
        self.serve(elsewhere)
        self.tick()
        self.assertEqual(self.acts()[-1].reason, 'WRONG_AREA')
        missing = despawn_request('INFAI_SUMIU', 'AR0406', owned={'INFAI_SUMIU'},
                                  action_id='3333333333')
        self.serve(missing)
        self.tick()
        self.assertEqual(self.acts()[-1].reason, 'NOT_FOUND')
        self.assertEqual(self.queued(), [])
        self.g.files['INFAIACT'] = PLACEHOLDER_ACT
        self.tick()
        self.assertEqual(len(self.acts()), 3)


class StaticTests(unittest.TestCase):
    def setUp(self):
        self.raw = MODULE.read_text(encoding='utf-8')
        self.code = strip_lua(self.raw)

    def test_only_allowlisted_engine_functions(self):
        used = set(re.findall(r'\b(?:EEex|Infinity)_\w+', self.code))
        self.assertEqual(used - ALLOWED, set())

    def test_no_forbidden_capabilities(self):
        self.assertIsNone(FORBIDDEN.search(self.code), FORBIDDEN.search(self.code))

    def test_actions_come_from_fixed_templates(self):
        self.assertEqual(re.findall(r"string\.format\('(\w+)\(", self.raw), ['CreateCreature'])
        self.assertIn('CreateCreature("%s",[%d.%d],%d)', self.raw)     # ACTION.IDS: no name
        self.assertIn('"^IA[A-Z0-9]+$"', self.raw)                       # only our files
        # EEex does "bCheckForLineOfSight or 1": false would turn the check ON (lab, S1x)
        self.assertIn('"[ANYONE]", INFAI_ACT_RANGE, 0, 0)', self.raw)
        self.assertNotRegex(self.code, r'GetAllOfTypeStringInRange\([^)]*false')
        # the engine's search radius is a signed 16-bit value: 65535 would be -1 (lab, S1x)
        self.assertLessEqual(int(re.search(r'INFAI_ACT_RANGE = (\d+)', self.raw).group(1)), 32767)
        self.assertEqual(self.raw.count('"DestroySelf()"'), 1)
        self.assertNotRegex(self.code, r'SetGlobal|ActionOverride|StartCutScene|GiveItem|Kill\(')

    def test_never_assigns_to_engine_state(self):
        for src_line in self.code.splitlines():
            for lhs in re.findall(r'([\w.\[\]:]+)\s*=(?!=)', src_line):
                if src_line.strip().startswith(('if ', 'elseif ', 'for ')):
                    continue
                with self.subTest(line=src_line.strip()):
                    self.assertNotRegex(lhs, r'\.m_|:|EngineGlobals')
                    root = lhs.split('.')[0].split('[')[0]
                    self.assertTrue(root.startswith(('INFAI_', 'infai_')) or root.islower(), lhs)

    def test_menu_is_bound_to_the_module(self):
        menu = MENU.read_text(encoding='utf-8')
        self.assertIn('INFAI_ACT_Menu', menu)
        self.assertIn('INFAI_ACT_Tick()', menu)
        self.assertIn('"INFAIAM"', self.raw)


if __name__ == '__main__':
    unittest.main()
