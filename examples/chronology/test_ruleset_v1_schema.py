"""DEC-096: JSON Schema contract shape tests, SYNTHETIC ONLY. Never game-engine tests."""
import json, unittest
from pathlib import Path
from copy import deepcopy
from jsonschema import Draft202012Validator
P=Path(__file__).resolve().parent
SCHEMA=json.loads((P/'ruleset_v1.candidate.schema.json').read_text())
FIXTURE=json.loads((P/'ruleset_v1.synthetic.json').read_text())

class CandidateRuleSetShapeTest(unittest.TestCase):
    def valid(self,obj):
        return not list(Draft202012Validator(SCHEMA).iter_errors(obj))
    def test_schema_valid(self):
        Draft202012Validator.check_schema(SCHEMA)
    def test_fixture_valid(self):
        self.assertTrue(self.valid(FIXTURE))
    def test_no_canon_source(self):
        f=deepcopy(FIXTURE);f['rules'][0]['source_kind']='CANON_CURATED';self.assertFalse(self.valid(f))
    def test_no_production_fixture(self):
        f=deepcopy(FIXTURE);f['fixture_only']=False;self.assertFalse(self.valid(f))
    def test_reject_event_without_canon_ref(self):
        f=deepcopy(FIXTURE);f['rules'][0].pop('canon_event_ref');self.assertFalse(self.valid(f))
    def test_invalid_month(self):
        f=deepcopy(FIXTURE);f['rules'][0]['time']['month_start']=13;self.assertFalse(self.valid(f))
    def test_invalid_day(self):
        f=deepcopy(FIXTURE);f['rules'][0]['time']['day_start']=31;self.assertFalse(self.valid(f))
    def test_unknown_location_type(self):
        f=deepcopy(FIXTURE);f['rules'][0]['scope']['location_tags']=['heaven'];self.assertFalse(self.valid(f))
    def test_unknown_operator(self):
        f=deepcopy(FIXTURE);f['rules'][0]['all_conditions'][0]['op']='EVAL';self.assertFalse(self.valid(f))
    def test_unknown_field(self):
        f=deepcopy(FIXTURE);f['rules'][0]['all_conditions'][0]['field']='npc.private_secret';self.assertFalse(self.valid(f))
    def test_no_script_field(self):
        f=deepcopy(FIXTURE);f['rules'][0]['script']='spawnEnemy()';self.assertFalse(self.valid(f))
    def test_no_negative_cap(self):
        f=deepcopy(FIXTURE);f['rules'][0]['effect']['cap']=-1;self.assertFalse(self.valid(f))
    def test_no_unknown_risk(self):
        f=deepcopy(FIXTURE);f['rules'][0]['effect']['risk']='NONE';self.assertFalse(self.valid(f))
    def test_no_nonlocal_version(self):
        f=deepcopy(FIXTURE);f['ruleset_revision']=0;self.assertFalse(self.valid(f))
    def test_no_nonhash_pin(self):
        f=deepcopy(FIXTURE);f['knowledge_pack_hash']='abc';self.assertFalse(self.valid(f))
    def test_no_branch_policy_override(self):
        f=deepcopy(FIXTURE);f['rules'][0]['branch_policy']='GLOBAL_MUTATE';self.assertFalse(self.valid(f))
    def test_reject_extra_action(self):
        f=deepcopy(FIXTURE);f['rules'][0]['effect']['template']='EXECUTE_HOST';self.assertFalse(self.valid(f))
    def test_reject_type_coercion(self):
        f=deepcopy(FIXTURE);f['rules'][0]['effect']['delta']=1.5;self.assertFalse(self.valid(f))
    def test_reject_extra_event_property(self):
        f=deepcopy(FIXTURE);f['rules'][0]['evil']='arbitrary';self.assertFalse(self.valid(f))
    def test_unique_locations_in_scope(self):
        f=deepcopy(FIXTURE);f['rules'][0]['scope']['location_tags']=['road','road'];self.assertFalse(self.valid(f))

    def test_year_only_cannot_claim_month(self):
        f=deepcopy(FIXTURE);f['rules'][2]['time']['month_start']=1;self.assertFalse(self.valid(f))
    def test_month_precision_requires_month(self):
        f=deepcopy(FIXTURE);f['rules'][0]['time'].pop('month_start');self.assertFalse(self.valid(f))
    def test_exact_day_precision_requires_days(self):
        f=deepcopy(FIXTURE);f['rules'][0]['time']['precision']='EXACT_DAY';self.assertFalse(self.valid(f))

if __name__=='__main__': unittest.main(verbosity=2)
