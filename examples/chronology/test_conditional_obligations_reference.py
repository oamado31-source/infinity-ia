"""SYNTHETIC-ONLY DEC-109/C tests; no BG2:EE/EEex integration."""
import copy, unittest, json
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from conditional_obligations_reference import plan_synthetic,load_fixture

P=Path(__file__).resolve().parent

def change(path,value):
    f=load_fixture(); p=f
    for key in path[:-1]:p=p[key]
    p[path[-1]]=value
    return f

def add_receipt(f,tid='SYN-TERM-A',amount='4',rid='SYN-RECEIPT-2',aid='SYN-ACTION-2',unit='BOX',fromp='SYN-GUILD-A',top='SYN-GUILD-B'):
    receipt=copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0])
    receipt.update(receipt_id=rid,action_id=aid,term_id=tid,quantity=amount,unit=unit,from_party=fromp,to_party=top)
    f['trusted_receipt_ledger']['receipts'].append(receipt)
    return f

class TestDEC109(unittest.TestCase):
    def safe(self, result):
        self.assertIs(result['dispatch_allowed'],False)
        self.assertIs(result['host_mutation'],False)
        self.assertIs(result['auto_sanction'],False)

    def test_001_baseline_waits_for_full_delivery(self):
        r=plan_synthetic(load_fixture());self.assertEqual(r['status'],'WAITING_DEPENDENCIES');self.assertEqual(r['term_state']['dependencies_satisfied'],0);self.safe(r)

    def test_002_full_delivery_enables_planning_not_execution(self):
        f=add_receipt(load_fixture());r=plan_synthetic(f)
        self.assertEqual(r['status'],'READY_FOR_AUTHORIZED_PLANNING');self.safe(r)

    def test_003_downstream_requires_second_obligation(self):
        f=add_receipt(load_fixture());f['request']['term_id']='SYN-TERM-C';r=plan_synthetic(f)
        self.assertEqual(r['status'],'WAITING_DEPENDENCIES');self.safe(r)

    def test_004_completion_requires_host_receipt_for_target(self):
        f=add_receipt(load_fixture());f=add_receipt(f,'SYN-TERM-B','50','SYN-RECEIPT-B','SYN-ACTION-B','GOLD','SYN-GUILD-B','SYN-GUILD-C')
        f['request']['term_id']='SYN-TERM-B';r=plan_synthetic(f)
        self.assertEqual(r['status'],'COMPLETE_CONFIRMED');self.safe(r)

    def test_005_downstream_eligible_after_second_receipt(self):
        f=add_receipt(load_fixture());f=add_receipt(f,'SYN-TERM-B','50','SYN-RECEIPT-B','SYN-ACTION-B','GOLD','SYN-GUILD-B','SYN-GUILD-C')
        f['request']['term_id']='SYN-TERM-C';r=plan_synthetic(f)
        self.assertEqual(r['status'],'READY_FOR_AUTHORIZED_PLANNING');self.safe(r)

    def test_006_duplicate_identical_receipt_idempotent(self):
        f=load_fixture();f['trusted_receipt_ledger']['receipts'].append(copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0]))
        r=plan_synthetic(f);self.assertEqual(r['status'],'WAITING_DEPENDENCIES');self.safe(r)

    def test_007_schema_validates_fixture(self):
        schema=json.loads((P/'conditional_obligations_v1.candidate.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(load_fixture())

    def test_008_schema_rejects_raw_source(self):
        schema=json.loads((P/'conditional_obligations_v1.candidate.schema.json').read_text())
        with self.assertRaises(ValidationError):Draft202012Validator(schema).validate(change(['source_kind'],'LIVE_GAME'))

    def test_009_order_and_digest_stable(self):
        f=load_fixture(); r=plan_synthetic(f);q=copy.deepcopy(f);q['trusted_term_registry']['terms'].reverse();s=plan_synthetic(q)
        self.assertEqual(r['graph_order'],s['graph_order']);self.assertEqual(r['proposal_key'],s['proposal_key']);self.safe(s)

    def test_010_input_not_mutated(self):
        f=load_fixture();o=copy.deepcopy(f);plan_synthetic(f);self.assertEqual(f,o)

# Dynamic independent unittest methods; all inspect exact outcomes and no mechanical side effects.
# Paths and mutations are synthetic, never actual host operations.
cases=[
 ('source_not_fixture',['source_kind'],'LIVE_HOST','QUARANTINED'),
 ('mode_not_fixture',['context','host_mode'],'LIVE','QUARANTINED'),
 ('fixture_only_false',['context','fixture_only'],False,'QUARANTINED'),
 ('scope_campaign_wrong',['trusted_agreement_registry','campaign_id'],'SYN-OTHER','QUARANTINED'),
 ('scope_branch_wrong',['trusted_term_registry','branch_id'],'SYN-OTHER','QUARANTINED'),
 ('scope_lineage_wrong',['trusted_receipt_ledger','lineage_id'],'SYN-OTHER','QUARANTINED'),
 ('scope_host_epoch_wrong',['trusted_authorization_registry','host_epoch'],99,'QUARANTINED'),
 ('scope_checkpoint_wrong',['trusted_reservation_registry','checkpoint_epoch'],99,'QUARANTINED'),
 ('scope_build_wrong',['trusted_policy','build_fingerprint'],'SYN-OTHER','QUARANTINED'),
 ('scope_modpack_wrong',['trusted_receipt_ledger','modpack_hash'],'SYN-OTHER','QUARANTINED'),
 ('agreement_not_authenticated',['trusted_agreement_registry','authenticated_fixture'],False,'QUARANTINED'),
 ('term_ledger_not_authenticated',['trusted_term_registry','authenticated_fixture'],False,'QUARANTINED'),
 ('receipt_ledger_not_authenticated',['trusted_receipt_ledger','authenticated_fixture'],False,'QUARANTINED'),
 ('authorization_not_authenticated',['trusted_authorization_registry','authenticated_fixture'],False,'QUARANTINED'),
 ('reservation_not_authenticated',['trusted_reservation_registry','authenticated_fixture'],False,'QUARANTINED'),
 ('policy_not_authenticated',['trusted_policy','authenticated_fixture'],False,'QUARANTINED'),
 ('wrong_agreement_request',['request','agreement_id'],'SYN-OTHER','QUARANTINED'),
 ('stale_agreement_revision',['request','expected_agreement_revision'],2,'BLOCKED_STALE'),
 ('stale_policy_revision',['request','policy_revision'],'SYN-OTHER','BLOCKED_STALE'),
 ('draft_agreement',['trusted_agreement_registry','state'],'DRAFT','BLOCKED_AGREEMENT'),
 ('revoked_agreement',['trusted_agreement_registry','state'],'REVOKED','BLOCKED_AGREEMENT'),
 ('agreement_unconsented',['trusted_agreement_registry','consents_confirmed'],False,'BLOCKED_AGREEMENT'),
 ('agreement_mandate_invalid',['trusted_agreement_registry','mandates_valid'],False,'BLOCKED_AGREEMENT'),
 ('agreement_commit_proof_missing',['trusted_agreement_registry','commit_proof_authenticated'],False,'BLOCKED_AGREEMENT'),
 ('insufficient_parties',['trusted_agreement_registry','parties'],['SYN-GUILD-A'],'QUARANTINED'),
 ('duplicate_parties',['trusted_agreement_registry','parties'],['SYN-GUILD-A','SYN-GUILD-A'],'QUARANTINED'),
 ('receipt_inflight',['trusted_receipt_ledger','inflight_actions'],['SYN-PENDING'],'BLOCKED_UNCERTAIN'),
 ('reservation_inflight',['trusted_reservation_registry','inflight_actions'],['SYN-PENDING'],'BLOCKED_UNCERTAIN'),
 ('too_many_terms_policy',['trusted_policy','max_terms'],2,'QUARANTINED'),
 ('unknown_target',['request','term_id'],'SYN-UNKNOWN','UNKNOWN'),
 ('stale_target',['request','expected_term_revision'],2,'BLOCKED_STALE'),
 ('term_agreement_wrong',['trusted_term_registry','terms',1,'agreement_id'],'SYN-OTHER','BLOCKED_AGREEMENT'),
 ('term_revoked',['trusted_term_registry','terms',1,'state'],'REVOKED','BLOCKED_AGREEMENT'),
 ('term_obligor_not_party',['trusted_term_registry','terms',1,'obligor'],'SYN-UNKNOWN','QUARANTINED'),
 ('term_beneficiary_same',['trusted_term_registry','terms',1,'beneficiary'],'SYN-GUILD-B','QUARANTINED'),
 ('term_zero_quantity',['trusted_term_registry','terms',1,'quantity'],'0','QUARANTINED'),
 ('term_negative_quantity',['trusted_term_registry','terms',1,'quantity'],'-1','QUARANTINED'),
 ('term_bad_decimal',['trusted_term_registry','terms',1,'quantity'],'NaN','QUARANTINED'),
 ('unsupported_operator',['trusted_term_registry','terms',1,'gate','operator'],'SCRIPT','QUARANTINED'),
 ('invalid_at_least_min',['trusted_term_registry','terms',1,'gate','minimum'],2,'WAITING_DEPENDENCIES'),
 ('dependency_revision_stale',['trusted_term_registry','terms',1,'gate','dependencies',0,'expected_revision'],2,'BLOCKED_STALE'),
 ('dependency_unknown_kind',['trusted_term_registry','terms',1,'gate','dependencies',0,'kind'],'LLM_SAYS_YES','QUARANTINED'),
 ('receipt_not_authenticated',['trusted_receipt_ledger','receipts',0,'host_authenticated'],False,'QUARANTINED'),
 ('receipt_status_uncertain',['trusted_receipt_ledger','receipts',0,'status'],'UNCERTAIN','QUARANTINED'),
 ('receipt_wrong_scope',['trusted_receipt_ledger','receipts',0,'branch_id'],'SYN-OTHER','QUARANTINED'),
 ('receipt_future_timestamp',['trusted_receipt_ledger','receipts',0,'world_tick'],30,'QUARANTINED'),
 ('receipt_unknown_term',['trusted_receipt_ledger','receipts',0,'term_id'],'SYN-OTHER','QUARANTINED'),
 ('receipt_wrong_agreement',['trusted_receipt_ledger','receipts',0,'agreement_id'],'SYN-OTHER','QUARANTINED'),
 ('receipt_wrong_revision',['trusted_receipt_ledger','receipts',0,'term_revision'],3,'QUARANTINED'),
 ('receipt_wrong_unit',['trusted_receipt_ledger','receipts',0,'unit'],'GOLD','QUARANTINED'),
 ('receipt_wrong_from_party',['trusted_receipt_ledger','receipts',0,'from_party'],'SYN-GUILD-B','QUARANTINED'),
 ('receipt_wrong_to_party',['trusted_receipt_ledger','receipts',0,'to_party'],'SYN-GUILD-C','QUARANTINED'),
 ('receipt_quantity_zero',['trusted_receipt_ledger','receipts',0,'quantity'],'0','QUARANTINED'),
 ('receipt_quantity_negative',['trusted_receipt_ledger','receipts',0,'quantity'],'-1','QUARANTINED'),
 ('receipt_quantity_nan',['trusted_receipt_ledger','receipts',0,'quantity'],'NaN','QUARANTINED'),
 ('receipt_id_empty',['trusted_receipt_ledger','receipts',0,'receipt_id'],'','QUARANTINED'),
 ('action_id_empty',['trusted_receipt_ledger','receipts',0,'action_id'],'','QUARANTINED'),
 ('receipt_exceeds_obligation',['trusted_receipt_ledger','receipts',0,'quantity'],'11','QUARANTINED'),
 ('resource_unavailable',['trusted_reservation_registry','resources_available'],False,'WAITING_DEPENDENCIES'),
 ('grant_removed',['trusted_authorization_registry','term_grants'],[],'WAITING_DEPENDENCIES'),
 ('time_not_reached',['trusted_term_registry','terms',1,'earliest_world_tick'],30,'WAITING_DEPENDENCIES'),
]

def dynamic(name,path,value,expected):
    def test(self):
        r=plan_synthetic(change(path,value));self.assertEqual(r['status'],expected,(name,r));self.safe(r)
    test.__name__='test_dec109_'+name
    return test
for name,path,value,expected in cases:
    setattr(TestDEC109,'test_dec109_'+name,dynamic(name,path,value,expected))

# Cross-field tests requiring more than one mutation.
extra=[
('cycle_detection',lambda f:f['trusted_term_registry']['terms'][0]['gate']['dependencies'].append({'term_id':'SYN-TERM-C','expected_revision':1,'kind':'CONFIRMED_COMPLETE'}),'QUARANTINED'),
('self_cycle',lambda f:f['trusted_term_registry']['terms'][0]['gate']['dependencies'].append({'term_id':'SYN-TERM-A','expected_revision':1,'kind':'CONFIRMED_COMPLETE'}),'QUARANTINED'),
('duplicate_dependency',lambda f:f['trusted_term_registry']['terms'][1]['gate']['dependencies'].append(copy.deepcopy(f['trusted_term_registry']['terms'][1]['gate']['dependencies'][0])),'QUARANTINED'),
('unknown_dependency',lambda f:f['trusted_term_registry']['terms'][1]['gate']['dependencies'][0].update(term_id='SYN-UNKNOWN'),'QUARANTINED'),
('unresolved_partial_threshold',lambda f:(f['trusted_term_registry']['terms'][1]['gate']['dependencies'][0].update(kind='CONFIRMED_AT_LEAST',amount='8')),'WAITING_DEPENDENCIES'),
('satisfied_partial_threshold',lambda f:(f['trusted_term_registry']['terms'][1]['gate']['dependencies'][0].update(kind='CONFIRMED_AT_LEAST',amount='5')),'READY_FOR_AUTHORIZED_PLANNING'),
('bad_partial_threshold',lambda f:(f['trusted_term_registry']['terms'][1]['gate']['dependencies'][0].update(kind='CONFIRMED_AT_LEAST',amount='11')),'QUARANTINED'),
('any_gate_waiting',lambda f:(f['trusted_term_registry']['terms'][1]['gate'].update(operator='ANY')),'WAITING_DEPENDENCIES'),
('invalid_at_least',lambda f:(f['trusted_term_registry']['terms'][1]['gate'].update(operator='AT_LEAST',minimum=2)),'QUARANTINED'),
('at_least_satisfied',lambda f:(f['trusted_term_registry']['terms'][1]['gate'].update(operator='AT_LEAST',minimum=1),add_receipt(f)),'READY_FOR_AUTHORIZED_PLANNING'),
('resource_conflict_after_ready',lambda f:(add_receipt(f),f['trusted_reservation_registry']['conflicting_reservations'].append('SYN-PURSE-1')),'BLOCKED_RESOURCE_CONFLICT'),
('resource_missing_after_ready',lambda f:(add_receipt(f),f['trusted_reservation_registry'].update(resources_available=False)),'BLOCKED_RESOURCE_UNAVAILABLE'),
('grant_missing_after_ready',lambda f:(add_receipt(f),f['trusted_authorization_registry'].update(term_grants=[])),'BLOCKED_AUTHORIZATION'),
('grant_wrong_party',lambda f:(add_receipt(f),f['trusted_authorization_registry']['term_grants'][1].update(party='SYN-GUILD-A')),'BLOCKED_AUTHORIZATION'),
('wait_due_dr_after_ready',lambda f:(add_receipt(f),f['trusted_term_registry']['terms'][1].update(earliest_world_tick=21)),'WAITING_DR_TIME'),
('conflicting_duplicate_receipt_id',lambda f:(f['trusted_receipt_ledger']['receipts'].append({**copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0]),'quantity':'5'})),'QUARANTINED'),
('duplicated_action_distinct_receipt',lambda f:(f['trusted_receipt_ledger']['receipts'].append({**copy.deepcopy(f['trusted_receipt_ledger']['receipts'][0]),'receipt_id':'SYN-OTHER'})),'QUARANTINED'),
('unknown_target_request',lambda f:f['request'].update(term_id='SYN-OTHER'),'UNKNOWN'),
('full_receipt_no_auto_dispatch',lambda f:add_receipt(f),'READY_FOR_AUTHORIZED_PLANNING'),
('term_duplicate_id',lambda f:f['trusted_term_registry']['terms'].append(copy.deepcopy(f['trusted_term_registry']['terms'][0])),'QUARANTINED'),
]
for name,mut,expected in extra:
    def make(mut,expected,name):
        def test(self):
            f=load_fixture();mut(f);r=plan_synthetic(f);self.assertEqual(r['status'],expected,(name,r));self.safe(r)
        return test
    setattr(TestDEC109,'test_dec109_extra_'+name,make(mut,expected,name))

if __name__=='__main__':unittest.main()
