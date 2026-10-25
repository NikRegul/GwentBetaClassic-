"""Build0.9.3c only after independent AI acceptance; preserve verified0.9.3b UI."""
from pathlib import Path
import hashlib,json,sys
from build093 import pipeline

ROOT=Path(__file__).resolve().parents[2]
pipeline.VERSION='0.9.3c';pipeline.LATEST=ROOT/'BetaGwent/build/release093c-latest.json'
proof_path=ROOT/'data/beta924/design/ai093c_validation.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
previous=ROOT/'BetaGwent/build/release093b-lock-ui-20261025-03'
names=['BetaGwentBoard.as','BetaGwentController.as','BetaGwentCardText.as','BetaGwentRelated091.as','BetaGwentBanners090.as']
canonical={n:sha(ROOT/'BetaGwent/ui/src'/n) for n in names}
reuse=None
if (previous/'archive-verification.json').exists() and (previous/'ui-sources/gamepad-source.json').exists():
    source=json.loads((previous/'ui-sources/gamepad-source.json').read_text('utf8'))
    if source==canonical:
        accepted=json.loads((previous/'archive-verification.json').read_text('utf8'));assert accepted['version']=='0.9.3b' and accepted['maxMenuBytes']<=65*1024**2
        patch=json.loads((previous/'ui-patch/manifest.json').read_text('utf8'))
        for platform in patch['platforms'].values():
            for item in platform['files'].values():assert sha(Path(item['path']))==item['sha256']
        reuse=dict(source=str(previous),sourceVersion='0.9.3b',archiveVerificationSha256=sha(previous/'archive-verification.json'),
                   patchManifestSha256=sha(previous/'ui-patch/manifest.json'),canonical=canonical,identicalCurrentSources=True,reusedCompiledMenus=True)
        pipeline.ASSETS=previous;pipeline.UI=previous/'ui-sources'
base_preflight=pipeline.preflight


def accepted_preflight():
    base_preflight()
    assert proof_path.is_file(),'0.9.3c requires the completed accepted holdout; no intermediate release is built'
    proof=json.loads(proof_path.read_text('utf8'));assert proof['accepted'] and proof['version']=='0.9.3c' and proof['holdout']['games']==3680
    assert proof['holdout']['errors']==0 and proof['holdout']['lower99']>.5 and proof['holdout']['clusterLower99']>.5
    sys.path.insert(0,str(ROOT/'tools/ai'));from snapshot import inputs,fingerprint
    assert fingerprint(inputs())==proof['candidateFingerprint'],'AI changed after the accepted holdout'
    from notes093c import write_notes
    write_notes(proof)
    print('Independent0.9.3c AI acceptance found.',flush=True)


pipeline.preflight=accepted_preflight
original_copy=pipeline.copy_assets


def copy_accepted_assets(out,include_ui=True):
    original_copy(out,include_ui)
    if reuse:
        assert include_ui,'Do not silently mix accepted UI with a different explicit source'
        (out/'ui-reuse-proof.json').write_text(json.dumps(reuse,indent=2)+'\n','utf8')


pipeline.copy_assets=copy_accepted_assets
if __name__=='__main__':pipeline.main()
