"""Unit tests solely for DEC-101 synthetic semantic mapper."""
import copy
import json
import pathlib
import unittest
from quest_semantic_mapper_reference import map_semantics_synthetic
BASE=json.loads(pathlib.Path(__file__).with_name('quest_semantics_v1.synthetic.json').read_text())

class QuestSemanticMapperTests(unittest.TestCase):
    def p(self): return copy.deepcopy(BASE)
    def status(self,p):return map_semantics_synthetic(p)['status']
    def test_happy_path(self):
        o=map_semantics_synthetic(self.p())
        self.assertEqual(o['status'],'RELEASE_SEMANTIC_MINIMAL')
        self.assertEqual(o['safe_milestone_id'],'SYN-QUEST-OBJECTIVE-DONE')
        self.assertEqual((o['host_calls'],o['quest_writes'],o['llm_calls']),(0,0,0))
        self.assertFalse(o['delivered_to_npc'])
    def test_no_input_mutation(self):
        p=self.p();before=copy.deepcopy(p);map_semantics_synthetic(p);self.assertEqual(p,before)
    def test_reject_real_source(self):
        p=self.p();p['source_kind']='REAL';self.assertRaises(ValueError,map_semantics_synthetic,p)
    def test_reject_live_host(self):
        p=self.p();p['context']['host_mode']='LIVE';self.assertRaises(ValueError,map_semantics_synthetic,p)
    def test_reject_real_build(self):
        p=self.p();p['context']['build_fingerprint']='BG2:EE';self.assertRaises(ValueError,map_semantics_synthetic,p)
    def test_reject_boolean_epoch(self):
        p=self.p();p['context']['host_epoch']=True;self.assertRaises(ValueError,map_semantics_synthetic,p)
    def test_scope_mismatch(self):
        p=self.p();p['request']['scope']['branch_id']='SYN-OTHER';self.assertEqual(self.status(p),'BLOCKED_ACL')
    def test_missing_catalog(self):
        p=self.p();p['catalog']=[];self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_duplicate_mapping(self):
        p=self.p();p['catalog'].append(copy.deepcopy(p['catalog'][0]));self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_wrong_build(self):
        p=self.p();p['catalog'][0]['build_fingerprint']='SYN-OTHER';self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_wrong_modpack(self):
        p=self.p();p['catalog'][0]['modpack_hash']='SYN-OTHER';self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_wrong_mapping_revision(self):
        p=self.p();p['catalog'][0]['mapping_revision']='SYN-OLD';self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_unreviewed_catalog(self):
        p=self.p();p['catalog'][0]['review_status']='DRAFT';self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_missing_evidence(self):
        p=self.p();p['catalog'][0]['curation_evidence']='';self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_missing_probe_not_false(self):
        p=self.p();p['observations'].pop();self.assertEqual(self.status(p),'UNKNOWN')
    def test_unavailable_probe(self):
        p=self.p();p['observations'][0]['read_state']='UNAVAILABLE';self.assertEqual(self.status(p),'UNKNOWN')
    def test_partial_positive_with_evidence(self):
        p=self.p();p['observations'][0]['coverage']='PARTIAL';self.assertEqual(self.status(p),'RELEASE_SEMANTIC_MINIMAL')
    def test_partial_insufficient(self):
        p=self.p();p['observations'][0]['coverage']='UNKNOWN';self.assertEqual(self.status(p),'UNKNOWN')
    def test_bad_value(self):
        p=self.p();p['observations'][0]['semantic_value']=3;self.assertEqual(self.status(p),'UNKNOWN')
    def test_wrong_type(self):
        p=self.p();p['observations'][0]['semantic_value']='4';self.assertEqual(self.status(p),'UNKNOWN')
    def test_stale(self):
        p=self.p();p['observations'][0]['observed_tick']=1;self.assertEqual(self.status(p),'STALE')
    def test_future_tick(self):
        p=self.p();p['observations'][0]['observed_tick']=99;self.assertEqual(self.status(p),'STALE')
    def test_duplicate_probe(self):
        p=self.p();p['observations'].append(copy.deepcopy(p['observations'][0]));self.assertEqual(self.status(p),'CONTRADICTORY')
    def test_forbidden_transition(self):
        p=self.p();p['history']['prior_milestone']='SYN-NOT-STARTED';self.assertEqual(self.status(p),'BLOCKED_TRANSITION')
    def test_ambiguous_exclusive(self):
        p=self.p();p['catalog'][0]['milestones'].append(copy.deepcopy(p['catalog'][0]['milestones'][0]));self.assertEqual(self.status(p),'AMBIGUOUS')
    def test_secret(self):
        p=self.p();p['catalog'][0]['milestones'][0]['classification']='FUTURE_BRANCH';self.assertEqual(self.status(p),'BLOCKED_SPOILER')
    def test_private_party_different_audience(self):
        p=self.p();p['catalog'][0]['milestones'][0]['classification']='PARTY_PRIVATE';p['request']['audience']='FACTION';self.assertEqual(self.status(p),'BLOCKED_ACL')
    def test_no_knowledge(self):
        p=self.p();p['policy']['knowledge_granted']=False;self.assertEqual(self.status(p),'OBSERVED_TECHNICAL_ONLY')
    def test_semantic_id_not_allowlisted(self):
        p=self.p();p['policy']['allowed_semantic_ids']=[];self.assertEqual(self.status(p),'OBSERVED_TECHNICAL_ONLY')
    def test_bad_purpose(self):
        p=self.p();p['request']['purpose']='NPC_ACTION';self.assertEqual(self.status(p),'BLOCKED_ACL')
    def test_request_cannot_grant_knowledge(self):
        p=self.p();p['policy']['knowledge_granted']=False;p['request']['knowledge_granted']=True
        self.assertEqual(self.status(p),'OBSERVED_TECHNICAL_ONLY')
    def test_request_cannot_overwrite_ttl(self):
        p=self.p();p['observations'][0]['observed_tick']=1;p['request']['max_age_ticks']=100000
        self.assertEqual(self.status(p),'STALE')
    def test_request_cannot_rewrite_prior(self):
        p=self.p();p['history']['prior_milestone']='SYN-WRONG';p['request']['prior_milestone']='SYN-QUEST-STARTED'
        self.assertEqual(self.status(p),'BLOCKED_TRANSITION')
    def test_untrusted_history(self):
        p=self.p();p['history']['host_epoch']=999;self.assertEqual(self.status(p),'BLOCKED_TRANSITION')
    def test_untrusted_policy(self):
        p=self.p();p['policy']['trusted_kind']='CLIENT';self.assertEqual(self.status(p),'BLOCKED_ACL')
    def test_no_raw_values_in_output(self):
        p=self.p();p['observations'][0]['semantic_value']=4;o=map_semantics_synthetic(p)
        self.assertNotIn('semantic_value',str(o));self.assertNotIn('probe_id',str(o));self.assertNotIn('script',str(o))
    def test_invalid_predicate_code(self):
        p=self.p();p['catalog'][0]['milestones'][0]['predicates'][0]['op']='eval';self.assertEqual(self.status(p),'BLOCKED_MAPPING')
    def test_set_membership(self):
        p=self.p();q=p['catalog'][0]['milestones'][0]['predicates'][0];q['op']='in';q['value']=[2,4,6];self.assertEqual(self.status(p),'RELEASE_SEMANTIC_MINIMAL')
    def test_empty_set(self):
        p=self.p();q=p['catalog'][0]['milestones'][0]['predicates'][0];q['op']='in';q['value']=[];self.assertEqual(self.status(p),'BLOCKED_MAPPING')

if __name__=='__main__':unittest.main()
