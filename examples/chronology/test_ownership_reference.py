"""DEC-099/C synthetic preflight tests; no live engine integration or POC."""
import copy
import json
from pathlib import Path
import unittest
from ownership_reference import preflight_ownership_synthetic

ROOT = Path(__file__).parent

class OwnershipSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.f = json.loads((ROOT / 'ownership_v1.synthetic.json').read_text('utf8'))

    def plan(self):
        return preflight_ownership_synthetic(self.f)

    def status(self, iid='SYN-1'):
        return next(d['status'] for d in self.plan()['decisions'] if d['intent_id'] == iid)

    def intent(self, iid='SYN-1'):
        return next(i for i in self.f['intents'] if i['intent_id'] == iid)

    def claim(self, pid='SYN-NPC-OWNED'):
        return next(i for i in self.f['claims'] if i['persistent_id'] == pid)

    def test_no_host_calls(self):
        a = self.plan()
        self.assertEqual(a['status'], 'PREVIEW_ONLY')
        self.assertEqual(a['engine_mutations'], 0)
        self.assertEqual(a['host_calls'], 0)
    def test_synthetic_patch_proposal_only(self): self.assertEqual(self.status(), 'PROPOSE_OWNED_PATCH')
    def test_native_quest_preserved(self): self.assertEqual(self.status('SYN-2'), 'BLOCKED_OWNERSHIP')
    def test_quest_flag_protected_even_on_owned_instance(self): self.assertEqual(self.status('SYN-3'), 'BLOCKED_PROTECTED_FIELD')
    def test_input_unmodified(self):
        copy_f = copy.deepcopy(self.f);self.plan();self.assertEqual(self.f, copy_f)
    def test_order_independence(self):
        a=self.plan();self.f['intents'].reverse();self.f['claims'].reverse();self.assertEqual(self.plan(),a)
    def test_nonsynthetic_denied(self):
        self.f['source_kind']='REAL_GAME';
        with self.assertRaises(ValueError):self.plan()
    def test_fixture_gate_denied(self):
        self.f['context']['fixture_only']=False
        with self.assertRaises(ValueError):self.plan()
    def test_real_build_denied(self):
        self.f['context']['build_fingerprint']='REAL-BG2EE'
        with self.assertRaises(ValueError):self.plan()
    def test_real_host_mode_denied(self):
        self.f['context']['host_mode']='HOST_LIVE'
        with self.assertRaises(ValueError):self.plan()
    def test_missing_context_denied(self):
        del self.f['context']['campaign_id']
        with self.assertRaises(ValueError):self.plan()
    def test_stale_branch_hold(self):
        self.intent()['branch_id']='SYN-OTHER';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_campaign_hold(self):
        self.intent()['campaign_id']='SYN-OTHER';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_region_hold(self):
        self.intent()['region_id']='SYN-OTHER';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_host_epoch_hold(self):
        self.intent()['host_epoch']=10;self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_checkpoint_hold(self):
        self.intent()['checkpoint_epoch']=20;self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_modpack_hold(self):
        self.intent()['modpack_hash']='SYN-NEW';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_build_hold(self):
        self.intent()['build_fingerprint']='SYN-NEW';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_adapter_hold(self):
        self.intent()['adapter_revision']='SYN-NEW';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_stale_ruleset_hold(self):
        self.intent()['rule_revision']='SYN-NEW';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_pending_uncertain_hold(self):
        self.f['pending_actions']=[{'persistent_id':'SYN-NPC-OWNED','state':'UNCERTAIN'}];self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_pending_dispatched_hold(self):
        self.f['pending_actions']=[{'persistent_id':'SYN-NPC-OWNED','state':'DISPATCHED'}];self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_pending_prepared_hold(self):
        self.f['pending_actions']=[{'persistent_id':'SYN-NPC-OWNED','state':'PREPARED'}];self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_pending_confirmed_no_hold(self):
        self.f['pending_actions']=[{'persistent_id':'SYN-NPC-OWNED','state':'CONFIRMED'}];self.assertEqual(self.status(),'PROPOSE_OWNED_PATCH')
    def test_duplicate_intent_rejected(self):
        self.f['intents'].append(copy.deepcopy(self.f['intents'][0]));
        with self.assertRaises(ValueError):self.plan()
    def test_competing_claims_escalated(self):
        r=copy.deepcopy(self.claim());r['owner_kind']='THIRD_PARTY_MOD';self.f['claims'].append(r)
        self.assertEqual(self.status(),'ESCALATE_CONFLICT')
    def test_mod_owned_protected(self):
        self.intent()['persistent_id']='SYN-NPC-MOD';self.assertEqual(self.status(),'BLOCKED_OWNERSHIP')
    def test_player_custodian_protected(self):
        self.claim()['runtime_custodian']='PLAYER';self.assertEqual(self.status(),'BLOCKED_OWNERSHIP')
    def test_unknown_owner_preserved(self):
        self.claim()['owner_kind']='UNKNOWN';self.assertEqual(self.status(),'BLOCKED_OWNERSHIP')
    def test_missing_owner_receipt_hold(self):
        self.claim()['owner_receipt_id']='';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_recycled_instance_hold(self):
        self.intent()['instance_id']='SYN-RECYCLED';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_owner_revision_mismatch_hold(self):
        self.intent()['expected_owner_revision']='SYN-OLD-REV';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_no_authorization_blocks(self):
        self.intent()['authorized']=False;self.assertEqual(self.status(),'BLOCKED_AUTHORIZATION')
    def test_high_risk_blocks(self):
        self.intent()['risk']='HIGH';self.assertEqual(self.status(),'BLOCKED_RISK')
    def test_missing_capability_blocks(self):
        self.f['capabilities']=[];self.assertEqual(self.status(),'BLOCKED_CAPABILITY')
    def test_untested_capability_blocks(self):
        self.f['capabilities'][0]['validation']='UNTESTED';self.assertEqual(self.status(),'BLOCKED_CAPABILITY')
    def test_other_build_capability_blocks(self):
        self.f['capabilities'][0]['build_fingerprint']='SYN-OTHER';self.assertEqual(self.status(),'BLOCKED_CAPABILITY')
    def test_field_not_owned_blocks(self):
        self.claim()['allowed_fields']=[];self.assertEqual(self.status(),'BLOCKED_OWNERSHIP')
    def test_state_already_matching_noop(self):
        self.intent()['desired_state']='SYN-OLD';self.assertEqual(self.status(),'NO_OP')
    def test_retire_never_delete(self):
        self.intent()['action_type']='RETIRE';self.assertEqual(self.status(),'PRESERVE_READ_ONLY')
    def test_retire_eligible_review_only(self):
        self.intent()['action_type']='RETIRE';self.claim()['retire_eligible']=True
        self.assertEqual(self.status(),'REVIEW_RETIRE')
    def test_create_synthetic_proposal_only(self):
        it=self.intent();it['persistent_id']='SYN-NEW-ID';it['action_type']='CREATE';it['field_id']='overlay_actor';it['owner_kind']='INFINITY_AI';it['template_id']='SYN-TEMPLATE-1'
        self.assertEqual(self.status(),'PROPOSE_OWNED_CREATE')
    def test_create_partial_scan_hold(self):
        it=self.intent();it['persistent_id']='SYN-NEW-ID';it['action_type']='CREATE';it['field_id']='overlay_actor';it['owner_kind']='INFINITY_AI';it['template_id']='SYN-TEMPLATE-1'
        self.f['context']['observation_coverage']='PARTIAL'
        self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_create_unknown_scan_hold(self):
        it=self.intent();it['persistent_id']='SYN-NEW-ID';it['action_type']='CREATE';it['field_id']='overlay_actor';it['owner_kind']='INFINITY_AI';it['template_id']='SYN-TEMPLATE-1'
        self.f['context']['observation_coverage']='UNKNOWN'
        self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_create_wrong_owner_blocks(self):
        it=self.intent();it['persistent_id']='SYN-NEW-ID';it['action_type']='CREATE';it['field_id']='overlay_actor';it['owner_kind']='UNKNOWN';it['template_id']='SYN-TEMPLATE-1'
        self.assertEqual(self.status(),'BLOCKED_OWNERSHIP')
    def test_create_wrong_template_blocks(self):
        it=self.intent();it['persistent_id']='SYN-NEW-ID';it['action_type']='CREATE';it['field_id']='overlay_actor';it['owner_kind']='INFINITY_AI';it['template_id']='CRE-NATIVE'
        self.assertEqual(self.status(),'BLOCKED_OWNERSHIP')
    def test_create_existing_owner_hold(self):
        it=self.intent();it['action_type']='CREATE';it['field_id']='overlay_actor';it['owner_kind']='INFINITY_AI';it['template_id']='SYN-TEMPLATE-1'
        self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_no_owner_patch_hold(self):
        self.intent()['persistent_id']='SYN-NO-CLAIM';self.assertEqual(self.status(),'HOLD_RECONCILE')
    def test_protected_inventory_always_blocks(self):
        self.intent()['field_id']='player_inventory';self.assertEqual(self.status(),'BLOCKED_PROTECTED_FIELD')
    def test_protected_romance_always_blocks(self):
        self.intent()['field_id']='romance_state';self.assertEqual(self.status(),'BLOCKED_PROTECTED_FIELD')
    def test_schema_accepts_synthetic_fixture(self):
        import jsonschema
        sch=json.loads((ROOT/'ownership_policy_v1.candidate.schema.json').read_text('utf8'))
        jsonschema.Draft202012Validator.check_schema(sch)
        jsonschema.validate(self.f,sch)
    def test_schema_rejects_non_test_fixture(self):
        import jsonschema
        sch=json.loads((ROOT/'ownership_policy_v1.candidate.schema.json').read_text('utf8'))
        self.f['source_kind']='REAL-BG2'
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(self.f,sch)

if __name__ == '__main__':
    unittest.main()
