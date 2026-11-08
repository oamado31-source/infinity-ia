"""DEC-105/C unit tests; synthetic fixtures ONLY; no runtime game integration."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest
from correction_diffusion_reference import plan_synthetic

P=Path(__file__).with_name('correction_diffusion_v1.synthetic.json')
def sample():
    return json.loads(P.read_text(encoding='utf-8'))
def setpath(data,path,value):
    obj=data
    for k in path[:-1]:obj=obj[k]
    obj[path[-1]]=value

class CorrectionDiffusionCore(unittest.TestCase):
    def test_valid_authorized_delivery_creates_only_proposal(self):
        out=plan_synthetic(sample())
        self.assertEqual(out['status'],'BELIEF_REVIEW_PROPOSED')
        self.assertEqual(out['proposed_action'],'PROPOSE_EVIDENCE_BASED_RECONSIDERATION')
        self.assertEqual(out['prior_belief'],'BELIEVES_PRIOR')
    def test_no_side_effects(self):
        out=plan_synthetic(sample())
        for k in ('host_calls','engine_writes','deliveries_sent','npc_memories_changed','npc_beliefs_committed'):
            self.assertEqual(out[k],0)
        self.assertFalse(out['ledger_mutated'])
    def test_fixture_immutable(self):
        v=sample(); before=copy.deepcopy(v); plan_synthetic(v);self.assertEqual(v,before)
    def test_deterministic(self):
        v=sample();self.assertEqual(plan_synthetic(v),plan_synthetic(copy.deepcopy(v)))
    def test_trace_id_does_not_affect_dedup_key(self):
        v=sample();key=plan_synthetic(v)['case_key'];v['request']['trace_ref']='SYN-OTHER'
        self.assertEqual(plan_synthetic(v)['case_key'],key)
    def test_correction_revision_changes_dedup_key(self):
        v=sample();key=plan_synthetic(v)['case_key'];v['trusted_correction_registry']['revision']='SYN-REV-3';v['trusted_channel_ledger']['correction_revision']='SYN-REV-3'
        self.assertNotEqual(plan_synthetic(v)['case_key'],key)
    def test_new_recipient_changes_dedup_key(self):
        v=sample();key=plan_synthetic(v)['case_key'];v['request']['recipient_ref']='SYN-NPC-2';v['trusted_recipient_registry']['recipient_id']='SYN-NPC-2';v['trusted_belief_ledger']['recipient_id']='SYN-NPC-2';v['trusted_channel_ledger']['recipient_id']='SYN-NPC-2'
        self.assertNotEqual(plan_synthetic(v)['case_key'],key)
    def test_distinct_branches_not_same_key(self):
        v=sample();key=plan_synthetic(v)['case_key'];v['context']['branch_id']='SYN-BRANCH-2';
        for store in ('trusted_correction_registry','trusted_recipient_registry','trusted_channel_ledger','trusted_belief_ledger'):v[store]['branch_id']='SYN-BRANCH-2'
        self.assertNotEqual(plan_synthetic(v)['case_key'],key)
    def test_old_belief_persists(self):
        v=sample(); plan_synthetic(v)
        self.assertEqual(v['trusted_belief_ledger']['belief_before'],'BELIEVES_PRIOR')
    def test_queued_is_not_delivered(self):
        v=sample();v['trusted_channel_ledger']['state']='PENDING';self.assertEqual(plan_synthetic(v)['status'],'DELIVERY_NOT_CONFIRMED')
    def test_delivery_not_perception(self):
        v=sample();v['trusted_channel_ledger']['perception']='UNKNOWN';self.assertEqual(plan_synthetic(v)['status'],'DELIVERY_NOT_CONFIRMED')
    def test_never_heard_does_not_invent_old_belief(self):
        v=sample();v['trusted_recipient_registry']['belief_before']='NEVER_HEARD';v['trusted_belief_ledger']['belief_before']='NEVER_HEARD'
        self.assertEqual(plan_synthetic(v)['proposed_action'],'RECORD_CORRECTION_WITHOUT_INFERRING_PRIOR_BELIEF')
    def test_source_with_low_confidence_may_contest(self):
        v=sample();v['trusted_recipient_registry']['source_confidence']='LOW'
        self.assertEqual(plan_synthetic(v)['proposed_action'],'PROPOSE_CONTESTED_REVIEW')
    def test_partial_evidence_not_full_confidence(self):
        v=sample();v['trusted_correction_registry']['evidence_grade']='PARTIAL'
        self.assertEqual(plan_synthetic(v)['proposed_action'],'PROPOSE_PARTIAL_RECONSIDERATION')
    def test_contested_evidence_never_accepts(self):
        v=sample();v['trusted_correction_registry']['evidence_grade']='CONTESTED'
        self.assertEqual(plan_synthetic(v)['proposed_action'],'HOLD_DISPUTED_CLAIM')
    def test_unverified_evidence_never_accepts(self):
        v=sample();v['trusted_correction_registry']['evidence_grade']='UNVERIFIED'
        self.assertEqual(plan_synthetic(v)['proposed_action'],'HOLD_DISPUTED_CLAIM')
    def test_dedup_planned(self):
        v=sample();key=plan_synthetic(v)['case_key'];v['trusted_belief_ledger']['planned_case_keys']=[key]
        self.assertEqual(plan_synthetic(v)['status'],'DUPLICATE_SUPPRESSED')
    def test_dedup_pending(self):
        v=sample();key=plan_synthetic(v)['case_key'];v['trusted_belief_ledger']['pending_case_keys']=[key]
        self.assertEqual(plan_synthetic(v)['status'],'DUPLICATE_SUPPRESSED')
    def test_existing_belief_revision_prevents_rewrite(self):
        v=sample();v['trusted_belief_ledger']['committed_revision_refs']=['SYN-REV-2']
        self.assertEqual(plan_synthetic(v)['status'],'ALREADY_REVIEWED')
    def test_future_arrival_blocks(self):
        v=sample();v['trusted_channel_ledger']['arrived_at_tick']=222
        self.assertEqual(plan_synthetic(v)['status'],'QUARANTINED')
    def test_world_clock_mode_does_not_automatically_send(self):
        for mode in ('FROZEN','PARTIAL','REALTIME'):
            v=sample();v['context']['clock_mode']=mode;self.assertEqual(plan_synthetic(v)['status'],'BELIEF_REVIEW_PROPOSED')
    def test_no_raw_content_or_private_ids_exposed(self):
        v=sample();v['trusted_correction_registry']['protected_source_identity']='SYN-SECRET-WITNESS'; v['trusted_correction_registry']['full_text']='SYN-SECRET-TEXT'
        result=json.dumps(plan_synthetic(v))
        self.assertNotIn('SYN-SECRET-WITNESS',result);self.assertNotIn('SYN-SECRET-TEXT',result)
    def test_fake_grant_in_request_does_not_override_policy(self):
        v=sample();v['context']['authenticated_principal']='SYN-ANON';v['request']['grants_admin']=True
        self.assertEqual(plan_synthetic(v)['status'],'DENIED')

class CorrectionDiffusionNegative(unittest.TestCase):
    pass

# Each generated case is a separate unittest: explicit expected failure state and no-side-effect gate.
CASES=[
    ('wrong_source_kind',('source_kind',),'PRODUCTION','QUARANTINED'),
    ('context_not_fixture',('context','fixture_only'),False,'QUARANTINED'),
    ('fake_host',('context','host_mode'),'REAL_HOST','QUARANTINED'),
    ('missing_campaign',('context','campaign_id'),None,'QUARANTINED'),
    ('cross_campaign',('trusted_correction_registry','campaign_id'),'SYN-OTHER','QUARANTINED'),
    ('cross_branch',('trusted_recipient_registry','branch_id'),'SYN-OTHER','QUARANTINED'),
    ('cross_lineage',('trusted_channel_ledger','lineage_id'),'SYN-OTHER','QUARANTINED'),
    ('cross_build',('trusted_belief_ledger','build_fingerprint'),'SYN-OTHER','QUARANTINED'),
    ('cross_modpack',('trusted_correction_registry','modpack_hash'),'SYN-OTHER','QUARANTINED'),
    ('stale_host_epoch',('trusted_channel_ledger','host_epoch'),3,'QUARANTINED'),
    ('stale_checkpoint_epoch',('trusted_belief_ledger','checkpoint_epoch'),5,'QUARANTINED'),
    ('invalid_mode',('context','clock_mode'),'UNSAFE','QUARANTINED'),
    ('invalid_tick',('context','world_tick'),-1,'QUARANTINED'),
    ('untrusted_policy',('trusted_policy','trusted_kind'),'REQUEST_OWNED','QUARANTINED'),
    ('untrusted_correction',('trusted_correction_registry','authenticated_fixture'),False,'QUARANTINED'),
    ('untrusted_channel',('trusted_channel_ledger','authenticated_fixture'),False,'QUARANTINED'),
    ('untrusted_belief',('trusted_belief_ledger','authenticated_fixture'),False,'QUARANTINED'),
    ('untrusted_recipient',('trusted_recipient_registry','authenticated_fixture'),False,'QUARANTINED'),
    ('unknown_principal',('context','authenticated_principal'),'SYN-UNKNOWN','DENIED'),
    ('wrong_request_correction',('request','correction_ref'),'SYN-FAKE','UNKNOWN'),
    ('wrong_request_recipient',('request','recipient_ref'),'SYN-FAKE','UNKNOWN'),
    ('wrong_request_delivery',('request','delivery_ref'),'SYN-FAKE','UNKNOWN'),
    ('unauthorized_purpose',('request','purpose'),'ADMIN_OVERRIDE','DENIED'),
    ('unauthorized_audience',('request','audience'),'SYN-PUBLIC','DENIED'),
    ('unauthorized_clearance',('trusted_recipient_registry','clearance'),0,'DENIED'),
    ('protected_classification',('trusted_correction_registry','classification'),'PROTECTED','DENIED'),
    ('different_recipient_audience',('trusted_recipient_registry','audiences'),['SYN-OTHER'],'DENIED'),
    ('different_recipient_purpose',('trusted_recipient_registry','allowed_purposes'),['OTHER'],'DENIED'),
    ('different_correction_purpose',('trusted_correction_registry','purpose'),'OTHER','DENIED'),
    ('stale_belief_revision',('request','expected_ledger_revision'),8,'QUARANTINED'),
    ('invalid_policy_revision',('trusted_policy','revision'),None,'QUARANTINED'),
    ('registry_uncommitted',('trusted_correction_registry','status'),'DRAFT','QUARANTINED'),
    ('registry_untrusted_proof',('trusted_correction_registry','proof_source'),'USER_TEXT','QUARANTINED'),
    ('future_correction',('trusted_correction_registry','committed_at_tick'),230,'QUARANTINED'),
    ('invalid_evidence',('trusted_correction_registry','evidence_grade'),'MAGIC','QUARANTINED'),
    ('invalid_belief',('trusted_recipient_registry','belief_before'),'BELIEVE_FOREVER','QUARANTINED'),
    ('belief_mismatch',('trusted_belief_ledger','belief_before'),'CONTESTED','QUARANTINED'),
    ('missing_origin_family',('trusted_correction_registry','source_family'),None,'QUARANTINED'),
    ('channel_belongs_to_another',('trusted_channel_ledger','recipient_id'),'SYN-OTHER','UNKNOWN'),
    ('channel_wrong_revision',('trusted_channel_ledger','correction_revision'),'SYN-OTHER','UNKNOWN'),
    ('channel_invalid_state',('trusted_channel_ledger','state'),'ARRIVED_MAYBE','QUARANTINED'),
    ('channel_not_allowed',('trusted_channel_ledger','channel'),'SYN-TELEPATHY','DENIED'),
    ('too_many_hops',('trusted_channel_ledger','hop_count'),5,'DENIED'),
    ('negative_hops',('trusted_channel_ledger','hop_count'),-1,'DENIED'),
    ('bad_hops_type',('trusted_channel_ledger','hop_count'),'4','DENIED'),
    ('bad_max_hops_type',('trusted_policy','max_hops'),'four','DENIED'),
    ('sent_before_proof',('trusted_channel_ledger','sent_at_tick'),200,'QUARANTINED'),
    ('arrival_before_sent',('trusted_channel_ledger','arrived_at_tick'),207,'QUARANTINED'),
    ('future_send',('trusted_channel_ledger','sent_at_tick'),221,'QUARANTINED'),
    ('receipt_pending',('trusted_channel_ledger','state'),'PENDING','DELIVERY_NOT_CONFIRMED'),
    ('receipt_in_transit',('trusted_channel_ledger','state'),'IN_TRANSIT','DELIVERY_NOT_CONFIRMED'),
    ('receipt_lost',('trusted_channel_ledger','state'),'LOST','DELIVERY_NOT_CONFIRMED'),
    ('receipt_uncertain',('trusted_channel_ledger','state'),'UNCERTAIN','DELIVERY_NOT_CONFIRMED'),
    ('perception_missing',('trusted_channel_ledger','perception'),'UNKNOWN','DELIVERY_NOT_CONFIRMED'),
    ('belief_confidence_unknown',('trusted_recipient_registry','source_confidence'),'INFINITE','QUARANTINED'),
]
for name,path,val,status in CASES:
    def run_case(self,path=path,val=val,status=status):
        v=sample();setpath(v,path,val);original=copy.deepcopy(v);result=plan_synthetic(v)
        self.assertEqual(result['status'],status)
        self.assertEqual(v,original)
        self.assertEqual(result['host_calls'],0)
        self.assertEqual(result['npc_beliefs_committed'],0)
        self.assertEqual(result['deliveries_sent'],0)
    setattr(CorrectionDiffusionNegative,'test_'+name,run_case)

if __name__ == '__main__':unittest.main()
