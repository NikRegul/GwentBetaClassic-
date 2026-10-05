"""Synthetic parser checks; never native registry evidence."""
from capture_registry_id_runtime import parse_suite

specs = dict(ACTION=['a'], APPLY=['b'], MANAGER=['m'], POWER=['p'], REGISTRY=['r', 's'])
good = ['REGISTRY_SUITE_BEGIN schema=1 key=registry power=power manager=manager', 'MANAGER_SUITE_BEGIN schema=1 key=manager']
for tag, ids in specs.items():
    if tag == 'POWER': good += ['MANAGER_SUITE_END schema=1']
    fixture = {'ACTION':'queue39', 'APPLY':'apply20', 'MANAGER':'manager1 key=manager', 'POWER':'power1 key=power', 'REGISTRY':'registry2 key=registry'}[tag]
    good += [f'{tag}_CHECK_BEGIN schema=1 fixture={fixture}']
    good += [f'{tag}_CHECK_PASS {i}' for i in ids] + [f'{tag}_CHECK_DONE checks={len(ids)} passed={len(ids)} failed=0']
good += ['REGISTRY_SUITE_END schema=1']
checks = 0
def check(label, lines, expected, count=1):
    global checks
    r, _ = parse_suite('\n'.join(lines).encode(), 'synthetic.log', 'registry', 'power', 'manager', specs, count)
    if r['expectedChecksComplete'] != expected: raise AssertionError(label)
    checks += 1

check('complete', good, True)
check('no attempt', [], False)
check('missing end', good[:-1], False)
check('wrong key', [good[0].replace('key=registry', 'key=old')] + good[1:], False)
check('wrong numeric key', [s.replace('power1 key=power', 'power1 key=old') for s in good], False)
check('latest incomplete wins', good + good[:1], False)
check('latest skip wins', good + ['REGISTRY_CHECK_SKIPPED no player'], False)
check('old skip harmless', ['REGISTRY_CHECK_SKIPPED no player'] + good, True)
for tag in specs:
    check('missing PASS ' + tag, [s for s in good if s != f'{tag}_CHECK_PASS {specs[tag][0]}'], False)
    check('extra PASS after DONE ' + tag, good[:-1] + [f'{tag}_CHECK_PASS extra'] + good[-1:], False)
check('failure after DONE', good[:-1] + ['REGISTRY_CHECK_FAIL extra'] + good[-1:], False)
check('mod error after DONE', good[:-1] + ['[Error][Script] game/betagwent/registryIds.ws: error'] + good[-1:], False)
check('unrelated error', good[:-1] + ['[Error][Script] game/vanilla.ws: error'] + good[-1:], True)
check('wrong count', [s.replace('REGISTRY_CHECK_DONE checks=2', 'REGISTRY_CHECK_DONE checks=3') for s in good], False)
check('extra BEGIN after DONE', good[:-1] + ['REGISTRY_CHECK_BEGIN schema=1 fixture=registry2 key=registry'] + good[-1:], False)
paired = good[:3] + [good[2]] + good[3:]
check('source declares queue pair', paired, True, 2)
check('single declaration rejects pair', paired, False)
check('pair declaration rejects single', good, False, 2)
check('third prefix rejected', paired[:3] + [paired[2]] + paired[3:], False, 2)
check('later queue restart rejected', good[:4] + [good[2]] + good[4:], False, 2)
print(f'REGISTRY suite parser synthetic guards: {checks}/{checks}. No native acceptance.')
