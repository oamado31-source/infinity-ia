# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 store, branches and backups (synthetic; not S1 evidence)."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.state import store as store_mod  # noqa: E402
from infinity_ai.state.backup import backup, verify_restore  # noqa: E402
from infinity_ai.state.branches import BranchAction, decide_branch  # noqa: E402
from infinity_ai.state.store import (  # noqa: E402
    ROOT_BRANCH, CampaignStore, IdempotencyConflict, StoreError,
)


def add(store, key, game_time=100, branch=ROOT_BRANCH, payload=None, event_type='AreaEntered'):
    return store.append_event(branch_id=branch, host_epoch=0, event_type=event_type,
                              category='CAMPAIGN_OBSERVATION', game_time=game_time,
                              payload=payload or {'area': 'AR0602'}, evidence='LAB_OBSERVED',
                              idempotency_key=key)


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'campaign.sqlite3'

    def tearDown(self):
        self.tmp.cleanup()

    def open(self, path=None, campaign_id='c1'):
        store = CampaignStore.open(path or self.path, campaign_id)
        self.addCleanup(store.close)
        return store


class StoreTests(TempDirCase):
    def test_append_is_idempotent_and_conflicts_are_refused(self):
        store = self.open()
        first, created = add(store, 'k1')
        again, created_again = add(store, 'k1')
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(first, again)
        with self.assertRaises(IdempotencyConflict):
            add(store, 'k1', payload={'area': 'AR0700'})

    def test_rows_are_append_only(self):
        store = self.open()
        add(store, 'k1')
        for sql in ('UPDATE events SET game_time = 1', 'DELETE FROM events',
                    'UPDATE branches SET lineage = lineage', 'DELETE FROM campaigns'):
            with self.subTest(sql=sql), self.assertRaises(sqlite3.DatabaseError):
                store.connection.execute(sql)

    def test_reopen_does_not_reapply_migrations_and_keeps_data(self):
        store = self.open()
        add(store, 'k1')
        store.close()
        store = self.open()
        versions = store.connection.execute('SELECT version FROM schema_migrations').fetchall()
        self.assertEqual(versions, [(1,)])
        self.assertEqual(len(store.visible_events(ROOT_BRANCH)), 1)

    def test_changed_migration_is_detected(self):
        self.open().close()
        conn = sqlite3.connect(self.path)
        conn.execute("UPDATE schema_migrations SET sha256 = 'tampered'")
        conn.commit()
        conn.close()
        with self.assertRaises(StoreError):
            CampaignStore.open(self.path, 'c1')

    def test_one_campaign_per_database(self):
        self.open().close()
        with self.assertRaises(StoreError):
            CampaignStore.open(self.path, 'c2')

    def test_validation(self):
        store = self.open()
        with self.assertRaises(ValueError):
            store.append_event(branch_id=ROOT_BRANCH, host_epoch=0, event_type='X',
                               category='BELIEF', game_time=1, payload={}, evidence='LAB_OBSERVED',
                               idempotency_key='k')
        with self.assertRaises(StoreError):
            add(store, 'k', branch='nope')
        with self.assertRaises(sqlite3.IntegrityError):
            store.append_event(branch_id=ROOT_BRANCH, host_epoch=-1, event_type='X',
                               category='CAMPAIGN_FACT', game_time=1, payload={},
                               evidence='LAB_OBSERVED', idempotency_key='k2')

    def test_fork_hides_parent_events_after_restore_point(self):
        store = self.open()
        before, _ = add(store, 'before', game_time=100)
        after, _ = add(store, 'after', game_time=300, payload={'area': 'AR0700'})
        child = store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=200, fork_epoch=1)
        mine, _ = add(store, 'child', game_time=250, branch=child, payload={'area': 'AR0800'})
        self.assertEqual([e.idempotency_key for e in store.visible_events(child)],
                         ['before', 'child'])
        self.assertEqual([e.idempotency_key for e in store.visible_events(ROOT_BRANCH)],
                         ['before', 'after'])
        self.assertTrue(store.is_visible(child, before.event_id))
        self.assertFalse(store.is_visible(child, after.event_id))
        self.assertFalse(store.is_visible(ROOT_BRANCH, mine.event_id))
        self.assertEqual(store.active_branch(), child)

    def test_parent_events_recorded_after_fork_stay_out_of_child(self):
        store = self.open()
        child = store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=500, fork_epoch=1)
        late, _ = add(store, 'late', game_time=10)  # recorded in the parent after the fork
        self.assertFalse(store.is_visible(child, late.event_id))

    def test_grandchild_takes_the_tightest_bounds(self):
        store = self.open()
        add(store, 'a', game_time=100)
        add(store, 'b', game_time=400, payload={'area': 'B'})
        child = store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=300, fork_epoch=1)
        add(store, 'c', game_time=350, branch=child, payload={'area': 'C'})
        grandchild = store.fork_branch(parent_branch_id=child, fork_game_time=500, fork_epoch=2)
        self.assertEqual([e.idempotency_key for e in store.visible_events(grandchild)], ['a', 'c'])
        self.assertEqual(store.latest_game_time(grandchild), 350)


class BranchDecisionTests(unittest.TestCase):
    def test_decisions(self):
        self.assertEqual(decide_branch(None, 100).action, BranchAction.CONTINUE)
        self.assertEqual(decide_branch(100, 150).action, BranchAction.CONTINUE)
        self.assertEqual(decide_branch(100, 99).action, BranchAction.CONTINUE)  # pause jitter
        fork = decide_branch(400, 300)
        self.assertEqual((fork.action, fork.fork_game_time), (BranchAction.FORK, 300))
        for bad in (None, -1, True):
            with self.subTest(bad=bad):
                self.assertEqual(decide_branch(100, bad).action, BranchAction.UNKNOWN)


class BackupTests(TempDirCase):
    def test_backup_and_verify(self):
        store = self.open()
        add(store, 'k1')
        info = backup(store, Path(self.tmp.name) / 'backups')
        self.assertEqual(info.last_seq, 1)
        self.assertEqual(info.counts['events'], 1)
        self.assertTrue(verify_restore(info).ok)
        restored = self.open(info.path)
        self.assertEqual(len(restored.visible_events(ROOT_BRANCH)), 1)

    def test_tampered_backup_fails_verification(self):
        store = self.open()
        add(store, 'k1')
        info = backup(store, Path(self.tmp.name) / 'backups')
        with info.path.open('r+b') as fh:
            fh.seek(-1, 2)
            fh.write(b'\x00' if fh.read(1) != b'\x00' else b'\x01')
        self.assertFalse(verify_restore(info).ok)


class MigrationFilesTests(unittest.TestCase):
    def test_migrations_split_into_complete_statements(self):
        sql = (store_mod.MIGRATIONS_DIR / '0001_initial.sql').read_text()
        statements = store_mod._split_sql(sql)
        self.assertTrue(all(sqlite3.complete_statement(s) for s in statements))
        self.assertEqual(sum(s.startswith('CREATE TRIGGER') for s in statements), 12)


if __name__ == '__main__':
    unittest.main()
