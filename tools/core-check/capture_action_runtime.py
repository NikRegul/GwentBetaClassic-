"""Read the last isolated ACTION batch; do not infer field effects or UI success."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\editor.log')
BEGIN = 'ACTION_CHECK_BEGIN schema=1 fixture=queue39'
DONE = re.compile(r'ACTION_CHECK_DONE checks=(\d+) passed=(\d+) failed=(\d+)')


def parse_runtime(raw, log_name, expected_ids, *, begin=BEGIN, tag='ACTION'):
    if tag not in ('ACTION', 'APPLY', 'MANAGER', 'POWER', 'REGISTRY'):
        raise ValueError('Unsupported isolated check tag')
    done_pattern = re.compile(rf'{tag}_CHECK_DONE checks=(\d+) passed=(\d+) failed=(\d+)')
    lines = raw.decode('utf-8', errors='replace').splitlines()
    starts = [index for index, line in enumerate(lines) if begin in line]
    batch = lines[starts[-1]:] if starts else []
    end = next((index for index, line in enumerate(batch) if done_pattern.search(line)), None)
    if end is not None:
        batch = batch[:end + 1]
    passes = [match.group(1) for line in batch if (match := re.search(rf'{tag}_CHECK_PASS (.+)$', line))]
    failures = [line for line in batch if tag + '_CHECK_FAIL ' in line]
    summaries = [tuple(int(value) for value in match.groups()) for line in batch if (match := done_pattern.search(line))]
    script_errors = [line for index, line in enumerate(batch) if '[Error][Script]' in line
                     and 'betagwent' in '\n'.join(batch[index:index + 3]).lower()]
    expected = len(expected_ids)
    complete = bool(starts) and summaries == [(expected, expected, 0)] and passes == expected_ids and not failures and not script_errors
    report = dict(log=str(log_name), logSha256=hashlib.sha256(raw).hexdigest(),
                  batchFound=bool(starts), expectedActionChecks=expected,
                  passIds=passes, expectedIds=expected_ids, checkFailures=failures,
                  summary=[dict(checks=c, passed=p, failed=f) for c, p, f in summaries],
                  modScriptErrors=script_errors, expectedChecksComplete=complete,
                  scope='Latest isolated queue batch through DONE only; no concrete effect or full scheduler verification.')
    return report, batch


def capture(log):
    manifest = json.loads((ROOT / 'docs/evidence/action-check-preparation.json').read_text(encoding='utf-8-sig'))
    source = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent/developmentActionQueueChecks.ws'
    raw_source = source.read_bytes()
    if hashlib.sha256(raw_source).hexdigest() != manifest['sourceSha256']:
        raise RuntimeError('Active action checks differ from prepared manifest')
    ids = re.findall(r'Check\("([^"]+)"', raw_source.decode('utf-8-sig'))
    if len(ids) != manifest['expectedActionChecks'] or len(set(ids)) != len(ids):
        raise RuntimeError('Action check IDs/count changed')
    report, batch = parse_runtime(log.read_bytes(), log, ids)
    report['activeCheckSourceSha256'] = manifest['sourceSha256']
    evidence = ROOT / 'docs/evidence'
    (evidence / 'action-runtime-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (evidence / 'action-runtime-trace.txt').write_text('\n'.join(batch) + ('\n' if batch else ''), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, default=DEFAULT_LOG)
    args = parser.parse_args()
    result = capture(args.log)
    print(json.dumps({key: result[key] for key in ('batchFound', 'expectedActionChecks', 'expectedChecksComplete', 'checkFailures', 'modScriptErrors')}, indent=2))
