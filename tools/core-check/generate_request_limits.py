"""Generate WS assertions from executed exact copied IL observations."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/evidence'
report = json.loads((EVIDENCE / 'beta-request-limit-fixtures.json').read_text())
manifest = json.loads((EVIDENCE / 'beta-request-extraction.json').read_text(encoding='utf-8-sig'))
if report['failed'] or report['checks'] != 18 or report['passed'] != 18:
    raise SystemExit('Original copied-IL fixtures have not passed')
for key in ('source', 'extract'):
    if hashlib.sha256(Path(manifest[key]).read_bytes()).hexdigest().upper() != manifest[key + 'Sha256']:
        raise SystemExit('Verified original/extracted assembly changed')
if report['extractSha256'] != manifest['extractSha256']:
    raise SystemExit('Oracle fixture was generated from another extract')
cases = ROOT / 'tools/oracle/beta-request-ref/limit-cases.json'
if hashlib.sha256(cases.read_bytes()).hexdigest().upper() != report['fixtureSha256']:
    raise SystemExit('Oracle case file changed')

boolean = lambda value: 'true' if value else 'false'
lines = ['        var limits : SBetaGwentRequestLimits;']
for item in report['observations']:
    case, actual = item['fixture'], item['actual']
    if not item['passed']:
        raise SystemExit('Failed oracle observation')
    if case['kind'] == 'targetApply':
        lines.append(f"        limits = BetaGwentAppliedTargetLimits({case['valid']}, {case['max']}, {case['selected']}, {boolean(case['finished'])});")
        expression = f"limits.minimum == {actual['min']} && limits.maximum == {actual['max']} && limits.finished == {boolean(actual['finished'])}"
    else:
        helper = f"BetaGwentRequestCanFinish({case['min']}, {case['max']}, {case['selected']})"
        if case['kind'] == 'choiceFinish':
            expression = f"{helper} == {boolean(actual['returned'])}"
        else:
            expression = f"({boolean(case['finished'])} || {helper}) == {boolean(actual['finished'])}"
    lines.append(f'        Check("copied IL {item["id"]}", {expression});')

path = ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentRequestChecks.ws'
text = path.read_text(encoding='utf-8-sig')
pattern = r'(    private function CheckCopiedILLimits\(\)\n    \{\n).*?(\n    \}\n\n    public function GetDisplaySummary)'
text, count = re.subn(pattern, lambda match: match[1] + '\n'.join(lines) + match[2], text, flags=re.S)
if count != 1:
    raise SystemExit('Oracle code marker missing')
path.write_text(text, encoding='utf-8-sig')
expected = len(re.findall(r'\bCheck\("', text))
output = dict(originalFixtureSha256=report['fixtureSha256'], originalCopiedILChecks=18,
              expectedRequestChecks=expected, runtimeVerified=False,
              source=str(path), sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
              note='Expected count assumes all guarded result-size assertions execute; native runtime pending.')
(EVIDENCE / 'request-check-preparation.json').write_text(json.dumps(output, indent=2) + '\n')
print(f'Generated18 oracle assertions; request runtime checks expected: {expected}')
