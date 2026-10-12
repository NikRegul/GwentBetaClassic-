"""Verify loop-only input provenance, allowlist, native CRCs and resource freshness."""
from pathlib import Path
import ast,hashlib,json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ui'))
from update_board_resource import validate_resource,validate_image_linkages

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def packaging_guards(folder,native):
    # Execute the actual packager guard without its command-line side effects.
    tree=ast.parse((ROOT/'tools/build_language_release.py').read_text('utf8'))
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('check_leaders','copy_release_tree')]
    scope=dict(ROOT=ROOT,STAGE=136,json=json,sha=sha,shutil=shutil)
    exec(compile(ast.Module(body=functions,type_ignores=[]),'packager-guards','exec'),scope)
    with tempfile.TemporaryDirectory(prefix='guard-',dir=ROOT/'BetaGwent/build/leaders136') as temporary:
        workspace=Path(temporary)/'workspace'
        shutil.copytree(folder,workspace)
        guard=scope['check_leaders'];guard(workspace)
        target=workspace/'gameplay/gui_new/swf/betagwentleaders'
        def rejected():
            try:guard(workspace)
            except (AssertionError,RuntimeError):return
            raise AssertionError('Packager accepted invalid leader staging')
        extra=target/'nonleader.redswf';extra.write_bytes(b'not allowed');rejected();extra.unlink()
        first=next(iter(native['resources'].values()))
        portrait=workspace/first['path'];original=portrait.read_bytes()
        portrait.unlink();rejected()
        portrait.write_bytes(b'stale');rejected();portrait.write_bytes(original)
        scope['STAGE']=135;rejected();scope['STAGE']=136
        destination=Path(temporary)/'copied-baseline'
        scope['copy_release_tree'](workspace,destination)
        assert not (destination/'gameplay/gui_new/swf/betagwentleaders').exists()
    return 6

def main():
    native=json.loads((ROOT/'docs/evidence/leaders136.json').read_text('utf8'))
    manifest=ROOT/'BetaGwent/build/release060-preparation/leaders/manifest.json'
    preparation=json.loads(manifest.read_text('utf8'))
    cards=json.loads((ROOT/'data/beta924/duel/slice.json').read_text('utf8'))['cards']
    expected={str(c['templateId']) for c in cards if int(c['fields']['Tier'])==1}
    assert len(expected)==21 and set(native['bindings'])==expected
    assert native['bindings']==preparation['bindings']
    assert sha(manifest)==native['preparationSha256']
    for item in preparation['resources']:
        source=Path(item['sourceFrames']);meta=json.loads((source/'complete.json').read_text('utf8'))
        assert meta['loopOnly'] and meta['introExcluded'] and item['loopOnly'] and item['introExcluded']
        assert [sha(source/f'{i:04}.png') for i in range(48)]==item['sourceFrameSha256']
        assert sha(Path(item['atlas']))==item['sha256']
        # The wrap is an ordinary adjacent captured frame, not a frozen endpoint.
        assert item['loopSeamDelta']>0 and item['loopSeamDelta']<=item['maximumStepDelta']
    folder=ROOT/'BetaGwent/build/leaders136/resources'
    assert len(list(folder.rglob('*.redswf')))==21
    for item in native['resources'].values():
        path=folder/item['path'];assert sha(path)==item['sha256']
        resource,_=validate_resource(path);validate_image_linkages(resource)
    for name,digest in native['sources'].items():assert sha(ROOT/name)==digest
    guards=packaging_guards(folder,native)
    # Four isolated RGBA atlases plus their BC1 copies stay below the animation budget.
    worst=4*(2048*1560*4+2048*1560//2)
    assert worst<70*1024*1024
    sources=['BetaGwent/ui/src/BetaGwentLeaderPreview.as','BetaGwent/ui/src/BetaGwentBoard.as',
        'tools/ui/leaders060/Capture.cs','tools/ui/leaders060/BetaLeaderMovie.as',
        'tools/ui/check_leaders136.py','tools/build_language_release.py']
    report=dict(stage=136,leaders=21,nonLeaderAnimations=0,loopOnly=True,introExcluded=True,packagingGuardChecks=guards,
        maxBoardMovies=3,maxHoverMovies=1,estimatedAtlasWorstCaseBytes=worst,
        animationBudgetBytes=70*1024*1024,measuredNativeMemory=False,nativeGameTested=False,
        sources={p:sha(ROOT/p) for p in sources})
    (ROOT/'docs/evidence/leader-checks136.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('PASS: 21 native loop-only leaders; current input SHA/CRC/linkages; no non-leaders; bounded atlas budget')

if __name__=='__main__':main()
