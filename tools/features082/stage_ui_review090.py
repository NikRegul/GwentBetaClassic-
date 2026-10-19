"""Stage a UI-only revision, reusing byte-identical compiled final2 scripts."""
from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import prepare_final090 as final
SOURCE=ROOT/'BetaGwent/build/release090-final2'
OUT=ROOT/'BetaGwent/build/release090-final3'
UI=ROOT/'BetaGwent/build/release090-ui-review2'
NATIVE=ROOT/'BetaGwent/build/clipboard090-r5'
BANNERS=ROOT/'BetaGwent/build/banners090-native'


def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*.ws')}


def main():
    expected=hashes(SOURCE/'scripts')
    assert hashes(UI/'scripts')==expected,'UI revision must not change gameplay scripts'
    compiled=json.loads((SOURCE/'compile-nextgen-final/result.json').read_text('utf8'))
    assert compiled['exitCode']==0 and compiled['patchSourcesUnchangedDuringCompile']
    assert {r['path']:r['sha256'] for r in compiled['patchSourcesBefore']}==expected
    classic=ROOT/'BetaGwent/build/universal081/classic-runtime/runs/release090-final2-import-unrestricted/result.json'
    result=json.loads(classic.read_text('utf8'))
    assert result['compilePassed'] and not result['errors']
    assert result['preparationManifestSha256']==final.sha(SOURCE/'classic-prepared-final/preparation.json')
    assert not OUT.exists(),'Fresh candidate required'
    OUT.mkdir()
    for name in ['scripts','classic-prepared-final','compile-nextgen-final']:
        shutil.copytree(SOURCE/name,OUT/name)
    for name in ['scripts-changed.json','classic-prepared-diff.json']:
        shutil.copy2(SOURCE/name,OUT/name)
    assert hashes(OUT/'scripts')==expected
    final.stage_phase(OUT,UI,NATIVE,json.loads((OUT/'scripts-changed.json').read_text()),BANNERS)
    (OUT/'compile-reuse.json').write_text(json.dumps(dict(source=str(SOURCE),classicResult=str(classic),
        gameplaySourcesIdentical=True,preparedManifestIdentical=True,inGameVerified=False),indent=2),'utf8')


if __name__=='__main__':main()
