"""DEC-107/C: synthetic-only tests. Not a BG2:EE/EEex/host execution."""
from __future__ import annotations
import unittest,json,copy
from pathlib import Path
import jsonschema
from mediation_reference import plan_synthetic
HERE=Path(__file__).parent
BASE=json.loads((HERE/'mediation_v1.synthetic.json').read_text('utf8'))
SCHEMA=json.loads((HERE/'mediation_v1.candidate.schema.json').read_text('utf8'))
def scenario(path,value):
    item=copy.deepcopy(BASE);d=item
    for key in path[:-1]:d=d[key]
    d[path[-1]]=value
    return item
def safe(r):
    assert r['proposal_only']
    for k in ('host_calls','notices_sent','agreements_signed','compelled_confessions','currency_transferred','reputation_written','quests_modified','beliefs_overwritten','parties_coerced','events_erased'):
        assert r[k]==0,(k,r)

class MediationReferenceTest(unittest.TestCase):
    def test_schema_valid(self):
        jsonschema.Draft202012Validator.check_schema(SCHEMA);jsonschema.validate(BASE,SCHEMA)
    def test_default_right_of_reply(self):
        r=plan_synthetic(BASE);self.assertEqual(r['status'],'PROPOSAL_READY');self.assertEqual(r['proposed_action'],'OFFER_RIGHT_OF_REPLY');safe(r)
    def test_non_mutation(self):
        b=copy.deepcopy(BASE);plan_synthetic(b);self.assertEqual(b,BASE)
    def test_repeat_determinism(self):
        self.assertEqual(plan_synthetic(BASE),plan_synthetic(copy.deepcopy(BASE)))
    def test_trace_irrelevant_to_dedup(self):
        r=plan_synthetic(scenario(['request','trace_ref'],'SYN-OTHER'))
        self.assertEqual(r['proposal_key'],plan_synthetic(BASE)['proposal_key'])
    def test_dedup_pending(self):
        key=plan_synthetic(BASE)['proposal_key']
        r=plan_synthetic(scenario(['trusted_mediation_ledger','pending_keys'],[key]))
        self.assertEqual(r['status'],'ALREADY_PLANNED');safe(r)
    def test_dedup_committed(self):
        key=plan_synthetic(BASE)['proposal_key']
        r=plan_synthetic(scenario(['trusted_mediation_ledger','committed_keys'],[key]))
        self.assertEqual(r['status'],'ALREADY_REGISTERED');safe(r)
    def test_notice_not_sent(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','state'],'NOT_SENT'))['proposed_action'],'PROPOSE_SCOPED_NOTICE')
    def test_notice_draft(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','state'],'DRAFT'))['proposed_action'],'PROPOSE_SCOPED_NOTICE')
    def test_notice_lost(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','state'],'LOST'))['proposed_action'],'PROPOSE_SCOPED_NOTICE')
    def test_notice_in_transit(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','state'],'IN_TRANSIT'))['proposed_action'],'WAIT_NOTICE_DELIVERY')
    def test_notice_unperceived(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','perceived'],False))['proposed_action'],'WAIT_NOTICE_PERCEPTION')
    def test_reply_unknown(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','reply_status'],'UNKNOWN'))['proposed_action'],'REQUEST_REPLY_STATUS_EVIDENCE')
    def test_reply_deadline_passed_no_sanction(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','reply_deadline_tick'],44))['proposed_action'],'PROPOSE_REPLY_EXTENSION')
    def test_reply_declined_not_guilt(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','reply_status'],'DECLINED'))['proposed_action'],'RESPECT_REFUSAL_NO_PENALTY')
    def test_reply_filed_consents_pending(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','reply_status'],'FILED'))['proposed_action'],'WAIT_VOLUNTARY_CONSENT')
    def test_reply_filed_one_declines(self):
        f=scenario(['trusted_notice_ledger','reply_status'],'FILED')
        f['trusted_party_registry']['parties']['SYN-ORG-A']['mediation_consent']='DECLINED'
        self.assertEqual(plan_synthetic(f)['proposed_action'],'RESPECT_REFUSAL_NO_PENALTY')
    def test_reply_filed_withdrawn(self):
        f=scenario(['trusted_notice_ledger','reply_status'],'FILED')
        f['trusted_party_registry']['parties']['SYN-ORG-A']['mediation_consent']='WITHDRAWN'
        self.assertEqual(plan_synthetic(f)['proposed_action'],'RESPECT_REFUSAL_NO_PENALTY')
    def test_reply_filed_both_consent(self):
        f=scenario(['trusted_notice_ledger','reply_status'],'FILED')
        for x in f['trusted_party_registry']['parties'].values():x['mediation_consent']='GRANTED'
        r=plan_synthetic(f);self.assertEqual(r['proposed_action'],'PROPOSE_MEDIATION_SESSION');safe(r)
    def test_conflicted_facilitator(self):
        f=scenario(['trusted_notice_ledger','reply_status'],'FILED')
        for x in f['trusted_party_registry']['parties'].values():x['mediation_consent']='GRANTED'
        f['trusted_facilitator_registry']['status']='CONFLICT'
        self.assertEqual(plan_synthetic(f)['proposed_action'],'REVIEW_FACILITATOR_CONFLICT')
    def test_facilitator_false_conflict_flag(self):
        f=scenario(['trusted_notice_ledger','reply_status'],'FILED')
        for x in f['trusted_party_registry']['parties'].values():x['mediation_consent']='GRANTED'
        f['trusted_facilitator_registry']['conflict_of_interest']=True
        self.assertEqual(plan_synthetic(f)['proposed_action'],'REVIEW_FACILITATOR_CONFLICT')
    def test_pc_owner_check(self):
        f=scenario(['trusted_party_registry','parties','SYN-ORG-A','kind'],'PC')
        self.assertEqual(plan_synthetic(f)['reason'],'PC_OWNER_AUTHORIZATION_REQUIRED')
    def test_pc_owner_attestation_only_narrowly_allows(self):
        f=scenario(['trusted_party_registry','parties','SYN-ORG-A','kind'],'PC')
        f['trusted_party_registry']['parties']['SYN-ORG-A']['pc_owner_attested']=True
        r=plan_synthetic(f);self.assertEqual(r['proposed_action'],'OFFER_RIGHT_OF_REPLY');safe(r)
    def test_public_restricted_proof_blocked(self):
        f=scenario(['request','audience'],'PUBLIC');f['trusted_case_registry']['allowed_audiences']=['PARTIES','PUBLIC']
        self.assertEqual(plan_synthetic(f)['reason'],'PUBLIC_DISCLOSURE_WITH_PROTECTED_EVIDENCE')
    def test_public_with_public_evidence_and_policy(self):
        f=scenario(['request','audience'],'PUBLIC')
        f['trusted_case_registry']['allowed_audiences']=['PUBLIC','PARTIES']
        f['trusted_evidence_ledger']['classification']='PUBLIC'
        f['trusted_evidence_ledger']['allowed_audiences']=['PARTIES','PUBLIC']
        self.assertEqual(plan_synthetic(f)['proposed_action'],'OFFER_RIGHT_OF_REPLY')
    def test_self_grant_schema_denied(self):
        f=scenario(['request','trace_ref'],'SYN-OK');f['request']['grant_access']=True
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(f,SCHEMA)
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_self_declared_truth_denied(self):
        f=copy.deepcopy(BASE);f['request']['case_is_true']=True
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_self_declared_consent_denied(self):
        f=copy.deepcopy(BASE);f['request']['both_parties_consent']=True
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_fixture_not_host(self):
        f=scenario(['context','host_mode'],'BG2EE_LIVE')
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(f,SCHEMA)
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_case_other_revision(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_case_registry','case_revision'],6))['reason'],'CASE_REVISION_CHANGED')
    def test_wrong_representative(self):
        self.assertEqual(plan_synthetic(scenario(['context','authenticated_principal'],'SYN-REP-A'))['reason'],'REQUESTER_NOT_AUTHORIZED_REPRESENTATIVE')
    def test_uncertain_reconcile(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_notice_ledger','state'],'UNCERTAIN'))['status'],'QUARANTINED')
    def test_ledger_dispatched_reconcile(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_mediation_ledger','dispatched'],True))['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION')
    def test_ledger_uncertain_reconcile(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_mediation_ledger','uncertain'],True))['reason'],'UNCERTAIN_OPERATION_REQUIRES_RECONCILIATION')
    def test_missing_trusted_registry(self):
        f=copy.deepcopy(BASE);del f['trusted_party_registry']
        self.assertEqual(plan_synthetic(f)['status'],'QUARANTINED')
    def test_invalid_evidence_status(self):
        self.assertEqual(plan_synthetic(scenario(['trusted_evidence_ledger','status'],'FAKE_TRUTH'))['reason'],'EVIDENCE_UNVERIFIED_OR_UNLINKED')
    def test_confidential_evidence_never_public_in_default(self):
        r=plan_synthetic(BASE)
        self.assertNotIn('evidence_payload',r)
        self.assertNotIn('witness_identity',r)
        safe(r)
    def test_no_oracle_or_verdict(self):
        r=plan_synthetic(BASE)
        self.assertEqual(r['dispute_resolution'],'NOT_ADJUDICATED')

# Non-identical adverse mutations, all must be contained without host operations.
_MUTATIONS=[
 (['source_kind'],'REAL_GAME','NOT_SYNTHETIC_FIXTURE'),
 (['context','fixture_only'],False,'INVALID_CONTEXT_OR_REQUEST'),
 (['context','host_epoch'],-1,'INVALID_CONTEXT_OR_REQUEST'),
 (['context','checkpoint_epoch'],-1,'INVALID_CONTEXT_OR_REQUEST'),
 (['context','campaign_id'],'REAL-CAMP','INVALID_CONTEXT_OR_REQUEST'),
 (['context','world_tick'],-2,'INVALID_CONTEXT_OR_REQUEST'),
 (['context','clock_mode'],'WALLCLOCK','INVALID_CONTEXT_OR_REQUEST'),
 (['context','authenticated_principal'],'SYN-UNTRUSTED','PRINCIPAL_NOT_AUTHORIZED'),
 (['request','expected_revision'],9,'STALE_LEDGER_REVISION'),
 (['request','party_ref'],'SYN-STRANGER','CASE_OR_PARTY_NOT_FOUND'),
 (['request','case_ref'],'SYN-NOT-FOUND','CASE_OR_PARTY_NOT_FOUND'),
 (['request','purpose'],'FORCE_CONFESSION','PURPOSE_OR_AUDIENCE_NOT_ALLOWED'),
 (['request','audience'],'EVERYONE','PURPOSE_OR_AUDIENCE_NOT_ALLOWED'),
 (['trusted_case_registry','campaign_id'],'SYN-OTHER','CROSS_SCOPE_OR_STALE_EPOCH'),
 (['trusted_party_registry','branch_id'],'SYN-OTHER','CROSS_SCOPE_OR_STALE_EPOCH'),
 (['trusted_evidence_ledger','lineage_id'],'SYN-OTHER','CROSS_SCOPE_OR_STALE_EPOCH'),
 (['trusted_notice_ledger','host_epoch'],4,'CROSS_SCOPE_OR_STALE_EPOCH'),
 (['trusted_facilitator_registry','checkpoint_epoch'],4,'CROSS_SCOPE_OR_STALE_EPOCH'),
 (['trusted_mediation_ledger','modpack_hash'],'SYN-OTHER','CROSS_SCOPE_OR_STALE_EPOCH'),
 (['trusted_policy','revision'],'UNPINNED','POLICY_NOT_PINNED'),
 (['trusted_case_registry','status'],'CLOSED','CASE_NOT_OPEN'),
 (['trusted_case_registry','high_risk_unresolved'],True,'HIGH_RISK_GATE_UNRESOLVED'),
 (['trusted_evidence_ledger','high_risk_unresolved'],True,'HIGH_RISK_GATE_UNRESOLVED'),
 (['trusted_case_registry','purpose'],'UNRELATED','CASE_SCOPE_NOT_ALLOWED'),
 (['trusted_case_registry','party_ids'],['SYN-ORG-A','SYN-ORG-A'],'INVALID_PARTY_MEMBERSHIP'),
 (['trusted_party_registry','parties','SYN-ORG-A','owner_attested'],False,'PARTY_AUTHORITY_NOT_VERIFIED'),
 (['trusted_party_registry','parties','SYN-ORG-B','mandate'],'REVOKED','PARTY_AUTHORITY_NOT_VERIFIED'),
 (['trusted_party_registry','parties','SYN-ORG-B','kind'],'UNKNOWN','INVALID_PARTY_KIND'),
 (['trusted_evidence_ledger','case_id'],'SYN-OTHER','EVIDENCE_UNVERIFIED_OR_UNLINKED'),
 (['trusted_evidence_ledger','claim_refs'],[],'MISSING_CLAIM_PROVENANCE'),
 (['trusted_evidence_ledger','classification'],'TOP_SECRET_UNMODELED','INVALID_EVIDENCE_CLASSIFICATION'),
 (['trusted_evidence_ledger','allowed_audiences'],[],'EVIDENCE_ACL_DENIED'),
 (['trusted_notice_ledger','case_id'],'SYN-OTHER','NOTICE_CASE_MISMATCH'),
 (['trusted_notice_ledger','state'],'FABRICATED','INVALID_NOTICE_STATE'),
 (['trusted_notice_ledger','delivery_tick'],500,'INVALID_NOTICE_TIMESTAMP'),
 (['trusted_notice_ledger','reply_status'],'CONFESSION_IMPLIED','INVALID_REPLY_STATUS'),
 (['trusted_facilitator_registry','status'],'MISSING','FACILITATOR_RECORD_UNAVAILABLE'),
 (['trusted_mediation_ledger','pending'],'INDETERMINATE','INVALID_PENDING_LEDGER'),
]
for ix,(path,value,reason) in enumerate(_MUTATIONS,1):
    def make_test(path=path,value=value,reason=reason):
        def test(self):
            r=plan_synthetic(scenario(path,value))
            self.assertEqual(r['reason'],reason,(path,r));safe(r)
        return test
    setattr(MediationReferenceTest,'test_adversarial_%02d'%ix,make_test())
if __name__=='__main__':unittest.main()
