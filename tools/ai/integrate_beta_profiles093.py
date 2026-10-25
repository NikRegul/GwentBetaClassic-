"""Promote selected profile data only after complete source/typed-WS parity."""
import argparse,datetime,hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',type=Path);p.add_argument('mapping',type=Path);a=p.parse_args()
    mapping=json.loads(a.mapping.read_text('utf8'));games_path=a.stage/'games-parity.json';games=json.loads(games_path.read_text('utf8'))
    assert mapping['validated'] and [x['presetId'] for x in mapping['assignments']]==list(range(21,130))
    assert games['complete'] and not games.get('error') and games['bindingChecks']==109
    assert len(games['records'])==games['total']==len({x['composition'] for x in mapping['assignments']})==92
    assert games['profileScope']=='Validated per-deck named original profiles'
    inputs=json.loads((a.stage/'games-run-inputs.json').read_text('utf8'))
    for name,digest in inputs['inputs'].items():assert sha(Path(name))==digest,name
    manifest=json.loads((a.stage/'ws-stage-manifest.json').read_text('utf8'))
    for name,digest in manifest['sources'].items():assert sha(a.stage/name)==digest,name
    handlers=json.loads((a.stage/'handlers-parity.json').read_text('utf8'));data=json.loads((a.stage/'source-data.json').read_text('utf8'))
    assert data['deckBindings']==mapping['assignments']
    selected={x['profile'] for x in mapping['assignments']}
    assert {x['name'] for x in data['profiles']}==selected and handlers['profiles']==len(selected)==24
    canonical=ROOT/'BetaGwent/development/scripts/game/betagwent';design=ROOT/'data/beta924/design'
    mapping_dest=design/'beta_ai_profiles093.json';parity_dest=design/'beta_ai_profiles093-ws-parity.json';proof_dest=design/'beta_ai_profiles093-source-proof.json'
    assert not any(p.exists() for p in (mapping_dest,parity_dest,proof_dest)),'Never replace previously promoted profile evidence'
    generated=['betaOriginalData.ws','betaOriginalHandlerData.ws','betaOriginalRequestData.ws']
    for name,digest in manifest['sources'].items():
        if name not in generated:assert sha(canonical/name)==digest,'Handwritten WS changed after parity '+name
    board=canonical/'developmentBoardMenu.ws';raw=board.read_bytes()
    old=b'originalPersonality.Initialize(chosen.header.factionMask)';new=b'originalPersonality.InitializeForDeck(enemyPreset,chosen.header.factionMask)'
    assert raw.count(old)==1 and new not in raw
    backup=a.stage/'canonical-before-profile-integration';backup.mkdir()
    for name in generated+['developmentBoardMenu.ws']:shutil.copy2(canonical/name,backup/name)
    for name in generated:shutil.copy2(a.stage/name,canonical/name)
    board.write_bytes(raw.replace(old,new))
    for name,digest in manifest['sources'].items():assert sha(canonical/name)==digest,name
    shutil.copy2(a.mapping,mapping_dest);shutil.copy2(games_path,parity_dest)
    common_manifest=Path(inputs['rules'])/'manifest.json'
    proof=dict(schema=1,promotedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),mappingSha256=sha(mapping_dest),wholeMatchReportSha256=sha(parity_dest),
               wsSources=manifest['sources'],boardSourceSha256=sha(board),handlerChecks=handlers['checks'],selectedProfiles=len(selected),presetBindings=109,wholeMatches=92,
               commonRulesManifestSha256=sha(common_manifest),stageInputs=inputs,scope='Completed selected original profile source/typedWS parity; final integrated regressions and native compilers remain required.',nativeGameplayVerified=False)
    proof_dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(selectedProfiles=len(selected),presetBindings=109,wholeMatches=92,mappingSha256=proof['mappingSha256'],canonicalInitializeForDeck=True)))

if __name__=='__main__':main()
