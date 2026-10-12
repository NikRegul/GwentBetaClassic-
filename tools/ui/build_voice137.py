"""Five isolated voice variants with identical events and actual phrase durations."""
import hashlib
import json
import re
import shutil
import subprocess
import wave
import xml.etree.ElementTree as ET
from pathlib import Path
from build_voice_mix135 import inventory

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = {'en': 'wwise-en89', 'ru': 'wwise', 'de': 'wwise-de137',
            'it': 'wwise-it137', 'pt-br': 'wwise-pt-br137'}
LOCALES = {'de': 'de_de', 'it': 'it_it', 'pt-br': 'pt_br'}
DEFAULT_TEXT = {'en': 2, 'ru': 1, 'de': 3, 'it': 5, 'pt-br': 9}
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
# Distinct per voice package: installing another package resets the text language once
# to that package's language (EN -> English, RU -> Russian, ...); later choices persist.
PACKAGE_ID = {'en': 1001, 'ru': 1002, 'de': 1003, 'it': 1004, 'pt-br': 1005}


def language_bridge(text, language):
    old = 'FlashArgInt(FactsQueryLatestValue("bg_text_language"))'
    assert text.count(old) == 1
    text = text.replace(old, 'FlashArgInt(BetaGwentTextLanguage137(FactsQueryLatestValue("bg_text_language")))')
    default, package = DEFAULT_TEXT[language], PACKAGE_ID[language]
    return text + ('\nfunction BetaGwentTextLanguage137(value:int):int\n{\n'
                   f'    if(FactsQueryLatestValue("bg_text_language_package")!={package})\n'
                   f'    {{ FactsSet("bg_text_language_package",{package});FactsSet("bg_text_language",{default});'
                   f'LogChannel(\'BetaGwent\',"TEXT_LANGUAGE_PACKAGE_DEFAULT package={package} language={default}");return {default}; }}\n'
                   f'    if(value>=1&&value<=13)return value;return {default};\n}}\n')


def durations(source, wav_folder):
    events = {m['event']: m['key'] for m in json.loads((ROOT/'docs/evidence/audio-import79.json').read_text('utf8'))['media']}
    methods = {m[1]: m[2] for m in re.finditer(r'function (BetaGwentAudioVoice(?:\d+|VariantPart\d+))\([^\n]+\n\{(.*?)\n\}', source, re.S)}
    cache = {}
    def seconds(event):
        if event not in cache:
            with wave.open(str(wav_folder/(events[event]+'.wav'))) as wav:
                cache[event] = wav.getnframes()/wav.getframerate()
        return cache[event]
    changed = 0
    def rewrite(match):
        nonlocal changed
        header, body = match[1], match[2]
        name = re.search(r'function (\w+)', header)[1].replace('VoiceVariantDurationPart', 'VoiceVariantPart').replace('VoiceDuration', 'Voice')
        values = methods.get(name)
        if values is None: return match[0]
        event_iter = iter(re.findall(r'return "(bg79_vo_[^"]+)";', values))
        def replace(value):
            nonlocal changed
            changed += 1
            return 'return '+f'{seconds(next(event_iter)):.3f}f;'
        return header+re.sub(r'return (?!0\.0f)[0-9.]+f;', replace, body)+'\n}'
    output = re.sub(r'(function BetaGwentAudioVoice(?:Duration\d+|VariantDurationPart\d+)\([^\n]+\n\{)(.*?)\n\}', rewrite, source, flags=re.S)
    assert changed >= 1000
    return output, changed


def main():
    original = ROOT/'BetaGwent/audio/wwise'
    baseline = inventory((original/'GeneratedSoundBanks/Windows/BetaGwent79.bnk').read_bytes())
    console = json.loads((ROOT/'docs/evidence/audio-bank-build79.json').read_text('utf8'))['command'][0]
    reports = {}
    for language, folder in PROJECTS.items():
        project = ROOT/'BetaGwent/audio'/folder
        if language in LOCALES:
            for source in original.rglob('*'):
                rel = source.relative_to(original)
                if not source.is_file() or any(p in ('.cache', 'GeneratedSoundBanks', 'Originals', '.backup', 'Logs') for p in rel.parts): continue
                if source.suffix.lower() not in ('.wwu', '.wproj', '.wf', '.prof'): continue
                target = project/rel; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
            actor = ET.parse(project/'Actor-Mixer Hierarchy/BetaGwent79.wwu')
            sources = [n.text for n in actor.iter('AudioFile')]
            prepared = ROOT/'BetaGwent/build/languages137/voice'/LOCALES[language]/'wav'
            voice_names = {p.name for p in prepared.glob('*.wav')}
            assert len(voice_names) == 907
            copied = set()
            for filename in sources:
                rel = Path(filename.replace('\\', '/'))
                src = prepared/rel.name if rel.name in voice_names else original/'Originals/SFX'/rel
                dst = project/'Originals/SFX'/rel
                assert src.is_file(), str(src)
                dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dst)
                if rel.name in voice_names: copied.add(rel.name)
            assert copied == voice_names
            log = ROOT/f'BetaGwent/build/audio137/{language}-wwise.log'; log.parent.mkdir(parents=True, exist_ok=True)
            with log.open('wb') as output:
                subprocess.run([console, 'generate-soundbank', str(project/'BetaGwent79.wproj'),
                                '--platform', 'Windows', '--bank', 'BetaGwent79', '--abort-on-load-issues',
                                '--no-source-control', '--skip-languages'], stdout=output, stderr=subprocess.STDOUT,
                               check=True, timeout=600, creationflags=subprocess.CREATE_NO_WINDOW)
        bank = project/'GeneratedSoundBanks/Windows/BetaGwent79.bnk'
        actual = inventory(bank.read_bytes())
        assert {item for item in actual if item[0] == 4} == {item for item in baseline if item[0] == 4}, 'Voice event IDs changed'
        assert len(actual) == len(baseline), 'Sound/event inventory count changed'
        if language != 'en': assert actual == baseline, 'Cloned object IDs changed'
        patch = ROOT/f'BetaGwent/build/stage137/{language}/sources/scripts'
        shutil.copytree(ROOT/'BetaGwent/build/board-patch', patch, dirs_exist_ok=True)
        catalog = patch/'game/betagwent/duelAudioCatalog.ws'
        output, count = durations(catalog.read_text('utf-8-sig'), project/'Originals/SFX/BetaGwent79')
        catalog.write_text(output, 'utf-8-sig')
        bridge = patch/'game/betagwent/developmentBoardMenu.ws'
        bridge.write_text(language_bridge(bridge.read_text('utf-8-sig'), language), 'utf-8-sig')
        reports[language] = dict(bank=str(bank), bytes=bank.stat().st_size, sha256=SHA(bank),
                                 project=folder, rewrittenDurations=count, eventInventoryPreserved=True,
                                 voiceCount=907, defaultTextLanguage=DEFAULT_TEXT[language], packageId=PACKAGE_ID[language],
                                 trollVoice='ru' if language in ('de', 'it') else language,
                                 patch=str(patch), catalogSha256=SHA(catalog), bridgeSha256=SHA(bridge))
        print('Voice ready:', language, bank.stat().st_size, count, 'durations', flush=True)
    (ROOT/'docs/evidence/voice137.json').write_text(json.dumps(reports, indent=2)+'\n', 'utf8')


if __name__ == '__main__': main()
