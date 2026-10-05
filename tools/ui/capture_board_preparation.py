"""Record current board artifacts without implying runtime acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
from register_board import audit
from update_board_resource import validate_resource, validate_image_linkages

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / 'GwentB/myproject1/workspace'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--compile-dir', type=Path, default=ROOT / 'BetaGwent/build/board-compile88e')
args = parser.parse_args()
compile_report = json.loads((args.compile_dir / 'result.json').read_text())
compile_log = (args.compile_dir / 'stdout.txt').read_text(encoding='utf-8', errors='replace')
compile_log += (args.compile_dir / 'wcc.log').read_text(encoding='utf-8', errors='replace')
if (compile_report['exitCode'] != 0 or compile_report['timedOut']
        or not compile_report['artifacts'] or 'Success! Patch scripts blob saved' not in compile_log
        or '[Script]: Error [' in compile_log):
    raise SystemExit('Compile is not confirmed successful')
for artifact in compile_report['artifacts']:
    raw = Path(artifact['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest().upper() != artifact['sha256'].upper():
        raise SystemExit('Compiled artifact changed: ' + artifact['path'])
registration = audit()
native_resource, _ = validate_resource(WORKSPACE / 'betagwent/betagwent_board.redswf')
validate_image_linkages(native_resource)
authoritative = list((ROOT / 'BetaGwent/scripts/game/betagwent').glob('*.ws'))
authoritative += list((ROOT / 'BetaGwent/development/scripts/game/betagwent').glob('*.ws'))
authoritative += [ROOT / 'tools/core-check/src/coreChecks.ws']
source_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in authoritative}
source_hashes['capabilityProbe.ws'] = 'c54d6e718e918efd92853ac8317b6132ec643a8669a98aa5efb19b3ea2c3a941'
compiled_sources = {entry['path']: entry['sha256'] for entry in compile_report.get('patchSourcesBefore', [])}
if compiled_sources and (not compile_report.get('patchSourcesUnchangedDuringCompile')
                         or compile_report['patchSourcesBefore'] != compile_report['patchSourcesAfter']):
    raise SystemExit('Patch sources changed during compile')
if set(source_hashes) != {path.name for path in (WORKSPACE / 'scripts/game/betagwent').glob('*.ws')}:
    raise SystemExit('Unexpected active board source set')
files = []
for path in sorted((WORKSPACE / 'scripts/game/betagwent').glob('*.ws')):
    patch = ROOT / 'BetaGwent/build/board-patch/game/betagwent' / path.name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if not patch.exists() or digest != hashlib.sha256(patch.read_bytes()).hexdigest():
        raise SystemExit('Active source differs from compiled patch: ' + path.name)
    if digest != source_hashes[path.name]:
        raise SystemExit('Active source differs from authoritative source: ' + path.name)
    if compiled_sources and digest != compiled_sources.get('game/betagwent/' + path.name):
        raise SystemExit('Active source differs from recorded compile input: ' + path.name)
    files.append(dict(path=str(path), bytes=path.stat().st_size, sha256=digest,
                      matchesCompiledPatch=True, matchesAuthoritativeSource=True))
resources = []
for path in sorted((WORKSPACE / 'betagwent').glob('*')):
    if not path.is_file():
        continue
    data = path.read_bytes()
    if path.suffix in ('.redswf', '.menu', '.guiconfig') and data[:4] != b'CR2W':
        raise SystemExit('Unexpected resource signature: ' + str(path))
    resources.append(dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                          signature=data[:4].decode('ascii', errors='replace')))
log = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\editor.log')
lines = []
if log.exists():
    with log.open('rb') as stream:
        stream.seek(max(0, log.stat().st_size - 16 * 1024 * 1024))
        lines = stream.read().decode('utf-8', errors='replace').splitlines()[1:]
report_path = ROOT / 'docs/evidence/board-native-preparation.json'
prior = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
import_evidence = prior.get('editorImportEvidence', [])
import_evidence += [line for line in lines if 'betagwent_board' in line or 'SWF file magic' in line]
menu = WORKSPACE / 'betagwent/betagwent_board.menu'
menu_class_present = registration['menuProperties']['menuClass'] == 'CR4BetaGwentBoardMenu'
report = dict(compile=compile_report, activeSources=files, resources=resources,
              editorImportEvidence=list(dict.fromkeys(import_evidence)),
              redswfCreated=(WORKSPACE / 'betagwent/betagwent_board.redswf').exists(),
              menuClassConfigured=menu_class_present,
              menuRegistered=registration['savedRegistrationVerified'] and registration['projectOverlayApplied'],
              registration=registration, engineReloadVerified=False, runtimeVerified=False,
              encoding='UTF-8 BOM; original capability probe unchanged',
              editorScriptLoadEvidence=[line for line in lines if 'Script functions: successfully loaded' in line],
              priorAcceptedBoardEvidence=str(ROOT / 'docs/evidence/board-runtime-accepted-20261002.json'),
              priorAcceptedRequestEvidence=str(ROOT / 'docs/evidence/request-runtime-accepted-20261002.json'),
              priorAcceptedRequestFlowEvidence=str(ROOT / 'docs/evidence/request-flow-runtime-accepted-20261002.json'),
              priorAcceptedQueueAndLiveUIEvidence=str(ROOT / 'docs/evidence/native20-acceptance.json'),
              priorAcceptedApplyEvidence=str(ROOT / 'docs/evidence/native21-acceptance.json'),
              priorAcceptedManagerEvidence=str(ROOT / 'docs/evidence/native26-acceptance.json'),
              priorAcceptedNumericEvidence=str(ROOT / 'docs/evidence/native28-acceptance.json'),
              nativeImageLinkagePrefixVerified=True,
              priorAcceptedArtworkEvidence=str(ROOT / 'docs/evidence/artwork40-accepted-20261002.json'),
              previousHumanStage50Acceptance=str(ROOT / 'docs/evidence/duel50-user-acceptance.json'),
              note='Stage88: forty adapted deck_rules archetypes, seventy combo dependencies, own-zone mulligan/ordering/reserves, visible engine threats, actual Impera spy boost and one-card catch. Sixty WS sources match Wcc88e. Three stage87 menus and licensed1418-media audio retained. Native battle acceptance pending. No UI automation.')
report_path.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Preparation evidence captured; newer script patch runtime pending, prior board acceptance preserved separately.')
