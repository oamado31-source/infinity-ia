"""Infinity AI chronology filter *reference*, DEC-096 proposal (NOT approved).

Pure deterministic unit-only demonstration.  Synthetic fixtures only; NO canon
imports, database writes, engine bridge, host dispatch, NPC knowledge updates,
or game-side effects.  Security/JSON schema validation remains candidate SPEC.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

F = Path(__file__).resolve().parent
ALLOWLIST_FIELDS = frozenset({'regional_alert', 'campaign_phase', 'canon_divergence'})


def load_synthetic_catalog() -> dict:
    catalog = json.loads((F/'events.synthetic.json').read_text(encoding='utf-8'))
    if catalog.get('fixture_only') is not True or catalog.get('schema_version')!='0.1-draft':
        raise ValueError('Not an approved synthetic fixture catalog')
    if any(e.get('source_kind') != 'SYNTHETIC_TEST' for e in catalog['events']):
        raise ValueError('A non-synthetic source is forbidden in this prototype')
    return catalog


def _check_conditions(conditions: list[dict], known: dict[str, Any]) -> bool:
    for cond in conditions:
        field, op, value = cond['field'], cond['op'], cond['value']
        if field not in ALLOWLIST_FIELDS:
            raise ValueError(f'Unknown field: {field}')
        if field not in known:
            return False
        observed = known[field]
        if op == 'EQ':
            if type(observed) is not type(value) or observed != value:
                return False
        elif op == 'IN':
            if not isinstance(value, list) or observed not in value:
                return False
        else:
            raise ValueError(f'Unknown operator: {op}')
    return True


def proposals(catalog: dict, context: dict, applied_effect_ids=frozenset()) -> list[dict]:
    """Returns proposals only. No writes, no host effects, no permanent knowledge."""
    if not catalog.get('fixture_only') or context.get('fixture_only') is not True:
        raise ValueError('Fixture-only demonstration; never feed real canon!')
    if not context.get('pack_pinned') or not context.get('branch_authorized'):
        return []
    known = context.get('conditions', {})
    results = []
    for ev in sorted(catalog['events'], key=lambda e:e['event_id']):
        if ev.get('source_kind') != 'SYNTHETIC_TEST':
            raise ValueError('Non-synthetic event')
        when=ev['time']
        # No assumed activation date for YEAR_ONLY, DISPUTED or unknown month.
        if when.get('precision')!='MONTH' or 'month' not in when:
            continue
        if (when['year_dr'],when['month']) != (context['year_dr'],context['month']):
            continue
        scope=ev['scope']
        if context['region_id'] not in scope['regions'] or context['location_tag'] not in scope['location_tags']:
            continue
        if ev['event_id'] not in context.get('confirmed_event_ids', []):
            continue
        if not set(ev.get('verified_prerequisites',[])).issubset(set(context.get('confirmed_event_ids',[]))):
            continue
        if not _check_conditions(ev['conditions'],known):
            continue
        for effect in ev['effects']:
            if effect['kind']=='INDIRECT' and effect.get('requires_applied_effect') not in applied_effect_ids:
                continue
            # Ledger checking is a dry-run dedup: real atomic idempotency is NOT implemented.
            dedup_key = ':'.join([context['campaign_id'],context['branch_id'],
                                  str(context['branch_epoch']),ev['event_id'],effect['effect_id'],
                                  context['region_id'],context['location_tag']])
            if dedup_key in context.get('already_applied_keys',[]):
                continue
            results.append({'kind':'IMPACT_PROPOSAL_ONLY','event_id':ev['event_id'],
                            'effect_id':effect['effect_id'],'risk':effect['risk'],
                            'metric':effect['metric'],'delta':effect['delta'],
                            'cap':effect['cap'],'dedup_key':dedup_key})
    return results


if __name__ == '__main__':
    fixture=load_synthetic_catalog()
    context={'fixture_only':True,'pack_pinned':True,'branch_authorized':True,
             'campaign_id':'C-TEST','branch_id':'B-TEST','branch_epoch':1,
             'year_dr':1369,'month':7,'region_id':'region-example',
             'location_tag':'road','confirmed_event_ids':['SYN-PORT-ALERT-1'],
             'conditions':{'regional_alert':True,'canon_divergence':False}}
    print(json.dumps(proposals(fixture,context),ensure_ascii=False,indent=2))
