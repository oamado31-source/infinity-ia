"""DEC-097 synthetic-only deterministic effect composition reference.

NO Forgotten Realms canon ingestion, engine writes, NPC materialization, real host receipts,
side effects or game/network integration. A `SYN-RECEIPT` is a fake test marker ONLY.
This reference demonstrates arithmetic, order independence and safe suppression.
"""
from __future__ import annotations
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_EVEN
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ALLOWED_METRICS=frozenset({'food_price','patrol_intensity'})
ALLOWED_UNITS={'food_price':('COIN','BASELINE_PLUS_BPS'),
               'patrol_intensity':('INTENSITY','ADD_ABSOLUTE')}


def load_fixture():
    fixture=json.loads((HERE/'composition_v1.synthetic.json').read_text(encoding='utf-8'))
    if fixture.get('source_kind')!='SYNTHETIC_TEST' or fixture.get('fixture_only') is not True:
        raise ValueError('Only test fixture data accepted')
    return fixture


def _weight_bp(effect,world_day):
    start,hold,fade=effect['world_day_start'],effect['hold_days'],effect['fade_days']
    if any(type(n) is not int or n<0 for n in (start,hold,fade,world_day)):
        raise ValueError('Invalid world-day parameters')
    elapsed=world_day-start
    if elapsed<0: return 0
    if elapsed<hold: return 10000
    if fade==0 or elapsed>=hold+fade: return 0
    return ((hold+fade-elapsed)*10000)//fade


def _validate_structure(data):
    if data.get('fixture_only') is not True or data.get('source_kind')!='SYNTHETIC_TEST':
        raise ValueError('Fixture only')
    ctx=data['context']
    if ctx.get('fixture_only') is not True or not isinstance(ctx.get('pack_hash'),str) or len(ctx['pack_hash'])!=64:
        raise ValueError('Fixture context and pack pin required')
    if any(type(ctx.get(n)) is not int or ctx[n]<0 for n in ('world_day','epoch')) or ctx['epoch']==0:
        raise ValueError('Invalid epoch or world-day')
    policies={}
    for p in data['policies']:
        mid=p['metric_id']
        if mid not in ALLOWED_METRICS or (p['unit'],p['operator'])!=ALLOWED_UNITS[mid]:
            raise ValueError('Unknown metric or incompatible operator/unit')
        if mid in policies or p['min']>p['max'] or not (p['min']<=p['baseline']<=p['max']):
            raise ValueError('Duplicate/invalid metric policy')
        if p['rounding']!='HALF_EVEN' or type(p['baseline']) is not int:
            raise ValueError('Rounding/baseline invalid')
        policies[mid]=p
    if not policies: raise ValueError('No metric policies')
    parent={e['effect_id']:e.get('requires_parent_effect_id') for e in data['effects']
            if e.get('requires_parent_effect_id')}
    def visit(n,path):
        if n in path: raise ValueError('Causal effect cycle')
        if n in parent: visit(parent[n],path|{n})
    for e in parent: visit(e,set())
    return ctx,policies


def compose_synthetic(data):
    """Read-only projection, never an actual game effect. Strictly synthetic."""
    ctx,policies=_validate_structure(data)
    skipped={}; candidates={m:[] for m in policies}; seen={}
    # A stable traversal order is used only for logs; mathematical output is order independent.
    for effect in sorted(data['effects'],key=lambda e:(e['effect_id'],e['event_id'])):
        eid=effect['effect_id']
        if eid in seen:
            if effect!=seen[eid]: raise ValueError('Conflicting duplicate effect ID')
            skipped[eid]='DUPLICATE_IDENTICAL'
            continue
        seen[eid]=effect
        if effect.get('source_kind')!='SYNTHETIC_TEST':raise ValueError('Real/non-test input forbidden')
        metric=effect.get('metric_id')
        if metric not in policies:raise ValueError('Unknown metric policy')
        if any(effect.get(k)!=ctx[k] for k in ('campaign_id','branch_id','epoch','pack_hash','scope_id')):
            skipped[eid]='WRONG_CONTEXT';continue
        if effect.get('status')!='CONFIRMED':
            skipped[eid]='NOT_CONFIRMED';continue
        if not effect.get('host_receipt_id') or not str(effect['host_receipt_id']).startswith('SYN-RECEIPT-'):
            skipped[eid]='MISSING_SYNTHETIC_RECEIPT';continue
        if effect.get('authorized') is not True or effect.get('risk')=='HIGH':
            skipped[eid]='AUTHORIZATION_REQUIRED';continue
        if effect.get('requires_parent_effect_id') and effect['requires_parent_effect_id'] not in ctx['confirmed_parent_ids']:
            skipped[eid]='UNCONFIRMED_PARENT';continue
        if type(effect.get('delta')) is not int or abs(effect['delta'])>1000000:
            raise ValueError('Invalid delta')
        weight=_weight_bp(effect,ctx['world_day'])
        if weight==0:
            skipped[eid]='OUTSIDE_WINDOW';continue
        if not isinstance(effect.get('stack_family'),str) or not effect['stack_family']:
            raise ValueError('Missing family policy')
        candidates[metric].append((effect,weight))
    targets={}; included={}; conflicts={}; components={}
    for metric,items in sorted(candidates.items()):
        families={}
        for eff,weight in items:
            families.setdefault(eff['stack_family'],[]).append((eff,weight))
        selected=[]
        for family,versions in sorted(families.items()):
            high=max(v[0]['priority'] for v in versions)
            leaders=[v for v in versions if v[0]['priority']==high]
            if len(leaders)!=1:
                conflicts[f'{metric}/{family}']=sorted(v[0]['effect_id'] for v in leaders)
                for e,_ in leaders:skipped[e['effect_id']]='TIED_EXCLUSIVE_FAMILY'
                for e,_ in versions:
                    if e['priority']!=high:skipped[e['effect_id']]='LOWER_PRIORITY'
                continue
            chosen=leaders[0]; selected.append(chosen)
            for other,_ in versions:
                if other['effect_id']!=chosen[0]['effect_id']:
                    skipped[other['effect_id']]='LOWER_PRIORITY'
        policy=policies[metric]
        # Decimal arithmetic avoids binary floats and defers rounding until final target.
        weighted_sum=sum((Decimal(e['delta'])*Decimal(w)/Decimal(10000) for e,w in selected),Decimal(0))
        if policy['operator']=='BASELINE_PLUS_BPS':
            unbounded=Decimal(policy['baseline'])*(Decimal(1)+weighted_sum/Decimal(10000))
        else:
            unbounded=Decimal(policy['baseline'])+weighted_sum
        bounded=max(Decimal(policy['min']),min(Decimal(policy['max']),unbounded))
        targets[metric]=int(bounded.quantize(Decimal('1'),rounding=ROUND_HALF_EVEN))
        included[metric]=sorted(e['effect_id'] for e,w in selected)
        components[metric]=[{'effect_id':e['effect_id'],'weight_bp':w,'delta':e['delta']}
                            for e,w in sorted(selected,key=lambda t:t[0]['effect_id'])]
    return {'status':'PROJECTION_ONLY','targets':targets,'included':included,
            'conflicts':conflicts,'skipped':dict(sorted(skipped.items())),
            'components':components}


if __name__=='__main__':
    print(json.dumps(compose_synthetic(load_fixture()),ensure_ascii=False,indent=2))
