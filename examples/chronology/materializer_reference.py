"""DEC-098/C: pure SYNTHETIC preview of region deltas; NEVER integrates with BG2:EE/EEex.

No filesystem/network/game/IPC side effects. Receipts and capabilities here are synthetic
fixture strings, not authenticated host evidence. The result is ALWAYS only a preview.
"""
from __future__ import annotations
import copy
import hashlib
import json
from typing import Any


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')).hexdigest()


def _index(records, label: str):
    result = {}
    for item in records:
        key = item.get('persistent_id')
        if not isinstance(key, str) or not key:
            raise ValueError(f'{label}: missing persistent_id')
        if key in result:
            raise ValueError(f'{label}: duplicated persistent_id {key}')
        result[key] = item
    return result


def plan_materialization_synthetic(payload: dict) -> dict:
    """Construct a deterministic, non-executable region-delta preview for SYNTHETIC inputs.

    Outputs NO engine action, NO authenticated receipts, NO real ownership claims.
    """
    obj=copy.deepcopy(payload)
    if obj.get('source_kind') != 'SYNTHETIC_TEST':
        raise ValueError('Only SYNTHETIC_TEST fixtures are allowed')
    c=obj['context']; s=obj['snapshot']; o=obj['observation']; d=obj['desired']
    if c.get('fixture_only') is not True or c.get('build_fingerprint','').startswith('REAL-'):
        raise ValueError('Synthetic fixture gate not satisfied')
    keys=('campaign_id','branch_id','region_id','host_epoch','checkpoint_epoch',
          'build_fingerprint','pack_hash','ruleset_revision')
    for k in keys:
        if not isinstance(c.get(k), (str,int)) or c[k] in ('',None):
            raise ValueError(f'context missing {k}')
        for other,label in ((s,'snapshot'),(o,'observation'),(d,'desired')):
            if other.get(k)!=c[k]:
                raise ValueError(f'{label} mismatch {k}; fail closed')
    if c['time_mode'] not in ('FROZEN','PARTIAL','REALTIME'):
        raise ValueError('Unsupported time mode')
    if c['region_mode'] not in ('ACTIVE','NEAR','DISTANT','DORMANT'):
        raise ValueError('Unsupported region mode')
    if not all(isinstance(c[k],int) and not isinstance(c[k],bool) and c[k]>=0
               for k in ('world_tick','max_catchup_ticks','max_new_entities')):
        raise ValueError('Invalid tick/quotas')
    if not isinstance(s['last_confirmed_world_tick'],int) or s['last_confirmed_world_tick']>c['world_tick']:
        raise ValueError('Time regression: require explicit restore/reconciliation')
    if c['max_catchup_ticks']>100:
        raise ValueError('Synthetic catchup budget too large')
    if not isinstance(c['capabilities'],list) or len(c['capabilities'])!=len(set(c['capabilities'])):
        raise ValueError('Capability list invalid')
    if d['world_tick']!=c['world_tick']:
        raise ValueError('Desired projection stale')
    if o['coverage'] not in ('COMPLETE_SYNTHETIC','PARTIAL','UNKNOWN'):
        raise ValueError('Unknown observation coverage')

    snapshot=_index(s['entities'],'snapshot')
    observed=_index(o['entities'],'observation')
    desired=_index(d['entities'],'desired')
    pending=_index(obj.get('pending_actions',[]),'pending')
    pending_states={'PREPARED','DISPATCHED','UNCERTAIN'}
    caps=set(c['capabilities']); actions=[];created=0
    for pid in sorted(set(snapshot)|set(desired)):
        before=snapshot.get(pid); seen=observed.get(pid); want=desired.get(pid)
        action={'persistent_id':pid}
        def mark(intent,reason):
            action['intent']=intent; action['reason']=reason
        if pid in pending and pending[pid].get('state') in pending_states:
            mark('HOLD_RECONCILE','pending mechanical action: do not retry')
        elif before and before.get('owner_kind')!='INFINITY_AI':
            mark('BLOCKED_OWNERSHIP','snapshot not owned by Infinity AI')
        elif seen and seen.get('owner_kind')!='INFINITY_AI':
            mark('BLOCKED_OWNERSHIP','observed entity is native/mod/player/unknown')
        elif before and (not before.get('ownership_receipt_id') or
                         not before.get('instance_id')):
            mark('HOLD_RECONCILE','insufficient original ownership proof')
        elif before and seen and (seen.get('instance_id')!=before.get('instance_id') or
                                  seen.get('ownership_receipt_id')!=before.get('ownership_receipt_id')):
            mark('HOLD_RECONCILE','instance mismatch or recycled reference')
        elif before and not seen:
            mark('HOLD_RECONCILE','previously confirmed instance is not observed: absence is not proof')
        elif before and want is None:
            if o['coverage']!='COMPLETE_SYNTHETIC':
                mark('HOLD_RECONCILE','partial scan cannot support retirement review')
            elif not before.get('retire_eligible',False):
                mark('NO_OP','persistent entity is not a retire candidate')
            else:
                mark('REVIEW_RETIRE','review only; NEVER host DELETE or automatic despawn')
        elif before and want:
            if want.get('owner_kind')!='INFINITY_AI':
                mark('BLOCKED_OWNERSHIP','desired ownership contested')
            elif want.get('template_id') != before.get('template_id'):
                mark('HOLD_RECONCILE','template mismatch: no blind replacement')
            elif want.get('target_state') != before.get('confirmed_state'):
                if want.get('approved') is not True or 'PROPOSE_PATCH' not in caps:
                    mark('BLOCKED_CAPABILITY','patch not approved or not in synthetic allowlist')
                else:
                    mark('PROPOSE_UPDATE','synthetic approved target differs; no patch emitted')
            else:
                mark('NO_OP','confirmed entity and desired state agree')
        elif want and not before:
            if seen:
                mark('HOLD_RECONCILE','unsnapshotted observed entity: do not adopt')
            elif o['coverage']!='COMPLETE_SYNTHETIC':
                mark('HOLD_RECONCILE','no complete synthetic observation for absence')
            elif want.get('owner_kind')!='INFINITY_AI' or want.get('approved') is not True:
                mark('BLOCKED_AUTHORIZATION','not an authorized Infinity-owned target')
            elif want.get('risk')!='LOW':
                mark('BLOCKED_RISK','MEDIUM/HIGH not auto-authorized')
            elif not str(want.get('template_id','')).startswith('SYN-TEMPLATE-'):
                mark('BLOCKED_TEMPLATE','template not synthetic allowlisted')
            elif 'PROPOSE_CREATE' not in caps:
                mark('BLOCKED_CAPABILITY','create capability not in synthetic allowlist')
            elif created>=c['max_new_entities']:
                mark('BLOCKED_QUOTA','new-entity quota reached')
            else:
                created+=1;mark('PROPOSE_CREATE','synthetic proposal only, no engine spawn')
        else:
            mark('NO_OP','no delta to propose')
        actions.append(action)

    if c['time_mode']=='FROZEN':
        evaltick=s['last_confirmed_world_tick'];backlog=0
    else:
        evaltick=min(c['world_tick'],s['last_confirmed_world_tick']+c['max_catchup_ticks'])
        backlog=c['world_tick']-evaltick
    result={
       'status':'PROJECTION_ONLY',
       'region_id':c['region_id'],'world_tick_evaluated_through':evaltick,
       'remaining_backlog_ticks':backlog,
       'host_calls':0,'engine_mutations':0,
       'actions':actions,
       'warning':'SYNTHETIC PREVIEW ONLY: no BG2:EE/EEex capabilities or host receipts verified.'}
    result['plan_hash']=_digest(result)
    return result
