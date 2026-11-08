"""DEC-102/C synthetic-only unit cases; never touches BG2:EE or host state."""
from __future__ import annotations
import copy
import unittest
from quest_reconciler_reference import reconcile_synthetic


def fixture():
    context = {'fixture_only': True, 'host_mode': 'SYNTHETIC_HOST_FIXTURE',
      'campaign_id':'SYN-CAMP', 'branch_id':'SYN-BRANCH', 'session_id':'SYN-SESSION',
      'build_fingerprint':'SYN-BUILD', 'modpack_hash':'SYN-MODPACK',
      'mapping_revision':'SYN-MAP-2', 'quest_key':'SYN-QUEST',
      'host_epoch':7, 'checkpoint_epoch':4, 'snapshot_tick':30}
    scope = {k: context[k] for k in ('campaign_id','branch_id','session_id',
      'build_fingerprint','modpack_hash','mapping_revision','quest_key')}
    return {'source_kind':'SYNTHETIC_TEST', 'context': context,
      'request': {'operation_id':'SYN-OP-1', 'purpose':'RECONCILE', 'audience':'HOST_OPERATOR',
                  'scope':scope,'expected_overlay_revision':'SYN-R7'},
      'policy': {'trusted_kind':'SYNTHETIC_POLICY_FIXTURE', 'revision':'SYN-POLICY-1',
                 'purposes':['RECONCILE'],'audiences':['HOST_OPERATOR'],'max_age_ticks':10},
      'host': {**scope, 'source_kind':'SYNTHETIC_HOST_OBSERVATION',
               'authenticated_fixture':True, 'host_epoch':7,'checkpoint_epoch':4,
               'observed_tick':29,'coverage':'FULL_FOR_SEMANTIC_PROOF',
               'semantic_status':'MAPPED_MINIMAL', 'semantic_id':'SYN-STAGE-B',
               'proof_id':'SYN-PROOF-1'},
      'overlay': {**scope, 'source_kind':'SYNTHETIC_OVERLAY_SNAPSHOT',
                  'trusted_fixture':True, 'host_epoch':7, 'checkpoint_epoch':4,
                  'revision':'SYN-R7', 'semantic_id':'SYN-STAGE-A'},
      'ledger': {**scope, 'trusted_kind':'SYNTHETIC_LEDGER_FIXTURE',
                'host_epoch':7,'checkpoint_epoch':4,'actions':[]},
      'mapping': {'trusted_kind':'SYNTHETIC_CURATED_MAPPING', 'review_status':'CURATED_SYNTHETIC',
                  'build_fingerprint':'SYN-BUILD','modpack_hash':'SYN-MODPACK',
                  'mapping_revision':'SYN-MAP-2','quest_key':'SYN-QUEST',
                  'allowed_transitions':[{'from':'SYN-STAGE-A','to':'SYN-STAGE-B'}]}}


