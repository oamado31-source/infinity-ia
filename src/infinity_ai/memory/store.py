# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 NPC memory store over the campaign database.

Acquisition needs a confirmed campaign event visible in the NPC's branch at or before the time of
acquisition (no knowing the future, no knowledge from a sibling timeline). Belief revisions need
at least one of the NPC's own experiences as evidence and must extend the current head of the
chain. Recall applies identity, branch lineage, time and audience *before* returning anything
(ADR-0023); SECRET is never stored in this stage. No LLM writes here.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Iterable

from ..bridge.domain import Audience, Visibility, audience_may_see
from ..state.store import CampaignStore, LineageStep, StoreError
from .model import (
    AcquisitionMode, BeliefRevision, NpcExperience, RecallItem, RecallResult, RecallStatus,
    Stance,
)

RECALL_PURPOSES = frozenset({'narrative_context', 'npc_dialogue'})
STORABLE_VISIBILITY = frozenset({Visibility.PARTY, Visibility.HOST_ONLY})


class MemoryRuleError(StoreError):
    pass


class StaleRevision(MemoryRuleError):
    """previous_revision_id is not the current head of the belief chain."""


_EXP_FIELDS = ('experience_id, npc_id, campaign_id, branch_id, game_time, acquisition_mode, '
               'claim_event_id, channel_ref, visibility')
_EXP_COLUMNS = _EXP_FIELDS + ', recorded_at'


def _row_to_experience(row: tuple) -> NpcExperience:
    return NpcExperience(row[0], row[1], row[2], row[3], row[4], AcquisitionMode(row[5]), row[6],
                         row[7], row[8], row[9])


