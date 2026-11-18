# SPDX-License-Identifier: Apache-2.0
"""ADR-0136 (gate P3): the first write to the game, through a minimal gateway (DEC-012, ADR-0022).

Two operations only, both validated by code and confirmed by the host:
- SPAWN_CREATURE: one of OUR creature files (`IA*.CRE`, deployed to override with the game closed,
  whose script-name field holds a name of ours, `INFAI_*`), in the area the party is in, at a point
  or near the party leader. BG2:EE's CreateCreature takes no script name (ACTION.IDS: resref, point,
  facing): ownership lives in the file (lab, 2026-11-18);
- DESPAWN: only creatures with one of our script names (ADR-0094, ADR-0068).

The request goes to the game as `override/INFAIACT.lua`: one table of validated literals, never
text to execute. The EEex module (`tools/eeex-probe/M_INFAIA.lua`) builds the engine action from a
fixed template and answers in the log (`INFAI-ACT {json}`), counting our creatures with that name in
the area before and after. One more (SPAWN) or none left (DESPAWN) is the host's confirmation; without it nothing counts as done, and nothing is resent
blindly. In this gate only the maintainer dispatches, by a lab command (D2).
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from ..bridge.talk import lua_string
from ..state.store import CampaignStore

ACT_RESREF = 'INFAIACT'
ACT_PREFIX = 'INFAI-ACT '
ACT_SCHEMA = 'infinity-ai.act.v1'
SPAWN, DESPAWN = 'SPAWN_CREATURE', 'DESPAWN'
OPERATIONS = (SPAWN, DESPAWN)
OWN_PREFIX = 'INFAI_'
POLICY = 'adr-0136-gate-p3-v1'
REQUESTED, CONFIRMED, FAILED = 'GameActionRequested', 'GameActionConfirmed', 'GameActionFailed'
ACCEPTED, DONE, REFUSED = 'ACCEPTED', 'DONE', 'REFUSED'
STATUSES = (ACCEPTED, DONE, REFUSED)
PLACEHOLDER_ACT = 'INFAI_ACT_Request = {action_id = ""}\n'
"""Kept in override/ at all times (present at launch); an empty id means nothing to do."""

_ID = re.compile(r'[a-z0-9]{10}')
_CRE = re.compile(r'[A-Z0-9_#-]{1,8}')
_AREA = re.compile(r'[A-Z0-9]{1,8}')
_NAME = re.compile(r'INFAI_[A-Z0-9_]{1,26}')
_TEMPLATE = re.compile(r'IA[A-Z0-9]{1,6}')
TEMPLATES_SCHEMA = 'infinity-ai.creature-templates.v1'
DEFAULT_TEMPLATE_DIR = Path.home() / '.infinity-ai' / 'templates'
CRE_SCRIPT_NAME = (0x280, 32)       # CRE V1.0: the script name (death variable) field
CRE_STATUS = 0x20                   # CRE V1.0: STATE.IDS flags
DEATH_STATES = 0x00000FC0           # dead, stone, frozen, exploding... (lab: DPMALE is a corpse)
_REASON = re.compile(r'[A-Z_]{1,32}')
MAX_COORD = 32767


class ActionError(ValueError):
    """A request the gateway refuses before it reaches the game (the code says why)."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ActionRequest:
    action_id: str
    op: str
    area: str
    name: str                 # our script name: of the creature to create, or to remove
    cre: str = ''             # SPAWN only: one of our creature files (IA*)
    x: int = -1               # -1: near the party leader
    y: int = -1
    facing: int = 0


def new_action_id() -> str:
    return uuid.uuid4().hex[:10]


def make_template(source: bytes, script_name: str) -> bytes:
    """One of our creature files: a CRE of the build with a script name of ours. Local only: the
    bytes are game data (CR-2026-030) and go to the VM's override, never to the repository."""
    if not _NAME.fullmatch(script_name or ''):
        raise ActionError('NOT_OURS')
    offset, size = CRE_SCRIPT_NAME
    if source[:8] != b'CRE V1.0' or len(source) < offset + size:
        raise ActionError('BAD_SOURCE_CRE')
    if int.from_bytes(source[CRE_STATUS:CRE_STATUS + 4], 'little') & DEATH_STATES:
        raise ActionError('DEAD_SOURCE_CRE')   # it would be created as a corpse, never counted
    data = bytearray(source)
    data[offset:offset + size] = script_name.encode('ascii').ljust(size, b'\0')
    return bytes(data)


