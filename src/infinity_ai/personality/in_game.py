# SPDX-License-Identifier: Apache-2.0
"""SPEC-006 + ADR-0116: the in-game box (`INFAI-TALK`) as the trusted dialogue-start observation.

The probe reports the creature under the cursor when the player sends text in the box. That
observation becomes one `NpcDialogueStarted` event (no player text) for `FirstContactService`:

- a creature with a script name is an individual authored by the game: `CANONICAL`, so no
  profile is generated (its curated persona belongs to SPEC-005; until then it speaks plainly);
- a creature without one is `CANDIDATE`: a temporary encounter profile, stable for that
  instance in the same session and area (the engine object id is the scene-unique token).

Nothing here proves a persistent identity (ADR-0061/0062); `VERIFIED` is never produced.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping

from ..bridge.talk import TalkRequest
from ..state.store import CampaignStore, Event
from .first_contact import FirstContactError, FirstContactService

CONTACT_EVENT = 'NpcDialogueStarted'


def resolve_speaker(req: TalkRequest, residents: Mapping[str, object]) -> str | None:
    """NPC id of the speaker. A creature without a script name is matched by its CRE file; a
    saved game reports it as '*' + the resref minus its first letter, so it is matched against
    the residents of the current area and only when exactly one fits."""
    if req.speaker_id:
        return req.speaker_id
    cre, area = req.speaker_cre, (req.area or '').upper()
    if not cre or not cre.startswith('*') or len(cre) < 2:
        return None
    fits = sorted(r.npc_id for r in residents.values()
                  if not getattr(r, 'script_name', '') and r.cre_resref[1:].upper() == cre[1:]
                  and len(r.cre_resref) == len(cre)
                  and area in {a.upper() for a in getattr(r, 'areas', ())})
    return fits[0] if len(fits) == 1 else None


def record_dialogue_start(store: CampaignStore, branch_id: str, req: TalkRequest, *,
                          game_time: int, speaker_id: str | None = None,
                          evidence: str = 'LAB_OBSERVED') -> Event:
    """One idempotent observation per box request; the payload carries no text."""
    instance = f'{req.area}#{req.speaker_instance}' if req.speaker_instance is not None \
        and req.area else None
    payload = {
        'req_id': req.req_id, 'speaker_id': speaker_id or req.speaker_id,
        'speaker_name': req.speaker_name,
        'cre': req.speaker_cre, 'input': req.input,
        'dialogue_started': True, 'target_visible': not req.speaker_dead, 'access_allowed': True,
        'session_id': f'session-{req.session_seq}', 'scene_id': req.area,
        'actor_instance_token': instance,
        'token_uniqueness': 'SCENE_VERIFIED' if instance else 'NONE',
        'role': 'OTHER', 'identity_state': 'CANONICAL' if req.speaker_script else 'CANDIDATE',
    }
    with store.transaction():
        event, _ = store.append_event(
            branch_id=branch_id, host_epoch=req.session_seq, event_type=CONTACT_EVENT,
            category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
            evidence=evidence, idempotency_key=f'talk-start|{branch_id}|{req.req_id}')
    return event


def profile_for(store: CampaignStore, branch_id: str, event: Event, *, at_game_time: int,
                world_seed: str, identity_factory: Callable[[str], dict] | None = None
                ) -> tuple[dict | None, str, dict | None]:
    """(profile, scope/reason, generated identity): ENCOUNTER profile with a background from
    `identity_factory` (ADR-0117), CANONICAL (neither) or a refusal."""
    try:
        contact = FirstContactService(store, world_seed=world_seed).begin(
            contact_event_id=event.event_id, branch_id=branch_id, at_game_time=at_game_time,
            identity_factory=identity_factory)
    except FirstContactError as exc:
        return None, f'NO_PROFILE:{exc}', None
    if contact.status != 'READY':
        return None, contact.scope, None
    return contact.profile, contact.scope, contact.identity
