"""DEC-104 tests: exclusively synthetic; does not touch host/save/network."""
import copy
import json
from pathlib import Path
import unittest
from rectification_reference import plan_synthetic

FIXTURE=Path(__file__).with_name('rectification_v1.synthetic.json')
def fixture():
    return json.loads(FIXTURE.read_text(encoding='utf-8'))

def set_nested(d,path,value):
    p=d
    for k in path[:-1]:p=p[k]
    p[path[-1]]=value

class RectificationCore(unittest.TestCase):
    def test_valid_plan_is_dry_run(self):
        r=plan_synthetic(fixture())
        self.assertEqual(r['status'],'PROPOSE_RECTIFICATION_PLAN')
        self.assertEqual(len(r['proposals']),4)
        for k in ('host_calls','engine_writes','npc_memories_changed','rumors_sent','compensations_executed'):
            self.assertEqual(r[k],0)
        self.assertFalse(r['ledger_mutated'])
    def test_four_distinct_proposals(self):
        acts={p['proposed_action'] for p in plan_synthetic(fixture())['proposals']}
        self.assertEqual(acts,{'HOLD_FUTURE_DISPATCH','PROPOSE_AUTHORIZED_SAGA_COMPENSATION_REVIEW','PROPOSE_CAUSAL_CORRECTION_DELIVERY','PROPOSE_VERSIONED_CAS_REBASE'})
    def test_facts_never_deleted(self):
        f=fixture(); before=copy.deepcopy(f)
        plan_synthetic(f);self.assertEqual(f,before)
    def test_deterministic(self):
        f=fixture();self.assertEqual(plan_synthetic(f),plan_synthetic(copy.deepcopy(f)))
    def test_node_order_independent(self):
        f=fixture();expected=plan_synthetic(f);f['ledger']['nodes'].reverse()
        self.assertEqual(plan_synthetic(f),expected)
    def test_request_id_not_part_of_case_key(self):
        f=fixture();k=plan_synthetic(f)['case_key'];f['request']['operation_id']='SYN-OTHEROP'
        self.assertEqual(plan_synthetic(f)['case_key'],k)
    def test_new_revision_produces_new_case_key(self):
        f=fixture();k=plan_synthetic(f)['case_key'];f['rectification_registry']['revision']='SYN-RECT-REV-3'
        self.assertNotEqual(plan_synthetic(f)['case_key'],k)
    def test_duplicate_suppressed(self):
        f=fixture();key=plan_synthetic(f)['case_key'];f['ledger']['planned_case_keys']=[key]
        self.assertEqual(plan_synthetic(f)['status'],'DUPLICATE_SUPPRESSED')
    def test_pending_case_suppressed(self):
        f=fixture();key=plan_synthetic(f)['case_key'];f['ledger']['pending_case_keys']=[key]
        self.assertEqual(plan_synthetic(f)['status'],'DUPLICATE_SUPPRESSED')
    def test_unrelated_node_ignored(self):
        f=fixture();n=copy.deepcopy(f['ledger']['nodes'][-1]);n['id']='SYN-UNRELATED';n['parents']=[]
        f['ledger']['nodes'].append(n)
        self.assertEqual(len(plan_synthetic(f)['proposals']),4)
    def test_delivered_news_is_not_erased(self):
        f=fixture();r=plan_synthetic(f)
        self.assertTrue(any(x['proposed_action']=='PROPOSE_CAUSAL_CORRECTION_DELIVERY' for x in r['proposals']))
        self.assertEqual(r['npc_memories_changed'],0)
    def test_dispatched_requires_reconciliation(self):
        f=fixture();f['ledger']['nodes'][1]['state']='DISPATCHED'
        self.assertIn('RECONCILE_HOST_BEFORE_ANY_CHANGE',[i['proposed_action'] for i in plan_synthetic(f)['proposals']])
    def test_uncertain_requires_reconciliation(self):
        f=fixture();f['ledger']['nodes'][1]['state']='UNCERTAIN'
        self.assertIn('RECONCILE_HOST_BEFORE_ANY_CHANGE',[i['proposed_action'] for i in plan_synthetic(f)['proposals']])
    def test_cross_scope_node_blocks(self):
        f=fixture();f['ledger']['nodes'][1]['branch_id']='SYN-OTHER'
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_cycle_blocks(self):
        f=fixture();f['ledger']['nodes'][0]['parents']=['SYN-VIEW']
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_cycle_other_branch_blocks(self):
        f=fixture(); n1=copy.deepcopy(f['ledger']['nodes'][1]);n2=copy.deepcopy(n1)
        n1.update(id='SYN-X1',parents=['SYN-X2']);n2.update(id='SYN-X2',parents=['SYN-X1'])
        f['ledger']['nodes'] += [n1,n2]
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_incomplete_graph_blocks(self):
        f=fixture();f['ledger']['nodes'][1]['parents']=['SYN-MISSING']
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_request_cannot_self_grant(self):
        f=fixture();f['request']['grant_protected']=True;f['request']['host_receipt']='SYN-FAKE';f['request']['reconcile_now']=True
        self.assertEqual(plan_synthetic(f)['host_calls'],0)
    def test_real_game_fixture_rejected(self):
        f=fixture();f['source_kind']='BG2_EE'
        with self.assertRaises(ValueError):plan_synthetic(f)
    def test_bad_root_status(self):
        f=fixture();f['ledger']['nodes'][0]['kind']='NEWS'
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_inconsistent_host_effect_delivery(self):
        f=fixture();f['ledger']['nodes'][1]['state']='DELIVERED'
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_inconsistent_news_confirmed(self):
        f=fixture();f['ledger']['nodes'][2]['state']='HOST_CONFIRMED'
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_new_branch_key_isolated(self):
        f=fixture();k=plan_synthetic(f)['case_key']
        for section in ('context','request','rectification_registry','ledger'):
            target=f[section]['scope'] if section=='request' else f[section]
            target['branch_id']='SYN-NEW-BRANCH'
        for n in f['ledger']['nodes']:n['branch_id']='SYN-NEW-BRANCH'
        self.assertNotEqual(plan_synthetic(f)['case_key'],k)
    def test_confidential_identifiers_not_in_output(self):
        f=fixture();f['ledger']['nodes'][2]['private_identity']='SYN-SECRET-NAME'
        self.assertNotIn('SYN-SECRET-NAME',str(plan_synthetic(f)))
    def test_higher_budget_irrelevant(self):
        f=fixture();old=plan_synthetic(f);f['policy']['max_nodes']=100
        self.assertEqual(plan_synthetic(f),old)

