"""Bind numeric fixtures, installed source set and compile28; no native claim."""
import ast
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value, message):
    if not value: raise RuntimeError(message)

compile_report = read(ROOT / 'BetaGwent/build/board-compile28/result.json')
prep = read(E / 'board-native-preparation.json')
require(prep['compile'] == compile_report and compile_report['exitCode'] == 0 and not compile_report['timedOut'], 'Compile association failed')
require(compile_report['patchSourcesBefore'] == compile_report['patchSourcesAfter'] and compile_report['patchSourcesUnchangedDuringCompile'], 'Compile inputs changed')
stdout = (ROOT / 'BetaGwent/build/board-compile28/stdout.txt').read_text(encoding='utf-8', errors='replace')
require('Success! Patch scripts blob saved' in stdout and '[Script]: Error [' not in stdout, 'Compiler diagnostics')
for artifact in compile_report['artifacts']:
    require(sha(Path(artifact['path'])).upper() == artifact['sha256'], 'Blob changed')
require(len(compile_report['artifacts']) == 1, 'Expected one blob')
active = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent'
compiled = {Path(item['path']).name: item['sha256'] for item in compile_report['patchSourcesBefore']}
sources = {p.name: p for p in (ROOT / 'BetaGwent/scripts/game/betagwent').glob('*.ws')}
sources.update({p.name: p for p in (ROOT / 'BetaGwent/development/scripts/game/betagwent').glob('*.ws')})
sources['coreChecks.ws'] = ROOT / 'tools/core-check/src/coreChecks.ws'
require(len(compiled) == len(list(active.glob('*.ws'))) == len(prep['activeSources']) == 24, 'Expected active24')
require(set(sources) | {'capabilityProbe.ws'} == set(compiled), 'Unexpected source set')
for name, digest in compiled.items():
    require((active / name).read_bytes().startswith(b'\xef\xbb\xbf'), 'Missing BOM: ' + name)
    require(sha(active / name) == sha(ROOT / 'BetaGwent/build/board-patch/game/betagwent' / name) == digest, 'Active/patch/compile mismatch')
    if name in sources: require(sha(sources[name]) == digest, 'Authoritative mismatch')
accepted = read(E / 'native26-acceptance.json')
require(accepted['managerChecksVerified'] and accepted['sourceCount'] == 22 and sha(Path(accepted['log'])) == accepted['logSha256'], 'Native26 evidence changed')
changed = []
for item in accepted['sources']:
    require(sha(Path(item['frozen'])) == item['sha256'], 'Frozen source changed')
    if compiled[item['name']] != item['sha256']: changed.append(item['name'])
require(changed == ['actionManager.ws', 'developmentManagerChecks.ws'], 'Unexpected prior source change: ' + str(changed))
for resource in accepted['resources']:
    require(sha(Path(resource['path'])) == resource['sha256'], 'GUI/Flash changed')
manager = read(E / 'manager-check-preparation.json')
for name, digest in manager['baseSources'].items(): require(digest == compiled[name], 'Manager base mismatch')
require(sha(Path(manager['source'])) == manager['sourceSha256'] == compiled['developmentManagerChecks.ws'], 'Manager suite mismatch')
for label, total, copied, seams in (('power-numeric', 40, 18, 1), ('registry-id', 16, 4, 0)):
    original = read(E / ('beta-' + label + '-fixtures.json'))
    extract = read(E / ('beta-' + label + '-extraction.json'))
    require(original['checks'] == original['passed'] == total and original['failed'] == 0 and original['originalCodeExecuted'], 'Oracle incomplete: ' + label)
    require(original['copiedMethods'] == copied and original['explicitShims'] == seams and not original['originalAssemblyLoaded'], 'Oracle scope: ' + label)
    require(all(m['exactInstructionMatch'] for m in extract['methods']), 'IL mismatch')
    for field in ('source', 'extract'): require(sha(Path(extract[field])).upper() == extract[field + 'Sha256'], 'Extraction identity changed')
    require(original['extractSha256'] == extract['extractSha256'], 'Oracle association changed')
    stem = 'beta-power-numeric-ref' if label == 'power-numeric' else 'beta-registry-id-ref'
    require(sha(ROOT / 'tools/oracle' / stem / 'Program.cs').upper() == original['harnessSha256'], 'Harness changed')
