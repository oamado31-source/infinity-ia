# SPDX-License-Identifier: Apache-2.0
"""SPEC-006: synthetic NPC personality, alignment and first-contact runtime."""
from .generator import ALIGNMENT_AXES, HEXACO, generate_new_npc_profile
from .first_contact import FirstContact, FirstContactError, FirstContactService
from .encounter_dialogue import NpcEncounterDialogue

__all__ = ["ALIGNMENT_AXES", "HEXACO", "generate_new_npc_profile",
           "FirstContact", "FirstContactError", "FirstContactService", "NpcEncounterDialogue"]
