"""Check statistical units, independent schedules and checkpoint resilience."""
import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from parallel_tests091 import aggregate, read, atomic

class ParallelChecks(unittest.TestCase):
    def test_paired_blocks_are_units_not_independent_games(self):
        r=aggregate([dict(completedGames=8,wins=6,losses=2,blocks=[1,.5])],8)
        self.assertTrue(r['complete']);self.assertEqual(r['pairedBlocks'],2)
        self.assertEqual(r['scoreRate'],.75)
        self.assertFalse(r['confirmedBetter']) # Wide uncertainty with two deals.

    def test_incomplete_or_errors_cannot_confirm_superiority(self):
        for count,errors in [(396,0),(400,1)]:
            r=aggregate([dict(completedGames=count,wins=count,errors=errors,blocks=[1]*100)],400)
            self.assertFalse(r['confirmedBetter'])

    def test_mirrors_do_not_inflate_deal_diversity(self):
        r=aggregate([dict(games=[dict(left=54,right=61,seed=1),dict(left=61,right=54,seed=1)])],4)
        self.assertEqual(r['matchupPairs'],1);self.assertEqual(r['distinctDeals'],1)

    def test_transient_windows_report_lock_is_retried(self):
        with patch.object(Path,'read_text',side_effect=[PermissionError(),FileNotFoundError(),'{"complete":true}']):
            self.assertEqual(read(Path('unused')),{'complete':True})

    def test_atomic_checkpoint_and_persistent_lock(self):
        root=Path(__file__).resolve().parents[2]/'BetaGwent/build'
        root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as d:
            p=Path(d)/'report.json';atomic(p,{'games':1});atomic(p,{'games':2})
            self.assertEqual(read(p),{'games':2})
        with patch.object(Path,'read_text',side_effect=PermissionError()),patch('parallel_tests091.time.sleep'):
            self.assertIsNone(read(Path('locked')))

if __name__=='__main__':unittest.main()
