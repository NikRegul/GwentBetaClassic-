"""Freeze and verify the UI/audio inputs of a post-audit 0.9.5 build.

Card data and engine sources are deliberately left to the existing rules freeze.
No compiler, packaging or installation is started by this module.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
NOTES=ROOT/'docs/releases/0.9.5-public-20261101-feedback101-ai'
# Includes screenshot measurements, long lists, scaled pointer dragging and focus scrolling.
UI_REPORTS={'windows':327,'preview-keywords':2707,'battle-cleanup':19,'pad-legend':23,'target-cancel':30,'feedback099':20,'presentation100':15,'side-keywords':19}
CONTRACT='ui-release-inputs.json'
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text('utf8'))
def inputs():
    from build_inputs import AUDIO,NEXTGEN_AUDIO
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('ui095_preparer',ROOT/'tools/features091/prepare_ui091.py');m=module_from_spec(spec);spec.loader.exec_module(m)
    # Audited card descriptions, related-card tables and choice captions can advance.
    shared={'BetaGwentCardText.as','BetaGwentRelated091.as','BetaGwentReleaseText093.as'}
    files=[ROOT/'BetaGwent/ui/src'/n for n in m.NAMES if n not in shared]
    files+=[ROOT/'tools/features091/BetaGwentBoard_classic093.as',ROOT/'data/beta924/design/editor_vfx094.json',ROOT/'BetaGwent/ui/assets/editor094/append-bc3.bin',ROOT/'BetaGwent/ui/assets/elements164/Elements.png']
    files+=[ROOT/'data/beta924/design/window_art098.json',ROOT/'BetaGwent/ui/assets/battle104/deckscreens104.png',ROOT/'BetaGwent/ui/assets/windows098/blocks.bin']
    audio={}
    for platform,folder in [('classic',AUDIO),('nextgen',NEXTGEN_AUDIO)]:
        expected=ROOT/'BetaGwent/build-inputs'/(platform+'-audio095-windows')
        assert folder.resolve()==expected.resolve(),'0.9.5 requires the accepted UI-window sound cache: '+str(expected)
        manifest=read(folder/'manifest.json');cache=folder/'soundspc.cache'
        digest=sha(cache);published=manifest['cache']['sha256']if platform=='classic'else manifest['sha256']
        assert digest==published,'Audio cache differs from manifest: '+str(cache)
        assert (manifest['stage096']['events']if platform=='classic'else manifest['events'])==48
        audio[platform]={'directory':str(folder.relative_to(ROOT)),'cacheSha256':digest,'manifestSha256':sha(folder/'manifest.json')}
    return {'schema':1,'version':'0.9.5','uiSources':{p.relative_to(ROOT).as_posix():sha(p)for p in files},
        'audioSourceSha256':sha(ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudio.ws'),'audio':audio,
        'rulesFrozenHere':False,'nativeGameTested':False,'allBetaAnimationsPorted':False}
def freeze(out):
    out=Path(out);record=inputs();target=out/CONTRACT
    if target.exists():assert read(target)==record,'UI/audio inputs changed; use a new release output'
    else:target.write_text(json.dumps(record,indent=2)+'\n','utf8')
    return record
def validate_frozen(out):
    out=Path(out);saved=read(out/CONTRACT)
    assert saved==inputs(),'UI/audio changed since this build was frozen; create a fresh build'
    assert sha(out/'scripts/game/betagwent/duelAudio.ws')==saved['audioSourceSha256'],'Prepared UI audio differs from selected source'
    return saved
def reports(out,ui):
    out,ui=Path(out),Path(ui);saved=validate_frozen(out);files=[CONTRACT]
    for platform in ['classic','nextgen']:
        board=ui/platform/'ui/src/BetaGwentBoard.as'
        expected=sha(board)
        canonical='tools/features091/BetaGwentBoard_classic093.as'if platform=='classic'else 'BetaGwent/ui/src/BetaGwentBoard.as'
        assert expected==saved['uiSources'][canonical]
        for prefix,count in UI_REPORTS.items():
            name=prefix+'-'+platform+'.json';r=read(out/name)
            assert r['checks']==count and not r['failures'] and r['actualActionScript'],name
            assert r['sourceSha256']==expected,'Report used a different Board: '+name
            assert not r['nativeGameTested'],name
            files.append(name)
    name='window-audio-check.json';r=read(out/name)
    assert r['checks']==97 and not r['failures'] and r['actualWitcherScript']
    assert r['sourceSha256']==saved['audioSourceSha256'] and not r['audibleGameVerified']
    files.append(name)
    name='outcome-faction-check.json';r=read(out/name)
    assert r['checks']==62 and not r['failures'] and r['actualActionScript'] and r['actualWitcherScript'] and not r['nativeGameTested']
    assert r['menuSourceSha256']==sha(out/'scripts/game/betagwent/developmentBoardMenu.ws')
    assert {v['source']:v['sha256'] for v in r['records']}=={n:saved['uiSources'][n] for n in ['BetaGwent/ui/src/BetaGwentBoard.as','tools/features091/BetaGwentBoard_classic093.as']}
    files.append(name)
    return files
def verify_archive_audio(archive,platform,mod,saved):
    """Stream the actual archive member so a stale packaged cache cannot pass."""
    with archive.open('Mods/'+mod+'/content/soundspc.cache')as f:
        assert hashlib.file_digest(f,'sha256').hexdigest()==saved['audio'][platform]['cacheSha256'],'Packaged UI sound cache is stale'
