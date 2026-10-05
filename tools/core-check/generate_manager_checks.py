"""Generate native manager scenarios from recipes and executed original observations.

Recipes are explicit inputs independently transcribed from the C# harness.
Only expected results come from the oracle; no expected trace is replayed by code.
"""
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
oracle = read(E / 'beta-manager-apply-fixtures.json')
extraction = read(E / 'beta-manager-apply-extraction.json')
if oracle['checks'] != 56 or oracle['failed'] or oracle['copiedMethods'] != 4 or oracle['explicitShims'] != 24:
    raise RuntimeError('Expected original manager56 with four copied methods/24 seams')
for key in ('source', 'extract'):
    if sha(Path(extraction[key])).upper() != extraction[key + 'Sha256']:
        raise RuntimeError('Original extraction changed')
if oracle['extractSha256'] != extraction['extractSha256']:
    raise RuntimeError('Oracle/extraction mismatch')

recipes = {}
def case(label, **config): recipes[label] = config
def alias(label, previous): recipes[label] = dict(recipes[previous])
case('normal/valid-apply-destroy')
case('normal/invalid-destroy-without-effect', valid=False)
case('before/unfired-diagnostic-is-not-throw', before=False)
case('before/no-fire-skips-diagnostic', fire=False, before=False)
alias('before/no-fire-short-circuits-getter', 'before/no-fire-skips-diagnostic')
for network in (-1, 0, 5, 10, 12): case(f'network/invalid-id-{network}', networkId=network, valid=False)
case('network/priority-skips-last-update', priority=True, networkId=5)
alias('network/priority-last-preserved', 'network/priority-skips-last-update')
case('state/dirty-precedes-effect', stateChanging=True)
case('state/invalid-not-dirty', stateChanging=True, valid=False)
alias('state/invalid-dirty-flag-false', 'state/invalid-not-dirty')
case('request/process-register-apply-deliver-retain', request=True)
case('request/state-dirty-between-register-and-apply', request=True, stateChanging=True)
case('request/not-processable-still-retained', request=True, processValues=[False])
case('request/not-processable-still-dirty', request=True, stateChanging=True, processValues=[False])
case('request/can-true-to-false-delivers-without-apply', request=True, processValues=[True, False])
case('request/can-false-to-true-applies-without-register-or-delivery', request=True, processValues=[False, True])
case('request/register-callback-changes-second-read', request=True, addClearsProcess=True)
case('request/invalid-destroyed', request=True, valid=False)
case('effect/throw-skips-send-and-destroy', stateChanging=True, failAt=1, main=True)
case('request/effect-throw-leaves-register-and-skips-delivery', request=True, failAt=1, main=True)
case('request/delivery-throw-skips-send', request=True, failAt=2, main=True)
for delay in (-1, 0, 25):
    case(f'main/send-pause-delay-{delay}', main=True, delay=delay)
    alias(f'main/delay-read-count-{delay}', f'main/send-pause-delay-{delay}')
case('main/send-false-still-pauses', main=True, delay=25, sendResult=False)
case('non-main/skips-send-pause', main=False, delay=25)
alias('non-main/delay-not-read', 'non-main/skips-send-pause')
case('main/send-throw-skips-pause-destroy', main=True, delay=25, failAt=3)
case('main/pause-throw-skips-destroy', main=True, delay=25, failAt=4)
case('callback/main-read-after-effect', main=True, effectMutation=1)
case('callback/main-read-after-delivery', request=True, receiveSetsMain=True)
for valid in (False, True): case(f'verbose/valid-{valid}', valid=valid, verbose=True)
case('network/getter-repeated-through-error-and-write', networkValues=[5, 5, 5, 12], valid=False)
alias('network/last-uses-final-read', 'network/getter-repeated-through-error-and-write')
case('delay/positive-test-then-repeated-argument-read', main=True, delayValues=[25, -7])
case('request/recipient-read-after-effect', request=True, effectMutation=2)
case('delay/read-after-send-callback', main=True, delay=25, sendChangesDelay=True)
case('request/effect-mutation-does-not-recheck-validity-or-delivery-snapshot', request=True, effectMutation=3)
case('main/invalid-skips-send-and-pause', main=True, delay=25, valid=False)
case('main/unprocessable-valid-request-still-sends-and-pauses', request=True, main=True, delay=25, processValues=[False])
for delay in (2147483648, 4294967295, 4294967296, 9223372036854775807, -9223372036854775808, -4294967296, -2147483649):
    case(f'delay64/value-{delay}', main=True, delay=delay)
if set(recipes) != {o['id'] for o in oracle['observations']}:
    raise RuntimeError('Native recipes must cover all original observation IDs exactly')

def int_expr(value): return '(-2147483647 - 1)' if value == -2147483648 else str(value)
def words(value):
    if not -(1 << 63) <= value < (1 << 63): raise ValueError('Delay out of Int64 range')
    low = value & 0xffffffff
    if low >= 1 << 31: low -= 1 << 32
    return value >> 32, low
def delay_assign(target, value):
    high, low = words(value)
    return [f'        {target}.highWord = {int_expr(high)};', f'        {target}.lowWord = {int_expr(low)};']
def trace_text(values):
    result = []
    for value in values:
        if value.startswith('pause:'):
            number = int(value[6:])
            if not -(1 << 31) <= number < (1 << 31):
                high, low = words(number); value = f'pause64:{high}:{low}'
        result.append(value + '|')
    return ''.join(result)

