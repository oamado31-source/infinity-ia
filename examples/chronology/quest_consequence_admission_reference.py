"""DEC-103/C: pure, strictly synthetic milestone admission *proposal* evaluator.

NO BG2:EE, EEex, host, LLM, network, save, file, or NPC integration. The
caller supplies independently sourced *synthetic fixture sections* only.
Production MUST retrieve and authenticate all trusted stores separately.
"""
from __future__ import annotations

import copy
import hashlib
import json

_SCOPE = ('campaign_id','branch_id','quest_key','build_fingerprint',
          'modpack_hash','mapping_revision','lineage_id')
_UNCERTAIN = {'DISPATCHED', 'UNCERTAIN', 'DISPATCH_PENDING', 'ACK_UNKNOWN'}
_SUPPORTED_RISKS = {'LOW', 'MEDIUM', 'HIGH'}


def _digest(*parts):
    b = json.dumps(parts, separators=(',', ':'), sort_keys=True, ensure_ascii=True)
    return 'SYN-' + hashlib.sha256(b.encode('ascii')).hexdigest()[:24]


def _result(status, reason, *, key=None, proposals=(), pending=False):
    return {'status': status, 'reason_code': reason, 'admission_key': key,
            'proposals': list(proposals), 'requires_reconciliation': pending,
            'engine_writes': 0, 'host_calls': 0, 'llm_calls': 0,
            'ledger_mutated': False, 'npc_knowledge_updated': False,
            'messages_sent': 0, 'effects_confirmed': 0}