class ReconciliationTests(unittest.TestCase):
    def test_valid_transition_only_proposes(self):
        r=reconcile_synthetic(fixture())
        self.assertEqual(r['status'],'PROPOSE_DERIVED_VIEW_REBASE')
        self.assertEqual(len(r['proposals']),2)
        self.assertEqual(r['host_calls'],0)
        self.assertEqual(r['engine_writes'],0)
        self.assertEqual(r['llm_calls'],0)
        self.assertFalse(r['overlay_state_mutated'])

    def test_idempotent_output(self):
        f=fixture()
        self.assertEqual(reconcile_synthetic(f),reconcile_synthetic(f))

    def test_does_not_mutate_inputs(self):
        f=fixture(); original=copy.deepcopy(f)
        reconcile_synthetic(f)
        self.assertEqual(f,original)

    def test_consistent_state_no_proposal(self):
        f=fixture();f['host']['semantic_id']='SYN-STAGE-A'
        r=reconcile_synthetic(f)
        self.assertEqual(r['status'],'CONSISTENT')
        self.assertEqual(r['proposals'],[])

    def test_id_does_not_expose_raw_proof(self):
        r=reconcile_synthetic(fixture())
        self.assertNotIn('SYN-PROOF-1',str(r))
        self.assertNotIn('SYN-STAGE-B',str(r))

    def test_rollback_requires_review(self):
        f=fixture();f['overlay']['checkpoint_epoch']=3
        self.assertEqual(reconcile_synthetic(f)['status'],'RESTORE_REVIEW_REQUIRED')

    def test_retired_epoch_no_automatic_port(self):
        f=fixture();f['overlay']['host_epoch']=6
        r=reconcile_synthetic(f)
        self.assertEqual(r['status'],'RESTORE_REVIEW_REQUIRED')
        self.assertEqual(r['proposals'],['FORK_OR_RESCOPE_OVERLAY_AFTER_REVIEW'])

    def test_unknown_transition_quarantined(self):
        f=fixture();f['host']['semantic_id']='SYN-UNSEEN'
        self.assertEqual(reconcile_synthetic(f)['status'],'QUARANTINED')

    def test_reverse_transition_quarantined(self):
        f=fixture();f['overlay']['semantic_id']='SYN-STAGE-B';f['host']['semantic_id']='SYN-STAGE-A'
        self.assertEqual(reconcile_synthetic(f)['status'],'QUARANTINED')

    def test_dispatch_uncertain_requires_receipt(self):
        f=fixture();f['ledger']['actions']=[{'dispatch_state':'UNCERTAIN'}]
        r=reconcile_synthetic(f)
        self.assertEqual(r['status'],'QUARANTINED');self.assertTrue(r['receipt_required'])

    def test_confirmed_receipt_does_not_grant_mutation(self):
        f=fixture();f['ledger']['actions']=[{'dispatch_state':'HOST_CONFIRMED'}]
        r=reconcile_synthetic(f)
        self.assertFalse(r['host_state_mutated']); self.assertFalse(r['overlay_state_mutated'])

    def test_untrusted_policy_not_self_authorized(self):
        f=fixture(); f['policy']['trusted_kind']='from-request';f['request']['authorize_all']=True
        self.assertEqual(reconcile_synthetic(f)['status'],'BLOCKED_ACL')


# Each case below has a separate unittest ID and an explicit expected consequence.
def _change(p, path, value):
    d=p
    for key in path[:-1]:d=d[key]
    d[path[-1]]=value

