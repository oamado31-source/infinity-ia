# SPDX-License-Identifier: Apache-2.0
"""ADR-0148: a giver who walks in through the door (presence from START, walk_to, its own call)
and the turn-in that pays once (REWARD)."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.actions.gateway import (  # noqa: E402
    REWARD, SPAWN, ActionError, ActionReceipt, confirmed, render_arrival_plan, render_request,
    reward_request, spawn_request,
)
from infinity_ai.quests.authoring import check_quest  # noqa: E402
from infinity_ai.quests.narrative import advance, parse_quest, state_of  # noqa: E402
from infinity_ai.quests.presence import (  # noqa: E402
    ENTER, arrival_plan, call_due, decide, dispatch_reward, request_for, reward_due,
    reward_status, wanted,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

try:
    import lupa  # type: ignore
except ImportError:  # pragma: no cover
    lupa = None

DOC = json.loads((ROOT / 'knowledge' / 'quests' / 'bernard-brooch.pt_BR.json').read_text())
GIVER = 'npc:infai_doran'
TEMPLATES = {'IADORAN': 'INFAI_DORAN', 'IAP3TEST': 'INFAI_P3TEST'}
DOOR, COUNTER = (580, 900), (760, 640)
DORAN = {'presence_id': 'doran', 'cre': 'IADORAN', 'name': 'INFAI_DORAN', 'area': 'AR0406',
         'from': 'START', 'x': DOOR[0], 'y': DOOR[1], 'walk_to': {'x': COUNTER[0], 'y': COUNTER[1]},
         'leave': 'ESCAPE'}
CALL = {'script_name': 'INFAI_DORAN', 'area': 'AR0406', 'strref': 102877, 'every': 4500}


def doc(presence=None, call=None, reward=None, giver=GIVER):
    d = copy.deepcopy(DOC)
    d['giver']['npc_id'] = giver
    d['presence'] = [DORAN] if presence is None else presence
    if call is not None:
        d['call'] = call
    if reward is not None:
        d['turn_in']['reward'] = reward
    return d


class FormatTests(unittest.TestCase):
    def test_start_walk_reward_and_own_call(self):
        q = parse_quest(doc(call=CALL, reward={'gold': 500, 'xp': 1000}))
        p = q.presence[0]
        self.assertEqual((p.start, p.x, p.y, p.walk_x, p.walk_y), ('START', *DOOR, *COUNTER))
        self.assertEqual((q.call.script_name, q.reward_gold, q.reward_xp),
                         ('INFAI_DORAN', 500, 1000))
        self.assertEqual((parse_quest(doc()).reward_gold, parse_quest(doc()).reward_xp), (0, 0))
        self.assertEqual(parse_quest(doc(reward={'gold': 50})).reward_xp, 0)

    def test_strict(self):
        bad_presence = (
            dict(DORAN, walk_to={'x': 1}),                       # both or none
            dict(DORAN, walk_to={'x': 1, 'y': 2, 'z': 3}),
            dict(DORAN, walk_to={'x': -1, 'y': 2}),
            dict(DORAN, walk_to={'x': True, 'y': 2}),
            {k: v for k, v in DORAN.items() if k not in ('x', 'y')},   # a walk needs a birth
            dict(DORAN, hostile_from='START'),                   # never hostile from the start
            dict(DORAN, until='START'),
        )
        for p in bad_presence:
            self.assertIsNone(parse_quest(doc(presence=[p])), p)
        for r in ({}, {'gold': 0}, {'gold': 0, 'xp': 0}, {'gold': -1}, {'gold': 10001},
                  {'xp': 50001}, {'gold': '5'}, {'gold': True}, {'gold': 5, 'item': 'x'}, []):
            self.assertIsNone(parse_quest(doc(reward=r)), r)
        # the call from one of ours only when it is a presence of the quest
        self.assertIsNone(parse_quest(doc(call=dict(CALL, script_name='INFAI_OUTRO'))))
        self.assertIsNone(parse_quest(doc(presence=[], call=CALL)))

    def test_checker_agrees_and_warns(self):
        good = dict(doc(call=CALL, reward={'gold': 500}), curation=DOC['curation'])
        self.assertTrue(check_quest(good).ok, check_quest(good).errors)
        for d, code in ((doc(reward={'gold': 0}), 'REWARD'),
                        (doc(reward={'gold': 5, 'item': 'x'}), 'REWARD'),
                        (doc(presence=[dict(DORAN, walk_to={'x': 1})]), 'WALK'),
                        (doc(presence=[{k: v for k, v in DORAN.items() if k not in ('x', 'y')}]),
                         'WALK'),
                        (doc(presence=[dict(DORAN, hostile_from='START')]), 'HOSTILE'),
                        (doc(call=dict(CALL, script_name='INFAI_OUTRO')), 'CALL')):
            self.assertIn(code, [e.code for e in check_quest(d).errors], d)
        # a new person giving the quest, without a START presence in its area
        warned = check_quest(doc(presence=[dict(DORAN, **{'from': 'ACCEPTED'})]))
        self.assertIn('GIVER_PRESENCE', [w.code for w in warned.warnings])
        self.assertNotIn('GIVER_PRESENCE', [w.code for w in check_quest(doc()).warnings])

    def test_checker_warns_a_request_written_as_an_order(self):
        # lab 2026-11-26: Doran repeated "Peça que o grupo dê uma olhada na rua" word for word
        def orders(d):
            return [w.where for w in check_quest(d).warnings if w.code == 'FACT_ORDER']
        d = doc()
        d['giver']['offer_fact'] = ('Você quer saber se vigiam a taverna. Peça que o grupo dê uma '
                                    'olhada na rua, e pergunte se aceitam.')
        d['turn_in']['fact'] = 'O grupo voltou. Mande que voltem amanhã.'
        self.assertEqual(orders(d), ['giver.offer_fact', 'turn_in.fact'])
        d['giver']['offer_fact'] = ('Você quer saber se vigiam a taverna e quer que o grupo dê uma '
                                    'olhada na rua. Pergunte se o grupo aceita.')
        d['turn_in']['fact'] = 'O grupo voltou. Agradeça primeiro. Depois conte o que sabe.'
        self.assertEqual(orders(d), [])     # orders about one's own speech work (Gregor)
        for name in ('bernard-brooch', 'sarevok-diary'):
            curated = json.loads((ROOT / 'knowledge' / 'quests' / f'{name}.pt_BR.json').read_text())
            self.assertEqual(orders(curated), [], name)


class GatewayTests(unittest.TestCase):
    def test_walk_and_reward_requests(self):
        req = spawn_request('IADORAN', 'AR0406', x=580, y=900, templates=TEMPLATES,
                            action_id='abcdef0123', to_x=760, to_y=640)
        self.assertIn('to_x = 760, to_y = 640, gold = 0, xp = 0}', render_request(req))
        for kw in ({'to_x': 760}, {'to_x': -2, 'to_y': 5}, {'to_x': 40000, 'to_y': 5}):
            with self.assertRaises(ActionError):
                spawn_request('IADORAN', 'AR0406', x=580, y=900, templates=TEMPLATES, **kw)
        with self.assertRaises(ActionError):                     # never from "near the leader"
            spawn_request('IADORAN', 'AR0406', templates=TEMPLATES, to_x=760, to_y=640)
        self.assertIn('to_x = 760, to_y = 640}', render_arrival_plan([req]))
        pay = reward_request('ar0406', gold=500, xp=1000, action_id='0123456789')
        self.assertEqual((pay.op, pay.area, pay.name, pay.gold, pay.xp),
                         (REWARD, 'AR0406', 'INFAI_PARTY', 500, 1000))
        self.assertIn('gold = 500, xp = 1000}', render_request(pay))
        for gold, xp in ((0, 0), (-1, 5), (10001, 0), (0, 50001), (True, 0), ('5', 0)):
            with self.assertRaises(ActionError):
                reward_request('AR0406', gold=gold, xp=xp)
        import dataclasses
        for bad in (dataclasses.replace(req, gold=5), dataclasses.replace(pay, to_x=1, to_y=1),
                    dataclasses.replace(pay, name='INFAI_DORAN'),
                    dataclasses.replace(pay, gold=20000)):
            with self.assertRaises(ActionError):
                render_request(bad)
        self.assertTrue(confirmed(pay, ActionReceipt('0123456789', 'DONE', 1)))
        self.assertFalse(confirmed(pay, ActionReceipt('0123456789', 'DONE', None, 'UNVERIFIED')))


class FakeTransport:
    def __init__(self, answer):
        self.answer, self.sent = answer, []

    def send(self, req):
        self.sent.append(req)
        return self.answer(req) if self.answer else None


class FlowTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.q = parse_quest(doc(call=CALL, reward={'gold': 500, 'xp': 1000}))
        self.quests = {self.q.quest_id: self.q}
        self.t = 1000

    def say(self, speaker, text):
        self.t += 10
        return advance(self.store, ROOT_BRANCH, self.quests, speaker=speaker, text=text,
                       area='AR0406', game_time=self.t)

    def resolve(self):
        self.say(GIVER, 'tem trabalho?')
        self.say(GIVER, 'aceito')
        self.say('npc:scdur', 'e o broche furtado?')
        self.say(GIVER, 'foi o unger')
        self.assertTrue(state_of(self.store, ROOT_BRANCH, self.q.quest_id).resolved)

    def test_start_presence_is_wanted_before_the_offer_and_walks_in(self):
        st = state_of(self.store, ROOT_BRANCH, self.q.quest_id)
        self.assertTrue(wanted(st, self.q.presence[0]))
        decision, _ = decide(self.store, ROOT_BRANCH, self.quests, area='AR0406', game_time=1)
        self.assertEqual(decision.rule, 'VERIFY')                # counted first, as always
        plan = arrival_plan(self.store, ROOT_BRANCH, self.quests, area='AR0400', game_time=1,
                            templates=TEMPLATES)
        self.assertEqual([(r.op, r.area, r.x, r.y, r.to_x, r.to_y) for _, r in plan],
                         [(SPAWN, 'AR0406', *DOOR, *COUNTER)])
        from infinity_ai.quests.presence import Decision
        req = request_for(Decision(self.q.quest_id, self.q.presence[0], ENTER), self.store,
                          ROOT_BRANCH, templates=TEMPLATES)
        self.assertEqual((req.x, req.y, req.to_x, req.to_y), (*DOOR, *COUNTER))

    def test_own_call_is_due_before_acceptance(self):
        self.assertIs(call_due(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                               game_time=5000), self.q)

    def test_reward_once_only_after_resolution(self):
        self.assertIsNone(reward_due(self.store, ROOT_BRANCH, self.quests))
        self.resolve()
        self.assertIs(reward_due(self.store, ROOT_BRANCH, self.quests), self.q)
        paid = FakeTransport(lambda req: ActionReceipt(req.action_id, 'DONE', 1))
        state = dispatch_reward(self.store, ROOT_BRANCH, self.q, transport=paid, area='AR0406',
                                game_time=self.t)
        self.assertEqual(state, 'HOST_CONFIRMED')
        self.assertEqual((paid.sent[0].gold, paid.sent[0].xp), (500, 1000))
        self.assertEqual(reward_status(self.store, ROOT_BRANCH, self.q.quest_id), 'PAID')
        self.assertIsNone(reward_due(self.store, ROOT_BRANCH, self.quests))   # never twice

    def test_unconfirmed_reward_is_held_never_resent(self):
        self.resolve()
        silent = FakeTransport(lambda req: ActionReceipt(req.action_id, 'DONE', None,
                                                         'UNVERIFIED'))
        state = dispatch_reward(self.store, ROOT_BRANCH, self.q, transport=silent,
                                area='AR0406', game_time=self.t)
        self.assertEqual(state, 'UNCERTAIN')
        self.assertEqual(reward_status(self.store, ROOT_BRANCH, self.q.quest_id), 'HELD')
        self.assertIsNone(reward_due(self.store, ROOT_BRANCH, self.quests))

    def test_quest_without_reward_never_pays(self):
        q = parse_quest(doc())
        self.quests = {q.quest_id: q}
        self.q = q
        self.resolve()
        self.assertIsNone(reward_due(self.store, ROOT_BRANCH, self.quests))


ENGINE_EXTRA = """
EngineGlobals.g_pBaldurChitin = { m_pObjectGame = { m_nPartyGold = 100 } }
leader.m_baseStats.m_xp = 2000
moved = {}
local instantly = EEex_Action_ExecuteResponseStringOnAIBaseInstantly
EEex_Action_ExecuteResponseStringOnAIBaseInstantly = function(s, target)
  local gold = string.match(s, '^GiveGoldForce%((%d+)%)$')
  if gold and pay_ok then
    EngineGlobals.g_pBaldurChitin.m_pObjectGame.m_nPartyGold =
      EngineGlobals.g_pBaldurChitin.m_pObjectGame.m_nPartyGold + tonumber(gold)
  end
  local xp = string.match(s, '^AddexperienceParty%((%d+)%)$')
  if xp and pay_ok then leader.m_baseStats.m_xp = leader.m_baseStats.m_xp + tonumber(xp) end
  return instantly(s, target)
