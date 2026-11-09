# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 recorder over bridge envelopes (synthetic; not S1 evidence)."""
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.bridge.domain import (  # noqa: E402
    Audience, Coverage, Evidence, ObservationEnvelope, Reason, SessionIdentity, Status,
    Visibility,
)
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.state.recorder import ObservationRecorder, RecordAction  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

SESSION = SessionIdentity('lab', 'main', 0, 'sha256:b', 'sha256:m', 'eeex-log-0.1+probe-v1')


def env(field, value, epoch=0, status=Status.OBSERVED, evidence=Evidence.LAB_OBSERVED,
        visibility=Visibility.PARTY, campaign='lab'):
    observed = status is Status.OBSERVED
    return ObservationEnvelope(
        observation_id=f'obs-{field}-{value}', timestamp='2026-11-09T00:00:00Z',
        session=replace(SESSION, host_epoch=epoch, campaign_id=campaign), field=field,
        purpose='narrative_context', audience=Audience.PLAYER, status=status,
        reason=Reason.NONE if observed else Reason.NOT_OBSERVED,
        value=str(value) if observed else None,
        coverage=Coverage.FULL if observed else Coverage.NONE, visibility=visibility,
        evidence=evidence)


def obs(area, time, epoch=0, **kw):
    return env('host.current_area_id', area, epoch, **kw), env('host.game_time', time, epoch, **kw)


