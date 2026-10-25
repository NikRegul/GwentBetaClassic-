"""Build the requested 0.9.3 release with the separate original Beta difficulty."""
from pathlib import Path
import hashlib,importlib.util,json

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release092_pipeline', ROOT/'tools/features092/build092.py')
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)
pipeline.VERSION = '0.9.3'
pipeline.LATEST = ROOT/'BetaGwent/build/release093-latest.json'
base_preflight=pipeline.preflight

def selected_profiles_preflight():
    base_preflight()
    design=ROOT/'data/beta924/design'
    mapping_path=design/'beta_ai_profiles093.json';parity_path=design/'beta_ai_profiles093-ws-parity.json'
    mapping=json.loads(mapping_path.read_text('utf8'));parity=json.loads(parity_path.read_text('utf8'))
    proof=json.loads((design/'beta_ai_profiles093-source-proof.json').read_text('utf8'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert mapping['validated'] and proof['mappingSha256']==sha(mapping_path)
    assert parity['complete'] and not parity.get('error') and proof['wholeMatchReportSha256']==sha(parity_path)
    assert len(parity['records'])==len({x['composition'] for x in mapping['assignments']})==92
    assert parity['bindingChecks']==len(mapping['assignments'])==109
    canonical=ROOT/'BetaGwent/development/scripts/game/betagwent'
    for name,digest in proof['wsSources'].items():assert sha(canonical/name)==digest,name
    assert 'originalPersonality.InitializeForDeck(enemyPreset,chosen.header.factionMask)' in (canonical/'developmentBoardMenu.ws').read_text('utf8')
    print('Selected original profiles: completed92 whole-match parity and109 native-source bindings found.',flush=True)

pipeline.preflight=selected_profiles_preflight

if __name__ == '__main__':
    pipeline.main()
