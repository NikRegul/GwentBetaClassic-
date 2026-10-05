"""Capture REGISTRY22 with manager39/20/86 and numeric55 regressions."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from capture_action_runtime import ROOT, DEFAULT_LOG, parse_runtime
from capture_manager_runtime import parse_suite as parse_manager

def parse_suite(raw, log_name, key, power_key, manager_key, specs, action_begin_count=1):
    lines = raw.decode('utf-8', errors='replace').splitlines()
    starts = [i for i, line in enumerate(lines) if 'REGISTRY_SUITE_BEGIN schema=1' in line or 'REGISTRY_CHECK_SKIPPED no player' in line]
    suite = lines[starts[-1]:] if starts else []
    end = next((i for i, line in enumerate(suite) if 'REGISTRY_SUITE_END schema=1' in line), None)
    if end is not None: suite = suite[:end + 1]
    correct = bool(suite) and suite[0].endswith(f'REGISTRY_SUITE_BEGIN schema=1 key={key} power={power_key} manager={manager_key}')
    scoped = '\n'.join(suite).encode()
    manager, _ = parse_manager(scoped, log_name, manager_key, specs['ACTION'], specs['APPLY'], specs['MANAGER'])
    batches = dict(manager['batches'])
    for tag, label, contract in (('POWER', 'power', power_key), ('REGISTRY', 'registry', key)):
        batch, _ = parse_runtime(scoped, log_name, specs[tag], tag=tag,
            begin=f'{tag}_CHECK_BEGIN schema=1 fixture={label}{len(specs[tag])} key={contract}')
        batch['expectedChecks'] = batch.pop('expectedActionChecks')
        batch.pop('scope')
        batches[tag] = batch
    exact = True
    positions = []
    for tag, ids in specs.items():
        passes = [m.group(1) for line in suite if (m := re.search(rf'{tag}_CHECK_PASS (.+)$', line))]
        begins = [i for i, line in enumerate(suite) if tag + '_CHECK_BEGIN schema=1' in line]
        dones = [i for i, line in enumerate(suite) if tag + '_CHECK_DONE checks=' in line]
        expected = action_begin_count if tag == 'ACTION' else 1
        exact = exact and passes == ids and len(begins) == expected and len(dones) == 1
        if expected > 1:
            exact = exact and all(begins[i] == begins[0] + i for i in range(len(begins)))
            exact = exact and all(suite[i].endswith('ACTION_CHECK_BEGIN schema=1 fixture=queue39') for i in begins)
        positions.append((begins[-1] if begins else -1, dones[0] if dones else -1))
    ordered = all(0 < begin < done for begin, done in positions)
    ordered = ordered and all(positions[i][1] < positions[i + 1][0] for i in range(len(positions) - 1))
    manager_end = [i for i, line in enumerate(suite) if 'MANAGER_SUITE_END schema=1' in line]
    exact = exact and sum('MANAGER_SUITE_BEGIN schema=1' in line for line in suite) == 1 and len(manager_end) == 1
    ordered = ordered and bool(manager_end) and positions[2][1] < manager_end[0] < positions[3][0]
    errors = [line for i, line in enumerate(suite) if '[Error][Script]' in line and 'betagwent' in '\n'.join(suite[i:i + 3]).lower()]
    failures = [line for line in suite if re.search(r'(?:ACTION|APPLY|MANAGER|POWER|REGISTRY)_CHECK_FAIL ', line)]
    complete = correct and end is not None and exact and ordered and manager['expectedChecksComplete'] and all(b['expectedChecksComplete'] for b in batches.values()) and not errors and not failures
    return dict(log=str(log_name), logSha256=hashlib.sha256(raw).hexdigest(), suiteFound=bool(suite) and 'REGISTRY_SUITE_BEGIN schema=1' in suite[0],
        lastAttemptSkipped=bool(suite) and 'REGISTRY_CHECK_SKIPPED no player' in suite[0],
        correctContractKey=correct, expectedContractKey=key, expectedPowerContractKey=power_key, expectedManagerContractKey=manager_key,
        expectedActionBeginCount=action_begin_count, suiteEnded=end is not None, wholeSuiteMarkersExact=exact, batchesOrdered=ordered,
        batches=batches, checkFailures=failures, modScriptErrors=errors, expectedChecksComplete=complete,
        scope='Opaque allocator/lookup22 with numeric55 and manager/queue/Apply regressions. No original Register/Unregister, live registry, death, save or match acceptance.'), suite

def capture(log):
    e = ROOT / 'docs/evidence'
    def read(name): return json.loads((e / name).read_text(encoding='utf-8-sig'))
    registry = read('registry-id-check-preparation.json')
    power = read('power-number-check-preparation.json')
    manager = read('manager-check-preparation.json')
    queue = read('action-check-preparation.json')
    apply = read('apply-check-preparation.json')
    if registry['powerContractKey'] != power['contractKey'] or registry['managerContractKey'] != manager['contractKey']:
        raise RuntimeError('Nested contract version changed')
    sources = {}
    for manifest in (registry, power, manager, queue, apply):
        for name, digest in dict(manifest.get('baseSources', {}), **{Path(manifest['source']).name: manifest['sourceSha256']}).items():
            if name in sources and sources[name] != digest: raise RuntimeError('Manifest source conflict: ' + name)
            sources[name] = digest
    active = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent'
    for name, digest in sources.items():
        if hashlib.sha256((active / name).read_bytes()).hexdigest() != digest: raise RuntimeError('Active contract source mismatch: ' + name)
    queue_text = (active / Path(queue['source']).name).read_text(encoding='utf-8-sig')
    action_ids = re.findall(r'Check\("([^"]+)"', queue_text)
    count = queue_text.count('LogChannel(\'BetaGwent\', "ACTION_CHECK_BEGIN schema=1 fixture=queue39");')
    if count not in (1, 2): raise RuntimeError('Unexpected authenticated queue BEGIN declarations')
    specs = dict(ACTION=action_ids, APPLY=apply['expectedIds'], MANAGER=manager['expectedIds'], POWER=power['expectedIds'], REGISTRY=registry['expectedIds'])
    report, suite = parse_suite(log.read_bytes(), log, registry['contractKey'], power['contractKey'], manager['contractKey'], specs, count)
    report['activeSources'] = sources
    (e / 'registry-id-runtime-result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (e / 'registry-id-runtime-trace.txt').write_text('\n'.join(suite) + ('\n' if suite else ''), encoding='utf-8')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, default=DEFAULT_LOG)
    result = capture(parser.parse_args().log)
    print(json.dumps({key: result[key] for key in ('suiteFound', 'correctContractKey', 'expectedChecksComplete', 'checkFailures', 'modScriptErrors')}, indent=2))
