"""Check the actual integrated release policy, board wiring and saved rotation."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser();p.add_argument('build',type=Path);a=p.parse_args();out=a.build/'unfair-checks';out.mkdir(exist_ok=True)
    h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    frozen=a.build/'rules/sources/BetaGwent/development/scripts/game/betagwent'
    canonical=ROOT/'BetaGwent/development/scripts/game/betagwent'
    for name in ['developmentBoardMenu.ws','deckProfile.ws','opponentRotation.ws']+[p.name for p in sorted(canonical.glob('betaOriginal*.ws'))]:
        assert h(frozen/name)==h(ROOT/'BetaGwent/development/scripts/game/betagwent'/name),name
    design=ROOT/'data/beta924/design'
    mapping_path=design/'beta_ai_profiles093.json'
    parity_path=design/'beta_ai_profiles093-ws-parity.json'
    proof_path=design/'beta_ai_profiles093-source-proof.json'
    mapping=json.loads(mapping_path.read_text('utf8'));parity=json.loads(parity_path.read_text('utf8'));proof=json.loads(proof_path.read_text('utf8'))
    assert mapping['validated'] and [x['presetId'] for x in mapping['assignments']]==list(range(21,130))
    assert proof['mappingSha256']==h(mapping_path) and proof['wholeMatchReportSha256']==h(parity_path)
    assert parity['complete'] and not parity.get('error') and parity['bindingChecks']==len(mapping['assignments'])
    assert len(parity['records'])==len({x['composition'] for x in mapping['assignments']})==parity['total']
    assert parity['profileScope']=='Validated per-deck named original profiles'
    for name,digest in proof['wsSources'].items():assert h(frozen/name)==digest,'Selected WS provenance '+name
    assert 'originalPersonality.InitializeForDeck(enemyPreset,chosen.header.factionMask)' in (frozen/'developmentBoardMenu.ws').read_text('utf8')
    for source,name in [(mapping_path,'profile-mapping.json'),(parity_path,'profile-ws-parity.json'),(proof_path,'profile-source-proof.json')]:shutil.copy2(source,out/name)
    frozen_mapping=out/'profile-mapping.json'
    commands=[['node','tools/ai/check_aim_choices093.cjs'],
              ['node','tools/ai/check_unfair_ui093.cjs'],
              ['node','tools/ai/check_playtest_ui093.cjs'],
              ['node','tools/ai/check_deck_difficulty093b.cjs',out/'deck-difficulty.json'],
              [sys.executable,'-X','utf8','tools/ai/compile_unfair_board093.py',out/'board'],
              ['node','tools/ai/check_unfair_board093.cjs',a.build/'rules',out/'board'],
              [sys.executable,'-X','utf8','tools/ai/check_rotation123.py',a.build/'rules'],
              ['node','tools/ai/check_drypass_weather093.cjs',a.build/'rules'],
              ['node','tools/ai/check_beta_ws_actions092.cjs',out,a.build/'rules',out/'actions.json'],
              ['node','tools/ai/check_beta_ws_games092.cjs',out,a.build/'rules',out/'games.json','5','--mapping',frozen_mapping]]
    records=[]
    for i,cmd in enumerate(commands):
        log=out/f'{i:02d}.log'
        with log.open('w',encoding='utf8') as f:
            subprocess.run([str(x) for x in cmd],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
        records.append(dict(command=[str(x) for x in cmd],log=log.name,sha256=h(log)))
        print('PASS',cmd[1],flush=True)
    games=json.loads((out/'games.json').read_text('utf8'));assert games['complete'] and len(games['records'])==5
    board=json.loads((out/'board/report.json').read_text('utf8'));assert board['selectedProfileStartCases']==3
    assert games['mappingPresets']==109 and games['bindingChecks']==109
    report=dict(fingerprint=json.loads((a.build/'rules/manifest.json').read_text('utf8'))['fingerprint'],checks=records,wholeMatches=5,selectedProfileWholeMatches=parity['total'],presetBindings=109,
                selectedProfiles=len({x['profile'] for x in mapping['assignments']}),profileMappingSha256=h(frozen_mapping),profileParitySha256=h(out/'profile-ws-parity.json'),profileSourceProofSha256=h(out/'profile-source-proof.json'),errors=0,nativeGameplayVerified=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n','utf8')

if __name__=='__main__':main()
