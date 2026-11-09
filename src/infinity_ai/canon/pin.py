# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 / ADR-0058: pin a canon pack revision to a campaign branch (no silent updates)."""
from __future__ import annotations

from enum import Enum

from ..state.store import CampaignStore, Event
from .pack import CanonPack


class PinStatus(str, Enum):
    MATCH = 'MATCH'
    NOT_PINNED = 'NOT_PINNED'
    REVISION_CHANGED = 'REVISION_CHANGED'


def pin_pack(store: CampaignStore, branch_id: str, pack: CanonPack, *,
             evidence: str = 'SYNTHETIC') -> tuple[Event, bool]:
    """Record which pack revision this branch uses; re-pinning the same revision is idempotent."""
    with store.transaction():
        return store.append_event(
            branch_id=branch_id, host_epoch=0, event_type='KnowledgePackPinned',
            category='CAMPAIGN_FACT', game_time=None,
            payload={'year_dr': pack.year_dr, 'revision': pack.revision,
                     'coverage_status': pack.coverage_status, 'entries': len(pack.entries)},
            evidence=evidence,
            idempotency_key=f'pack-pin|{branch_id}|{pack.year_dr}|{pack.revision}')


def check_pin(store: CampaignStore, branch_id: str, pack: CanonPack) -> PinStatus:
    pins = [e for e in store.visible_events(branch_id, 'KnowledgePackPinned')
            if e.payload.get('year_dr') == pack.year_dr]
    if not pins:
        return PinStatus.NOT_PINNED
    return PinStatus.MATCH if pins[-1].payload.get('revision') == pack.revision \
        else PinStatus.REVISION_CHANGED
