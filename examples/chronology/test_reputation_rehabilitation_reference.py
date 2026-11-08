"""DEC-106/C tests: synthetic-only planner, no motor/host/LLM use."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
import jsonschema
from reputation_rehabilitation_reference import plan_synthetic

ROOT=Path(__file__).parent
FIX=json.loads((ROOT/'reputation_rehabilitation_v1.synthetic.json').read_text('utf-8'))
SCHEMA=json.loads((ROOT/'reputation_rehabilitation_v1.candidate.schema.json').read_text('utf-8'))


def changed(path, value):
    f=copy.deepcopy(FIX)
    obj=f
    for p in path[:-1]:obj=obj[p]
    obj[path[-1]]=value
    return f


class ReputationRehabilitationReferenceTest(unittest.TestCase):
    def test_fixture_schema(self):
        jsonschema.Draft202012Validator.check_schema(SCHEMA)
        jsonschema.validate(FIX,SCHEMA)

    def test_fixture_result_no_effects(self):
        r=plan_synthetic(copy.deepcopy(FIX))
        self.assertEqual(r['status'],'PROPOSAL_READY')
        self.assertEqual(r['proposed_social_action'],'PROPOSE_VOLUNTARY_REENGAGEMENT')
        self.assertEqual(r['suggested_harm_next_step'],'REFER_TO_SEPARATE_RESTITUTION_REVIEW')
        self._safe(r)

    def _safe(self,r):
        self.assertTrue(r['proposal_only'])
        for k in ('host_calls','currency_transferred','reputation_points_written','npcs_compelled','notices_sent','facts_erased'):
            self.assertEqual(r[k],0,k)
        self.assertFalse(r['stored_events_mutated'])

    def test_no_input_mutation(self):
        f=copy.deepcopy(FIX);before=copy.deepcopy(f)
        plan_synthetic(f)
        self.assertEqual(f,before)

    def test_determinism(self):
        self.assertEqual(plan_synthetic(FIX),plan_synthetic(FIX))

    def test_trace_not_in_proposal_key(self):
        other=changed(['request','trace_ref'],'SYN-OTHER-TRACE')
        self.assertEqual(plan_synthetic(FIX)['case_key'],plan_synthetic(other)['case_key'])

    def test_case_isolation(self):
        other=changed(['context','branch_id'],'SYN-DIFFERENT-BRANCH')
        self.assertEqual(plan_synthetic(other)['status'],'QUARANTINED')

    def test_lost_delivery_requires_scoped_notice(self):
        other=changed(['trusted_correction_delivery','state'],'LOST')
        self.assertEqual(plan_synthetic(other)['proposed_social_action'],'PROPOSE_SCOPED_CORRECTION_NOTICE')

    def test_no_trust_on_delivered_unperceived(self):
        other=changed(['trusted_correction_delivery','perception'],'UNKNOWN')
        self.assertEqual(plan_synthetic(other)['proposed_social_action'],'WAIT_FOR_CORRECTION_PERCEPTION')

    def test_no_harm_double_count(self):
        other=changed(['trusted_harm_ledger','state'],'ALLEGED')
        self.assertEqual(plan_synthetic(other)['suggested_harm_next_step'],'REQUEST_EVIDENCE_FOR_HARM')

    def test_no_reputation_change_even_after_belief_revision(self):
        other=changed(['trusted_belief_ledger','trust_state'],'WILLING_TO_REENGAGE')
        r=plan_synthetic(other)
        self.assertEqual(r['proposed_social_action'],'NO_FORCED_ADDITIONAL_TRUST_CHANGE')
        self._safe(r)

    def test_pending_ledger_key_dedup(self):
        key=plan_synthetic(FIX)['case_key']
        f=changed(['trusted_rehabilitation_ledger','pending_case_keys'],[key])
        self.assertEqual(plan_synthetic(f)['status'],'ALREADY_PLANNED')

    def test_committed_ledger_key_dedup(self):
        key=plan_synthetic(FIX)['case_key']
        f=changed(['trusted_rehabilitation_ledger','committed_case_keys'],[key])
        self.assertEqual(plan_synthetic(f)['status'],'ALREADY_REGISTERED')

    def test_original_claim_unheard_does_not_infer_exposure(self):
        f=changed(['trusted_exposure_ledger','state'],'NOT_OBSERVED')
        self.assertEqual(plan_synthetic(f)['status'],'NO_REPUTATIONAL_EXPOSURE')

    def test_pc_consent_required(self):
        f=copy.deepcopy(FIX);f['trusted_subject_registry']['kind']='PC'
        self.assertEqual(plan_synthetic(f)['reason'],'PC_OWNER_CONSENT_REQUIRED')

    def test_pc_consent_alone_not_overriding_other_gates(self):
        f=copy.deepcopy(FIX);f['trusted_subject_registry']['kind']='PC'
        f['trusted_case_registry']['pc_owner_consent']=True
        self.assertEqual(plan_synthetic(f)['status'],'PROPOSAL_READY')
        self._safe(plan_synthetic(f))

    def test_schema_rejects_self_grant(self):
        f=copy.deepcopy(FIX);f['request']['grant_access']=True
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(f,SCHEMA)
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')

    def test_schema_rejects_untrusted_data(self):
        f=copy.deepcopy(FIX);f['source_kind']='REAL_GAME'
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(f,SCHEMA)
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')

    def test_schema_rejects_boolean_epoch(self):
        f=changed(['context','host_epoch'],True)
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(f,SCHEMA)
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')

    def test_correction_precedes_delivery(self):
        f=changed(['trusted_correction_delivery','arrived_at_tick'],200)
        self.assertEqual(plan_synthetic(f)['reason'],'INVALID_DELIVERY_TIME')

    def test_no_unauthorized_payment_even_with_host_receipt(self):
        r=plan_synthetic(FIX)
        self.assertEqual(r['currency_transferred'],0)
        self.assertNotIn('payment_amount',r)

    def test_scope_rejection_for_each_authority(self):
        for store in ('trusted_correction_registry','trusted_subject_registry','trusted_case_registry',
                      'trusted_exposure_ledger','trusted_correction_delivery','trusted_belief_ledger',
                      'trusted_reputation_context','trusted_harm_ledger','trusted_rehabilitation_ledger'):
            with self.subTest(store=store):
                f=changed([store,'branch_id'],'SYN-OTHER')
                self.assertEqual(plan_synthetic(f)['reason'],'CROSS_SCOPE_OR_STALE_AUTHORITY')


# Individual scenarios are generated deterministically as distinct unit methods,
# unlike looped subtests, to keep the runner's count verifiable.
SCENARIOS = [
    (('source_kind',), 'RAW_LLM', 'QUARANTINED'),
    (('context','fixture_only'),False,'QUARANTINED'),
    (('context','host_mode'),'REAL_HOST','QUARANTINED'),
    (('context','campaign_id'),'REAL-CAMPAIGN','QUARANTINED'),
    (('context','world_tick'),-1,'QUARANTINED'),
    (('context','clock_mode'),'INVALID','QUARANTINED'),
    (('context','authenticated_principal'),'SYN-INTRUDER','DENIED'),
    (('request','case_ref'),'SYN-UNRELATED','UNKNOWN'),
    (('request','subject_ref'),'SYN-OTHER','UNKNOWN'),
    (('request','purpose'),'BROADCAST','DENIED'),
    (('request','audience'),'SYN-PUBLIC','DENIED'),
    (('request','expected_revision'),10,'QUARANTINED'),
    (('trusted_policy','trusted_kind'),'UNSIGNED','QUARANTINED'),
    (('trusted_policy','revision'),None,'QUARANTINED'),
    (('trusted_policy','authorized_principals'),[],'DENIED'),
    (('trusted_policy','allowed_dimensions'),[],'QUARANTINED'),
    (('trusted_correction_registry','status'),'DRAFT','QUARANTINED'),
    (('trusted_correction_registry','source'),'LLM_GUESS','QUARANTINED'),
    (('trusted_correction_registry','grade'),'CONTESTED','QUARANTINED'),
    (('trusted_correction_registry','committed_at_tick'),231,'QUARANTINED'),
    (('trusted_correction_registry','source_family'),'','QUARANTINED'),
    (('trusted_correction_registry','claim_ref'),None,'QUARANTINED'),
    (('trusted_correction_registry','subject_id'),'SYN-OTHER','QUARANTINED'),
    (('trusted_correction_registry','classification'),'PROTECTED','DENIED'),
    (('trusted_subject_registry','kind'),'UNKNOWN','QUARANTINED'),
    (('trusted_subject_registry','owner_attested'),False,'QUARANTINED'),
    (('trusted_subject_registry','clearance'),0,'DENIED'),
    (('trusted_subject_registry','allowed_audiences'),[],'DENIED'),
    (('trusted_case_registry','status'),'CLOSED','DENIED'),
    (('trusted_case_registry','consent_status'),'WITHDRAWN','DENIED'),
    (('trusted_case_registry','authorized_principal'),'SYN-OTHER','DENIED'),
    (('trusted_case_registry','correction_ref'),'SYN-OTHER','QUARANTINED'),
    (('trusted_case_registry','subject_id'),'SYN-OTHER','QUARANTINED'),
    (('trusted_case_registry','reputation_context_id'),'SYN-OTHER','QUARANTINED'),
    (('trusted_case_registry','high_risk_unresolved'),True,'QUARANTINED'),
    (('trusted_exposure_ledger','claim_ref'),'SYN-OTHER','QUARANTINED'),
    (('trusted_exposure_ledger','state'),'MAYBE','QUARANTINED'),
    (('trusted_exposure_ledger','heard_at_tick'),231,'QUARANTINED'),
    (('trusted_correction_delivery','state'),'UNCERTAIN','QUARANTINED'),
    (('trusted_correction_delivery','correction_id'),'SYN-OTHER','QUARANTINED'),
    (('trusted_correction_delivery','revision'),'SYN-OTHER','QUARANTINED'),
    (('trusted_correction_delivery','audience'),'SYN-OTHER','QUARANTINED'),
    (('trusted_correction_delivery','arrived_at_tick'),231,'QUARANTINED'),
    (('trusted_belief_ledger','state'),'INVALID','QUARANTINED'),
    (('trusted_belief_ledger','trust_state'),'INVALID','QUARANTINED'),
    (('trusted_belief_ledger','subject_context_id'),'SYN-OTHER','QUARANTINED'),
    (('trusted_reputation_context','dimension'),'ALL_WORLD','QUARANTINED'),
    (('trusted_reputation_context','audience'),'SYN-OTHER','QUARANTINED'),
    (('trusted_reputation_context','owner_attested'),False,'QUARANTINED'),
    (('trusted_reputation_context','high_risk_unresolved'),True,'QUARANTINED'),
    (('trusted_reputation_context','subject_id'),'SYN-OTHER','QUARANTINED'),
    (('trusted_harm_ledger','claim_ref'),'SYN-OTHER','QUARANTINED'),
    (('trusted_harm_ledger','state'),'UNSUPPORTED','QUARANTINED'),
    (('trusted_harm_ledger','host_receipt_ref'),None,'QUARANTINED'),
    (('trusted_rehabilitation_ledger','revision'),12,'QUARANTINED'),
    (('trusted_rehabilitation_ledger','trusted_kind'),'FORGED','QUARANTINED'),
    (('trusted_rehabilitation_ledger','authenticated_fixture'),False,'QUARANTINED'),
]


def _make_case(i,path,value,status):
    def run(self):
        f=changed(path,value)
        r=plan_synthetic(f)
        self.assertEqual(r['status'],status,(path,value,r))
        self._safe(r)
    run.__name__=f'test_scenario_{i:03d}_{path[-1]}'
    return run

for i,(path,value,status) in enumerate(SCENARIOS,1):
    setattr(ReputationRehabilitationReferenceTest,f'test_scenario_{i:03d}',_make_case(i,path,value,status))


if __name__=='__main__':unittest.main()
