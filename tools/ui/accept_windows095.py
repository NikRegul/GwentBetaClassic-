"""Verify one isolated UI-window candidate; never build a release or install it."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,re
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/features096'),str(ROOT/'tools/features091')]
import patch_audio096 as audio
from classic_audio091 import patch as classic_audio
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--sources',default='ui-sources08');p.add_argument('--patch',default='ui-patch08');a=p.parse_args()
    suffix=re.search(r'\d+$',a.sources)[0]
    out=a.candidate.resolve();sources=out/a.sources;logs=out/('checks'+suffix);logs.mkdir(exist_ok=True)
    results=[]
    def run(name,args):
        dest=logs/(name+'.log');r=subprocess.run(list(map(str,args)),cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        dest.write_bytes(r.stdout);results.append({'name':name,'exitCode':r.returncode,'log':str(dest.relative_to(out))})
        if r.returncode:raise RuntimeError(name+'\n'+r.stdout.decode('utf8',errors='replace')[-3500:])
    source_proof={}
    prior=(ROOT/'BetaGwent/build/ui095-review-20261028-01/ui-sources03/nextgen/ui/src/BetaGwentUiText096.as').read_text('utf-8-sig')
    prior_maps=json.loads(re.search(r'BY:Array=(.*);',prior)[1])
    for key in ['classic','nextgen']:
        ui=sources/key/'ui';board=ui/'src/BetaGwentBoard.as'
        manifest=json.loads((sources/key/'ui-inputs.json').read_text('utf8'))
        assert all(sha(ui/'src'/n)==h for n,h in manifest['sources'].items())
        copies=[ui/c/'BetaGwentBoard.as' for c in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']]
        assert len({sha(f) for f in copies})==1
        for f in copies:
            raw=f.read_bytes();assert raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'')
        canonical=ROOT/('tools/features091/BetaGwentBoard_classic093.as' if key=='classic' else 'BetaGwent/ui/src/BetaGwentBoard.as')
        assert sha(board)==sha(canonical)
        current_maps=json.loads(re.search(r'BY:Array=(.*);',(ui/'src/BetaGwentUiText096.as').read_text('utf-8-sig'))[1])
        assert all(all(n in after and after[n]==v for n,v in before.items())for before,after in zip(prior_maps,current_maps)),'Accepted translations changed'
        menus=json.loads((sources/key/'menus/menus.json').read_text('utf8'))
        assert menus['frozenSources']==manifest['sources'] and len(menus['menus'])==4
        for m in menus['menus']:
            assert sha(Path(m['path']))==m['sha256'] and sha(Path(m['path']).with_suffix('.swf'))==m['sourceSha256']
        source_proof[key]={'menus':4,'boardSha256':sha(board),'allFrozenSourcesMatched':True}
        for test in ['check_windows095','check_preview_keywords095','check_battle_cleanup095','check_pad_legend096','check_controller_aim094','check_editor_stats094a','check_editor_followup094']:
            run(test+'-'+key,['node',ROOT/'tools/ui'/(test+'.cjs'),board,logs/(test+'-'+key+'.json')])
        for test in ['check_pass_coin096','check_editor_valid095']:
            run(test+'-'+key,['node',ROOT/'tools/ui'/(test+'.cjs'),ui/'src',logs/(test+'-'+key+'.json')])
        for test in ['check_editor_fx094','check_editor_slot096']:
            run(test+'-'+key,['node',ROOT/'tools/ui'/(test+'.cjs'),board,ui/'editor_vfx094.json',logs/(test+'-'+key+'.json')])
    run('gamepad',['node',ROOT/'tools/features091/check_gamepad091.js',sources,logs/'gamepad.json'])
    run('related',['node',ROOT/'tools/features091/check_related091.js',sources])
    run('choice-captions',['node',ROOT/'tools/ai/check_choice_captions093.cjs',logs/'choice-captions.json'])
    run('window-audio',['node',ROOT/'tools/ui/check_window_audio095.cjs',ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudio.ws',logs/'window-audio.json'])
    run('layout',[sys.executable,'-X','utf8',ROOT/'tools/recon/check_project_layout.py','--sources-only'])
    patch=json.loads((out/a.patch/'manifest.json').read_text('utf8'));sizes={}
    for key,platform in patch['platforms'].items():
        for v in platform['files'].values():assert sha(Path(v['path']))==v['sha256']
        sizes[key]=max(m['bytes']for m in platform['menus']);assert sizes[key]<65*1024**2
    # Parse actual cached banks, not only their import report.
    audio.SOURCE_REPORT=out/'audio-import.json';names=audio.event_names();bankproof=[]
    cache=ROOT/'BetaGwent/build-inputs/nextgen-audio095-windows/soundspc.cache'
    _,index=audio.sound_index(cache);offset,size=index['betagwent79.bnk']
    with cache.open('rb')as f:f.seek(offset);raw=f.read(size)
    banks=[('nextgen',raw,False)]
    for f in sorted((ROOT/'BetaGwent/build-inputs/classic-audio095-windows/banks').glob('*.bnk')):banks.append((f.name,f.read_bytes(),True))
    for name,raw,classic in banks:
        rows=audio.records(dict(audio.chunks(raw))[b'HIRC']);audio.require_load_order(rows)
        rec={i:(k,b)for i,k,b in rows};closure=audio.closure(rec,names,classic)
        bankproof.append({'bank':name,'events':len(names),'closureObjects':len(closure),'loadOrderVerified':True})
    canonical=(ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudio.ws').read_text('utf-8-sig')
    assert (out/'native-audio-final/scripts/game/betagwent/duelAudio.ws').read_text('utf-8-sig')==canonical
    assert (out/'classic-audio-final/Mods/modBetaGwentClassic132/content/scripts/game/betagwent/duelAudio.ws').read_text('utf16')==classic_audio(canonical)
    ng=json.loads((out/'native-audio-final/compile-nextgen-final/result.json').read_text('utf8'))
    cl=json.loads((ROOT/'BetaGwent/toolchains/classic-runtime/runs/ui-windows095-20261028-01-04/result.json').read_text('utf8'))
    assert ng['exitCode']==0 and not ng['timedOut'] and cl['compilePassed'] and not cl['timedOut'] and not cl['errors']
    assert ng['patchSourcesUnchangedDuringCompile'] and ng['artifacts'] and cl['freshArtifacts']
    base=ROOT/'BetaGwent/build/release095-20261027-final01'
    for previous,current in [(base/'scripts',out/'native-audio-final/scripts'),
            (base/'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts',out/'classic-audio-final/Mods/modBetaGwentClassic132/content/scripts')]:
        files={f.relative_to(previous).as_posix():sha(f)for f in previous.rglob('*.ws')}
        changed=[n for n,h in files.items()if sha(current/n)!=h]
        assert changed==['game/betagwent/duelAudio.ws'],changed
    report={'status':'ui-technical-checks-passed','uiSource':a.sources,'uiPatch':a.patch,'nativeMenus':8,'menuMaximumBytes':sizes,'limitBytes':65*1024**2,
        'sourceProof':source_proof,'nativeUiAudio':{'nextgen':True,'classic':True,'scope':'accepted 0.9.5 scripts with UI audio only; separate card audit not included'},'audioBanks':bankproof,
        'checks':results,'nativeGameTested':False,'allBetaAnimationsPorted':False,'fullReleaseRebuilt':False,'installedGameModified':False,'published':False}
    (out/('acceptance'+suffix+'.json')).write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps({'checks':len(results),'menus':8,'maximumBytes':sizes,'audioBanks':len(bankproof)}))
if __name__=='__main__':main()
