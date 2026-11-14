# SPDX-License-Identifier: Apache-2.0
"""SPEC-006: deterministic creation-time personality generator for ORIGINAL NEW NPCs.

This is a pure, synthetic prototype. No engine writes, DB writes, dialogue integration or
automatic alignment changes. Store the returned snapshot; NEVER reroll on every encounter.
Do not call it for existing/official BG2:EE characters, whose alignment and authored
traits require source curation and can have game-mechanical constraints.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections.abc import Mapping

SCHEMA = "infinity-ai.personality.v1"
POLICY = "spec-006-generator-v1"
HEXACO = (
    "honesty_humility", "emotionality", "extraversion",
    "agreeableness", "conscientiousness", "openness",
)
ALIGNMENT_AXES = {
    "LG": ("LAWFUL", "GOOD"),
    "NG": ("NEUTRAL", "GOOD"),
    "CG": ("CHAOTIC", "GOOD"),
    "LN": ("LAWFUL", "NEUTRAL"),
    "TN": ("NEUTRAL", "NEUTRAL"),
    "CN": ("CHAOTIC", "NEUTRAL"),
    "LE": ("LAWFUL", "EVIL"),
    "NE": ("NEUTRAL", "EVIL"),
    "CE": ("CHAOTIC", "EVIL"),
}
VALUES = ("justice", "loyalty", "freedom", "tradition", "knowledge",
          "security", "power", "community", "honor", "compassion")
DRIVES = ("belonging", "achievement", "autonomy", "discovery",
          "protection", "recognition", "stability", "influence")
VULNERABILITIES = ("rejection", "loss", "failure", "betrayal",
                   "powerlessness", "uncertainty", "isolation")


def _validated_weights(weights: Mapping[str, float] | None) -> dict[str, float]:
    if weights is None:
        return {code: 1.0 for code in ALIGNMENT_AXES}
    if not isinstance(weights, Mapping) or set(weights) != set(ALIGNMENT_AXES):
        raise ValueError("alignment_weights must specify exactly all nine AD&D alignments")
    out: dict[str, float] = {}
    for code in ALIGNMENT_AXES:
        value = weights[code]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("alignment weights must be finite, nonnegative numbers")
        if not math.isfinite(value) or value < 0:
            raise ValueError("alignment weights must be finite, nonnegative numbers")
        out[code] = float(value)
    if not math.isfinite(sum(out.values())) or sum(out.values()) <= 0:
        raise ValueError("at least one alignment must have positive weight")
    return out


def generate_new_npc_profile(*, npc_id: str, campaign_id: str, creation_branch_id: str,
                             world_seed: str, npc_origin: str,
                             alignment_weights: Mapping[str, float] | None = None,
                             fixed_alignment: str | None = None) -> dict:
    """Generate a reproducible creation snapshot; caller owns identity + persistence gates.

    Alignment is independently weighted: HEXACO traits do not mechanically imply Good/Evil
    or Law/Chaos. The default neutral prior is uniform only as a sandbox baseline, not a
    demographic or Forgotten Realms population model. Campaign rules can supply weights.
    """
    if npc_origin != "CREATED":
        raise ValueError("only NPCs marked CREATED may be generated; curate official NPCs")
    for value in (npc_id, campaign_id, creation_branch_id, world_seed):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("npc_id, campaign_id, creation_branch_id and world_seed required")
    if not npc_id.startswith("npc:generated:") or len(npc_id) <= len("npc:generated:"):
        raise ValueError("new NPC ids must use npc:generated: namespace")
    if fixed_alignment is not None and fixed_alignment not in ALIGNMENT_AXES:
        raise ValueError("fixed_alignment must be one of the nine alignment codes")
    weights = _validated_weights(alignment_weights)
    seed_text = json.dumps([POLICY, world_seed, campaign_id, creation_branch_id, npc_id],
                           ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    rng = random.Random(int.from_bytes(digest, "big"))
    traits = {trait: round(rng.triangular(0, 100, 50)) for trait in HEXACO}
    draw, cumulative, selected = rng.random() * sum(weights.values()), 0.0, "TN"
    for code, weight in weights.items():
        cumulative += weight
        if draw < cumulative:
            selected = code
            break
    # CR-2026-010: a curated official NPC keeps the alignment of its game sheet. The draw above
    # still runs, so traits, values and drives stay the same as without it.
    provenance = "GENERATED"
    if fixed_alignment is not None:
        selected, provenance = fixed_alignment, "GAME_DATA"
    ethical, moral = ALIGNMENT_AXES[selected]
    return {
        "schema": SCHEMA,
        "npc_id": npc_id,
        "origin": npc_origin,
        "generator_version": POLICY,
        "seed_fingerprint": hashlib.sha256(digest).hexdigest()[:16],
        "creation_context": {"campaign_id": campaign_id,
                             "creation_branch_id": creation_branch_id},
        "hexaco": traits,
        "alignment_initial": {"code": selected, "ethical": ethical, "moral": moral,
                              "provenance": provenance},
        "values": rng.sample(VALUES, 3),
        "drives": rng.sample(DRIVES, 2),
        "vulnerabilities": rng.sample(VULNERABILITIES, 2),
    }