manifest = read(E / 'power-number-check-preparation.json')
require(manifest['expectedPowerChecks'] == 55 and manifest['originalChecks'] == 40 and len(manifest['nativeOnlyChecks']) == 15, 'Native55 count')
require(sha(Path(manifest['source'])) == manifest['sourceSha256'] == compiled['developmentPowerNumberChecks.ws'], 'Native source mismatch')
for name, digest in manifest['baseSources'].items(): require(digest == compiled[name], 'Numeric base mismatch')
inputs = manifest['contractInputs']
require(inputs['managerContractKey'] == manager['contractKey'] == manifest['managerContractKey'], 'Manager version mismatch')
require(inputs['supportSha256'] == sha(ROOT / 'tools/core-check/src/powerNumberCheckSupport.ws'), 'Support changed')
require(inputs['generatorSha256'] == manifest['generatorSha256'] == sha(ROOT / 'tools/core-check/generate_power_number_checks.py'), 'Generator changed')
require(inputs['oracleSha256'] == manifest['originalFixtureSha256'] == sha(E / 'beta-power-numeric-fixtures.json'), 'Original observations changed')
key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
require(key == manifest['contractKey'], 'Power version mismatch')
ids = re.findall(r'Check\("([^"]+)"', Path(manifest['source']).read_text(encoding='utf-8-sig'))
require(set(ids) == set(manifest['expectedIds']) and len(ids) == len(set(ids)) == 55, 'Numeric IDs mismatch')
death = read(E / 'beta-death-boundaries.json')
require(death['methodCount'] == 26 and not death['originalCodeExecuted'] and
    sha(Path(death['ilPath'])).upper() == death['ilSha256'], 'Death static scope/identity')
runtime = read(E / 'power-number-runtime-result.json')
native = runtime['expectedChecksComplete'] and runtime['correctContractKey'] and runtime['expectedContractKey'] == key
scripts = ['tools/recon/accept_native26.py', 'tools/recon/audit_power_number_preparation.py',
    'tools/core-check/generate_power_number_checks.py', 'tools/core-check/capture_power_number_runtime.py',
    'tools/core-check/check_power_number_capture.py', 'tools/core-check/capture_action_runtime.py']
for filename in scripts: ast.parse((ROOT / filename).read_text(encoding='utf-8'))
report = dict(latestCompile=compile_report, activeSourceCount=24,
    previousNativeManagerAcceptance=str(E / 'native26-acceptance.json'), priorSourcesUnchanged=20,
    modifiedPriorSources=changed, resourcesUnchanged=True, powerNumericBoundaryWritten=True,
    originalNumericChecksPassed=40, copiedNumericMethods=18, explicitNumericShims=1,
    expectedNativeChecks=dict(ACTION=39, APPLY=20, MANAGER=86, POWER=55),
    numericNativeVerified=native, contractKey=key, managerContractKey=manager['contractKey'],
    runtime=str(E / 'power-number-runtime-result.json'), originalRegistryIdChecksPassed=16,
    registryIdDraftInstalled=False, registryDeathStaticMethodsRead=26,
    realPowerEventsWritten=False, armorAbsorptionWritten=False, deathDrainWritten=False,
    fullRegistryWritten=False, completeMatchWritten=False, parserSyntheticChecksPassed=22,
    nextManualStep='Restart REDkit -> test save -> bgpower_check(); combined39/20/86/55. No Flash import.',
    nextDevelopment='Live final setter/events/death, exact death boundary fixtures, UInt16 registry/ID reuse, then selected card handlers and scheduler.',
    scope='Numeric setters/restore/armor add and multiply with raw final-setter seam. Bool failure differences and Int32 float range guards explicit; no real card effects/full match acceptance.')
(E / 'power-number-development-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
audit = dict(passed=True, activeCompileInputsVerified=24, accepted26SourcesUnchanged=20,
    changedAcceptedSources=changed, resourcesUnchanged=True, originalNumericChecksPassed=40,
    numericNativeExpectedChecks=55, numericNativeVerified=native, contractKey=key,
    originalRegistryIdChecksPassed=16, registryDraftInstalled=False, staticDeathMethods=26, pythonSyntaxFiles=len(scripts))
(E / 'power-number-preparation-audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
print(json.dumps(audit, indent=2))
