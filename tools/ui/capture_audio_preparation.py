"""Record audio preparation separately from unperformed Wwise/runtime checks."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
import argparse

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/evidence'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', choices=['79a', '79b', '79c', '79d', '79e', '80', '81', '86', '87'])
args = parser.parse_args()
source = json.loads((EVIDENCE / 'beta-audio-extract79.json').read_text('utf8'))
imported = json.loads((EVIDENCE / 'audio-import79.json').read_text('utf8'))
prepared = json.loads((EVIDENCE / 'board-native-preparation.json').read_text('utf8'))
bridge = json.loads((EVIDENCE / 'board-bridge-bytecode.json').read_text('utf8'))
resource = json.loads((EVIDENCE / 'board-resource-update.json').read_text('utf8'))
project = Path(imported['project'])
audio_script = (ROOT / 'BetaGwent/development/scripts/game/betagwent/duelAudio.ws').read_text('utf-8-sig')
native_events = set(re.findall(r'"(gui_[a-z0-9_]+)"', audio_script))
native_xml = ET.parse(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\assets\w3_audio\Events\gui.wwu')
declared_events = {event.get('Name') for event in native_xml.iter('Event')}
if native_events - declared_events:
    raise RuntimeError('Undeclared native fallback sound')
files = []
for item in imported['media']:
    wav = project.parent / 'Originals/SFX/BetaGwent79' / (item['key'] + '.wav')
    if hashlib.sha256(wav.read_bytes()).hexdigest() != item['source']['sha256']:
        raise RuntimeError('Prepared media changed')
for path in sorted(project.parent.rglob('*')):
    if not path.is_file() or path.suffix not in ['.wwu', '.wproj']:
        continue
    ET.parse(path)
    files.append(dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
catalog = (ROOT / 'BetaGwent/development/scripts/game/betagwent/duelAudioCatalog.ws').read_text('utf-8-sig')
installed = 'function BetaGwentAudioBankInstalled() : bool { return true; }' in catalog
bank_report = None
if installed:
    bank_report = json.loads((EVIDENCE / 'audio-bank-build79.json').read_text('utf8'))
    target = Path(bank_report['target'])
    if not bank_report['installed'] or bank_report['exitCode'] != 0 or hashlib.sha256(target.read_bytes()).hexdigest() != bank_report['sha256']:
        raise RuntimeError('Installed audio bank differs from successful build')
if not bridge['passed'] or len(bridge['bindings']) != (44 if args.stage in ['86','87'] else 36 if args.stage=='81' else 35 if args.stage=='80' else 34 if args.stage in ['79c','79d','79e'] else 33) or not resource['applied']:
    raise RuntimeError('Current UI/resource is not verified prepared')
stage = args.stage or ('79b' if installed else '79a')
report = dict(stage=stage, scriptCompileStage=stage, currentResourceSha256=resource['updatedSha256'],
    scriptSources=len(prepared['activeSources']), uiFunctions=len(bridge['bindings']),
    nativeFallbackEvents=sorted(native_events), originalFilesModified=False,
    extractedBanks=len(source['banks']), russianCardClips=sum(v['role']=='cards' for v in source['voices']),
    russianAnnouncerClips=sum(v['role']=='announcer' for v in source['voices']),
    decodedRussianClips=sum('pcm' in v for v in source['voices']),
    preparedMediaCount=imported['mediaCount'], preparedVoiceClips=sum(m['role']=='voice' for m in imported['media']),
    preparedEffectClips=sum(m['role']=='sfx' for m in imported['media']),
    preparedVoiceBindings=imported['voiceBindings'], preparedEffectBindings=imported['effectBindings'],
    generatedProjectFiles=files, wwiseBankBuildVerified=installed, betaBankInstalled=installed,
    bankBuild=bank_report,
    runtimeSoundVerified=stage in ['79e','80','81'], runtimeVoicesVerified=False,
    priorHumanAudioAcceptance=str(EVIDENCE/'stage79d-user-acceptance.json') if stage in ['79e','80','81'] else None,
    latestObservedNativeLoadFailureEvidence=str(EVIDENCE / 'audio79d-user-log.txt') if stage=='79d' else str(EVIDENCE / 'audio79-reload-required.json') if stage=='79c' else None,
    nativeRuntimeInstallationEvidence=str(EVIDENCE / 'audio79-runtime-install.json') if stage=='79d' else None,
    authorizationsConsumedOnce=True, audioUsesMatchRng=False,
    controls=['effects on/off','voice on/off' if installed else 'voice on/off (disabled until bank installation)'],
    cancellation=['skip replay','deck selection/restart','rematch','menu close'],
    limitations=['Current UX runtime not yet observed; prior bank sounds accepted by user.' if stage in ['79e','80','81'] else 'Native GUI fallback is written and compiled, awaiting playback check.',
                 'Mixed-case lookup corrected and additional native loose bank installed; restart/actual load/audio pending.' if stage=='79d' else 'User/log confirmed nativeLoaded=false; manual REDkit registration and audible playback pending.' if stage=='79c' else 'Prior bank sounds accepted; complete voice coverage remains pending.' if stage in ['80','81'] else 'First Beta bank is compiled and installed; native loading/audible playback pending.' if installed else 'Original Beta effects/voices remain inactive pending bank installation.',
                 'Installed Wwise trial permits200 media; complete coverage needs an appropriate project license.',
                 'First voice and a rendered standard effect variant; conditional/weighted VO pending.',
                 'Settings last only for the current menu; fixed Russian clips routed through GUI.'])
if stage in ['86','87']:
    runtime=json.loads((EVIDENCE/'audio79-runtime-install.json').read_text('utf8'))
    assert installed and imported['fullImport'] and bank_report['embeddedMedia']==imported['mediaCount']>200
    assert runtime['installed'] and runtime['sha256']==bank_report['sha256']
    assert hashlib.sha256(Path(runtime['target']).read_bytes()).hexdigest()==bank_report['sha256']
    report.update(licensedFullBankBuildVerified=True,preparedVoiceVariantBindings=imported['voiceVariantBindings'],
        originalVoiceWeights=True,originalVoiceTriggers=True,betaUiBindings=imported['uiBindings'],
        betaCueBindings=imported['cueBindings'],betaWeatherBindings=imported['weatherBindings'],
        betaAmbushBindings=imported['ambushBindings'],betaTransformBindings=imported['transformBindings'],
        nativeRuntimeInstallationEvidence=str(EVIDENCE/'audio79-runtime-install.json'),
        priorHumanAudioAcceptance=str(EVIDENCE/'stage79d-user-acceptance.json'),
        limitations=['Expanded bank playback and animation timing await human acceptance.',imported['limitation'],
                     'Fixed Russian clips routed through GUI; menu settings last for the current session.'])
(EVIDENCE / 'audio79-preparation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
shutil.copyfile(EVIDENCE/'audio79-preparation.json',EVIDENCE/('stage'+stage+'-audio-preparation.json'))
for filename in ['board-native-preparation.json','board-resource-update.json','board-build.json',
                 'board-bridge-bytecode.json','card-art-build.json']:
    shutil.copyfile(EVIDENCE / filename, EVIDENCE / ('stage' + stage + '-' + filename))
print(f'Audio{stage} captured: {len(native_events)} native events, {imported["mediaCount"]} WAVs, bank installed={installed}; prior audio acceptance stored separately.')
