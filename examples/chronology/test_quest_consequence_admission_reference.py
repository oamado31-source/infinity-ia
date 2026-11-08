"""DEC-103/C synthetic-only tests: no BG2:EE, EEex, network or host calls."""
import copy
import unittest
from quest_consequence_admission_reference import evaluate_synthetic


def fixture():
    scope={'campaign_id':'SYN-CAMP', 'branch_id':'SYN-BRANCH', 'quest_key':'SYN-QUEST',
           'build_fingerprint':'SYN-BUILD', 'modpack_hash':'SYN-MODPACK',
           'mapping_revision':'SYN-MAPPING', 'lineage_id':'SYN-LINEAGE'}
    return {'source_kind':'SYNTHETIC_TEST',
        'context':{**scope,'fixture_only':True,'host_mode':'SYNTHETIC_HOST_FIXTURE',
                   'host_epoch':8, 'checkpoint_epoch':6,'world_tick':100,'dr_year':1369,
                   'dr_month':7,'region_id':'SYN-REGION'},
        'request':{'operation_id':'SYN-OP','proof_ref':'SYN-PROOF','purpose':'ADMIT_QUEST_MILESTONE',
                   'audience':'HOST_OPERATOR','scope':scope,'expected_ledger_revision':'SYN-LR1'},
        'policy':{'trusted_kind':'SYNTHETIC_POLICY_STORE','revision':'SYN-POLICY',
                  'purposes':['ADMIT_QUEST_MILESTONE'],'audiences':['HOST_OPERATOR'],
                  'max_age_ticks':10,'can_process_protected':False,'can_propose_high_risk':False},
        'proof_registry':{**scope,'trusted_kind':'SYNTHETIC_RECONCILED_PROOF_STORE',
                          'authenticated_fixture':True, 'proof_id':'SYN-PROOF',
                          'source':'DEC100_DEC101_DEC102','semantic_status':'MAPPED_MINIMAL',
                          'coverage':'FULL_FOR_MILESTONE','mapping_status':'CURATED_PINNED',
                          'reconciliation':'CONSISTENT_WITH_PROOF',
                          'host_epoch':8,'checkpoint_epoch':6,'observed_tick':98,
                          'milestone_id':'SYN-MILESTONE','occurrence_id':'SYN-OCC1',
                          'classification':'PUBLIC', 'confidential_spoiler':'SYN-SECRET-DO-NOT-EXPOSE'},
        'catalog':{'trusted_kind':'SYNTHETIC_CURATED_RULESET','curation_status':'CURATED_SYNTHETIC',
                   'revision':'SYN-RULESET', 'quest_key':'SYN-QUEST',
                   'build_fingerprint':'SYN-BUILD','modpack_hash':'SYN-MODPACK',
                   'mapping_revision':'SYN-MAPPING', 'rules':[
                     {'rule_id':'SYN-R1','milestone_id':'SYN-MILESTONE',
                      'region_id':'SYN-REGION','dr_start':1369,'dr_end':1370,
                      'month_start':6,'month_end':8,'classification':'PUBLIC',
                      'risk':'LOW','requires':{'SYN-EVIDENCE':True},'kind':'RUMOR_PROPOSAL'},
                     {'rule_id':'SYN-R2','milestone_id':'SYN-MILESTONE',
                      'region_id':'SYN-REGION','dr_start':1369,'dr_end':1370,
                      'month_start':6,'month_end':8,'classification':'PRIVATE',
                      'risk':'MEDIUM','requires':{'SYN-EVIDENCE':True},'kind':'FACTION_REACTION_PROPOSAL'}]},
        'ledger':{**scope,'trusted_kind':'SYNTHETIC_ADMISSION_LEDGER',
                  'host_epoch':8,'checkpoint_epoch':6,'revision':'SYN-LR1',
                  'actions':[], 'admitted_keys':[], 'pending_keys':[],
                  'confirmed_facts':{'SYN-EVIDENCE':True}}}

