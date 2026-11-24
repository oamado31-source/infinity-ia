# SPDX-License-Identifier: Apache-2.0
"""ADR-0136 (gate P3): the minimal gateway and the EEex action module (simulated engine)."""
import dataclasses
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
    ACT_SCHEMA, CALL, DESPAWN, ESCAPE, PLACEHOLDER_ACT, SPAWN, TEMPLATES_SCHEMA, ActionError,
    ActionReceipt,
    SET_HOSTILE, call_request, confirmed, count_request, despawn_request, escape_request,
    hostile_request, load_templates, make_template, owned_creatures, render_arrival_plan,
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
    'EEex_Action_ExecuteResponseStringOnAIBaseInstantly',  # the game's own INSTANT.IDS actions only
    'EEex_Action_QueueResponseStringOnAIBase',             # EscapeArea() only, it walks (ADR-0144)
    'EEex_Sprite_DisplayTextRef',                          # a line over a head, CALL (ADR-0144)
    'EEex_UDEqual',                                        # is the leader in the area (ADR-0145)
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
            'facing = 3, count = 1, strref = -1}\n'))
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
        totals = line.replace('"reason": null', '"reason": null, "seen": 46, "seen_before": 45')
        self.assertEqual((parse_receipt(totals).seen, parse_receipt(totals).seen_before), (46, 45))
        self.assertIsNone(parse_receipt(line.replace('"reason": null',
                                                     '"reason": null, "seen": -1')))
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
            self.assertFalse(confirmed(spawn, ActionReceipt('abcdef0123', 'DONE', 1, None, 1,
                                                            46, 45)))
            # ADR-0143: ours rose, the area did not (lab S2d: nothing was created) - not done
            self.assertFalse(confirmed(spawn, ActionReceipt('abcdef0123', 'DONE', 1, None, 0,
                                                            46, 46)))
            self.assertFalse(confirmed(spawn, ActionReceipt('abcdef0123', 'DONE', 1, None, 0)))
            self.assertEqual(record_result(store, ROOT_BRANCH, spawn,
                                           ActionReceipt('abcdef0123', 'DONE', 1, None, 0, 46, 45),
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
                          ActionReceipt('2222222222', 'DONE', 1, None, 0, 46, 45), game_time=None)
            self.assertEqual(owned_creatures(store, ROOT_BRANCH), {})   # off the timeline: ignored
            refused = spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES, action_id='1111111111')
            self.assertEqual(record_result(store, ROOT_BRANCH, refused,
                                           ActionReceipt('1111111111', 'REFUSED', None,
                                                         'WRONG_AREA'), game_time=40), 'DENIED')

    def test_copies_are_asked_together_and_confirmed_by_both_counts(self):
        """ADR-0143: one request for the copies; both counts must rise by exactly that many."""
        req = spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES, action_id='abcdef0123',
                            count=3)
        self.assertEqual(req.count, 3)
        self.assertIn('count = 3, strref = -1}', render_request(req))
        self.assertTrue(confirmed(req, ActionReceipt('abcdef0123', 'DONE', 3, None, 0, 48, 45)))
        for observed, before, seen, seen_before in ((2, 0, 47, 45), (3, 0, 47, 45),
                                                    (3, 0, 49, 45), (4, 1, 47, 45)):
            self.assertFalse(confirmed(req, ActionReceipt('abcdef0123', 'DONE', observed, None,
                                                          before, seen, seen_before)))
        for bad in (0, 9, True, '2'):
            with self.assertRaises(ActionError) as ctx:
                spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES, count=bad)
            self.assertEqual(ctx.exception.code, 'BAD_COUNT')
        count = count_request('INFAI_P3TEST', 'AR0406', action_id='0123456789')
        with self.assertRaises(ActionError):
            render_request(dataclasses.replace(count, count=2))    # copies only for SPAWN

    def test_call_and_escape_requests_are_strict(self):
        """ADR-0144: CALL only for a pair a curated quest declares, never one of ours; ESCAPE
        only for ours that the branch owns; the confirmations."""
        declared = {('DRUNK1', 102877)}
        req = call_request('drunk1', 'ar0406', 102877, declared=declared, action_id='abcdef0123')
        self.assertEqual((req.op, req.name, req.area, req.strref), (CALL, 'DRUNK1', 'AR0406',
                                                                   102877))
        self.assertIn('strref = 102877}', render_request(req))
        for args, code in ((('DRUNK1', 'AR0406', 4167), 'CALL_NOT_DECLARED'),
                           (('BERNARD', 'AR0406', 102877), 'CALL_NOT_DECLARED'),
                           (('INFAI_TESTE', 'AR0406', 102877), 'BAD_NAME'),
                           (('DRUNK 1', 'AR0406', 102877), 'BAD_NAME'),
                           (('DRUNK1', 'AR0406', -1), 'BAD_STRREF'),
                           (('DRUNK1', 'AR0406', True), 'BAD_STRREF')):
            with self.assertRaises(ActionError) as ctx:
                call_request(*args, declared=declared)
            self.assertEqual(ctx.exception.code, code, args)
        self.assertTrue(confirmed(req, ActionReceipt('abcdef0123', 'DONE', 1, None, 1)))
        self.assertFalse(confirmed(req, ActionReceipt('abcdef0123', 'REFUSED', 0, 'NOT_FOUND')))
        out = escape_request('INFAI_GREGOR', 'AR0416', owned={'INFAI_GREGOR'},
                             action_id='0123456789')
        self.assertEqual(out.op, ESCAPE)
        for name, code in (('Bernard', 'NOT_OURS'), ('INFAI_OUTRO', 'NOT_OWNED')):
            with self.assertRaises(ActionError) as ctx:
                escape_request(name, 'AR0416', owned={'INFAI_GREGOR'})
            self.assertEqual(ctx.exception.code, code)
        self.assertTrue(confirmed(out, ActionReceipt('0123456789', 'DONE', 0, None, 1, 40, 41)))
        self.assertFalse(confirmed(out, ActionReceipt('0123456789', 'DONE', 1, None, 1, 41, 41)))
        with tempfile.TemporaryDirectory() as tmp:
            store = CampaignStore.open(Path(tmp) / 'c.sqlite3', 'lab')
            self.addCleanup(store.close)
            spawn = spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                  action_id='2222222222')
            record_result(store, ROOT_BRANCH, spawn,
                          ActionReceipt('2222222222', 'DONE', 1, None, 0, 41, 40), game_time=10)
            gone = escape_request('INFAI_P3TEST', 'AR0406', owned={'INFAI_P3TEST'},
                                  action_id='3333333333')
            record_result(store, ROOT_BRANCH, gone,
                          ActionReceipt('3333333333', 'DONE', 0, None, 1, 40, 41), game_time=20)
            self.assertEqual(owned_creatures(store, ROOT_BRANCH), {})     # it walked out

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
           m_baseStats = { m_generalState = 0 }, m_typeAI = { m_EnemyAlly = 128 } }
