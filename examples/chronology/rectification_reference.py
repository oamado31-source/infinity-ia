"""DEC-104/C synthetic-only rectification planner: no I/O, host, LLM or mutations.

The 'registry', 'policy' and 'ledger' keys model separate trusted services ONLY
inside synthetic test fixtures. A production caller must resolve/authenticate them
independently, never from an untrusted request body.
"""
from __future__ import annotations
import copy
import hashlib
import json

_SCOPE = ('campaign_id', 'branch_id', 'lineage_id', 'build_fingerprint', 'modpack_hash')
_ACTIVE_PENDING = {'PROPOSED', 'QUEUED', 'RISK_VALIDATED', 'AUTHORIZED', 'READY'}
_DISPATCH = {'DISPATCHED', 'UNCERTAIN', 'ACK_UNKNOWN'}
_CONFIRMED = {'HOST_CONFIRMED', 'APPLIED'}
_DELIVERED = {'DELIVERED', 'KNOWLEDGE_ACQUIRED'}
_DERIVED = {'DERIVED_VIEW', 'PROJECTED', 'MATERIALIZED_VIEW'}
_KINDS = {'PROPOSAL', 'HOST_EFFECT', 'NEWS', 'KNOWLEDGE', 'VIEW'}

def _hash(*parts):
    value=json.dumps(parts, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    return 'SYN-' + hashlib.sha256(value.encode('ascii')).hexdigest()[:24]

def _out(status, reason, *, case_key=None, items=()):
    return {'status': status, 'reason_code': reason, 'case_key': case_key,
            'proposals': list(items), 'host_calls': 0, 'engine_writes': 0,
            'ledger_mutated': False, 'llm_calls': 0, 'npc_memories_changed': 0,
            'rumors_sent': 0, 'compensations_executed': 0}

def plan_synthetic(payload: dict) -> dict:
    """Produce a deterministic, *non-executing* containment/rectification plan."""
    f=copy.deepcopy(payload)
    if not isinstance(f,dict) or f.get('source_kind')!='SYNTHETIC_TEST':
        raise ValueError('Only synthetic fixture inputs are permitted')
    ctx,req,policy,reg,ledger=(f.get(k) for k in ('context','request','policy','rectification_registry','ledger'))
    if not all(isinstance(k,dict) for k in (ctx,req,policy,reg,ledger)):
        raise ValueError('Missing fixture sections')
    if ctx.get('fixture_only') is not True or ctx.get('host_mode')!='SYNTHETIC_HOST_FIXTURE':
        raise ValueError('Synthetic context only')
    if any(not isinstance(ctx.get(k),str) or not ctx[k] for k in _SCOPE):
        raise ValueError('Missing scope')
    if any(not ctx[k].startswith('SYN-') for k in ('build_fingerprint','modpack_hash')):
        raise ValueError('Real build not accepted')
    if any(type(ctx.get(k)) is not int or ctx[k]<0 for k in
           ('host_epoch','checkpoint_epoch','world_tick')):
        raise ValueError('Invalid epoch or clock')
    if not isinstance(req.get('operation_id'),str) or not req['operation_id'].startswith('SYN-'):
        raise ValueError('Synthetic operation ID required')
    if policy.get('trusted_kind')!='SYNTHETIC_POLICY_STORE' or policy.get('revision','')[:4]!='SYN-':
        return _out('BLOCKED_ACL','POLICY_NOT_TRUSTED')
    if req.get('purpose') not in policy.get('purposes',()) or req.get('audience') not in policy.get('audiences',()):
        return _out('BLOCKED_ACL','PURPOSE_OR_AUDIENCE_DENIED')
    if any(req.get('scope',{}).get(k)!=ctx[k] for k in _SCOPE):
        return _out('BLOCKED_ACL','REQUEST_SCOPE_MISMATCH')
    if reg.get('trusted_kind')!='SYNTHETIC_RECTIFICATION_REGISTRY' or reg.get('authenticated_fixture') is not True:
        return _out('QUARANTINED','RECTIFICATION_PROOF_UNTRUSTED')
    if req.get('rectification_ref')!=reg.get('rectification_id'):
        return _out('UNKNOWN','RECTIFICATION_REFERENCE_NOT_FOUND')
    if any(reg.get(k)!=ctx[k] for k in _SCOPE):
        return _out('QUARANTINED','RECTIFICATION_SCOPE_MISMATCH')
    if reg.get('host_epoch')!=ctx['host_epoch'] or reg.get('checkpoint_epoch')!=ctx['checkpoint_epoch']:
        return _out('QUARANTINED','RECTIFICATION_EPOCH_MISMATCH')
    if reg.get('source')!='DEC100_DEC101_DEC102_DEC103' or reg.get('state')!='RECTIFICATION_COMMITTED':
        return _out('QUARANTINED','RECTIFICATION_NOT_COMMITTED')
    if not isinstance(reg.get('root_admission_key'),str) or not reg['root_admission_key'].startswith('SYN-') or not isinstance(reg.get('revision'),str) or not reg['revision'].startswith('SYN-'):
        return _out('UNKNOWN','RECTIFICATION_IDENTITY_MISSING')
    if reg.get('classification') not in ('PUBLIC','PROTECTED'):
        return _out('QUARANTINED','UNKNOWN_SECRECY_CLASS')
    if reg['classification']=='PROTECTED' and policy.get('process_protected') is not True:
        return _out('BLOCKED_ACL','PROTECTED_CASE_DENIED')
    if type(reg.get('committed_at_tick')) is not int or reg['committed_at_tick'] > ctx['world_tick']:
        return _out('QUARANTINED','INVALID_RECTIFICATION_TIME')
    if ledger.get('trusted_kind')!='SYNTHETIC_CAUSAL_LEDGER':
        return _out('QUARANTINED','LEDGER_NOT_TRUSTED')
    if any(ledger.get(k)!=ctx[k] for k in _SCOPE):
        return _out('QUARANTINED','LEDGER_SCOPE_MISMATCH')
    if ledger.get('host_epoch')!=ctx['host_epoch'] or ledger.get('checkpoint_epoch')!=ctx['checkpoint_epoch']:
        return _out('QUARANTINED','LEDGER_EPOCH_MISMATCH')
    if req.get('expected_ledger_revision')!=ledger.get('revision'):
        return _out('QUARANTINED','CAS_REVISION_MISMATCH')
    if ledger.get('mapping_revision')!=reg.get('mapping_revision'):
        return _out('QUARANTINED','MAPPING_REVISION_MISMATCH')
    if any(x.get('status') in ('DISPATCHED','UNCERTAIN') for x in ledger.get('open_gateway_actions',())):
        return _out('QUARANTINED','OPEN_GATEWAY_ACTION_REQUIRES_RECONCILIATION')
    root=reg['root_admission_key']
    case_key=_hash(*(ctx[k] for k in _SCOPE), root, reg['revision'],reg.get('source_revision'))
    if case_key in ledger.get('planned_case_keys',()) or case_key in ledger.get('pending_case_keys',()):
        return _out('DUPLICATE_SUPPRESSED','CASE_ALREADY_PLANNED',case_key=case_key)
    nodes=ledger.get('nodes')
    if not isinstance(nodes,list) or len(nodes)>policy.get('max_nodes',0) or type(policy.get('max_nodes')) is not int:
        return _out('QUARANTINED','INVALID_GRAPH_SIZE')
    graph={}
    for n in nodes:
        if not isinstance(n,dict) or not isinstance(n.get('id'),str) or not n['id'].startswith('SYN-'):
            return _out('QUARANTINED','INVALID_NODE')
        if n['id'] in graph:
            return _out('QUARANTINED','DUPLICATE_GRAPH_NODE')
        if any(n.get(k)!=ctx[k] for k in _SCOPE):
            return _out('QUARANTINED','CROSS_SCOPE_GRAPH_NODE')
        if n.get('kind') not in _KINDS or n.get('state') not in (_ACTIVE_PENDING|_DISPATCH|_CONFIRMED|_DELIVERED|_DERIVED|{'REJECTED','EXPIRED','REVOKED'}):
            return _out('QUARANTINED','INVALID_NODE_KIND_OR_STATE')
        if not isinstance(n.get('parents'),list) or any(not isinstance(p,str) for p in n['parents']):
            return _out('QUARANTINED','INVALID_NODE_PARENTS')
        graph[n['id']]=n
    if root not in graph:
        return _out('UNKNOWN','ROOT_NOT_IN_CAUSAL_GRAPH')
    if graph[root]['kind']!='PROPOSAL' or graph[root]['parents']:
        return _out('QUARANTINED','INVALID_ROOT')
    # Dangling references are not interpreted as proof of no additional consequences.
    if any(parent not in graph for n in nodes for parent in n['parents']):
        return _out('QUARANTINED','INCOMPLETE_CAUSAL_GRAPH')
    children={k:[] for k in graph}
    for n in nodes:
        for parent in n['parents']:
            children[parent].append(n['id'])
    # Cycle detection is conservative across the entire supplied graph, including unvisited nodes.
    state={}
    def visit(k):
        if state.get(k)==1: return False
        if state.get(k)==2: return True
        state[k]=1
        for nxt in children[k]:
            if not visit(nxt):return False
        state[k]=2
        return True
    if not all(visit(k) for k in sorted(graph) if state.get(k)!=2):
        return _out('QUARANTINED','CYCLIC_GRAPH')
    seen=set()
    def descendants(k):
        for child in sorted(children[k]):
            if child not in seen:
                seen.add(child)
                descendants(child)
    descendants(root)
    if len(seen)>policy.get('max_descendants',-1):
        return _out('QUARANTINED','DESCENDANT_BUDGET_EXCEEDED')
    items=[]
    for node_id in sorted(seen):
        n=graph[node_id]
        kind,stage=n['kind'],n['state']
        if stage in _ACTIVE_PENDING:
            action='HOLD_FUTURE_DISPATCH'  # no host cancellation or resource release
        elif stage in _DISPATCH:
            action='RECONCILE_HOST_BEFORE_ANY_CHANGE'
        elif stage in _CONFIRMED:
            action='PROPOSE_AUTHORIZED_SAGA_COMPENSATION_REVIEW'
        elif stage in _DELIVERED:
            action='PROPOSE_CAUSAL_CORRECTION_DELIVERY'
        elif stage in _DERIVED:
            action='PROPOSE_VERSIONED_CAS_REBASE'
        else:
            action='PRESERVE_TERMINAL_HISTORY'
        # NEWS cannot be auto-undelivered; even pending information is only held.
        if kind in ('NEWS','KNOWLEDGE') and stage in _CONFIRMED:
            return _out('QUARANTINED','INCONSISTENT_KNOWLEDGE_STATE')
        if kind=='HOST_EFFECT' and stage in _DELIVERED:
            return _out('QUARANTINED','INCONSISTENT_HOST_EFFECT_STATE')
        items.append({'node_ref':_hash(case_key,node_id), 'proposed_action':action,
                      'requires_authorization': action in ('PROPOSE_AUTHORIZED_SAGA_COMPENSATION_REVIEW','PROPOSE_CAUSAL_CORRECTION_DELIVERY','PROPOSE_VERSIONED_CAS_REBASE'),
                      'requires_host_reconciliation': action=='RECONCILE_HOST_BEFORE_ANY_CHANGE'})
    return _out('PROPOSE_RECTIFICATION_PLAN','NO_EFFECTS_APPLIED',case_key=case_key,items=items)
