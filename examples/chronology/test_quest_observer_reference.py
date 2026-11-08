"""DEC-100/C. Unit tests for pure synthetic quest observation preflight; NO game integration."""
import copy
import json
import unittest
from pathlib import Path
from quest_observer_reference import observe_quest_synthetic

SRC=Path(__file__).parent

class QuestObservationSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.fixture=json.loads((SRC/'quest_observation_v1.synthetic.json').read_text('utf8'))
    def run_gate(self):
        return observe_quest_synthetic(self.fixture)
    def decision(self, rid='SYN-REQ-1'):
        return next(x for x in self.run_gate()['decisions'] if x['request_id']==rid)
    def request(self,rid='SYN-REQ-1'):
        return next(x for x in self.fixture['requests'] if x['request_id']==rid)
    def probe(self,pid='SYN-PROBE-1'):
        return next(x for x in self.fixture['manifest'] if x['probe_id']==pid)
    def observation(self,pid='SYN-PROBE-1'):
        return next(x for x in self.fixture['observations'] if x['probe_id']==pid)
    def test_no_engine_activity(self):
        r=self.run_gate()
        self.assertEqual(r['host_calls'],0)
        self.assertEqual(r['engine_mutations'],0)
        self.assertEqual(r['script_reads'],0)
        self.assertEqual(r['quest_writes'],0)
        self.assertEqual(r['disclosures_delivered'],0)
    def test_valid_milestone(self):
        self.assertEqual(self.decision()['status'],'RELEASE_SEMANTIC_MINIMAL')
        self.assertEqual(self.decision()['milestone'],'COMPLETED')
    def test_protected_quest_denied(self): self.assertEqual(self.decision('SYN-REQ-2')['status'],'BLOCKED_SPOILER')
    def test_private_party_allowed_to_party(self): self.assertEqual(self.decision('SYN-REQ-3')['status'],'RELEASE_SEMANTIC_MINIMAL')
    def test_input_immutable(self):
        before=copy.deepcopy(self.fixture)
        self.run_gate()
        self.assertEqual(self.fixture,before)
    def test_no_raw_flag_in_output(self):
        raw=json.dumps(self.run_gate())
        self.assertNotIn('SYNTHETIC-PRIVATE-NOT-FOR-OUTPUT',raw)
        self.assertNotIn('raw_internal_flag_value',raw)
    def test_secret_semantic_not_leaked(self):
        data=json.dumps(self.run_gate())
        self.assertNotIn('secret_outcome',data)
    def test_order_independent(self):
        before=self.run_gate()
        self.fixture['requests'].reverse()
        self.fixture['manifest'].reverse()
        self.fixture['observations'].reverse()
        self.assertEqual(self.run_gate(),before)
    def test_hash_present_and_deterministic(self):
        self.assertEqual(len(self.run_gate()['decision_sha256']),64)
        self.assertEqual(self.run_gate(),self.run_gate())
    def test_no_observation_is_unknown(self):
        self.fixture['observations']=[x for x in self.fixture['observations'] if x['probe_id']!='SYN-PROBE-1']
        self.assertEqual(self.decision()['status'],'UNKNOWN')
    def test_unmapped_probe_denied(self):
        self.request()['probe_id']='SYN-PROBE-NOT-ALLOWLISTED'
        self.assertEqual(self.decision()['status'],'BLOCKED_NOT_ALLOWLISTED')
    def test_false_with_full_coverage(self):
        self.observation()['semantic_value']='NOT_COMPLETED'
        self.assertEqual(self.decision()['milestone'],'NOT_COMPLETED')
    def test_false_with_partial_scan_not_allowed(self):
        self.observation()['semantic_value']='NOT_COMPLETED'
        self.observation()['coverage']='PARTIAL'
        self.assertEqual(self.decision()['status'],'UNKNOWN')
    def test_false_with_context_partial_not_allowed(self):
        self.observation()['semantic_value']='NOT_COMPLETED'
        self.fixture['context']['coverage']='PARTIAL'
        self.assertEqual(self.decision()['status'],'UNKNOWN')
    def test_positive_with_partial_scan(self):
        self.observation()['coverage']='PARTIAL'
        self.assertEqual(self.decision()['status'],'RELEASE_SEMANTIC_MINIMAL')
    def test_unavailable(self):
        self.observation()['read_state']='UNAVAILABLE'
        self.assertEqual(self.decision()['status'],'UNAVAILABLE')
    def test_unknown_read(self):
        self.observation()['read_state']='UNKNOWN'
        self.assertEqual(self.decision()['status'],'UNKNOWN')
    def test_stale_read(self):
        self.observation()['read_state']='STALE'
        self.assertEqual(self.decision()['status'],'STALE')
    def test_stale_host_epoch(self):
        self.observation()['host_epoch']=4
        self.assertEqual(self.decision()['status'],'STALE')
    def test_stale_checkpoint_epoch(self):
        self.observation()['checkpoint_epoch']=7
        self.assertEqual(self.decision()['status'],'STALE')
    def test_ttl_expired(self):
        self.observation()['observed_tick']=70
        self.assertEqual(self.decision()['status'],'STALE')
    def test_future_observation_denied(self):
        self.observation()['observed_tick']=101
        self.assertEqual(self.decision()['status'],'STALE')
    def test_unknown_semantic(self):
        self.observation()['semantic_value']='UNKNOWN'
        self.assertEqual(self.decision()['status'],'UNKNOWN')
    def test_non_fixture_rejected(self):
        self.fixture['source_kind']='REAL_GAME'
        with self.assertRaises(ValueError):self.run_gate()
    def test_live_host_rejected(self):
        self.fixture['context']['host_mode']='LIVE'
        with self.assertRaises(ValueError):self.run_gate()
    def test_real_build_rejected(self):
        self.fixture['context']['build_fingerprint']='REAL-HASH'
        with self.assertRaises(ValueError):self.run_gate()
    def test_real_modpack_rejected(self):
        self.fixture['context']['modpack_hash']='REAL-HASH'
        with self.assertRaises(ValueError):self.run_gate()
    def test_duplicate_request_id_rejected(self):
        self.fixture['requests'].append(copy.deepcopy(self.request()))
        with self.assertRaises(ValueError):self.run_gate()
    def test_duplicate_manifest_probe_rejected(self):
        self.fixture['manifest'].append(copy.deepcopy(self.probe()))
        with self.assertRaises(ValueError):self.run_gate()
    def test_duplicate_observation_rejected(self):
        self.fixture['observations'].append(copy.deepcopy(self.observation()))
        with self.assertRaises(ValueError):self.run_gate()
    def test_missing_scope_rejected(self):
        self.fixture['context'].pop('branch_id')
        with self.assertRaises(ValueError):self.run_gate()
    def test_boolean_epoch_rejected(self):
        self.fixture['context']['host_epoch']=True
        with self.assertRaises(ValueError):self.run_gate()
    def test_unknown_coverage_rejected(self):
        self.fixture['context']['coverage']='FULL_UNKNOWN_NOT_ALLOWED'
        with self.assertRaises(ValueError):self.run_gate()
    def test_invalid_observation_value_rejected(self):
        self.observation()['semantic_value']='VICTORY_OF_HIDDEN_VILLAIN'
        with self.assertRaises(ValueError):self.run_gate()
    def test_empty_audiences_rejected(self):
        self.probe()['audiences']=[]
        with self.assertRaises(ValueError):self.run_gate()
    def test_invalid_sensitivity_rejected(self):
        self.probe()['sensitivity']='OMNISCIENT'
        with self.assertRaises(ValueError):self.run_gate()
    def test_unverified_capability_denied(self):
        self.probe()['validation']='UNVERIFIED'
        self.assertEqual(self.decision()['status'],'BLOCKED_CAPABILITY')
    def test_unverified_explicit_probe_denied(self):
        self.fixture['requests'].append({**self.request(),'request_id':'SYN-REQ-X','probe_id':'SYN-PROBE-UNVERIFIED'})
        d=self.decision('SYN-REQ-X')
        self.assertEqual(d['status'],'BLOCKED_CAPABILITY')
    def test_no_narrative_entitlement(self):
        self.request()['knowledge_entitled']=False
        self.assertEqual(self.decision()['status'],'BLOCKED_KNOWLEDGE')
    def test_no_release_authorization(self):
        self.request()['release_authorized']=False
        self.assertEqual(self.decision()['status'],'BLOCKED_KNOWLEDGE')
    def test_unlisted_audience_denied(self):
        self.request()['audience']='HIDDEN-ENEMY'
        self.assertEqual(self.decision()['status'],'BLOCKED_ACCESS')
    def test_other_purpose_denied(self):
        self.request()['purpose']='INTERCEPT_PRIVATE_FLAGS'
        self.assertEqual(self.decision()['status'],'BLOCKED_ACCESS')
    def test_quest_secret_denied_even_when_allowlisted(self):
        self.probe()['sensitivity']='QUEST_SECRET'
        self.assertEqual(self.decision()['status'],'BLOCKED_SPOILER')
    def test_state_changes_do_not_write(self):
        self.observation()['semantic_value']='NOT_COMPLETED'
        self.assertEqual(self.run_gate()['engine_mutations'],0)
    def test_partial_unknown_global(self):
        self.fixture['context']['coverage']='UNKNOWN'
        self.assertEqual(self.decision()['status'],'UNKNOWN')


