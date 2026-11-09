# SPDX-License-Identifier: Apache-2.0
"""Synthetic NPC personality profiles. Runtime integration is pending SPEC-006 gates."""
from .generator import ALIGNMENT_AXES, HEXACO, generate_new_npc_profile

__all__ = ["ALIGNMENT_AXES", "HEXACO", "generate_new_npc_profile"]
