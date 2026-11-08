"""DEC-110/C escrow synthetic-only tests. No game, network, host writes or escrow operations."""
import copy, json, unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from escrow_reference import fixture,plan_synthetic
P=Path(__file__).resolve().parent

def mutate(path,value):
    d=fixture();s=d
    for k in path[:-1]:s=s[k]
    s[path[-1]]=value
    return d
class EscrowReferenceTests(unittest.TestCase):
    def assert_safe(self,r):
        self.assertEqual(r['host_action'],'NONE');self.assertFalse(r['transfer_performed']);self.assertFalse(r['release_performed']);self.assertFalse(r['punishment'])
    def test_baseline_unproven_capability(self):
        r=plan_synthetic(fixture());self.assertEqual(r['status'],'BLOCKED_CAPABILITY');self.assert_safe(r)
    def test_positive_case_is_only_proposal(self):
        f=fixture();c=f['trusted_capability'];c.update(escrow_tested_two_clients=True,transfer_tested=True,query_tested=True,recovery_tested=True)
        r=plan_synthetic(f);self.assertEqual(r['status'],'RELEASE_ELIGIBLE_FOR_REVIEW');self.assert_safe(r)
    def test_request_does_not_mutate_input(self):
        f=fixture();before=copy.deepcopy(f);plan_synthetic(f);self.assertEqual(f,before)
    def test_schema_candidate_fixture(self):
        s=json.loads((P/'escrow_v1.candidate.schema.json').read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(fixture())
    def test_schema_rejects_live_mode(self):
        s=json.loads((P/'escrow_v1.candidate.schema.json').read_text());self.assertTrue(list(Draft202012Validator(s).iter_errors(mutate(['source_kind'],'LIVE_GAME'))))
    def test_no_receipt_not_custody(self):
        f=fixture();f['trusted_capability'].update(escrow_tested_two_clients=True,transfer_tested=True,query_tested=True,recovery_tested=True);f['trusted_host_receipts']['confirmed_deposits']=[]
        r=plan_synthetic(f);self.assertEqual(r['status'],'NOT_MECHANICALLY_HELD');self.assert_safe(r)
    def test_repeated_receipt_quarantined(self):
        f=fixture();f['trusted_capability'].update(escrow_tested_two_clients=True,transfer_tested=True,query_tested=True,recovery_tested=True);f['trusted_host_receipts']['confirmed_deposits'].append(copy.deepcopy(f['trusted_host_receipts']['confirmed_deposits'][0]));r=plan_synthetic(f);self.assertEqual(r['status'],'QUARANTINED');self.assert_safe(r)

# Independently check adverse scenarios with capabilities enabled; never host side effects.
case_list = [('wrong_scope', ['trusted_agreement', 'campaign_id'], 'WRONG', 'QUARANTINED'), ('wrong_branch', ['trusted_host_receipts', 'branch_id'], 'WRONG', 'QUARANTINED'), ('wrong_lineage', ['trusted_ownership', 'lineage_id'], 'WRONG', 'QUARANTINED'), ('wrong_modpack', ['trusted_capability', 'modpack_hash'], 'WRONG', 'QUARANTINED'), ('host_epoch_mismatch', ['trusted_release_rule', 'host_epoch'], 99, 'QUARANTINED'), ('checkpoint_mismatch', ['trusted_authorizations', 'checkpoint_epoch'], 99, 'QUARANTINED'), ('not_authenticated', ['trusted_agreement', 'authenticated_fixture'], False, 'QUARANTINED'), ('missing_requester', ['request', 'requester'], 'WRONG', 'DENIED'), ('wrong_audience', ['request', 'audience'], 'WRONG', 'DENIED'), ('stale_revision', ['request', 'expected_revision'], 999, 'BLOCKED_STALE'), ('uncommitted', ['trusted_agreement', 'state'], 'DRAFT', 'BLOCKED_STALE'), ('depositant_without_consent', ['trusted_authorizations', 'depositant_consented'], False, 'WAITING_CONSENT'), ('release_without_consent', ['trusted_authorizations', 'release_consent_valid'], False, 'WAITING_CONSENT'), ('owner_not_proven', ['trusted_ownership', 'proven_owner'], False, 'BLOCKED_OWNERSHIP'), ('owner_wrong', ['trusted_ownership', 'owner'], 'WRONG', 'BLOCKED_OWNERSHIP'), ('custodian_not_validated', ['trusted_ownership', 'custodian_validated'], False, 'BLOCKED_OWNERSHIP'), ('resource_wrong', ['trusted_ownership', 'asset_id'], 'WRONG', 'BLOCKED_OWNERSHIP'), ('capability_not_transfer', ['trusted_capability', 'transfer_tested'], False, 'BLOCKED_CAPABILITY'), ('capability_not_query', ['trusted_capability', 'query_tested'], False, 'BLOCKED_CAPABILITY'), ('capability_not_recovery', ['trusted_capability', 'recovery_tested'], False, 'BLOCKED_CAPABILITY'), ('capability_not_two_clients', ['trusted_capability', 'escrow_tested_two_clients'], False, 'BLOCKED_CAPABILITY'), ('pending_command', ['trusted_host_receipts', 'dispatched_actions'], ['PENDING'], 'RECONCILE_REQUIRED'), ('uncertain_command', ['trusted_host_receipts', 'uncertain_actions'], ['UNKNOWN'], 'RECONCILE_REQUIRED'), ('contested_agreement', ['trusted_agreement', 'contested'], True, 'CONTESTED_HOLD'), ('contested_rule', ['trusted_release_rule', 'contested'], True, 'CONTESTED_HOLD'), ('incomplete_predicate', ['trusted_release_rule', 'conditions_confirmed'], False, 'WAITING_CONDITIONS'), ('tampered_receipt', ['trusted_host_receipts', 'confirmed_deposits', 0, 'authenticated_fixture'], False, 'QUARANTINED'), ('unconfirmed_receipt', ['trusted_host_receipts', 'confirmed_deposits', 0, 'status'], 'UNCERTAIN', 'QUARANTINED'), ('wrong_receiver', ['trusted_host_receipts', 'confirmed_deposits', 0, 'to_custodian'], 'WRONG', 'QUARANTINED'), ('wrong_from_owner', ['trusted_host_receipts', 'confirmed_deposits', 0, 'from_owner'], 'WRONG', 'QUARANTINED'), ('wrong_amount', ['trusted_host_receipts', 'confirmed_deposits', 0, 'amount'], '-1', 'QUARANTINED'), ('wrong_unit', ['trusted_host_receipts', 'confirmed_deposits', 0, 'unit'], 'BOX', 'QUARANTINED'), ('oversize_deposit', ['trusted_host_receipts', 'confirmed_deposits', 0, 'amount'], '51', 'QUARANTINED')]
for label,path,value,expect in case_list:
    def factory(path=path,value=value,expect=expect):
        def test_case(self):
            d=fixture();d['trusted_capability'].update(escrow_tested_two_clients=True,transfer_tested=True,query_tested=True,recovery_tested=True)
            p=d
            for k in path[:-1]:p=p[k]
            p[path[-1]]=value
            r=plan_synthetic(d);self.assertEqual(r['status'],expect,(path,r));self.assert_safe(r)
        return test_case
    setattr(EscrowReferenceTests,'test_adversarial_'+label,factory())
if __name__=='__main__':unittest.main()
