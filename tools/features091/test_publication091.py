"""Publication must reject unfinished/failed evidence before touching checkout."""
import json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import prepare_github091 as export
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
from validate091 import NAMES

class PublicationChecks(unittest.TestCase):
    def test_incomplete_wrong_snapshot_and_failed_checks_are_rejected(self):
        (ROOT/'BetaGwent/build').mkdir(parents=True,exist_ok=True)
        for kind in ['incomplete','wrong-snapshot','failed-regression']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory(dir=ROOT/'BetaGwent/build') as folder:
                root=Path(folder);public=root/'public';(public/'.git').mkdir(parents=True)
                candidate=root/'candidate';(candidate/'rules').mkdir(parents=True);(candidate/'regressions').mkdir()
                experiment=root/'BetaGwent/build/ai091/final18';experiment.mkdir(parents=True)
                def save(p,v):p.write_text(json.dumps(v),encoding='utf8')
                save(candidate/'release.json',dict(version='0.9.1',archives=[{},{}]))
                save(candidate/'rules/manifest.json',dict(fingerprint='candidate'))
                save(experiment/'summary.json',dict(identity=dict(candidate='wrong' if kind=='wrong-snapshot' else 'candidate'),experiments=dict(versions=dict(complete=kind!='incomplete',errors=0))))
                save(candidate/'regressions/summary.json',[dict(name=n,exitCode=int(kind=='failed-regression')) for n in NAMES])
                before=set(public.rglob('*'))
                with patch.object(export,'ROOT',root),patch.object(export,'PUBLIC',public),patch.object(export.subprocess,'check_output',return_value=b''),patch('evidence091.comparison_compatibility',return_value=dict(comparisonFingerprint='candidate')),patch.object(sys,'argv',['export','--candidate',str(candidate)]):
                    with self.assertRaises(AssertionError):export.main()
                self.assertEqual(before,set(public.rglob('*')))

if __name__=='__main__':unittest.main()