class MemoryStore:
    def __init__(self, store: CampaignStore) -> None:
        self._store = store
        self._conn = store.connection

    # ---- helpers --------------------------------------------------------------------------

    def _step_for(self, branch_id: str, owner_branch: str) -> LineageStep | None:
        return next((s for s in self._store.lineage(branch_id) if s.branch_id == owner_branch),
                    None)

    def _experience_visible(self, exp: NpcExperience, branch_id: str) -> bool:
        step = self._step_for(branch_id, exp.branch_id)
        claim = self._store.get_event(exp.claim_event_id)
        return step is not None and claim is not None and step.admits(claim.seq, exp.game_time)

    def get_experience(self, experience_id: str) -> NpcExperience | None:
        row = self._conn.execute(f'SELECT {_EXP_COLUMNS} FROM npc_experiences '
                                 'WHERE experience_id = ?', (experience_id,)).fetchone()
        return _row_to_experience(row) if row else None

    # ---- acquisition ----------------------------------------------------------------------

    def record_experience(self, *, npc_id: str, branch_id: str, game_time: int,
                          mode: AcquisitionMode, claim_event_id: str, channel_ref: str,
                          visibility: Visibility = Visibility.PARTY
                          ) -> tuple[NpcExperience, bool]:
        if not npc_id or not channel_ref:
            raise MemoryRuleError('npc_id and channel_ref are required')
        if visibility not in STORABLE_VISIBILITY:
            raise MemoryRuleError(f'{visibility} is not persisted in this stage')
        if isinstance(game_time, bool) or not isinstance(game_time, int) or game_time < 0:
            raise MemoryRuleError('game_time must be a non-negative integer')
        if not self._store.is_visible(branch_id, claim_event_id):
            raise MemoryRuleError('claim event is not part of this branch')
        claim = self._store.get_event(claim_event_id)
        if claim.game_time is not None and claim.game_time > game_time:
            raise MemoryRuleError('cannot acquire a claim before it happened')
        key = hashlib.sha256('|'.join((self._store.campaign_id, npc_id, branch_id, claim_event_id,
                                       mode.value, channel_ref)).encode()).hexdigest()
        experience_id = 'xp-' + uuid.uuid4().hex
        cursor = self._conn.execute(
            f'INSERT INTO npc_experiences ({_EXP_FIELDS}, idempotency_key, recorded_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (idempotency_key) DO NOTHING',
            (experience_id, npc_id, self._store.campaign_id, branch_id, game_time, mode.value,
             claim_event_id, channel_ref, visibility.value, key, self._store.now()))
        row = self._conn.execute(f'SELECT {_EXP_COLUMNS} FROM npc_experiences '
                                 'WHERE idempotency_key = ?', (key,)).fetchone()
        return _row_to_experience(row), cursor.rowcount == 1

    # ---- beliefs --------------------------------------------------------------------------

    def belief_chain(self, belief_id: str, branch_id: str) -> list[BeliefRevision]:
        rows = self._conn.execute(
            'SELECT revision_id, belief_id, previous_revision_id, npc_id, branch_id, game_time, '
            'claim_event_id, stance, reason_codes_json FROM belief_revisions '
            'WHERE belief_id = ? AND campaign_id = ? ORDER BY rowid', (belief_id,
                                                                     self._store.campaign_id))
        chain = []
        for r in rows.fetchall():
            step = self._step_for(branch_id, r[4])
            claim = self._store.get_event(r[6])
            if step is None or claim is None or not step.admits(claim.seq, r[5]):
                continue
            sources = tuple(s for (s,) in self._conn.execute(
                'SELECT experience_id FROM belief_revision_sources WHERE revision_id = ? '
                'ORDER BY experience_id', (r[0],)))
            chain.append(BeliefRevision(r[0], r[1], r[2], r[3], r[4], r[5], r[6], Stance(r[7]),
                                        sources, tuple(json.loads(r[8]))))
        return chain

    def revise_belief(self, *, npc_id: str, belief_id: str, branch_id: str, game_time: int,
                      claim_event_id: str, stance: Stance, source_experience_ids: Iterable[str],
                      reason_codes: Iterable[str], previous_revision_id: str | None
                      ) -> BeliefRevision:
        sources = tuple(dict.fromkeys(source_experience_ids))
        if not sources:
            raise MemoryRuleError('a belief revision needs at least one experience as evidence')
        if not self._store.is_visible(branch_id, claim_event_id):
            raise MemoryRuleError('claim event is not part of this branch')
        for experience_id in sources:
            exp = self.get_experience(experience_id)
            if exp is None or exp.npc_id != npc_id:
                raise MemoryRuleError(f'{experience_id} is not an experience of {npc_id}')
            if not self._experience_visible(exp, branch_id) or exp.game_time > game_time:
                raise MemoryRuleError(f'{experience_id} is not available to {npc_id} at that time')
        chain = self.belief_chain(belief_id, branch_id)
        if chain and chain[-1].npc_id != npc_id:
            raise MemoryRuleError('belief belongs to another NPC')
        head = chain[-1].revision_id if chain else None
        if previous_revision_id != head:
            raise StaleRevision(f'head is {head}, got {previous_revision_id}')
        revision = BeliefRevision('rev-' + uuid.uuid4().hex, belief_id, previous_revision_id, npc_id,
                                  branch_id, game_time, claim_event_id, Stance(stance), sources,
                                  tuple(reason_codes))
        with self._store.transaction():
            self._conn.execute(
                'INSERT INTO belief_revisions (revision_id, belief_id, previous_revision_id, '
                'campaign_id, branch_id, npc_id, game_time, claim_event_id, stance, '
                "reason_codes_json, authored_by, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'RULES', ?)",
                (revision.revision_id, belief_id, previous_revision_id, self._store.campaign_id,
                 branch_id, npc_id, game_time, claim_event_id, revision.stance.value,
                 json.dumps(list(revision.reason_codes)), self._store.now()))
            self._conn.executemany('INSERT INTO belief_revision_sources VALUES (?, ?)',
                                   [(revision.revision_id, s) for s in sources])
        return revision

    # ---- recall ---------------------------------------------------------------------------

    def recall(self, *, npc_id: str, branch_id: str, at_game_time: int | None, purpose: str,
               audience: str) -> RecallResult:
        if purpose not in RECALL_PURPOSES:
            return RecallResult(RecallStatus.DENIED, 'ACL_PURPOSE')
        try:
            audience_enum = Audience(audience)
        except ValueError:
            return RecallResult(RecallStatus.DENIED, 'UNKNOWN_AUDIENCE')
        if not self._store.branch_exists(branch_id):
            return RecallResult(RecallStatus.DENIED, 'UNKNOWN_BRANCH')
        if isinstance(at_game_time, bool) or not isinstance(at_game_time, int) or at_game_time < 0:
            return RecallResult(RecallStatus.DENIED, 'UNKNOWN_TIME')

        rows = self._conn.execute(f'SELECT {_EXP_COLUMNS} FROM npc_experiences '
                                  'WHERE campaign_id = ? AND npc_id = ? ORDER BY game_time, rowid',
                                  (self._store.campaign_id, npc_id)).fetchall()
        items = []
        for exp in map(_row_to_experience, rows):
            if exp.game_time > at_game_time or not self._experience_visible(exp, branch_id):
                continue
            if not audience_may_see(audience_enum, Visibility(exp.visibility)):
                continue
            claim = self._store.get_event(exp.claim_event_id)
            items.append(RecallItem(exp, claim.event_type, claim.payload, claim.evidence))

        belief_ids = [b for (b,) in self._conn.execute(
            'SELECT DISTINCT belief_id FROM belief_revisions WHERE campaign_id = ? AND npc_id = ?',
            (self._store.campaign_id, npc_id))]
        visible_sources = {i.experience.experience_id for i in items}
        beliefs = []
        for belief_id in sorted(belief_ids):
            chain = [r for r in self.belief_chain(belief_id, branch_id)
                     if r.game_time <= at_game_time]
            if chain and set(chain[-1].source_experience_ids) <= visible_sources:
                beliefs.append(chain[-1])
        return RecallResult(RecallStatus.OK, 'OK', tuple(items), tuple(beliefs))
