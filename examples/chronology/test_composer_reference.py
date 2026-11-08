"""Isolated unit checks for DEC-097 SYNTHETIC composer (NOT game integration)."""
import unittest
from copy import deepcopy
from itertools import permutations
from composer_reference import load_fixture, compose_synthetic


class SyntheticCompositionTest(unittest.TestCase):
    def setUp(self):self.data=load_fixture()
    def run_compose(self):return compose_synthetic(self.data)
    def add(self,eid,**overrides):
        e=deepcopy(self.data['effects'][0]);e.update({'effect_id':eid,'event_id':'SYN-'+eid,
             'rule_id':'SYN-RULE-'+eid,'lineage_root_id':'SYN-'+eid,
             'stack_family':eid,'host_receipt_id':'SYN-RECEIPT-'+eid})
        e.update(overrides);self.data['effects'].append(e);return e

    def test_base_price_125(self):self.assertEqual(self.run_compose()['targets']['food_price'],125)
    def test_no_engine_dispatch(self):self.assertEqual(self.run_compose()['status'],'PROJECTION_ONLY')
    def test_only_synthetic_fixture(self):
        self.data['source_kind']='REAL_CANON'
        with self.assertRaises(ValueError):self.run_compose()
    def test_only_synthetic_context(self):
        self.data['context']['fixture_only']=False
        with self.assertRaises(ValueError):self.run_compose()
    def test_canonical_source_forbidden(self):
        self.data['effects'][0]['source_kind']='CANON'
        with self.assertRaises(ValueError):self.run_compose()
    def test_all_permutations_identical(self):
        first=self.run_compose()
        for items in permutations(self.data['effects']):
            clone=deepcopy(self.data);clone['effects']=list(items)
            self.assertEqual(compose_synthetic(clone),first)
    def test_duplicate_identical_suppressed(self):
        self.data['effects'].append(deepcopy(self.data['effects'][0]))
        self.assertEqual(self.run_compose()['targets']['food_price'],125)
    def test_conflicting_duplicate_rejected(self):
        e=deepcopy(self.data['effects'][0]);e['delta']+=1;self.data['effects'].append(e)
        with self.assertRaises(ValueError):self.run_compose()
    def test_no_receipt_no_effect(self):
        self.data['effects'][0]['host_receipt_id']=None
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_unknown_receipt_not_accepted(self):
        self.data['effects'][0]['host_receipt_id']='REAL-RECEIPT'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_uncertain_not_applied(self):
        self.data['effects'][0]['status']='UNCERTAIN'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_dispatched_not_applied(self):
        self.data['effects'][0]['status']='DISPATCHED'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_proposed_not_applied(self):
        self.data['effects'][0]['status']='PROPOSED'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_rejected_not_applied(self):
        self.data['effects'][0]['status']='REJECTED'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_unauthorized_not_applied(self):
        self.data['effects'][0]['authorized']=False
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_high_risk_blocked(self):
        self.data['effects'][0]['risk']='HIGH'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_wrong_branch_excluded(self):
        self.data['effects'][0]['branch_id']='OTHER'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_wrong_campaign_excluded(self):
        self.data['effects'][0]['campaign_id']='OTHER'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_wrong_epoch_excluded(self):
        self.data['effects'][0]['epoch']=2
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_wrong_knowledge_pack_excluded(self):
        self.data['effects'][0]['pack_hash']='1'*64
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_wrong_scope_excluded(self):
        self.data['effects'][0]['scope_id']='other'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_unknown_metric_rejected(self):
        self.data['effects'][0]['metric_id']='unknown'
        with self.assertRaises(ValueError):self.run_compose()
    def test_unknown_policy_rejected(self):
        self.data['policies'][0]['operator']='LLM_ARBITRATE'
        with self.assertRaises(ValueError):self.run_compose()
    def test_unknown_unit_rejected(self):
        self.data['policies'][0]['unit']='HIT_POINTS'
        with self.assertRaises(ValueError):self.run_compose()
    def test_missing_policy_rejected(self):
        self.data['policies']=[]
        with self.assertRaises(ValueError):self.run_compose()
    def test_invalid_caps_rejected(self):
        self.data['policies'][0]['min']=200
        with self.assertRaises(ValueError):self.run_compose()
    def test_duplicate_policy_rejected(self):
        self.data['policies'].append(deepcopy(self.data['policies'][0]))
        with self.assertRaises(ValueError):self.run_compose()
    def test_future_effect_not_active(self):
        self.data['effects'][0]['world_day_start']=136901
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_hold_stays_full(self):
        self.data['context']['world_day']=136909
        self.assertEqual(self.run_compose()['targets']['food_price'],125)
    def test_mid_fade_at_50pct(self):
        self.data['context']['world_day']=136915
        self.assertEqual(self.run_compose()['targets']['food_price'],112)
    def test_expiration_removes_contributions(self):
        self.data['context']['world_day']=136920
        self.assertEqual(self.run_compose()['targets']['food_price'],100)
    def test_zero_fade_expires_after_hold(self):
        for e in self.data['effects']:e['fade_days']=0
        self.data['context']['world_day']=136910
        self.assertEqual(self.run_compose()['targets']['food_price'],100)
    def test_not_real_clock_dependent(self):
        self.assertEqual(self.run_compose(),self.run_compose())
    def test_cap_upper(self):
        self.add('SYN-LARGE',delta=99000)
        self.assertEqual(self.run_compose()['targets']['food_price'],150)
    def test_cap_lower(self):
        self.add('SYN-NEG',delta=-99000)
        self.assertEqual(self.run_compose()['targets']['food_price'],50)
    def test_absolute_metric(self):
        self.add('SYN-PATROL',metric_id='patrol_intensity',delta=3)
        self.assertEqual(self.run_compose()['targets']['patrol_intensity'],5)
    def test_separate_metric_unchanged(self):
        self.assertEqual(self.run_compose()['targets']['patrol_intensity'],2)
    def test_exclusive_higher_priority(self):
        e=self.add('SYN-COMPETITOR',stack_family='regional-war',delta=500,priority=20)
        self.assertEqual(self.run_compose()['targets']['food_price'],110)
    def test_exclusive_tie_suppresses_family(self):
        self.add('SYN-TIE',stack_family='regional-war',delta=500,priority=10)
        r=self.run_compose();self.assertEqual(r['targets']['food_price'],105)
        self.assertTrue(r['conflicts'])
    def test_tie_order_independent(self):
        self.add('SYN-TIE',stack_family='regional-war',delta=500,priority=10)
        a=self.run_compose(); self.data['effects'].reverse()
        self.assertEqual(a,self.run_compose())
    def test_parent_unknown_excluded(self):
        self.data['effects'][0]['requires_parent_effect_id']='SYN-PARENT'
        self.assertEqual(self.run_compose()['targets']['food_price'],105)
    def test_parent_confirmed_context(self):
        self.data['effects'][0]['requires_parent_effect_id']='SYN-PARENT'
        self.data['context']['confirmed_parent_ids']=['SYN-PARENT']
        self.assertEqual(self.run_compose()['targets']['food_price'],125)
    def test_self_parent_cycle_rejected(self):
        self.data['effects'][0]['requires_parent_effect_id']='SYN-WAR'
        with self.assertRaises(ValueError):self.run_compose()
    def test_two_node_cycle_rejected(self):
        self.data['effects'][0]['requires_parent_effect_id']='SYN-TRANSPORT'
        self.data['effects'][1]['requires_parent_effect_id']='SYN-WAR'
        with self.assertRaises(ValueError):self.run_compose()
    def test_invalid_world_day(self):
        self.data['context']['world_day']=-1
        with self.assertRaises(ValueError):self.run_compose()
    def test_invalid_decay(self):
        self.data['effects'][0]['fade_days']=-1
        with self.assertRaises(ValueError):self.run_compose()
    def test_invalid_delta(self):
        self.data['effects'][0]['delta']=float('nan')
        with self.assertRaises(ValueError):self.run_compose()
    def test_boolean_not_integer_delta(self):
        self.data['effects'][0]['delta']=True
        with self.assertRaises(ValueError):self.run_compose()
    def test_components_have_trace(self):
        r=self.run_compose()
        self.assertEqual(len(r['components']['food_price']),3)
        self.assertEqual(r['included']['food_price'],sorted(r['included']['food_price']))

if __name__=='__main__':unittest.main()
