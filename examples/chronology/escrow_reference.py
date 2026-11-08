"""DEC-110/C SYNTHETIC ONLY. Pure escrow planning; never a host or wallet adapter.
Trusted_* fields represent TEST FIXTURE BOUNDARIES, not authenticated production data.
"""
from __future__ import annotations
import hashlib,json
from decimal import Decimal, InvalidOperation
from pathlib import Path

def fixture():
    return json.loads(Path(__file__).with_name('escrow_v1.synthetic.json').read_text(encoding='utf8'))

def plan_synthetic(d):
    out={'status':'QUARANTINED','reason':'INVALID','host_action':'NONE','transfer_performed':False,'release_performed':False,'punishment':False}
    def finish(status,reason,**kwargs): return {**out,'status':status,'reason':reason,**kwargs}
    try:
        c=d['context'];q=d['request'];a=d['trusted_agreement'];cap=d['trusted_capability'];own=d['trusted_ownership'];receipts=d['trusted_host_receipts'];auth=d['trusted_authorizations'];release=d['trusted_release_rule']
        if c.get('mode')!='SYNTHETIC_ONLY' or not c.get('fixture_only') or d.get('source_kind')!='SYNTHETIC_FIXTURE':return finish('QUARANTINED','NOT_SYNTHETIC')
        keys=('campaign_id','branch_id','lineage_id','build_fingerprint','modpack_hash','host_epoch','checkpoint_epoch')
        if any(not c.get(k) for k in keys):return finish('QUARANTINED','INVALID_SCOPE')
        for x in (a,cap,own,receipts,auth,release):
            if not x.get('authenticated_fixture') or any(x.get(k)!=c.get(k) for k in keys):return finish('QUARANTINED','LEDGER_UNTRUSTED_OR_SCOPE_MISMATCH')
        if q['escrow_id']!=a['escrow_id'] or q['expected_revision']!=a['revision'] or a['state']!='COMMITTED':return finish('BLOCKED_STALE','AGREEMENT_NOT_COMMITTED_OR_STALE')
        if q['requester'] not in auth['authorized_requesters']:return finish('DENIED','REQUESTER_UNAUTHORIZED')
        if q['audience'] not in a['allowed_audiences'] or q['audience'] not in auth['allowed_audiences']:return finish('DENIED','AUDIENCE_UNAUTHORIZED')
        if receipts['uncertain_actions'] or receipts['dispatched_actions']:return finish('RECONCILE_REQUIRED','HOST_ACTION_IN_FLIGHT')
        if release['contested'] or a['contested']:return finish('CONTESTED_HOLD','CONTESTED')
        if not cap['escrow_tested_two_clients'] or not cap['transfer_tested'] or not cap['query_tested'] or not cap['recovery_tested']:
            return finish('BLOCKED_CAPABILITY','NOT_MECHANICALLY_HELD')
        if not own['proven_owner'] or not own['custodian_validated'] or own['asset_id']!=a['asset_id'] or own['owner']!=a['depositant']:
            return finish('BLOCKED_OWNERSHIP','OWNER_OR_CUSTODIAN_UNVERIFIED')
        if not auth['depositant_consented'] or not auth['release_consent_valid']:return finish('WAITING_CONSENT','SPECIFIC_OWNER_CONSENT_REQUIRED')
        amount=Decimal(str(a['amount']))
        if amount<=0 or not amount.is_finite():return finish('QUARANTINED','INVALID_AMOUNT')
        total=Decimal('0');seen=set();actions=set()
        for r in receipts['confirmed_deposits']:
            if r.get('receipt_id') in seen or r.get('action_id') in actions:return finish('QUARANTINED','DUPLICATE_DEPOSIT_RECEIPT')
            seen.add(r.get('receipt_id'));actions.add(r.get('action_id'))
            if not r['authenticated_fixture'] or r['status']!='CONFIRMED' or any(r.get(k)!=c.get(k) for k in keys):return finish('QUARANTINED','INVALID_HOST_RECEIPT')
            if r['escrow_id']!=a['escrow_id'] or r['asset_id']!=a['asset_id'] or r['to_custodian']!=a['custodian'] or r['from_owner']!=a['depositant'] or r['unit']!=a['unit']:return finish('QUARANTINED','RECEIPT_TARGET_MISMATCH')
            n=Decimal(str(r['amount']))
            if n<=0 or not n.is_finite():return finish('QUARANTINED','INVALID_RECEIPT_AMOUNT')
            total+=n
        if total>amount:return finish('QUARANTINED','OVERDEPOSIT_RECONCILE')
        if total<amount:return finish('NOT_MECHANICALLY_HELD','NO_FULL_DEPOSIT_RECEIPT',confirmed_amount=str(total))
        if not release['conditions_confirmed']:return finish('WAITING_CONDITIONS','CONTRACT_PREDICATE_PENDING',confirmed_amount=str(total))
        seed=json.dumps({'scope':{k:c[k] for k in keys},'escrow_id':a['escrow_id'],'revision':a['revision'],'receipts':sorted(seen),'rule_revision':release['revision']},sort_keys=True)
        key=hashlib.sha256(seed.encode()).hexdigest()
        if key in receipts['pending_release_keys'] or key in receipts['confirmed_release_keys']:return finish('RECONCILE_REQUIRED','RELEASE_ALREADY_PENDING_OR_CONFIRMED')
        return finish('RELEASE_ELIGIBLE_FOR_REVIEW','PROPOSE_ONLY',proposal_key=key,confirmed_amount=str(total))
    except (KeyError,TypeError,ValueError,InvalidOperation):return finish('QUARANTINED','MALFORMED_SYNTHETIC_FIXTURE')