class AdmissionCoreTests(unittest.TestCase):
    def test_returns_proposals_only(self):
        r=evaluate_synthetic(fixture())
        self.assertEqual(r['status'],'PROPOSE_ADMISSION')
        self.assertEqual(len(r['proposals']),2)
        self.assertEqual((r['engine_writes'],r['host_calls'],r['llm_calls']), (0,0,0))
        self.assertFalse(r['npc_knowledge_updated'])
    def test_repeat_is_deterministic(self):
        f=fixture();self.assertEqual(evaluate_synthetic(f),evaluate_synthetic(f))
    def test_pure_no_mutation(self):
        f=fixture();old=copy.deepcopy(f);evaluate_synthetic(f);self.assertEqual(old,f)
    def test_no_spoiler_in_response(self):
        self.assertNotIn('SYN-SECRET-DO-NOT-EXPOSE',str(evaluate_synthetic(fixture())))
    def test_duplicate_same_occurrence(self):
        f=fixture();key=evaluate_synthetic(f)['admission_key'];f['ledger']['admitted_keys']=[key]
        self.assertEqual(evaluate_synthetic(f)['status'],'DUPLICATE_SUPPRESSED')
    def test_repeat_new_observation_id_same_key(self):
        f=fixture();key=evaluate_synthetic(f)['admission_key'];f['proof_registry']['observation_id']='SYN-OBS2'
        self.assertEqual(evaluate_synthetic(f)['admission_key'],key)
    def test_new_certified_occurrence_yields_new_key(self):
        f=fixture();key=evaluate_synthetic(f)['admission_key'];f['proof_registry']['occurrence_id']='SYN-OCC2'
        self.assertNotEqual(evaluate_synthetic(f)['admission_key'],key)
    def test_reordering_rules_deterministic(self):
        f=fixture();orig=evaluate_synthetic(f);f['catalog']['rules'].reverse()
        self.assertEqual(orig,evaluate_synthetic(f))
    def test_request_cannot_self_authorize(self):
        f=fixture();f['request']['authorize_all']=True;f['request']['host_receipt']='SYN-FAKE'
        self.assertEqual(evaluate_synthetic(f)['status'],'PROPOSE_ADMISSION')
        self.assertEqual(evaluate_synthetic(f)['effects_confirmed'],0)
    def test_protected_source_never_public_rule(self):
        f=fixture();f['proof_registry']['classification']='PROTECTED';f['policy']['can_process_protected']=True
        r=evaluate_synthetic(f)
        self.assertEqual(r['status'],'PROPOSE_ADMISSION');self.assertEqual(len(r['proposals']),1)
        self.assertEqual(r['proposals'][0]['kind'],'FACTION_REACTION_PROPOSAL')
    def test_pending_rebase_never_admitted(self):
        f=fixture();f['proof_registry']['reconciliation']='PROPOSE_DERIVED_VIEW_REBASE'
        self.assertEqual(evaluate_synthetic(f)['status'],'QUARANTINED')
    def test_committed_rebase_accepted(self):
        f=fixture();f['proof_registry']['reconciliation']='APPROVED_AND_COMMITTED_REBASE'
        self.assertEqual(evaluate_synthetic(f)['status'],'PROPOSE_ADMISSION')
    def test_outbox_pending_suppresses_duplicate(self):
        f=fixture();f['ledger']['pending_keys']=[evaluate_synthetic(f)['admission_key']]
        self.assertEqual(evaluate_synthetic(f)['status'],'DUPLICATE_SUPPRESSED')
    def test_no_rule_matches_still_no_host_mutation(self):
        f=fixture();f['context']['region_id']='SYN-OTHER'
        r=evaluate_synthetic(f);self.assertEqual(r['status'],'PROPOSE_ADMISSION');self.assertEqual(r['proposals'],[])
    def test_invalid_source_rejected(self):
        f=fixture();f['source_kind']='REAL_GAME'
        with self.assertRaises(ValueError):evaluate_synthetic(f)


def change(f,path,value):
    obj=f
    for part in path[:-1]:obj=obj[part]
    obj[path[-1]]=value

