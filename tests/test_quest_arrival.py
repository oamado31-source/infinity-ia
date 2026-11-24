# SPDX-License-Identifier: Apache-2.0
"""ADR-0139: the hour of the day, arrival steps, step order and presence only at night."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.actions.gateway import COUNT, SPAWN, ActionReceipt, owned_creatures  # noqa: E402
from infinity_ai.quests.clock import UNITS_PER_HOUR, hour_of, is_night  # noqa: E402
from infinity_ai.quests.narrative import (  # noqa: E402
    ARRIVE, STEP_DONE, TALK, advance, arrive, mark_journal_shown, parse_quest, pending_journal,
    state_of,
)
from infinity_ai.quests.presence import COUNT_RULES, ENTER, LEAVE, decide, dispatch  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

BERNARD, YARIN = 'npc:cre-bernard', 'npc:yarin'
DOC = json.loads((ROOT / 'knowledge' / 'quests' / 'bernard-brooch.pt_BR.json').read_text())
HOUR = UNITS_PER_HOUR
DAY = 24 * HOUR
NOON, MIDNIGHT = 12 * HOUR, DAY * 3           # day 3, 00:00
TEMPLATES = {'IATESTE': 'INFAI_TESTE'}


def quest(steps=None, presence=None, **change):
    doc = copy.deepcopy(DOC)
    doc.pop('area')                            # ADR-0139: a quest across several areas
    if steps is not None:
        doc['steps'] = steps
    if presence is not None:
        doc['presence'] = presence
    doc.update(change)
    return parse_quest(doc)


YARIN_STEP = dict(DOC['steps'][0], area='AR0406')
STREET = {'step_id': 'ir-a-rua', 'arrive': {'area': 'AR0400'}, 'journal': 'Você chegou às Favelas.'}
NIGHT_STREET = {'step_id': 'rua-a-noite', 'arrive': {'area': 'AR0400', 'night': True},
                'journal': 'De noite, nas Favelas.'}


class ClockTests(unittest.TestCase):
    def test_hours_and_night(self):
        self.assertEqual([hour_of(t) for t in (0, HOUR - 1, HOUR, NOON, DAY - 1, DAY)],
                         [0, 0, 1, 12, 23, 0])
        self.assertEqual(hour_of(497541), 14)          # lab, 2026-11-22: the game said 14h
        self.assertEqual([is_night(h * HOUR) for h in (20, 21, 23, 0, 5, 6, 12)],
                         [False, True, True, True, True, False, False])
        self.assertEqual((hour_of(None), is_night(None), hour_of(-1), hour_of(True)),
                         (None, False, None, None))


class FormatTests(unittest.TestCase):
    def test_arrival_steps_and_order_are_strict(self):
        q = quest([YARIN_STEP, dict(STREET, after=['ask-yarin']), NIGHT_STREET])
        yarin, street, night = q.steps
        self.assertEqual((yarin.kind, yarin.area), (TALK, 'AR0406'))
        self.assertEqual((street.kind, street.area, street.night, street.after, street.npc_id),
                         (ARRIVE, 'AR0400', False, ('ask-yarin',), None))
        self.assertTrue(night.night)
        for bad in ([dict(STREET, after=['depois'])],                    # only earlier steps
                    [STREET, dict(NIGHT_STREET, after=['rua-a-noite'])],  # not itself
                    [dict(STREET, arrive={'area': 'ar 0400'})],
                    [dict(STREET, arrive={'area': 'AR0400', 'night': 'sim'})],
                    [dict(STREET, arrive={'area': 'AR0400', 'hora': 3})],
                    [dict(STREET, npc_id=YARIN)],                          # arrival has no person
                    [dict(YARIN_STEP, area='x y')],
                    [YARIN_STEP, dict(YARIN_STEP, step_id='outra')]):      # one step per person
            self.assertIsNone(quest(bad), bad)
        self.assertEqual(quest(presence=[{'presence_id': 'v', 'cre': 'IATESTE',
                                          'name': 'INFAI_TESTE', 'area': 'AR0406',
                                          'when': 'NIGHT'}]).presence[0].when, 'NIGHT')
        self.assertIsNone(quest(presence=[{'presence_id': 'v', 'cre': 'IATESTE',
                                           'name': 'INFAI_TESTE', 'area': 'AR0406',
                                           'when': 'DAWN'}]))


class FlowTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.t = NOON

    def use(self, q):
        self.quests = {q.quest_id: q}
        self.qid = q.quest_id

    def say(self, who, text, area='AR0406'):
        self.t += 10
        return advance(self.store, ROOT_BRANCH, self.quests, speaker=who, text=text, area=area,
                       game_time=self.t)

    def reach(self, area, at=None):
        self.t = at if at is not None else self.t + 10
        return arrive(self.store, ROOT_BRANCH, self.quests, area=area, game_time=self.t,
                      night=is_night(self.t))

    def accept(self):
        self.say(BERNARD, 'Tem trabalho?')
        self.say(BERNARD, 'Aceito.')

    def test_arriving_does_the_step_once_and_only_after_accepting(self):
        self.use(quest([STREET]))
        self.assertEqual(self.reach('AR0400'), ())                      # not accepted yet
        self.accept()
        self.assertEqual(self.reach('AR0406'), ())                      # another area
        self.assertEqual(self.reach('AR0400'), (f'{self.qid}:ir-a-rua',))
        self.assertEqual(self.reach('AR0400'), ())                      # leave and come back
        self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, STEP_DONE)), 1)
        pending = pending_journal(self.store, ROOT_BRANCH, self.quests)
        self.assertEqual(pending, ((self.qid, 'ir-a-rua', 'Você chegou às Favelas.'),))
        mark_journal_shown(self.store, ROOT_BRANCH, pending, game_time=self.t)
        self.assertEqual(pending_journal(self.store, ROOT_BRANCH, self.quests), ())
        turn_in = self.say(BERNARD, 'Yarin falou de um novato nas Docas.')
        self.assertTrue(state_of(self.store, ROOT_BRANCH, self.qid).resolved, turn_in)
        self.assertEqual(self.reach('AR0400'), ())                      # resolved: nothing

    def test_night_arrival_and_order(self):
        self.use(quest([YARIN_STEP, dict(NIGHT_STREET, after=['ask-yarin'])]))
        self.accept()
        self.assertEqual(self.reach('AR0400', at=MIDNIGHT), ())         # Yarin first
        self.assertEqual(self.say(YARIN, 'Quem furtou o broche?', area='AR0300').changes, ())
        self.assertNotEqual(self.say(YARIN, 'Quem furtou o broche?').changes, ())
        self.assertEqual(self.reach('AR0400', at=MIDNIGHT + DAY - 6 * HOUR), ())   # 18:00
        self.assertEqual(self.reach('AR0400', at=MIDNIGHT + DAY + HOUR),           # 01:00
                         (f'{self.qid}:rua-a-noite',))

    def test_a_talk_step_waits_for_its_order(self):
        street_first = {'step_id': 'ir-a-rua', 'arrive': {'area': 'AR0400'}, 'journal': 'Rua.'}
        self.use(quest([street_first, dict(YARIN_STEP, after=['ir-a-rua'])]))
        self.accept()
        self.assertEqual(self.say(YARIN, 'Quem furtou o broche?').changes, ())
        self.reach('AR0400')
        self.assertNotEqual(self.say(YARIN, 'Quem furtou o broche?').changes, ())


class NightPresenceTests(unittest.TestCase):
    def test_a_vision_of_the_night_comes_at_night_and_fades_at_dawn(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CampaignStore.open(Path(tmp) / 'c.sqlite3', 'lab')
            self.addCleanup(store.close)
            q = quest(presence=[{'presence_id': 'visao', 'cre': 'IATESTE',
                                 'name': 'INFAI_TESTE', 'area': 'AR0406', 'when': 'NIGHT'}])
            quests = {q.quest_id: q}
            for i, text in enumerate(('Tem trabalho?', 'Aceito.'), 1):
                advance(store, ROOT_BRANCH, quests, speaker=BERNARD, text=text, area='AR0406',
                        game_time=NOON + i)

            class Game:
                here = 0

                def send(self, req):
                    if req.op == COUNT:
                        return ActionReceipt(req.action_id, 'DONE', self.here, None, self.here)
                    before = self.here
                    self.here = before + req.count if req.op == SPAWN else 0
                    return ActionReceipt(req.action_id, 'DONE', self.here, None, before,
                                         40 + self.here, 40 + before)
            game = Game()

            def tick(t):
                for _ in range(3):
                    decision, _ = decide(store, ROOT_BRANCH, quests, area='AR0406', game_time=t)
                    if decision:
                        dispatch(store, ROOT_BRANCH, decision, transport=game,
                                 templates=TEMPLATES, game_time=t)
                    if decision is None or decision.rule not in COUNT_RULES:
                        return decision.rule if decision else None
                return decision.rule
            self.assertEqual(tick(NOON + 10), None)                        # day: not yet
            self.assertEqual(tick(MIDNIGHT - 2 * HOUR), ENTER)             # 22:00
            self.assertEqual(tick(MIDNIGHT + HOUR), None)                  # still night
            self.assertEqual(owned_creatures(store, ROOT_BRANCH), {'INFAI_TESTE': 'AR0406'})
            self.assertEqual(tick(MIDNIGHT + 7 * HOUR), LEAVE)             # 07:00, dawn
            self.assertEqual(tick(MIDNIGHT + 8 * HOUR), None)
            self.assertEqual(tick(MIDNIGHT + DAY - HOUR), ENTER)          # the next night


if __name__ == '__main__':
    unittest.main()
