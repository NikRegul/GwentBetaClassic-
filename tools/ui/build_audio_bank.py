"""Build only the prepared additional bank; install only after structural checks.

Requires a user-installed/licensed Wwise2023.1 console. Never replaces Init.bnk
or modifies the game, REDkit installation or depot. Native loading still needs
a later runtime check; a valid bank header does not prove playback.
"""
from pathlib import Path
import argparse
import ctypes
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/recon'))
from extract_beta_audio import chunks, fnv


def executable_version(path):
    library = ctypes.WinDLL('version', use_last_error=True)
    library.GetFileVersionInfoSizeW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint32)]
    library.GetFileVersionInfoW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    library.VerQueryValueW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)]
    unused = ctypes.c_uint32(); size = library.GetFileVersionInfoSizeW(str(path), ctypes.byref(unused))
    if not size:
        raise ValueError('WwiseConsole version resource missing')
    buffer = ctypes.create_string_buffer(size)
    if not library.GetFileVersionInfoW(str(path), 0, size, buffer):
        raise ValueError('Could not read console version')
    pointer = ctypes.c_void_p(); length = ctypes.c_uint32()
    if not library.VerQueryValueW(buffer, '\\', ctypes.byref(pointer), ctypes.byref(length)) or length.value < 16:
        raise ValueError('Invalid version resource')
    signature, _, high, low = struct.unpack('<4I', ctypes.string_at(pointer, 16))
    if signature != 0xfeef04bd:
        raise ValueError('Invalid fixed version signature')
    return [high >> 16, high & 65535, low >> 16, low & 65535]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--console', type=Path, required=True)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    console = args.console.resolve()
    if not console.is_file() or console.name.lower() != 'wwiseconsole.exe':
        raise ValueError('Supply the installed WwiseConsole.exe')
    version = executable_version(console)
    if version[:2] != [2023, 1]:
        raise ValueError('This REDkit project requires Wwise2023.1, received ' + str(version))
    manifest = json.loads((ROOT / 'docs/evidence/audio-import79.json').read_text('utf8'))
    project = Path(manifest['project']).resolve()
    if not project.is_relative_to(ROOT / 'BetaGwent/audio/wwise'):
        raise ValueError('Project outside workspace audio directory')
    root = ET.parse(project).getroot()
    if any('CustomCmd' in p.get('Name', '') and
           (p.get('Value', '').strip() or any((v.text or '').strip() for v in p.iter('Value')))
           for p in root.iter('Property')):
        raise ValueError('Custom Wwise pre/post commands are not allowed in this generated project')
    for p in root.iter('Property'):
        if p.get('Name') == 'SoundBankPaths':
            for value in p.iter('Value'):
                relative = value.text or ''
                if not re.fullmatch(r'GeneratedSoundBanks\\[A-Za-z0-9]+\\', relative):
                    raise ValueError('Unexpected bank output path')
    for media in manifest['media']:
        path = project.parent / 'Originals/SFX/BetaGwent79' / (media['key'] + '.wav')
        if hashlib.sha256(path.read_bytes()).hexdigest() != media['source']['sha256']:
            raise ValueError('Prepared WAV changed: ' + media['key'])
    run_dir = ROOT / 'BetaGwent/build/audio79' / ('wwise-' + time.strftime('%Y%m%d-%H%M%S'))
    run_dir.mkdir(parents=True, exist_ok=False)
    output = project.parent / 'GeneratedSoundBanks/Windows'
    bank = output / 'BetaGwent79.bnk'
    before = hashlib.sha256(bank.read_bytes()).hexdigest() if bank.exists() else None
    command = [str(console), 'generate-soundbank', str(project), '--platform', 'Windows', '--bank', 'BetaGwent79',
        '--abort-on-load-issues', '--no-source-control', '--skip-languages']
    result = subprocess.run(command, cwd=project.parent, capture_output=True,
        timeout=180, creationflags=subprocess.CREATE_NO_WINDOW)
    (run_dir / 'stdout.txt').write_bytes(result.stdout)
    (run_dir / 'stderr.txt').write_bytes(result.stderr)
    report = dict(command=command, version=version, exitCode=result.returncode,
        priorBankSha256=before, installed=False, nativePlaybackVerified=False)
    # Wwise1 means warnings; require clean success until diagnostics are reviewed.
    if result.returncode != 0 or not bank.is_file():
        (run_dir / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
        raise RuntimeError('Wwise bank generation needs review: ' + str(run_dir))
    raw = bank.read_bytes(); parts = dict(chunks(raw))
    if not all(k in parts for k in [b'BKHD', b'HIRC', b'DIDX', b'DATA']):
        raise ValueError('Expected additional bank with embedded media')
    bank_version, bank_id = struct.unpack_from('<II', parts[b'BKHD'])
    if bank_version <= 128 or bank_id != fnv('BetaGwent79'):
        raise ValueError('Bank ID/version mismatch')
    payload = parts[b'HIRC']; count = struct.unpack_from('<I', payload)[0]; pos = 4; event_ids = set(); object_types = {}
    for _ in range(count):
        kind, size = struct.unpack_from('<BI', payload, pos); pos += 5
        if size < 4 or pos + size > len(payload):
            raise ValueError('Invalid HIRC object')
        ident = struct.unpack_from('<I', payload, pos)[0]
        if kind not in [2, 3, 4, 7]:
            raise ValueError('Unexpected object type in first additional bank; native bus/device definitions must not be installed')
        object_types[kind] = object_types.get(kind, 0) + 1
        if kind == 4:
            event_ids.add(ident)
        pos += size
    if pos != len(payload):
        raise ValueError('Unexpected HIRC trailing data')
    expected = {fnv(m['event']) for m in manifest['media']} | {fnv('bg79_stop_voice'), fnv('bg79_stop_sfx')}
    if not expected <= event_ids:
        raise ValueError('Missing imported audio events')
    if len(parts[b'DIDX']) % 12:
        raise ValueError('Invalid embedded media table')
    if len(parts[b'DIDX']) // 12 != manifest['mediaCount']:
        raise ValueError('Embedded media count differs from prepared import')
    for pos in range(0, len(parts[b'DIDX']), 12):
        _, offset, size = struct.unpack_from('<III', parts[b'DIDX'], pos)
        if offset + size > len(parts[b'DATA']):
            raise ValueError('Invalid media extent')
    report.update(bank=str(bank), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
        bankVersion=bank_version, expectedEventsVerified=True, expectedEventCount=len(expected),
        eventCount=len(event_ids), objectTypeCounts=object_types, nativeBusDefinitionsIncluded=False,
        embeddedMedia=len(parts[b'DIDX']) // 12)
    if args.install:
        source = ROOT / 'BetaGwent/development/scripts/game/betagwent/duelAudioCatalog.ws'
        prepared=ROOT/'BetaGwent/audio/generated/duelAudioCatalog-full.ws' if manifest.get('fullImport') else source
        text = prepared.read_text('utf-8-sig')
        old = 'function BetaGwentAudioBankInstalled() : bool { return false; }'
        new = 'function BetaGwentAudioBankInstalled() : bool { return true; }'
        if old not in text and new not in text:
            raise ValueError('Generated bank activation declaration changed')
        target = ROOT / 'GwentB/myproject1/workspace/soundbanks/pc/BetaGwent79.bnk'
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = run_dir / 'prior-BetaGwent79.bnk'; shutil.copyfile(target, backup)
        shutil.copyfile(bank, target)
        if old in text or prepared!=source:
            source.write_text(text.replace(old, new), encoding='utf-8-sig')
        report.update(installed=True, target=str(target), scriptPreparationAndCompilationRequired=True)
    (run_dir / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    (ROOT / 'docs/evidence/audio-bank-build79.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    manifest['wwiseBuildVerified'] = True
    if args.install:
        manifest['bankInstalled'] = True
    (ROOT / 'docs/evidence/audio-import79.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