_CASES = [
 ('request_purpose_denied',('request','purpose'),'WRITE_QUEST','BLOCKED_ACL'),
 ('request_audience_denied',('request','audience'),'ALL_NPCS','BLOCKED_ACL'),
 ('request_scope_wrong',('request','scope','branch_id'),'SYN-OTHER','BLOCKED_ACL'),
 ('scope_host_wrong_campaign',('host','campaign_id'),'SYN-OTHER','QUARANTINED'),
 ('scope_overlay_wrong_branch',('overlay','branch_id'),'SYN-OTHER','QUARANTINED'),
 ('scope_ledger_wrong_quest',('ledger','quest_key'),'SYN-OTHER','QUARANTINED'),
 ('untrusted_ledger',('ledger','trusted_kind'),'BAD','QUARANTINED'),
 ('untrusted_host',('host','source_kind'),'BAD','QUARANTINED'),
 ('not_authenticated',('host','authenticated_fixture'),False,'QUARANTINED'),
 ('untrusted_overlay',('overlay','trusted_fixture'),False,'QUARANTINED'),
 ('untrusted_mapper',('mapping','trusted_kind'),'BAD','BLOCKED_MAPPING'),
 ('uncurated_mapping',('mapping','review_status'),'REVOKED','BLOCKED_MAPPING'),
 ('build_mismatch',('mapping','build_fingerprint'),'SYN-NEWBUILD','BLOCKED_MAPPING'),
 ('modpack_mismatch',('mapping','modpack_hash'),'SYN-NEWMOD','BLOCKED_MAPPING'),
 ('mapping_revision_mismatch',('mapping','mapping_revision'),'SYN-MAP-3','BLOCKED_MAPPING'),
 ('quest_mismatch',('mapping','quest_key'),'SYN-OTHER','BLOCKED_MAPPING'),
 ('host_epoch_mismatch',('host','host_epoch'),6,'QUARANTINED'),
 ('host_checkpoint_mismatch',('host','checkpoint_epoch'),3,'QUARANTINED'),
 ('ledger_epoch_mismatch',('ledger','host_epoch'),6,'QUARANTINED'),
 ('ledger_checkpoint_mismatch',('ledger','checkpoint_epoch'),3,'QUARANTINED'),
 ('future_observation',('host','observed_tick'),31,'QUARANTINED'),
 ('stale_observation',('host','observed_tick'),10,'UNKNOWN'),
 ('coverage_partial',('host','coverage'),'PARTIAL','UNKNOWN'),
 ('unmapped_semantics',('host','semantic_status'),'UNKNOWN','UNKNOWN'),
 ('ambiguous_semantics',('host','semantic_status'),'AMBIGUOUS','UNKNOWN'),
 ('contradictory_semantics',('host','semantic_status'),'CONTRADICTORY','UNKNOWN'),
 ('spoiler_semantics',('host','semantic_status'),'BLOCKED_SPOILER','UNKNOWN'),
 ('missing_proof',('host','proof_id'),'','UNKNOWN'),
 ('missing_semantic',('host','semantic_id'),'','UNKNOWN'),
 ('bad_overlay_revision',('overlay','revision'),'BAD','QUARANTINED'),
 ('ledger_dispatch_pending',('ledger','actions'),[{'dispatch_state':'DISPATCH_PENDING'}],'QUARANTINED'),
 ('ledger_dispatched',('ledger','actions'),[{'dispatch_state':'DISPATCHED'}],'QUARANTINED'),
 ('ledger_ack_unknown',('ledger','actions'),[{'dispatch_state':'ACK_UNKNOWN'}],'QUARANTINED'),
 ('ledger_state_other',('ledger','actions'),[{'dispatch_state':'MYSTERY'}],'QUARANTINED'),
 ('overlay_semantic_unrecognized',('overlay','semantic_id'),'X','UNKNOWN'),
 ('mapping_transition_bad',('mapping','allowed_transitions'),{},'BLOCKED_MAPPING'),
 ('mapping_transition_missing',('mapping','allowed_transitions'),[],'QUARANTINED'),
 ('revision_CAS_conflict',('request','expected_overlay_revision'),'SYN-R6','QUARANTINED'),
 ('untrusted_policy_revision',('policy','revision'),'not-versioned','BLOCKED_ACL'),
 ('ttl_invalid',('policy','max_age_ticks'),-1,'UNKNOWN'),
 ('ledger_actions_invalid',('ledger','actions'),'NOT-A-LIST','QUARANTINED'),
 ('ledger_rejected',('ledger','actions'),[{'dispatch_state':'REJECTED'}],'PROPOSE_DERIVED_VIEW_REBASE'),
 ('ledger_not_dispatched',('ledger','actions'),[{'dispatch_state':'NOT_DISPATCHED'}],'PROPOSE_DERIVED_VIEW_REBASE'),
]
for name,path,value,expected in _CASES:
    def test_case(self, path=path, value=value, expected=expected):
        f=fixture();_change(f,path,value)
        r=reconcile_synthetic(f)
        self.assertEqual(r['status'],expected)
        self.assertEqual(r['host_calls'],0)
        self.assertEqual(r['engine_writes'],0)
        self.assertFalse(r['npc_knowledge_updated'])
    setattr(ReconciliationTests,'test_'+name,test_case)

if __name__=='__main__':unittest.main()