end
area = { m_resref = { get = function() return "AR0406" end }, sprites = { sprite("Bernard", 5, 5) } }
leader = sprite("Player1", 100, 200)
EEex_Area_GetVisible = function() return area end
EEex_UDEqual = function(a, b) return a == b end
EEex_Sprite_GetInPortrait = function(i) if i == 0 then return leader end end
EEex_Area_GetAllOfTypeStringInRange = function(a) return a.sprites end
EEex_Action_ExecuteResponseStringOnAIBaseInstantly = function(s, target)
  table.insert(queued, s)
  local cre, x, y = string.match(s, '^CreateCreature%("([^"]+)",%[(%d+)%.(%d+)%]')
  if cre and templates[cre] then table.insert(area.sprites, sprite(templates[cre], tonumber(x), tonumber(y))) end
  if s == "Enemy()" and target.m_typeAI then target.m_typeAI.m_EnemyAlly = 255 end
  if s == "DestroySelf()" then
    for i, sp in ipairs(area.sprites) do if sp == target then table.remove(area.sprites, i) end end
  end
end
shown = {}
EEex_Sprite_DisplayTextRef = function(target, strref, opts)       -- ADR-0144: CALL
  table.insert(shown, target.m_scriptName.get() .. ":" .. strref .. ":" .. tostring(opts.overHead)
               .. ":" .. tostring(opts.playSound))
end
walking = {}
EEex_Action_QueueResponseStringOnAIBase = function(s, target)    -- ADR-0144: EscapeArea()
  table.insert(queued, s)
  if s == "EscapeArea()" then table.insert(walking, target) end
