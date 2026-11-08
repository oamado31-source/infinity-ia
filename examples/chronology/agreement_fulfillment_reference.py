"""DEC-108/C reference planner using *synthetic, pretrusted fixture data only*.

No engine, multiplayer, network, files, LLM, transactions or side effects.
"trusted_*" names merely distinguish TEST FIXTURE TRUST BOUNDARIES. A real
implementation must authenticate them independently; this module CANNOT do so.
"""
from __future__ import annotations
import hashlib
import json
from decimal import Decimal
from jsonschema import Draft202012Validator
from pathlib import Path

SCHEMA = json.loads(Path(__file__).with_name('agreement_fulfillment_v1.candidate.schema.json').read_text(encoding='utf8'))
VALIDATOR = Draft202012Validator(SCHEMA)
SCOPES = ('campaign_id','branch_id','lineage_id','build_fingerprint','modpack_hash','host_epoch','checkpoint_epoch')
PROHIBITED_OUTPUT_FIELDS = frozenset({'execute','host_command','transfer','penalty','reputation_delta','money_delta','set_quest_flag','signed_agreement'})

def result(status: str, reason: str, **extras):
    return {'status':status,'reason':reason,'host_action':'NONE','mechanical_effects':False,'punishment':False,**extras}

def _same_scope(context, obj):
    return all(obj.get(k)==context.get(k) for k in SCOPES)

