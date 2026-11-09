# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 NPC memory: acquisition, belief revision and recall ACL (synthetic)."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.bridge.domain import Visibility  # noqa: E402
from infinity_ai.memory.model import AcquisitionMode, RecallStatus, Stance  # noqa: E402
from infinity_ai.memory.store import MemoryRuleError, MemoryStore, StaleRevision  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

OBSERVED = AcquisitionMode.OBSERVED


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = CampaignStore.open(Path(self.tmp.name) / 'm.sqlite3', 'lab')
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.store.close)
        self.memory = MemoryStore(self.store)
        self.fact, _ = self.event('fact', 100, {'area': 'AR0602'})

    def event(self, key, game_time, payload, branch=ROOT_BRANCH):
        return self.store.append_event(branch_id=branch, host_epoch=0, event_type='AreaEntered',
                                       category='CAMPAIGN_OBSERVATION', game_time=game_time,
                                       payload=payload, evidence='LAB_OBSERVED',
                                       idempotency_key=key)

    def witness(self, npc='npc:imoen', game_time=100, claim=None, branch=ROOT_BRANCH,
                visibility=Visibility.PARTY, channel='presence:party'):
        exp, _ = self.memory.record_experience(
            npc_id=npc, branch_id=branch, game_time=game_time, mode=OBSERVED,
            claim_event_id=(claim or self.fact).event_id, channel_ref=channel,
            visibility=visibility)
        return exp

    def recall(self, npc='npc:imoen', branch=ROOT_BRANCH, at=1000, purpose='npc_dialogue',
               audience='NARRATIVE_CONTEXT'):
        return self.memory.recall(npc_id=npc, branch_id=branch, at_game_time=at, purpose=purpose,
                                  audience=audience)

    # ---- acquisition ----

    def test_experience_is_idempotent_and_immutable(self):
        exp = self.witness()
        again, created = self.memory.record_experience(
            npc_id='npc:imoen', branch_id=ROOT_BRANCH, game_time=100, mode=OBSERVED,
            claim_event_id=self.fact.event_id, channel_ref='presence:party')
        self.assertEqual((again, created), (exp, False))
        with self.assertRaises(sqlite3.DatabaseError):
            self.store.connection.execute("UPDATE npc_experiences SET npc_id = 'npc:other'")

    def test_cannot_know_before_it_happened_or_from_other_timeline(self):
        with self.assertRaises(MemoryRuleError):
            self.witness(game_time=50)
        child = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=80,
                                       fork_epoch=1)
        with self.assertRaises(MemoryRuleError):  # the fact (t=100) is after the fork point
            self.witness(branch=child, game_time=120)

    def test_secret_is_not_stored_and_inputs_are_checked(self):
        with self.assertRaises(MemoryRuleError):
            self.witness(visibility=Visibility.SECRET)
        with self.assertRaises(MemoryRuleError):
            self.witness(channel='')
        with self.assertRaises(MemoryRuleError):
            self.memory.record_experience(npc_id='npc:imoen', branch_id=ROOT_BRANCH,
                                          game_time=100, mode=OBSERVED, claim_event_id='ev-none',
                                          channel_ref='presence:party')

    # ---- recall ----

    def test_recall_returns_own_memories_with_provenance(self):
        self.witness()
        result = self.recall()
        self.assertEqual(result.status, RecallStatus.OK)
        item = result.items[0]
        self.assertEqual((item.claim_type, item.claim_payload, item.claim_evidence),
                         ('AreaEntered', {'area': 'AR0602'}, 'LAB_OBSERVED'))
        self.assertEqual(item.experience.claim_event_id, self.fact.event_id)

    def test_recall_never_crosses_npc_time_or_branch(self):
        self.witness()
        self.assertEqual(self.recall(npc='npc:jaheira').items, ())
        self.assertEqual(self.recall(at=99).items, ())
        child = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=90,
                                       fork_epoch=1)
        self.assertEqual(self.recall(branch=child).items, ())
        sibling_fact, _ = self.event('sib', 95, {'area': 'AR0700'}, branch=child)
        self.witness(claim=sibling_fact, branch=child, game_time=95)
        self.assertEqual([i.claim_payload['area'] for i in self.recall().items], ['AR0602'])

    def test_recall_respects_audience_and_purpose(self):
        self.witness(visibility=Visibility.HOST_ONLY, channel='presence:host-note')
        self.assertEqual(self.recall(audience='PLAYER').items, ())
        self.assertEqual(len(self.recall(audience='HOST').items), 1)
        self.assertEqual(self.recall(purpose='marketing').status, RecallStatus.DENIED)
        self.assertEqual(self.recall(audience='ADMIN').status, RecallStatus.DENIED)

    def test_recall_requires_known_time_and_branch(self):
        self.assertEqual(self.recall(at=None).reason, 'UNKNOWN_TIME')
        self.assertEqual(self.recall(branch='nope').reason, 'UNKNOWN_BRANCH')

    # ---- beliefs ----

    def revise(self, stance, sources, previous, game_time=110, npc='npc:imoen'):
        return self.memory.revise_belief(
            npc_id=npc, belief_id='belief:party-in-ar0602', branch_id=ROOT_BRANCH,
            game_time=game_time, claim_event_id=self.fact.event_id, stance=stance,
            source_experience_ids=sources, reason_codes=['DIRECT_OBSERVATION'],
            previous_revision_id=previous)

    def test_belief_chain_is_append_only_and_needs_evidence(self):
        exp = self.witness()
        with self.assertRaises(MemoryRuleError):
            self.revise(Stance.ACCEPTED, [], None)
        first = self.revise(Stance.ACCEPTED, [exp.experience_id], None)
        with self.assertRaises(StaleRevision):
            self.revise(Stance.DOUBTFUL, [exp.experience_id], None)
        second = self.revise(Stance.DOUBTFUL, [exp.experience_id], first.revision_id, 120)
        chain = self.memory.belief_chain('belief:party-in-ar0602', ROOT_BRANCH)
        self.assertEqual([r.stance for r in chain], [Stance.ACCEPTED, Stance.DOUBTFUL])
        self.assertEqual(chain[-1].previous_revision_id, first.revision_id)
        self.assertEqual(self.recall().beliefs[0].revision_id, second.revision_id)
        self.assertEqual(self.recall(at=115).beliefs[0].stance, Stance.ACCEPTED)

    def test_belief_cannot_use_someone_elses_or_future_experience(self):
        other = self.witness(npc='npc:jaheira')
        with self.assertRaises(MemoryRuleError):
            self.revise(Stance.ACCEPTED, [other.experience_id], None)
        late = self.witness(game_time=500, channel='presence:later')
        with self.assertRaises(MemoryRuleError):
            self.revise(Stance.ACCEPTED, [late.experience_id], None, game_time=200)

    def test_belief_hidden_when_its_evidence_is_hidden(self):
        exp = self.witness(visibility=Visibility.HOST_ONLY, channel='presence:host-note')
        self.revise(Stance.ACCEPTED, [exp.experience_id], None)
        self.assertEqual(self.recall(audience='PLAYER').beliefs, ())
        self.assertEqual(len(self.recall(audience='HOST').beliefs), 1)


if __name__ == '__main__':
    unittest.main()
