"""Independent read-only SHA/CRC/profile/native evidence audit of final093."""
from pathlib import Path,PurePosixPath
import argparse,binascii,datetime,hashlib,json,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import CLASSIC_RUNTIME

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--version',choices=['0.9.3','0.9.3a','0.9.3b','0.9.3c'],default='0.9.3');p.add_argument('--user-release',action='store_true');a=p.parse_args();out=a.build.resolve();version=a.version
    if a.user_release:assert version=='0.9.3'
    destination=out/'archive-verification.json';assert not destination.exists(),'Do not overwrite a previous verification'
    release=json.loads((out/'release.json').read_text('utf8'));assert release['version']==version and len(release['archives'])==2
    ordinary_ai=None
    if version in ('0.9.3a','0.9.3b','0.9.3c') or a.user_release:
        snapshot=json.loads((out/'rules/manifest.json').read_text('utf8'))
        for name,digest in snapshot['snapshotFiles'].items():assert sha(out/'rules'/name)==digest,'Modified snapshot '+name
        regressions=json.loads((out/'regressions/summary.json').read_text('utf8'))
        expected_groups=json.loads((out/'user-release-checks.json').read_text('utf8'))['regressionGroups'] if a.user_release else {'0.9.3a':82,'0.9.3b':83,'0.9.3c':85}[version]
        if a.user_release:assert expected_groups in [87,90,92,93,94]
        assert len(regressions)==len({r['name'] for r in regressions})==expected_groups and all(r['exitCode']==0 for r in regressions)
        required=['check_reply_pass094','check_exhausted_frontier094','check_draw_frontier094','check_chase_budget093a']
        if version in ('0.9.3b','0.9.3c') or a.user_release:required.append('check_lock_resilience093b')
        if version=='0.9.3c' or a.user_release:required+=['check_plans093c','check_four_card093c']
        assert set(required)<={r['name'] for r in regressions}
        targeted={}
        for name in required:
            data=json.loads((out/'regressions'/(name+'.json')).read_text('utf8'))
            assert data['fingerprint']==snapshot['fingerprint'] and not data['failures']
            if name!='check_lock_resilience093b':assert data.get('peakActions',data.get('peakPlays'))==1
            targeted[name]=data['checks']
        assert sum(targeted.values())==(7508 if a.user_release else {'0.9.3a':3136,'0.9.3b':3429,'0.9.3c':7508}[version])
        tactics=json.loads((out/'tactics-all/report.json').read_text('utf8'))
        rows=json.loads((out/'rows-all/report.json').read_text('utf8'))
        varied=json.loads((out/'varied/summary.json').read_text('utf8'))
        assert all(data['fingerprint']==snapshot['fingerprint'] for data in [tactics,rows,varied])
        assert tactics['failed']==0 and len(tactics['results'])==1426
        assert len(rows['results'])==414 and all(r['pass'] for r in rows['results'])
        assert varied['cases']==5632 and varied['failed']==0
        full=json.loads((out/'full-ai-games/report.json').read_text('utf8'))
        assert full['complete'] and full['errors']==0 and len(full['games'])==full['planned']==10
        assert full['fingerprint']==snapshot['fingerprint'] and full['planSha256']==sha(out/'full-ai-games/plan.json')
        assert all(g['winner'] in [1,2,3] and not g.get('error') for g in full['games'])
        ordinary_ai=dict(fingerprint=snapshot['fingerprint'],regressionGroups=expected_groups,targetedChecks=targeted,tactics=1426,rowChoices=414,variedPositions=5632,fullTechnicalGames=10,errors=0,strengthGainEstablished=False)
        if a.user_release:
            if expected_groups>=90:
                for name,count in [('check_ambush_hyp094b',427),('check_ambush_decision094b',11),('check_ambush_pairs094b',30)]:
                    data=json.loads((out/'regressions'/(name+'.json')).read_text('utf8'))
                    assert data['fingerprint']==snapshot['fingerprint'] and data['checks']==count and not data['failures']
                    targeted[name]=count
                assert json.loads((out/'regressions/check_ambush_hyp094b.json').read_text('utf8'))['peakActions']==1
            for name,count in [('check_user_targets093',80),('check_reveal_strategy093',48)]:
                data=json.loads((out/'regressions'/(name+'.json')).read_text('utf8'))
                assert data['checks']==count and not data['failures'] and data['fingerprint']==snapshot['fingerprint']
                targeted[name]=count
            if expected_groups>=94:
                for name,count in [('check_special_target_mode197',16),('check_kayran_miruna197',10),('check_cyclops_swordsman197',11),('check_stored_damage198',45)]:
                    data=json.loads((out/'regressions'/(name+'.json')).read_text('utf8'))
                    assert data['checks']==count and data['actualWitcherScript'],name
                    targeted[name]=count
            evidence=json.loads((out/'user-release-checks.json').read_text('utf8'))
            assert evidence['complete'] and evidence['fingerprint']==snapshot['fingerprint'] and evidence['errors']==0
            assert evidence['newStrengthComparisonConducted']==False
            storage=json.loads((out/'profile-storage-check/report.json').read_text('utf8'))
            assert storage['complete'] and storage['checks']>=1241 and storage['bankChecksumsValidated'] and storage['profileSourcesFrozen']
            assert storage['fingerprint']==snapshot['fingerprint'] and not storage['nativeSerializationTested']
            for name,digest in storage['sources'].items():assert sha(ROOT/name)==digest,name
            for platform in ['classic','nextgen']:
                platform_root=out/'all-card-platforms'/platform
                matrix=json.loads((platform_root/'coverage.json').read_text('utf8'));native_inputs=json.loads((platform_root/'manifest.json').read_text('utf8'))
                assert matrix['complete'] and not matrix['failures'] and matrix['testedCards']==matrix['cards']==511
                assert len(matrix['records'])==4088 and all(row['ok'] for row in matrix['records'])
                assert len(matrix['rareCases'])==24 and all(row['ok'] for row in matrix['rareCases'])
                assert matrix['actualNativeResultDispatch'] and not matrix['nativeGameplayExecuted']
                assert matrix['fingerprint']==native_inputs['fingerprint'] and matrix['checkerSha256']==sha(ROOT/'tools/ai/check_all_cards198.cjs')
                for name,digest in native_inputs['sourceInputs'].items():assert sha(Path(name))==digest,name
            for item in evidence['reports']:
                assert sha(out/item['path'])==item['sha256']
            audio=json.loads((out/'user-audio-check/report.json').read_text('utf8'))
            assert audio['checks']==309036 and audio['templates']==539
            voices=audio['actualClassicBankCoverage']
            assert len(voices)==5 and all(v['missing']==0 and v['voiceEventsChecked']==881 for v in voices)
            assert json.loads((out/'user-ui-check.json').read_text('utf8'))['checks']==7107
            captions=json.loads((out/'choice-captions.json').read_text('utf8'))
            assert captions['checks']==2498 and len(captions['records'])==2 and len(captions['captioned'])==21
            fates=json.loads((out/'choice-fates.json').read_text('utf8'))
            assert fates['checks']==153 and fates['fingerprint']==snapshot['fingerprint'] and len(fates['records'])==20
            assert json.loads((out/'card-offer.json').read_text('utf8'))['checks']==18
            reveal=json.loads((out/'reveal-classic.json').read_text('utf8'))
            assert reveal['fingerprint']==snapshot['fingerprint'] and reveal['ordinaryPolicySelectorsAllowed']==False
            assert len(reveal['records'])==4 and all(r['golemsDeployed']==r['enemyCardsRevealed'] for r in reveal['records'])
            leader=json.loads((out/'reveal-leader.json').read_text('utf8'))
            assert leader['fingerprint']==snapshot['fingerprint'] and leader['checks']==51 and len(leader['records'])==11
            assert all(r['reveals']==4 and r['golems']==3 for r in leader['records'])
        if version in ('0.9.3b','0.9.3c') or a.user_release:
            visible=json.loads((out/'unfair-checks/deck-difficulty.json').read_text('utf8'))
            assert visible['checks']==89 and not visible['failures'] and len(visible['cases'])==10
            selection=json.loads((out/'ui-selection.json').read_text('utf8'))
            ui_root=out/'ui-sources'
            if a.user_release:
                ui_root=Path(selection['source'])
                if not ui_root.is_relative_to(out):
                    reuse=json.loads((out/'ui-reuse-proof.json').read_text('utf8'));prior=Path(reuse['source']);assert ui_root==prior/'ui-sources'
                    assert prior.is_relative_to(ROOT/'BetaGwent/build') and reuse['canonical']==selection['canonical']
                    assert sha(prior/'ui-patch/manifest.json')==reuse['patchManifestSha256']
                    assert sha(out/'scripts/game/betagwent/developmentBoardMenu.ws')==reuse['boardBridgeSha256']
            if version=='0.9.3c':
                ui_root=Path(selection['source'])
                if ui_root!=out/'ui-sources':
                    reuse=json.loads((out/'ui-reuse-proof.json').read_text('utf8'));accepted_ui=Path(reuse['source'])
                    assert reuse['identicalCurrentSources'] and reuse['reusedCompiledMenus'] and reuse['canonical']==selection['canonical']
                    assert sha(accepted_ui/'archive-verification.json')==reuse['archiveVerificationSha256']
                    assert sha(accepted_ui/'ui-patch/manifest.json')==reuse['patchManifestSha256']
                    assert ui_root==accepted_ui/'ui-sources'
            prepared_sources=json.loads((ui_root/'gamepad-source.json').read_text('utf8'))
            assert selection['canonical']==prepared_sources
            for name,digest in prepared_sources.items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest
            if a.user_release:assert 'BetaGwentReleaseText093.as' in prepared_sources
            folders=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
            for platform,source in [('nextgen',ROOT/'BetaGwent/ui/src/BetaGwentBoard.as'),('classic',ROOT/'tools/features091/BetaGwentBoard_classic093.as')]:
                raws=[(ui_root/platform/'ui'/f/'BetaGwentBoard.as').read_bytes() for f in folders]
                assert all(raw==raws[0] and raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'') for raw in raws)
                assert raws[0].decode('utf-8-sig').replace('\r\n','\n')==source.read_text('utf-8-sig')
                native_menus=json.loads((ui_root/platform/'menus/menus.json').read_text('utf8'))
                pinned_ui=json.loads((ui_root/platform/'ui-inputs.json').read_text('utf8'))
                assert native_menus['frozenSources']==pinned_ui['sources']
                for name,digest in pinned_ui['sources'].items():assert sha(ui_root/platform/'ui/src'/name)==digest
                assert not native_menus['canonicalSourcesModified'] and len(native_menus['menus'])==4
                for menu in native_menus['menus']:
                    assert sha(Path(menu['path']))==menu['sha256']
            ordinary_ai['deckDifficultyVisibilityChecks']=89
            if a.user_release:
                whole=json.loads((out/'selected-profiles-current92.json').read_text('utf8'))
                assert whole['complete'] and not whole.get('error') and whole['total']==len(whole['records'])==92 and whole['bindingChecks']==109
                if expected_groups>=90:
                    assert whole['fingerprint']==snapshot['fingerprint']
                    for name,digest in whole['inputDigests'].items():assert sha(Path(name))==digest
                assert whole['peakActionsPerCallback']<=1 and whole['nativeProcessesAllowed']==False
                ordinary_ai['currentSelectedProfileParityMatches']=92
    gate=json.loads((out/'unfair-checks/report.json').read_text('utf8'));assert gate['errors']==0 and gate['presetBindings']==109 and gate['selectedProfileWholeMatches']==92
    expected=release['originalBetaAI'];assert expected['namedProfiles']==24 and expected['presetBindings']==109
    assert expected['actualHandVisible'] and expected['actualDeckVisible'] and not expected['globallyStrongestProfileEstablished']
    mapping_path=out/'unfair-checks/profile-mapping.json';assert sha(mapping_path)==expected['mappingSha256']==gate['profileMappingSha256']
    mapping=json.loads(mapping_path.read_text('utf8'));assert mapping['validated'] and len(mapping['assignments'])==109
    nextgen=json.loads((out/'compile-nextgen-final/result.json').read_text('utf8'))
    assert nextgen['exitCode']==0 and nextgen['completedByOutput'] and nextgen['patchSourcesUnchangedDuringCompile']
    blob=out/'compile-nextgen-final/compiled/blob.rsblob';assert sha(blob)==nextgen['artifacts'][0]['sha256']
    classic_path=out/'classic-compile.json'
    if not classic_path.exists():classic_path=CLASSIC_RUNTIME/'runs'/out.name/'result.json'
    classic=json.loads(classic_path.read_text('utf8'));assert classic['compilePassed'] and not classic['errors'] and not classic['timedOut']
    assert classic['preparationManifestSha256']==sha(out/'classic-prepared-final/preparation.json')
    ui=json.loads((out/'ui-patch/manifest.json').read_text('utf8'));menus=[m['bytes'] for platform in ui['platforms'].values() for m in platform['menus']]
    assert menus and max(menus)<65*1024**2
    board_sources=[(ROOT/'BetaGwent/ui'/directory/'BetaGwentBoard.as').read_bytes() for directory in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']]
    assert all(raw==board_sources[0] and raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'') for raw in board_sources)
    records=[]
    accepted_hard=None
    if version=='0.9.3c':
        proof_path=ROOT/'data/beta924/design/ai093c_validation.json';accepted_hard=json.loads(proof_path.read_text('utf8'));holdout=accepted_hard['holdout']
        assert accepted_hard['accepted'] and accepted_hard['candidateFingerprint']==snapshot['fingerprint']
        assert accepted_hard['sourceFiles']==snapshot['files']
        assert holdout['games']==3680 and holdout['poolSize']==92 and holdout['errors']==0 and holdout['lower99']>.5 and holdout['clusterLower99']>.5
        assert sum(holdout[k] for k in ['wins','losses','draws'])==3680
        control=accepted_hard['negativeControl'];negative=control['result']
        assert sha(Path(control['path']))==control['sha256']
        assert json.loads(Path(control['path']).read_text('utf8'))==negative
        assert negative['complete'] and negative['passed'] and negative['candidateFingerprint']==snapshot['fingerprint']
        assert negative['games']==368 and negative['blocks']==92 and negative['scoreRate']==.5 and negative['errors']==0 and negative['everyMirroredPolicySwapCancels']
        assert release['hardAI']['validationSha256']==sha(proof_path)
        sys.path.insert(0,str(ROOT/'tools/ai'));from audit_policy093c import audit as audit_policy
        assert audit_policy(out/'rules',Path(accepted_hard['baselineSnapshot']))==accepted_hard['policySourceAudit']
        witness=accepted_hard['qualitativeWitness']
        assert sha(ROOT/'tools/ai/check_witness093c.cjs')==witness['toolSha256']
        assert sha(ROOT/'tools/ai/fixtures/four-card-tutor093c.json.gz')==witness['fixtureSha256']
        assert witness['result']['candidateFingerprint']==snapshot['fingerprint']
        assert [r['result']['winner'] for r in witness['result']['records']]==[1,2]
        ordinary_ai['strengthGainEstablished']=True
        ordinary_ai['strengthEvidenceScope']='Fixed 3680-game paired stand comparison against 0.9.3b on 92 compositions; no universal or retail gameplay claim.'
    for archive in release['archives']:
        file=Path(archive['path']);assert sha(file)==archive['sha256'];assert file.stat().st_size==archive['bytes']
        with zipfile.ZipFile(file) as z:
            names=z.namelist();assert len(names)==len({n.lower() for n in names})
            assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n for n in names)
            manifest_name=f'manifest-{version}.json';manifest=json.loads(z.read(manifest_name));assert manifest['version']==version
            assert manifest['originalBetaAI']==expected
            if accepted_hard:
                assert manifest['hardAI']==release['hardAI']
                validation=z.read(f'BetaGwentDocs/AI_Validation_{version}.json')
                assert hashlib.sha256(validation).hexdigest()==release['hardAI']['validationSha256'] and json.loads(validation)==accepted_hard
            declared={r['path']:r for r in manifest['files']};assert len(declared)==len(manifest['files']) and set(declared)==set(names)-{manifest_name}
            checked_bytes=0
            for name,row in declared.items():
                digest=hashlib.sha256();crc=0;size=0
                with z.open(name) as stream:
                    while chunk:=stream.read(1024*1024):digest.update(chunk);crc=binascii.crc32(chunk,crc);size+=len(chunk)
                assert digest.hexdigest()==row['sha256'] and size==row['bytes'],name
                assert (crc&0xffffffff)==z.getinfo(name).CRC,name
                checked_bytes+=size
            raw=z.read(f'BetaGwentDocs/AI_Profile_Mapping_{version}.json');assert hashlib.sha256(raw).hexdigest()==expected['mappingSha256']
            if a.user_release:
                assert hashlib.sha256(z.read('BetaGwentDocs/UserFixes_0.9.3.json')).hexdigest()==sha(out/'user-release-checks.json')
                for code in ['RU','EN','DE','FR','IT','PL','ES','ES_MX','PT_BR','JA','KO','ZH_CN','ZH_TW']:
                    for kind in ['DESCRIPTION','POST','CHANGELOG']:
                        name=f'0.9.3_{kind}_{code}.md';assert hashlib.sha256(z.read('BetaGwentDocs/'+name)).hexdigest()==manifest['releaseNotes'][name]
            assert json.loads(raw)==mapping
            parity=z.read(f'BetaGwentDocs/AI_Profile_Parity_{version}.json');assert hashlib.sha256(parity).hexdigest()==gate['profileParitySha256']
            build_info=json.loads(z.read('BetaGwentDocs/BuildInfo.json'));assert build_info['originalBetaAI']==expected
            if accepted_hard:assert build_info['hardAI']==release['hardAI']
            if '5.0+' in file.name:assert hashlib.sha256(z.read('Mods/modBetaGwent0924/content/precompiled.rsblob')).hexdigest()==sha(blob)
            records.append(dict(path=str(file),sha256=archive['sha256'],files=len(names),bytes=archive['bytes'],allDeclaredFilesSha256AndCrcPassed=True,uncompressedBytesChecked=checked_bytes,selectedProfileMetadataPassed=True))
    report=dict(version=version,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),archives=records,originalBetaAI=expected,
                classicCompilerPassed=True,nextgenCompilerPassed=True,maxMenuBytes=max(menus),fiveIdenticalBomCrlfCopies=True,installed=False,published=False,nativeGameplayVerified=False)
    if ordinary_ai:report['ordinaryAI']=ordinary_ai
    if accepted_hard:report['hardAI']=release['hardAI']
    destination.write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))

if __name__=='__main__':main()