# Generated from an explicit adversarial matrix; all cases remain synthetic.
def _add_variant(name,path,value,expected):
    def f(self):
        node=self.fixture
        parts=path.split('.')
        for key in parts[:-1]:
            node=node[int(key)] if key.isdigit() else node[key]
        node[parts[-1]]=value
        self.assertEqual(self.decision()['status'],expected)
    setattr(QuestObservationSyntheticTests,'test_variant_'+name,f)
_add_variant('campaign_mismatch','requests.0.campaign_id','OTHER','BLOCKED_ACCESS')
_add_variant('branch_mismatch','requests.0.branch_id','OTHER','BLOCKED_ACCESS')
_add_variant('session_mismatch','requests.0.session_id','OTHER','BLOCKED_ACCESS')
_add_variant('host_epoch_mismatch','requests.0.host_epoch',99,'BLOCKED_ACCESS')
_add_variant('checkpoint_epoch_mismatch','requests.0.checkpoint_epoch',99,'BLOCKED_ACCESS')
_add_variant('build_mismatch_request','requests.0.build_fingerprint','SYN-OTHER','BLOCKED_ACCESS')
_add_variant('modpack_mismatch_request','requests.0.modpack_hash','SYN-OTHER','BLOCKED_ACCESS')
_add_variant('adapter_mismatch_request','requests.0.adapter_revision','SYN-OTHER','BLOCKED_ACCESS')
_add_variant('policy_mismatch_request','requests.0.policy_revision','SYN-OTHER','BLOCKED_ACCESS')
_add_variant('manifest_build_mismatch','manifest.0.build_fingerprint','SYN-OTHER','BLOCKED_CAPABILITY')
_add_variant('manifest_modpack_mismatch','manifest.0.modpack_hash','SYN-OTHER','BLOCKED_CAPABILITY')
_add_variant('manifest_adapter_mismatch','manifest.0.adapter_revision','SYN-OTHER','BLOCKED_CAPABILITY')
_add_variant('future_branch_hidden','manifest.0.sensitivity','FUTURE_BRANCH','BLOCKED_SPOILER')
_add_variant('hidden_identity','manifest.0.sensitivity','HIDDEN_IDENTITY','BLOCKED_SPOILER')
_add_variant('private_romance','manifest.0.sensitivity','ROMANCE_PRIVATE','BLOCKED_SPOILER')
_add_variant('private_party_to_director','manifest.0.sensitivity','PARTY_PRIVATE','RELEASE_SEMANTIC_MINIMAL')
_add_variant('no_probe_knowledge','requests.0.knowledge_entitled',None,'BLOCKED_KNOWLEDGE')
_add_variant('no_probe_release','requests.0.release_authorized',None,'BLOCKED_KNOWLEDGE')
_add_variant('read_stale','observations.0.read_state','STALE','STALE')
_add_variant('read_unknown','observations.0.read_state','UNKNOWN','UNKNOWN')
_add_variant('read_unavailable','observations.0.read_state','UNAVAILABLE','UNAVAILABLE')
_add_variant('observation_coverage_unknown','observations.0.coverage','UNKNOWN','UNKNOWN')
_add_variant('observation_value_unknown','observations.0.semantic_value','UNKNOWN','UNKNOWN')
_add_variant('manifest_ttl_short','manifest.0.max_age_ticks',1,'STALE')
_add_variant('manifest_ttl_exact','manifest.0.max_age_ticks',2,'RELEASE_SEMANTIC_MINIMAL')
_add_variant('observed_tick_exact','observations.0.observed_tick',100,'RELEASE_SEMANTIC_MINIMAL')
