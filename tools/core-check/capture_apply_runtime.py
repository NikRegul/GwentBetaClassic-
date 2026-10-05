"""Capture direct APPLY20 from real REDkit log; queue and UI evidence are separate."""
import argparse
import hashlib
import json
from pathlib import Path
from capture_action_runtime import ROOT, DEFAULT_LOG, parse_runtime

def capture(log):
    evidence = ROOT / 'docs/evidence'
    manifest = json.loads((evidence / 'apply-check-preparation.json').read_text())
    active = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent'
    for key in ('source', 'baseSource'):
        path = active / Path(manifest[key]).name
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest[key + 'Sha256']:
            raise RuntimeError('Active Apply source differs from preparation: ' + path.name)
    report, batch = parse_runtime(log.read_bytes(), log, manifest['expectedIds'],
        begin='APPLY_CHECK_BEGIN schema=1 fixture=apply20', tag='APPLY')
    report['expectedApplyChecks'] = report.pop('expectedActionChecks')
    report['activeCheckSourceSha256'] = manifest['sourceSha256']
    report['activeBaseSourceSha256'] = manifest['baseSourceSha256']
    report['scope'] = 'Latest isolated Apply20 batch only. No manager policy, actual card effects or full scheduler verification.'
    (evidence / 'apply-runtime-result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (evidence / 'apply-runtime-trace.txt').write_text('\n'.join(batch) + ('\n' if batch else ''), encoding='utf-8')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, default=DEFAULT_LOG)
    report = capture(parser.parse_args().log)
    print(json.dumps({key: report[key] for key in ('batchFound', 'expectedApplyChecks', 'expectedChecksComplete', 'checkFailures', 'modScriptErrors')}, indent=2))