def spawn_request(cre: str, area: str, *, x: int = -1, y: int = -1, facing: int = 0,
                  templates: dict[str, str], action_id: str | None = None) -> ActionRequest:
    """A valid SPAWN_CREATURE, or ActionError. `templates`: our creature files deployed in this
    build (resref -> the script name inside the file)."""
    cre, area = (cre or '').upper(), (area or '').upper()
    action_id = action_id or new_action_id()
    if not _ID.fullmatch(action_id):
        raise ActionError('BAD_ACTION_ID')
    if not _CRE.fullmatch(cre):
        raise ActionError('BAD_CRE')
    if not _TEMPLATE.fullmatch(cre):
        raise ActionError('NOT_OUR_TEMPLATE')
    if cre not in templates or not _NAME.fullmatch(templates[cre]):
        raise ActionError('UNKNOWN_TEMPLATE')
    if not _AREA.fullmatch(area):
        raise ActionError('BAD_AREA')
    for value in (x, y):
        if isinstance(value, bool) or not isinstance(value, int) or not -1 <= value <= MAX_COORD:
            raise ActionError('BAD_POINT')
    if (x < 0) != (y < 0):
        raise ActionError('BAD_POINT')
    if isinstance(facing, bool) or not isinstance(facing, int) or not 0 <= facing <= 15:
        raise ActionError('BAD_FACING')
    return ActionRequest(action_id, SPAWN, area, templates[cre], cre, x, y, facing)


def despawn_request(name: str, area: str, *, owned: set[str] | frozenset[str],
                    action_id: str | None = None) -> ActionRequest:
    """A valid DESPAWN of one of our creatures, or ActionError."""
    area = (area or '').upper()
    action_id = action_id or new_action_id()
    if not _ID.fullmatch(action_id):
        raise ActionError('BAD_ACTION_ID')
    name = (name or '').upper() if isinstance(name, str) else ''
    if not _NAME.fullmatch(name):
        raise ActionError('NOT_OURS')
    if name not in {n.upper() for n in owned}:
        raise ActionError('NOT_OWNED')
    if not _AREA.fullmatch(area):
        raise ActionError('BAD_AREA')
    return ActionRequest(action_id, DESPAWN, area, name)


def render_request(req: ActionRequest) -> str:
    """Contents of `override/INFAIACT.lua`: escaped literals only (like INFAIRSP.lua)."""
    if req.op not in OPERATIONS or not _ID.fullmatch(req.action_id) \
            or not _NAME.fullmatch(req.name) or not _AREA.fullmatch(req.area) \
            or (req.op == SPAWN and not _TEMPLATE.fullmatch(req.cre)):
        raise ActionError('BAD_REQUEST')
    return ('INFAI_ACT_Request = {'
            f'action_id = {lua_string(req.action_id)}, op = {lua_string(req.op)}, '
            f'area = {lua_string(req.area)}, name = {lua_string(req.name)}, '
            f'cre = {lua_string(req.cre)}, x = {int(req.x)}, y = {int(req.y)}, '
            f'facing = {int(req.facing)}}}\n')


@dataclass(frozen=True)
class ActionReceipt:
    action_id: str
    status: str               # ACCEPTED (queued), DONE (checked), REFUSED
    observed: int | None      # how many creatures with our name the area holds after the action
    reason: str | None = None
    before: int | None = None  # how many it held before (DONE)


def parse_receipt(line: str) -> ActionReceipt | None:
    """One `INFAI-ACT {json}` log line, strictly; anything else is None (logs are untrusted)."""
    index = line.find(ACT_PREFIX)
    if index < 0:
        return None
    try:
        doc = json.loads(line[index + len(ACT_PREFIX):].strip())
    except ValueError:
        return None
    if not isinstance(doc, dict) or doc.get('schema') != ACT_SCHEMA:
        return None
    action_id, status = doc.get('action_id'), doc.get('status')
    observed, reason, before = doc.get('observed'), doc.get('reason'), doc.get('before')
    if not isinstance(action_id, str) or not _ID.fullmatch(action_id) or status not in STATUSES:
        return None
    for count in (observed, before):
        if count is not None and (isinstance(count, bool) or not isinstance(count, int)
                                  or not 0 <= count <= 99):
            return None
    if reason is not None and (not isinstance(reason, str) or not _REASON.fullmatch(reason)):
        return None
    return ActionReceipt(action_id, status, observed, reason, before)