support = (ROOT / 'tools/core-check/src/managerCheckSupport.ws').read_text(encoding='utf-8')
extra = (ROOT / 'tools/core-check/src/managerCheckIntegration.ws').read_text(encoding='utf-8')
base_names = ['actionManager.ws', 'actionQueue.ws', 'actionApply.ws']
base_sources = {name: sha(ROOT / 'BetaGwent/scripts/game/betagwent' / name) for name in base_names}
contract_inputs = dict(baseSources=base_sources, supportSha256=sha(ROOT / 'tools/core-check/src/managerCheckSupport.ws'),
    integrationSha256=sha(ROOT / 'tools/core-check/src/managerCheckIntegration.ws'),
    generatorSha256=sha(Path(__file__)), oracleSha256=sha(E / 'beta-manager-apply-fixtures.json'))
contract_key = hashlib.sha256(json.dumps(contract_inputs, sort_keys=True).encode()).hexdigest()[:16]
extra = extra.replace('MANAGER_SUITE_BEGIN schema=1', 'MANAGER_SUITE_BEGIN schema=1 key=' + contract_key)
extra_ids = re.findall(r'Check\("([^"]+)"', extra)
total = 56 + len(extra_ids)
lines = [support]
associations = []
for index, observation in enumerate(oracle['observations']):
    if index % 8 == 0:
        if index: lines.append('    }')
        lines += [f'    private function RunOriginal{index // 8}()', '    {',
            '        var config : SBetaGwentManagerCheckConfig;',
            '        var delay : SBetaGwentDelay64;', '        var passed : bool;']
    label = observation['id']; config = recipes[label]; actual = observation['actual']
    lines.append('        config = BetaGwentManagerCheckDefaults();')
    for field, value in config.items():
        if field == 'delay': lines += delay_assign('config.delay', value)
        elif field == 'delayValues':
            for number in value:
                lines += delay_assign('delay', number); lines.append('        config.delayValues.PushBack(delay);')
        elif isinstance(value, list):
            for item in value:
                literal = str(item).lower() if isinstance(item, bool) else str(item)
                lines.append(f'        config.{field}.PushBack({literal});')
        else:
            literal = str(value).lower() if isinstance(value, bool) else str(value)
            lines.append(f'        config.{field} = {literal};')
    lines += ['        Setup(config);', '        passed = manager.ApplyAction(action);']
    error = actual.get('error') if isinstance(actual, dict) else None
    conditions = ['!passed && manager.IsFaulted()' if error else 'passed && !manager.IsFaulted()']
    trace = None
    if isinstance(actual, dict):
        if 'trace' in actual:
            trace = trace_text(actual['trace'])
            conditions.append(f'fixture.Text() == "{trace}"')
            pause_values = [int(v[6:]) for v in actual['trace'] if v.startswith('pause:')]
            conditions.append(f'fixture.PauseCount() == {len(pause_values)}')
            if pause_values:
                high, low = words(pause_values[-1])
                lines.append('        delay = fixture.LastPause();')
                conditions += [f'delay.highWord == {int_expr(high)}', f'delay.lowWord == {int_expr(low)}']
        getters = {'last': 'manager.GetLastKnownNetworkId()', 'seen': 'fixture.LastSeen()', 'reads': 'fixture.NetworkReads()'}
        for key in ('last', 'seen', 'reads'):
            if key in actual: conditions.append(getters[key] + ' == ' + str(actual[key]))
    elif label.startswith('main/delay-read-count') or label == 'non-main/delay-not-read':
        conditions.append('fixture.DelayReads() == ' + str(actual))
    elif label == 'before/no-fire-short-circuits-getter': conditions.append('fixture.BeforeReads() == ' + str(actual))
    elif label == 'network/priority-last-preserved': conditions.append('manager.GetLastKnownNetworkId() == ' + str(actual))
    elif label == 'state/invalid-dirty-flag-false': conditions.append('!context.IsDirty()')
    else: raise RuntimeError('Unexpected result schema: ' + label)
    condition = ' && '.join(conditions)
    lines.append(f'        Check("{label}", {condition});')
    associations.append(dict(id=label, config=config, nativeCondition=condition,
        exceptionDifference='Original exception becomes bool failure plus latched manager fault; no automatic cleanup.' if error else None))
lines += ['    }', '    public function Run()', '    {', '        checks = 0; failures = 0;',
    f'        LogChannel(\'BetaGwent\', "MANAGER_CHECK_BEGIN schema=1 fixture=manager{total} key={contract_key}");']
lines += [f'        RunOriginal{index}();' for index in range((len(oracle['observations']) + 7) // 8)]
lines += ['        RunExtra();', '        LogChannel(\'BetaGwent\', "MANAGER_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);', '    }', extra]
source = ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentManagerChecks.ws'
source.write_text('\n'.join(lines), encoding='utf-8-sig')
report = dict(expectedManagerChecks=total, originalChecks=56, nativeOnlyChecks=extra_ids,
    contractKey=contract_key, contractInputs=contract_inputs, baseSources=base_sources,
    source=str(source), sourceSha256=sha(source), originalFixtureSha256=sha(E / 'beta-manager-apply-fixtures.json'),
    originalHarnessSha256=sha(ROOT / 'tools/oracle/beta-manager-apply-ref/Program.cs'),
    generatorSha256=sha(Path(__file__)), associations=associations,
    expectedIds=[o['id'] for o in oracle['observations']] + extra_ids,
    runtimeVerified=False,
    scope='56 original observations through synthetic service callbacks plus native guards/integration. Exception->bool+fault differences explicit. No real card effects, network/cache/timer or full scheduler.')
(E / 'manager-check-preparation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(f'Prepared manager{total}: original56 + native-only{len(extra_ids)}; runtime pending.')