end
function reach_exit()                                         -- the walkers vanish at the exit
  for _, w in ipairs(walking) do
    for i, sp in ipairs(area.sprites) do if sp == w then table.remove(area.sprites, i) end end
  end
  walking = {}
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
                                       ActionReceipt('abcdef0123', 'DONE', 1, None, 0, 2, 1)])
        self.tick(3500)                                    # same request still in the file
        self.assertEqual(len(self.queued()), 1)
        gone = despawn_request('INFAI_P3TEST', 'AR0406', owned={'INFAI_P3TEST'},
                               action_id='0123456789')
        self.serve(gone)
        self.tick()
        self.tick(3500)
        self.assertEqual(self.queued()[-1], 'DestroySelf()')
        self.assertEqual(self.acts()[-1], ActionReceipt('0123456789', 'DONE', 0, None, 1, 1, 2))

    def test_copies_are_created_at_the_same_instant(self):
        """ADR-0143: every copy in the same tick, one step to the side; both counts rise by three."""
        self.serve(spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                 action_id='abcdef0123', count=3))
        self.tick()
        self.assertEqual(self.queued(), ['CreateCreature("IAP3TEST",[160.230],0)',
                                         'CreateCreature("IAP3TEST",[200.230],0)',
                                         'CreateCreature("IAP3TEST",[240.230],0)'])
        self.tick(3500)
        self.assertEqual(self.acts()[-1], ActionReceipt('abcdef0123', 'DONE', 3, None, 0, 4, 1))
        self.g.files['INFAIACT'] = render_request(spawn_request(
            'IAP3TEST', 'AR0406', templates=TEMPLATES, action_id='1111111111')).replace(
            'count = 1', 'count = 9')                                   # beyond the limit
        self.tick(3500)
        self.assertEqual(self.acts()[-1].reason, 'BAD_REQUEST')
        self.assertEqual(len(self.queued()), 3)

    def test_call_shows_a_line_over_a_givers_head_only(self):
        """ADR-0144: display only; the giver of the game, by script name, with the strref."""
        self.serve(call_request('BERNARD', 'AR0406', 102877, declared={('BERNARD', 102877)},
                                action_id='abcdef0123'))
        self.tick()
        self.assertEqual(self.acts()[-1], ActionReceipt('abcdef0123', 'DONE', 1, None, 1))
        self.assertEqual([self.g.shown[i] for i in range(1, len(self.g.shown) + 1)],
                         ['Bernard:102877:true:nil'])
        self.assertEqual(self.queued(), [])                             # nothing else done
        self.serve(call_request('GAROLL', 'AR0406', 102877, declared={('GAROLL', 102877)},
                                action_id='0123456789'))
        self.tick(3500)
        self.assertEqual(self.acts()[-1].reason, 'NOT_FOUND')
        self.g.files['INFAIACT'] = render_request(call_request(
            'BERNARD', 'AR0406', 1, declared={('BERNARD', 1)}, action_id='1111111111')).replace(
            'name = "BERNARD"', 'name = "INFAI_P3TEST"')                # never one of ours
        self.tick(3500)
        self.assertEqual(self.acts()[-1].reason, 'BAD_REQUEST')

    def test_escape_walks_to_the_exit_and_holds_when_none_is_left(self):
        """ADR-0144: EscapeArea() queued on ours; counted each second up to 30 s."""
        self.serve(spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                 action_id='abcdef0123', count=2))
        self.tick()
        self.tick(3500)
        self.serve(escape_request('INFAI_P3TEST', 'AR0406', owned={'INFAI_P3TEST'},
                                  action_id='0123456789'))
        self.tick()
        self.assertEqual(self.queued()[-2:], ['EscapeArea()', 'EscapeArea()'])
        self.tick(1100)
        self.tick(1100)                                                 # still walking
        self.assertEqual(self.acts()[-1].status, 'ACCEPTED')
        self.lua.execute('reach_exit()')
        self.tick(1100)
        self.assertEqual(self.acts()[-1], ActionReceipt('0123456789', 'DONE', 0, None, 2, 1, 3))
        self.assertTrue(confirmed(escape_request('INFAI_P3TEST', 'AR0406',
                                                 owned={'INFAI_P3TEST'},
                                                 action_id='0123456789'), self.acts()[-1]))

    def test_an_escape_that_never_arrives_answers_at_the_deadline(self):
        self.serve(spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                 action_id='abcdef0123'))
        self.tick()
        self.tick(3500)
        self.serve(escape_request('INFAI_P3TEST', 'AR0406', owned={'INFAI_P3TEST'},
                                  action_id='0123456789'))
        self.tick()
        for _ in range(31):
            self.tick(1000)
        receipt = self.acts()[-1]
        self.assertEqual((receipt.status, receipt.observed), ('DONE', 1))   # stuck: not done
        self.assertFalse(confirmed(escape_request('INFAI_P3TEST', 'AR0406',
                                                  owned={'INFAI_P3TEST'},
                                                  action_id='0123456789'), receipt))

    def test_an_arrival_plan_is_made_the_moment_its_area_loads(self):
        """ADR-0145: the module creates what is missing on loading the planned area, once, and
        answers each entry like a SPAWN; other areas, names not ours and used entries: nothing."""
        plan = render_arrival_plan([
            spawn_request('IAP3TEST', 'AR0409', templates=TEMPLATES, action_id='abcdef0123',
                          count=2),
            spawn_request('IATESTE', 'AR0331', templates=TEMPLATES, action_id='0123456789')])
        self.g.files['INFAIARR'] = plan
        self.tick()                                                    # still in AR0406
        self.assertEqual(self.queued(), [])
        self.lua.execute("""
          local function body(name)
            return { m_scriptName = { get = function() return name end }, m_pos = { x = 0, y = 0 },
                     m_baseStats = { m_generalState = 0 }, m_typeAI = { m_EnemyAlly = 128 } }
          end
          area = { m_resref = { get = function() return "AR0409" end },
                   sprites = { body("Rato"), body("INFAI_P3TEST") } }""")
        self.lua.execute('leader.m_pArea = nil')                       # the party not put yet
        self.tick()                                                    # AR0409 loads
        self.tick(1000)
        self.assertEqual(self.queued(), [])                            # waits for the leader
        self.lua.execute('leader.m_pArea = area')
        self.tick()
        self.assertEqual(self.queued(), ['CreateCreature("IAP3TEST",[160.230],0)'])  # one missing
        self.tick(3500)
        self.assertEqual(self.acts()[-1], ActionReceipt('abcdef0123', 'DONE', 2, None, 1, 3, 2))
        self.lua.execute('area = { m_resref = { get = function() return "AR0400" end }, '
                         'sprites = {} }')
        self.tick()
        self.lua.execute('area = { m_resref = { get = function() return "AR0409" end }, '
                         'sprites = {} }; leader.m_pArea = area')
        self.tick(3500)
        self.tick(3500)                                                # entered again: used
        self.assertEqual(len(self.queued()), 1)
        bad = plan.replace('name = "INFAI_TESTE"', 'name = "Bernard"').replace(
            'abcdef0123', '2222222222')
        self.g.files['INFAIARR'] = bad.replace('AR0331', 'AR0400')
        self.lua.execute('area = { m_resref = { get = function() return "AR0400" end }, '
                         'sprites = {} }; leader.m_pArea = area')
        self.tick(3500)
        self.tick(3500)
        self.assertEqual(len(self.queued()), 1)                         # never a name not ours

    def test_count_reads_without_queueing(self):
        self.serve(spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                 action_id='abcdef0123'))
        self.tick()
        self.tick(3500)
        self.serve(count_request('INFAI_P3TEST', 'AR0406', action_id='2222222222'))
        self.tick()
        self.assertEqual(self.acts()[-1], ActionReceipt('2222222222', 'DONE', 1, None, 1, 2))
        self.assertEqual(len(self.queued()), 1)                         # nothing queued
        for i in range(1, len(self.g.area.sprites) + 1):                 # it falls: a corpse
            sp = self.g.area.sprites[i]
            if sp.m_scriptName.get() == 'INFAI_P3TEST':
                sp.m_baseStats.m_generalState = 0x800 | 0x1
        self.serve(count_request('INFAI_P3TEST', 'AR0406', action_id='6666666666'))
        self.tick()
        self.assertEqual(self.acts()[-1], ActionReceipt('6666666666', 'DONE', 0, None, 0, 2))  # the corpse is seen
        self.serve(count_request('INFAI_NINGUEM', 'AR0406', action_id='4444444444'))
        self.tick()
        self.assertEqual(self.acts()[-1], ActionReceipt('4444444444', 'DONE', 0, None, 0, 2))
        self.serve(count_request('INFAI_P3TEST', 'AR0300', action_id='5555555555'))
        self.tick()
        self.assertEqual(self.acts()[-1].reason, 'WRONG_AREA')

    def test_set_hostile_queues_enemy_and_counts_the_hostile(self):
        for action_id in ('abcdef0123', '1234512345'):
            self.serve(spawn_request('IAP3TEST', 'AR0406', templates=TEMPLATES,
                                     action_id=action_id))
            self.tick()
            self.tick(3500)
        req = hostile_request('INFAI_P3TEST', 'AR0406', owned={'INFAI_P3TEST'},
                              action_id='7777777777')
        self.assertEqual(req.op, SET_HOSTILE)
        self.serve(req)
        self.tick()
        self.assertEqual(self.queued()[-2:], ['Enemy()', 'Enemy()'])         # both of ours
        self.tick(3500)
        receipt = self.acts()[-1]
        self.assertEqual((receipt.status, receipt.before, receipt.observed), ('DONE', 2, 2))
        self.assertTrue(confirmed(req, receipt))
        self.assertFalse(confirmed(req, ActionReceipt('7777777777', 'DONE', 1, None, 2)))
        self.assertFalse(confirmed(req, ActionReceipt('7777777777', 'DONE', 0, None, 0)))
        bernard = self.g.area.sprites[1]
        self.assertEqual(bernard.m_typeAI.m_EnemyAlly, 128)                 # never the game's
        nobody = hostile_request('INFAI_NINGUEM', 'AR0406', owned={'INFAI_NINGUEM'},
                                 action_id='8888888888')
        self.serve(nobody)
        self.tick()
        self.assertEqual(self.acts()[-1].reason, 'NOT_FOUND')
        with self.assertRaises(ActionError):
            hostile_request('Bernard', 'AR0406', owned={'Bernard'})

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
        self.assertEqual(re.findall(r"string\.format\('(\w+)\(", self.raw),
                         ['CreateCreature', 'LeaveAreaLUA'])
        # ADR-0146: a passage only into or out of an area of ours, from one fixed template
        self.assertEqual(self.raw.count('LeaveAreaLUA("%s","",[%d.%d],%d)'), 1)
        self.assertIn('"^IA%d%d%d%d$"', self.raw)
        self.assertIn('CreateCreature("%s",[%d.%d],%d)', self.raw)     # ACTION.IDS: no name
        self.assertIn('"^IA[A-Z0-9]+$"', self.raw)                       # only our files
        # EEex does "bCheckForLineOfSight or 1": false would turn the check ON (lab, S1x)
        self.assertIn('"[ANYONE]", INFAI_ACT_RANGE, 0, 0)', self.raw)
        self.assertNotRegex(self.code, r'GetAllOfTypeStringInRange\([^)]*false')
        # the engine's search radius is a signed 16-bit value: 65535 would be -1 (lab, S1x)
        self.assertLessEqual(int(re.search(r'INFAI_ACT_RANGE = (\d+)', self.raw).group(1)), 32767)
        self.assertEqual(self.raw.count('"DestroySelf()"'), 1)
        self.assertEqual(self.raw.count('"Enemy()"'), 1)                   # ADR-0142
        # INSTANT.IDS actions run at once: a queue on the leader is lost in a fight (lab, ADR-0142);
        # only EscapeArea(), which walks, is queued, on our own creature (ADR-0144)
        self.assertEqual(self.raw.count('QueueResponseString'), 1)
        self.assertIn('EEex_Action_QueueResponseStringOnAIBase, "EscapeArea()", sprite', self.raw)
        self.assertEqual(self.raw.count('"EscapeArea()"'), 1)
        # CALL only shows a line of dialog.tlk over a head (ADR-0144): one call, no other option
        self.assertEqual(self.raw.count('EEex_Sprite_DisplayTextRef'), 1)
        self.assertIn('EEex_Sprite_DisplayTextRef, sprite, req.strref, { overHead = true })',
                      self.raw)
        self.assertNotRegex(self.code, r'SetGlobal|ActionOverride|StartCutScene|GiveItem|Kill\(|Ally\(')

    def test_never_assigns_to_engine_state(self):
        for src_line in self.code.splitlines():
            for lhs in re.findall(r'([\w.\[\]:]+)\s*=(?!=)', src_line):
                if src_line.strip().startswith(('if ', 'elseif ', 'for ')):
                    continue
                if lhs == 'overHead' and '{ overHead = true }' in src_line:
                    continue              # a key of the options table of CALL, not engine state
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
