"""Verify dynamic callback counts without losing fixed historical case coverage."""
from pathlib import Path
import copy,json,sys,unittest
from verify093 import verify_current_targeted_plans

BUILD=Path(sys.argv.pop(1)).resolve()
NAMES=['check_reply_pass094','check_exhausted_frontier094','check_draw_frontier094',
       'check_chase_budget093a','check_lock_resilience093b','check_plans093c','check_four_card093c']
def load(build):
    reports={n:json.loads((build/'regressions'/(n+'.json')).read_text('utf8')) for n in NAMES}
    return {n:r['checks'] for n,r in reports.items()},reports['check_plans093c']

class Coverage(unittest.TestCase):
    def setUp(self):self.counts,self.plans=copy.deepcopy(load(BUILD))
    def verify(self):verify_current_targeted_plans(self.counts,self.plans)
    def test_current_report(self):self.verify()
    def test_historical_report(self):
        self.counts,self.plans=load(BUILD.parent/'release095-20261027-final01');self.verify()
    def test_different_callback_count(self):
        self.counts['check_plans093c']+=2;self.plans['checks']+=2;self.verify()
    def test_fixed_count_change_rejected(self):
        self.counts['check_reply_pass094']-=1
        with self.assertRaises(AssertionError):self.verify()
    def test_missing_case_rejected(self):
        self.plans['cases'].pop()
        with self.assertRaises(AssertionError):self.verify()
    def test_duplicate_case_rejected(self):
        self.plans['cases'][0]=copy.deepcopy(self.plans['cases'][1])
        with self.assertRaises(AssertionError):self.verify()
    def test_unplayed_spy_rejected(self):
        self.plans['cases'][0]['played']=False
        with self.assertRaises(AssertionError):self.verify()
    def test_lost_hand_rejected(self):
        self.plans['cases'][0]['hand']=3
        with self.assertRaises(AssertionError):self.verify()
    def test_missing_continuation_rejected(self):
        self.plans['cases'][-1]['sequence']=[]
        with self.assertRaises(AssertionError):self.verify()
    def test_useless_continuation_rejected(self):
        self.plans['cases'][-1]['after']=self.plans['cases'][-1]['before']
        with self.assertRaises(AssertionError):self.verify()
    def test_failed_assertion_rejected(self):
        self.plans['failures']=['failed']
        with self.assertRaises(AssertionError):self.verify()
    def test_missing_historical_proof_rejected(self):
        self.plans['actualHistoricalFixtures']=False
        with self.assertRaises(AssertionError):self.verify()

if __name__=='__main__':unittest.main()
