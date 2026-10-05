"""Stage the single additional Beta bank for a manual REDkit soundbank reload.

Does not automate REDkit, edit its installation/depot, publish, or install Init.
"""
from pathlib import Path
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
report = json.loads((ROOT / 'docs/evidence/audio-bank-build79.json').read_text('utf-8'))
bank = Path(report['bank'])
target = Path(report['target'])
digest = hashlib.sha256(bank.read_bytes()).hexdigest()
if not report['installed'] or digest != report['sha256'] or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
    raise SystemExit('Built/installed bank mismatch')
info = ET.parse(bank.parent / 'SoundbanksInfo.xml')
banks = info.getroot().find('SoundBanks')
selected = [b for b in banks if b.findtext('ShortName') == 'BetaGwent79']
if len(selected) != 1 or selected[0].findtext('Path') != bank.name:
    raise SystemExit('Unexpected bank metadata')
for b in list(banks):
    if b is not selected[0]:
        banks.remove(b)
for media in selected[0].findall('./Media/File'):
    if media.get('Streaming') != 'false' or media.get('Location') != 'Memory':
        raise SystemExit('Reload package requires self-contained embedded media')
out = ROOT / 'BetaGwent/build/audio79-redkit-reload'
out.mkdir(parents=True, exist_ok=True)
if (out / 'Init.bnk').exists():
    raise SystemExit('Init must not be included in this package')
shutil.copyfile(bank, out / bank.name)
info.getroot().find('./RootPaths/ProjectRoot').text = str(ROOT / 'BetaGwent/audio/wwise')
info.getroot().find('./RootPaths/SourceFilesRoot').text = str(ROOT / 'BetaGwent/audio/wwise/.cache/Windows')
ET.indent(info, space='\t')
info.write(out / 'SoundbanksInfo.xml', encoding='utf-8', xml_declaration=True)
shutil.copyfile(bank.parent / 'BetaGwent79.txt', out / 'BetaGwent79.txt')
result = dict(package=str(out), bank=str(out / bank.name), sha256=digest,
    additionalBankOnly=True, initIncluded=False, runtimeLoaded=False,
    userReportedNoVoiceAndClassicEffects=True,
    logEvidence=['2026.10.04 15:06:14 AUDIO_BANK_PENDING nativeLoaded=false',
                 '2026.10.04 15:08:47 AUDIO_BANK_PENDING nativeLoaded=false'],
    manualAction='REDkit Tools > Sound > Reload soundbanks; select BetaGwent79',
    generatedBankFolder=str(bank.parent), wwiseProject=str(ROOT / 'BetaGwent/audio/wwise/BetaGwent79.wproj'),
    source='https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/6327994/HOW-TO%3A%2BImplement%2Bsounds%2Band%2Buse%2BWwise')
(ROOT / 'docs/evidence/audio79-reload-required.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n','utf-8')
print('Additional bank reload package prepared; manual registration and audible playback still required.')