def _key(context, agreement, term, receipt_rev):
    scope={k:context[k] for k in SCOPES}
    seed={'scope':scope,'agreement_id':agreement['agreement_id'],'agreement_revision':agreement['revision'],
          'term_id':term['term_id'],'term_revision':term['revision'],'receipt_ledger_revision':receipt_rev,
          'world_tick':context['world_tick'],'action':'REVIEW_ONLY'}
    return hashlib.sha256(json.dumps(seed,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def plan_synthetic(data):
    """Return a deterministic *proposal*. Never changes ``data`` or calls a host.

    This validator protects a synthetic demo input shape; real receipt signatures
    and mandates CANNOT be validated from arbitrary booleans in a JSON request.
    """
    if not isinstance(data,dict) or list(VALIDATOR.iter_errors(data)):
        return result('QUARANTINED','SCHEMA_OR_FIXTURE_INVALID')
    try:
        ctx=data['context'];request=data['request'];pol=data['trusted_policy']; agreement=data['trusted_agreement_registry']
        term=data['trusted_term_registry']; receipts=data['trusted_receipt_ledger']; claims=data['trusted_claim_ledger']; outbox=data['trusted_outbox_ledger']
        for ledger in (agreement,term,receipts,claims,outbox):
            if not ledger.get('authenticated_fixture') or not _same_scope(ctx,ledger):
                return result('QUARANTINED','TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH')
        if not pol['authenticated_fixture'] or pol['revision']!=agreement['policy_revision']:
            return result('QUARANTINED','POLICY_NOT_VERIFIED')
        if ctx['authenticated_principal'] not in pol['authorized_principals'] or ctx['authenticated_principal'] not in agreement['authorized_representatives']:
            return result('DENIED','PRINCIPAL_UNAUTHORIZED')
        if request['audience'] not in pol['allowed_audiences'] or request['audience'] not in agreement['allowed_audiences'] or request['audience'] not in term['allowed_audiences']:
            return result('DENIED','AUDIENCE_UNAUTHORIZED')
        if pol['high_risk_unresolved'] or agreement['high_risk_unresolved'] or term['high_risk_unresolved'] or claims['high_risk_unresolved']:
            return result('QUARANTINED','HIGH_RISK_REQUIRES_AUTHORIZATION')
        if request['agreement_ref']!=agreement['agreement_id'] or request['term_ref']!=term['term_id'] or term['agreement_id']!=agreement['agreement_id']:
            return result('DENIED','AGREEMENT_TERM_MISMATCH')
        if request['expected_agreement_revision']!=agreement['revision'] or request['expected_term_revision']!=term['revision']:
            return result('QUARANTINED','STALE_REVISION')
        if agreement['commit_state']!='COMMITTED' or not agreement['commit_receipt_authenticated'] or term['status']!='ACTIVE' or not agreement['mandate_valid']:
            return result('QUARANTINED','AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID')
        if term['obligor'] not in agreement['party_ids'] or term['beneficiary'] not in agreement['party_ids'] or term['obligor']==term['beneficiary']:
            return result('QUARANTINED','TERM_PARTIES_INVALID')
        if claims['agreement_id']!=agreement['agreement_id'] or claims['term_id']!=term['term_id'] or receipts['term_id']!=term['term_id'] or outbox['agreement_id']!=agreement['agreement_id']:
            return result('QUARANTINED','LEDGER_LINK_INVALID')
        if receipts['term_revision']!=term['revision'] or claims['term_revision']!=term['revision']:
            return result('QUARANTINED','TERM_LEDGER_REVISION_MISMATCH')
        if outbox['state'] in ('DISPATCHED','UNCERTAIN') or outbox['pending_actions'] or receipts['pending_actions'] or receipts['uncertain_actions'] or receipts['dispatched_actions']:
            return result('QUARANTINED','UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION')
        confirmed=Decimal('0');receipt_ids=set();action_ids=set()
        for r in receipts['receipts']:
            if not _same_scope(ctx,r) or not r['authenticated_fixture']:
                return result('QUARANTINED','RECEIPT_SCOPE_OR_AUTHENTICATION_MISMATCH')
            if r['term_id']!=term['term_id'] or r['term_revision']!=term['revision'] or r['from_party']!=term['obligor'] or r['to_party']!=term['beneficiary'] or r['unit']!=term['unit']:
                return result('QUARANTINED','RECEIPT_TARGET_OR_UNIT_MISMATCH')
            if r['world_tick']>ctx['world_tick']:
                return result('QUARANTINED','RECEIPT_FROM_FUTURE')
            if r['receipt_id'] in receipt_ids:
                return result('QUARANTINED','RECEIPT_ID_DUPLICATE')
            if r['action_id'] in action_ids:
                return result('QUARANTINED','ACTION_ID_DUPLICATE')
            receipt_ids.add(r['receipt_id']);action_ids.add(r['action_id'])
            if r['status']=='UNCERTAIN' or r['status']=='DISPATCHED':
                return result('QUARANTINED','UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION')
            if r['status']=='CONFIRMED':confirmed+=Decimal(str(r['amount']))
        expected=Decimal(str(term['amount']))
        remaining=max(Decimal('0'), expected-confirmed)
        if confirmed>expected and not term['allow_overdelivery']:
            return result('QUARANTINED','OVERDELIVERY_NOT_AUTOMATIC_CREDIT')
        stable=_key(ctx,agreement,term,receipts['revision'])
        if stable in outbox['pending_proposal_keys'] or stable in outbox['committed_proposal_keys']:
            return result('QUARANTINED','PROPOSAL_IN_OUTBOX_RECONCILE')
        output={'agreement_id':agreement['agreement_id'],'term_id':term['term_id'],'confirmed_amount':str(confirmed),
                'remaining_unproven':str(remaining),'unit':term['unit'],'proposal_key':stable,
                'fulfillment_is_not_host_commit':True,'silence_is_not_breach':True,'no_penalty':True}
        if claims['is_contested']:
            return result('CONTESTED','CLAIM_OR_RECEIPT_CONTESTED',proposed_action='PROPOSE_CONTRADICTORY_REVIEW',**output)
        if confirmed>=expected:
            return result('FULFILLMENT_CANDIDATE','CONFIRMED_AMOUNT_AT_LEAST_EXPECTED',proposed_action='PROPOSE_TERM_COMPLETION_REVIEW',**output)
        if claims['force_majeure_alleged']:
            return result('REVIEW_PENDING','FORCE_MAJEURE_ALLEGED_NOT_PROVED',proposed_action='PROPOSE_VOLUNTARY_RENEGOTIATION',**output)
        if confirmed>0:
            return result('PARTIAL_CONFIRMED','HOST_RECEIPTS_PARTIAL',proposed_action='PROPOSE_PARTIAL_CLARIFICATION',**output)
        if ctx['world_tick']>=term['due_tick']:
            return result('OVERDUE_UNVERIFIED','DUE_TICK_REACHED_WITHOUT_CONFIRMED_DELIVERY',proposed_action='PROPOSE_EVIDENCE_REQUEST_NO_SANCTION',**output)
        if claims['claims']:
            return result('CLAIMED_UNVERIFIED','CLAIM_IS_NOT_RECEIPT',proposed_action='PROPOSE_EVIDENCE_REQUEST',**output)
        return result('WAITING','DUE_TICK_NOT_REACHED',proposed_action='WAIT_UNTIL_DUE',**output)
    except (TypeError,KeyError,ValueError,OverflowError,ArithmeticError,IndexError):
        return result('QUARANTINED','INVALID_OR_INCOMPLETE_FIXTURE')
