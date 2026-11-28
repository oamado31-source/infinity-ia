# SPDX-License-Identifier: Apache-2.0
"""ADR-0140: the game counts our creatures (read only); copies; a presence's defeat."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.actions.gateway import (  # noqa: E402
    COUNT, DESPAWN, SPAWN, ActionReceipt, count_request, creature_counts, owned_creatures,
    record_requested, record_result,
)
from infinity_ai.quests.narrative import (  # noqa: E402
    DEFEATED, advance, parse_quest, pending_journal, state_of,
)
from infinity_ai.quests.presence import (  # noqa: E402
    COUNT_RULES, DEFEAT, DEFEAT_WATCH, ENTER, LEAVE, VERIFY, WATCH_EVERY, decide, dispatch,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

BERNARD = 'npc:cre-bernard'
DOC = json.loads((ROOT / 'knowledge' / 'quests' / 'bernard-brooch.pt_BR.json').read_text())
TEMPLATES = {'IATESTE': 'INFAI_TESTE', 'IAGUARDA': 'INFAI_GUARDA'}
VISION = {'presence_id': 'visao', 'cre': 'IATESTE', 'name': 'INFAI_TESTE', 'area': 'AR0406'}
GUARDS = {'presence_id': 'guardas', 'cre': 'IAGUARDA', 'name': 'INFAI_GUARDA', 'area': 'AR0406',
          'copies': 2}
FELL = {'step_id': 'guardas-cairam', 'defeated': {'presence': 'guardas'},
        'journal': 'Os guardas caíram.'}


def quest(presence, extra_steps=()):
    doc = copy.deepcopy(DOC)
    doc['presence'] = presence
    doc['steps'] = doc['steps'] + list(extra_steps)
    return parse_quest(doc)


class Game:
    """Counts per name; SPAWN adds one, DESPAWN removes all, COUNT only reads."""

    def __init__(self):
        self.here, self.writes, self.reads = {}, [], []

    def send(self, req):
        if req.op == COUNT:
            self.reads.append(req.name)
            n = self.here.get(req.name, 0)
            return ActionReceipt(req.action_id, 'DONE', n, None, n)
        self.writes.append((req.op, req.name))
        before = self.here.get(req.name, 0)
        self.here[req.name] = before + req.count if req.op == SPAWN else 0
        return ActionReceipt(req.action_id, 'DONE', self.here[req.name], None, before,
                             40 + self.here[req.name], 40 + before)   # the area's total


class FormatTests(unittest.TestCase):
    def test_copies_and_defeat_steps_are_strict(self):
        q = quest([VISION, GUARDS], [FELL])
        self.assertEqual(q.presence[1].copies, 2)
        self.assertEqual((q.steps[-1].kind, q.steps[-1].presence_id), (DEFEATED, 'guardas'))
        self.assertIsNone(quest([VISION, {**GUARDS, 'copies': 0}]))
        self.assertIsNone(quest([VISION, {**GUARDS, 'copies': 9}]))
        self.assertIsNone(quest([VISION], [FELL]))                       # unknown presence
        self.assertIsNone(quest([GUARDS], [FELL, dict(FELL, step_id='de-novo')]))
        self.assertIsNone(quest([GUARDS], [dict(FELL, defeated={'presence': 'guardas',
                                                                'x': 1})]))


class CountTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.t = 100
        self.game = Game()

    def use(self, *presence, steps=()):
        q = quest(list(presence), steps)
        self.quests = {q.quest_id: q}
        self.qid = q.quest_id

    def say(self, text):
        self.t += 10
        return advance(self.store, ROOT_BRANCH, self.quests, speaker=BERNARD, text=text,
                       area='AR0406', game_time=self.t)

    def enter_area(self):
        """What the recorder writes on entering an area or loading a save."""
        self.t += 1
        with self.store.transaction():
            self.store.append_event(branch_id=ROOT_BRANCH, host_epoch=0, event_type='AreaEntered',
                                    category='CAMPAIGN_OBSERVATION', game_time=self.t,
                                    payload={'area': 'AR0406'}, evidence='LAB_OBSERVED',
                                    idempotency_key=f'area|{self.t}')

    def step(self):
        self.t += 1
        decision, _ = decide(self.store, ROOT_BRANCH, self.quests, area='AR0406',
                             game_time=self.t)
        if decision is None:
            return None, None
        return decision.rule, dispatch(self.store, ROOT_BRANCH, decision, transport=self.game,
                                       templates=TEMPLATES, game_time=self.t)

    def rules(self, limit=8):
        out = []
        for _ in range(limit):
            rule, _ = self.step()
            if rule is None:
                break
            out.append(rule)
        return out

    def test_the_gateway_counts_and_the_count_is_the_branch_word(self):
        req = count_request('INFAI_TESTE', 'AR0406')
        self.assertEqual((req.op, req.cre), (COUNT, ''))
        record_requested(self.store, ROOT_BRANCH, req, game_time=1)
        self.assertEqual(record_result(self.store, ROOT_BRANCH, req,
                                       ActionReceipt(req.action_id, 'DONE', 2, None, 2),
                                       game_time=1), 'HOST_CONFIRMED')
        self.assertEqual(creature_counts(self.store, ROOT_BRANCH), {'INFAI_TESTE': ('AR0406', 2)})
        zero = count_request('INFAI_TESTE', 'AR0406')
        record_requested(self.store, ROOT_BRANCH, zero, game_time=2)
        record_result(self.store, ROOT_BRANCH, zero,
                      ActionReceipt(zero.action_id, 'DONE', 0, None, 0), game_time=2)
        self.assertEqual(owned_creatures(self.store, ROOT_BRANCH), {})
        for bad in ('Bernard', 'INFAI_X;'):
            with self.assertRaises(Exception):
                count_request(bad, 'AR0406')

    def test_counts_before_trusting_the_branch(self):
        self.use(VISION)
        self.say('Tem trabalho?')
        self.say('Aceito.')
        self.assertEqual(self.rules(), [VERIFY, ENTER])                 # count, then create
        self.assertEqual(self.rules(), [])                              # the word is fresh
        self.game.here['INFAI_TESTE'] = 0                               # another line's save
        self.enter_area()
        self.assertEqual(self.rules(), [VERIFY, ENTER])                 # zero: created again
        self.game.here['INFAI_TESTE'] = 1
        self.enter_area()
        self.assertEqual(self.rules(), [VERIFY])                        # one there: kept
        self.assertEqual(self.game.writes, [(SPAWN, 'INFAI_TESTE')] * 2)

    def test_a_save_that_already_has_her_is_not_given_a_second(self):
        self.use(VISION)
        self.game.here['INFAI_TESTE'] = 1                               # the save holds her
        self.say('Tem trabalho?')
        self.say('Aceito.')
        self.assertEqual(self.rules(), [VERIFY])
        self.assertEqual(self.game.writes, [])

    def test_copies_come_together_and_all_leave_together(self):
        self.use(GUARDS)
        self.say('Tem trabalho?')
        self.say('Aceito.')
        self.assertEqual(self.rules(), [VERIFY, ENTER])                 # ADR-0143: one request
        self.assertEqual(self.game.here['INFAI_GUARDA'], 2)
        self.game.here['INFAI_GUARDA'] = 1                               # one lost, no defeat step
        self.enter_area()
        self.assertEqual(self.rules(), [VERIFY, ENTER])                 # made whole again
        self.say('Unger falou de um novato nas Docas.')                  # not resolved: Unger
        state = state_of(self.store, ROOT_BRANCH, self.qid)
        self.assertFalse(state.resolved)

    def test_a_defeat_is_the_fall_to_zero_and_is_never_undone(self):
        self.use(GUARDS, steps=[FELL])
        self.say('Tem trabalho?')
        self.say('Aceito.')
        self.assertEqual(self.rules(), [VERIFY, ENTER])
        self.assertEqual(self.rules(), [])                              # watch not due yet
        self.game.here['INFAI_GUARDA'] = 1                               # one fell
        self.t += WATCH_EVERY
        self.assertEqual(self.rules(), [DEFEAT_WATCH])                  # never recreated
        self.game.here['INFAI_GUARDA'] = 0                               # the other fell
        self.t += WATCH_EVERY
        self.assertEqual(self.rules(), [DEFEAT_WATCH, DEFEAT])
        self.assertIn('guardas-cairam', state_of(self.store, ROOT_BRANCH, self.qid).steps_done)
        self.assertEqual(pending_journal(self.store, ROOT_BRANCH, self.quests),
                         ((self.qid, 'guardas-cairam', 'Os guardas caíram.'),))
        self.enter_area()
        self.t += WATCH_EVERY
        self.assertEqual(self.rules(), [])                              # gone for good
        self.assertEqual(self.game.writes, [(SPAWN, 'INFAI_GUARDA')])   # one request, two

    def test_the_quest_removing_them_is_not_a_defeat(self):
        self.use({**GUARDS, 'until': 'ask-unger'}, steps=[FELL])
        self.say('Tem trabalho?')
        self.say('Aceito.')
        self.rules()
        advance(self.store, ROOT_BRANCH, self.quests, speaker='npc:scdur',
                text='Quem furtou o broche?', area='AR0406', game_time=self.t + 1)
        self.assertEqual(self.rules(), [LEAVE])
        self.assertEqual(self.game.writes[-1], (DESPAWN, 'INFAI_GUARDA'))
        self.t += WATCH_EVERY
        self.assertEqual(self.rules(), [])
        self.assertNotIn('guardas-cairam', state_of(self.store, ROOT_BRANCH, self.qid).steps_done)

    def test_counts_are_rules_of_their_own(self):
        self.assertEqual(set(COUNT_RULES), {VERIFY, DEFEAT_WATCH})


if __name__ == '__main__':
    unittest.main()
