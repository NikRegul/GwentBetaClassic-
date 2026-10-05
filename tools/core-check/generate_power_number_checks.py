"""Generate numeric native recipes from executed exact original40 observations."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def require(value, message):
    if not value: raise RuntimeError(message)
def integer(value): return '(-2147483647 - 1)' if value == -(1 << 31) else str(value)
def fields(value):
    return 'BetaGwentPowerFields(' + ', '.join(integer(value[key]) for key in ('Base', 'Permanent', 'Current', 'Armor')) + ')'

oracle_path = E / 'beta-power-numeric-fixtures.json'
oracle = read(oracle_path)
extract = read(E / 'beta-power-numeric-extraction.json')
require(oracle['checks'] == oracle['passed'] == 40 and oracle['failed'] == 0, 'Original40 incomplete')
require(oracle['copiedMethods'] == 18 and oracle['explicitShims'] == 1 and
    oracle['originalCodeExecuted'] and not oracle['originalAssemblyLoaded'], 'Original scope changed')
for key in ('source', 'extract'):
    require(sha(Path(extract[key])).upper() == extract[key + 'Sha256'], 'Extraction source identity changed')
require(oracle['extractSha256'] == extract['extractSha256'] and
    all(m['exactInstructionMatch'] for m in extract['methods']), 'Copied IL identity changed')
harness = ROOT / 'tools/oracle/beta-power-numeric-ref/Program.cs'
require(oracle['harnessSha256'] == sha(harness).upper(), 'Harness changed since observations')
require(extract['extractorSha256'] == sha(ROOT / 'tools/oracle/extract_beta_power_numeric.ps1').upper(), 'Extractor changed')
manager = read(E / 'manager-check-preparation.json')
support_path = ROOT / 'tools/core-check/src/powerNumberCheckSupport.ws'
support = support_path.read_text(encoding='utf-8')
extra_ids = re.findall(r'Check\("([^"]+)"', support)
require(len(extra_ids) == len(set(extra_ids)) == 15, 'Expected guards/integration15')
bases = {name: sha(ROOT / 'BetaGwent/scripts/game/betagwent' / name)
    for name in ('powerNumbers.ws', 'types.ws', 'actionManager.ws', 'actionApply.ws', 'actionQueue.ws')}
inputs = dict(baseSources=bases, managerContractKey=manager['contractKey'],
    supportSha256=sha(support_path), generatorSha256=sha(Path(__file__)), oracleSha256=sha(oracle_path))
key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
methods = {'SetPower', 'SetArmor', 'SetBasePower', 'SetPermanentPower',
    'SetBasePowerAndArmor', 'SetPermanentPowerAndArmor', 'RestorePower', 'AddArmor', 'MultiplyArmor', 'MultiplyValue'}
lines = [support]
associations = []
for index, observation in enumerate(oracle['observations']):
    require(observation['passed'] and observation['method'] in methods, 'Unexpected observation')
    if index % 8 == 0:
        if index: lines.append('    }')
        lines += [f'    private function RunOriginal{index // 8}()', '    {',
            '        var fixture : CBetaGwentPowerNumberCheckFixture;', '        var passed : bool;', '        var result : int;']
    expected = observation['actual']
    require(len(expected['Calls']) <= 1, 'Unexpected multiple final setter calls')
    mutation = observation['mutateInSetter']
    lines += ['        fixture = new CBetaGwentPowerNumberCheckFixture in this;',
        f'        fixture.InitFromFields({fields(observation["before"])});',
        f'        fixture.Configure({str(bool(expected["Error"])).lower()}, {str(mutation is not None).lower()}, {fields(mutation or observation["before"])});']
    arguments = [integer(value) for value in observation['arguments']]
    if observation['method'] == 'MultiplyValue': arguments.append('result')
    lines.append('        passed = fixture.' + observation['method'] + '(' + ', '.join(arguments) + ');')
    condition = ['!passed' if expected['Error'] else 'passed',
        'BetaGwentPowerFieldsEqual(fixture.Snapshot(), ' + fields(expected['After']) + ')',
        'fixture.CallCount() == ' + str(len(expected['Calls']))]
    if expected['Calls']:
        call = expected['Calls'][0]
        condition.append(f'fixture.LastCallEquals({integer(call["Power"])}, {integer(call["Armor"])}, {fields(call["FieldsAtEntry"])})')
    if expected['Return'] is not None: condition.append('result == ' + integer(expected['Return']))
    label = observation['id']
    lines.append('        Check("' + label + '", ' + ' && '.join(condition) + ');')
    associations.append(dict(id=label, method=observation['method'], before=observation['before'],
        arguments=observation['arguments'], mutation=mutation, expected=expected,
        exceptionDifference='CLR callback throw becomes false, no rollback.' if expected['Error'] else None))
lines += ['    }', '    public function Run()', '    {', '        checks = 0; failures = 0;',
    f'        LogChannel(\'BetaGwent\', "POWER_CHECK_BEGIN schema=1 fixture=power55 key={key}");']
lines += [f'        RunOriginal{index}();' for index in range(5)]
lines += ['        RunGuards(); RunIntegration();',
    '        LogChannel(\'BetaGwent\', "POWER_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);',
    '    }', '}', '', 'exec function bgpower_check()', '{',
    '    var runner : CBetaGwentPowerNumberCheckRunner;',
    '    if (!thePlayer) { LogChannel(\'BetaGwent\', "POWER_CHECK_SKIPPED no player"); return; }',
    f'    LogChannel(\'BetaGwent\', "POWER_SUITE_BEGIN schema=1 key={key} manager={manager["contractKey"]}");',
    '    BetaGwentRunManagerChecks();', '    runner = new CBetaGwentPowerNumberCheckRunner in thePlayer;', '    runner.Run();',
    '    LogChannel(\'BetaGwent\', "POWER_SUITE_END schema=1");',
    '    theGame.GetGuiManager().ShowNotification("Сила/броня: " + (55 - runner.Failures()) + "/55, ошибок: " + runner.Failures(), 8.0);', '}']
source = ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentPowerNumberChecks.ws'
source.write_text('\n'.join(lines) + '\n', encoding='utf-8-sig')
report = dict(expectedPowerChecks=55, originalChecks=40, nativeOnlyChecks=extra_ids,
    contractKey=key, managerContractKey=manager['contractKey'], contractInputs=inputs, baseSources=bases,
    source=str(source), sourceSha256=sha(source), originalFixtureSha256=sha(oracle_path),
    originalHarnessSha256=sha(harness), generatorSha256=sha(Path(__file__)),
    associations=associations, expectedIds=[o['id'] for o in oracle['observations']] + extra_ids,
    runtimeVerified=False,
    scope='Numeric raw setter boundary only; guards and manager integration. Missing/failed setter -> false, no undo. No actual SetPowerAndArmor clamp/events/armor absorption/card death/registry or full attack acceptance.')
(E / 'power-number-check-preparation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(f'Prepared POWER55: original40 + guards/integration15; native pending. key={key}')
