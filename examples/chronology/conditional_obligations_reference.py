"""DEC-109/C: PURE, SYNTHETIC, READ-ONLY graph evaluator.

NO game integration, NO signatures verified, NO transfers, NO release of escrow,
NO dispatch, NO NPC/PC mutation. The authenticated fixtures stand in for trusted
registries and must NEVER be populated from request-authored claims in production.
"""
from __future__ import annotations
import copy
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE = Path(__file__).resolve().parent
CORE_SCOPE = ('campaign_id','branch_id','lineage_id','host_epoch','checkpoint_epoch','build_fingerprint','modpack_hash')
TERMINAL = {'COMMITTED'}
MAX_TERMS = 64
MAX_DEPTH = 32


def _out(status, reason, **extra):
    return {'status': status, 'reason': reason, 'dispatch_allowed': False,
            'host_mutation': False, 'auto_sanction': False, **extra}


def _amount(s):
    if not isinstance(s, str):
        raise ValueError('NOT_A_STRING_DECIMAL')
    try:
        d = Decimal(s)
    except (InvalidOperation, ValueError):
        raise ValueError('INVALID_DECIMAL') from None
    if not d.is_finite() or d < 0 or d.as_tuple().exponent < -3:
        raise ValueError('INVALID_QUANTITY')
    return d


def _scope_ok(obj, context):
    return all(obj.get(k) == context.get(k) for k in CORE_SCOPE)


def _graph_order(terms):
    by_id = {}
    for t in terms:
        tid=t['term_id']
        if tid in by_id: raise ValueError('DUPLICATE_TERM')
        by_id[tid]=t
    marks={}; ordered=[]
    def visit(tid,depth):
        if depth > MAX_DEPTH: raise ValueError('GRAPH_DEPTH_EXCEEDED')
        if tid not in by_id: raise ValueError('UNKNOWN_DEPENDENCY')
        state=marks.get(tid)
        if state==1: raise ValueError('DEPENDENCY_CYCLE')
        if state==2:return
        marks[tid]=1
        t=by_id[tid]
        dependencies=t.get('gate',{}).get('dependencies',[])
        ids=[d.get('term_id') for d in dependencies]
        if len(ids)!=len(set(ids)): raise ValueError('DUPLICATE_DEPENDENCY')
        for dep in sorted(ids):
            if dep==tid: raise ValueError('DEPENDENCY_CYCLE')
            visit(dep,depth+1)
        marks[tid]=2;ordered.append(tid)
    for tid in sorted(by_id):visit(tid,0)
    return by_id, ordered


