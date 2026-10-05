"""Freeze native numeric55 and nested manager regressions before development."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value, message):
    if not value: raise RuntimeError(message)

runtime = read(E / 'power-number-runtime-result.json')
log = E / 'native28-editor-20261002-2105.log'
require(runtime['expectedChecksComplete'] and runtime['correctContractKey'] and
    runtime['logSha256'] == sha(log), 'Power acceptance/log mismatch')
manifest = read(E / 'power-number-check-preparation.json')
require(runtime['expectedContractKey'] == manifest['contractKey'], 'Wrong numeric version')
compile_report = read(ROOT / 'BetaGwent/build/board-compile28/result.json')
prep = read(E / 'board-native-preparation.json')
require(prep['compile'] == compile_report and compile_report['exitCode'] == 0 and
    not compile_report['timedOut'] and compile_report['patchSourcesUnchangedDuringCompile'], 'Compile28 association failed')
require(compile_report['patchSourcesBefore'] == compile_report['patchSourcesAfter'], 'Compile inputs changed')
copies = ROOT / 'BetaGwent/build/accepted-board28-sources'
copies.mkdir(exist_ok=True)
sources = []
for item in compile_report['patchSourcesBefore']:
    path = ROOT / 'GwentB/myproject1/workspace/scripts' / item['path']
    require(sha(path) == item['sha256'], 'Active source differs from compile28')
    frozen = copies / path.name
    if frozen.exists(): require(frozen.read_bytes() == path.read_bytes(), 'Frozen source changed')
    else: frozen.write_bytes(path.read_bytes())
    sources.append(dict(name=path.name, sha256=item['sha256'], frozen=str(frozen)))
require(len(sources) == 24, 'Expected sources24')
for resource in prep['resources']:
    require(sha(Path(resource['path'])) == resource['sha256'], 'Resource changed')
for tag, total in (('ACTION', 39), ('APPLY', 20), ('MANAGER', 86)):
    batch = runtime['manager']['batches'][tag]
    require(batch['expectedChecksComplete'] and len(batch['passIds']) == total, 'Batch incomplete: ' + tag)
require(runtime['power']['expectedChecksComplete'] and len(runtime['power']['passIds']) == 55, 'Numeric batch incomplete')
for artifact in compile_report['artifacts']:
    require(sha(Path(artifact['path'])).upper() == artifact['sha256'], 'Compiled blob changed')
report = dict(date='2026-10-02', compile='board-compile28', sourceCount=len(sources), sources=sources,
    resources=prep['resources'], log=str(log), logSha256=sha(log), contractKey=manifest['contractKey'],
    managerContractKey=manifest['managerContractKey'], numericChecksVerified=True,
    queueChecksVerified=True, applyChecksVerified=True, managerChecksVerified=True,
    checks=dict(ACTION=39, APPLY=20, MANAGER=86, POWER=55), modScriptErrors=runtime['modScriptErrors'],
    priorManagerAcceptance=str(E / 'native26-acceptance.json'),
    scope='Native numeric raw final-setter boundary55 and isolated queue39/Apply20/manager86. No real power events, death, armor absorption, full registry or match acceptance.')
(E / 'power-number-runtime-accepted-20261002.json').write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')
(E / 'power-number-runtime-accepted-20261002-trace.txt').write_bytes((E / 'power-number-runtime-trace.txt').read_bytes())
(E / 'native28-acceptance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Accepted native28 ACTION39/APPLY20/MANAGER86/POWER55; exact sources24 and resource hashes frozen.')
