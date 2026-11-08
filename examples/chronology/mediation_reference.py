"""DEC-107/C: PURE SYNTHETIC proposal planner; never a mediation executor.

Input ``trusted_*`` fields are TEST HARNESS fixtures. A real system must retrieve,
authenticate and authorize them out-of-band, not from the caller's request.
Nothing here contacts BG2:EE, an LLM, networks, files, the host or any NPC.
"""
from __future__ import annotations
import hashlib, json
_SCOPE=('campaign_id','branch_id','lineage_id','build_fingerprint','modpack_hash','host_epoch','checkpoint_epoch')
_ALLOWED_REQUEST={'case_ref','party_ref','audience','purpose','expected_revision','trace_ref'}
_LEVEL={'PUBLIC':0,'RESTRICTED':1,'PROTECTED':2}

def result(status,reason,**extra):
    return dict(status=status,reason=reason,proposal_only=True,host_calls=0,
                notices_sent=0,agreements_signed=0,compelled_confessions=0,
                currency_transferred=0,reputation_written=0,quests_modified=0,
                beliefs_overwritten=0,parties_coerced=0,events_erased=0,
                **extra)

def scoped(rec,ctx):
    return isinstance(rec,dict) and all(rec.get(k)==ctx.get(k) for k in _SCOPE)

def valid_context(ctx):
    return (isinstance(ctx,dict) and ctx.get('fixture_only') is True and
        ctx.get('host_mode')=='SYNTHETIC_HOST_FIXTURE' and
        all(isinstance(ctx.get(k),str) and ctx[k].startswith('SYN-') for k in _SCOPE[:5]) and
        all(type(ctx.get(k)) is int and ctx[k]>=0 for k in _SCOPE[5:]) and
        type(ctx.get('world_tick')) is int and ctx['world_tick']>=0 and
        ctx.get('clock_mode') in ('FROZEN','PARTIAL','REALTIME') and
        isinstance(ctx.get('authenticated_principal'),str))

def stable_key(*args):
    blob=json.dumps(args,sort_keys=True,separators=(',',':'),ensure_ascii=True)
    return hashlib.sha256(blob.encode()).hexdigest()

