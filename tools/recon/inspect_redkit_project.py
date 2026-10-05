"""Capture actual REDkit project/depot and supervised compilation evidence."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'GwentB/myproject1'
INSTALLED = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit/r4data')

def fingerprint(path):
    return {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest().upper()}

project_file = PROJECT / 'myproject1.w3edit'
depot_info = ROOT / 'depot/depot_info.json'
depot = json.loads(depot_info.read_text(encoding='utf-8-sig'))
lookups = []
for relative in ['scripts/game/player/r4Player.ws',
                 'gameplay/gui_new/swf/gwint/gwint_game.swf',
                 'quests/sidequests/novigrad/sq306_maverick.w2phase']:
    lookups.append({'relative': relative, 'installedR4data': (INSTALLED / relative).is_file(),
                    'userDepot': (ROOT / 'depot' / relative).is_file()})
builds = []
for report in sorted((PROJECT / 'build').glob('capability-*/result.json')):
    result = json.loads(report.read_text(encoding='utf-8'))
    log_path = report.parent / 'wcc.log'
    log = log_path.read_text(encoding='utf-8', errors='replace') if log_path.is_file() else ''
    result['report'] = str(report)
    result['compilerErrors'] = [s for s in log.splitlines() if '[Error][WCC]' in s]
    result['compileConfirmed'] = (result['exitCode'] == 0 and not result['timedOut']
                                  and bool(result['artifacts'])
                                  and 'Success! Patch scripts blob saved' in log
                                  and not result['compilerErrors'])
    if log_path.is_file():
        result['log'] = fingerprint(log_path)
    builds.append(result)
runtime_result = ROOT / 'docs/evidence/capability-runtime-result.json'
runtime_status = json.loads(runtime_result.read_text(encoding='utf-8')) if runtime_result.is_file() else None
report = {'project': fingerprint(project_file),
          'projectMetadata': json.loads(project_file.read_text(encoding='utf-8-sig')),
          'workspace': str(PROJECT / 'workspace'),
          'depotManifest': {**fingerprint(depot_info), 'version': depot['version'],
                            'fileRecords': len(depot['files'])},
          'resourceLookup': lookups,
          'probeSourceAtCapture': fingerprint(PROJECT / 'workspace/scripts/game/betagwent/capabilityProbe.ws'),
          'builds': builds,
          'runtimeResult': runtime_status,
          'runtimeVerification': 'See runtimeResult for observed versus human-reported checks.' if runtime_status else 'Not yet tested',
          'newSwfAuthoringVerified': False,
          'note': 'User reported depot ready. Manifest presence is not a full editor Depot-is-valid audit. Installed r4data and user depot form separate layers.'}
output = ROOT / 'docs/evidence/redkit-project.json'
output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'project': str(project_file), 'depotRecords': len(depot['files']),
                  'confirmedBuilds': [Path(b['report']).parent.name for b in builds if b['compileConfirmed']]}, ensure_ascii=False))
