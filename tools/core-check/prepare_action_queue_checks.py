"""Bind native queue check IDs to executed copied-IL observations and explicit differences."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
evidence = ROOT / 'docs/evidence'
oracle = json.loads((evidence / 'beta-action-fixtures.json').read_text(encoding='utf-8-sig'))
extraction = json.loads((evidence / 'beta-action-extraction.json').read_text(encoding='utf-8-sig'))
if oracle['failed'] or oracle['checks'] != 36 or oracle['copiedMethods'] != 21 or oracle['explicitShims'] != 5:
    raise RuntimeError('Original queue observations are incomplete')
for key in ('source', 'extract'):
    if hashlib.sha256(Path(extraction[key]).read_bytes()).hexdigest().upper() != extraction[key + 'Sha256']:
        raise RuntimeError('Original/extracted assembly changed')
if oracle['extractSha256'] != extraction['extractSha256']:
    raise RuntimeError('Fixture/extraction association changed')
source = ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentActionQueueChecks.ws'
ids = re.findall(r'Check\("([^"]+)"', source.read_text(encoding='utf-8-sig'))
original_ids = {item['id'] for item in oracle['observations']}
differences = {
    'push/non-authority-front-guarded': {'original': 'push/non-authority-front-rejected',
                                      'difference': 'Native returns false; original throws through exception helper.'},
    'local/empty-call-guarded': {'original': 'local/empty-call-throws',
                               'difference': 'Native guards empty invocation with false; original indexes an empty List and throws.'},
}
guards = [value for value in ids if value.startswith('guard/')]
mapped = [value for value in ids if value in original_ids]
unmapped = set(ids) - original_ids - set(differences) - set(guards)
omitted = original_ids - set(mapped) - {value['original'] for value in differences.values()}
if len(ids) != 39 or len(ids) != len(set(ids)) or unmapped or len(mapped) != 31 or len(guards) != 6:
    raise RuntimeError('Native check IDs/count changed unexpectedly')
if omitted != {'debug/before-break', 'debug/dispatch-break', 'debug/push-break'}:
    raise RuntimeError('Unexpected omitted original observations')
report = dict(expectedActionChecks=len(ids), source=str(source),
              sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              originalFixtureSha256=hashlib.sha256((evidence / 'beta-action-fixtures.json').read_bytes()).hexdigest(),
              originalCopiedILChecks=36, copiedMethods=21, explicitShims=5,
              originalObservationIds=mapped, explicitNativeDifferences=differences,
              nativeOnlyGuards=guards, originalObservationsNotPorted=sorted(omitted),
              runtimeVerified=False,
              scope='31 original observation IDs, two explicit exception/guard differences, six local guards. Real ApplyAction, effect execution, debug break and full scheduler remain outside the port.')
(evidence / 'action-check-preparation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Prepared ACTION39: original observations31, explicit differences2, native guards6; runtime pending.')
