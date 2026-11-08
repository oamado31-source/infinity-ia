"""DEC-102/C: pure, synthetic-only quest/Living World reconciliation prototype.

Not a BG2:EE/EEex integration. No host reads/writes, network, LLM, or saves.
Inputs are intentionally fabricated fixtures; real attestations MUST be verified
outside this module by a trusted host/observer and authorization gateway.
"""
from __future__ import annotations
import copy
import hashlib
import json

_SCOPE = ('campaign_id', 'branch_id', 'session_id', 'build_fingerprint',
          'modpack_hash', 'mapping_revision', 'quest_key')
_UNCERTAIN = {'DISPATCHED', 'UNCERTAIN', 'DISPATCH_PENDING', 'ACK_UNKNOWN'}
_BAD = {'UNKNOWN', 'AMBIGUOUS', 'CONTRADICTORY', 'STALE', 'UNAVAILABLE',
        'BLOCKED_ACL', 'BLOCKED_BUILD', 'BLOCKED_MAPPING', 'BLOCKED_SPOILER'}


def _out(op, status, reason, *, proposals=(), receipt_required=False):
    """Minimal projection, deliberately NEVER returns quest flags or spoiler text."""
    return {'operation_id': str(op), 'status': status, 'reason_code': reason,
            'proposals': list(proposals), 'receipt_required': bool(receipt_required),
            'host_calls': 0, 'engine_writes': 0, 'llm_calls': 0,
            'host_state_mutated': False, 'overlay_state_mutated': False,
            'npc_knowledge_updated': False}


