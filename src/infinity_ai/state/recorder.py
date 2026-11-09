# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 recorder: turn read-only bridge observations into append-only campaign events.

Only transitions are recorded (a new game session, a new area), not every poll. Envelopes that are
not OBSERVED, not PARTY-visible, synthetic (unless explicitly allowed) or from another campaign are
skipped and never become facts (REQ-BRIDGE-005, ADR-0059). A new session whose first game time is
earlier than what the active branch already recorded forks a child branch (REQ-STATE-002).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum

from ..bridge.domain import Evidence, ObservationEnvelope, Status, Visibility
from ..bridge.eeex_log import AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD, companion_ids
from ..memory.model import AcquisitionMode
from ..memory.store import MemoryStore
from .branches import BranchAction, decide_branch
from .store import CampaignStore, Event

PRESENCE_CHANNEL = 'presence:party'



class RecordAction(str, Enum):
    RECORDED = 'RECORDED'
    NO_CHANGE = 'NO_CHANGE'
    SKIPPED = 'SKIPPED'


@dataclass(frozen=True)
class RecordResult:
    action: RecordAction
    reason: str
    branch_id: str | None = None
    events: tuple[Event, ...] = field(default_factory=tuple)
    experiences: int = 0


def _evidence_name(env: ObservationEnvelope) -> str:
    return env.evidence.value


class ObservationRecorder:
    def __init__(self, store: CampaignStore, *, allow_synthetic: bool = False,
                 run_id: str | None = None) -> None:
        self._store = store
        self._memory = MemoryStore(store)
        self._allow_synthetic = allow_synthetic
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self._epoch: int | None = None
        self._branch = store.active_branch()
        self._last_area = self._latest_area(self._branch)
        self._last_party = self._latest_party(self._branch)

    @property
    def branch_id(self) -> str:
        return self._branch

    def _latest_area(self, branch_id: str) -> str | None:
        areas = self._store.visible_events(branch_id, 'AreaEntered')
        return areas[-1].payload.get('area') if areas else None

    def _latest_party(self, branch_id: str) -> tuple[str, ...] | None:
        changes = self._store.visible_events(branch_id, 'PartyChanged')
        return tuple(changes[-1].payload['members']) if changes else None

    def _party(self, party_env: ObservationEnvelope | None, epoch: int) -> tuple[str, ...] | None:
        """Companions present, or None when unknown (then nobody is credited as a witness)."""
        if party_env is None or self._refusal(party_env, PARTY_FIELD):
            return None
        if party_env.session.host_epoch != epoch:
            return None
        return companion_ids(party_env.value)

    def _refusal(self, env: ObservationEnvelope, expected_field: str) -> str | None:
        if env.field != expected_field:
            return f'expected {expected_field}, got {env.field}'
        if env.status is not Status.OBSERVED:
            return f'{env.field} {env.status.value}'
        if env.visibility is not Visibility.PARTY:
            return f'{env.field} not PARTY'
        if env.evidence is Evidence.SYNTHETIC and not self._allow_synthetic:
            return 'synthetic evidence'
        if env.session.campaign_id != self._store.campaign_id:
            return 'campaign mismatch'
        return None

    def observe(self, area_env: ObservationEnvelope, time_env: ObservationEnvelope,
                party_env: ObservationEnvelope | None = None) -> RecordResult:
        for env, name in ((area_env, AREA_FIELD), (time_env, GAME_TIME_FIELD)):
            reason = self._refusal(env, name)
            if reason:
                return RecordResult(RecordAction.SKIPPED, reason, self._branch)
        if area_env.session.host_epoch != time_env.session.host_epoch:
            return RecordResult(RecordAction.SKIPPED, 'envelopes from different epochs',
                                self._branch)
        try:
            game_time = int(time_env.value)
        except (TypeError, ValueError):
            return RecordResult(RecordAction.SKIPPED, 'game time not numeric', self._branch)
        epoch, area = area_env.session.host_epoch, area_env.value
        evidence = _evidence_name(area_env)
        companions = self._party(party_env, epoch)
        created: list[Event] = []
        witnessed: list[Event] = []
        experiences = 0

        with self._store.transaction():
            if self._epoch != epoch:
                created += self._start_session(epoch, game_time, evidence)
            if area != self._last_area:
                event, new = self._store.append_event(
                    branch_id=self._branch, host_epoch=epoch, event_type='AreaEntered',
                    category='CAMPAIGN_OBSERVATION', game_time=game_time,
                    payload={'area': area, 'previous_area': self._last_area},
                    evidence=evidence, idempotency_key=f'area|{self._branch}|{area}|{game_time}',
                    source_observation_id=area_env.observation_id)
                if new:
                    created.append(event)
                    witnessed.append(event)
                self._last_area = area
            if companions is not None and companions != self._last_party:
                members = list(companions)
                event, new = self._store.append_event(
                    branch_id=self._branch, host_epoch=epoch, event_type='PartyChanged',
                    category='CAMPAIGN_OBSERVATION', game_time=game_time,
                    payload={'members': members, 'previous': list(self._last_party)
                             if self._last_party is not None else None, 'area': area},
                    evidence=evidence,
                    idempotency_key=f'party|{self._branch}|{",".join(members)}|{game_time}',
                    source_observation_id=party_env.observation_id)
                if new:
                    created.append(event)
                    witnessed.append(event)
                self._last_party = companions
            if companions:
                for event in witnessed:
                    for npc_id in companions:
                        _, new = self._memory.record_experience(
                            npc_id=npc_id, branch_id=self._branch, game_time=game_time,
                            mode=AcquisitionMode.OBSERVED, claim_event_id=event.event_id,
                            channel_ref=PRESENCE_CHANNEL)
                        experiences += int(new)

        action = RecordAction.RECORDED if created else RecordAction.NO_CHANGE
        return RecordResult(action, 'ok', self._branch, tuple(created), experiences)

    def _start_session(self, epoch: int, game_time: int, evidence: str) -> list[Event]:
        decision = decide_branch(self._store.latest_game_time(self._branch), game_time)
        created: list[Event] = []
        parent = self._branch
        if decision.action is BranchAction.FORK:
            child = self._store.fork_branch(parent_branch_id=parent, fork_game_time=game_time,
                                            fork_epoch=epoch)
            event, _ = self._store.append_event(
                branch_id=parent, host_epoch=epoch, event_type='BranchForked',
                category='RECONCILIATION', game_time=None,
                payload={'child_branch_id': child, 'fork_game_time': game_time,
                         'lineage': 'INFERRED_FROM_ACTIVE', 'run_id': self.run_id},
                evidence=evidence, idempotency_key=f'fork|{self.run_id}|{epoch}|{child}')
            created.append(event)
            self._branch = child
            self._last_area = self._latest_area(child)
            self._last_party = self._latest_party(child)
        event, _ = self._store.append_event(
            branch_id=self._branch, host_epoch=epoch, event_type='SessionStarted',
            category='RECONCILIATION', game_time=game_time,
            payload={'epoch': epoch, 'first_game_time': game_time, 'run_id': self.run_id,
                     'decision': decision.action.value, 'parent_branch_id':
                     parent if decision.action is BranchAction.FORK else None},
            evidence=evidence, idempotency_key=f'session|{self.run_id}|{epoch}|{game_time}')
        created.append(event)
        self._epoch = epoch
        return created
