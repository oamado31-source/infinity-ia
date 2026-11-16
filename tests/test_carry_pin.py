# SPDX-License-Identifier: Apache-2.0
"""CR-2026-020: a branch forked by a loaded save takes a pack revision the maintainer already
pinned in the same campaign, and nothing else."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from infinity_ai.canon.pin import (  # noqa: E402
    PinStatus, approved_pin, carry_pin, check_pin, pin_pack,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402
from test_canon import TempKnowledge, entry  # noqa: E402


class CarryPinTests(TempKnowledge):
    def setUp(self):
        super().setUp()
        self.store = CampaignStore.open(Path(self.tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.old = self.load()
        pin_pack(self.store, ROOT_BRANCH, self.old, evidence='LAB_OBSERVED', game_time=50)
        self.add(entry())                                     # a new lote: a new revision
        self.new = self.load()
        self.manual, _ = pin_pack(self.store, ROOT_BRANCH, self.new, evidence='LAB_OBSERVED',
                                  game_time=200)
        # Loading a save from before the new pin forks a branch that still sees the old one.
        self.branch = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=150,
                                             fork_epoch=1)

    def test_a_loaded_save_opens_a_branch_with_the_old_pin(self):
        self.assertIs(check_pin(self.store, self.branch, self.new), PinStatus.REVISION_CHANGED)

    def test_the_branch_takes_the_revision_already_pinned_by_hand(self):
        pin, source = carry_pin(self.store, self.branch, self.new, game_time=160)
        self.assertIs(check_pin(self.store, self.branch, self.new), PinStatus.MATCH)
        self.assertEqual(source.event_id, self.manual.event_id)
        self.assertEqual(pin.payload['carried_from'], self.manual.event_id)
        self.assertEqual((pin.branch_id, pin.game_time, pin.evidence),
                         (self.branch, 160, 'LAB_OBSERVED'))
        self.assertIsNone(carry_pin(self.store, self.branch, self.new, game_time=170))

    def test_a_revision_never_pinned_by_hand_stays_off(self):
        self.add(entry(id='event:other-test'), name='other')
        unseen = self.load()
        self.assertIsNone(carry_pin(self.store, self.branch, unseen, game_time=160))
        self.assertIs(check_pin(self.store, self.branch, unseen), PinStatus.REVISION_CHANGED)

    def test_a_carried_pin_never_approves_another(self):
        carry_pin(self.store, self.branch, self.new, game_time=160)
        self.assertEqual(approved_pin(self.store, self.new).event_id, self.manual.event_id)

    def test_a_matching_branch_is_left_alone(self):
        self.assertIsNone(carry_pin(self.store, ROOT_BRANCH, self.new, game_time=210))
        pins = self.store.campaign_events('KnowledgePackPinned')
        self.assertEqual(len(pins), 2)

    def test_a_manual_pin_later_on_the_same_branch_is_idempotent(self):
        carry_pin(self.store, self.branch, self.new, game_time=160)
        _, created = pin_pack(self.store, self.branch, self.new, evidence='LAB_OBSERVED',
                              game_time=170)
        self.assertFalse(created)
