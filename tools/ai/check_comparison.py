"""Checks for preserving battle rules while replacing AI and validating snapshots."""
import hashlib, json, tempfile, unittest
from pathlib import Path
from comparison_inputs import graft_policy, methods, validate_snapshot

class ComparisonChecks(unittest.TestCase):
    def test_rules_stay_current_and_ai_is_old(self):
        current='''class C {
 public var state : int;
 public function Damage() { state = 42; }
 public function OpponentStep() : bool { return true; }
 private function AiTarget() : int { return 2; }
 private function TargetValue() : int { return 20; }
 }'''
        old=current.replace('state = 42','state = 1').replace('return true','return false').replace('return 2;','return 3;').replace('return 20','return 10')
        merged,copied=graft_policy(current,old)
        self.assertIn('state = 42',merged)
        self.assertNotIn('state = 1;',merged)
        self.assertIn('return false',merged)
        self.assertIn('return 3;',merged)
        self.assertIn('return 10;',merged)
        self.assertEqual(copied,['AiTarget','OpponentStep','TargetValue'])

    def test_comments_strings_nested_braces(self):
        text='class C { public function OpponentStep() { if (true) { Message("}"); } /* { */ } public function Damage() {} }'
        spans=methods(text)
        self.assertEqual(set(spans),{'OpponentStep','Damage'})
        a,b=spans['OpponentStep'];self.assertTrue(text[a:b].endswith('/* { */ }'))

    def test_cooperative_policy_is_old_but_battle_rules_are_current(self):
        current='class C { public function Damage() { NewDamage(); } public function OpponentStep() {} } class CBetaGwentAISequence188 { public function Step() { NewSearch(); } }'
        old=current.replace('NewDamage','OldDamage').replace('NewSearch','OldSearch')
        merged,_=graft_policy(current,old)
        self.assertIn('NewDamage()',merged)
        self.assertIn('OldSearch()',merged)
        self.assertNotIn('NewSearch()',merged)

    def test_missing_old_helper_is_imported(self):
        current='class C { public function OpponentStep() { } }'
        old='class C { public function OpponentStep() { AiRetired(); } private function AiRetired() {} }'
        result,copied=graft_policy(current,old)
        self.assertIn('AiRetired',copied)
        self.assertIn('function AiRetired()',result)

    def test_missing_policy_rejected(self):
        with self.assertRaises(ValueError):graft_policy('class C {}','class C {}')

    def test_tampered_snapshot_rejected(self):
        test_root=Path(__file__).resolve().parents[2]/'BetaGwent/build/comparison-tests'
        test_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=test_root) as folder:
            directory=Path(folder);(directory/'rules.js').write_bytes(b'original')
            manifest={'schema':2,'presets':list(range(46)),'snapshotFiles':{'rules.js':hashlib.sha256(b'original').hexdigest()}}
            (directory/'manifest.json').write_text(json.dumps(manifest),'utf8')
            validate_snapshot(directory)
            (directory/'rules.js').write_bytes(b'changed')
            with self.assertRaises(ValueError):validate_snapshot(directory)

if __name__=='__main__':unittest.main()
