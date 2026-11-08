"""DEC-108 synthetic tests, not BG2/EEex integration or rights attestation."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator,ValidationError
from agreement_fulfillment_reference import plan_synthetic,SCHEMA,PROHIBITED_OUTPUT_FIELDS

BASE=json.loads(Path(__file__).with_name('agreement_fulfillment_v1.synthetic.json').read_text())
VALIDATOR=Draft202012Validator(SCHEMA)

def modify(path,value):
    f=copy.deepcopy(BASE)
    cur=f
    for part in path[:-1]:cur=cur[part]
    cur[path[-1]]=value
    return f

def safe(res):
    assert res['host_action']=='NONE'
    assert res['mechanical_effects'] is False
    assert res['punishment'] is False
    assert not PROHIBITED_OUTPUT_FIELDS.intersection(res)

class TestAgreementFulfillment(unittest.TestCase):
    def test_fixture_valid(self):VALIDATOR.validate(BASE)
    def test_schema_valid(self):Draft202012Validator.check_schema(SCHEMA)
    def test_baseline(self):
        r=plan_synthetic(BASE);self.assertEqual(r['status'],'PARTIAL_CONFIRMED');self.assertEqual(r['confirmed_amount'],'6');self.assertEqual(r['remaining_unproven'],'4');safe(r)
    def test_is_pure(self):
        f=copy.deepcopy(BASE);r=plan_synthetic(f);self.assertEqual(BASE,f);safe(r)
    def test_deterministic(self):
        self.assertEqual(plan_synthetic(BASE),plan_synthetic(copy.deepcopy(BASE)))
    def test_trace_does_not_change_key(self):
        x=plan_synthetic(modify(['request','trace_ref'],'SYN-T2'))
        self.assertEqual(plan_synthetic(BASE)['proposal_key'],x['proposal_key'])
    def test_time_changes_key(self):
        x=plan_synthetic(modify(['context','world_tick'],16))
        self.assertNotEqual(plan_synthetic(BASE)['proposal_key'],x['proposal_key'])
    def test_agreement_draft(self):
        self.assertEqual(plan_synthetic(modify(['trusted_agreement_registry','commit_state'],'DRAFT'))['reason'],'AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID')
    def test_claim_without_receipt(self):
        f=copy.deepcopy(BASE);f['trusted_receipt_ledger']['receipts']=[]
        f['trusted_claim_ledger']['claims']=[{'claim_id':'SYN-CLAIM-1','author':'SYN-ORG-A','alleged_amount':10,'statement_ref':'SYN-STATEMENT-1'}]
        r=plan_synthetic(f);self.assertEqual(r['status'],'CLAIMED_UNVERIFIED');self.assertEqual(r['confirmed_amount'],'0');safe(r)
    def test_due_no_receipts(self):
        f=copy.deepcopy(BASE);f['trusted_receipt_ledger']['receipts']=[];f['context']['world_tick']=20
        r=plan_synthetic(f);self.assertEqual(r['status'],'OVERDUE_UNVERIFIED');self.assertTrue(r['no_penalty']);safe(r)
    def test_due_frozen_no_wallclock(self):
        f=copy.deepcopy(BASE);f['trusted_receipt_ledger']['receipts']=[];f['context']['clock_mode']='FROZEN';f['context']['world_tick']=15
        self.assertEqual(plan_synthetic(f)['status'],'WAITING')
    def test_total_fulfilled_candidate(self):
        f=copy.deepcopy(BASE);f['trusted_receipt_ledger']['receipts'][0]['amount']=10
        r=plan_synthetic(f);self.assertEqual(r['status'],'FULFILLMENT_CANDIDATE');self.assertFalse(r['mechanical_effects'])
    def test_multiple_confirmed_receipts(self):
        f=copy.deepcopy(BASE);b=copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0]);b.update(receipt_id='SYN-R-2',action_id='SYN-ACTION-2',amount=4)
        f['trusted_receipt_ledger']['receipts'].append(b)
        self.assertEqual(plan_synthetic(f)['status'],'FULFILLMENT_CANDIDATE')
    def test_order_independent(self):
        f=copy.deepcopy(BASE);b=copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0]);b.update(receipt_id='SYN-R-2',action_id='SYN-ACTION-2',amount=4)
        f['trusted_receipt_ledger']['receipts'].append(b)
        x=plan_synthetic(f);f['trusted_receipt_ledger']['receipts'].reverse();y=plan_synthetic(f)
        self.assertEqual(x,y)
    def test_receipt_failed_not_counted(self):
        f=modify(['trusted_receipt_ledger','receipts',0,'status'],'FAILED')
        self.assertEqual(plan_synthetic(f)['confirmed_amount'],'0')
    def test_receipt_cancelled_not_counted(self):
        f=modify(['trusted_receipt_ledger','receipts',0,'status'],'CANCELLED')
        self.assertEqual(plan_synthetic(f)['confirmed_amount'],'0')
    def test_receipt_duplicate(self):
        f=copy.deepcopy(BASE);f['trusted_receipt_ledger']['receipts'].append(copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0]));self.assertEqual(plan_synthetic(f)['reason'],'RECEIPT_ID_DUPLICATE')
    def test_action_duplicate(self):
        f=copy.deepcopy(BASE);b=copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0]);b['receipt_id']='SYN-R-2';f['trusted_receipt_ledger']['receipts'].append(b)
        self.assertEqual(plan_synthetic(f)['reason'],'ACTION_ID_DUPLICATE')
    def test_overdelivery_not_credit(self):
        f=modify(['trusted_receipt_ledger','receipts',0,'amount'],11)
        self.assertEqual(plan_synthetic(f)['reason'],'OVERDELIVERY_NOT_AUTOMATIC_CREDIT')
    def test_approved_overdelivery_still_no_transfer(self):
        f=modify(['trusted_term_registry','allow_overdelivery'],True)
        f['trusted_receipt_ledger']['receipts'][0]['amount']=11
        r=plan_synthetic(f);self.assertEqual(r['status'],'FULFILLMENT_CANDIDATE');safe(r)
    def test_dispute(self):
        f=modify(['trusted_claim_ledger','is_contested'],True)
        r=plan_synthetic(f);self.assertEqual(r['status'],'CONTESTED');safe(r)
    def test_force_majeure_alleged(self):
        f=modify(['trusted_claim_ledger','force_majeure_alleged'],True)
        r=plan_synthetic(f);self.assertEqual(r['proposed_action'],'PROPOSE_VOLUNTARY_RENEGOTIATION');safe(r)
    def test_high_risk_no_enforcement(self):
        f=modify(['trusted_term_registry','high_risk_unresolved'],True)
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_public_view_not_authorized(self):
        f=modify(['request','audience'],'PUBLIC')
        self.assertEqual(plan_synthetic(f)['reason'],'AUDIENCE_UNAUTHORIZED')
    def test_principal_not_authorized(self):
        f=modify(['context','authenticated_principal'],'SYN-STRANGER')
        self.assertEqual(plan_synthetic(f)['reason'],'PRINCIPAL_UNAUTHORIZED')
    def test_outbox_same_key(self):
        f=copy.deepcopy(BASE);f['trusted_outbox_ledger']['pending_proposal_keys'].append(plan_synthetic(f)['proposal_key'])
        self.assertEqual(plan_synthetic(f)['reason'],'PROPOSAL_IN_OUTBOX_RECONCILE')
    def test_ledger_uncertain(self):
        f=modify(['trusted_outbox_ledger','state'],'UNCERTAIN')
        self.assertEqual(plan_synthetic(f)['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION')
    def test_ledger_dispatched(self):
        f=modify(['trusted_outbox_ledger','state'],'DISPATCHED')
        self.assertEqual(plan_synthetic(f)['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION')
    def test_receipt_future(self):
        f=modify(['trusted_receipt_ledger','receipts',0,'world_tick'],21)
        self.assertEqual(plan_synthetic(f)['reason'],'RECEIPT_FROM_FUTURE')
    def test_receipt_uncertain(self):
        f=modify(['trusted_receipt_ledger','receipts',0,'status'],'UNCERTAIN')
        self.assertEqual(plan_synthetic(f)['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION')
    def test_context_other_branch(self):
        f=modify(['context','branch_id'],'SYN-OTHER-BRANCH')
        self.assertEqual(plan_synthetic(f)['reason'],'TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH')
    def test_receipt_wrong_scope(self):
        f=modify(['trusted_receipt_ledger','receipts',0,'host_epoch'],19)
        self.assertEqual(plan_synthetic(f)['reason'],'RECEIPT_SCOPE_OR_AUTHENTICATION_MISMATCH')
    def test_schema_rejects_self_permission(self):
        f=copy.deepcopy(BASE);f['request']['grant_payment']=True
        self.assertEqual(plan_synthetic(f)['reason'],'SCHEMA_OR_FIXTURE_INVALID')
    def test_schema_rejects_raw_host(self):
        f=copy.deepcopy(BASE);f['context']['host_mode']='BG2EE_REAL'
        self.assertEqual(plan_synthetic(f)['reason'],'SCHEMA_OR_FIXTURE_INVALID')
    def test_schema_rejects_wrong_number_type(self):
        f=copy.deepcopy(BASE);f['trusted_term_registry']['amount']='10'
        self.assertEqual(plan_synthetic(f)['reason'],'SCHEMA_OR_FIXTURE_INVALID')
    def test_missing_receipt_field(self):
        f=copy.deepcopy(BASE);del f['trusted_receipt_ledger']['receipts'][0]['authenticated_fixture']
        self.assertEqual(plan_synthetic(f)['reason'],'SCHEMA_OR_FIXTURE_INVALID')
    def test_not_signed_receipt(self):
        f=modify(['trusted_receipt_ledger','receipts',0,'authenticated_fixture'],False)
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')

    def test_mutation_01_wrong_campaign(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'campaign_id'],'SYN-OTHER'));self.assertEqual(r['reason'],'TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH');safe(r)

    def test_mutation_02_wrong_branch(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'branch_id'],'SYN-OTHER'));self.assertEqual(r['reason'],'TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH');safe(r)

    def test_mutation_03_wrong_lineage(self):
        r=plan_synthetic(modify(['trusted_agreement_registry', 'lineage_id'],'SYN-OTHER'));self.assertEqual(r['reason'],'TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH');safe(r)

    def test_mutation_04_wrong_checkpoint(self):
        r=plan_synthetic(modify(['trusted_claim_ledger', 'checkpoint_epoch'],20));self.assertEqual(r['reason'],'TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH');safe(r)

    def test_mutation_05_wrong_build(self):
        r=plan_synthetic(modify(['trusted_outbox_ledger', 'build_fingerprint'],'SYN-OTHER'));self.assertEqual(r['reason'],'TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH');safe(r)

    def test_mutation_06_wrong_modpack(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'modpack_hash'],'SYN-OTHER'));self.assertEqual(r['reason'],'TRUSTED_LEDGER_SCOPE_OR_AUTHENTICATION_MISMATCH');safe(r)

    def test_mutation_07_agreement_not_authenticated(self):
        r=plan_synthetic(modify(['trusted_agreement_registry', 'authenticated_fixture'],False));self.assertEqual(r['reason'],'SCHEMA_OR_FIXTURE_INVALID');safe(r)

    def test_mutation_08_term_not_authenticated(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'authenticated_fixture'],False));self.assertEqual(r['reason'],'SCHEMA_OR_FIXTURE_INVALID');safe(r)

    def test_mutation_09_claims_not_authenticated(self):
        r=plan_synthetic(modify(['trusted_claim_ledger', 'authenticated_fixture'],False));self.assertEqual(r['reason'],'SCHEMA_OR_FIXTURE_INVALID');safe(r)

    def test_mutation_10_outbox_not_authenticated(self):
        r=plan_synthetic(modify(['trusted_outbox_ledger', 'authenticated_fixture'],False));self.assertEqual(r['reason'],'SCHEMA_OR_FIXTURE_INVALID');safe(r)

    def test_mutation_11_policy_not_authenticated(self):
        r=plan_synthetic(modify(['trusted_policy', 'authenticated_fixture'],False));self.assertEqual(r['reason'],'SCHEMA_OR_FIXTURE_INVALID');safe(r)

    def test_mutation_12_policy_mismatch(self):
        r=plan_synthetic(modify(['trusted_policy', 'revision'],'SYN-OTHER'));self.assertEqual(r['reason'],'POLICY_NOT_VERIFIED');safe(r)

    def test_mutation_13_agreement_pending(self):
        r=plan_synthetic(modify(['trusted_agreement_registry', 'commit_state'],'PENDING'));self.assertEqual(r['reason'],'AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID');safe(r)

    def test_mutation_14_agreement_revoked(self):
        r=plan_synthetic(modify(['trusted_agreement_registry', 'commit_state'],'REVOKED'));self.assertEqual(r['reason'],'AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID');safe(r)

    def test_mutation_15_no_commit_receipt(self):
        r=plan_synthetic(modify(['trusted_agreement_registry', 'commit_receipt_authenticated'],False));self.assertEqual(r['reason'],'AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID');safe(r)

    def test_mutation_16_mandate_invalid(self):
        r=plan_synthetic(modify(['trusted_agreement_registry', 'mandate_valid'],False));self.assertEqual(r['reason'],'AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID');safe(r)

    def test_mutation_17_term_amended(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'status'],'AMENDED'));self.assertEqual(r['reason'],'AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID');safe(r)

    def test_mutation_18_term_terminated(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'status'],'TERMINATED'));self.assertEqual(r['reason'],'AGREEMENT_NOT_COMMITTED_OR_MANDATE_INVALID');safe(r)

    def test_mutation_19_agreement_ref_wrong(self):
        r=plan_synthetic(modify(['request', 'agreement_ref'],'SYN-WRONG'));self.assertEqual(r['reason'],'AGREEMENT_TERM_MISMATCH');safe(r)

    def test_mutation_20_term_ref_wrong(self):
        r=plan_synthetic(modify(['request', 'term_ref'],'SYN-WRONG'));self.assertEqual(r['reason'],'AGREEMENT_TERM_MISMATCH');safe(r)

    def test_mutation_21_term_agreement_mismatch(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'agreement_id'],'SYN-WRONG'));self.assertEqual(r['reason'],'AGREEMENT_TERM_MISMATCH');safe(r)

    def test_mutation_22_agreement_revision_stale(self):
        r=plan_synthetic(modify(['request', 'expected_agreement_revision'],2));self.assertEqual(r['reason'],'STALE_REVISION');safe(r)

    def test_mutation_23_term_revision_stale(self):
        r=plan_synthetic(modify(['request', 'expected_term_revision'],2));self.assertEqual(r['reason'],'STALE_REVISION');safe(r)

    def test_mutation_24_term_wrong_obligor(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'obligor'],'SYN-STRANGER'));self.assertEqual(r['reason'],'TERM_PARTIES_INVALID');safe(r)

    def test_mutation_25_term_same_party(self):
        r=plan_synthetic(modify(['trusted_term_registry', 'beneficiary'],'SYN-ORG-A'));self.assertEqual(r['reason'],'TERM_PARTIES_INVALID');safe(r)

    def test_mutation_26_receipt_ledger_term_mismatch(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'term_id'],'SYN-WRONG'));self.assertEqual(r['reason'],'LEDGER_LINK_INVALID');safe(r)

    def test_mutation_27_claim_ledger_agreement_mismatch(self):
        r=plan_synthetic(modify(['trusted_claim_ledger', 'agreement_id'],'SYN-WRONG'));self.assertEqual(r['reason'],'LEDGER_LINK_INVALID');safe(r)

    def test_mutation_28_outbox_agreement_mismatch(self):
        r=plan_synthetic(modify(['trusted_outbox_ledger', 'agreement_id'],'SYN-WRONG'));self.assertEqual(r['reason'],'LEDGER_LINK_INVALID');safe(r)

    def test_mutation_29_receipt_ledger_revision_mismatch(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'term_revision'],2));self.assertEqual(r['reason'],'TERM_LEDGER_REVISION_MISMATCH');safe(r)

    def test_mutation_30_claim_ledger_revision_mismatch(self):
        r=plan_synthetic(modify(['trusted_claim_ledger', 'term_revision'],2));self.assertEqual(r['reason'],'TERM_LEDGER_REVISION_MISMATCH');safe(r)

    def test_mutation_31_receipt_wrong_unit(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'receipts', 0, 'unit'],'GOLD'));self.assertEqual(r['reason'],'RECEIPT_TARGET_OR_UNIT_MISMATCH');safe(r)

    def test_mutation_32_receipt_wrong_obligor(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'receipts', 0, 'from_party'],'SYN-OTHER'));self.assertEqual(r['reason'],'RECEIPT_TARGET_OR_UNIT_MISMATCH');safe(r)

    def test_mutation_33_receipt_wrong_beneficiary(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'receipts', 0, 'to_party'],'SYN-OTHER'));self.assertEqual(r['reason'],'RECEIPT_TARGET_OR_UNIT_MISMATCH');safe(r)

    def test_mutation_34_receipt_wrong_term(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'receipts', 0, 'term_id'],'SYN-OTHER'));self.assertEqual(r['reason'],'RECEIPT_TARGET_OR_UNIT_MISMATCH');safe(r)

    def test_mutation_35_receipt_wrong_term_rev(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'receipts', 0, 'term_revision'],2));self.assertEqual(r['reason'],'RECEIPT_TARGET_OR_UNIT_MISMATCH');safe(r)

    def test_mutation_36_pending_receipt_action(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'pending_actions'],['SYN-ACTION-99']));self.assertEqual(r['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION');safe(r)

    def test_mutation_37_dispatched_receipt_action(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'dispatched_actions'],['SYN-ACTION-99']));self.assertEqual(r['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION');safe(r)

    def test_mutation_38_uncertain_receipt_action(self):
        r=plan_synthetic(modify(['trusted_receipt_ledger', 'uncertain_actions'],['SYN-ACTION-99']));self.assertEqual(r['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION');safe(r)

    def test_mutation_39_pending_outbox_action(self):
        r=plan_synthetic(modify(['trusted_outbox_ledger', 'pending_actions'],['SYN-ACTION-99']));self.assertEqual(r['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION');safe(r)

    def test_mutation_40_high_risk_policy(self):
        r=plan_synthetic(modify(['trusted_policy', 'high_risk_unresolved'],True));self.assertEqual(r['reason'],'HIGH_RISK_REQUIRES_AUTHORIZATION');safe(r)

    def test_mutation_41_high_risk_agreement(self):
        r=plan_synthetic(modify(['trusted_agreement_registry', 'high_risk_unresolved'],True));self.assertEqual(r['reason'],'HIGH_RISK_REQUIRES_AUTHORIZATION');safe(r)

    def test_mutation_42_high_risk_claims(self):
        r=plan_synthetic(modify(['trusted_claim_ledger', 'high_risk_unresolved'],True));self.assertEqual(r['reason'],'HIGH_RISK_REQUIRES_AUTHORIZATION');safe(r)

if __name__=="__main__":unittest.main()