end
local queue = EEex_Action_QueueResponseStringOnAIBase
EEex_Action_QueueResponseStringOnAIBase = function(s, target)
  if string.match(s, '^MoveToPoint') then table.insert(moved, target.m_scriptName.get() .. ':' .. s) end
  return queue(s, target)
end
pay_ok = true
"""


@unittest.skipIf(lupa is None, 'lupa not installed')
class ModuleTests(unittest.TestCase):
    def setUp(self):
        from test_actions import ENGINE, MODULE
        self.lua = lupa.LuaRuntime()
        self.lua.execute(ENGINE)
        self.lua.execute('templates.IADORAN = "INFAI_DORAN"')
        self.lua.execute(ENGINE_EXTRA)
        self.lua.execute(MODULE.read_text(encoding='utf-8'))
        self.g = self.lua.globals()

    def tick(self, ms=600):
        self.g.clock = self.g.clock + ms
        self.g.INFAI_ACT_Tick()

    def acts(self):
        from infinity_ai.actions.gateway import parse_receipt
        return [r for r in (parse_receipt(self.g.printed[i])
                            for i in range(1, len(self.g.printed) + 1)) if r is not None]

    def lst(self, name):
        t = self.g[name]
        return [t[i] for i in range(1, len(t) + 1)]

    def test_spawn_at_the_door_then_walk_to_the_counter(self):
        self.g.files['INFAIACT'] = render_request(spawn_request(
            'IADORAN', 'AR0406', x=580, y=900, templates=TEMPLATES, action_id='abcdef0123',
            to_x=760, to_y=640))
        self.tick()
        self.assertEqual(self.lst('moved'), ['INFAI_DORAN:MoveToPoint([760.640])'])
        self.tick(3500)
        self.assertEqual(self.acts()[-1].status, 'DONE')

    def test_arrival_plan_walks_too(self):
        req = spawn_request('IADORAN', 'AR0406', x=580, y=900, templates=TEMPLATES,
                            action_id='abcdef0123', to_x=760, to_y=640)
        self.g.files['INFAIARR'] = render_arrival_plan([req])
        self.lua.execute('leader.m_pArea = area')                      # the party is in the area
        self.tick()                                                    # AR0406 loads
        self.tick()
        self.assertEqual(self.lst('moved'), ['INFAI_DORAN:MoveToPoint([760.640])'])

    def test_walk_only_on_a_spawn_with_a_point(self):
        bad = render_request(spawn_request('IADORAN', 'AR0406', x=580, y=900,
                                           templates=TEMPLATES, action_id='abcdef0123',
                                           to_x=760, to_y=640)).replace('x = 580', 'x = -1')
        self.g.files['INFAIACT'] = bad
        self.tick()
        self.assertEqual((self.acts()[-1].reason, self.lst('moved')), ('BAD_REQUEST', []))

    def test_reward_pays_and_confirms_by_the_gold(self):
        self.g.files['INFAIACT'] = render_request(reward_request(
            'AR0406', gold=500, xp=1000, action_id='abcdef0123'))
        self.tick()
        self.assertIn('GiveGoldForce(500)', self.lst('queued'))
        self.assertIn('AddexperienceParty(1000)', self.lst('queued'))
        self.tick(1100)
        self.assertEqual(self.acts()[-1], ActionReceipt('abcdef0123', 'DONE', 1))
        self.assertEqual(self.g.EngineGlobals.g_pBaldurChitin.m_pObjectGame.m_nPartyGold, 600)

    def test_reward_unverified_when_the_gold_does_not_rise(self):
        self.g.pay_ok = False
        self.g.files['INFAIACT'] = render_request(reward_request(
            'AR0406', gold=500, xp=0, action_id='abcdef0123'))
        self.tick()
        self.tick(1100)
        self.assertEqual(self.acts()[-1], ActionReceipt('abcdef0123', 'DONE', None, 'UNVERIFIED'))

    def test_reward_reads_the_gold_like_the_game_ui_and_the_xp_from_active_stats(self):
        # lab 2026-11-26: m_nPartyGold gave no number; the game's own UI asks game:GetPartyGold()
        self.lua.execute("""
