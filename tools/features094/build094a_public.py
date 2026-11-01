"""Full public 0.9.4a: the 0.9.4 pipeline plus deck-editor Beta effects, the fixed
leader, editor/gamepad fixes, Spectral Whale and two AI fixes.

No installation or publication. --finish-prepared accepts only completed proofs.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))  # build_inputs (also when resuming)
sys.path.insert(0,str(ROOT/'tools/features093'))
sys.path.insert(0,str(ROOT/'tools/features094'))
sys.path.insert(0,str(ROOT/'tools/ai'))
sys.path.insert(0,str(ROOT/'tools/features095'))
from validate091 import NAMES as REGRESSION_NAMES
VERSION='0.9.4a'
NOTES=ROOT/'docs/releases/0.9.4a-public-20261027'
STORE=['betaGwentStore','betaGwentStoreText','betaGwentRewardActors','betaGwentRewardedQuests']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run(out,label,command):
    log=out/'logs'/(label+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf8') as f:subprocess.run([str(x) for x in command],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    print('PASS',label,flush=True)

def collect(out):
    snapshot=json.loads((out/'rules/manifest.json').read_text('utf8'));fingerprint=snapshot['fingerprint']
    sys.path.insert(0,str(ROOT/'tools/ai'));from snapshot import inputs,fingerprint as current_fingerprint
    assert current_fingerprint(inputs())==fingerprint,'Current engine differs from frozen release'
    summary=json.loads((out/'regressions/summary.json').read_text('utf8'))
    assert len(summary)==len(REGRESSION_NAMES)==len({r['name'] for r in summary})
    assert {r['name'] for r in summary}==set(REGRESSION_NAMES) and all(r['exitCode']==0 for r in summary)
    if VERSION=='0.9.5':
        passing=json.loads((out/'regressions/check_pass_carry094a.json').read_text('utf8'))
        hidden=json.loads((out/'regressions/check_pass_carry_hidden094a.json').read_text('utf8'))
        assert passing['checks']==155 and not passing['failures'] and passing['actualWitcherScript']
        assert passing['fingerprint']==fingerprint
        assert hidden['checks']==30 and hidden['hiddenEnemyIdentityAndOrderIndependent'] and not hidden['failures']
    whole=json.loads((out/'selected-profiles-current92.json').read_text('utf8'))
    assert whole['complete'] and not whole.get('error') and len(whole['records'])==whole['total']==92 and whole['bindingChecks']==109
    assert whole['fingerprint']==fingerprint
    for name,digest in whole['inputDigests'].items():assert sha(Path(name))==digest,name
    assert whole['peakActionsPerCallback']<=1 and not whole['nativeProcessesAllowed']
    for name,count in [('user-ui-check.json',7120),('whale-check.json',2242),('editor-fx-source.json',566),('choice-captions.json',2498),('choice-fates.json',153),('card-offer.json',18),('reveal-classic.json',80),('reveal-leader.json',51),('user-audio-check/report.json',309036)]:
        data=json.loads((out/name).read_text('utf8'));assert data['checks']==count,name
        if 'fingerprint' in data:assert data['fingerprint']==fingerprint,name
    fonts=json.loads((out/'user-font-check.json').read_text('utf8'));assert fonts['complete'] and fonts['languages']==13 and len(fonts['records'])==52
    selection=json.loads((out/'ui-selection.json').read_text('utf8'));ui=Path(selection['source'])
    if not ui.is_relative_to(out):
        reuse=json.loads((out/'ui-reuse-proof.json').read_text('utf8'));prior=Path(reuse['source'])
        assert ui==prior/'ui-sources' and prior.is_relative_to(ROOT/'BetaGwent/build')
        assert reuse['canonical']==selection['canonical'] and sha(prior/'ui-patch/manifest.json')==reuse['patchManifestSha256']
        assert sha(ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws')==reuse['boardBridgeSha256']
    expected=json.loads((ui/'gamepad-source.json').read_text('utf8'));assert expected==selection['canonical']
    ui_reports=[]
    if VERSION=='0.9.5':
        from ui_release095 import reports
        ui_reports=reports(out,ui)
    for n,h in expected.items():assert sha(ROOT/'BetaGwent/ui/src'/n)==h,n
    for platform in ['classic','nextgen']:
        menus=json.loads((ui/platform/'menus/menus.json').read_text('utf8'))
        frozen_ui=json.loads((ui/platform/'ui-inputs.json').read_text('utf8'))['sources']
        assert menus['frozenSources']==frozen_ui
        for n,h in frozen_ui.items():assert sha(ui/platform/'ui/src'/n)==h,n
        assert all(sha(Path(m['path']))==m['sha256'] for m in menus['menus'])
    packaged_ui=json.loads((out/'ui-patch/manifest.json').read_text('utf8'))
    assert max(m['bytes'] for p in packaged_ui['platforms'].values() for m in p['menus'])<=65*1024**2
    for key in ['classic','nextgen']:
        for name,count in [('editor-slot',27),('pad-legend',23),('pass-coin',11)]:
            data=json.loads((out/(name+'-'+key+'.json')).read_text('utf8'));assert data['checks']==count and not data['failures'],(name,key,data['checks'],count)
        for name,count in [('editor-fx-'+key+'.json',566),('editor-valid-'+key+'.json',1013 if key=='classic' else 1005),('editor-leader-lock-'+key+'.json',61),('controller-aim-'+key+'.json',23),('editor-stats-'+key+'.json',48),('editor-layout-'+key+'.json',55)]:
            data=json.loads((out/name).read_text('utf8'));assert data['checks']==count and not data['failures'],name
    followup=json.loads((out/'editor-followup.json').read_text('utf8'));assert followup['checks']==48 and not followup['failures']
    for platform,rows in packaged_ui['platforms'].items():
        editors=[m for m in rows['menus'] if m.get('editorFx094')]
        assert len(editors)==2 and all(m['editorFx094']['appendedBytes']==len((ROOT/'BetaGwent/ui/assets/editor094/append-bc3.bin').read_bytes()) for m in editors),platform
        editor_spec=json.loads((ROOT/'data/beta924/design/editor_vfx094.json').read_text('utf8'))
        assert editor_spec['validVfx094a']['index']==28
        expected_cells=29+len(editor_spec.get('chrome096',{}).get('names',[]))+len(editor_spec.get('slotFx096',{}).get('cells',[]))
        assert len(editor_spec['rects'])==expected_cells
        assert all(m['editorFx094']['classicFrameBindings']==(len(editor_spec['rects']) if platform=='1.32' else 0) for m in editors),platform
    whale=json.loads((out/'whale-check.json').read_text('utf8'));assert whale['fingerprint']==fingerprint and not whale['failures']
    full=json.loads((out/'full-ai-games/report.json').read_text('utf8'));assert full['complete'] and full['errors']==0 and len(full['games'])==10 and full['fingerprint']==fingerprint
    storage=json.loads((out/'profile-storage-check/report.json').read_text('utf8'))
    assert storage['complete'] and storage['checks']>=1241 and storage['bankChecksumsValidated'] and storage['profileSourcesFrozen']
    assert storage['fingerprint']==fingerprint and not storage['nativeSerializationTested']
    for n,h in storage['sources'].items():assert sha(ROOT/n)==h,n
    for folder in ['save-safety-check','starter-recovery-check']:
        safety=json.loads((out/folder/'report.json').read_text('utf8'))
        assert safety['complete'] and not safety['failures'] and safety['profileSourcesFrozen']
        assert safety['snapshotFingerprint']==fingerprint and not safety['nativeSerializationTested']
        for n,h in safety['sources'].items():assert sha(ROOT/n)==h,n
        if folder=='save-safety-check':assert safety['savedPlayerFields']==STORE,'Only the store may be saved on W3PlayerWitcher'
    delivery=json.loads((out/'profile-native-source-proof-complete.json').read_text('utf8'))
    expected_profile_files={'aaProfileStore.ws','deckProfile.ws','profileBackup.ws','collectionProfile.ws','collectionQuest.ws','deckBuilder.ws','profileCleanup090.ws','kegProfile.ws','scrapsProfile.ws','opponentRotation.ws'}
    assert delivery['complete'] and len(delivery['records'])==len(expected_profile_files)
    assert {r['name'] for r in delivery['records']}==expected_profile_files
    assert sum(r['classicInjectedMembersVerified'] for r in delivery['records'])>=93
    assert sha(Path(delivery['classicPlayerPath']))==delivery['classicPlayerSha256']
    for row in delivery['records']:
        assert sha(ROOT/'BetaGwent/development/scripts/game/betagwent'/row['name'])==row['canonicalSha256']==row['preparedSha256']
    for platform in ['classic','nextgen']:
        prepared=out/'all-card-platforms'/platform
        matrix=json.loads((prepared/'coverage.json').read_text('utf8'));native=json.loads((prepared/'manifest.json').read_text('utf8'))
        assert matrix['complete'] and not matrix['failures'] and matrix['testedCards']==matrix['cards']==511
        assert len(matrix['records'])==4088 and all(r['ok'] for r in matrix['records'])
        assert len(matrix['rareCases'])==24 and all(r['ok'] for r in matrix['rareCases'])
        assert matrix['fingerprint']==native['fingerprint'] and not matrix['nativeGameplayExecuted'] and matrix['actualNativeResultDispatch']
        assert matrix['checkerSha256']==sha(ROOT/'tools/ai/check_all_cards198.cjs')
        for name,digest in native['sourceInputs'].items():assert sha(Path(name))==digest,name
    files=['regressions/summary.json','regressions/check_user_targets093.json','regressions/check_reveal_strategy093.json','regressions/check_ambush_hyp094b.json','regressions/check_ambush_decision094b.json','regressions/check_ambush_pairs094b.json','user-ui-check.json','choice-captions.json','choice-fates.json','user-font-check.json','card-offer.json','reveal-classic.json','reveal-leader.json','user-audio-check/report.json','selected-profiles-current92.json','full-ai-games/report.json','ui-selection.json','gamepad-tests.json']
    files.append('profile-storage-check/report.json')
    files.append('save-safety-check/report.json')
    files.append('starter-recovery-check/report.json')
    files.append('profile-native-source-proof-complete.json')
    files+=['whale-check.json','editor-fx-source.json','editor-followup.json']+[n+'-'+k+'.json' for k in ['classic','nextgen'] for n in ['editor-fx','editor-leader-lock','controller-aim','editor-stats','editor-layout']]
    files+=['editor-valid-'+key+'.json' for key in ['classic','nextgen']]
    files+=[name+'-'+key+'.json' for key in ['classic','nextgen'] for name in ['editor-slot','pad-legend','pass-coin']]
    # Some historical groups emit only a log; retain every JSON report they produce.
    files += ['regressions/'+name+'.json' for name in REGRESSION_NAMES
        if (out/'regressions'/(name+'.json')).is_file() and 'regressions/'+name+'.json' not in files]
    files += ['all-card-platforms/'+p+'/'+n for p in ['classic','nextgen'] for n in ['manifest.json','coverage.json']]
    files=list(dict.fromkeys(files+ui_reports))
    if VERSION=='0.9.5':files.append('logs/profile-provenance-contracts.log')
    report=dict(complete=True,errors=0,version=VERSION,fingerprint=fingerprint,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        regressionGroups=len(REGRESSION_NAMES),currentSelectedProfileParityMatches=92,presetBindings=109,newStrengthComparisonConducted=False,
        historicalStrengthEvidence='0.9.3c fixed3680-game trial is preserved separately; current mechanics and target fixes were not part of that trial.',
        reports=[dict(path=n,sha256=sha(out/n)) for n in files],nativeGameplayVerified=False,installed=False,published=False)
    notes=sorted(NOTES.glob(VERSION+'_*.md'));assert len(notes)==39
    report['publicationCopy']={p.name:sha(p) for p in notes}
    gate=out/'user-release-checks.json'
    if gate.exists():
        prior=json.loads(gate.read_text('utf8'));report['createdAt']=prior['createdAt']
        assert report==prior,'Completed user-fix proof changed; do not repackage an existing release'
    else:gate.write_text(json.dumps(report,indent=2)+'\n','utf8')

def platform_proof(out):
    # Each platform run covers 511 cards over the actual native-prepared sources and takes a long
    # time, while the preparer refuses to reuse its own output directory. A completed proof is
    # bound below to the exact source bytes, checker body and translated files on disk, so --resume
    # may reuse it; collect() asserts the same facts again before any archive is written.
    root=out/'all-card-platforms';preparation=root/'preparation.json'
    if not preparation.exists():return False
    try:
        bound={r['platform']:r['fingerprint']for r in json.loads(preparation.read_text('utf8'))}
        assert set(bound)=={'classic','nextgen'}
        checker=sha(ROOT/'tools/ai/check_all_cards198.cjs')
        for platform in ['classic','nextgen']:
            matrix=json.loads((root/platform/'coverage.json').read_text('utf8'))
            native=json.loads((root/platform/'manifest.json').read_text('utf8'))
            assert matrix['complete'] and not matrix['failures'] and matrix['testedCards']==matrix['cards']==511
            assert len(matrix['records'])==4088 and all(r['ok'] for r in matrix['records'])
            assert len(matrix['rareCases'])==24 and all(r['ok'] for r in matrix['rareCases'])
            assert matrix['fingerprint']==native['fingerprint']==bound[platform]
            assert not matrix['nativeGameplayExecuted'] and matrix['actualNativeResultDispatch']
            assert matrix['checkerSha256']==checker
            for name,digest in native['sourceInputs'].items():assert sha(Path(name))==digest,name
            for name,digest in native['snapshotFiles'].items():assert sha(root/platform/name)==digest,name
    except Exception:return False
    return True

def finish(out):
    assert not (out/'release-readiness.json').exists(),'Do not alter a completed release'
    collect(out)
    sys.path.insert(0,str(ROOT/'tools/features091'))
    spec=importlib.util.spec_from_file_location('public_package091',ROOT/'tools/features091/build091.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.VERSION=VERSION
    os.environ['BETA093_RELEASE_NOTES_DIR']=str(NOTES)
    from build_inputs import AUDIO
    if (out/'release.json').exists():
        # Independent verification may have stopped after complete packaging.
        # Preserve those archives and bind them again before retrying the audit.
        prior=json.loads((out/'release.json').read_text('utf8'))
        assert prior['version']==VERSION and len(prior['archives'])==2
        assert {Path(r['path']).name for r in prior['archives']}=={f'GwentBetaClassic-{VERSION}-{p}-AllLanguages.zip' for p in ['1.32','5.0+']}
        for row in prior['archives']:
            archive=Path(row['path']).resolve()
            assert archive.parent==(out/'archives').resolve() and archive.stat().st_size==row['bytes']
            assert sha(archive)==row['sha256']==archive.with_suffix('.zip.sha256').read_text('ascii').split()[0]
    else:module.package(out,AUDIO)
    run(out,'independent-public-audit',[sys.executable,'-X','utf8','tools/features093/verify093.py',out,'--version',VERSION,'--user-release'])
    audit=json.loads((out/'archive-verification.json').read_text('utf8'))
    ready=dict(version=VERSION,status='ready',sourceFingerprint=json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint'],
        completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),archives=audit['archives'],regressionGroups=len(REGRESSION_NAMES),currentSelectedProfileParityMatches=92,
        publicationCopyLanguages=13,publicationCopyDocuments=39,maxMenuBytes=audit['maxMenuBytes'],classicCompilerPassed=True,nextgenCompilerPassed=True,
        nativeGameplayVerified=False,installed=False,published=False,verifiedReport='archive-verification.json')
    (out/'release-readiness.json').write_text(json.dumps(ready,indent=2)+'\n','utf8');print(json.dumps(ready),flush=True)

def main():
    global VERSION,NOTES
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--finish-prepared',action='store_true');p.add_argument('--resume',action='store_true',help='continue a fresh public build whose technical stage stopped');p.add_argument('--reuse-ui-from',type=Path);p.add_argument('--version',choices=['0.9.4a','0.9.5'],default=VERSION);a=p.parse_args();out=a.out.resolve()
    VERSION=a.version
    if VERSION=='0.9.5':
        from ui_release095 import NOTES as ui_notes
        NOTES=ui_notes
    assert out.is_relative_to(ROOT/'BetaGwent/build') and out!=ROOT/'BetaGwent/build'
    if not a.finish_prepared:
        if a.resume:assert (out/'source-freeze.json').is_file() and not (out/'user-release-checks.json').exists(),'Nothing to resume'
        else:
            assert not out.exists(),'Use a fresh release folder'
            subprocess.run([sys.executable,'-X','utf8','tools/ai/gen_clone.py'],cwd=ROOT,check=True)
            if VERSION=='0.9.5':
                sys.path.insert(0,str(ROOT/'tools/features095'))
                from notes095_public import main as notes
            else:
                from notes094a_public import main as notes
            notes()
            subprocess.run([sys.executable,'-X','utf8','tools/features091/build091.py','--out',str(out),'--version',VERSION,'--prepare-only'],cwd=ROOT,check=True)
            if VERSION=='0.9.5':
                from ui_release095 import freeze
                freeze(out)
            sys.path.insert(0,str(ROOT/'tools/features092'));import build092
            if a.reuse_ui_from:
                prior=a.reuse_ui_from.resolve();assert prior.is_relative_to(ROOT/'BetaGwent/build')
                canonical=json.loads((prior/'ui-sources/gamepad-source.json').read_text('utf8'))
                for name,digest in canonical.items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest,name
                old_manifest=json.loads((prior/'ui-patch/manifest.json').read_text('utf8'))
                for platform in old_manifest['platforms'].values():
                    for item in platform['files'].values():assert sha(Path(item['path']))==item['sha256']
                bridge=sha(ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws')
                assert bridge==sha(prior/'scripts/game/betagwent/developmentBoardMenu.ws')
                shutil.copytree(prior/'ui-patch',out/'ui-patch')
                (out/'ui-reuse-proof.json').write_text(json.dumps(dict(source=str(prior),canonical=canonical,patchManifestSha256=sha(prior/'ui-patch/manifest.json'),boardBridgeSha256=bridge),indent=2)+'\n','utf8')
            build092.copy_assets(out,include_ui=False)
        if VERSION=='0.9.5':
            from ui_release095 import validate_frozen
            validate_frozen(out)
        from build_inputs import AUDIO
        ui=(a.reuse_ui_from.resolve()/'ui-sources') if a.reuse_ui_from else out/'ui-sources'
        run(out,'classic132-ops',[sys.executable,'-X','utf8','tools/ai/check_classic132_ops094.py'])
        run(out,'technical',[sys.executable,'-X','utf8','tools/features091/build091.py','--out',out,'--version',VERSION,'--resume','--skip-package','--native-first','--classic-audio',AUDIO,'--ui-source',ui])
        if VERSION=='0.9.5':
            run(out,'profile-provenance-contracts',[sys.executable,'-X','utf8','tools/ai/test_profile_provenance096.py',out])
        canonical=json.loads((ui/'gamepad-source.json').read_text('utf8'))
        (out/'ui-selection.json').write_text(json.dumps(dict(source=str(ui),canonical=canonical,reuseAcceptedPatch=False),indent=2)+'\n','utf8')
        for label,cmd in [
            ('user-ui',['node','tools/ai/check_user_ui093.cjs',out/'user-ui-check.json']),
            ('whale',['node','tools/ai/check_whale094a.cjs',out/'rules',out/'whale-check.json']),
            ('editor-fx-source',['node','tools/ui/check_editor_fx094.cjs','BetaGwent/ui/src/BetaGwentBoard.as','data/beta924/design/editor_vfx094.json',out/'editor-fx-source.json']),
            ('editor-feedback',['node','tools/ui/check_editor_feedback094.cjs']),
            ('editor-stats-classic',['node','tools/ui/check_editor_stats094a.cjs',ui/'classic/ui/src/BetaGwentBoard.as',out/'editor-stats-classic.json']),
            ('editor-stats-nextgen',['node','tools/ui/check_editor_stats094a.cjs',ui/'nextgen/ui/src/BetaGwentBoard.as',out/'editor-stats-nextgen.json']),
            ('editor-followup',['node','tools/ui/check_editor_followup094.cjs','BetaGwent/ui/src/BetaGwentBoard.as',out/'editor-followup.json']),
            ('editor178',['node','tools/ui/check_editor178.js']),
            ('editor168',['node','tools/ui/check_editor168.js']),
            ('user-fonts',[sys.executable,'-X','utf8','tools/features093/check_user_fonts093.py',out/'user-font-check.json']),
            ('choice-captions',['node','tools/ai/check_choice_captions093.cjs',out/'choice-captions.json']),
            ('choice-fates',['node','tools/ai/check_choice_fates093.cjs',out/'rules',out/'choice-fates.json']),
            ('card-offer',['node','tools/ai/check_card_offer093.cjs',out/'rules',out/'card-offer.json']),
            ('classic-reveal',['node','tools/ai/check_reveal_classic093.cjs',out/'rules',out/'reveal-classic.json']),
            ('leader-reveal',['node','tools/ai/check_reveal_leader093.cjs',out/'rules',out/'reveal-leader.json']),
            ('audio',[sys.executable,'-X','utf8','tools/features093/check_multivoice_user093.py',out/'rules/sources/BetaGwent/development/scripts/game/betagwent/duelAudioCatalog.ws',out/'user-audio-check','--snapshot',out/'rules']),
            ('profile-storage',[sys.executable,'-X','utf8','tools/ai/check_deck_recovery198.py',out/'rules',out/'profile-storage-check','--release']),
            ('save-safety',[sys.executable,'-X','utf8','tools/ai/check_save_safety094.py',out/'rules',out/'save-safety-check','--release']),
            ('starter-recovery',[sys.executable,'-X','utf8','tools/ai/check_starter_recovery094.py',out/'rules',out/'starter-recovery-check','--release']),
            ('profile-delivery',[sys.executable,'-X','utf8','tools/ai/check_prepared_profiles198.py',out,out/'profile-native-source-proof-complete.json']),
            ('all-card-platforms',[sys.executable,'-X','utf8','tools/ai/prepare_platform_rules198.py',out,out/'rules',out/'all-card-platforms']),
            ('classic-all-cards',['node','tools/ai/check_all_cards198.cjs',out/'all-card-platforms/classic',out/'all-card-platforms/classic/coverage.json']),
            ('nextgen-all-cards',['node','tools/ai/check_all_cards198.cjs',out/'all-card-platforms/nextgen',out/'all-card-platforms/nextgen/coverage.json']),
            ('full-games',['node','tools/ai/check_full_matches094.js',out/'rules',out/'full-ai-games']),
            ('selected-current92',['node','tools/ai/check_beta_ws_games092.cjs',out/'unfair-checks',out/'rules',out/'selected-profiles-current92.json','92','--mapping',ROOT/'data/beta924/design/beta_ai_profiles093.json'])]:
            cached={'save-safety':'save-safety-check','starter-recovery':'starter-recovery-check'}.get(label)
            if cached and (out/cached/'report.json').exists():
                # Completed fault-injection evidence is immutable on resume.
                saved=json.loads((out/cached/'report.json').read_text('utf8'))
                assert saved['complete'] and not saved['failures'] and saved['profileSourcesFrozen']
                assert saved['snapshotFingerprint']==json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint']
                for name,digest in saved['sources'].items():assert sha(ROOT/name)==digest,name
                print('PASS '+label+' (unchanged completed proof)',flush=True)
            elif label in ('all-card-platforms','classic-all-cards','nextgen-all-cards') and platform_proof(out):
                print('PASS '+label+' (unchanged completed proof)',flush=True)
            elif label=='all-card-platforms' and (out/'all-card-platforms').exists():
                # An incomplete or superseded proof cannot be extended in place: the preparer
                # insists on a fresh directory, so drop it and translate from current sources.
                shutil.rmtree(out/'all-card-platforms');run(out,label,cmd)
            else:run(out,label,cmd)
    finish(out)

if __name__=='__main__':main()
