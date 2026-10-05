"""Freeze direct Apply20 acceptance and the exact compile21 source set."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
runtime = read(E / 'apply-runtime-result.json')
log = E / 'native21-editor-20261002-1708.log'
if not runtime['expectedChecksComplete'] or runtime['logSha256'] != sha(log):
    raise RuntimeError('Apply acceptance/log mismatch')
compile_report = read(ROOT / 'BetaGwent/build/board-compile21/result.json')
prep = read(E / 'board-native-preparation.json')
if prep['compile'] != compile_report:
    raise RuntimeError('Expected compile21 preparation before mutation')
copies = ROOT / 'BetaGwent/build/accepted-board21-sources'
copies.mkdir(exist_ok=True)
sources = []
for item in compile_report['patchSourcesBefore']:
    path = ROOT / 'GwentB/myproject1/workspace/scripts' / item['path']
    if sha(path) != item['sha256']: raise RuntimeError('Active source differs from accepted compile21')
    frozen = copies / path.name
    frozen.write_bytes(path.read_bytes())
    sources.append(dict(name=path.name, sha256=item['sha256'], frozen=str(frozen)))
resources = []
for item in prep['resources']:
    if sha(Path(item['path'])) != item['sha256']: raise RuntimeError('Resource changed since preparation21')
    resources.append(item)
(E / 'apply-runtime-accepted-20261002.json').write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')
(E / 'apply-runtime-accepted-20261002-trace.txt').write_bytes((E / 'apply-runtime-trace.txt').read_bytes())
report = dict(date='2026-10-02', compile='board-compile21', sourceCount=len(sources), sources=sources,
    resources=resources, log=str(log), logSha256=sha(log), applyChecksVerified=True,
    summary=runtime['summary'], modScriptErrors=runtime['modScriptErrors'],
    priorQueueAndLiveUIAcceptance=str(E / 'native20-acceptance.json'),
    scope='Native direct Apply20. No manager/effect/scheduler acceptance inferred.')
(E / 'native21-acceptance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
development = read(E / 'apply-development-result.json')
development.update(nativeApplyChecksVerified=True, runtimeAcceptance=str(E / 'native21-acceptance.json'),
    nextManualStep='Direct Apply20 accepted. No repeat required until dependencies change.')
(E / 'apply-development-result.json').write_text(json.dumps(development, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Accepted native APPLY20, compile21 sources20 and resource hashes frozen.')
