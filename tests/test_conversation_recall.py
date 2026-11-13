# SPDX-License-Identifier: Apache-2.0
"""ADR-0124: NPCs remember earlier conversations (ids and game time only) and their sources."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import Catalog, build_resident_context  # noqa: E402
from infinity_ai.dialogue.engine import system_prompt  # noqa: E402
from infinity_ai.dialogue.recall import (  # noqa: E402
    DAY, NO_RECALL, TURN_EVENT, npc_key, recall, recall_lines, record_turn,
)
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

PACK = load_partition(1369)
TITLES = {e.id: e.title for e in PACK.entries.values()}


class RecallTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def turn(self, conv, req, entries=(), t=100, key='npc:cre-bernard', branch=ROOT_BRANCH):
        return record_turn(self.store, branch, key=key, speaker_id='npc:cre-bernard',
                           conversation_id=conv, req_id=req, entries=entries, game_time=t,
                           host_epoch=0)

    def test_counts_conversations_and_keeps_recent_subjects(self):
        self.turn('0-1', 'r1', ['org:council-of-six'], t=100)
        self.turn('0-1', 'r2', ['rel:lehtinan-owns-copper-coronet'], t=150)
        self.turn('0-2', 'r3', ['place:copper-coronet'], t=100 + 2 * DAY)
        self.turn('0-2', 'r3', ['place:copper-coronet'], t=100 + 2 * DAY)       # idempotent
        rec = recall(self.store, ROOT_BRANCH, 'npc:cre-bernard', at_game_time=100 + 3 * DAY,
                     exclude_conversation='0-3')
        self.assertEqual(rec.conversations, 2)
        self.assertEqual(rec.subjects, ('place:copper-coronet', 'rel:lehtinan-owns-copper-coronet',
                                        'org:council-of-six'))
        lines = recall_lines(rec, TITLES, 100 + 3 * DAY)
        self.assertEqual(lines[0][1], 'Você já conversou com o jogador antes (2 vezes, a última há 1 dia).')
        self.assertIn('Coroa de Cobre', lines[1][1])
        # The conversation in progress is not "earlier".
        only = recall(self.store, ROOT_BRANCH, 'npc:cre-bernard', at_game_time=10**9,
                      exclude_conversation='0-2')
        self.assertEqual(only.conversations, 1)
        self.assertEqual(recall_lines(NO_RECALL, TITLES, 0), ())

    def test_a_branch_forked_before_the_talk_does_not_remember_it(self):
        self.turn('0-1', 'r1', ['org:council-of-six'], t=500)
        earlier = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=100,
                                         fork_epoch=1)
        self.assertFalse(recall(self.store, earlier, 'npc:cre-bernard', at_game_time=600))
        self.assertTrue(recall(self.store, ROOT_BRANCH, 'npc:cre-bernard', at_game_time=600))

    def test_generic_people_are_remembered_only_in_the_same_session(self):
        same = npc_key('npc:cre-mtown6', stable=False, session_seq=0, instance=7)
        self.assertEqual(same, 'npc:cre-mtown6@0#7')
        self.assertNotEqual(same, npc_key('npc:cre-mtown6', stable=False, session_seq=1,
                                          instance=7))
        self.assertEqual(npc_key('npc:cre-mtown6', stable=False, session_seq=0, instance=None),
                         '')
        self.assertEqual(npc_key('npc:cre-bernard', stable=True, session_seq=3, instance=9),
                         'npc:cre-bernard')

    def test_events_carry_no_text(self):
        self.turn('0-1', 'r1', ['org:council-of-six'])
        payload = self.store.visible_events(ROOT_BRANCH, TURN_EVENT)[0].payload
        self.assertEqual(set(payload), {'npc_key', 'speaker_id', 'conversation_id', 'req_id',
                                        'entries'})
        self.assertNotIn('Conselho', json.dumps(payload, ensure_ascii=False))

    def test_recall_becomes_facts_about_oneself(self):
        self.turn('0-1', 'r1', ['org:council-of-six'], t=100)
        rec = recall(self.store, ROOT_BRANCH, 'npc:cre-bernard', at_game_time=200)
        context = build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:cre-bernard',
            display_name='Bernard', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=200,
            recall_lines=recall_lines(rec, TITLES, 200)).context
        prompt = system_prompt(context)
        self.assertIn('F1: Você já conversou com o jogador antes (uma vez, a última hoje).', prompt)
        self.assertIn('F2: Vocês falaram sobre: Conselho dos Seis.', prompt)
        self.assertIn('Conselho', context.vocabulary)


class HeardFromTests(unittest.TestCase):
    """ADR-0124: a companion can say whom it heard something from (new INQUIRY records)."""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def heard(self, speaker_name, before=None):
        from infinity_ai.canon.pin import pin_pack
        from infinity_ai.dialogue.context import build_context
        from infinity_ai.memory.common_knowledge import share_knowledge
        from infinity_ai.state.recorder import ObservationRecorder
        from test_recorder import obs, party
        store = CampaignStore.open(self.dir / f'{speaker_name or "old"}.sqlite3', 'lab')
        self.addCleanup(store.close)
        ObservationRecorder(store).observe(*obs('AR0406', 10), party('["imoen","jaheira"]'))
        pin_pack(store, ROOT_BRANCH, PACK, game_time=10)
        if before is not None:                     # an earlier hearing, recorded without a name
            share_knowledge(
                store, ROOT_BRANCH, PACK, speaker='npc:cre-bernard', listeners=['npc:jaheira'],
                used_entry_ids=['org:council-of-six'], req_id='r0', host_epoch=0,
                at_game_time=15, also_held=['org:council-of-six'], speaker_name=before)
        report = share_knowledge(
            store, ROOT_BRANCH, PACK, speaker='npc:cre-bernard', listeners=['npc:jaheira'],
            used_entry_ids=['org:council-of-six'], req_id='r1', host_epoch=0, at_game_time=20,
            also_held=['org:council-of-six'], speaker_name=speaker_name, area='AR0406')
        self.assertEqual(report.status, 'OK')
        context = build_context(MemoryStore(store), store, Catalog.load(), npc_id='npc:jaheira',
                                branch_id=ROOT_BRANCH, at_game_time=30).context
        return next(k.text for k in context.knowledge if k.event_id == 'canon:org:council-of-six')

    def test_new_records_say_whom_it_was_heard_from(self):
        text = self.heard('Bernard')
        self.assertTrue(text.startswith('Conselho dos Seis (você ouviu isso de Bernard, na Coroa '
                                        'de Cobre):'), text)

    def test_hearing_it_again_from_a_named_person_gives_the_source(self):
        # The knowledge record keeps the first hearing (no name); the later one has the name.
        text = self.heard('Bernard', before='')
        self.assertIn('(você ouviu isso de Bernard', text)

    def test_older_records_have_no_source(self):
        self.assertTrue(self.heard('').startswith('Conselho dos Seis:'))

    def test_rule_7_allows_naming_the_source(self):
        store = CampaignStore.open(self.dir / 'p.sqlite3', 'lab')
        self.addCleanup(store.close)
        context = build_resident_context(
            MemoryStore(store), store, Catalog.load(), npc_id='npc:cre-x', display_name='X',
            residence_areas=(), area='AR0406', dead=False, branch_id=ROOT_BRANCH,
            at_game_time=10).context
        prompt = system_prompt(context)
        self.assertIn('se o item disser de quem você ouviu', prompt)
        self.assertIn('não invente de quem ouviu', prompt)


if __name__ == '__main__':
    unittest.main()
