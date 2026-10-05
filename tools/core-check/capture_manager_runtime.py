"""Capture one versioned MANAGER suite; require queue39, Apply20 and manager86."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from capture_action_runtime import ROOT, DEFAULT_LOG, parse_runtime

def parse_suite(raw, log_name, key, action_ids, apply_ids, manager_ids):
    lines = raw.decode('utf-8', errors='replace').splitlines()
    # A newer suite with a wrong version supersedes an older matching suite.
    starts = [i for i, line in enumerate(lines) if 'MANAGER_SUITE_BEGIN schema=1' in line]
    suite = lines[starts[-1]:] if starts else []
    end = next((i for i, line in enumerate(suite) if 'MANAGER_SUITE_END schema=1' in line), None)
    if end is not None: suite = suite[:end + 1]
    correct_key = bool(suite) and suite[0].rstrip().endswith('MANAGER_SUITE_BEGIN schema=1 key=' + key)
    specs = [('ACTION', action_ids, 'ACTION_CHECK_BEGIN schema=1 fixture=queue39'),
        ('APPLY', apply_ids, 'APPLY_CHECK_BEGIN schema=1 fixture=apply20'),
        ('MANAGER', manager_ids, f'MANAGER_CHECK_BEGIN schema=1 fixture=manager{len(manager_ids)} key={key}')]
    batches, positions = {}, []
    scoped_raw = '\n'.join(suite).encode('utf-8')
    for tag, ids, begin in specs:
        batch, _ = parse_runtime(scoped_raw, log_name, ids, begin=begin, tag=tag)
        batch['expectedChecks'] = batch.pop('expectedActionChecks')
        batch.pop('scope')
        batches[tag] = batch
        found = [i for i, line in enumerate(suite) if begin in line]
        positions.append(found[-1] if found else -1)
    errors = [line for i, line in enumerate(suite) if '[Error][Script]' in line
        and 'betagwent' in '\n'.join(suite[i:i + 3]).lower()]
    failures = [line for line in suite if re.search(r'(?:ACTION|APPLY|MANAGER)_CHECK_FAIL ', line)]
    ordered = bool(suite) and 0 < positions[0] < positions[1] < positions[2]
    complete = correct_key and end is not None and ordered and not errors and not failures and all(b['expectedChecksComplete'] for b in batches.values())
    report = dict(log=str(log_name), logSha256=hashlib.sha256(raw).hexdigest(),
        suiteFound=bool(starts), correctContractKey=correct_key, expectedContractKey=key,
        suiteEnded=end is not None, batchesOrdered=ordered, batches=batches,
        checkFailures=failures, modScriptErrors=errors, expectedChecksComplete=complete,
        scope='Versioned isolated manager suite, queue39/Apply20 regression and manager checks. No actual card/network/clock/cache/full scheduler acceptance.')
    return report, suite

def capture(log):
    evidence = ROOT / 'docs/evidence'
    manager = json.loads((evidence / 'manager-check-preparation.json').read_text())
    queue = json.loads((evidence / 'action-check-preparation.json').read_text())
    apply = json.loads((evidence / 'apply-check-preparation.json').read_text())
    active = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent'
    sources = dict(manager['baseSources'])
    sources[Path(manager['source']).name] = manager['sourceSha256']
    sources[Path(queue['source']).name] = queue['sourceSha256']
    sources[Path(apply['source']).name] = apply['sourceSha256']
    for name, digest in sources.items():
        if hashlib.sha256((active / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Active source differs from prepared contract: ' + name)
    queue_ids = re.findall(r'Check\("([^"]+)"', (active / Path(queue['source']).name).read_text(encoding='utf-8-sig'))
    report, suite = parse_suite(log.read_bytes(), log, manager['contractKey'], queue_ids, apply['expectedIds'], manager['expectedIds'])
    report['activeSources'] = sources
    (evidence / 'manager-runtime-result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (evidence / 'manager-runtime-trace.txt').write_text('\n'.join(suite) + ('\n' if suite else ''), encoding='utf-8')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, default=DEFAULT_LOG)
    report = capture(parser.parse_args().log)
    print(json.dumps({key: report[key] for key in ('suiteFound', 'correctContractKey', 'expectedChecksComplete', 'checkFailures', 'modScriptErrors')}, indent=2))
