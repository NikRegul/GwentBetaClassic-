"""Bind APPLY20 to 14 original Apply observations, with explicit bool differences."""
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
oracle = read('beta-apply-fixtures.json')
extraction = read('beta-apply-extraction.json')
if oracle['failed'] or oracle['checks'] != 14 or oracle['copiedMethods'] != 5 or oracle['explicitShims'] != 4:
    raise RuntimeError('Original Apply observations incomplete')
for key in ('source', 'extract'):
    if sha(Path(extraction[key])).upper() != extraction[key + 'Sha256']:
        raise RuntimeError('Original or extracted assembly changed')
if oracle['extractSha256'] != extraction['extractSha256']:
    raise RuntimeError('Oracle/extraction association changed')
source = ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentApplyChecks.ws'
base = ROOT / 'BetaGwent/scripts/game/betagwent/actionApply.ws'
text = source.read_text(encoding='utf-8-sig')
cases = re.findall(r'Check\("([^"]+)", ([^\n]+)\);', text)
ids = [label for label, _ in cases]
if len(ids) != 20 or len(set(ids)) != len(ids):
    raise RuntimeError('Expected APPLY20 unique check IDs')
conditions = dict(cases)
associations = []
for observation in oracle['observations']:
    label = observation['id']
    condition = conditions[label]
    expected = observation['actual']
    trace = ''.join(item + '|' for item in expected['trace'])
    result_prefix = '!a.Apply()' if expected['error'] else 'a.Apply()'
    if not condition.startswith(result_prefix + ' && a.Text() == "' + trace + '"'):
        raise RuntimeError('Native expectation differs from original trace: ' + label)
    associations.append(dict(id=label, expectedTrace=trace, nativeResult=not bool(expected['error']),
        difference='Original CLR exception is represented by false; no engine exception is thrown.' if expected['error'] else None))
guards = [label for label in ids if label.startswith('guard/')]
if len(guards) != 6 or set(ids) != {item['id'] for item in associations} | set(guards):
    raise RuntimeError('Unexpected native-only checks')
report = dict(expectedApplyChecks=20, source=str(source), sourceSha256=sha(source),
    baseSource=str(base), baseSourceSha256=sha(base), expectedIds=ids,
    originalFixtureSha256=sha(E / 'beta-apply-fixtures.json'), originalChecks=14,
    copiedMethods=5, explicitShims=4, originalAssociations=associations, nativeOnlyGuards=guards,
    runtimeVerified=False,
    scope='Direct Apply/After boundary. Six original exception paths return false; Prepare is local setup, not original Init. No actual effects, manager policy, sink or scheduler.')
(E / 'apply-check-preparation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Prepared APPLY20: original trace associations14, native-only guards6; runtime pending.')
