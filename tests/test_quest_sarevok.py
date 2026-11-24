# SPDX-License-Identifier: Apache-2.0
"""The curated quest "O diário perdido de Sarevok" end to end, with a simulated game, and ADR-0144:
the giver's call over its head, a person with several conversation steps, the way out by the door."""
import copy
import dataclasses
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.actions.gateway import (  # noqa: E402
    CALL, COUNT, DESPAWN, ESCAPE, SET_HOSTILE, SPAWN, ActionReceipt, confirmed,
)
from infinity_ai.quests.narrative import advance, arrive, parse_quest, state_of  # noqa: E402
from infinity_ai.quests.presence import (  # noqa: E402
    arrival_plan, call_due, decide, dispatch, dispatch_call, record_arrival,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

DOC = json.loads((ROOT / 'knowledge' / 'quests' / 'sarevok-diary.pt_BR.json').read_text())
TEMPLATES = {'IATAMOKO': 'INFAI_TAMOKO', 'IAGREGOR': 'INFAI_GREGOR',
             'IACARCER': 'INFAI_CARCEREIRO', 'IAKALESS': 'INFAI_KALESSIA',
             'IAAGENTE': 'INFAI_AGENTE'}
HOUR = 4500
NIGHT, DAY = 22 * HOUR, 12 * HOUR


class Game:
    """Our creatures per name, the area's other creatures, and the giver standing in the tavern."""

    def __init__(self):
        self.here, self.hostile, self.writes, self.calls, self.other = {}, {}, [], [], 40

    def total(self):
        return self.other + sum(self.here.values())

    def send(self, req):
        n = self.here.get(req.name, 0)
        if req.op == CALL:
            self.calls.append((req.name, req.area, req.strref))
            return ActionReceipt(req.action_id, 'DONE', 1, None, 1)
        if req.op == COUNT:
            return ActionReceipt(req.action_id, 'DONE', n, None, n, self.total())
        self.writes.append((req.op, req.name, req.count))
        if req.op == SET_HOSTILE:
            self.hostile[req.name] = n
            return ActionReceipt(req.action_id, 'DONE', n, None, n, self.total())
        before = self.total()
        self.here[req.name] = n + req.count if req.op == SPAWN else 0
        return ActionReceipt(req.action_id, 'DONE', self.here[req.name], None, n, self.total(),
                             before)


class QuestFileTests(unittest.TestCase):
    def test_the_quest_parses_with_its_call_and_two_steps_of_tamoko(self):
        quest = parse_quest(copy.deepcopy(DOC))
        self.assertIsNotNone(quest)
        self.assertEqual((quest.call.script_name, quest.call.area, quest.call.strref),
                         ('DRUNK1', 'AR0406', 102877))
        tamoko = [s.step_id for s in quest.steps if s.npc_id == 'npc:infai_tamoko']
        self.assertEqual(tamoko, ['visao', 'descanso'])
        self.assertEqual({p.presence_id: p.leave for p in quest.presence}['gregor'], ESCAPE)

    def test_a_person_with_two_open_steps_at_once_is_refused(self):
        doc = copy.deepcopy(DOC)
        doc['steps'][-1]['after'] = []                     # descanso no longer after visao
        self.assertIsNone(parse_quest(doc))
        for bad in ({'script_name': 'INFAI_X', 'area': 'AR0406', 'strref': 1, 'every': 1500},
                    {'script_name': 'DRUNK1', 'area': 'AR0406', 'strref': 1, 'every': 10},
                    {'script_name': 'DRUNK1', 'area': 'AR0406', 'strref': 1}):
            self.assertIsNone(parse_quest(dict(copy.deepcopy(DOC), call=bad)), bad)
        doc = copy.deepcopy(DOC)
        doc['presence'][1]['leave'] = 'TELEPORT'
        self.assertIsNone(parse_quest(doc))


class FlowTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        quest = parse_quest(copy.deepcopy(DOC))
        self.quests = {quest.quest_id: quest}
        self.qid = quest.quest_id
        self.game = Game()
        self.day = 2 * 108000

    def at(self, hour_ticks):
        return self.day + hour_ticks

    def enter(self, area, t):
        with self.store.transaction():
            self.store.append_event(branch_id=ROOT_BRANCH, host_epoch=0, event_type='AreaEntered',
                                    category='CAMPAIGN_OBSERVATION', game_time=t,
                                    payload={'area': area}, evidence='LAB_OBSERVED',
                                    idempotency_key=f'area|{area}|{t}')
        arrive(self.store, ROOT_BRANCH, self.quests, area=area, game_time=t,
               night=NIGHT <= t % 108000 or t % 108000 < 6 * HOUR)

    def say(self, who, text, area, t):
        return advance(self.store, ROOT_BRANCH, self.quests, speaker=who, text=text, area=area,
                       game_time=t)

    def rules(self, area, t, limit=8):
        out = []
        for i in range(limit):
            decision, _ = decide(self.store, ROOT_BRANCH, self.quests, area=area,
                                 game_time=t + i)
            if decision is None:
                break
            dispatch(self.store, ROOT_BRANCH, decision, transport=self.game,
                     templates=TEMPLATES, game_time=t + i)
            out.append((decision.rule, decision.presence.presence_id))
        return out

    def done(self):
        return state_of(self.store, ROOT_BRANCH, self.qid).steps_done

    def test_the_whole_quest(self):
        t = self.at(DAY)
        # Garoll calls for help in the tavern, on entering and every 1500 ticks, until accepted
        self.enter('AR0406', t)
        self.assertIsNone(call_due(self.store, ROOT_BRANCH, self.quests, area='AR0300',
                                   game_time=t))
        quest = call_due(self.store, ROOT_BRANCH, self.quests, area='AR0406', game_time=t)
        self.assertEqual(dispatch_call(self.store, ROOT_BRANCH, quest, transport=self.game,
                                       game_time=t), 'HOST_CONFIRMED')
        self.assertIsNone(call_due(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                                   game_time=t + 10))
        self.assertIsNotNone(call_due(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                                      game_time=t + 1500))
        self.say('npc:drunk1', 'Ouvi falar de um fantasma no cemitério.', 'AR0406', t + 20)
        self.say('npc:drunk1', 'Pode deixar, vamos ver.', 'AR0406', t + 30)
        self.assertIsNone(call_due(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                                   game_time=t + 3000))                  # accepted: quiet
        self.assertEqual(self.game.calls, [('DRUNK1', 'AR0406', 102877)])
        self.assertEqual(self.game.writes, [])                          # a call writes nothing
        # the cemetery by day: no vision; at night she comes
        self.enter('AR0800', self.at(DAY + HOUR))
        self.assertEqual(self.rules('AR0800', self.at(DAY + HOUR)), [])
        t = self.at(NIGHT)
        self.enter('AR0800', t)
        self.assertEqual(self.rules('AR0800', t), [('VERIFY', 'tamoko'), ('ENTER', 'tamoko')])
        turn = self.say('npc:infai_tamoko', 'Quem te matou?', 'AR0800', t + 10)
        self.assertIn('visao', self.done())
        self.assertIn('Gregor', ' '.join(turn.facts))
        self.assertEqual(turn.fresh, turn.facts)                        # CR-2026-033: new now
        turn = self.say('npc:infai_tamoko', 'Tem mais alguma coisa?', 'AR0800', t + 20)
        self.assertIn('Gregor', ' '.join(turn.facts))                   # she remembers it
        self.assertEqual(turn.fresh, ())                                # told, no longer (agora)
        # the captivity: Gregor and two jailers, the jailers together; they fall
        t += 2 * HOUR
        self.enter('AR0409', t)
        self.assertIn('cativeiro', self.done())
        rules = self.rules('AR0409', t)
        self.assertIn(('ENTER', 'carcereiros'), rules)
        self.assertIn((SPAWN, 'INFAI_CARCEREIRO', 2), self.game.writes)
        self.assertIn((SPAWN, 'INFAI_GREGOR', 1), self.game.writes)
        self.game.here['INFAI_CARCEREIRO'] = 0
        self.rules('AR0409', t + 200)
        self.assertIn('carcereiros-cairam', self.done())
        # Gregor tells, then walks out by the door (ESCAPE, never DESPAWN)
        turn = self.say('npc:infai_gregor', 'Você está livre. Onde fica o esconderijo?',
                        'AR0409', t + 300)
        self.assertIn('Docas', ' '.join(turn.facts))
        self.assertEqual(self.rules('AR0409', t + 310), [('LEAVE', 'gregor')])
        self.assertEqual(self.game.writes[-1], (ESCAPE, 'INFAI_GREGOR', 1))
        self.assertEqual(self.game.here['INFAI_GREGOR'], 0)
        self.assertEqual(self.rules('AR0409', t + 400), [])             # never recreated
        # the hideout: Kalessia and three agents, neutral; the demand turns them; they fall
        t += 2 * HOUR
        self.enter('IA0001', t)
        self.rules('IA0001', t)
        self.assertEqual((self.game.here['INFAI_KALESSIA'], self.game.here['INFAI_AGENTE']),
                         (1, 3))
        self.say('npc:infai_kalessia', 'Entregue o diário de Sarevok.', 'IA0001', t + 100)
        self.assertEqual(self.rules('IA0001', t + 110, limit=2),
                         [('HOSTILE', 'kalessia'), ('HOSTILE', 'agentes')])
        self.game.here.update(INFAI_KALESSIA=0, INFAI_AGENTE=0)
        self.rules('IA0001', t + 400)
        self.assertTrue({'kalessia-caiu', 'agentes-cairam'} <= self.done())
        # back at the cemetery at night: she rests and goes
        t = self.at(NIGHT) + 108000
        self.enter('AR0800', t)
        self.rules('AR0800', t)
        self.say('npc:infai_tamoko', 'Trouxemos o diário. Prometemos guardá-lo.', 'AR0800',
                 t + 10)
        self.assertIn('descanso', self.done())
        self.assertEqual(self.rules('AR0800', t + 20), [('LEAVE', 'tamoko')])
        self.assertEqual(self.game.writes[-1], (DESPAWN, 'INFAI_TAMOKO', 1))
        # Garoll: the quest is done and he is grateful
        turn = self.say('npc:drunk1', 'O fantasma descansou.', 'AR0406', t + HOUR)
        self.assertEqual(turn.milestones, ('quest:sarevok-diary:RESOLVED',))
        self.assertTrue(state_of(self.store, ROOT_BRANCH, self.qid).resolved)


    def test_the_places_are_prepared_from_the_acceptance(self):
        """ADR-0145 (maintainer, 2026-11-24): from the moment the quest is accepted, the plan holds
        Gregor and both jailers (AR0409) and Kalessia with three agents (IA0001), as the people of
        a quest of the game; what the module made on entering is recorded as the director's ENTER."""
        t = self.at(DAY)
        self.say('npc:drunk1', 'Que fantasma?', 'AR0406', t)
        self.assertEqual(arrival_plan(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                                      game_time=t + 5, templates=TEMPLATES), ())   # offered only
        self.say('npc:drunk1', 'Vamos ajudar.', 'AR0406', t + 10)
        plan = arrival_plan(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                            game_time=t + 20, templates=TEMPLATES)
        self.assertEqual(sorted((r.area, r.name, r.count) for _, r in plan),
                         [('AR0409', 'INFAI_CARCEREIRO', 2), ('AR0409', 'INFAI_GREGOR', 1),
                          ('IA0001', 'INFAI_AGENTE', 3), ('IA0001', 'INFAI_KALESSIA', 1)])
        self.enter('AR0409', t + 60)                    # the module made them on loading
        self.assertIn('cativeiro', self.done())         # no longer waits for the vision
        # both made in the same instant: each answer sees the area rise by all three (lab)
        made = {'INFAI_GREGOR': (0, 1), 'INFAI_CARCEREIRO': (0, 2)}
        for decision, req in plan:
            if req.area != 'AR0409':
                continue
            before, after = made[req.name]
            receipt = ActionReceipt(req.action_id, 'DONE', after, None, before, 8, 5)
            if req.name == 'INFAI_GREGOR':      # alone, +3 for one creature does not add up
                self.assertFalse(confirmed(dataclasses.replace(req, count=1), receipt))
            self.assertEqual(record_arrival(self.store, ROOT_BRANCH, decision, req, receipt,
                                            game_time=t + 61, arrival_made=3), 'HOST_CONFIRMED')
            self.game.here[req.name] = after
        rules = [r for r, _ in self.rules('AR0409', t + 70, limit=3)]
        self.assertNotIn('ENTER', rules)                               # nothing left to create
        self.assertNotIn('VERIFY', rules)                              # the arrival already told
        left = arrival_plan(self.store, ROOT_BRANCH, self.quests, area='AR0409',
                            game_time=t + 80, templates=TEMPLATES)
        self.assertEqual(sorted(r.area for _, r in left), ['IA0001', 'IA0001'])  # the hideout

if __name__ == '__main__':
    unittest.main()
