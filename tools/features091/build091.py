"""Build a fresh 0.9.1 candidate, preserving the accepted 0.9.0 art and bug fixes."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import BASE_ARCHIVES as BASE, CLASSIC_RUNTIME as RUNTIME
sys.path.insert(0,str(Path(__file__).resolve().parent))
from classic_soundbanks091 import fix_bundle as fix_classic_soundbanks
VERSION='0.9.1'  # --version 0.9.1a etc.: same pipeline, new archive/manifest names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def menu_music_cache(out,platform):
    source=out/'scripts/game/betagwent/duelAudio.ws'
    if not source.exists() or 'bg_menu_music_play' not in source.read_text('utf-8-sig'):return None
    manifest=out/'menu-music-caches/manifest.json'
    assert manifest.is_file(),'Editor music scripts require both platform music caches'
    record=json.loads(manifest.read_text('utf8'))['platforms']['classic' if platform=='1.32' else 'nextgen']
    cache=Path(record['cache']);assert sha(cache)==record['cacheSha256'],'Editor music cache changed'
    return cache
def run(args,log):
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf8') as output:
        r=subprocess.run([str(x) for x in args],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError(f'Failed ({r.returncode}); see {log}\n'+log.read_text('utf8',errors='replace')[-3500:])
    print('PASS',log.stem,flush=True)

def checked_run(out,name,args):
    # Resume is valid only for the same immutable game inputs AND test tools.
    if name=='regressions':
        from validate091 import NAMES as checks
        scripts=[ROOT/'tools/ai'/(n+'.js') for n in checks]
        scripts=[p if p.is_file() else p.with_suffix('.cjs') for p in scripts]
        paths=[ROOT/'tools/ai/validate091.py',ROOT/'tools/ai/comparison_inputs.py',ROOT/'data/beta924/normalized/catalog.json']+scripts
        paths+=[ROOT/'tools/ai/reconstruct_user_positions093.cjs']+list((ROOT/'tools/ai/fixtures/user093').glob('*.json'))
    elif name=='varied':paths=[ROOT/'tools/features091/varied091.py',ROOT/'tools/ai/check_varied_tactics091.js',ROOT/'tools/ai/check_consume_self.js',ROOT/'tools/ai/comparison_inputs.py']
    else:paths=[ROOT/str(args[1])]
    tools={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    record=dict(command=[str(x) for x in args],tools=tools,
                fingerprint=json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint'])
    proof=out/'checkpoints'/(name+'.json')
    if proof.exists():
        prior=json.loads(proof.read_text('utf8'))
        if prior['command']==record['command'] and prior['fingerprint']==record['fingerprint'] and all(prior['tools'].get(n)==h for n,h in tools.items()):
            print('PASS cached',name,flush=True);return
    run(args,out/'logs'/(name+'.log'));proof.parent.mkdir(exist_ok=True)
    proof.write_text(json.dumps(record,indent=2),encoding='utf8')

def verify_archive(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        assert len(names)==len(set(n.lower() for n in names))
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts and '\\' not in n for n in names)
        assert z.testzip() is None
        m=json.loads(z.read(f'manifest-{VERSION}.json'));assert m['version']==VERSION
        assert {f['path'] for f in m['files']}==set(names)-{f'manifest-{VERSION}.json'}
        for f in m['files']:
            raw=z.read(f['path']);assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256']
    return dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size,files=len(names))

def package(out,classic_audio=None):
    selected_profiles=None;profile_docs={}
    if VERSION in ('0.9.3','0.9.3a','0.9.3b','0.9.3c'):
        checks=out/'unfair-checks';gate=json.loads((checks/'report.json').read_text('utf8'))
        mapping_path=checks/'profile-mapping.json';parity_path=checks/'profile-ws-parity.json'
        assert sha(mapping_path)==gate['profileMappingSha256'] and sha(parity_path)==gate['profileParitySha256']
        assert sha(checks/'profile-source-proof.json')==gate['profileSourceProofSha256']
        selected_profiles=dict(displayDifficulty='Classic',namedProfiles=gate['selectedProfiles'],presetBindings=gate['presetBindings'],
                               mappingSha256=gate['profileMappingSha256'],selectedProfileWholeMatches=gate['selectedProfileWholeMatches'],
                               actualHandVisible=True,actualDeckVisible=True,globallyStrongestProfileEstablished=False)
        profile_docs={f'BetaGwentDocs/AI_Profile_Mapping_{VERSION}.json':mapping_path.read_bytes(),
                      f'BetaGwentDocs/AI_Profile_Parity_{VERSION}.json':parity_path.read_bytes()}
    hard_ai=None
    if VERSION=='0.9.3c':
        accepted_path=ROOT/'data/beta924/design/ai093c_validation.json'
        accepted=json.loads(accepted_path.read_text('utf8'));assert accepted['accepted'] and accepted['version']==VERSION
        assert accepted['candidateFingerprint']==json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint']
        holdout=accepted['holdout'];assert holdout['games']==3680 and holdout['errors']==0 and holdout['lower99']>.5 and holdout['clusterLower99']>.5
        hard_ai=dict(baselineVersion='0.9.3b',validationSha256=sha(accepted_path),holdoutGames=holdout['games'],uniqueCompositions=holdout['poolSize'],
                     scoreRate=holdout['scoreRate'],lower99=holdout['lower99'],clusterLower99=holdout['clusterLower99'],hiddenInformationAccessUnchanged=True)
        profile_docs[f'BetaGwentDocs/AI_Validation_{VERSION}.json']=accepted_path.read_bytes()
    notes_dir=Path(os.environ.get('BETA093_RELEASE_NOTES_DIR',str(ROOT/'docs/releases'))).resolve()
    assert notes_dir.is_relative_to(ROOT/'docs/releases') and notes_dir.is_dir()
    if notes_dir!=ROOT/'docs/releases':
        user_proof=out/'user-release-checks.json';user_gate=json.loads(user_proof.read_text('utf8'))
        assert user_gate['complete'] and user_gate['errors']==0 and user_gate['fingerprint']==json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint']
        profile_docs['BetaGwentDocs/UserFixes_0.9.3.json']=user_proof.read_bytes()
        profile_docs['BetaGwentDocs/PUBLICATION_INDEX.md']=(notes_dir/'README.md').read_bytes()
    note_names=['0.9.1_AI_RU.md','0.9.1_AI_EN.md','0.9.1_FIXES_RU.md','0.9.1_CHANGELOG_RU.md','0.9.1_CHANGELOG_EN.md','0.9.1_POST_EN_RU.md'] if notes_dir==ROOT/'docs/releases' else []
    if VERSION!='0.9.1':note_names+=[f'{VERSION}_CHANGELOG_RU.md',f'{VERSION}_CHANGELOG_EN.md']
    # Keep the release's Nexus description/post alongside its changelog.
    for note in sorted(notes_dir.glob(f'{VERSION}_*.md')):
        if note.name not in note_names:note_names.append(note.name)
    release_notes={name:sha(notes_dir/name) for name in note_names}
    ui_manifest=out/'ui-patch/manifest.json'
    assert ui_manifest.is_file(),'Build the gamepad menu patch before packaging: build_ui091.py'
    ui=json.loads(ui_manifest.read_text('utf8'))
    classic_audio=classic_audio or out/'classic-audio'
    audio_manifest=json.loads((classic_audio/'manifest.json').read_text('utf8'))
    assert sha(classic_audio/'soundspc.cache')==audio_manifest['cache']['sha256']
    freeze=json.loads((out/'source-freeze.json').read_text('utf8'))
    for name,digest in freeze['scripts'].items():assert sha(out/'scripts'/name)==digest,'Frozen script changed: '+name
    ng=json.loads((out/'compile-nextgen-final/result.json').read_text('utf8'))
    assert ng['exitCode']==0 and ng['completedByOutput'] and ng['patchSourcesUnchangedDuringCompile']
    assert {f['path']:f['sha256'] for f in ng['patchSourcesBefore']}==freeze['scripts']
    assert sha(out/'compile-nextgen-final/compiled/blob.rsblob')==ng['artifacts'][0]['sha256']
    classic_result=out/'classic-compile.json'
    if not classic_result.exists():classic_result=RUNTIME/'runs'/out.name/'result.json'
    classic=json.loads(classic_result.read_text('utf8'))
    assert classic['compilePassed'] and not classic['errors'] and not classic['timedOut']
    assert classic['preparationManifestSha256']==sha(out/'classic-prepared-final/preparation.json')
    prepared=out/'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts'
    expected=json.loads((out/'classic-prepared-final/preparation.json').read_text('utf8'))['outputScripts']
    assert {p.relative_to(prepared).as_posix():sha(p) for p in prepared.rglob('*.ws')}==expected
    assert 'betagwent091_ru.bnk' in (prepared/'game/betagwent/duelAudio.ws').read_text('utf16'),'Classic language-bank loader missing'
    dest=out/'archives';dest.mkdir(exist_ok=True);reports=[]
    for platform,mod in [('1.32','modBetaGwentClassic132'),('5.0+','modBetaGwent0924')]:
        menu_cache=menu_music_cache(out,platform)
        source=BASE/f'GwentBetaClassic-0.9.0-{platform}-AllLanguages.zip'
        target=dest/f'GwentBetaClassic-{VERSION}-{platform}-AllLanguages.zip'
        assert source.is_file()
        if target.exists():
            report=verify_archive(target)
            with zipfile.ZipFile(target) as existing:
                prior=json.loads(existing.read(f'manifest-{VERSION}.json'))
                assert prior['aiSourceFingerprint']==json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint']
                assert prior.get('releaseNotes')==release_notes,'Release notes changed: create fresh archives'
                assert prior.get('uiPatchManifestSha256')==sha(ui_manifest),'UI patch changed: create fresh archives'
                if platform=='1.32':assert prior.get('classicAudioManifestSha256')==sha(classic_audio/'manifest.json'),'Classic audio changed: create fresh archives'
                assert prior.get('menuMusicCacheSha256')==(sha(menu_cache) if menu_cache else None),'Editor music changed: create fresh archives'
                if selected_profiles:assert prior.get('originalBetaAI')==selected_profiles,'Selected profiles changed: create fresh archives'
                if hard_ai:assert prior.get('hardAI')==hard_ai,'Accepted Hard AI proof changed: create fresh archives'
            with zipfile.ZipFile(source) as original_archive:
                original={f['path']:f['sha256'] for f in json.loads(original_archive.read('manifest-0.9.0.json'))['files']}
            report['preservedBaseFiles']=sum(original.get(f['path'])==f['sha256'] for f in prior['files'])
            reports.append(report);continue
        patch=dict(profile_docs)
        if menu_cache:patch['Mods/modBetaGwentMenuMusic/content/soundspc.cache']=menu_cache.read_bytes()
        for name,record in ui['platforms'][platform]['files'].items():
            path=Path(record['path']);assert sha(path)==record['sha256']
            patch[name]=path.read_bytes()
        if platform=='1.32':
            folder=out/'classic-prepared-final/Mods'/mod/'content/scripts'
            patch.update({f'Mods/{mod}/content/scripts/'+p.relative_to(folder).as_posix():p.read_bytes() for p in folder.rglob('*.ws')})
            patch[f'Mods/{mod}/content/soundspc.cache']=(classic_audio/'soundspc.cache').read_bytes()
        else:
            patch[f'Mods/{mod}/content/precompiled.rsblob']=(out/'compile-nextgen-final/compiled/blob.rsblob').read_bytes()
        for name in note_names:patch['BetaGwentDocs/'+name]=(notes_dir/name).read_bytes()
        for lang in ['RU','EN']:
            patch[f'BetaGwentDocs/CHANGELOG_{lang}.md']=(notes_dir/f'{VERSION}_CHANGELOG_{lang}.md').read_bytes()
        files=[];preserved=0
        with zipfile.ZipFile(source) as src,zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as dst:
            old_manifest=json.loads(src.read('manifest-0.9.0.json'))
            original={f['path']:f for f in old_manifest['files']}
            assert set(original)==set(src.namelist())-{'manifest-0.9.0.json'}
            for info in src.infolist():
                n=info.filename
                if n.startswith('manifest-'):continue
                source_raw=src.read(n)
                assert len(source_raw)==original[n]['bytes'] and hashlib.sha256(source_raw).hexdigest()==original[n]['sha256'],'Base archive changed: '+n
                raw=patch.pop(n,None)
                # 1.32: vanilla always-load list; betagwent79 loads per match (Seven Cats q601 hang).
                if platform=='1.32' and n==f'Mods/{mod}/content/blob0.bundle':raw=fix_classic_soundbanks(source_raw if raw is None else raw)
                if raw is None:raw=source_raw
                if n==f'Mods/{mod}/info.json':
                    metadata=json.loads(raw.decode('utf-8-sig'));metadata.update(version=VERSION,gamepadHandPreviewFix=True,gamepadPileNavigationFix=True);raw=json.dumps(metadata,ensure_ascii=False,indent=2).encode('utf8')
                if n=='BetaGwentDocs/BuildInfo.json':
                    metadata=json.loads(raw.decode('utf-8-sig'));metadata.update(version=VERSION,nativeGameplayVerified=False,gamepadHandPreviewFix=True,gamepadPileNavigationFix=True,aiSourceFingerprint=json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint'])
                    if selected_profiles:metadata['originalBetaAI']=selected_profiles
                    if hard_ai:metadata['hardAI']=hard_ai
                    raw=json.dumps(metadata,ensure_ascii=False,indent=2).encode('utf8')
                if n in ('BetaGwentDocs/README_RU.md','BetaGwentDocs/README_EN.md'):
                    intro=(f'# Gwent Beta Classic {VERSION}\n\nИзменения этого обновления: [{VERSION}_CHANGELOG_RU.md]({VERSION}_CHANGELOG_RU.md). Ниже — руководство базовой версии 0.9.0.\n\n' if n.endswith('_RU.md') else f'# Gwent Beta Classic {VERSION}\n\nThis update: [{VERSION}_CHANGELOG_EN.md]({VERSION}_CHANGELOG_EN.md). The base 0.9.0 guide follows.\n\n')
                    raw=intro.encode('utf8')+raw
                if raw==source_raw:preserved+=1
                dst.writestr(n,raw);files.append(dict(path=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            for n,raw in patch.items():dst.writestr(n,raw);files.append(dict(path=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            manifest={k:v for k,v in old_manifest.items() if k not in ('version','files','nativeGameplayVerified')}
            manifest.update(version=VERSION,files=files,nativeGameplayVerified=False,baseVersion='0.9.0-final17',candidate=notes_dir==ROOT/'docs/releases',
                            aiSourceFingerprint=json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint'],
                            maximumDifficultyKnowsStartingList=True,releaseNotes=release_notes,
                            gamepadHandPreviewFix=True,gamepadPileNavigationFix=True,uiPatchManifestSha256=sha(ui_manifest),
                            classicSoundbankList='vanilla-1.32' if platform=='1.32' else 'unchanged')
            manifest['classicAudioBanks']='per-language-on-demand' if platform=='1.32' else 'unchanged'
            if menu_cache:manifest['menuMusicCacheSha256']=sha(menu_cache)
            if platform=='1.32':manifest['classicAudioManifestSha256']=sha(classic_audio/'manifest.json')
            if selected_profiles:manifest['originalBetaAI']=selected_profiles
            if hard_ai:manifest['hardAI']=hard_ai
            dst.writestr(f'manifest-{VERSION}.json',json.dumps(manifest,indent=2))
        record=verify_archive(target);record['preservedBaseFiles']=preserved;reports.append(record)
        target.with_suffix('.zip.sha256').write_text(record['sha256']+'  '+target.name+'\n',encoding='ascii')
    release=dict(version=VERSION,archives=reports,nativeGameplayVerified=False)
    if selected_profiles:release['originalBetaAI']=selected_profiles
    if hard_ai:release['hardAI']=hard_ai
    (out/'release.json').write_text(json.dumps(release,indent=2),encoding='utf8')
    return reports

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path)
    p.add_argument('--resume',action='store_true')
    p.add_argument('--prepare-only',action='store_true')
    p.add_argument('--ui-source',type=Path,help='Prepared platform-specific gamepad UI sources (prepare_ui091.py)')
    p.add_argument('--classic-audio',type=Path,help='Verified split Classic language banks (split_classic_audio091.py)')
    p.add_argument('--version',default='0.9.1',help='Release label, e.g. 0.9.1a (needs docs/releases/<version>_CHANGELOG_RU/EN.md)')
    p.add_argument('--skip-package',action='store_true',help='Complete technical checks; package only after additional release gates pass')
    p.add_argument('--native-first',action='store_true',help='Check new WS syntax on both native compilers before long battle tests')
    a=p.parse_args();global VERSION;VERSION=a.version;latest=ROOT/'BetaGwent/build/release091-latest.json'
    if a.out:out=a.out.resolve()
    elif a.resume:
        if not latest.exists():p.error('--resume requires --out, or a previous default build')
        out=Path(json.loads(latest.read_text('utf8'))['path']).resolve()
    else:out=ROOT/'BetaGwent/build'/('release091-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    assert out.is_relative_to((ROOT/'BetaGwent/build').resolve())
    assert not (out/'cancelled.json').exists(),'This candidate was cancelled; use a fresh --out directory'
    if not a.resume:
        assert not out.exists(),'Use a fresh output path or --resume'
        run([sys.executable,'-X','utf8','tools/features091/prepare091.py','--out',out],out.parent/(out.name+'-prepare.log'))
    else:assert (out/'source-freeze.json').is_file()
    latest.write_text(json.dumps(dict(path=str(out)),indent=2),encoding='utf8')
    if a.prepare_only:return
    for name,digest in json.loads((out/'source-freeze.json').read_text('utf8'))['scripts'].items():assert sha(out/'scripts'/name)==digest
    logs=out/'logs'
    run(['node','tools/features091/check_practice091.js',out],logs/'practice-entry.log')
    run([sys.executable,'-X','utf8','tools/features091/test_build091.py'],logs/'build-contracts.log')
    run([sys.executable,'-X','utf8','tools/features091/test_glossary091.py'],logs/'glossary.log')
    if not (out/'rules/manifest.json').exists():run([sys.executable,'-X','utf8','tools/ai/snapshot.py',out/'rules'],logs/'snapshot.log')
    # Ensure tests execute precisely the battle sources sent to both compilers.
    sys.path.insert(0,str(ROOT/'tools/ai'));from build_js import NAMES
    for name in NAMES:
        if (out/'scripts/game/betagwent'/(name+'.ws')).exists():
            assert sha(out/'scripts/game/betagwent'/(name+'.ws'))==sha(out/'rules/sources/BetaGwent/development/scripts/game/betagwent'/(name+'.ws')),'Snapshot/compile mismatch: '+name
    if a.native_first:
        if not (out/'compile-nextgen-final/result.json').exists():
            run([sys.executable,'-X','utf8','tools/features082/compile_nextgen_final090.py','--input',out],logs/'compile-nextgen.log')
        else:assert json.loads((out/'compile-nextgen-final/result.json').read_text('utf8'))['exitCode']==0
        if not (out/'classic-compile.json').exists() and not (RUNTIME/'runs'/out.name/'result.json').exists():
            run([sys.executable,'-X','utf8','tools/classic132/native_compile.py','--probe-root',RUNTIME,'--prepared',out/'classic-prepared-final','--label',out.name,'--compiler-feedback','--without-store-provider','--timeout','180'],logs/'compile-classic.log')
    checked_run(out,'regressions',[sys.executable,'-X','utf8','tools/ai/validate091.py',out/'rules',out/'regressions'])
    checked_run(out,'tactics-all',['node','tools/ai/check_tactics082.js','--snapshot',out/'rules','--output',out/'tactics-all'])
    checked_run(out,'rows-all',['node','tools/ai/check_row_choices082.js','--snapshot',out/'rules','--output',out/'rows-all'])
    checked_run(out,'varied',[sys.executable,'tools/features091/varied091.py',out/'rules',out/'varied'])
    if VERSION in ('0.9.3','0.9.3a','0.9.3b','0.9.3c') and not (out/'unfair-checks/report.json').exists():
        run([sys.executable,'-X','utf8','tools/features093/check_unfair093.py',out],logs/'unfair-mode.log')
    if not (out/'compile-nextgen-final/result.json').exists():
        run([sys.executable,'-X','utf8','tools/features082/compile_nextgen_final090.py','--input',out],logs/'compile-nextgen.log')
    if not (out/'classic-compile.json').exists() and not (RUNTIME/'runs'/out.name/'result.json').exists():
        run([sys.executable,'-X','utf8','tools/classic132/native_compile.py','--probe-root',RUNTIME,'--prepared',out/'classic-prepared-final','--label',out.name,'--compiler-feedback','--without-store-provider','--timeout','180'],logs/'compile-classic.log')
    ui_source=a.ui_source.resolve() if a.ui_source else out/'ui-sources'
    if not (out/'ui-patch/manifest.json').exists():
        if not ui_source.exists():run([sys.executable,'-X','utf8','tools/features091/prepare_ui091.py','--out',ui_source],logs/'prepare-ui.log')
        run(['node','tools/features091/check_related091.js',ui_source],logs/'related-cards.log')
        for key in ['classic','nextgen']:
            run(['node','tools/features091/check_ambush_shackles091.js',ui_source/key/'ui'],logs/('ambush-shackles-'+key+'.log'))
        for key in ['classic','nextgen']:
            if not (ui_source/key/'menus/menus.json').exists():
                run([sys.executable,'-X','utf8','tools/universal/build_menus.py','--stage','202',
                     '--prepared',out/'classic-prepared-final','--source-ui',ui_source/key/'ui',
                     '--input-manifest',ui_source/key/'ui-inputs.json','--out',ui_source/key/'menus'],logs/('menus-'+key+'.log'))
        run([sys.executable,'-X','utf8','tools/features091/build_ui091.py','--ui',ui_source,'--out',out/'ui-patch'],logs/'ui-patch.log')
    run(['node','tools/features091/check_gamepad091.js',ui_source,out/'gamepad-tests.json'],logs/'gamepad.log')
    run(['node','tools/features091/check_aim_source091.js',ui_source],logs/'aim-source.log')
    classic_audio=a.classic_audio.resolve() if a.classic_audio else out/'classic-audio'
    if not (classic_audio/'manifest.json').exists():
        run([sys.executable,'-X','utf8','tools/features091/split_classic_audio091.py','--out',classic_audio],logs/'classic-audio-split.log')
    run([sys.executable,'-X','utf8','tools/features091/test_classic_audio091.py','--prepared',out/'classic-prepared-final','--banks',classic_audio,'--output',out/'classic-audio-check'],logs/'classic-audio-tests.log')
    if 'bg_menu_music_play' in (out/'scripts/game/betagwent/duelAudio.ws').read_text('utf-8-sig'):
        if not (out/'menu-music/music.json').exists():
            run([sys.executable,'-X','utf8','tools/ui/build_menu_music092.py','--out',out/'menu-music'],logs/'menu-music-build.log')
        if not (out/'menu-music-caches/manifest.json').exists():
            run([sys.executable,'-X','utf8','tools/ui/package_menu_music092.py','--music',out/'menu-music','--out',out/'menu-music-caches'],logs/'menu-music-caches.log')
        run([sys.executable,'-X','utf8','tools/ui/check_menu_music092.py','--snapshot',out/'rules','--out',out/'menu-music-check'],logs/'menu-music-check.log')
    if a.skip_package:
        print('TECHNICAL CHECKS COMPLETE; packaging deferred for additional release gates.',flush=True)
        return
    reports=package(out,classic_audio)
    print(json.dumps(dict(version=VERSION,archives=reports,gameplayVerified=False),indent=2),flush=True)

if __name__=='__main__':main()
