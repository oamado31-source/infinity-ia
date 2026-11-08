"""Unit tests DEC-098/C. SYNTHETIC ONLY; no engine, files, host or multiplayer."""
import copy
import json
import unittest
from pathlib import Path
from materializer_reference import plan_materialization_synthetic

ROOT=Path(__file__).parent
class TestMaterializationSynthetic(unittest.TestCase):
    def setUp(self):
        self.f=json.loads((ROOT/'materialization_v1.synthetic.json').read_text('utf-8'))
    def p(self):return plan_materialization_synthetic(self.f)
    def action(self,id):
        return next(a for a in self.p()['actions'] if a['persistent_id']==id)
    def test_preview_only_no_host_mutations(self):
        v=self.p();self.assertEqual(v['status'],'PROJECTION_ONLY');self.assertEqual(v['host_calls'],0)
        self.assertEqual(v['engine_mutations'],0)
    def test_present_persistent_actor_noop(self):self.assertEqual(self.action('SYN-NPC-1')['intent'],'NO_OP')
    def test_new_actor_only_proposal(self):self.assertEqual(self.action('SYN-NPC-2')['intent'],'PROPOSE_CREATE')
    def test_order_independence(self):
        first=self.p()
        self.f['desired']['entities'].reverse()
        self.assertEqual(first,self.p())
    def test_no_input_mutation(self):
        copy_f=copy.deepcopy(self.f);self.p();self.assertEqual(copy_f,self.f)
    def test_nonsynthetic_source_rejected(self):
        self.f['source_kind']='REAL_CANON'
        with self.assertRaises(ValueError):self.p()
    def test_fake_fixture_gate_rejected(self):
        self.f['context']['fixture_only']=False
        with self.assertRaises(ValueError):self.p()
    def test_wrong_branch_rejected(self):
        self.f['observation']['branch_id']='SYN-OTHER'
        with self.assertRaises(ValueError):self.p()
    def test_wrong_host_epoch_rejected(self):
        self.f['snapshot']['host_epoch']=6
        with self.assertRaises(ValueError):self.p()
    def test_wrong_checkpoint_rejected(self):
        self.f['observation']['checkpoint_epoch']=8
        with self.assertRaises(ValueError):self.p()
    def test_wrong_pack_rejected(self):
        self.f['desired']['pack_hash']='SYN-DIFFERENT'
        with self.assertRaises(ValueError):self.p()
    def test_wrong_build_rejected(self):
        self.f['snapshot']['build_fingerprint']='SYN-OTHER-BUILD'
        with self.assertRaises(ValueError):self.p()
    def test_duplicate_desired_id_rejected(self):
        self.f['desired']['entities'].append(copy.deepcopy(self.f['desired']['entities'][1]))
        with self.assertRaises(ValueError):self.p()
    def test_duplicate_observed_id_rejected(self):
        self.f['observation']['entities'].append(copy.deepcopy(self.f['observation']['entities'][0]))
        with self.assertRaises(ValueError):self.p()
    def test_partial_observation_no_create(self):
        self.f['observation']['coverage']='PARTIAL'
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'HOLD_RECONCILE')
    def test_unknown_observation_no_create(self):
        self.f['observation']['coverage']='UNKNOWN'
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'HOLD_RECONCILE')
    def test_native_collision_no_create(self):
        self.f['observation']['entities'].append({'persistent_id':'SYN-NPC-2',
               'owner_kind':'NATIVE_OR_MOD','instance_id':'SYN-NATIVE'})
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'BLOCKED_OWNERSHIP')
    def test_observed_unknown_without_snapshot_hold(self):
        self.f['observation']['entities'].append({'persistent_id':'SYN-NPC-2',
               'owner_kind':'INFINITY_AI','instance_id':'SYN-ORPHAN'})
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'HOLD_RECONCILE')
    def test_snapshot_missing_from_host_never_clone(self):
        self.f['observation']['entities']=[]
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'HOLD_RECONCILE')
    def test_instance_id_recycled_holds(self):
        self.f['observation']['entities'][0]['instance_id']='SYN-DIFFERENT'
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'HOLD_RECONCILE')
    def test_owner_receipt_mismatch_holds(self):
        self.f['observation']['entities'][0]['ownership_receipt_id']='SYN-FOREIGN'
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'HOLD_RECONCILE')
    def test_no_create_capability_blocks(self):
        self.f['context']['capabilities']=[]
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'BLOCKED_CAPABILITY')
    def test_no_quota_blocks(self):
        self.f['context']['max_new_entities']=0
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'BLOCKED_QUOTA')
    def test_high_risk_no_create(self):
        self.f['desired']['entities'][1]['risk']='HIGH'
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'BLOCKED_RISK')
    def test_unauthorized_no_create(self):
        self.f['desired']['entities'][1]['approved']=False
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'BLOCKED_AUTHORIZATION')
    def test_template_not_allowlisted(self):
        self.f['desired']['entities'][1]['template_id']='CRE-X'
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'BLOCKED_TEMPLATE')
    def test_pending_dispatched_prevents_create(self):
        self.f['pending_actions']=[{'persistent_id':'SYN-NPC-2','state':'DISPATCHED'}]
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'HOLD_RECONCILE')
    def test_uncertain_prevents_create(self):
        self.f['pending_actions']=[{'persistent_id':'SYN-NPC-2','state':'UNCERTAIN'}]
        self.assertEqual(self.action('SYN-NPC-2')['intent'],'HOLD_RECONCILE')
    def test_retire_is_review_not_delete(self):
        self.f['desired']['entities']=[self.f['desired']['entities'][1]]
        self.f['snapshot']['entities'][0]['retire_eligible']=True
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'REVIEW_RETIRE')
    def test_not_retireable_noop(self):
        self.f['desired']['entities']=[self.f['desired']['entities'][1]]
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'NO_OP')
    def test_patch_is_proposal_only(self):
        self.f['desired']['entities'][0]['target_state']='WAITING'
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'PROPOSE_UPDATE')
    def test_patch_without_capability_blocks(self):
        self.f['context']['capabilities']=['PROPOSE_CREATE']
        self.f['desired']['entities'][0]['target_state']='WAITING'
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'BLOCKED_CAPABILITY')
    def test_patch_template_conflict_holds(self):
        self.f['desired']['entities'][0]['template_id']='SYN-TEMPLATE-OTHER'
        self.assertEqual(self.action('SYN-NPC-1')['intent'],'HOLD_RECONCILE')
    def test_catchup_bounded(self):
        self.f['context']['world_tick']=200
        self.f['desired']['world_tick']=200
        v=self.p();self.assertEqual(v['world_tick_evaluated_through'],103)
        self.assertEqual(v['remaining_backlog_ticks'],97)
    def test_frozen_no_catchup(self):
        self.f['context']['time_mode']='FROZEN'
        v=self.p();self.assertEqual(v['world_tick_evaluated_through'],100)
        self.assertEqual(v['remaining_backlog_ticks'],0)
    def test_time_regression_rejected(self):
        self.f['snapshot']['last_confirmed_world_tick']=110
        with self.assertRaises(ValueError):self.p()
    def test_schema_validates_fixture(self):
        import jsonschema
        sch=json.loads((ROOT/'materialization_plan_v1.candidate.schema.json').read_text('utf-8'))
        jsonschema.Draft202012Validator.check_schema(sch)
        jsonschema.validate(self.f,sch)
    def test_schema_rejects_nonsynthetic(self):
        import jsonschema
        sch=json.loads((ROOT/'materialization_plan_v1.candidate.schema.json').read_text('utf-8'))
        self.f['source_kind']='PRODUCTION'
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(self.f,sch)

if __name__=='__main__':unittest.main()
