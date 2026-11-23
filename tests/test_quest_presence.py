# SPDX-License-Identifier: Apache-2.0
"""ADR-0138: who must be on the map is decided by the quest, through the action gateway."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.actions.gateway import (  # noqa: E402
    CONFIRMED, COUNT, DESPAWN, FAILED, REQUESTED, SPAWN, ActionReceipt, despawn_request,
    owned_creatures, record_requested, record_result, spawn_request,
)
from infinity_ai.quests.narrative import advance, parse_quest  # noqa: E402
from infinity_ai.quests.presence import (  # noqa: E402
    COUNT_RULES, ENTER, LEAVE, RESUMED, SUSPENDED, decide, dispatch, record_resumed, wanted,
)
from infinity_ai.quests.narrative import QuestState  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

BERNARD, YARIN = 'npc:cre-bernard', 'npc:yarin'
DOC = json.loads((ROOT / 'knowledge' / 'quests' / 'bernard-brooch.pt_BR.json').read_text())
VISION = {'presence_id': 'visao', 'cre': 'IATESTE', 'name': 'INFAI_TESTE', 'area': 'AR0406'}
TEMPLATES = {'IATESTE': 'INFAI_TESTE'}


def quest_with(*presence, **change):
    doc = copy.deepcopy(DOC)
    doc['presence'] = list(presence)
    doc.update(change)
    return parse_quest(doc)


class FakeGame:
    """The EEex module's answers: counts our creatures with the name in the area. `sent` keeps
    the writes (SPAWN, DESPAWN); `counts` the reads (ADR-0140), answered by `count_answer`."""

    def __init__(self, answer='DONE', count_answer='DONE'):
        self.answer, self.count_answer, self.here, self.sent, self.counts = \
            answer, count_answer, 0, [], []

    def send(self, req):
        if req.op == COUNT:
            self.counts.append(req)
            if self.count_answer is None:
                return None
            return ActionReceipt(req.action_id, 'DONE', self.here, None, self.here)
        self.sent.append(req)
        if self.answer is None:
            return None                                   # no word from the game
        if self.answer == 'REFUSED':
            return ActionReceipt(req.action_id, 'REFUSED', None, 'NO_LEADER')
        if self.answer == 'WRONG_AREA':
            return ActionReceipt(req.action_id, 'REFUSED', None, 'WRONG_AREA')
        before = self.here
        self.here = before + 1 if req.op == SPAWN else 0
        return ActionReceipt(req.action_id, 'DONE', self.here, None, before)


class FormatTests(unittest.TestCase):
    def test_presence_is_strict(self):
        quest = quest_with(VISION, {**VISION, 'presence_id': 'outra', 'name': 'INFAI_OUTRA',
                                    'from': 'ask-yarin', 'x': 500, 'y': 600, 'facing': 4})
        first, second = quest.presence
        self.assertEqual((first.start, first.end, first.x), ('ACCEPTED', 'RESOLVED', -1))
        self.assertEqual((second.start, second.x, second.y, second.facing),
                         ('ask-yarin', 500, 600, 4))
        self.assertEqual(parse_quest(copy.deepcopy(DOC)).presence, ())     # optional
        for bad in ({**VISION, 'cre': 'MTOWN6'},              # not one of our files
                    {**VISION, 'name': 'Tamoko'},              # not one of our names
                    {**VISION, 'area': 'ar 0406'},
                    {**VISION, 'from': 'passo-que-nao-existe'},
                    {**VISION, 'until': 'ACCEPTED'},
                    {**VISION, 'from': 'ask-yarin', 'until': 'ask-yarin'},
                    {**VISION, 'x': 100},                      # half a point
                    {**VISION, 'facing': 16}):
            self.assertIsNone(quest_with(bad), bad)
        self.assertIsNone(quest_with(VISION, dict(VISION)))     # the same presence twice

    def test_between_its_two_points(self):
        vision = quest_with(VISION).presence[0]
        after_step = quest_with({**VISION, 'from': 'ask-yarin'}).presence[0]
        until_step = quest_with({**VISION, 'until': 'ask-yarin'}).presence[0]
        accepted = QuestState(True, True)
        stepped = QuestState(True, True, frozenset({'ask-yarin'}))
        resolved = QuestState(True, True, frozenset({'ask-yarin'}), True)
        self.assertEqual([wanted(s, vision) for s in (QuestState(True), accepted, resolved)],
                         [False, True, False])
        self.assertEqual([wanted(s, after_step) for s in (accepted, stepped)], [False, True])
        self.assertEqual([wanted(s, until_step) for s in (accepted, stepped)], [True, False])


class DirectorTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.quests = {'bernard-brooch': quest_with(VISION)}
        self.t = 0

    def say(self, who, text, branch=ROOT_BRANCH):
        self.t += 10
        return advance(self.store, branch, self.quests, speaker=who, text=text, area='AR0406',
                       game_time=self.t)

    def tick(self, game, area='AR0406', branch=ROOT_BRANCH):
        """One reading of the game: decide and, if needed, ask; the counts the director asks
        first (ADR-0140) are followed by what it decides next, in the same reading."""
        for _ in range(4):
            self.t += 1
            decision, held = decide(self.store, branch, self.quests, area=area, game_time=self.t)
            state = dispatch(self.store, branch, decision, transport=game, templates=TEMPLATES,
                             game_time=self.t) if decision else None
            if decision is None or decision.rule not in COUNT_RULES or state != 'HOST_CONFIRMED':
                return decision, state, held
        return decision, state, held

    def test_accept_creates_resolve_removes_and_nothing_repeats(self):
        game = FakeGame()
        self.assertEqual(self.tick(game)[0], None)                 # nobody asked yet
        self.say(BERNARD, 'Tem trabalho?')
        self.assertEqual(self.tick(game)[0], None)                 # offered, not accepted
        self.say(BERNARD, 'Aceito.')
        self.assertEqual(self.tick(game, area='AR0300')[0], None)  # the party is elsewhere
        decision, state, _ = self.tick(game)
        self.assertEqual((decision.rule, state), (ENTER, 'HOST_CONFIRMED'))
        self.assertEqual(owned_creatures(self.store, ROOT_BRANCH), {'INFAI_TESTE': 'AR0406'})
        for area in ('AR0406', 'AR0300', 'AR0406'):                # leave and come back
            self.assertEqual(self.tick(game, area=area)[0], None)
        self.say(YARIN, 'Quem furtou o broche de Bernard?')
        self.assertEqual(self.tick(game)[0], None)                 # still wanted
        self.say(BERNARD, 'Yarin falou de um novato nas Docas.')
        decision, state, _ = self.tick(game)
        self.assertEqual((decision.rule, state), (LEAVE, 'HOST_CONFIRMED'))
        self.assertEqual(owned_creatures(self.store, ROOT_BRANCH), {})
        self.assertEqual(self.tick(game)[0], None)
        self.assertEqual([r.op for r in game.sent], [SPAWN, DESPAWN])
        for t in (REQUESTED, CONFIRMED):                           # the cause, never player text
            for e in self.store.visible_events(ROOT_BRANCH, t):
                self.assertEqual((e.payload['cause']['quest_id'],
                                  e.payload['cause']['presence_id']), ('bernard-brooch', 'visao'))
                self.assertNotIn('Docas', json.dumps(e.payload, ensure_ascii=False))

    def test_an_older_save_follows_its_own_branch(self):
        game = FakeGame()
        self.say(BERNARD, 'Tem trabalho?')                          # t=10
        self.say(BERNARD, 'Aceito.')                                # t=20
        self.tick(game)                                             # created at t=21
        before_accept = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=15,
                                               fork_epoch=1)
        self.assertEqual(owned_creatures(self.store, before_accept), {})
        self.assertEqual(self.tick(game, branch=before_accept)[0], None)   # not accepted there
        after = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=25,
                                       fork_epoch=2)
        self.assertEqual(self.tick(game, branch=after)[0], None)    # the save has her: no repeat
        self.assertEqual(len(game.sent), 1)

    def test_what_the_game_does_not_confirm_suspends_until_resumed(self):
        for answer, expected in ((None, 'UNCERTAIN'), ('REFUSED', 'DENIED')):
            with self.subTest(answer=answer):
                self.setUp()
                game = FakeGame(answer)
                self.say(BERNARD, 'Tem trabalho?')
                self.say(BERNARD, 'Aceito.')
                self.assertEqual(self.tick(game)[1], expected)
                decision, _, held = self.tick(game)
                self.assertEqual((decision, held), (None, ('bernard-brooch/visao=SUSPENDED',)))
                self.assertEqual(len(game.sent), 1)                 # never resent blindly
                self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, SUSPENDED)), 1)
                record_resumed(self.store, ROOT_BRANCH, 'bernard-brooch', 'visao',
                               game_time=self.t, key='manual-1')
                game.answer = 'DONE'
                self.assertEqual(self.tick(game)[1], 'HOST_CONFIRMED')
                self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, RESUMED)), 1)

    def test_a_missing_file_suspends_before_the_game(self):
        self.quests = {'bernard-brooch': quest_with({**VISION, 'cre': 'IAFALTA'})}
        game = FakeGame()
        self.say(BERNARD, 'Tem trabalho?')
        self.say(BERNARD, 'Aceito.')
        self.assertEqual(self.tick(game)[1], 'REFUSED:UNKNOWN_TEMPLATE')
        self.assertEqual((game.sent, self.tick(game)[2]),
                         ([], ('bernard-brooch/visao=SUSPENDED',)))

    def test_a_request_without_result_blocks_and_wrong_area_does_not_suspend(self):
        game = FakeGame('WRONG_AREA')
        self.say(BERNARD, 'Tem trabalho?')
        self.say(BERNARD, 'Aceito.')
        self.assertEqual(self.tick(game)[1], 'DENIED')              # the party had just left
        self.assertEqual(self.store.visible_events(ROOT_BRANCH, SUSPENDED), [])
        self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, FAILED)), 1)
        game.answer = None
        req = spawn_request('IATESTE', 'AR0406', templates=TEMPLATES)   # service stopped mid-way
        record_requested(self.store, ROOT_BRANCH, req, game_time=self.t, cause={
            'policy': 'adr-0138-quest-presence-v1', 'quest_id': 'bernard-brooch',
            'presence_id': 'visao', 'rule': ENTER})
        self.assertEqual(self.tick(game)[2], ('bernard-brooch/visao=PENDING',))

    def test_a_save_of_another_timeline_is_corrected_by_the_game_count(self):
        game = FakeGame()
        self.say(BERNARD, 'Tem trabalho?')
        self.say(BERNARD, 'Aceito.')
        self.tick(game)                                             # created and confirmed
        game.here = 0                                               # the loaded save lacks her
        self.assertEqual(self.tick(game)[0], None)                  # the branch still believes
        req = despawn_request('INFAI_TESTE', 'AR0406', owned={'INFAI_TESTE'})   # maintainer
        record_requested(self.store, ROOT_BRANCH, req, game_time=self.t)
        state = record_result(self.store, ROOT_BRANCH, req,
                              ActionReceipt(req.action_id, 'REFUSED', 0, 'NOT_FOUND'),
                              game_time=self.t)
        self.assertEqual((state, owned_creatures(self.store, ROOT_BRANCH)), ('HOST_CONFIRMED', {}))
        decision, state, _ = self.tick(game)
        self.assertEqual((decision.rule, state), (ENTER, 'HOST_CONFIRMED'))   # back by the quest
        for observed, reason in ((0, 'WRONG_AREA'), (None, 'NOT_FOUND')):  # no count: no word
            other = despawn_request('INFAI_TESTE', 'AR0406', owned={'INFAI_TESTE'})
            receipt = ActionReceipt(other.action_id, 'REFUSED', observed, reason)
            self.assertEqual(record_result(self.store, ROOT_BRANCH, other, receipt,
                                           game_time=self.t), 'DENIED')

    def test_never_removes_what_the_maintainer_placed(self):
        game = FakeGame()
        req = spawn_request('IATESTE', 'AR0406', templates=TEMPLATES)   # lab_action, no cause
        record_requested(self.store, ROOT_BRANCH, req, game_time=1)
        record_result(self.store, ROOT_BRANCH, req, ActionReceipt(req.action_id, 'DONE', 1, None, 0),
                      game_time=1)
        self.assertEqual(self.tick(game)[0], None)                  # quest not running: kept
        self.assertEqual(game.sent, [])
        out = despawn_request('INFAI_TESTE', 'AR0406', owned={'INFAI_TESTE'})
        self.assertEqual(out.op, DESPAWN)


if __name__ == '__main__':
    unittest.main()
