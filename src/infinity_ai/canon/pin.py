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
             evidence: str = 'SYNTHETIC', game_time: int | None = None,
             carried_from: str | None = None) -> tuple[Event, bool]:
    """Record which pack revision this branch uses; re-pinning the same revision is idempotent.

    `game_time` (latest observed game time, when known) anchors ADR-0114: only residence time
    after the pin counts towards common knowledge of this revision. `carried_from` (CR-2026-020)
    names the maintainer's explicit pin that a carried pin repeats."""
    current = active_pin(store, branch_id, pack.year_dr)
    if current is not None and current.branch_id == branch_id \
            and current.payload.get('revision') == pack.revision:
        return current, False            # already pinned here, by hand or carried (CR-2026-020)
    payload = {'year_dr': pack.year_dr, 'revision': pack.revision,
               'coverage_status': pack.coverage_status, 'entries': len(pack.entries)}
    if carried_from is not None:
        payload['carried_from'] = carried_from
    with store.transaction():
        return store.append_event(
            branch_id=branch_id, host_epoch=0, event_type='KnowledgePackPinned',
            category='CAMPAIGN_FACT', game_time=game_time, payload=payload, evidence=evidence,
            idempotency_key=f'pack-pin|{branch_id}|{pack.year_dr}|{pack.revision}')


def approved_pin(store: CampaignStore, pack: CanonPack) -> Event | None:
    """CR-2026-020: the latest explicit pin of this very revision on any branch of the campaign
    (a carried pin never approves another)."""
    for event in reversed(store.campaign_events('KnowledgePackPinned')):
        payload = event.payload
        if (payload.get('year_dr') == pack.year_dr and payload.get('revision') == pack.revision
                and not payload.get('carried_from')):
            return event
    return None


def carry_pin(store: CampaignStore, branch_id: str, pack: CanonPack, *,
              game_time: int | None = None) -> tuple[Event, Event] | None:
    """CR-2026-020 (ADR-0058 item 6, pre-authorised policy): a branch without this revision (a
    loaded save forks one with the pin of its time) takes it only when the maintainer already
    pinned this very revision on another branch of the same campaign. Returns (new pin, the
    approving pin), or None when the branch already matches or nothing approves the revision."""
    if check_pin(store, branch_id, pack) is PinStatus.MATCH:
        return None
    source = approved_pin(store, pack)
    if source is None:
        return None
    event, _ = pin_pack(store, branch_id, pack, evidence=source.evidence, game_time=game_time,
                        carried_from=source.event_id)
    return event, source


def active_pin(store: CampaignStore, branch_id: str, year_dr: int) -> Event | None:
    pins = [e for e in store.visible_events(branch_id, 'KnowledgePackPinned')
            if e.payload.get('year_dr') == year_dr]
    return pins[-1] if pins else None


def check_pin(store: CampaignStore, branch_id: str, pack: CanonPack) -> PinStatus:
    pins = [e for e in store.visible_events(branch_id, 'KnowledgePackPinned')
            if e.payload.get('year_dr') == pack.year_dr]
    if not pins:
        return PinStatus.NOT_PINNED
    return PinStatus.MATCH if pins[-1].payload.get('revision') == pack.revision \
        else PinStatus.REVISION_CHANGED