def _fingerprint(*parts):
    raw = json.dumps(parts, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    return 'SYN-' + hashlib.sha256(raw.encode('ascii')).hexdigest()[:20]


def reconcile_synthetic(payload: dict) -> dict:
    """Classify a conflict and propose safe *next steps*, never mutate anything."""
    p = copy.deepcopy(payload)
    if p.get('source_kind') != 'SYNTHETIC_TEST':
        raise ValueError('Only synthetic fixtures are accepted')
    context = p.get('context')
    if not isinstance(context, dict) or context.get('fixture_only') is not True \
       or context.get('host_mode') != 'SYNTHETIC_HOST_FIXTURE':
        raise ValueError('Requires explicit synthetic host context')
    for key in _SCOPE:
        if not isinstance(context.get(key), str) or not context[key]:
            raise ValueError('Missing scope ' + key)
    for key in ('build_fingerprint', 'modpack_hash', 'mapping_revision'):
        if not context[key].startswith('SYN-'):
            raise ValueError('Only synthetic build/mapping versions supported')
    for key in ('host_epoch', 'checkpoint_epoch', 'snapshot_tick'):
        if type(context.get(key)) is not int or context[key] < 0:
            raise ValueError('Invalid epoch ' + key)
    request = p.get('request')
    if not isinstance(request, dict) or not isinstance(request.get('operation_id'), str):
        raise ValueError('Invalid request')
    op = request['operation_id']
    if not op.startswith('SYN-'):
        raise ValueError('Only synthetic operation ids supported')
    policy, host, overlay, ledger, mapping = (p.get(k) for k in
        ('policy', 'host', 'overlay', 'ledger', 'mapping'))
    if not all(isinstance(x, dict) for x in (policy, host, overlay, ledger, mapping)):
        raise ValueError('All trusted synthetic fixture sections required')
    # In real implementation these data are read from separate trusted stores.
    if policy.get('trusted_kind') != 'SYNTHETIC_POLICY_FIXTURE' or not str(policy.get('revision', '')).startswith('SYN-'):
        return _out(op, 'BLOCKED_ACL', 'POLICY_NOT_TRUSTED')
    if request.get('purpose') not in policy.get('purposes', ()) or request.get('audience') not in policy.get('audiences', ()):
        return _out(op, 'BLOCKED_ACL', 'RECIPIENT_OR_PURPOSE_DENIED')
    if any(request.get('scope', {}).get(k) != context[k] for k in _SCOPE):
        return _out(op, 'BLOCKED_ACL', 'REQUEST_SCOPE_MISMATCH')
    if ledger.get('trusted_kind') != 'SYNTHETIC_LEDGER_FIXTURE':
        return _out(op, 'QUARANTINED', 'LEDGER_UNTRUSTED')
    for source, label in ((host, 'HOST'), (overlay, 'OVERLAY'), (ledger, 'LEDGER')):
        if any(source.get(k) != context[k] for k in _SCOPE):
            return _out(op, 'QUARANTINED', label + '_SCOPE_MISMATCH')
    if host.get('source_kind') != 'SYNTHETIC_HOST_OBSERVATION' or host.get('authenticated_fixture') is not True:
        return _out(op, 'QUARANTINED', 'HOST_EVIDENCE_UNVERIFIED')
    if overlay.get('source_kind') != 'SYNTHETIC_OVERLAY_SNAPSHOT' or overlay.get('trusted_fixture') is not True:
        return _out(op, 'QUARANTINED', 'OVERLAY_EVIDENCE_UNVERIFIED')
    if mapping.get('trusted_kind') != 'SYNTHETIC_CURATED_MAPPING' or mapping.get('review_status') != 'CURATED_SYNTHETIC':
        return _out(op, 'BLOCKED_MAPPING', 'MAPPING_NOT_CURATED')
    if any(mapping.get(k) != context[k] for k in ('build_fingerprint', 'modpack_hash', 'mapping_revision', 'quest_key')):
        return _out(op, 'BLOCKED_MAPPING', 'MAPPING_VERSION_MISMATCH')
    if host.get('host_epoch') != context['host_epoch'] or host.get('checkpoint_epoch') != context['checkpoint_epoch']:
        return _out(op, 'QUARANTINED', 'HOST_EPOCH_MISMATCH')
    if ledger.get('host_epoch') != context['host_epoch'] or ledger.get('checkpoint_epoch') != context['checkpoint_epoch']:
        return _out(op, 'QUARANTINED', 'LEDGER_EPOCH_MISMATCH')
    if type(host.get('observed_tick')) is not int or host['observed_tick'] > context['snapshot_tick']:
        return _out(op, 'QUARANTINED', 'INVALID_OBSERVATION_TIME')
    max_age = policy.get('max_age_ticks')
    if type(max_age) is not int or max_age < 0 or context['snapshot_tick']-host['observed_tick'] > max_age:
        return _out(op, 'UNKNOWN', 'STALE_OBSERVATION')
    if host.get('coverage') != 'FULL_FOR_SEMANTIC_PROOF':
        return _out(op, 'UNKNOWN', 'INSUFFICIENT_COVERAGE')
    if host.get('semantic_status') in _BAD or host.get('semantic_status') != 'MAPPED_MINIMAL':
        return _out(op, 'UNKNOWN', 'UNRELIABLE_SEMANTICS')
    if not str(host.get('semantic_id', '')).startswith('SYN-') or not str(host.get('proof_id', '')).startswith('SYN-'):
        return _out(op, 'UNKNOWN', 'PROOF_MISSING')
    if str(overlay.get('revision', '')).startswith('SYN-') is False:
        return _out(op, 'QUARANTINED', 'OVERLAY_REVISION_MISSING')
    if overlay.get('host_epoch') != context['host_epoch'] or overlay.get('checkpoint_epoch') != context['checkpoint_epoch']:
        # Preserve the old branch's ledger. No global rollback/merge.
        return _out(op, 'RESTORE_REVIEW_REQUIRED', 'SAVED_TIMELINE_DIVERGED',
                    proposals=('FORK_OR_RESCOPE_OVERLAY_AFTER_REVIEW',))
    actions = ledger.get('actions')
    if not isinstance(actions, list):
        return _out(op, 'QUARANTINED', 'INVALID_LEDGER')
    if any(a.get('dispatch_state') in _UNCERTAIN for a in actions if isinstance(a, dict)):
        return _out(op, 'QUARANTINED', 'PENDING_HOST_RECEIPTS',
                    proposals=('REQUEST_RECEIPT_RECONCILIATION',), receipt_required=True)
    if any(not isinstance(a, dict) or a.get('dispatch_state') not in ('HOST_CONFIRMED', 'NOT_DISPATCHED', 'REJECTED') for a in actions):
        return _out(op, 'QUARANTINED', 'UNRECOGNIZED_DISPATCH_STATE')
    previous = overlay.get('semantic_id')
    current = host['semantic_id']
    if not str(previous).startswith('SYN-'):
        return _out(op, 'UNKNOWN', 'OVERLAY_MILESTONE_UNKNOWN')
    allowed = mapping.get('allowed_transitions', ())
    if not isinstance(allowed, list):
        return _out(op, 'BLOCKED_MAPPING', 'INVALID_TRANSITION_CATALOG')
    transitions = {(t.get('from'), t.get('to')) for t in allowed if isinstance(t, dict)}
    if previous == current:
        return _out(op, 'CONSISTENT', 'SAME_SEMANTIC_MILESTONE')
    if (previous, current) not in transitions:
        return _out(op, 'QUARANTINED', 'UNEXPLAINED_SEMANTIC_DIVERGENCE',
                    proposals=('REQUEST_CAUSAL_REVIEW',))
    # It is *only* a proposal to update a DERIVED VIEW, requiring a separately
    # trusted approval. Never rewrites the event ledger or the engine state.
    if overlay.get('revision') != request.get('expected_overlay_revision'):
        return _out(op, 'QUARANTINED', 'OPTIMISTIC_REVISION_CONFLICT')
    proposal_id = _fingerprint(op, context['campaign_id'], context['branch_id'],
                   context['host_epoch'], context['checkpoint_epoch'], previous,
                   current, host['proof_id'], overlay['revision'])
    return _out(op, 'PROPOSE_DERIVED_VIEW_REBASE', 'CURATED_TRANSITION_VERIFIED',
                proposals=(proposal_id, 'REQUIRE_AUTHORIZED_CAS_COMMIT'))