def parse_receipts(text: str) -> list[ActionReceipt]:
    return [r for r in map(parse_receipt, text.splitlines()) if r is not None]


def confirmed(req: ActionRequest, receipt: ActionReceipt) -> bool:
    """The host's word that the action happened: one more of ours (SPAWN), or none left."""
    if receipt.action_id != req.action_id or receipt.status != DONE or receipt.observed is None:
        return False
    if req.op == SPAWN:
        return receipt.before is not None and receipt.observed == receipt.before + 1
    return receipt.observed == 0


def record_requested(store: CampaignStore, branch_id: str, req: ActionRequest, *,
                     game_time: int | None, host_epoch: int = 0,
                     evidence: str = 'LAB_OBSERVED') -> None:
    """Every action is placed on the game's timeline: without the game time an older save would
    inherit it (a branch admits earlier events that carry no time; lab, S1x)."""
    if isinstance(game_time, bool) or not isinstance(game_time, int) or game_time < 0:
        raise ActionError('NO_GAME_TIME')
    payload = {'action_id': req.action_id, 'op': req.op, 'area': req.area, 'name': req.name,
               'cre': req.cre, 'policy': POLICY}
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=host_epoch, event_type=REQUESTED,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
                           evidence=evidence, idempotency_key=f'act|{req.action_id}|requested')


def record_result(store: CampaignStore, branch_id: str, req: ActionRequest,
                  receipt: ActionReceipt | None, *, game_time: int | None, host_epoch: int = 0,
                  evidence: str = 'LAB_OBSERVED') -> str:
    """CONFIRMED with the host's word; FAILED with a refusal; nothing recorded while uncertain.
    Returns the gateway state: HOST_CONFIRMED, DENIED or UNCERTAIN."""
    if receipt is not None and confirmed(req, receipt):
        event_type, state = CONFIRMED, 'HOST_CONFIRMED'
    elif receipt is not None and receipt.status == REFUSED:
        event_type, state = FAILED, 'DENIED'
    else:
        return 'UNCERTAIN'
    payload = {'action_id': req.action_id, 'op': req.op, 'area': req.area, 'name': req.name,
               'cre': req.cre, 'observed': receipt.observed, 'before': receipt.before,
               'reason': receipt.reason,
               'policy': POLICY}
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=host_epoch, event_type=event_type,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time, payload=payload,
                           evidence=evidence, idempotency_key=f'act|{req.action_id}|result')
    return state


def owned_creatures(store: CampaignStore, branch_id: str) -> dict[str, str]:
    """Our creatures this branch confirms as present: script name -> area. An action without the
    game time cannot be placed on the timeline, so it does not count (lab, S1x)."""
    out: dict[str, str] = {}
    for event in store.visible_events(branch_id, CONFIRMED):
        if event.game_time is None:
            continue
        p = event.payload
        if p.get('op') == SPAWN:
            out[p['name']] = p['area']
        elif p.get('op') == DESPAWN:
            out.pop(p['name'], None)
    return out


def templates_path(build_fingerprint: str, base: Path = DEFAULT_TEMPLATE_DIR) -> Path:
    digest = build_fingerprint.split(':', 1)[-1][:16].lower()
    return Path(base) / f'install-{digest}' / 'templates.json'


def load_templates(build_fingerprint: str, base: Path = DEFAULT_TEMPLATE_DIR) -> dict[str, str]:
    """Our creature files deployed for this build: resref -> script name inside the file."""
    path = templates_path(build_fingerprint, base)
    try:
        doc = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    if doc.get('schema') != TEMPLATES_SCHEMA or doc.get('build_fingerprint') != build_fingerprint:
        return {}
    return {t['resref']: t['script_name'] for t in doc.get('templates', [])
            if _TEMPLATE.fullmatch(t.get('resref', '')) and _NAME.fullmatch(t.get('script_name', ''))}
