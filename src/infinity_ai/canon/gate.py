# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 canon gate (REQ-CANON-001/002): may this curated entry be treated as canon here?

CANON_OK only when the campaign year matches the partition (and the entry's validity), the region
has at least one area in this build's inventory, and every source is S0/S1 with the entry checked
by the maintainer. Anything else is a typed refusal, never a guess.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .pack import CanonPack

CHECKED = frozenset({'SOURCE_CHECKED', 'CAMPAIGN_CANON'})
STRONG_CLASSES = frozenset({'S0_PRIMARY', 'S1_LICENSED'})


class CanonStatus(str, Enum):
    CANON_OK = 'CANON_OK'
    UNKNOWN = 'UNKNOWN'
    WRONG_YEAR = 'WRONG_YEAR'
    UNMAPPED_REGION = 'UNMAPPED_REGION'
    WEAK_SOURCE = 'WEAK_SOURCE'


@dataclass(frozen=True)
class CanonAssessment:
    status: CanonStatus
    reasons: tuple[str, ...] = ()


def assess(pack: CanonPack, entry_id: str, *, campaign_year: int,
           build_areas: frozenset[str] | None) -> CanonAssessment:
    entry = pack.get(entry_id)
    if entry is None:
        return CanonAssessment(CanonStatus.UNKNOWN, ('NO_ENTRY',))
    if pack.year_dr != campaign_year:
        return CanonAssessment(CanonStatus.WRONG_YEAR, (f'partition {pack.year_dr}',))
    lo, hi = entry.valid_from_dr, entry.valid_to_dr
    if (lo is not None and campaign_year < lo) or (hi is not None and campaign_year > hi):
        return CanonAssessment(CanonStatus.WRONG_YEAR, ('outside validity',))

    region = entry if entry.kind == 'REGION' else (pack.get(entry.region_id)
                                                   if entry.region_id else None)
    if entry.region_id and region is None:
        return CanonAssessment(CanonStatus.UNKNOWN, ('REGION_NOT_IN_PACK',))
    if region is not None:
        if build_areas is None:
            return CanonAssessment(CanonStatus.UNKNOWN, ('NO_INVENTORY',))
        if not set(region.area_resrefs) & build_areas:
            return CanonAssessment(CanonStatus.UNMAPPED_REGION, (region.id,))

    reasons = []
    if entry.verification_status not in CHECKED:
        reasons.append(entry.verification_status)
    for ref in entry.source_refs:
        source = pack.sources.get(ref.source_id)
        if source is None or source.source_class not in STRONG_CLASSES:
            reasons.append(f'WEAK_CLASS:{ref.source_id}')
        elif source.setting_year_dr not in (None, campaign_year) and lo is None and hi is None:
            reasons.append(f'SETTING_YEAR_MISMATCH:{ref.source_id}')
    if reasons:
        return CanonAssessment(CanonStatus.WEAK_SOURCE, tuple(reasons))
    return CanonAssessment(CanonStatus.CANON_OK)
