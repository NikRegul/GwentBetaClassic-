"""Positive and negative checks for the narrowly reviewed Choices amendment,
including the 097 reactive-request record, which binds check_bearer097 evidence."""
from pathlib import Path
import json,shutil,sys,unittest,uuid
from profile_provenance094 import amendments

ROOT=Path(__file__).resolve().parents[2]
BUILD=Path(sys.argv.pop(1)).resolve()
PROOF=json.loads((ROOT/'data/beta924/design/beta_ai_profiles093-source-proof.json').read_text('utf8'))
NAME='betaOriginalChoices.ws'
REL=Path('rules/sources/BetaGwent/development/scripts/game/betagwent')/NAME
OUTPUT=ROOT/'BetaGwent/build'/('profile-provenance096-tests-'+uuid.uuid4().hex[:12])

class Provenance(unittest.TestCase):
    def setUp(self):
        self.out=OUTPUT/self._testMethodName;self.out.mkdir(parents=True)
        for relative in [REL,Path('rules/manifest.json'),Path('regressions/audit_whole_requests096.json'),Path('regressions/audit_batch80_requests096.json'),Path('regressions/check_bearer097.json')]:
            target=self.out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BUILD/relative,target)
        self.proof={'wsSources':{NAME:PROOF['wsSources'][NAME]}}
    def result(self):return amendments(self.out,self.proof)
    def change_report(self,name,change):
        p=self.out/'regressions'/(name+'.json');d=json.loads(p.read_text('utf8'));change(d);p.write_text(json.dumps(d),'utf8')
    def test_reviewed_patch_and_both_regressions(self):
        r=self.result();self.assertEqual(len(r),2);self.assertEqual([c['path'] for c in r],[NAME,NAME])
        self.assertEqual(r[0]['step'],'reactions097');self.assertEqual([x['path'] for x in r[0]['regressions']],['regressions/check_bearer097.json'])
        self.assertTrue(r[1]['exactReversePatchMatchesHistoricalSource']);self.assertEqual(len(r[1]['regressions']),2)
    def test_unrelated_source_change_rejected(self):
        p=self.out/REL;p.write_bytes(p.read_bytes()+b'\r\n')
        with self.assertRaisesRegex(AssertionError,'Other Choices edits'):self.result()
    def test_unknown_request_id_rejected(self):
        p=self.out/REL;p.write_bytes(p.read_bytes().replace(b'source==152203',b'source==152204'))
        with self.assertRaisesRegex(AssertionError,'context changed'):self.result()
    def test_wrong_historical_digest_rejected(self):
        self.proof['wsSources'][NAME]='0'*64
        with self.assertRaisesRegex(AssertionError,'Other Choices edits'):self.result()
    def test_wrong_snapshot_rejected(self):
        self.change_report('audit_whole_requests096',lambda d:d.update(fingerprint='other'))
        with self.assertRaises(AssertionError):self.result()
    def test_failed_request_regression_rejected(self):
        self.change_report('audit_batch80_requests096',lambda d:d.update(failures=['broken']))
        with self.assertRaises(AssertionError):self.result()
    def test_missing_card_coverage_rejected(self):
        self.change_report('audit_batch80_requests096',lambda d:d.update(cases=[dict(r,id=122201) for r in d['cases']]))
        with self.assertRaises(AssertionError):self.result()
    def test_missing_seat_coverage_rejected(self):
        self.change_report('audit_whole_requests096',lambda d:d.update(cases=[dict(r,side=1) for r in d['cases']]))
        with self.assertRaises(AssertionError):self.result()

if __name__=='__main__':unittest.main()
