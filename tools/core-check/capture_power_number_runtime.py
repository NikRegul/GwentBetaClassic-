"""Capture a versioned POWER suite with complete nested manager regressions."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from capture_action_runtime import ROOT, DEFAULT_LOG, parse_runtime
from capture_manager_runtime import parse_suite as parse_manager_suite


def parse_suite(raw, log_name, key, manager_key, action_ids, apply_ids, manager_ids, power_ids, action_begin_count=1):
    lines = raw.decode('utf-8', errors='replace').splitlines()
    starts = [i for i, line in enumerate(lines) if 'POWER_SUITE_BEGIN schema=1' in line
        or 'POWER_CHECK_SKIPPED no player' in line]
    suite = lines[starts[-1]:] if starts else []
    end = next((i for i, line in enumerate(suite) if 'POWER_SUITE_END schema=1' in line), None)
    if end is not None: suite = suite[:end + 1]
    correct = bool(suite) and suite[0].rstrip().endswith(f'POWER_SUITE_BEGIN schema=1 key={key} manager={manager_key}')
    scoped = '\n'.join(suite).encode('utf-8')
    manager, _ = parse_manager_suite(scoped, log_name, manager_key, action_ids, apply_ids, manager_ids)
    begin = f'POWER_CHECK_BEGIN schema=1 fixture=power{len(power_ids)} key={key}'
    power, _ = parse_runtime(scoped, log_name, power_ids, begin=begin, tag='POWER')
    power['expectedChecks'] = power.pop('expectedActionChecks')
    manager_ends = [i for i, line in enumerate(suite) if 'MANAGER_SUITE_END schema=1' in line]
    power_starts = [i for i, line in enumerate(suite) if begin in line]
    ordered = bool(manager_ends and power_starts and manager_ends[-1] < power_starts[-1])
    errors = [line for i, line in enumerate(suite) if '[Error][Script]' in line
        and 'betagwent' in '\n'.join(suite[i:i + 3]).lower()]
    failures = [line for line in suite if re.search(r'(?:ACTION|APPLY|MANAGER|POWER)_CHECK_FAIL ', line)]
    # Do not let the per-batch DONE cutoff hide extra PASS/BEGIN/DONE markers.
    exact = True
    for tag, ids in (('ACTION', action_ids), ('APPLY', apply_ids), ('MANAGER', manager_ids), ('POWER', power_ids)):
        passes = [m.group(1) for line in suite if (m := re.search(rf'{tag}_CHECK_PASS (.+)$', line))]
        exact = exact and passes == ids
        # The authenticated queue39 source logs BEGIN twice consecutively.
        # Permit that exact source-declared prefix, never an extra restart.
        begins = [i for i, line in enumerate(suite) if tag + '_CHECK_BEGIN schema=1' in line]
        expected_begins = action_begin_count if tag == 'ACTION' else 1
        exact = exact and len(begins) == expected_begins
        if expected_begins > 1:
            exact = exact and all(begins[i] == begins[0] + i for i in range(len(begins)))
            exact = exact and all(suite[i].endswith('ACTION_CHECK_BEGIN schema=1 fixture=queue39') for i in begins)
        exact = exact and sum(tag + '_CHECK_DONE checks=' in line for line in suite) == 1
    exact = exact and sum('MANAGER_SUITE_BEGIN schema=1' in line for line in suite) == 1
    exact = exact and sum('MANAGER_SUITE_END schema=1' in line for line in suite) == 1
    complete = correct and end is not None and ordered and exact and manager['expectedChecksComplete'] and power['expectedChecksComplete'] and not errors and not failures
    report = dict(log=str(log_name), logSha256=hashlib.sha256(raw).hexdigest(),
        suiteFound=bool(suite) and 'POWER_SUITE_BEGIN schema=1' in suite[0],
        lastAttemptSkipped=bool(suite) and 'POWER_CHECK_SKIPPED no player' in suite[0],
        correctContractKey=correct, expectedContractKey=key,
        expectedManagerContractKey=manager_key, expectedActionBeginCount=action_begin_count,
        suiteEnded=end is not None, batchesOrdered=ordered, wholeSuiteMarkersExact=exact,
        manager=manager, power=power, checkFailures=failures, modScriptErrors=errors,
        expectedChecksComplete=complete,
        scope='Numeric raw final-setter boundary and isolated manager/queue/Apply regressions. No real card power events, death, armor absorption or full match acceptance.')
    return report, suite


def capture(log):
    evidence = ROOT / 'docs/evidence'
    def read(name): return json.loads((evidence / name).read_text(encoding='utf-8-sig'))
    power = read('power-number-check-preparation.json')
    manager = read('manager-check-preparation.json')
    queue = read('action-check-preparation.json')
    apply = read('apply-check-preparation.json')
    if power['managerContractKey'] != manager['contractKey']:
        raise RuntimeError('Nested manager version differs from power preparation')
    active = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent'
    sources = dict(power['baseSources'])
    for manifest in (power, manager, queue, apply):
        sources[Path(manifest['source']).name] = manifest['sourceSha256']
    for name, digest in sources.items():
        if hashlib.sha256((active / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Active source differs from prepared contract: ' + name)
    queue_text = (active / Path(queue['source']).name).read_text(encoding='utf-8-sig')
    ids = re.findall(r'Check\("([^"]+)"', queue_text)
    begin_count = queue_text.count('LogChannel(\'BetaGwent\', "ACTION_CHECK_BEGIN schema=1 fixture=queue39");')
    if begin_count not in (1, 2): raise RuntimeError('Unexpected authenticated queue BEGIN declarations')
    report, suite = parse_suite(log.read_bytes(), log, power['contractKey'], manager['contractKey'],
        ids, apply['expectedIds'], manager['expectedIds'], power['expectedIds'], begin_count)
    report['activeSources'] = sources
    (evidence / 'power-number-runtime-result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (evidence / 'power-number-runtime-trace.txt').write_text('\n'.join(suite) + ('\n' if suite else ''), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, default=DEFAULT_LOG)
    result = capture(parser.parse_args().log)
    print(json.dumps({key: result[key] for key in ('suiteFound', 'correctContractKey', 'expectedChecksComplete', 'checkFailures', 'modScriptErrors')}, indent=2))
