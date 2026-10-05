"""Compile the AS3-only probe and export GFx; nothing deployed to game/project."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / 'tools/ui'
BUILD = UI / 'build'
BUILD.mkdir(exist_ok=True)
EXPORTER = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\tools\GFx4\gfxexport_mult4fix.exe')
SWF = BUILD / 'betagwent_ui_probe.swf'
commands = [
    [shutil.which('java'), '-Duser.language=en', '-Duser.country=US', '-jar',
     str(ROOT / 'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
     '-load-config=' + str(UI / 'probe-config.xml'), '-output=' + str(SWF),
     str(UI / 'BetaGwentUIProbe.as')],
    [str(EXPORTER), '-i', 'DDS', '-lwr', '-o', str(BUILD), '-d', str(BUILD), str(SWF)],
]
runs = []
for index, command in enumerate(commands):
    result = subprocess.run(command, cwd=UI, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            creationflags=subprocess.CREATE_NO_WINDOW, timeout=60)
    log = result.stdout.decode('utf-8', errors='replace')
    (BUILD / ('compile.log' if index == 0 else 'export.log')).write_text(log, encoding='utf-8')
    runs.append(dict(command=command, exitCode=result.returncode, log=log))
    if result.returncode or 'Error:' in log or 'Failed to' in log:
        print(log)
        raise SystemExit(result.returncode or 1)

def inspect(path):
    data = path.read_bytes()
    signature, version = data[:3].decode('ascii'), data[3]
    declared = struct.unpack_from('<I', data, 4)[0]
    body = zlib.decompress(data[8:]) if signature in ('CWS', 'CFX') else data[8:]
    if declared != 8 + len(body):
        raise SystemExit('Invalid SWF/GFx length')
    nbits = body[0] >> 3
    rect_bytes = (5 + 4 * nbits + 7) // 8
    frame_rate, frames = struct.unpack_from('<HH', body, rect_bytes)
    offset = rect_bytes + 4
    tags = []; symbols = []; abc = 0; attributes = 0
    while offset < len(body):
        header = struct.unpack_from('<H', body, offset)[0]; offset += 2
        code, size = header >> 6, header & 63
        if size == 63:
            size = struct.unpack_from('<I', body, offset)[0]; offset += 4
        payload = body[offset:offset + size]
        if len(payload) != size:
            raise SystemExit('Truncated tag')
        tags.append(code)
        if code == 69: attributes = int.from_bytes(payload[:4], 'little')
        if code == 82: abc += 1
        if code == 76:
            count = struct.unpack_from('<H', payload)[0]; pos = 2
            for _ in range(count):
                tag = struct.unpack_from('<H', payload, pos)[0]; pos += 2
                end = payload.index(0, pos)
                symbols.append(dict(characterId=tag, className=payload[pos:end].decode('utf-8')))
                pos = end + 1
        offset += size
        if code == 0: break
    if not (attributes & 8) or abc < 1 or not any(s['characterId'] == 0 and s['className'] == 'BetaGwentUIProbe' for s in symbols):
        raise SystemExit('AS3/root class missing')
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                signature=signature, version=version, frameRate=frame_rate / 256,
                frames=frames, tagCodes=tags, symbolClasses=symbols, abcBlocks=abc,
                as3=True, declaredLengthValid=True)

report = dict(runs=runs, artifacts=[inspect(SWF), inspect(BUILD / 'betagwent_ui_probe.gfx')],
              exported=True, redswfCreated=False, nativeMenuRegistered=False,
              runtimeBridgeVerified=False,
              scope='AS3 compile and Scaleform GFx export only. No Flash runtime or Adobe installer. No project/game/depot deployment.')
(ROOT / 'docs/evidence/ui-probe-build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('AS3 + GFx export verified:', ', '.join(str(a['bytes']) + ' bytes' for a in report['artifacts']))
