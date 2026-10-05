"""Native allocator/lookup recipes, tied to exact original16 observations."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(value, message):
    if not value: raise RuntimeError(message)

original = read(E / 'beta-registry-id-fixtures.json')
extract = read(E / 'beta-registry-id-extraction.json')
require(original['checks'] == original['passed'] == 16 and original['failed'] == 0, 'Original16 incomplete')
require(original['originalCodeExecuted'] and not original['originalAssemblyLoaded'] and
    original['copiedMethods'] == 4 and original['explicitShims'] == 0, 'Original scope changed')
for field in ('source', 'extract'):
    require(sha(Path(extract[field])).upper() == extract[field + 'Sha256'], 'Extraction identity changed')
require(original['extractSha256'] == extract['extractSha256'] and all(m['exactInstructionMatch'] for m in extract['methods']), 'IL changed')
harness = ROOT / 'tools/oracle/beta-registry-id-ref/Program.cs'
require(sha(harness).upper() == original['harnessSha256'], 'Harness changed')
require(sha(ROOT / 'tools/oracle/extract_beta_registry_ids.ps1').upper() == extract['extractorSha256'], 'Extractor changed')
support_path = ROOT / 'tools/core-check/src/registryIdCheckSupport.ws'
support = support_path.read_text(encoding='utf-8-sig')
guards = re.findall(r'Check\("([^"]+)"', support)
require(len(guards) == len(set(guards)) == 10, 'Expected guards10')
power = read(E / 'power-number-check-preparation.json')
manager = read(E / 'manager-check-preparation.json')
base = {'registryIds.ws': sha(ROOT / 'BetaGwent/scripts/game/betagwent/registryIds.ws')}
inputs = dict(baseSources=base, powerContractKey=power['contractKey'], managerContractKey=manager['contractKey'],
    oracleSha256=sha(E / 'beta-registry-id-fixtures.json'), supportSha256=sha(support_path), generatorSha256=sha(Path(__file__)))
key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
observations = original['observations'][:12]
require(all(o['passed'] for o in observations), 'Original fixtures failed')
recipes = []
def recipe(index, setup, expression):
    o = observations[index]
    recipes.append((o['id'], setup, expression))
def ids(o):
    return '\n'.join(f'        ok = f.Allocate(id) && ok; ok = id == {v} && ok;' for v in o['actual']['ids'])
v = observations[0]['actual']
recipe(0, '        ok = true;\n' + ids(observations[0]), f'ok && f.GetNextId() == {v["next"]} && f.Capacity() == {v["capacity"]}')
v = observations[1]['actual']
recipe(1, '        f.State(63, 64); f.Slot(2, card);\n        ok = f.Allocate(id);\n'
    f'        ok = id == {v["first"]} && f.Capacity() == {v["capacityBefore"]} && ok;\n        ok = f.Allocate(id) && ok;',
    f'ok && id == {v["second"]} && f.Capacity() == {v["capacityAfter"]} && f.GetNextId() == {v["next"]} && f.GetCard(2) == card')
v = observations[2]['actual']
recipe(2, '        f.State(128, 128); f.Slot(127, card); ok = f.Allocate(id);',
    f'ok && id == {v["id"]} && f.Capacity() == {v["capacity"]} && f.GetNextId() == {v["next"]} && f.GetCard(127) == card')
v = observations[3]['actual']
recipe(3, '        f.Recycle(9); f.Recycle(4); ok = true;\n' + ids(observations[3]),
    f'ok && f.GetNextId() == {v["next"]} && f.Capacity() == {v["capacity"]} && f.RecycledCount() == {v["recycledLeft"]}')
v = observations[4]['actual']
recipe(4, '        f.Recycle(7); f.Recycle(7); ok = true;\n' + ids(observations[4]), f'ok && f.GetNextId() == {v["next"]}')
v = observations[5]['actual']
recipe(5, '        f.State(64, 64); f.Recycle(5); ok = f.Allocate(id);',
    f'ok && id == {v["id"]} && f.GetNextId() == {v["next"]} && f.Capacity() == {v["capacity"]}')
v = observations[6]['actual']
recipe(6, '        f.State(65535, 65536); ok = true;\n' + ids(observations[6]),
    f'ok && f.GetNextId() == {v["next"]} && f.Capacity() == {v["capacity"]}')
for index, lookup in enumerate((1, 2, 0, 64, 65535), 7):
    require(observations[index]['actual'] is True, 'Unexpected lookup result')
    recipe(index, '        f.Slot(1, card);', 'f.GetCard(1) == card' if lookup == 1 else f'!f.GetCard({lookup})')
lines = [support]
for index, (label, setup, expr) in enumerate(recipes):
    if index % 4 == 0:
        if index: lines.append('    }')
        lines += [f'    private function RunOriginal{index // 4}()', '    {',
            '        var f : CBetaGwentRegistryIdCheckFixture;', '        var card : CBetaGwentRegistryCardReference;',
            '        var id : int;', '        var ok : bool;', '        card = new CBetaGwentRegistryCardReference in this;']
    lines += ['        f = new CBetaGwentRegistryIdCheckFixture in this; f.Initialize();', setup,
        f'        Check("{label}", {expr});']
lines += ['    }', '    public function Run()', '    {', '        checks = 0; failures = 0;',
    f'        LogChannel(\'BetaGwent\', "REGISTRY_CHECK_BEGIN schema=1 fixture=registry22 key={key}");',
    '        RunOriginal0(); RunOriginal1(); RunOriginal2(); RunGuards();',
    '        LogChannel(\'BetaGwent\', "REGISTRY_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);',
    '    }', '}', '', 'exec function bgregistry_check()', '{',
    '    var runner : CBetaGwentRegistryIdCheckRunner;', '    var power : CBetaGwentPowerNumberCheckRunner;',
    '    if (!thePlayer) { LogChannel(\'BetaGwent\', "REGISTRY_CHECK_SKIPPED no player"); return; }',
    f'    LogChannel(\'BetaGwent\', "REGISTRY_SUITE_BEGIN schema=1 key={key} power={power["contractKey"]} manager={manager["contractKey"]}");',
    '    BetaGwentRunManagerChecks();', '    power = new CBetaGwentPowerNumberCheckRunner in thePlayer; power.Run();',
    '    runner = new CBetaGwentRegistryIdCheckRunner in thePlayer; runner.Run();',
    '    LogChannel(\'BetaGwent\', "REGISTRY_SUITE_END schema=1");',
    '    theGame.GetGuiManager().ShowNotification("ID карт: " + (22 - runner.Failures()) + "/22, ошибок: " + runner.Failures(), 8.0);', '}']
source = ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentRegistryIdChecks.ws'
source.write_text('\n'.join(lines) + '\n', encoding='utf-8-sig')
report = dict(expectedRegistryChecks=22, originalChecksMapped=12, originalChecksTotal=16,
    unmappedOriginalObservations=[dict(id=o['id'], reason='CLR null array/stack state cannot be represented by WS value arrays.') for o in original['observations'][12:]],
    nativeOnlyChecks=guards, contractKey=key, contractInputs=inputs, baseSources=base,
    powerContractKey=power['contractKey'], managerContractKey=manager['contractKey'],
    source=str(source), sourceSha256=sha(source), expectedIds=[o['id'] for o in observations] + guards,
    associations=observations, generatorSha256=sha(Path(__file__)), runtimeVerified=False,
    scope='Opaque references; allocator UInt16 wrap/LIFO/growth and lookup only. Local reconstruction guards10. No ctor, Register/Unregister events, live card state, death, save or complete registry acceptance.')
(E / 'registry-id-check-preparation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(f'Prepared REGISTRY22: original12 mapped + guards10; four null-container originals explicitly unmapped. key={key}')
