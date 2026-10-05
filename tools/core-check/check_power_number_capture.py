"""Synthetic parser guards; these are never native gameplay evidence."""
from capture_power_number_runtime import parse_suite

key, manager_key = 'power-version', 'manager-version'
action, apply, manager, power = ['a1', 'a2'], ['b1'], ['m1', 'm2'], ['p1', 'p2']

def batch(tag, ids, begin):
    return [begin] + [tag + '_CHECK_PASS ' + item for item in ids] + [f'{tag}_CHECK_DONE checks={len(ids)} passed={len(ids)} failed=0']

good = [f'POWER_SUITE_BEGIN schema=1 key={key} manager={manager_key}',
    f'MANAGER_SUITE_BEGIN schema=1 key={manager_key}']
good += batch('ACTION', action, 'ACTION_CHECK_BEGIN schema=1 fixture=queue39')
good += batch('APPLY', apply, 'APPLY_CHECK_BEGIN schema=1 fixture=apply20')
good += batch('MANAGER', manager, f'MANAGER_CHECK_BEGIN schema=1 fixture=manager2 key={manager_key}')
good += ['MANAGER_SUITE_END schema=1']
good += batch('POWER', power, f'POWER_CHECK_BEGIN schema=1 fixture=power2 key={key}')
good += ['POWER_SUITE_END schema=1']

checks = 0
def check(label, lines, expected, action_begin_count=1):
    global checks
    report, _ = parse_suite('\n'.join(lines).encode(), 'synthetic.log', key, manager_key, action, apply, manager, power, action_begin_count)
    if report['expectedChecksComplete'] != expected: raise AssertionError(label)
    checks += 1

check('complete', good, True)
check('missing', [], False)
check('missing outer end', good[:-1], False)
check('wrong outer key', [good[0].replace(key, 'old')] + good[1:], False)
check('new wrong version wins', good + ['POWER_SUITE_BEGIN schema=1 key=old manager=old'], False)
check('new incomplete wins', good + good[:1], False)
check('missing nested manager', [line for line in good if 'MANAGER_' not in line], False)
check('wrong manager key', [line.replace(manager_key, 'wrong') if 'MANAGER_' in line else line for line in good], False)
check('missing numeric ID', [line for line in good if line != 'POWER_CHECK_PASS p2'], False)
check('duplicate numeric ID after DONE', good[:-1] + ['POWER_CHECK_PASS p2'] + good[-1:], False)
check('extra regression ID after DONE', good[:-1] + ['ACTION_CHECK_PASS extra'] + good[-1:], False)
check('extra numeric BEGIN after DONE', good[:-1] + [f'POWER_CHECK_BEGIN schema=1 fixture=power2 key={key}'] + good[-1:], False)
check('extra numeric DONE after DONE', good[:-1] + ['POWER_CHECK_DONE checks=2 passed=2 failed=0'] + good[-1:], False)
check('numeric failure marker after DONE', good[:-1] + ['POWER_CHECK_FAIL extra'] + good[-1:], False)
check('mod error after numeric DONE', good[:-1] + ['[Error][Script] game/betagwent/powerNumbers.ws: fixture'] + good[-1:], False)
check('unrelated error', good[:-1] + ['[Error][Script] game/vanilla.ws: fixture'] + good[-1:], True)
check('wrong counters', [line.replace('POWER_CHECK_DONE checks=2 passed=2 failed=0', 'POWER_CHECK_DONE checks=2 passed=1 failed=1') for line in good], False)
check('regression missing ID', [line for line in good if line != 'ACTION_CHECK_PASS a1'], False)
check('regression wrong counters', [line.replace('MANAGER_CHECK_DONE checks=2 passed=2 failed=0', 'MANAGER_CHECK_DONE checks=2 passed=2 failed=1') for line in good], False)
check('latest fresh complete', good[:1] + good, True)
check('latest skip supersedes old success', good + ['POWER_CHECK_SKIPPED no player'], False)
check('old skip does not poison fresh success', ['POWER_CHECK_SKIPPED no player'] + good, True)
paired = good[:3] + [good[2]] + good[3:]
check('authenticated consecutive queue prefix', paired, True, 2)
check('third queue prefix rejected', paired[:3] + [paired[2]] + paired[3:], False, 2)
check('single queue prefix cannot satisfy two', good, False, 2)
check('second prefix after PASS rejected', good[:4] + [good[2]] + good[4:], False, 2)
check('pair not allowed by single declaration', paired, False)
check('queue prefix after DONE rejected', good[:-1] + [good[2]] + good[-1:], False, 2)
print(f'POWER suite parser synthetic guards: {checks}/{checks}. No native acceptance.')
