"""DEC-099/C. Deterministic, PURE SYNTHETIC ownership preflight. NO BG2/EEex IPC.

No engine calls, file writes, script edits, external imports, or runtime authority.
The string 'SYNTHETIC_VERIFIED' in a fixture is not real POC evidence.
"""
from __future__ import annotations
import copy
import hashlib
import json

PROTECTED_FIELDS = frozenset({
    'quest_flag', 'global_var', 'area_script', 'npc_script', 'ai_script',
    'dialogue_state', 'romance_state', 'banter', 'cutscene_state',
    'player_inventory', 'third_party_inventory', 'script_trigger',
    'kill_revive', 'character_control', 'plot_teleport', 'quest_reward'
})
OWNERS = frozenset({'ENGINE_NATIVE', 'QUEST_SCRIPT', 'THIRD_PARTY_MOD',
                    'PLAYER', 'INFINITY_AI', 'UNKNOWN'})
KEYS = ('campaign_id', 'branch_id', 'region_id', 'host_epoch',
        'checkpoint_epoch', 'build_fingerprint', 'modpack_hash',
        'adapter_revision', 'rule_revision')
PENDING = frozenset({'PREPARED', 'DISPATCHED', 'UNCERTAIN'})


def _hash(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def preflight_ownership_synthetic(payload: dict) -> dict:
    """Fail-closed preview; NEVER sends or performs a mechanical action."""
    p = copy.deepcopy(payload)
    c = p.get('context', {})
    if p.get('source_kind') != 'SYNTHETIC_TEST' or c.get('fixture_only') is not True:
        raise ValueError('Only synthetic fixtures are supported')
    for key in KEYS:
        if key not in c or c[key] is None or c[key] == '':
            raise ValueError('Missing scope: ' + key)
    if not isinstance(c['host_epoch'], int) or isinstance(c['host_epoch'], bool):
        raise ValueError('host_epoch must be integer')
    if not isinstance(c['checkpoint_epoch'], int) or isinstance(c['checkpoint_epoch'], bool):
        raise ValueError('checkpoint_epoch must be integer')
    if not str(c['build_fingerprint']).startswith('SYN-') or not str(c['modpack_hash']).startswith('SYN-'):
        raise ValueError('This reference only accepts synthetic build fingerprints')
    if c.get('observation_coverage') not in ('FULL_SYNTHETIC', 'PARTIAL', 'UNKNOWN'):
        raise ValueError('Invalid synthetic observation coverage')
    if c.get('host_mode') != 'SYNTHETIC_HOST_FIXTURE':
        raise ValueError('No real host binding supported')
    for name in ('claims', 'intents', 'capabilities'):
        if not isinstance(p.get(name), list):
            raise ValueError(name + ' must be a list')
    if not isinstance(p.get('pending_actions', []), list):
        raise ValueError('pending_actions must be list')

    claims = {}
    for rec in p['claims']:
        if rec.get('owner_kind') not in OWNERS:
            raise ValueError('Unrecognized ownership category')
        pid = rec.get('persistent_id')
        if not isinstance(pid, str) or not pid:
            raise ValueError('Missing persistent_id')
        claims.setdefault(pid, []).append(rec)
    intents = {}
    for intent in p['intents']:
        iid = intent.get('intent_id')
        if not isinstance(iid, str) or not iid or iid in intents:
            raise ValueError('Missing/duplicate intent_id')
        intents[iid] = intent
    pending = set()
    for item in p.get('pending_actions', []):
        if item.get('state') in PENDING:
            pending.add(item.get('persistent_id'))
    capabilities = set()
    for cap in p['capabilities']:
        # Synthetic verification means test *fixture* only, never runtime EEex POC.
        if cap.get('validation') == 'SYNTHETIC_VERIFIED':
            if (cap.get('build_fingerprint') == c['build_fingerprint'] and
                cap.get('modpack_hash') == c['modpack_hash'] and
                cap.get('adapter_revision') == c['adapter_revision']):
                capabilities.add((cap.get('action_type'), cap.get('field_id')))

    decisions = []
    for iid, it in sorted(intents.items()):
        pid = it.get('persistent_id')
        operation = it.get('action_type')
        field = it.get('field_id')
        recs = claims.get(pid, [])
        decision = {'intent_id': iid, 'persistent_id': pid}

        def result(status, reason):
            decision['status'] = status
            decision['reason_code'] = reason

        if not isinstance(pid, str) or not pid or operation not in {'PATCH', 'CREATE', 'RETIRE'} or not isinstance(field, str) or not field:
            result('BLOCKED_CAPABILITY', 'INVALID_INTENT')
        elif any(it.get(k) != c[k] for k in KEYS):
            result('HOLD_RECONCILE', 'SCOPE_OR_REVISION_MISMATCH')
        elif pid in pending:
            result('HOLD_RECONCILE', 'PENDING_OR_UNCERTAIN_HOST_ACTION')
        elif field in PROTECTED_FIELDS:
            result('BLOCKED_PROTECTED_FIELD', 'PROTECTED_ENGINE_OR_PLAYER_FIELD')
        elif len(recs) > 1:
            result('ESCALATE_CONFLICT', 'COMPETING_OWNERSHIP_CLAIMS')
        elif recs and (recs[0].get('owner_kind') != 'INFINITY_AI' or
                       recs[0].get('runtime_custodian') != 'INFINITY_AI'):
            result('BLOCKED_OWNERSHIP', 'NOT_IN_INFINITY_AI_CUSTODY')
        elif recs and (recs[0].get('owner_receipt_id', '').startswith('SYN-RECEIPT-') is False or
                       recs[0].get('instance_generation', 0) < 1):
            result('HOLD_RECONCILE', 'MISSING_INSTANCE_OWNER_EVIDENCE')
        elif recs and (recs[0].get('instance_id') != it.get('instance_id') or
                       recs[0].get('owner_revision') != it.get('expected_owner_revision')):
            result('HOLD_RECONCILE', 'RECYCLED_INSTANCE_OR_STALE_OWNER_REVISION')
        elif it.get('authorized') is not True:
            result('BLOCKED_AUTHORIZATION', 'NO_EXPRESS_AUTHORIZATION')
        elif it.get('risk') == 'HIGH':
            result('BLOCKED_RISK', 'HIGH_RISK_NEEDS_ADDITIONAL_GATES')
        elif (operation, field) not in capabilities:
            result('BLOCKED_CAPABILITY', 'NO_MATCHING_SYNTHETIC_CAPABILITY')
        elif operation == 'CREATE':
            if recs:
                result('HOLD_RECONCILE', 'INSTANCE_ALREADY_HAS_OWNER_RECORD')
            elif c['observation_coverage'] != 'FULL_SYNTHETIC':
                result('HOLD_RECONCILE', 'INSUFFICIENT_ABSENCE_OBSERVATION')
            elif it.get('owner_kind') != 'INFINITY_AI' or not str(it.get('template_id', '')).startswith('SYN-TEMPLATE-'):
                result('BLOCKED_OWNERSHIP', 'CREATE_NAMESPACE_OR_TEMPLATE_NOT_ALLOWLISTED')
            else:
                result('PROPOSE_OWNED_CREATE', 'SYNTHETIC_PREFLIGHT_ONLY')
        elif not recs:
            result('HOLD_RECONCILE', 'NO_OWNER_RECORD')
        elif field not in recs[0].get('allowed_fields', []):
            result('BLOCKED_OWNERSHIP', 'FIELD_AUTHORITY_MISSING')
        elif operation == 'RETIRE':
            if recs[0].get('retire_eligible') is True:
                result('REVIEW_RETIRE', 'NEVER_DELETE_WITHOUT_HOST_APPROVAL')
            else:
                result('PRESERVE_READ_ONLY', 'LIFECYCLE_NOT_RETIRE_ELIGIBLE')
        elif operation == 'PATCH':
            if it.get('desired_state') == recs[0].get('host_confirmed_state'):
                result('NO_OP', 'CONFIRMED_STATE_ALREADY_MATCHES')
            else:
                result('PROPOSE_OWNED_PATCH', 'SYNTHETIC_PREFLIGHT_ONLY')
        else:
            result('BLOCKED_CAPABILITY', 'NO_SUPPORTED_ACTION')
        decisions.append(decision)
    out = {'status': 'PREVIEW_ONLY', 'host_calls': 0, 'engine_mutations': 0,
           'campaign_id': c['campaign_id'], 'branch_id': c['branch_id'],
           'decisions': decisions,
           'warning': 'SYNTHETIC ONLY: no verified EEex build, host receipts or multiplayer engine actions.'}
    out['decision_hash'] = _hash(out)
    return out
