import unittest
from pathlib import Path
from unittest.mock import patch
import evidence091 as evidence
class EvidenceChecks(unittest.TestCase):
    def test_only_reviewed_bran_slot_can_differ(self):
        key='BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'
        before=b'\xef\xbb\xbffunction BetaGwentDuelPresetCards96(out ids : array<int>) { ids.PushBack(201773); }'
        after=before.replace(b'201773',b'152109')
        old=dict(files={key:'old'},fingerprint='old');new=dict(files={key:'new'},fingerprint='new')
        for actual,ok in [(after,True),(after+b' OtherRuleChanged();',False)]:
            with patch.object(evidence,'validate_snapshot',side_effect=[old,new]),patch.object(Path,'read_bytes',side_effect=[before,actual]):
                if ok:self.assertTrue(evidence.comparison_compatibility(Path('new'),Path('run'))['samePolicy'])
                else:
                    with self.assertRaises(AssertionError):evidence.comparison_compatibility(Path('new'),Path('run'))
        wrong=dict(files={key:'new','policy.ws':'changed'},fingerprint='new')
        with patch.object(evidence,'validate_snapshot',side_effect=[old,wrong]):
            with self.assertRaises(AssertionError):evidence.comparison_compatibility(Path('new'),Path('run'))
if __name__=='__main__':unittest.main()
