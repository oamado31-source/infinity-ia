"""DEC-100/C: pure read-only gate for SYNTHETIC quest-state observations.

NOT a BG2:EE/EEex bridge, NOT a runtime capability check, NOT proof of POC.
Does not invoke a host, access quest files, use network, mutate inputs, or dispatch actions.
The fixture token SYNTHETIC_VERIFIED applies ONLY inside test fixtures.
"""
from __future__ import annotations
import copy
import hashlib
import json

_SCOPE = ('campaign_id','branch_id','session_id','host_epoch','checkpoint_epoch',
          'build_fingerprint','modpack_hash','adapter_revision','policy_revision')
_SECRET = frozenset({'QUEST_SECRET','FUTURE_BRANCH','HIDDEN_IDENTITY','ROMANCE_PRIVATE'})
_VALUES = frozenset({'COMPLETED','NOT_COMPLETED','UNKNOWN'})
_COVERAGE = frozenset({'FULL_SYNTHETIC','PARTIAL','UNKNOWN'})
_STATES = frozenset({'AVAILABLE','UNAVAILABLE','STALE','UNKNOWN'})


def observe_quest_synthetic(payload: dict) -> dict:
    """Return a minimal non-disclosing preview. Never query or mutate a live engine."""
    p = copy.deepcopy(payload)
    c = p.get('context', {})
    if p.get('source_kind') != 'SYNTHETIC_TEST' or c.get('fixture_only') is not True:
        raise ValueError('Only synthetic test fixtures are permitted')
    if c.get('host_mode') != 'SYNTHETIC_HOST_FIXTURE':
        raise ValueError('No live host mode permitted')
    for k in _SCOPE:
        if k not in c or c[k] is None or c[k] == '':
            raise ValueError('Invalid or absent scope: ' + k)
    for k in ('host_epoch','checkpoint_epoch','snapshot_tick'):
        if type(c.get(k)) is not int or c[k] < 0:
            raise ValueError('Invalid tick or epoch: ' + k)
    for k in ('build_fingerprint','modpack_hash'):
        if not str(c[k]).startswith('SYN-'):
            raise ValueError('Real engine/build references are prohibited')
    if c.get('coverage') not in _COVERAGE:
        raise ValueError('Invalid coverage')
    for k in ('manifest','observations','requests'):
        if not isinstance(p.get(k),list):
            raise ValueError('Expected array: ' + k)
    m = {}
    for item in p['manifest']:
        pid = item.get('probe_id')
        if not isinstance(pid,str) or not pid or pid in m:
            raise ValueError('Duplicate/invalid probe_id')
        if item.get('sensitivity') not in _SECRET | {'PUBLIC_PROGRESS','PARTY_PRIVATE'}:
            raise ValueError('Invalid sensitivity')
        if not isinstance(item.get('audiences'), list) or not item['audiences']:
            raise ValueError('Manifest audiences absent')
        if type(item.get('max_age_ticks')) is not int or item['max_age_ticks'] < 0:
            raise ValueError('Invalid TTL')
        if not isinstance(item.get('semantic_key'),str) or not item['semantic_key']:
            raise ValueError('Invalid semantic_key')
        m[pid] = item
    obs = {}
    for item in p['observations']:
        pid=item.get('probe_id')
        if not isinstance(pid,str) or not pid or pid in obs:
            raise ValueError('Duplicate/invalid observation probe_id')
        if item.get('read_state') not in _STATES or item.get('coverage') not in _COVERAGE or item.get('semantic_value') not in _VALUES:
            raise ValueError('Invalid observation state')
        if type(item.get('observed_tick')) is not int:
            raise ValueError('Invalid observed tick')
        obs[pid] = item
    requests={}
    for item in p['requests']:
        rid=item.get('request_id')
        if not isinstance(rid,str) or not rid or rid in requests:
            raise ValueError('Duplicate/invalid request id')
        requests[rid]=item
    output=[]
    for rid, r in sorted(requests.items()):
        item={'request_id':rid}
        def result(status, reason):
            item['status']=status
            item['reason_code']=reason
        if any(r.get(k)!=c[k] for k in _SCOPE):
            result('BLOCKED_ACCESS','SCOPE_OR_REVISION_MISMATCH')
        elif not isinstance(r.get('probe_id'),str) or r['probe_id'] not in m:
            result('BLOCKED_NOT_ALLOWLISTED','PROBE_NOT_ALLOWED')
        else:
            pr=m[r['probe_id']]
            if pr.get('sensitivity') in _SECRET:
                result('BLOCKED_SPOILER','PROTECTED_QUEST_INFORMATION')
            elif r.get('purpose')!=pr.get('purpose') or r.get('audience') not in pr['audiences']:
                result('BLOCKED_ACCESS','AUDIENCE_OR_PURPOSE_NOT_ALLOWED')
            elif any(pr.get(k)!=c[k] for k in ('build_fingerprint','modpack_hash','adapter_revision')) or pr.get('validation')!='SYNTHETIC_VERIFIED':
                result('BLOCKED_CAPABILITY','NO_MATCHING_SYNTHETIC_CAPABILITY')
            elif r.get('knowledge_entitled') is not True or r.get('release_authorized') is not True:
                result('BLOCKED_KNOWLEDGE','NARRATIVE_RELEASE_NOT_AUTHORIZED')
            elif c['coverage']=='UNKNOWN':
                result('UNKNOWN','OBSERVATION_COVERAGE_UNKNOWN')
            else:
                ob=obs.get(r['probe_id'])
                if ob is None:
                    result('UNKNOWN','OBSERVATION_NOT_AVAILABLE')
                elif ob['read_state']=='UNAVAILABLE':
                    result('UNAVAILABLE','PROBE_UNAVAILABLE')
                elif ob['read_state']=='STALE' or ob.get('host_epoch')!=c['host_epoch'] or ob.get('checkpoint_epoch')!=c['checkpoint_epoch']:
                    result('STALE','EPOCH_OR_CACHE_STALE')
                elif ob['read_state']=='UNKNOWN' or ob['coverage']=='UNKNOWN':
                    result('UNKNOWN','OBSERVATION_UNKNOWN')
                elif ob['observed_tick']>c['snapshot_tick'] or c['snapshot_tick']-ob['observed_tick']>pr['max_age_ticks']:
                    result('STALE','OBSERVATION_TTL_EXPIRED')
                elif ob['semantic_value']=='UNKNOWN' or (ob['semantic_value']=='NOT_COMPLETED' and (ob['coverage']!='FULL_SYNTHETIC' or c['coverage']!='FULL_SYNTHETIC')):
                    result('UNKNOWN','INSUFFICIENT_EVIDENCE_FOR_NEGATIVE')
                elif ob['semantic_value'] in ('COMPLETED','NOT_COMPLETED'):
                    # Deliberately omit source flag, script, quest branching, raw value, ID and provenance text.
                    result('RELEASE_SEMANTIC_MINIMAL','SYNTHETIC_POLICY_RELEASE')
                    item['semantic_key']=pr['semantic_key']
                    item['milestone']=ob['semantic_value']
                else:
                    result('UNKNOWN','UNMAPPED_OBSERVATION')
        output.append(item)
    out={'mode':'SYNTHETIC_PREVIEW_ONLY','host_calls':0,'engine_mutations':0,
         'script_reads':0,'quest_writes':0,'disclosures_delivered':0,
         'decisions':output,
         'warning':'SYNTHETIC ONLY: not a BG2:EE/EEex observation, permission or POC.'}
    out['decision_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,ensure_ascii=False,
                                     separators=(',',':')).encode('utf8')).hexdigest()
    return out
