"""Extract pinned Beta audio into build staging; never change source assets.

UnityPy and vgmstream are local, separately installed tools. Bank version128 is
archival input, not a bank to load in TW3. CardAudio.xml is the identity source.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
import wave
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets'
OUT = ROOT / 'BetaGwent/build/audio79'
DECODER = ROOT / 'tools/vendor/audio/vgmstream-r2117/vgmstream-cli.exe'
sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))


def fnv(text):
    value = 2166136261
    for byte in text.lower().encode('utf8'):
        value = ((value * 16777619) ^ byte) & 0xffffffff
    return value


def chunks(raw):
    pos = 0
    while pos < len(raw):
        if pos + 8 > len(raw):
            raise ValueError('Truncated bank chunk')
        tag, size = struct.unpack_from('<4sI', raw, pos)
        end = pos + 8 + size
        if end > len(raw):
            raise ValueError('Invalid bank chunk extent')
        yield tag, raw[pos + 8:end]
        pos = end


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def decode(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        result = subprocess.run([str(DECODER), '-i', '-o', str(target), str(source)],
            capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise RuntimeError(str(source) + ': ' + result.stderr.decode(errors='replace'))
    with wave.open(str(target)) as audio:
        if audio.getsampwidth() != 2 or not audio.getnframes():
            raise ValueError('Expected nonempty PCM16 output')
        return dict(path=str(target.relative_to(ROOT)), channels=audio.getnchannels(),
            sampleRate=audio.getframerate(), frames=audio.getnframes(),
            durationMs=round(audio.getnframes() * 1000 / audio.getframerate()),
            sha256=hashlib.sha256(target.read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--decode-voices', action='store_true')
    args = parser.parse_args()
    inventory = json.loads((ROOT / 'docs/evidence/beta-audio-inventory78.json').read_text('utf8'))
    with zipfile.ZipFile(STREAM / 'data_definitions') as archive:
        audio_xml = archive.read('CardAudio.xml')
        records = ET.fromstring(audio_xml)
        templates = ET.fromstring(archive.read('Templates.xml'))
    audio = {}
    bank_names = {}
    for wrapper in records:
        record = wrapper.find('CardAudio')
        if record is None:
            continue
        banks = [dict(b.attrib) for b in record.findall('SoundBanks/Soundbank')]
        for bank in banks:
            bank_names[fnv(bank['name'])] = bank['name']
        audio[int(record.get('id'))] = dict(name=record.get('name'), banks=banks,
            triggers=[dict(t.attrib) for t in record.findall('Triggers/Trigger')],
            defaultVoices=[dict(v.attrib) for v in record.findall('Voiceovers/VoiceoverGroup/Voiceover')],
            conditionalXml=ET.tostring(record.find('Voiceovers/Conditionals'), encoding='unicode')
                if record.find('Voiceovers/Conditionals') is not None else '',
            effects=[dict(e.attrib) for e in record.findall('SoundEffects/SoundEffect')])
    bank_records = []
    for package in inventory['packages']:
        path = Path(package['path'])
        if path.stem == 'Music':
            continue
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != package['sha256']:
            raise ValueError('Pinned package changed')
        for entry in package['banks']:
            blob = raw[entry['offset']:entry['offset'] + entry['bytes']]
            parts = dict(chunks(blob))
            names = {}
            if b'STID' in parts:
                text = parts[b'STID']; count = struct.unpack_from('<I', text, 4)[0]; pos = 8
                for _ in range(count):
                    ident, length = struct.unpack_from('<IB', text, pos); pos += 5
                    names[ident] = text[pos:pos + length].decode('utf8'); pos += length
            name = names.get(entry['id'], bank_names.get(entry['id'], str(entry['id'])))
            if not re.fullmatch(r'[A-Za-z0-9_().-]+', name):
                raise ValueError('Unexpected bank name')
            target = OUT / 'banks' / path.stem / (name + '.bnk')
            write(target, blob)
            media = []
            if b'DIDX' in parts:
                index, payload = parts[b'DIDX'], parts[b'DATA']
                if len(index) % 12:
                    raise ValueError('Invalid media index')
                for pos in range(0, len(index), 12):
                    ident, start, length = struct.unpack_from('<III', index, pos)
                    if start + length > len(payload):
                        raise ValueError('Media outside bank')
                    wem = OUT / 'banks' / path.stem / (str(ident) + '.wem')
                    data = payload[start:start + length]
                    if wem.exists() and wem.read_bytes() != data:
                        raise ValueError('Conflicting embedded media ID')
                    write(wem, data); media.append(ident)
            bank_records.append(dict(package=path.stem, name=name, id=entry['id'],
                path=str(target.relative_to(ROOT)), media=media))
    import UnityPy
    voices = {}
    for role, relative in [('cards', 'audio/highend/vo/ru-ru'),
                           ('announcer', 'audio/highend/vo/announcers/ru-ru')]:
        bundle = STREAM / 'AssetBundles' / relative
        pin = next(v for v in inventory['russianVoiceBundles'] if Path(v['path']) == bundle)
        if hashlib.sha256(bundle.read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('Pinned Russian voice bundle changed')
        for obj in UnityPy.load(str(bundle)).objects:
            if obj.type.name != 'TextAsset':
                continue
            asset = obj.read()
            name = asset.m_Name
            if not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
                raise ValueError('Unexpected voice key')
            raw = asset.m_Script.encode('utf8', 'surrogateescape')
            if raw[:4] != b'RIFF' or raw[8:12] != b'WAVE' or struct.unpack_from('<I', raw, 4)[0] + 8 != len(raw):
                raise ValueError('Voice RIFF extent mismatch')
            target = OUT / 'wem' / role / (name + '.wem'); write(target, raw)
            item = dict(role=role, key=name, sourceBundle=relative,
                wem=str(target.relative_to(ROOT)), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            if args.decode_voices:
                item['pcm'] = decode(target, OUT / 'wav' / role / (name + '.wav'))
            voices[name] = item
    bindings = []
    for template in templates:
        art = template.find('ArtDefinition')
        audio_id = int(art.get('AudioId', '0')) if art is not None else 0
        if audio_id not in audio:
            continue
        data = audio[audio_id]
        bindings.append(dict(templateId=int(template.get('Id')), audioId=audio_id,
            debugName=template.get('DebugName'), defaultVoices=data['defaultVoices'],
            missingDefaultVoices=[v['key'] for v in data['defaultVoices'] if v['key'] not in voices],
            banks=data['banks'], effects=data['effects'], triggers=data['triggers'],
            conditionalXml=data['conditionalXml']))
    report = dict(stage=79, target='0.9.24.3.432', originalFilesModified=False,
        cardAudioXmlSha256=hashlib.sha256(audio_xml).hexdigest(), banks=bank_records,
        voices=list(voices.values()), cards=bindings, decodedVoices=args.decode_voices,
        soundBankImported=False, nativePlaybackVerified=False,
        note='Exact AudioId/default voice bindings. Conditional groups retained for later rule-aware playback. No Beta128 bank loaded into TW3.')
    write(ROOT / 'docs/evidence/beta-audio-extract79.json', (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(f'Extracted {len(bank_records)} banks and {len(voices)} Russian voices; {len(bindings)} exact AudioId card bindings; decoded={args.decode_voices}.')


if __name__ == '__main__':
    main()
