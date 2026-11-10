# SPDX-License-Identifier: Apache-2.0
"""SPEC-006: lazy personality provisioning when a dialogue *observation* is received.

The future game adapter owns the observation and actor-target proof. No player text,
creature name, scene position or resref is trusted as an identity. Without VERIFIED
identity, only a scene/session-bound presentation exists (ADR-0061/0062).
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..state.store import CampaignStore, Event
from .generator import generate_new_npc_profile

ROLE_NAMES = {
    "BEGGAR": "Pessoa pedindo esmolas",
    "COMMONER": "Pessoa comum",
    "PEASANT": "Camponês",
    "MERCHANT": "Comerciante",
    "GUARD": "Guarda",
    "TRAVELER": "Viajante",
    "ARTISAN": "Artesão",
    "NOBLE": "Nobre",
    "OTHER": "Pessoa desconhecida",
}
_ALLOWED_STATES = {"VERIFIED", "CANDIDATE", "AMBIGUOUS", "STALE", "CANONICAL"}
_CONTACT_EVENT = "NpcDialogueStarted"
_ASSIGNMENT_EVENT = "NpcPersonalityAssigned"
_PROOF_EVENT = "NpcIdentityVerified"


class FirstContactError(ValueError):
    """Missing/invalid observation or identity proof. Fail closed."""


@dataclass(frozen=True)
class FirstContact:
    status: str
    npc_id: str | None
    display_name: str
    profile: dict[str, Any] | None
    scope: str
    created: bool
    contact_event_id: str
    reason: str = "OK"
    identity: dict[str, Any] | None = None   # ADR-0117 generated background (never for CANONICAL)


def _required(payload: dict, name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise FirstContactError("invalid or missing " + name)
    return value


def _digest(*parts: str) -> str:
    blob = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _at_event(store: CampaignStore, *, event_id: str, branch_id: str,
              at_game_time: int) -> Event:
    event = store.get_event(event_id)
    if event is None or not store.is_visible(branch_id, event_id):
        raise FirstContactError("event not visible in this branch")
    if event.game_time is None or event.game_time > at_game_time:
        raise FirstContactError("event outside requested game time")
    return event


class FirstContactService:
    """Assign once on verified identity, otherwise a temporary encounter persona.

    Only trusted observation code may append NpcDialogueStarted/NpcIdentityVerified.
    An arbitrary player-supplied HTTP request is NOT an observation. The current EEex
    probe does not produce these events: game-click integration remains unverified.
    """

    def __init__(self, store: CampaignStore, *, world_seed: str,
                 alignment_weights: dict[str, float] | None = None) -> None:
        if not isinstance(world_seed, str) or not world_seed.strip():
            raise ValueError("world_seed required")
        self.store = store
        self.world_seed = world_seed
        self.weights = alignment_weights

    def begin(self, *, contact_event_id: str, branch_id: str, at_game_time: int,
              identity_factory: Callable[[str], dict] | None = None) -> FirstContact:
        if isinstance(at_game_time, bool) or not isinstance(at_game_time, int) or at_game_time < 0:
            raise FirstContactError("invalid game time")
        event = _at_event(self.store, event_id=contact_event_id,
                          branch_id=branch_id, at_game_time=at_game_time)
        if event.event_type != _CONTACT_EVENT or event.category != "CAMPAIGN_OBSERVATION":
            raise FirstContactError("not a dialogue-start observation")
        data = event.payload
        if data.get("dialogue_started") is not True or data.get("target_visible") is not True:
            raise FirstContactError("dialogue target was not confirmed")
        if data.get("access_allowed") is not True:
            raise FirstContactError("interaction not allowed")
        session = _required(data, "session_id")
        scene = _required(data, "scene_id")
        state = _required(data, "identity_state")
        if state not in _ALLOWED_STATES:
            raise FirstContactError("unknown identity state")
        role = data.get("role")
        if not isinstance(role, str) or role not in ROLE_NAMES:
            raise FirstContactError("role must be an adapter-curated enum")
        display = ROLE_NAMES[role]

        if state == "CANONICAL":
            # The official NPC's authored/canonical profile belongs to SPEC-005.
            # A mere actor name cannot be used to force a generated alignment.
            return FirstContact("CURATION_REQUIRED", None, display, None, "CANONICAL",
                                False, event.event_id, "USE_CANONICAL_PROFILE")

        actor_ref = data.get("actor_instance_token")
        actor_ref = actor_ref if isinstance(actor_ref, str) and actor_ref.strip() \
            and len(actor_ref) <= 256 else None

        if state != "VERIFIED":
            # No identity, no cross-session memory. A trusted per-scene actor token
            # permits reuse within one live session; otherwise each dialogue is
            # an independent encounter (never reuse a name/CRE/script reference).
            token = actor_ref if data.get("token_uniqueness") == "SCENE_VERIFIED" \
                else event.event_id
            key = _digest(self.store.campaign_id, branch_id, str(event.host_epoch),
                          session, scene, token)
            npc_id = "npc:generated:enc-" + key[:24]
            profile = generate_new_npc_profile(
                npc_id=npc_id, campaign_id=self.store.campaign_id,
                creation_branch_id=branch_id, world_seed=self.world_seed,
                npc_origin="CREATED", alignment_weights=self.weights)
            identity = identity_factory(npc_id) if identity_factory else None
            return FirstContact("READY", npc_id, display, profile, "ENCOUNTER",
                                False, event.event_id, identity=identity)

        npc_id = _required(data, "verified_npc_id")
        if not npc_id.startswith("npc:generated:"):
            raise FirstContactError("verified generic identity must be namespaced")
        proof_id = _required(data, "identity_proof_event_id")
        proof = _at_event(self.store, event_id=proof_id, branch_id=branch_id,
                          at_game_time=event.game_time)
        if proof.event_type != _PROOF_EVENT or proof.category != "CAMPAIGN_FACT" \
                or proof.seq >= event.seq:
            raise FirstContactError("invalid identity proof event")
        for name, expected in (("npc_id", npc_id), ("session_id", session),
                               ("scene_id", scene), ("actor_instance_token", actor_ref)):
            if not expected or proof.payload.get(name) != expected:
                raise FirstContactError("identity proof does not match observed target")
        if proof.payload.get("identity_state") != "VERIFIED":
            raise FirstContactError("identity must be positively verified")

        for prior in self.store.visible_events(branch_id, _ASSIGNMENT_EVENT):
            if prior.game_time is None or prior.game_time > at_game_time:
                continue
            if prior.payload.get("npc_id") == npc_id:
                snapshot = prior.payload["profile"]
                return FirstContact("READY", npc_id, display, snapshot, "PERSISTENT",
                                    False, event.event_id,
                                    identity=prior.payload.get("identity"))

        profile = generate_new_npc_profile(
            npc_id=npc_id, campaign_id=self.store.campaign_id,
            creation_branch_id=branch_id, world_seed=self.world_seed,
            npc_origin="CREATED", alignment_weights=self.weights)
        key = "spec006-personality:" + _digest(self.store.campaign_id, branch_id, npc_id)
        assignment, created = self.store.append_event(
            branch_id=branch_id, host_epoch=event.host_epoch,
            event_type=_ASSIGNMENT_EVENT, category="CAMPAIGN_FACT",
            game_time=event.game_time,
            payload={"npc_id": npc_id, "profile": profile,
                     "identity": identity_factory(npc_id) if identity_factory else None,
                     "identity_proof_event_id": proof.event_id,
                     "first_contact_event_id": event.event_id},
            evidence=event.evidence, idempotency_key=key,
            source_observation_id=event.event_id)
        return FirstContact("READY", npc_id, display, assignment.payload["profile"],
                            "PERSISTENT", created, event.event_id,
                            identity=assignment.payload.get("identity"))
