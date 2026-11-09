# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 NPC memory types (subset of the doc 64 candidate contracts, ADR-0059)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AcquisitionMode(str, Enum):
    OBSERVED = 'OBSERVED'
    TOLD = 'TOLD'
    READ = 'READ'
    INVESTIGATED = 'INVESTIGATED'


class Stance(str, Enum):
    ACCEPTED = 'ACCEPTED'
    DOUBTFUL = 'DOUBTFUL'
    REJECTED = 'REJECTED'
    SUSPENDED = 'SUSPENDED'
    INVESTIGATING = 'INVESTIGATING'


class RecallStatus(str, Enum):
    OK = 'OK'
    DENIED = 'DENIED'


@dataclass(frozen=True)
class NpcExperience:
    """How an NPC came to know a claim. Immutable: corrections never edit it (ADR-0059 item 4)."""
    experience_id: str
    npc_id: str
    campaign_id: str
    branch_id: str
    game_time: int
    acquisition_mode: AcquisitionMode
    claim_event_id: str
    channel_ref: str
    visibility: str
    recorded_at: str


@dataclass(frozen=True)
class BeliefRevision:
    """One step of an NPC's stance on a claim; the chain is append-only (REQ-MEM-002)."""
    revision_id: str
    belief_id: str
    previous_revision_id: str | None
    npc_id: str
    branch_id: str
    game_time: int
    claim_event_id: str
    stance: Stance
    source_experience_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    authored_by: str = 'RULES'


@dataclass(frozen=True)
class RecallItem:
    experience: NpcExperience
    claim_type: str
    claim_payload: dict[str, Any]
    claim_evidence: str


@dataclass(frozen=True)
class RecallResult:
    """What an NPC may use now. An empty OK result means "nothing known", never "did not happen"."""
    status: RecallStatus
    reason: str
    items: tuple[RecallItem, ...] = field(default_factory=tuple)
    beliefs: tuple[BeliefRevision, ...] = field(default_factory=tuple)


class KnowledgeBasis(str, Enum):
    """ADR-0114 channels for common regional knowledge (INQUIRY is reserved, not granted yet)."""
    ORIGIN = 'ORIGIN'
    RESIDENCE = 'RESIDENCE'
    INQUIRY = 'INQUIRY'


@dataclass(frozen=True)
class CanonKnowledge:
    """A COMMON_REGIONAL canon entry an NPC acquired, with the summary as it was at the time."""
    knowledge_id: str
    npc_id: str
    branch_id: str
    game_time: int
    basis: KnowledgeBasis
    region_id: str
    entry_id: str
    pack_year_dr: int
    pack_revision: str
    pin_event_id: str
    trigger_event_id: str
    title: str
    summary: str