def evaluate(fixture: dict) -> dict:
    """Returns a plan/proof, never a host action. Denies unknown/unsafe input."""
    if not isinstance(fixture,dict) or fixture.get('source_kind') != 'SYNTHETIC_TEST':
        return _out('QUARANTINED', 'SYNTHETIC_FIXTURE_REQUIRED')
    try:
        ctx=fixture['context'];req=fixture['request']
        agreement=fixture['trusted_agreement_registry']
        terms_registry=fixture['trusted_term_registry']
        receipts=fixture['trusted_receipt_ledger']
        authorization=fixture['trusted_authorization_registry']
        reservation=fixture['trusted_reservation_registry']
        policy=fixture['trusted_policy']
        if ctx.get('host_mode')!='SYNTHETIC_HOST_FIXTURE' or ctx.get('fixture_only') is not True:
            return _out('QUARANTINED','LIVE_HOST_NOT_SUPPORTED')
        for name,reg in [('AGREEMENT',agreement),('TERMS',terms_registry),('RECEIPTS',receipts),('AUTHORIZATION',authorization),('RESERVATIONS',reservation),('POLICY',policy)]:
            if reg.get('authenticated_fixture') is not True or not _scope_ok(reg,ctx):
                return _out('QUARANTINED',f'{name}_TRUSTED_SCOPE_INVALID')
        if req.get('agreement_id')!=agreement.get('agreement_id'):
            return _out('QUARANTINED','AGREEMENT_MISMATCH')
        if req.get('expected_agreement_revision') != agreement.get('revision'):
            return _out('BLOCKED_STALE','AGREEMENT_REVISION_STALE')
        if req.get('policy_revision')!=policy.get('revision'):
            return _out('BLOCKED_STALE','POLICY_REVISION_STALE')
        if agreement.get('state')!='COMMITTED' or agreement.get('consents_confirmed') is not True or agreement.get('mandates_valid') is not True or agreement.get('commit_proof_authenticated') is not True:
            return _out('BLOCKED_AGREEMENT','AGREEMENT_NOT_AUTHENTICATED_COMMITTED')
        parties=agreement.get('parties',[])
        if not isinstance(parties,list) or len(parties)<2 or len(parties)!=len(set(parties)):
            return _out('QUARANTINED','INVALID_PARTIES')
        if reservation.get('inflight_actions') or receipts.get('inflight_actions'):
            return _out('BLOCKED_UNCERTAIN','INFLIGHT_REQUIRES_HOST_RECONCILIATION')
        terms=terms_registry.get('terms',[])
        if len(terms)>min(MAX_TERMS,policy.get('max_terms',MAX_TERMS)):
            return _out('QUARANTINED','TOO_MANY_TERMS')
        by_id,order=_graph_order(terms)
        target=req.get('term_id')
        if target not in by_id:
            return _out('UNKNOWN','TERM_NOT_FOUND')
        if req.get('expected_term_revision')!=by_id[target].get('revision'):
            return _out('BLOCKED_STALE','TERM_REVISION_STALE')
        for term in terms:
            if term.get('agreement_id')!=agreement['agreement_id'] or term.get('state') not in TERMINAL:
                return _out('BLOCKED_AGREEMENT','TERM_NOT_COMMITTED')
            if term.get('obligor') not in parties or term.get('beneficiary') not in parties or term.get('obligor')==term.get('beneficiary'):
                return _out('QUARANTINED','INVALID_TERM_PARTIES')
            if _amount(term.get('quantity'))<=0:
                return _out('QUARANTINED','INVALID_TERM_QUANTITY')
            gate=term.get('gate',{})
            deps=gate.get('dependencies',[]);op=gate.get('operator','ALL')
            if op not in ('ALL','ANY','AT_LEAST'):
                return _out('QUARANTINED','UNSUPPORTED_GATE_OPERATOR')
            mincount=gate.get('minimum',0)
            if op=='AT_LEAST' and (not isinstance(mincount,int) or isinstance(mincount,bool) or not 1<=mincount<=len(deps)):
                return _out('QUARANTINED','INVALID_GATE_THRESHOLD')
            for dep in deps:
                parent=by_id[dep['term_id']]
                if dep.get('expected_revision')!=parent['revision']:
                    return _out('BLOCKED_STALE','DEPENDENCY_REVISION_STALE')
                if dep.get('kind') not in ('CONFIRMED_COMPLETE','CONFIRMED_AT_LEAST'):
                    return _out('QUARANTINED','UNKNOWN_DEPENDENCY_KIND')
                if dep.get('kind')=='CONFIRMED_AT_LEAST' and (_amount(dep.get('amount','0'))<=0 or _amount(dep['amount'])>_amount(parent['quantity'])):
                    return _out('QUARANTINED','INVALID_PARTIAL_THRESHOLD')
        seen_r={};seen_a={};total={k:Decimal('0') for k in by_id}
        for rec in receipts.get('receipts',[]):
            if not _scope_ok(rec,ctx) or rec.get('host_authenticated') is not True or rec.get('status')!='CONFIRMED' or rec.get('world_tick',ctx['world_tick']+1)>ctx['world_tick']:
                return _out('QUARANTINED','RECEIPT_UNVERIFIED_OR_SCOPE_MISMATCH')
            tid=rec.get('term_id')
            if tid not in by_id:return _out('QUARANTINED','RECEIPT_UNKNOWN_TERM')
            term=by_id[tid]
            if (rec.get('agreement_id')!=agreement['agreement_id'] or rec.get('term_revision')!=term['revision'] or rec.get('unit')!=term['unit'] or rec.get('from_party')!=term['obligor'] or rec.get('to_party')!=term['beneficiary']):
                return _out('QUARANTINED','RECEIPT_TARGET_OR_UNIT_MISMATCH')
            qty=_amount(rec.get('quantity'))
            if qty<=0:return _out('QUARANTINED','RECEIPT_QUANTITY_INVALID')
            rid=rec.get('receipt_id');aid=rec.get('action_id')
            if not isinstance(rid,str) or not isinstance(aid,str) or not rid or not aid:
                return _out('QUARANTINED','INVALID_RECEIPT_IDENTITY')
            if rid in seen_r:
                if seen_r[rid]!=rec:return _out('QUARANTINED','CONFLICTING_RECEIPT_ID')
                continue
            if aid in seen_a:return _out('QUARANTINED','DUPLICATE_ACTION_ID')
            seen_r[rid]=rec;seen_a[aid]=rid;total[tid]+=qty
        if any(total[tid]>_amount(by_id[tid]['quantity']) for tid in by_id):
            return _out('QUARANTINED','RECEIPTS_EXCEED_OBLIGATION')
        states={}
        for tid in order:
            t=by_id[tid];deps=t.get('gate',{}).get('dependencies',[]);gate=t.get('gate',{});op=gate.get('operator','ALL')
            hit=0
            for d in deps:
                parent=by_id[d['term_id']]
                proof=total[d['term_id']]
                required=(_amount(parent['quantity']) if d['kind']=='CONFIRMED_COMPLETE' else _amount(d['amount']))
                hit+=int(proof>=required)
            need=(len(deps) if op=='ALL' else 1 if op=='ANY' and deps else gate.get('minimum',0))
            if total[tid]==_amount(t['quantity']):
                status='COMPLETE_CONFIRMED'
            elif hit<need:
                status='WAITING_DEPENDENCIES'
            elif ctx['world_tick']<t.get('earliest_world_tick',0):
                status='WAITING_DR_TIME'
            elif t.get('resource_id') in reservation.get('conflicting_reservations',[]):
                status='BLOCKED_RESOURCE_CONFLICT'
            elif not reservation.get('resources_available',True):
                status='BLOCKED_RESOURCE_UNAVAILABLE'
            elif not any(a.get('term_id')==tid and a.get('revision')==t['revision'] and a.get('party')==t['obligor'] and a.get('authorized') is True for a in authorization.get('term_grants',[])):
                status='BLOCKED_AUTHORIZATION'
            else:
                status='READY_FOR_AUTHORIZED_PLANNING'
            states[tid]={'status':status,'confirmed_quantity':str(total[tid]),'required_quantity':t['quantity'],'dependencies_satisfied':hit,'dependencies_required':need}
        stable = json.dumps({'scope':[ctx.get(k) for k in CORE_SCOPE], 'agreement':agreement['agreement_id'], 'revision':agreement['revision'], 'term':target,'term_revision':by_id[target]['revision'], 'policy':policy['revision'], 'confirmed':str(total[target]), 'dependencies':states[target]['dependencies_satisfied']}, sort_keys=True,ensure_ascii=True)
        return _out(states[target]['status'],'EVALUATED_DETERMINISTICALLY',term_id=target,term_state=states[target],graph_order=order,proposal_key=hashlib.sha256(stable.encode()).hexdigest()[:24])
    except (KeyError,TypeError,ValueError,AttributeError,IndexError) as e:
        return _out('QUARANTINED', 'INVALID_GRAPH_OR_FIXTURE')


def plan_synthetic(fixture):
    return evaluate(copy.deepcopy(fixture))


def load_fixture():
    return json.loads((BASE/'conditional_obligations_v1.synthetic.json').read_text(encoding='utf8'))


if __name__=='__main__':
    print(json.dumps(plan_synthetic(load_fixture()),indent=2))
