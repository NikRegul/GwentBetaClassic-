"""Capture the latest development-board session from editor.log, read-only.

Logs verify native callbacks/script results, not visible rendering or restored
Geralt controls. Those two observations must come from the person testing.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\editor.log')
MARKER = re.compile(r'\b(?:BOARD_(?:OPEN|CONFIGURED|INTENT|VIEW|CLOSED|MISSING|REJECT|STATE|CHECK)|CORE_CHECK_|REQUEST_CHECK_|FLOW_CHECK_|REQUEST_FLOW_)')
VIEW = re.compile(r'BOARD_VIEW revision=(\d+) round=(\d+) current=(\d+) score=(\d+):(\d+) flags=(\d+)')
SUMMARY = re.compile(r'(CORE|BOARD|REQUEST|FLOW)_CHECK_DONE checks=(\d+) passed=(\d+) failed=(\d+)')
BRIDGE_ERROR = re.compile(r'CallGameEvent: Function must be bound to a Flash DisplayObject before calling\.|flashMovieAdapter\.cpp.*flashThis\.IsFlashDisplayObject')


def parse_runtime(raw, log_name, expected_counts=None):
    lines = raw.decode('utf-8', errors='replace').splitlines()
    starts = [i for i, line in enumerate(lines) if 'BOARD_OPEN_REQUEST name=BetaGwentBoard' in line
              or 'BOARD_OPEN_SKIPPED ' in line]
    if not starts:
        starts = [i for i, line in enumerate(lines) if 'BOARD_CONFIGURED ' in line]
    # Keep engine diagnostics only inside the latest board attempt.
    attempt = lines[starts[-1]:] if starts else []
    closed_at = next((i for i, line in enumerate(attempt) if 'BOARD_CLOSED ' in line), None)
    if closed_at is not None:
        attempt = attempt[:closed_at + 1]
    session = [line for line in attempt if MARKER.search(line) or BRIDGE_ERROR.search(line)]
    views, summaries = [], []
    for line in session:
        view = VIEW.search(line)
        if view:
            revision, round_number, current, own, enemy, flags = map(int, view.groups())
            views.append(dict(revision=revision, round=round_number, current=current,
                              scoreOne=own, scoreTwo=enemy, flags=flags, winnerMask=flags >> 4))
        summary = SUMMARY.search(line)
        if summary:
            kind, total, passed, failed = summary.groups()
            total, passed, failed = int(total), int(passed), int(failed)
            summaries.append(dict(kind=kind, checks=total, passed=passed, failed=failed,
                                  countersConsistent=(passed + failed == total)))
    fatal = [line for line in session if any(token in line for token in (
        'BOARD_MISSING_FLASH_FUNCTION', 'BOARD_STATE_ERROR', 'CORE_CHECK_FAIL ', 'BOARD_CHECK_FAIL ', 'REQUEST_CHECK_FAIL ',
        'FLOW_CHECK_FAIL ', 'REQUEST_FLOW_ERROR '))]
    bridge_errors = [line for line in session if BRIDGE_ERROR.search(line)]
    relevant_errors = [line for line in attempt if BRIDGE_ERROR.search(line)
                       or ('betagwent' in line.lower() and ('[Error]' in line or '[Warning]' in line))]
    script_errors = [line for line in relevant_errors if '[Error][Script]' in line]
    configured = any('BOARD_CONFIGURED ' in line for line in session)
    closed = any('BOARD_CLOSED ' in line for line in session)
    if expected_counts is None:
        expected_counts = {'CORE': 116, 'BOARD': 104}
    latest_summaries = {item['kind']: item for item in summaries}
    checks_complete = all(kind in latest_summaries
                          and latest_summaries[kind]['checks'] == total
                          and latest_summaries[kind]['failed'] == 0
                          and latest_summaries[kind]['countersConsistent']
                          for kind, total in expected_counts.items()) and not fatal and not bridge_errors and not script_errors
    report = dict(log=str(log_name), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                  sessionFound=bool(session), nativeConfigured=configured, nativeClosed=closed,
                  views=views, checkSummaries=summaries, fatalOrCheckFailures=fatal,
                  relevantEngineErrors=relevant_errors,
                  modScriptErrors=script_errors,
                  requestFlowEvents=[line for line in session if 'REQUEST_FLOW_' in line],
                  nativeBridgeErrors=bridge_errors, nativeBridgeFailed=bool(bridge_errors),
                  revisionIncreasing=all(a['revision'] < b['revision'] for a, b in zip(views, views[1:])) if len(views) > 1 else None,
                  countersConsistent=all(item['countersConsistent'] for item in summaries) if summaries else None,
                  expectedCheckCounts=expected_counts, expectedChecksComplete=checks_complete,
                  checksObserved=sorted(set(item['kind'] for item in summaries)),
                  visualRenderingVerified=False, restoredInputVerified=False,
                  nativeRuntimeObserved=configured and bool(views),
                  note='Latest board attempt only. Rendering/input observations are not inferred from logs.')
    return report, session


def capture(log):
    expected = {'CORE': 116, 'BOARD': 104}
    active = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent/developmentRequestChecks.ws'
    if active.exists():
        prepared = json.loads((ROOT / 'docs/evidence/request-check-preparation.json').read_text())
        if hashlib.sha256(active.read_bytes()).hexdigest() != prepared['sourceSha256']:
            raise RuntimeError('Request checks differ from prepared expected count')
        expected['REQUEST'] = prepared['expectedRequestChecks']
    active_flow = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent/developmentRequestFlowChecks.ws'
    if active_flow.exists():
        prepared_flow = json.loads((ROOT / 'docs/evidence/request-flow-check-preparation.json').read_text())
        if hashlib.sha256(active_flow.read_bytes()).hexdigest() != prepared_flow['sourceSha256']:
            raise RuntimeError('Request flow checks differ from prepared expected count')
        expected['FLOW'] = prepared_flow['expectedFlowChecks']
    report, session = parse_runtime(log.read_bytes(), log, expected)
    output = ROOT / 'docs/evidence/board-runtime-result.json'
    trace = ROOT / 'docs/evidence/board-runtime-trace.txt'
    trace.write_text('\n'.join(session) + ('\n' if session else ''), encoding='utf-8')
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, default=DEFAULT_LOG)
    args = parser.parse_args()
    report = capture(args.log)
    print(json.dumps({key: report[key] for key in ('sessionFound', 'nativeRuntimeObserved',
        'nativeClosed', 'checksObserved', 'nativeBridgeFailed', 'fatalOrCheckFailures', 'visualRenderingVerified')}, indent=2))
