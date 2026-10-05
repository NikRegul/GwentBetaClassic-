"""Verify installed manager/driver preparation against immutable native21 inputs."""
import ast
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/evidence'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value, message):
    if not value: raise RuntimeError(message)

compile_report = read(ROOT / 'BetaGwent/build/board-compile26/result.json')
prep = read(E / 'board-native-preparation.json')
require(prep['compile'] == compile_report and compile_report['exitCode'] == 0 and not compile_report['timedOut'], 'Compile association/status')
require(compile_report['patchSourcesUnchangedDuringCompile'] and compile_report['patchSourcesBefore'] == compile_report['patchSourcesAfter'], 'Compile inputs changed')
log = (ROOT / 'BetaGwent/build/board-compile26/stdout.txt').read_text(encoding='utf-8', errors='replace')
require('Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log, 'Compiler diagnostics')
require(len(compile_report['artifacts']) == 1, 'Expected one compiled blob')
artifact = compile_report['artifacts'][0]
require(sha(Path(artifact['path'])).upper() == artifact['sha256'], 'Blob changed')
active = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent'
authoritative = {p.name: p for p in (ROOT / 'BetaGwent/scripts/game/betagwent').glob('*.ws')}
authoritative.update({p.name: p for p in (ROOT / 'BetaGwent/development/scripts/game/betagwent').glob('*.ws')})
authoritative['coreChecks.ws'] = ROOT / 'tools/core-check/src/coreChecks.ws'
compiled = {Path(item['path']).name: item['sha256'] for item in compile_report['patchSourcesBefore']}
require(len(compiled) == len(prep['activeSources']) == len(list(active.glob('*.ws'))) == 22, 'Source count')
require(set(authoritative) | {'capabilityProbe.ws'} == set(compiled), 'Authoritative set')
for name, digest in compiled.items():
    path = active / name
    require(path.read_bytes().startswith(b'\xef\xbb\xbf'), 'Missing BOM')
    require(sha(path) == digest == sha(ROOT / 'BetaGwent/build/board-patch/game/betagwent' / name), 'Active/patch/compile mismatch')
    if name in authoritative: require(digest == sha(authoritative[name]), 'Authoritative mismatch')
accepted = read(E / 'native21-acceptance.json')
require(accepted['applyChecksVerified'] and accepted['sourceCount'] == 20, 'Native21 incomplete')
require(sha(Path(accepted['log'])) == accepted['logSha256'], 'Frozen log changed')
changed = []
for item in accepted['sources']:
    require(sha(Path(item['frozen'])) == item['sha256'], 'Frozen accepted source changed')
    if sha(active / item['name']) != item['sha256']: changed.append(item['name'])
require(changed == ['actionQueue.ws'], 'Unexpected accepted source mutation: ' + str(changed))
for item in accepted['resources']:
    require(sha(Path(item['path'])) == item['sha256'], 'Accepted GUI/Flash resource changed')
require(compiled['capabilityProbe.ws'] == 'c54d6e718e918efd92853ac8317b6132ec643a8669a98aa5efb19b3ea2c3a941', 'Capability mutation')
oracle = read(E / 'beta-manager-apply-fixtures.json')
extract = read(E / 'beta-manager-apply-extraction.json')
require(oracle['checks'] == oracle['passed'] == 56 and not oracle['failed'], 'Original manager56 failure')
require(oracle['copiedMethods'] == 4 and oracle['explicitShims'] == 24 and not oracle['originalAssemblyLoaded'], 'Original scope')
require(oracle['extractSha256'] == extract['extractSha256'] == sha(Path(extract['extract'])).upper(), 'Original extraction identity')
require(all(item['exactInstructionMatch'] for item in extract['methods']), 'Instruction mismatch')
for item in extract['metadataDependencies']: require(sha(Path(item['path'])).upper() == item['sha256'], 'Metadata dependency mutation')
manifest = read(E / 'manager-check-preparation.json')
require(manifest['expectedManagerChecks'] == 86 and manifest['originalChecks'] == 56 and len(manifest['nativeOnlyChecks']) == 30, 'Native fixture count')
require(manifest['sourceSha256'] == sha(Path(manifest['source'])) == compiled[Path(manifest['source']).name], 'Native fixture source association')
require(manifest['originalFixtureSha256'] == sha(E / 'beta-manager-apply-fixtures.json'), 'Oracle observations changed')
require(manifest['originalHarnessSha256'] == sha(ROOT / 'tools/oracle/beta-manager-apply-ref/Program.cs'), 'Oracle harness changed')
require(manifest['generatorSha256'] == sha(ROOT / 'tools/core-check/generate_manager_checks.py'), 'Generator changed')
for name, digest in manifest['baseSources'].items(): require(digest == compiled[name], 'Base source manifest mismatch')
inputs = manifest['contractInputs']
require(inputs['supportSha256'] == sha(ROOT / 'tools/core-check/src/managerCheckSupport.ws'), 'Support template changed')
require(inputs['integrationSha256'] == sha(ROOT / 'tools/core-check/src/managerCheckIntegration.ws'), 'Integration template changed')
key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
require(key == manifest['contractKey'], 'Contract version changed')
power = read(E / 'beta-power-primitives.json')
require(power['methodCount'] == len(power['methods']) == 111 and not power['originalCodeExecuted'], 'Power static scope')
require(sha(Path(power['source'])).upper() == power['sourceSha256'] and sha(Path(power['ilPath'])).upper() == power['ilSha256'], 'Power evidence identity')
runtime = read(E / 'manager-runtime-result.json')
native = runtime['expectedChecksComplete'] and runtime['correctContractKey'] and runtime['expectedContractKey'] == key
files = ['tools/recon/accept_native21.py', 'tools/recon/audit_manager_preparation.py',
    'tools/core-check/generate_manager_checks.py', 'tools/core-check/capture_manager_runtime.py',
    'tools/core-check/check_manager_capture.py', 'tools/core-check/capture_action_runtime.py',
    'tools/ui/capture_board_preparation.py']
for name in files: ast.parse((ROOT / name).read_text(encoding='utf-8'))
development = dict(latestCompile=compile_report, activeSourceCount=22,
    priorNativeApplyAcceptance=str(E / 'native21-acceptance.json'), priorSourcesUnchanged=19,
    modifiedPriorSources=changed, resourcesUnchanged=True, managerPolicyBoundaryWritten=True,
    mutableQueueAuthorityWritten=True, boundedQueueDriverWritten=True, maxStepsPerBudget=256,
    realCardEffectHandlersWritten=False, realServiceAdaptersWritten=False, fullSchedulerWritten=False,
    delay64Representation='Signed high int32 and raw low int32; no truncation, positive test and unchanged pause argument.',
    originalManagerChecksPassed=56, originalManagerCopiedMethods=4, originalBoundaryShims=24,
    expectedNativeChecks=dict(ACTION=39, APPLY=20, MANAGER=86), nativeManagerVerified=native,
    contractKey=key, preparation=str(E / 'manager-check-preparation.json'), runtime=str(E / 'manager-runtime-result.json'),
    parserSyntheticChecksPassed=16, powerStaticMethodsRead=111, powerHandlersVerified=False,
    manualInstruction=str(ROOT / 'GwentB/myproject1/BOARD_CHECK.md'),
    manualChecksDeferredByUser=True,
    deferredUntil='User returns and resumes sequential checks; do not request a run while developing.',
    nextManualStep='On return: restart REDkit -> test save -> bgmanager_check(); command runs ACTION39/APPLY20/MANAGER86. No Flash import.',
    nextDevelopment='Exact power numeric fixtures, registry/services/event and waiting-to-die primitives; then ability/request/controller interleaving.',
    scope='ApplyAction policy and bounded queue driver. Synthetic service fixtures; CLR exceptions become bool+latched fault. No actual effects/network/clock/cache/full scheduler.')
(E / 'manager-development-result.json').write_text(json.dumps(development, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
audit = dict(passed=True, activeCompileInputsVerified=22, accepted21SourcesUnchanged=19,
    changedAcceptedSources=changed, resourcesUnchanged=True, originalManagerChecksPassed=56,
    nativeManagerExpectedChecks=86, nativeManagerVerified=native, pythonSyntaxFiles=len(files),
    powerMethodsStaticOnly=111, contractKey=key)
(E / 'manager-preparation-audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
print(json.dumps(audit, indent=2))
