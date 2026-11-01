"""Synthetic proof fixture for the resume reuse of the two 511-card platform runs."""
import hashlib,importlib.util,json,shutil,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('build094a_public',Path(__file__).with_name('build094a_public.py'))
public=importlib.util.module_from_spec(spec);spec.loader.exec_module(public)
CHECKER=ROOT/'tools/ai/check_all_cards198.cjs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class PlatformProof(unittest.TestCase):
    def setUp(self):
        self.tmp=Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree,self.tmp,ignore_errors=True)
        self.out=self.tmp/'build'
        self.make_proof()

    def make_proof(self,cards=511,records=4088,rare=24,case_ok=True,identity=None,bound=None,checker=None,translated=None):
        root=self.out/'all-card-platforms';root.mkdir(parents=True,exist_ok=True)
        pinned={}
        for platform in ['classic','nextgen']:
            target=root/platform;(target/'sources'/'development').mkdir(parents=True,exist_ok=True)
            prepared=self.out/'scripts'/'game'/'betagwent';prepared.mkdir(parents=True,exist_ok=True)
            source=prepared/(platform+'.ws');source.write_text('prepared source '+platform+'\n','utf8')
            (target/'sources'/'development'/(platform+'.ws')).write_text(translated or 'translated '+platform+'\n','utf8')
            (target/'rules.js').write_text('rules '+platform+'\n','utf8')
            entries={str(source.resolve()):sha(source)}
            payload={p.relative_to(target).as_posix():sha(p) for p in sorted(target.rglob('*')) if p.is_file()}
            digest=identity or hashlib.sha256(json.dumps(entries,sort_keys=True).encode()).hexdigest()
            (target/'manifest.json').write_text(json.dumps({'schema':2,'fingerprint':digest,'snapshotFiles':payload,'platform':platform,'sourceInputs':entries}),'utf8')
            (target/'coverage.json').write_text(json.dumps({'complete':True,'failures':[],'cards':cards,'testedCards':cards,
                'records':[{'ok':case_ok} for _ in range(records)],'rareCases':[{'ok':case_ok} for _ in range(rare)],
                'fingerprint':digest,'nativeGameplayExecuted':False,'actualNativeResultDispatch':True,
                'checkerSha256':checker or sha(CHECKER)}),'utf8')
            pinned[platform]=digest
        (root/'preparation.json').write_text(json.dumps([{'platform':p,'fingerprint':(bound or pinned)[p],'files':1} for p in ['nextgen','classic']]),'utf8')
        return root

    def test_completed_proof_is_reused(self):
        self.assertTrue(public.platform_proof(self.out))

    def test_absent_stage_is_not_reused(self):
        shutil.rmtree(self.out/'all-card-platforms')
        self.assertFalse(public.platform_proof(self.out))

    def test_changed_translation_invalidates(self):
        (self.out/'all-card-platforms'/'classic'/'sources'/'development'/'classic.ws').write_text('tampered\n','utf8')
        self.assertFalse(public.platform_proof(self.out))

    def test_rewritten_translated_payload_invalidates(self):
        (self.out/'all-card-platforms'/'nextgen'/'rules.js').write_text('tampered\n','utf8')
        self.assertFalse(public.platform_proof(self.out))

    def test_prepared_source_drift_invalidates(self):
        (self.out/'scripts'/'game'/'betagwent'/'nextgen.ws').write_text('edited after the run\n','utf8')
        self.assertFalse(public.platform_proof(self.out))

    def test_checker_body_invalidates(self):
        self.make_proof(checker='0'*64);self.assertFalse(public.platform_proof(self.out))

    def test_preparation_fingerprint_mismatch_invalidates(self):
        self.make_proof(bound={'classic':'0'*64,'nextgen':'1'*64});self.assertFalse(public.platform_proof(self.out))

    def test_shrunken_or_failed_coverage_invalidates(self):
        for kwargs in [{'records':4000},{'rare':23},{'case_ok':False},{'cards':510}]:
            self.make_proof(**kwargs);self.assertFalse(public.platform_proof(self.out),str(kwargs))

    def test_missing_coverage_invalidates(self):
        (self.out/'all-card-platforms'/'classic'/'coverage.json').unlink()
        self.assertFalse(public.platform_proof(self.out))

if __name__=='__main__':unittest.main()