# Each tuple becomes a separately named unittest case, allowing individual debugging.
_CASES=[
 ('bad_policy',('policy','trusted_kind'),'REQUEST_SAYS_TRUSTED','BLOCKED_ACL'),
 ('bad_policy_rev',('policy','revision'),'none','BLOCKED_ACL'),
 ('purpose_denied',('request','purpose'),'EDIT_QUEST','BLOCKED_ACL'),
 ('audience_denied',('request','audience'),'ALL_NPCS','BLOCKED_ACL'),
 ('request_branch_wrong',('request','scope','branch_id'),'SYN-OTHER','BLOCKED_ACL'),
 ('request_campaign_wrong',('request','scope','campaign_id'),'SYN-OTHER','BLOCKED_ACL'),
 ('request_quest_wrong',('request','scope','quest_key'),'SYN-OTHER','BLOCKED_ACL'),
 ('request_mapping_wrong',('request','scope','mapping_revision'),'SYN-OTHER','BLOCKED_ACL'),
 ('missing_proof_ref',('request','proof_ref'),'','UNKNOWN'),
 ('wrong_proof_ref',('request','proof_ref'),'SYN-NOT-THERE','UNKNOWN'),
 ('untrusted_proof',('proof_registry','trusted_kind'),'REQUEST_STORE','QUARANTINED'),
 ('unauthenticated_proof',('proof_registry','authenticated_fixture'),False,'QUARANTINED'),
 ('proof_branch_wrong',('proof_registry','branch_id'),'SYN-OTHER','QUARANTINED'),
 ('proof_lineage_wrong',('proof_registry','lineage_id'),'SYN-OTHER','QUARANTINED'),
 ('proof_build_wrong',('proof_registry','build_fingerprint'),'SYN-OTHER','QUARANTINED'),
 ('proof_mapping_wrong',('proof_registry','mapping_revision'),'SYN-OTHER','QUARANTINED'),
 ('proof_source_wrong',('proof_registry','source'),'LLM_GUESS','UNKNOWN'),
 ('ambiguous_semantic',('proof_registry','semantic_status'),'AMBIGUOUS','UNKNOWN'),
 ('unknown_semantic',('proof_registry','semantic_status'),'UNKNOWN','UNKNOWN'),
 ('partial_coverage',('proof_registry','coverage'),'PARTIAL','BLOCKED_MAPPING'),
 ('mapping_revoked',('proof_registry','mapping_status'),'REVOKED','BLOCKED_MAPPING'),
 ('uncommitted_rebase',('proof_registry','reconciliation'),'PROPOSE_DERIVED_VIEW_REBASE','QUARANTINED'),
 ('restored_pending',('proof_registry','reconciliation'),'RESTORE_REVIEW_REQUIRED','QUARANTINED'),
 ('proof_epoch_mismatch',('proof_registry','host_epoch'),7,'QUARANTINED'),
 ('checkpoint_mismatch',('proof_registry','checkpoint_epoch'),5,'QUARANTINED'),
 ('future_observation',('proof_registry','observed_tick'),101,'UNKNOWN'),
 ('stale_observation',('proof_registry','observed_tick'),89,'UNKNOWN'),
 ('invalid_semantic_id',('proof_registry','milestone_id'),None,'UNKNOWN'),
 ('uncertified_occurrence',('proof_registry','occurrence_id'),None,'UNKNOWN'),
 ('unknown_classification',('proof_registry','classification'),'TOP_SECRET_UNKNOWN','QUARANTINED'),
 ('protected_denied',('proof_registry','classification'),'PROTECTED','BLOCKED_ACL'),
 ('bad_catalog_kind',('catalog','trusted_kind'),'FROM_REQUEST','BLOCKED_RULE'),
 ('catalog_not_curated',('catalog','curation_status'),'LLM_AUTHORED','BLOCKED_RULE'),
 ('catalog_modpack_mismatch',('catalog','modpack_hash'),'SYN-OTHER','BLOCKED_RULE'),
 ('catalog_mapping_mismatch',('catalog','mapping_revision'),'SYN-OTHER','BLOCKED_RULE'),
 ('catalog_quest_mismatch',('catalog','quest_key'),'SYN-OTHER','BLOCKED_RULE'),
 ('catalog_revision_missing',('catalog','revision'),'none','BLOCKED_RULE'),
 ('untrusted_ledger',('ledger','trusted_kind'),'FROM_REQUEST','QUARANTINED'),
 ('ledger_branch_wrong',('ledger','branch_id'),'SYN-OTHER','QUARANTINED'),
 ('ledger_lineage_wrong',('ledger','lineage_id'),'SYN-OTHER','QUARANTINED'),
 ('ledger_epoch_wrong',('ledger','host_epoch'),7,'QUARANTINED'),
 ('ledger_checkpoint_wrong',('ledger','checkpoint_epoch'),5,'QUARANTINED'),
 ('cas_conflict',('ledger','revision'),'SYN-LR2','QUARANTINED'),
 ('absent_confirmed_facts',('ledger','confirmed_facts'),None,'QUARANTINED'),
 ('unknown_fact',('ledger','confirmed_facts'),{},'PROPOSE_ADMISSION'),
 ('contradicted_fact',('ledger','confirmed_facts','SYN-EVIDENCE'),False,'PROPOSE_ADMISSION'),
 ('different_region',('context','region_id'),'SYN-OTHER','PROPOSE_ADMISSION'),
 ('different_year',('context','dr_year'),1391,'PROPOSE_ADMISSION'),
 ('different_month',('context','dr_month'),12,'PROPOSE_ADMISSION'),
]

for name,path,value,expected in _CASES:
    def test_case(self,path=path,value=value,expected=expected):
        f=fixture();change(f,path,value)
        self.assertEqual(evaluate_synthetic(f)['status'],expected)
    setattr(AdmissionCoreTests,'test_'+name,test_case)

if __name__=='__main__':unittest.main()
