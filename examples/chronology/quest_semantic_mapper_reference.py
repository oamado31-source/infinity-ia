"""DEC-101/C — pure synthetic quest semantic mapper.

No BG2:EE/EEex hooks, files, network, model, host calls or engine operations.
Use solely to test bounded deterministic mapping and information minimization.
"""
from __future__ import annotations
import copy

_SCOPE = ('campaign_id','branch_id','session_id','build_fingerprint',
          'modpack_hash','adapter_revision','mapping_revision','host_epoch','checkpoint_epoch')
_SECRET = frozenset({'QUEST_SECRET','FUTURE_BRANCH','HIDDEN_IDENTITY','ROMANCE_PRIVATE'})
_KNOWN = _SECRET | {'PUBLIC_PROGRESS','PARTY_PRIVATE'}


def map_semantics_synthetic(payload: dict) -> dict:
    """Return a *minimal* decision; never interpret any real game input."""
    p=copy.deepcopy(payload)
    c=p.get('context',{})
    if p.get('source_kind')!='SYNTHETIC_TEST' or c.get('fixture_only') is not True or c.get('host_mode')!='SYNTHETIC_HOST_FIXTURE':
        raise ValueError('Synthetic fixtures only')
    for k in _SCOPE:
        if not c.get(k) and c.get(k)!=0: raise ValueError('Missing scope: '+k)
    for k in ('build_fingerprint','modpack_hash','mapping_revision'):
        if not isinstance(c[k],str) or not c[k].startswith('SYN-'):
            raise ValueError('Synthetic versions only')
    for k in ('host_epoch','checkpoint_epoch','snapshot_tick'):
        if type(c.get(k)) is not int or c[k]<0:
            raise ValueError('Invalid epoch/tick')
    if not isinstance(p.get('catalog'),list) or not isinstance(p.get('observations'),list) or not isinstance(p.get('request'),dict):
        raise ValueError('Invalid fixture shape')
    req=p['request']
    policy=p.get('policy',{})
    history=p.get('history',{})
    # Distinct trusted synthetic fixtures, NEVER grants supplied by the request.
    if policy.get('trusted_kind')!='SYNTHETIC_POLICY_FIXTURE' or not str(policy.get('grant_revision','')).startswith('SYN-'):
        return _result(req,'BLOCKED_ACL','UNTRUSTED_POLICY')
    if history.get('trusted_kind')!='SYNTHETIC_HISTORY_FIXTURE' or any(history.get(k)!=c[k] for k in ('host_epoch','checkpoint_epoch')):
        return _result(req,'BLOCKED_TRANSITION','UNTRUSTED_HISTORY')
    if req.get('audience') not in policy.get('audiences',[]) or req.get('purpose') not in policy.get('purposes',[]):
        return _result(req,'BLOCKED_ACL','POLICY_DENIED')
    if any(req.get('scope',{}).get(k)!=c[k] for k in _SCOPE):
        return _result(req,'BLOCKED_ACL','SCOPE_MISMATCH')
    matches=[m for m in p['catalog'] if m.get('mapping_id')==req.get('mapping_id')]
    if len(matches)!=1:
        return _result(req,'BLOCKED_MAPPING','CATALOG_NOT_UNIQUE')
    cat=matches[0]
    if any(cat.get(k)!=c[k] for k in ('build_fingerprint','modpack_hash','mapping_revision')):
        return _result(req,'BLOCKED_MAPPING','VERSION_NOT_PINNED')
    if cat.get('review_status')!='CURATED_SYNTHETIC' or not str(cat.get('curation_evidence','')).startswith('SYN-'):
        return _result(req,'BLOCKED_MAPPING','CURATION_NOT_APPROVED')
    obs={}
    for o in p['observations']:
        key=o.get('probe_id')
        if not isinstance(key,str) or not key.startswith('SYN-') or key in obs:
            return _result(req,'CONTRADICTORY','BAD_OBSERVATION_SET')
        obs[key]=o
    hits=[]
    stale=False
    for rule in cat.get('milestones',[]):
        if rule.get('classification') not in _KNOWN or not isinstance(rule.get('predicates'),list) or not rule['predicates']:
            return _result(req,'BLOCKED_MAPPING','INVALID_RULE')
        evidence_complete=True
        predicates_met=True
        for cond in rule['predicates']:
            if cond.get('op') not in ('eq','in') or not str(cond.get('probe_id','')).startswith('SYN-'):
                return _result(req,'BLOCKED_MAPPING','INVALID_PREDICATE')
            o=obs.get(cond['probe_id'])
            if o is None or o.get('read_state') not in ('AVAILABLE',) or o.get('coverage') not in ('FULL_SYNTHETIC','PARTIAL'):
                evidence_complete=False;predicates_met=False;break
            tick=o.get('observed_tick')
            ttl=policy.get('max_age_ticks',-1)
            if type(tick) is not int or type(ttl) is not int or ttl<0 or tick>c['snapshot_tick'] or c['snapshot_tick']-tick>ttl:
                stale=True; evidence_complete=False;predicates_met=False;break
            val=o.get('semantic_value')
            if cond['op']=='eq':
                if type(val)!=type(cond.get('value')) or val!=cond['value']: predicates_met=False
            else:
                allowed=cond.get('value')
                if not isinstance(allowed,list) or not allowed:
                    return _result(req,'BLOCKED_MAPPING','INVALID_PREDICATE')
                if not any(type(val)==type(v) and val==v for v in allowed): predicates_met=False
        if evidence_complete and predicates_met:
            hits.append(rule)
    if not hits:
        return _result(req,'STALE' if stale else 'UNKNOWN','STALE_OBSERVATION' if stale else 'INSUFFICIENT_EVIDENCE')
    # Exclusive matches: never apply arbitrary priority or last-read wins.
    by_group={}
    for h in hits: by_group.setdefault(h.get('exclusive_group'),[]).append(h)
    if any(len(v)>1 for v in by_group.values()) or len(hits)>1:
        return _result(req,'AMBIGUOUS','MULTIPLE_SEMANTIC_MATCHES')
    h=hits[0]
    if history.get('prior_milestone') not in h.get('allowed_previous',[]):
        return _result(req,'BLOCKED_TRANSITION','TRANSITION_NOT_CURATED')
    if h.get('classification') in _SECRET:
        return _result(req,'BLOCKED_SPOILER','SENSITIVE_MILESTONE')
    if not policy.get('knowledge_granted') or h.get('semantic_id') not in policy.get('allowed_semantic_ids',[]):
        return _result(req,'OBSERVED_TECHNICAL_ONLY','KNOWLEDGE_OR_ACL_DENIED')
    if h['classification']=='PARTY_PRIVATE' and req.get('audience')!='PARTY':
        return _result(req,'BLOCKED_ACL','AUDIENCE_DENIED')
    if req.get('purpose')!='NARRATIVE_PROGRESS':
        return _result(req,'BLOCKED_ACL','PURPOSE_DENIED')
    # This key is author-approved synthetic and never derived from raw flag names.
    return _result(req,'RELEASE_SEMANTIC_MINIMAL','CURATED_MATCH',h['semantic_id'])


def _result(req,status,reason,semantic_id=None):
    result={'request_id':str(req.get('request_id','SYN-UNKNOWN')),
            'status':status,'reason_code':reason,
            'host_calls':0,'quest_writes':0,'llm_calls':0,'delivered_to_npc':False}
    if semantic_id is not None:result['safe_milestone_id']=semantic_id
    return result
