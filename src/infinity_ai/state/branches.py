# SPDX-License-Identifier: Apache-2.0
"""SPEC-003 / REQ-STATE-002: decide whether a new game session continues the active branch.

The bridge cannot tell which save was loaded. What it can tell is the game time when a new epoch
starts. If that time is earlier than the latest event already recorded in the active branch, those
events are not in the past of the loaded save: the session forks a child branch at that time, and
the old rows stay untouched. Lineage is therefore *inferred* from the active branch.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# m_gameTime steps back 1 tick on pause (noted in EEex B3TimeStep.lua; seen in the P2 lab run).
PAUSE_JITTER_TICKS = 2


class BranchAction(str, Enum):
    CONTINUE = 'CONTINUE'
    FORK = 'FORK'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class BranchDecision:
    action: BranchAction
    fork_game_time: int | None = None


def decide_branch(last_recorded_game_time: int | None, first_game_time: int | None, *,
                  jitter: int = PAUSE_JITTER_TICKS) -> BranchDecision:
    """CONTINUE when nothing recorded lies after the session's first observed time; FORK otherwise.

    Without an observed first time the decision is UNKNOWN: no branch is created and nothing is
    recorded until a real time is seen.
    """
    if first_game_time is None or isinstance(first_game_time, bool) or first_game_time < 0:
        return BranchDecision(BranchAction.UNKNOWN)
    if last_recorded_game_time is None or first_game_time >= last_recorded_game_time - jitter:
        return BranchDecision(BranchAction.CONTINUE)
    return BranchDecision(BranchAction.FORK, first_game_time)
