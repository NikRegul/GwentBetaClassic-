"""Full public0.9.3, including user fixes and current92-deck JS/WS parity.

No installation or publication. --finish-prepared accepts only completed proofs.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))  # build_inputs (also when resuming)
NOTES=ROOT/'docs/releases/0.9.3-public-20261025'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run(out,label,command):
    log=out/'logs'/(label+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf8') as f:subprocess.run([str(x) for x in command],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    print('PASS',label,flush=True)

def collect(out):
    snapshot=json.loads((out/'rules/manifest.json').read_text('utf8'));fingerprint=snapshot['fingerprint']
    sys.path.insert(0,str(ROOT/'tools/ai'));from snapshot import inputs,fingerprint as current_fingerprint
    assert current_fingerprint(inputs())==fingerprint,'Current engine differs from frozen release'
    summary=json.loads((out/'regressions/summary.json').read_text('utf8'));assert len(summary)==94 and all(r['exitCode']==0 for r in summary)
    whole=json.loads((out/'selected-profiles-current92.json').read_text('utf8'))
    assert whole['complete'] and not whole.get('error') and len(whole['records'])==whole['total']==92 and whole['bindingChecks']==109
    assert whole['fingerprint']==fingerprint
    for name,digest in whole['inputDigests'].items():assert sha(Path(name))==digest,name
    assert whole['peakActionsPerCallback']<=1 and not whole['nativeProcessesAllowed']
    for name,count in [('user-ui-check.json',7107),('choice-captions.json',2498),('choice-fates.json',153),('card-offer.json',18),('reveal-classic.json',80),('reveal-leader.json',51),('user-audio-check/report.json',309036)]:
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
    for n,h in expected.items():assert sha(ROOT/'BetaGwent/ui/src'/n)==h,n
    for platform in ['classic','nextgen']:
        menus=json.loads((ui/platform/'menus/menus.json').read_text('utf8'))
        frozen_ui=json.loads((ui/platform/'ui-inputs.json').read_text('utf8'))['sources']
        assert menus['frozenSources']==frozen_ui
        for n,h in frozen_ui.items():assert sha(ui/platform/'ui/src'/n)==h,n
        assert all(sha(Path(m['path']))==m['sha256'] for m in menus['menus'])
    packaged_ui=json.loads((out/'ui-patch/manifest.json').read_text('utf8'))
    assert max(m['bytes'] for p in packaged_ui['platforms'].values() for m in p['menus'])<=65*1024**2
    full=json.loads((out/'full-ai-games/report.json').read_text('utf8'));assert full['complete'] and full['errors']==0 and len(full['games'])==10 and full['fingerprint']==fingerprint
    storage=json.loads((out/'profile-storage-check/report.json').read_text('utf8'))
    assert storage['complete'] and storage['checks']>=1241 and storage['bankChecksumsValidated'] and storage['profileSourcesFrozen']
    assert storage['fingerprint']==fingerprint and not storage['nativeSerializationTested']
    for n,h in storage['sources'].items():assert sha(ROOT/n)==h,n
    delivery=json.loads((out/'profile-native-source-proof-complete.json').read_text('utf8'))
    assert delivery['complete'] and len(delivery['records'])==5
    assert sum(r['classicInjectedMembersVerified'] for r in delivery['records'])==93
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
    files.append('profile-native-source-proof-complete.json')
    files += ['all-card-platforms/'+p+'/'+n for p in ['classic','nextgen'] for n in ['manifest.json','coverage.json']]
    report=dict(complete=True,errors=0,version='0.9.3',fingerprint=fingerprint,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        regressionGroups=94,currentSelectedProfileParityMatches=92,presetBindings=109,newStrengthComparisonConducted=False,
        historicalStrengthEvidence='0.9.3c fixed3680-game trial is preserved separately; current mechanics and target fixes were not part of that trial.',
        reports=[dict(path=n,sha256=sha(out/n)) for n in files],nativeGameplayVerified=False,installed=False,published=False)
    notes=sorted(NOTES.glob('0.9.3_*.md'));assert len(notes)==39
    report['publicationCopy']={p.name:sha(p) for p in notes}
    gate=out/'user-release-checks.json'
    if gate.exists():
        prior=json.loads(gate.read_text('utf8'));report['createdAt']=prior['createdAt']
        assert report==prior,'Completed user-fix proof changed; do not repackage an existing release'
    else:gate.write_text(json.dumps(report,indent=2)+'\n','utf8')

def finish(out):
    collect(out)
    sys.path.insert(0,str(ROOT/'tools/features091'))
    spec=importlib.util.spec_from_file_location('public_package091',ROOT/'tools/features091/build091.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.VERSION='0.9.3'
    os.environ['BETA093_RELEASE_NOTES_DIR']=str(NOTES)
    from build_inputs import AUDIO
    module.package(out,AUDIO)
    run(out,'independent-public-audit',[sys.executable,'-X','utf8','tools/features093/verify093.py',out,'--version','0.9.3','--user-release'])
    audit=json.loads((out/'archive-verification.json').read_text('utf8'))
    ready=dict(version='0.9.3',status='ready',sourceFingerprint=json.loads((out/'rules/manifest.json').read_text('utf8'))['fingerprint'],
        completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),archives=audit['archives'],regressionGroups=94,currentSelectedProfileParityMatches=92,
        publicationCopyLanguages=13,publicationCopyDocuments=39,maxMenuBytes=audit['maxMenuBytes'],classicCompilerPassed=True,nextgenCompilerPassed=True,
        nativeGameplayVerified=False,installed=False,published=False,verifiedReport='archive-verification.json')
    (out/'release-readiness.json').write_text(json.dumps(ready,indent=2)+'\n','utf8');print(json.dumps(ready),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--finish-prepared',action='store_true');p.add_argument('--resume',action='store_true',help='continue a fresh public build whose technical stage stopped');p.add_argument('--reuse-ui-from',type=Path);a=p.parse_args();out=a.out.resolve()
    assert out.is_relative_to(ROOT/'BetaGwent/build') and out!=ROOT/'BetaGwent/build'
    if not a.finish_prepared:
        if a.resume:assert (out/'source-freeze.json').is_file() and not (out/'user-release-checks.json').exists(),'Nothing to resume'
        else:
            assert not out.exists(),'Use a fresh release folder'
            subprocess.run([sys.executable,'-X','utf8','tools/ai/gen_clone.py'],cwd=ROOT,check=True)
            from notes093_public import main as notes;notes()
            subprocess.run([sys.executable,'-X','utf8','tools/features091/build091.py','--out',str(out),'--version','0.9.3','--prepare-only'],cwd=ROOT,check=True)
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
        from build_inputs import AUDIO
        ui=(a.reuse_ui_from.resolve()/'ui-sources') if a.reuse_ui_from else out/'ui-sources'
        run(out,'technical',[sys.executable,'-X','utf8','tools/features091/build091.py','--out',out,'--version','0.9.3','--resume','--skip-package','--native-first','--classic-audio',AUDIO,'--ui-source',ui])
        canonical=json.loads((ui/'gamepad-source.json').read_text('utf8'))
        (out/'ui-selection.json').write_text(json.dumps(dict(source=str(ui),canonical=canonical,reuseAcceptedPatch=False),indent=2)+'\n','utf8')
        for label,cmd in [
            ('user-ui',['node','tools/ai/check_user_ui093.cjs',out/'user-ui-check.json']),
            ('user-fonts',[sys.executable,'-X','utf8','tools/features093/check_user_fonts093.py',out/'user-font-check.json']),
            ('choice-captions',['node','tools/ai/check_choice_captions093.cjs',out/'choice-captions.json']),
            ('choice-fates',['node','tools/ai/check_choice_fates093.cjs',out/'rules',out/'choice-fates.json']),
            ('card-offer',['node','tools/ai/check_card_offer093.cjs',out/'rules',out/'card-offer.json']),
            ('classic-reveal',['node','tools/ai/check_reveal_classic093.cjs',out/'rules',out/'reveal-classic.json']),
            ('leader-reveal',['node','tools/ai/check_reveal_leader093.cjs',out/'rules',out/'reveal-leader.json']),
            ('audio',[sys.executable,'-X','utf8','tools/features093/check_multivoice_user093.py',out/'rules/sources/BetaGwent/development/scripts/game/betagwent/duelAudioCatalog.ws',out/'user-audio-check','--snapshot',out/'rules']),
            ('profile-storage',[sys.executable,'-X','utf8','tools/ai/check_deck_recovery198.py',out/'rules',out/'profile-storage-check','--release']),
            ('profile-delivery',[sys.executable,'-X','utf8','tools/ai/check_prepared_profiles198.py',out,out/'profile-native-source-proof-complete.json']),
            ('all-card-platforms',[sys.executable,'-X','utf8','tools/ai/prepare_platform_rules198.py',out,out/'rules',out/'all-card-platforms']),
            ('classic-all-cards',['node','tools/ai/check_all_cards198.cjs',out/'all-card-platforms/classic',out/'all-card-platforms/classic/coverage.json']),
            ('nextgen-all-cards',['node','tools/ai/check_all_cards198.cjs',out/'all-card-platforms/nextgen',out/'all-card-platforms/nextgen/coverage.json']),
            ('full-games',['node','tools/ai/check_full_matches094.js',out/'rules',out/'full-ai-games']),
            ('selected-current92',['node','tools/ai/check_beta_ws_games092.cjs',out/'unfair-checks',out/'rules',out/'selected-profiles-current92.json','92','--mapping',ROOT/'data/beta924/design/beta_ai_profiles093.json'])]:run(out,label,cmd)
    finish(out)

if __name__=='__main__':main()
