"""Unit tests for SYNTHETIC filtering only; NOT BG2:EE or EEex integration tests."""
import unittest
from copy import deepcopy
from evaluator_reference import load_synthetic_catalog, proposals


class ChronologyRulesReferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=load_synthetic_catalog()

    def ctx(self, **kwargs):
        o={'fixture_only':True,'pack_pinned':True,'branch_authorized':True,
           'campaign_id':'C-TEST','branch_id':'B-TEST','branch_epoch':1,
           'year_dr':1369,'month':7,'region_id':'region-example','location_tag':'road',
           'confirmed_event_ids':['SYN-PORT-ALERT-1'],
           'conditions':{'regional_alert':True,'canon_divergence':False}}
        o.update(kwargs)
        return o

    def test_valid_fixture_is_not_canon(self):
        self.assertTrue(self.catalog['fixture_only'])
        self.assertTrue(all(e['source_kind']=='SYNTHETIC_TEST' for e in self.catalog['events']))

    def test_month_valid_only_direct_proposal(self):
        v=proposals(self.catalog,self.ctx())
        self.assertEqual(len(v),1)
        self.assertEqual(v[0]['effect_id'],'SYN-PATROL-PLUS-1')
        self.assertEqual(v[0]['kind'],'IMPACT_PROPOSAL_ONLY')

    def test_wrong_year(self):
        self.assertEqual(proposals(self.catalog,self.ctx(year_dr=1368)),[])

    def test_wrong_month(self):
        self.assertEqual(proposals(self.catalog,self.ctx(month=6)),[])

    def test_unknown_month_blocks_activation(self):
        self.assertEqual(proposals(self.catalog,self.ctx(location_tag='tavern',confirmed_event_ids=['SYN-UNSPECIFIED-MONTH'])),[])

    def test_wrong_region(self):
        self.assertEqual(proposals(self.catalog,self.ctx(region_id='other-region')),[])

    def test_wrong_location_type(self):
        self.assertEqual(proposals(self.catalog,self.ctx(location_tag='dungeon')),[])

    def test_unconfirmed_event(self):
        self.assertEqual(proposals(self.catalog,self.ctx(confirmed_event_ids=[])),[])

    def test_missing_pack_pin(self):
        self.assertEqual(proposals(self.catalog,self.ctx(pack_pinned=False)),[])

    def test_branch_not_authorized(self):
        self.assertEqual(proposals(self.catalog,self.ctx(branch_authorized=False)),[])

    def test_failed_condition(self):
        self.assertEqual(proposals(self.catalog,self.ctx(conditions={'regional_alert':False,'canon_divergence':False})),[])

    def test_canon_divergence_blocks(self):
        self.assertEqual(proposals(self.catalog,self.ctx(conditions={'regional_alert':True,'canon_divergence':True})),[])

    def test_indirect_requires_confirmed_parent(self):
        self.assertEqual(len(proposals(self.catalog,self.ctx(),{'SYN-PATROL-PLUS-1'})),2)

    def test_applied_key_dedup(self):
        first=proposals(self.catalog,self.ctx())
        self.assertEqual(proposals(self.catalog,self.ctx(already_applied_keys=[first[0]['dedup_key']])),[])

    def test_retries_are_deterministic(self):
        self.assertEqual(proposals(self.catalog,self.ctx()),proposals(self.catalog,self.ctx()))

    def test_future_event_never_leaks(self):
        self.assertEqual(proposals(self.catalog,self.ctx(year_dr=1369,month=7,confirmed_event_ids=['SYN-FUTURE-1370'])),[])

    def test_reject_nonsynthetic_catalog(self):
        c=deepcopy(self.catalog)
        c['events'][0]['source_kind']='CANON_CURATED'
        with self.assertRaises(ValueError):
            proposals(c,self.ctx())

    def test_reject_non_fixture_context(self):
        with self.assertRaises(ValueError):
            proposals(self.catalog,self.ctx(fixture_only=False))

    def test_reject_unknown_predicate(self):
        c=deepcopy(self.catalog)
        c['events'][0]['conditions']=[{'field':'secret_player_history','op':'EQ','value':True}]
        with self.assertRaises(ValueError):
            proposals(c,self.ctx())

    def test_reject_unknown_operator(self):
        c=deepcopy(self.catalog)
        c['events'][0]['conditions']=[{'field':'regional_alert','op':'EVAL','value':'__import__(...)'}]
        with self.assertRaises(ValueError):
            proposals(c,self.ctx())


if __name__=='__main__':
    unittest.main(verbosity=2)
