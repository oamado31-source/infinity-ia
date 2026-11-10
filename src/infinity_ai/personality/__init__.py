# SPDX-License-Identifier: Apache-2.0
"""SPEC-006: synthetic NPC personality, alignment and first-contact runtime."""
from .generator import ALIGNMENT_AXES, HEXACO, generate_new_npc_profile
from .first_contact import FirstContact, FirstContactError, FirstContactService

__all__ = ["ALIGNMENT_AXES", "HEXACO", "generate_new_npc_profile",
           "FirstContact", "FirstContactError", "FirstContactService", "NpcEncounterDialogue"]


def __getattr__(name: str):
    # Lazy: encounter_dialogue imports the dialogue package, which imports personality.style.
    if name == "NpcEncounterDialogue":
        from .encounter_dialogue import NpcEncounterDialogue
        return NpcEncounterDialogue
    raise AttributeError(name)