EngineGlobals.g_pBaldurChitin.m_pObjectGame.m_nPartyGold = nil
leader.m_baseStats.m_xp = nil
game = { gold = 40 }
function game:GetPartyGold() return self.gold end
active = { m_nXP = { m_value = 300 } }      -- an EEex Primitive<> keeps the number in m_value
EEex_Sprite_GetActiveStats = function(sprite) return active end
local instantly = EEex_Action_ExecuteResponseStringOnAIBaseInstantly
EEex_Action_ExecuteResponseStringOnAIBaseInstantly = function(s, target)
  local gold = string.match(s, '^GiveGoldForce%((%d+)%)$')
  if gold then game.gold = game.gold + tonumber(gold) end
  return instantly(s, target)
end
""")
        self.g.files['INFAIACT'] = render_request(reward_request(
            'AR0406', gold=100, xp=50, action_id='abcdef0123'))
        self.tick()
        self.tick(1100)
        self.assertEqual(self.acts()[-1], ActionReceipt('abcdef0123', 'DONE', 1))
        printed = [self.g.printed[i] for i in range(1, len(self.g.printed) + 1)]
        self.assertIn('INFAI-DIAG reward gold=40 via=1 xp=300 via=1', printed)
        self.assertIn('INFAI-DIAG reward-after gold=140 xp=300', printed)

    def test_reward_values_are_bounded_in_the_module_too(self):
        text = render_request(reward_request('AR0406', gold=500, xp=0,
                                             action_id='abcdef0123')).replace('gold = 500',
                                                                              'gold = 99999')
        self.g.files['INFAIACT'] = text
        self.tick()
        self.assertEqual(self.acts()[-1].reason, 'BAD_REQUEST')
        self.assertNotIn('GiveGoldForce(99999)', self.lst('queued'))


if __name__ == '__main__':
    unittest.main()
