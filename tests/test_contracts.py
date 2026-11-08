import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from infinity_ai.contracts import Observation,Status,observe_stub

class ContractTests(unittest.TestCase):
    def test_unknown_is_not_false(self):
        x=observe_stub('host.session_id',campaign_id='test',branch_id='b',host_epoch=0,
                       build_fingerprint='fixture',adapter_version='candidate')
        self.assertEqual(x.status,Status.UNKNOWN)
        self.assertIsNone(x.value)
    def test_forbidden_field_fail_closed(self):
        x=observe_stub('quest.secret_flag',campaign_id='test',branch_id='b',host_epoch=0,
                       build_fingerprint='fixture',adapter_version='candidate')
        self.assertEqual(x.status,Status.BLOCKED_CAPABILITY)
    def test_no_value_when_blocked(self):
        with self.assertRaises(ValueError):
            Observation('c','b',0,'f','a','x',Status.UNKNOWN,'made_up')
    def test_observed_requires_value(self):
        with self.assertRaises(ValueError):
            Observation('c','b',0,'f','a','x',Status.OBSERVED)
    def test_reject_missing_identity(self):
        with self.assertRaises(ValueError):
            Observation('','b',0,'f','a','x',Status.UNKNOWN)
    def test_reject_negative_epoch(self):
        with self.assertRaises(ValueError):
            Observation('c','b',-1,'f','a','x',Status.UNKNOWN)

if __name__=='__main__': unittest.main()