_CASES=[
 ('bad_policy',('policy','trusted_kind'),'FROM_REQUEST','BLOCKED_ACL'),
 ('bad_policy_revision',('policy','revision'),'x','BLOCKED_ACL'),
 ('denied_audience',('request','audience'),'EVERYONE','BLOCKED_ACL'),
 ('denied_purpose',('request','purpose'),'SPAWN_NPC','BLOCKED_ACL'),
 ('scope_branch_mismatch',('request','scope','branch_id'),'SYN-OTHER','BLOCKED_ACL'),
 ('scope_campaign_mismatch',('request','scope','campaign_id'),'SYN-OTHER','BLOCKED_ACL'),
 ('scope_lineage_mismatch',('request','scope','lineage_id'),'SYN-OTHER','BLOCKED_ACL'),
 ('scope_build_mismatch',('request','scope','build_fingerprint'),'SYN-OTHER','BLOCKED_ACL'),
 ('scope_modpack_mismatch',('request','scope','modpack_hash'),'SYN-OTHER','BLOCKED_ACL'),
 ('registry_untrusted',('rectification_registry','trusted_kind'),'FROM_REQUEST','QUARANTINED'),
 ('registry_not_authenticated',('rectification_registry','authenticated_fixture'),False,'QUARANTINED'),
 ('registry_wrong_ref',('rectification_registry','rectification_id'),'SYN-OTHER','UNKNOWN'),
 ('registry_wrong_campaign',('rectification_registry','campaign_id'),'SYN-OTHER','QUARANTINED'),
 ('registry_wrong_branch',('rectification_registry','branch_id'),'SYN-OTHER','QUARANTINED'),
 ('registry_wrong_lineage',('rectification_registry','lineage_id'),'SYN-OTHER','QUARANTINED'),
 ('registry_wrong_build',('rectification_registry','build_fingerprint'),'SYN-OTHER','QUARANTINED'),
 ('registry_wrong_modpack',('rectification_registry','modpack_hash'),'SYN-OTHER','QUARANTINED'),
 ('registry_wrong_host_epoch',('rectification_registry','host_epoch'),99,'QUARANTINED'),
 ('registry_wrong_checkpoint_epoch',('rectification_registry','checkpoint_epoch'),99,'QUARANTINED'),
 ('registry_uncommitted',('rectification_registry','state'),'RECTIFICATION_PROPOSED','QUARANTINED'),
 ('registry_proposed_restore',('rectification_registry','state'),'RESTORE_PENDING','QUARANTINED'),
 ('registry_wrong_source',('rectification_registry','source'),'LLM_GUESS','QUARANTINED'),
 ('registry_missing_root',('rectification_registry','root_admission_key'),None,'UNKNOWN'),
 ('registry_missing_rev',('rectification_registry','revision'),None,'UNKNOWN'),
 ('registry_private_denied',('rectification_registry','classification'),'PROTECTED','BLOCKED_ACL'),
 ('registry_secrecy_unknown',('rectification_registry','classification'),'TOP_SECRET','QUARANTINED'),
 ('registry_future_commit',('rectification_registry','committed_at_tick'),300,'QUARANTINED'),
 ('ledger_untrusted',('ledger','trusted_kind'),'REQUEST_LEDGER','QUARANTINED'),
 ('ledger_wrong_branch',('ledger','branch_id'),'SYN-OTHER','QUARANTINED'),
 ('ledger_wrong_campaign',('ledger','campaign_id'),'SYN-OTHER','QUARANTINED'),
 ('ledger_wrong_lineage',('ledger','lineage_id'),'SYN-OTHER','QUARANTINED'),
 ('ledger_wrong_build',('ledger','build_fingerprint'),'SYN-OTHER','QUARANTINED'),
 ('ledger_wrong_modpack',('ledger','modpack_hash'),'SYN-OTHER','QUARANTINED'),
 ('ledger_wrong_host_epoch',('ledger','host_epoch'),99,'QUARANTINED'),
 ('ledger_wrong_checkpoint_epoch',('ledger','checkpoint_epoch'),99,'QUARANTINED'),
 ('ledger_wrong_mapping_rev',('ledger','mapping_revision'),'SYN-OLDER','QUARANTINED'),
 ('ledger_cas_conflict',('request','expected_ledger_revision'),99,'QUARANTINED'),
 ('graph_not_array',('ledger','nodes'),{},'QUARANTINED'),
 ('graph_too_many',('policy','max_nodes'),3,'QUARANTINED'),
 ('descendants_too_many',('policy','max_descendants'),1,'QUARANTINED'),
 ('graph_duplicate_ids',('ledger','nodes',1,'id'),'SYN-ROOT','QUARANTINED'),
 ('graph_wrong_kind',('ledger','nodes',1,'kind'),'CHEAT','QUARANTINED'),
 ('graph_wrong_state',('ledger','nodes',1,'state'),'MAGICALLY_DONE','QUARANTINED'),
 ('graph_wrong_parent',('ledger','nodes',1,'parents'),['SYN-MISSING'],'QUARANTINED'),
]

for _name,_path,_value,_status in _CASES:
    def _case(self,path=_path,value=_value,expected=_status):
        f=fixture();set_nested(f,path,value);self.assertEqual(plan_synthetic(f)['status'],expected)
    setattr(RectificationCore,'test_case_'+_name,_case)

if __name__=='__main__':unittest.main()