def party(members, epoch=0, **kw):
    return env('party.companion_ids', members, epoch, **kw)


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'lab.sqlite3'
        self.store = CampaignStore.open(self.path, 'lab')
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(lambda: self.store.close())

    def types(self, branch):
        return [e.event_type for e in self.store.visible_events(branch)]

    def test_first_observation_starts_session_and_enters_area(self):
        result = ObservationRecorder(self.store).observe(*obs('AR0602', 100))
        self.assertEqual(result.action, RecordAction.RECORDED)
        self.assertEqual(self.types(ROOT_BRANCH), ['SessionStarted', 'AreaEntered'])
        area = self.store.visible_events(ROOT_BRANCH, 'AreaEntered')[0]
        self.assertEqual((area.payload['area'], area.game_time, area.evidence),
                         ('AR0602', 100, 'LAB_OBSERVED'))

    def test_only_transitions_are_recorded(self):
        rec = ObservationRecorder(self.store)
        rec.observe(*obs('AR0602', 100))
        self.assertEqual(rec.observe(*obs('AR0602', 160)).action, RecordAction.NO_CHANGE)
        rec.observe(*obs('AR0603', 220))
        self.assertEqual(self.types(ROOT_BRANCH), ['SessionStarted', 'AreaEntered', 'AreaEntered'])

    def test_not_observed_synthetic_foreign_or_non_party_is_skipped(self):
        rec = ObservationRecorder(self.store)
        cases = {
            'unknown area': (env('host.current_area_id', None, status=Status.UNKNOWN),
                             env('host.game_time', 1)),
            'synthetic': obs('AR0602', 1, evidence=Evidence.SYNTHETIC),
            'other campaign': obs('AR0602', 1, campaign='other'),
            'host only': obs('AR0602', 1, visibility=Visibility.HOST_ONLY),
            'mixed epochs': (env('host.current_area_id', 'AR0602', 0), env('host.game_time', 1, 1)),
            'swapped fields': (env('host.game_time', 1), env('host.current_area_id', 'AR0602')),
        }
        for name, pair in cases.items():
            with self.subTest(name):
                self.assertEqual(rec.observe(*pair).action, RecordAction.SKIPPED)
        self.assertEqual(self.types(ROOT_BRANCH), [])

    def test_synthetic_allowed_only_when_explicit(self):
        ObservationRecorder(self.store, allow_synthetic=True).observe(
            *obs('AR0602', 1, evidence=Evidence.SYNTHETIC))
        self.assertEqual(self.store.visible_events(ROOT_BRANCH)[0].evidence, 'SYNTHETIC')

    def test_load_of_earlier_save_forks_and_keeps_old_rows(self):
        rec = ObservationRecorder(self.store)
        rec.observe(*obs('AR0602', 100))
        rec.observe(*obs('AR0603', 400))            # after the save point
        result = rec.observe(*obs('AR0602', 300, epoch=1))  # load save made at t=300
        child = result.branch_id
        self.assertNotEqual(child, ROOT_BRANCH)
        self.assertEqual(self.types(ROOT_BRANCH),
                         ['SessionStarted', 'AreaEntered', 'AreaEntered', 'BranchForked'])
        # The child inherits "entered AR0602 at t=100"; still in AR0602 after the load, so no new
        # transition. AR0603 at t=400 is not part of this timeline.
        self.assertEqual(self.types(child), ['SessionStarted', 'AreaEntered', 'SessionStarted'])
        areas = [e.payload['area'] for e in self.store.visible_events(child, 'AreaEntered')]
        self.assertEqual(areas, ['AR0602'])
        rec.observe(*obs('AR0603', 350, epoch=1))  # entering AR0603 again in the new timeline
        self.assertEqual([e.game_time for e in self.store.visible_events(child, 'AreaEntered')],
                         [100, 350])
        session = self.store.visible_events(child, 'SessionStarted')[-1]
        self.assertEqual((session.payload['decision'], session.payload['parent_branch_id']),
                         ('FORK', ROOT_BRANCH))

    def test_load_that_does_not_go_back_continues(self):
        rec = ObservationRecorder(self.store)
        rec.observe(*obs('AR0602', 100))
        result = rec.observe(*obs('AR0602', 150, epoch=1))
        self.assertEqual(result.branch_id, ROOT_BRANCH)
        self.assertEqual(self.types(ROOT_BRANCH), ['SessionStarted', 'AreaEntered',
                                                   'SessionStarted'])

    def test_restarted_recorder_does_not_duplicate(self):
        ObservationRecorder(self.store).observe(*obs('AR0602', 100))
        self.store.close()
        self.store = CampaignStore.open(self.path, 'lab')
        rec = ObservationRecorder(self.store)
        rec.observe(*obs('AR0602', 120))
        self.assertEqual(self.types(ROOT_BRANCH), ['SessionStarted', 'AreaEntered',
                                                   'SessionStarted'])

    def test_game_restart_reusing_epoch_zero_still_forks(self):
        rec = ObservationRecorder(self.store)
        rec.observe(*obs('AR0602', 100))
        rec.observe(*obs('AR0603', 400))
        rec2 = ObservationRecorder(self.store)       # new process, probe counts from 0 again
        result = rec2.observe(*obs('AR0602', 300, epoch=0))
        self.assertNotEqual(result.branch_id, ROOT_BRANCH)


    def test_companions_present_remember_what_they_witnessed(self):
        rec = ObservationRecorder(self.store)
        result = rec.observe(*obs('AR0602', 100), party('["imoen"]'))
        self.assertEqual(result.experiences, 2)  # AreaEntered + PartyChanged
        memory = MemoryStore(self.store)
        recalled = memory.recall(npc_id='npc:imoen', branch_id=ROOT_BRANCH, at_game_time=100,
                                 purpose='npc_dialogue', audience='NARRATIVE_CONTEXT')
        self.assertEqual(sorted(i.claim_type for i in recalled.items),
                         ['AreaEntered', 'PartyChanged'])
        self.assertEqual({i.experience.channel_ref for i in recalled.items}, {'presence:party'})
        nobody = memory.recall(npc_id='npc:jaheira', branch_id=ROOT_BRANCH, at_game_time=100,
                               purpose='npc_dialogue', audience='NARRATIVE_CONTEXT')
        self.assertEqual(nobody.items, ())

    def test_party_change_and_new_member_only_knows_from_joining(self):
        rec = ObservationRecorder(self.store)
        rec.observe(*obs('AR0602', 100), party('["imoen"]'))
        rec.observe(*obs('AR0602', 200), party('["imoen","jaheira"]'))
        rec.observe(*obs('AR0603', 300), party('["imoen","jaheira"]'))
        memory = MemoryStore(self.store)
        jaheira = memory.recall(npc_id='npc:jaheira', branch_id=ROOT_BRANCH, at_game_time=1000,
                                purpose='npc_dialogue', audience='NARRATIVE_CONTEXT')
        self.assertEqual([(i.claim_type, i.experience.game_time) for i in jaheira.items],
                         [('PartyChanged', 200), ('AreaEntered', 300)])
        changes = self.store.visible_events(ROOT_BRANCH, 'PartyChanged')
        self.assertEqual([c.payload['members'] for c in changes],
                         [['npc:imoen'], ['npc:imoen', 'npc:jaheira']])

    def test_unknown_or_unusable_party_credits_nobody(self):
        rec = ObservationRecorder(self.store)
        for bad in (party(None, status=Status.UNKNOWN), party('["imoen"]', epoch=5),
                    party('["imoen"]', evidence=Evidence.SYNTHETIC), party('not json'), None):
            rec.observe(*obs('AR0602', 100), bad)
        self.assertEqual(self.store.connection.execute(
            'SELECT COUNT(*) FROM npc_experiences').fetchone()[0], 0)
        self.assertEqual(self.store.visible_events(ROOT_BRANCH, 'PartyChanged'), [])

    def test_fork_restores_party_from_the_new_timeline(self):
        rec = ObservationRecorder(self.store)
        rec.observe(*obs('AR0602', 100), party('["imoen"]'))
        rec.observe(*obs('AR0602', 400), party('["imoen","jaheira"]'))
        result = rec.observe(*obs('AR0602', 300, epoch=1), party('["imoen","jaheira"]', epoch=1))
        changes = self.store.visible_events(result.branch_id, 'PartyChanged')
        self.assertEqual([c.payload['members'] for c in changes],
                         [['npc:imoen'], ['npc:imoen', 'npc:jaheira']])
        self.assertEqual(changes[-1].game_time, 300)  # Jaheira joins again in this timeline

if __name__ == '__main__':
    unittest.main()