def evaluate_synthetic(payload: dict) -> dict:
    """Return a possible admission/outbox plan; NEVER commit or distribute it."""
    p = copy.deepcopy(payload)
    if not isinstance(p, dict) or p.get('source_kind') != 'SYNTHETIC_TEST':
        raise ValueError('Synthetic test inputs only')
    ctx, request, policy, proof, catalog, ledger = (p.get(x) for x in
        ('context', 'request', 'policy', 'proof_registry', 'catalog', 'ledger'))
    if not all(isinstance(x, dict) for x in (ctx,request,policy,proof,catalog,ledger)):
        raise ValueError('Missing synthetic test sections')
    if ctx.get('fixture_only') is not True or ctx.get('host_mode') != 'SYNTHETIC_HOST_FIXTURE':
        raise ValueError('Synthetic context required')
    if any(not isinstance(ctx.get(k), str) or not ctx[k] for k in _SCOPE):
        raise ValueError('Incomplete identifiers')
    if any(not ctx[k].startswith('SYN-') for k in ('build_fingerprint','modpack_hash','mapping_revision')):
        raise ValueError('Not synthetic build')
    if any(type(ctx.get(k)) is not int or ctx[k] < 0
           for k in ('host_epoch','checkpoint_epoch','world_tick','dr_year','dr_month')):
        raise ValueError('Invalid clock or epoch')
    if ctx['dr_month'] < 1 or ctx['dr_month'] > 12 or not isinstance(ctx.get('region_id'),str):
        raise ValueError('Invalid region/date')
    op=request.get('operation_id')
    if not isinstance(op,str) or not op.startswith('SYN-'):
        raise ValueError('Synthetic operation ID required')
    # These sections represent independently trusted stores ONLY in the fixture.
    if policy.get('trusted_kind') != 'SYNTHETIC_POLICY_STORE' or not str(policy.get('revision','')).startswith('SYN-'):
        return _result('BLOCKED_ACL', 'POLICY_NOT_TRUSTED')
    if request.get('purpose') not in policy.get('purposes',()) or request.get('audience') not in policy.get('audiences',()):
        return _result('BLOCKED_ACL', 'PURPOSE_OR_AUDIENCE_DENIED')
    if any(request.get('scope',{}).get(k) != ctx[k] for k in _SCOPE):
        return _result('BLOCKED_ACL', 'REQUEST_SCOPE_MISMATCH')
    if not isinstance(request.get('proof_ref'),str) or not request['proof_ref'].startswith('SYN-'):
        return _result('UNKNOWN','MISSING_PROOF_REF')
    if proof.get('trusted_kind') != 'SYNTHETIC_RECONCILED_PROOF_STORE' or proof.get('authenticated_fixture') is not True:
        return _result('QUARANTINED','PROOF_REGISTRY_NOT_TRUSTED')
    if any(proof.get(k)!=ctx[k] for k in _SCOPE):
        return _result('QUARANTINED','PROOF_SCOPE_MISMATCH')
    if request['proof_ref'] != proof.get('proof_id'):
        return _result('UNKNOWN','PROOF_NOT_FOUND')
    if proof.get('source')!='DEC100_DEC101_DEC102' or proof.get('semantic_status')!='MAPPED_MINIMAL':
        return _result('UNKNOWN','SEMANTICS_NOT_VERIFIED')
    if proof.get('coverage')!='FULL_FOR_MILESTONE' or proof.get('mapping_status')!='CURATED_PINNED':
        return _result('BLOCKED_MAPPING','COVERAGE_OR_MAPPING_UNTRUSTED')
    if proof.get('reconciliation') not in ('CONSISTENT_WITH_PROOF','APPROVED_AND_COMMITTED_REBASE'):
        return _result('QUARANTINED','RECONCILIATION_NOT_COMMITTED')
    if proof.get('host_epoch')!=ctx['host_epoch'] or proof.get('checkpoint_epoch')!=ctx['checkpoint_epoch']:
        return _result('QUARANTINED','EPOCH_MISMATCH')
    if type(proof.get('observed_tick')) is not int or proof['observed_tick'] > ctx['world_tick']:
        return _result('UNKNOWN','INVALID_OBSERVATION_TIME')
    age = policy.get('max_age_ticks')
    if type(age) is not int or age < 0 or ctx['world_tick'] - proof['observed_tick'] > age:
        return _result('UNKNOWN','STALE_PROOF')
    if not isinstance(proof.get('milestone_id'),str) or not proof['milestone_id'].startswith('SYN-'):
        return _result('UNKNOWN','NO_MILESTONE')
    if not isinstance(proof.get('occurrence_id'),str) or not proof['occurrence_id'].startswith('SYN-'):
        return _result('UNKNOWN','NO_CERTIFIED_OCCURRENCE')
    if proof.get('classification') not in ('PUBLIC','PROTECTED'):
        return _result('QUARANTINED','UNKNOWN_SECRECY_CLASS')
    if proof['classification']=='PROTECTED' and policy.get('can_process_protected') is not True:
        return _result('BLOCKED_ACL','PROTECTED_SOURCE_DENIED')
    if catalog.get('trusted_kind')!='SYNTHETIC_CURATED_RULESET' or catalog.get('curation_status')!='CURATED_SYNTHETIC':
        return _result('BLOCKED_RULE','CATALOG_NOT_CURATED')
    if any(catalog.get(k)!=ctx[k] for k in ('quest_key','build_fingerprint','modpack_hash','mapping_revision')):
        return _result('BLOCKED_RULE','RULESET_VERSION_MISMATCH')
    if not isinstance(catalog.get('revision'),str) or not catalog['revision'].startswith('SYN-'):
        return _result('BLOCKED_RULE','MISSING_RULESET_REVISION')
    if ledger.get('trusted_kind')!='SYNTHETIC_ADMISSION_LEDGER' or any(ledger.get(k)!=ctx[k] for k in _SCOPE):
        return _result('QUARANTINED','LEDGER_SCOPE_MISMATCH')
    if ledger.get('host_epoch')!=ctx['host_epoch'] or ledger.get('checkpoint_epoch')!=ctx['checkpoint_epoch']:
        return _result('QUARANTINED','LEDGER_EPOCH_MISMATCH')
    if request.get('expected_ledger_revision') != ledger.get('revision'):
        return _result('QUARANTINED','CAS_LEDGER_REVISION_MISMATCH')
    if any(action.get('state') in _UNCERTAIN for action in ledger.get('actions',())):
        return _result('QUARANTINED','DISPATCH_UNCERTAIN',pending=True)
    admission_key = _digest(*(ctx[k] for k in ('campaign_id','branch_id','lineage_id','quest_key')),
                            proof['milestone_id'], proof['occurrence_id'],
                            ctx['mapping_revision'], catalog['revision'])
    if admission_key in ledger.get('admitted_keys',()) or admission_key in ledger.get('pending_keys',()):
        return _result('DUPLICATE_SUPPRESSED','ALREADY_ADMITTED_OR_PENDING',key=admission_key)
    facts = ledger.get('confirmed_facts')
    if not isinstance(facts,dict):
        return _result('QUARANTINED','NO_CONFIRMED_WORLD_FACTS')
    proposals=[]
    ids=set()
    for rule in catalog.get('rules',[]):
        if not isinstance(rule,dict) or not str(rule.get('rule_id','')).startswith('SYN-'):
            return _result('BLOCKED_RULE','MALFORMED_RULE')
        if rule['rule_id'] in ids:
            return _result('BLOCKED_RULE','DUPLICATE_RULE_ID')
        ids.add(rule['rule_id'])
        if rule.get('milestone_id')!=proof['milestone_id']:
            continue
        if rule.get('region_id') != ctx['region_id']:
            continue
        if not (type(rule.get('dr_start')) is int and type(rule.get('dr_end')) is int
                and rule['dr_start'] <= ctx['dr_year'] <= rule['dr_end']):
            continue
        if not (type(rule.get('month_start')) is int and type(rule.get('month_end')) is int
                and rule['month_start'] <= ctx['dr_month'] <= rule['month_end']):
            continue
        if rule.get('classification') not in ('PUBLIC','PRIVATE'):
            return _result('BLOCKED_RULE','INVALID_VISIBILITY')
        if proof['classification']=='PROTECTED' and rule['classification']=='PUBLIC':
            continue  # fail closed: never launder protected source into public rumor
        if rule.get('risk') not in _SUPPORTED_RISKS:
            return _result('BLOCKED_RULE','INVALID_RISK')
        if rule['risk']=='HIGH' and not policy.get('can_propose_high_risk',False):
            continue
        requirements=rule.get('requires',{})
        if not isinstance(requirements,dict):
            return _result('BLOCKED_RULE','INVALID_PREDICATE')
        if any(type(v) not in (bool,int,str) or k not in facts for k,v in requirements.items()):
            continue  # missing or invalid confirmed fact => non-eligible
        if any(type(facts[k]) is not type(v) or facts[k]!=v for k,v in requirements.items()):
            continue
        if rule.get('kind') not in ('RUMOR_PROPOSAL','FACTION_REACTION_PROPOSAL','LOCAL_EFFECT_PROPOSAL'):
            return _result('BLOCKED_RULE','UNSUPPORTED_EFFECT_KIND')
        proposals.append({'candidate_id':_digest(admission_key,rule['rule_id'],rule['kind'],ctx['region_id']),
                          'kind':rule['kind'], 'risk':rule['risk'],
                          'needs_host_receipt':rule['kind']!='RUMOR_PROPOSAL',
                          'needs_delivery_proof':rule['kind']=='RUMOR_PROPOSAL'})
    proposals.sort(key=lambda q:q['candidate_id'])
    return _result('PROPOSE_ADMISSION','READY_FOR_ATOMIC_LEDGER_AND_OUTBOX',key=admission_key,proposals=proposals)
