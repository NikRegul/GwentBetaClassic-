"""Freeze the observed board20 run, with unrelated engine diagnostics retained."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'
def read(name):
    return json.loads((E / name).read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
action = read('action-runtime-accepted-20261002.json')
board = read('board20-runtime-accepted-20261002.json')
log = E / 'native20-editor-20261002-1309.log'
raw = log.read_bytes()
if not action['expectedChecksComplete'] or not board['expectedChecksComplete']:
    raise RuntimeError('Native check acceptance failed')
if sha(log) != action['logSha256'] or sha(log) != board['sha256']:
    raise RuntimeError('Frozen log does not match captured run')
compile_report = json.loads((ROOT / 'BetaGwent/build/board-compile20/result.json').read_text())
sources = []
for item in compile_report['patchSourcesBefore']:
    name = Path(item['path']).name
    active = ROOT / 'GwentB/myproject1/workspace/scripts' / item['path']
    frozen = ROOT / 'BetaGwent/build/accepted-board20-sources' / name
    if sha(active) != item['sha256'] or sha(frozen) != item['sha256']:
        raise RuntimeError('Accepted source changed: ' + name)
    sources.append(dict(name=name, sha256=item['sha256'], frozen=str(frozen)))
events = board['requestFlowEvents']
live = [line for line in events if re.search(r'REQUEST_FLOW_(BEGIN|SELECT|END|ABORT) ', line)]
ids = sorted({int(m.group(1)) for line in live if (m := re.search(r'REQUEST_FLOW_BEGIN id=(\d+)', line))})
observed = {}
for request_id in ids:
    prefix = f'id={request_id} '
    subset = [line for line in live if prefix in line or line.endswith(f'id={request_id}')]
    observed[str(request_id)] = subset
errors = [line for line in raw.decode('utf-8', errors='replace').splitlines() if '[Error]' in line]
report = dict(acceptedDate='2026-10-02', log=str(log), logSha256=sha(log),
    compile='board-compile20', sources=sources,
    actionChecks=action['summary'], boardChecks=board['checkSummaries'],
    actionChecksVerified=True, boardAssertionsVerified=True, liveRequestEvents=observed,
    liveChoicesObserved=any('REQUEST_FLOW_BEGIN' in line and 'kind=1' in line for line in live),
    liveTargetsObserved=any('REQUEST_FLOW_BEGIN' in line and 'kind=2' in line for line in live),
    liveAbortObserved=any('REQUEST_FLOW_ABORT' in line for line in live),
    boardClosed=board['nativeClosed'], revisionIncreasing=board['revisionIncreasing'],
    visualAndManualChecks='User reports all commands completed and working; individual toggle/Esc/reopen gestures are not separately proven by this trace.',
    engineErrorLines=errors,
    engineDiagnosticsNote='Audio/RedIO/HUD/native movableRepresentation assertions remain. No BetaGwent errors or native bridge failure observed; this is not an error-free editor log.',
    duplicateActionBegin=raw.count(b'ACTION_CHECK_BEGIN schema=1 fixture=queue39') == 2,
    scope='Queue39 and isolated CORE116/BOARD104/REQUEST123/FLOW43, plus live synthetic DEV choices/targets. No canonical effects or full scheduler acceptance.')
(E / 'native20-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
development = read('action-queue-development-result.json')
development.update(nativeActionChecksVerified=True, nativeInteractiveRequestIntentsObserved=True,
    runtimeAcceptance=str(E / 'native20-acceptance.json'),
    nextManualStep='No repeat of accepted queue39 required. Production ApplyAction/effects are the next implementation slice.')
(E / 'action-queue-development-result.json').write_text(json.dumps(development, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Accepted ACTION39 and board checks; live requests {ids}; sources {len(sources)} frozen.')
