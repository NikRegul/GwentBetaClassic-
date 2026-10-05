"""Freeze version26 manager suite and exact sources before further development."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value, message):
    if not value: raise RuntimeError(message)

runtime = read(E / 'manager-runtime-result.json')
log = E / 'native26-editor-20261002-2026.log'
require(runtime['expectedChecksComplete'] and runtime['correctContractKey'] and
    runtime['logSha256'] == sha(log), 'Manager acceptance/log mismatch')
manifest = read(E / 'manager-check-preparation.json')
require(runtime['expectedContractKey'] == manifest['contractKey'], 'Wrong manager version')
compile_report = read(ROOT / 'BetaGwent/build/board-compile26/result.json')
prep = read(E / 'board-native-preparation.json')
require(prep['compile'] == compile_report and compile_report['exitCode'] == 0 and
    compile_report['patchSourcesUnchangedDuringCompile'], 'Compile26 association failed')
require(compile_report['patchSourcesBefore'] == compile_report['patchSourcesAfter'], 'Compile inputs changed')
copies = ROOT / 'BetaGwent/build/accepted-board26-sources'
copies.mkdir(exist_ok=True)
sources = []
for item in compile_report['patchSourcesBefore']:
    path = ROOT / 'GwentB/myproject1/workspace/scripts' / item['path']
    require(sha(path) == item['sha256'], 'Active source differs from compile26')
    frozen = copies / path.name
    if frozen.exists(): require(frozen.read_bytes() == path.read_bytes(), 'Frozen source changed')
    else: frozen.write_bytes(path.read_bytes())
    sources.append(dict(name=path.name, sha256=item['sha256'], frozen=str(frozen)))
require(len(sources) == 22, 'Expected sources22')
for resource in prep['resources']:
    require(sha(Path(resource['path'])) == resource['sha256'], 'Resource changed')
for tag, total in (('ACTION', 39), ('APPLY', 20), ('MANAGER', 86)):
    batch = runtime['batches'][tag]
    require(batch['expectedChecksComplete'] and len(batch['passIds']) == total, 'Batch incomplete: ' + tag)
for artifact in compile_report['artifacts']:
    require(sha(Path(artifact['path'])).upper() == artifact['sha256'], 'Compiled blob changed')
report = dict(date='2026-10-02', compile='board-compile26', sourceCount=len(sources), sources=sources,
    resources=prep['resources'], log=str(log), logSha256=sha(log), contractKey=manifest['contractKey'],
    queueChecksVerified=True, applyChecksVerified=True, managerChecksVerified=True,
    checks=dict(ACTION=39, APPLY=20, MANAGER=86), modScriptErrors=runtime['modScriptErrors'],
    priorApplyAcceptance=str(E / 'native21-acceptance.json'),
    scope='Native isolated manager policy/driver, mutable authority, queue39/Apply20 regressions. Synthetic services, no real effects/network/clock/cache/full scheduler acceptance.')
(E / 'manager-runtime-accepted-20261002.json').write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')
(E / 'manager-runtime-accepted-20261002-trace.txt').write_bytes((E / 'manager-runtime-trace.txt').read_bytes())
(E / 'native26-acceptance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Accepted native26 ACTION39/APPLY20/MANAGER86; exact sources22 and resource hashes frozen.')