def plan_synthetic(fixture):
    """Return a scoped proposal only; never enforce social/motor effects."""
    if not isinstance(fixture,dict) or fixture.get('source_kind')!='SYNTHETIC_TEST':
        return result('QUARANTINED','NOT_SYNTHETIC_FIXTURE')
    try:
        ctx=fixture['context']; req=fixture['request']
        policy=fixture['trusted_policy']
        case=fixture['trusted_case_registry']; parties=fixture['trusted_party_registry']
        evidence=fixture['trusted_evidence_ledger']; delivery=fixture['trusted_notice_ledger']
        mediator=fixture['trusted_facilitator_registry']; ledger=fixture['trusted_mediation_ledger']
        records=(case,parties,evidence,delivery,mediator,ledger)
        if not valid_context(ctx) or not isinstance(req,dict) or set(req)-_ALLOWED_REQUEST:
            return result('QUARANTINED','INVALID_CONTEXT_OR_REQUEST')
        if not isinstance(policy,dict) or any(not isinstance(x,dict) for x in records):
            return result('QUARANTINED','INVALID_TRUSTED_REGISTRY_SHAPE')
        if any(not scoped(x,ctx) for x in records):
            return result('QUARANTINED','CROSS_SCOPE_OR_STALE_EPOCH')
        if policy.get('trusted_kind')!='SYNTHETIC_SIGNED_POLICY' or not str(policy.get('revision','')).startswith('SYN-'):
            return result('QUARANTINED','POLICY_NOT_PINNED')
        expected=('SYNTHETIC_DISPUTE_CASE','SYNTHETIC_PARTY_REGISTRY',
                  'SYNTHETIC_EVIDENCE_LEDGER','SYNTHETIC_NOTICE_LEDGER',
                  'SYNTHETIC_FACILITATOR_REGISTRY','SYNTHETIC_MEDIATION_LEDGER')
        if any(r.get('trusted_kind')!=tag or r.get('authenticated_fixture') is not True for r,tag in zip(records,expected)):
            return result('QUARANTINED','TRUSTED_RECORD_ATTESTATION_MISSING')
        if req.get('purpose') not in policy.get('allowed_purposes',[]) or req.get('audience') not in policy.get('allowed_audiences',[]):
            return result('DENIED','PURPOSE_OR_AUDIENCE_NOT_ALLOWED')
        if ctx['authenticated_principal'] not in policy.get('authorized_principals',[]):
            return result('DENIED','PRINCIPAL_NOT_AUTHORIZED')
        if any(not isinstance(req.get(k),str) or not req[k].startswith('SYN-') for k in ('case_ref','party_ref')):
            return result('QUARANTINED','INVALID_REFERENCE')
        if not isinstance(case.get('party_ids'),list) or len(case['party_ids'])<2 or len(set(case['party_ids']))!=len(case['party_ids']):
            return result('QUARANTINED','INVALID_PARTY_MEMBERSHIP')
        if req['case_ref']!=case.get('case_id') or req['party_ref'] not in case.get('party_ids',[]):
            return result('UNKNOWN','CASE_OR_PARTY_NOT_FOUND')
        if req.get('expected_revision')!=ledger.get('revision') or type(ledger.get('revision')) is not int:
            return result('QUARANTINED','STALE_LEDGER_REVISION')
        if case.get('case_revision')!=ledger.get('case_revision'):
            return result('QUARANTINED','CASE_REVISION_CHANGED')
        if case.get('status')!='OPEN':
            return result('DENIED','CASE_NOT_OPEN')
        if case.get('high_risk_unresolved') or evidence.get('high_risk_unresolved'):
            return result('QUARANTINED','HIGH_RISK_GATE_UNRESOLVED')
        if case.get('purpose')!=req['purpose'] or req['audience'] not in case.get('allowed_audiences',[]):
            return result('DENIED','CASE_SCOPE_NOT_ALLOWED')
        if not isinstance(parties.get('parties'),dict) or set(case['party_ids'])-set(parties['parties']):
            return result('QUARANTINED','UNRESOLVED_PARTY_IDENTITY')
        for party_id in case['party_ids']:
            party=parties['parties'][party_id]
            if not isinstance(party,dict) or not party.get('owner_attested') or party.get('mandate')!='VALID':
                return result('QUARANTINED','PARTY_AUTHORITY_NOT_VERIFIED')
            if party.get('kind')=='PC' and party.get('pc_owner_attested') is not True:
                return result('DENIED','PC_OWNER_AUTHORIZATION_REQUIRED')
            if party.get('kind') not in ('PC','NPC','ORG','FAC'):
                return result('QUARANTINED','INVALID_PARTY_KIND')
        requesting_party=parties['parties'][req['party_ref']]
        if requesting_party.get('represented_by')!=ctx['authenticated_principal']:
            return result('DENIED','REQUESTER_NOT_AUTHORIZED_REPRESENTATIVE')
        if evidence.get('case_id')!=case['case_id'] or evidence.get('status') not in ('CONTESTED','PARTIALLY_CORROBORATED','CORROBORATED'):
            return result('QUARANTINED','EVIDENCE_UNVERIFIED_OR_UNLINKED')
        if not isinstance(evidence.get('claim_refs'),list) or not evidence['claim_refs']:
            return result('QUARANTINED','MISSING_CLAIM_PROVENANCE')
        if evidence.get('classification') not in _LEVEL:
            return result('QUARANTINED','INVALID_EVIDENCE_CLASSIFICATION')
        if req['audience']=='PUBLIC' and evidence['classification']!='PUBLIC':
            return result('DENIED','PUBLIC_DISCLOSURE_WITH_PROTECTED_EVIDENCE')
        if req['audience'] not in evidence.get('allowed_audiences',[]):
            return result('DENIED','EVIDENCE_ACL_DENIED')
        if delivery.get('case_id')!=case['case_id'] or delivery.get('respondent_id') not in case['party_ids']:
            return result('QUARANTINED','NOTICE_CASE_MISMATCH')
        notice=delivery.get('state')
        if notice not in ('NOT_SENT','DRAFT','IN_TRANSIT','LOST','DELIVERED','UNCERTAIN'):
            return result('QUARANTINED','INVALID_NOTICE_STATE')
        if delivery.get('delivery_tick') is not None and (type(delivery['delivery_tick']) is not int or delivery['delivery_tick']>ctx['world_tick']):
            return result('QUARANTINED','INVALID_NOTICE_TIMESTAMP')
        if delivery.get('reply_status') not in ('NOT_FILED','FILED','DECLINED','UNKNOWN'):
            return result('QUARANTINED','INVALID_REPLY_STATUS')
        if mediator.get('case_id')!=case['case_id'] or mediator.get('status') not in ('VALID','CONFLICT','UNKNOWN'):
            return result('QUARANTINED','FACILITATOR_RECORD_UNAVAILABLE')
        if ledger.get('pending') not in (True,False) or ledger.get('dispatched') not in (True,False) or ledger.get('uncertain') not in (True,False):
            return result('QUARANTINED','INVALID_PENDING_LEDGER')
        key=stable_key(tuple(ctx[k] for k in _SCOPE),policy['revision'],case['case_id'],
                       case['case_revision'],req['party_ref'],req['purpose'],req['audience'],ledger['revision'])
        if key in ledger.get('committed_keys',[]):
            return result('ALREADY_REGISTERED','CASE_ACTION_ALREADY_REGISTERED',proposal_key=key)
        if key in ledger.get('pending_keys',[]) or ledger['pending']:
            return result('ALREADY_PLANNED','CASE_ACTION_ALREADY_PENDING',proposal_key=key)
        if ledger['dispatched'] or ledger['uncertain'] or notice=='UNCERTAIN':
            return result('QUARANTINED','UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION',proposal_key=key)
        if notice in ('NOT_SENT','DRAFT','LOST'):
            action='PROPOSE_SCOPED_NOTICE'
        elif notice=='IN_TRANSIT':
            action='WAIT_NOTICE_DELIVERY'
        elif delivery.get('perceived') is not True:
            action='WAIT_NOTICE_PERCEPTION'
        elif delivery['reply_status']=='UNKNOWN':
            action='REQUEST_REPLY_STATUS_EVIDENCE'
        elif delivery['reply_status']=='NOT_FILED':
            if type(delivery.get('reply_deadline_tick')) is not int:
                return result('QUARANTINED','UNKNOWN_REPLY_DEADLINE')
            action='OFFER_RIGHT_OF_REPLY' if ctx['world_tick']<=delivery['reply_deadline_tick'] else 'PROPOSE_REPLY_EXTENSION'
        elif delivery['reply_status']=='DECLINED':
            action='RESPECT_REFUSAL_NO_PENALTY'
        else:
            consents=[parties['parties'][pid].get('mediation_consent') for pid in case['party_ids']]
            if any(c not in ('GRANTED','PENDING','DECLINED','WITHDRAWN') for c in consents):
                return result('QUARANTINED','CONSENT_PROVENANCE_MISSING')
            if any(c in ('DECLINED','WITHDRAWN') for c in consents):
                action='RESPECT_REFUSAL_NO_PENALTY'
            elif any(c!='GRANTED' for c in consents):
                action='WAIT_VOLUNTARY_CONSENT'
            elif mediator['status']!='VALID' or mediator.get('conflict_of_interest') is not False:
                action='REVIEW_FACILITATOR_CONFLICT'
            else:
                action='PROPOSE_MEDIATION_SESSION'
        return result('PROPOSAL_READY','NO_SOCIAL_OR_HOST_EFFECTS',
                      proposed_action=action,proposal_key=key,
                      classification=evidence['classification'],
                      case_id=case['case_id'],dispute_resolution='NOT_ADJUDICATED',
                      voluntary=True,consent_is_independent=True)
    except (KeyError, TypeError, ValueError, OverflowError):
        return result('QUARANTINED','MISSING_OR_INVALID_FIXTURE_FIELDS')
