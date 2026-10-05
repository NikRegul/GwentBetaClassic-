"""Build the DIY-backed standalone development board; no runtime deployment."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import zlib
import argparse

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / 'BetaGwent/ui'
BUILD = UI / 'build'
BUILD.mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--entry', choices=['BetaGwentBoard','DeckBuilder','GwintGame'], default='BetaGwentBoard')
parser.add_argument('--reuse-assets', action='store_true')
parser.add_argument('--source-dir',type=Path,help='Isolated localized source directory; requires --reuse-assets')
args = parser.parse_args()
SOURCE_DIR=args.source_dir.resolve() if args.source_dir else UI/'src'
if args.source_dir and not args.reuse_assets:raise SystemExit('Use --reuse-assets with isolated sources')
stem, root_class = {'BetaGwentBoard':('betagwent_board','BetaGwentBoard'), 'DeckBuilder':('betagwent_decks','BetaGwentDeckMenu'), 'GwintGame':('betagwent_npc00','BetaGwentNpcMenu')}[args.entry]
SWF = BUILD / (stem + '.swf')
DDS_BUILD = BUILD / ('native-atlas' if args.entry=='BetaGwentBoard' else 'native-atlas-'+args.entry)
DDS_BUILD.mkdir(exist_ok=True)
# Source ordering can change image IDs between language builds. Keep only this
# build's DDS exports so a stale alias cannot be mistaken for current artwork.
for stale in DDS_BUILD.glob('*.dds'):
    if not stale.resolve().is_relative_to((UI/'build').resolve()):raise RuntimeError('DDS path escaped build directory')
    stale.unlink()
EXPORTER = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\tools\GFx4\gfxexport_mult4fix.exe')
if not args.reuse_assets:
    subprocess.run([sys.executable, str(ROOT / 'tools/build_full_catalog.py')],cwd=ROOT,check=True,timeout=60)
    subprocess.run([sys.executable, str(ROOT / 'tools/ui/build_card_art.py')],cwd=ROOT,check=True,timeout=300)
    subprocess.run([sys.executable, str(ROOT / 'tools/build_full_catalog.py')],cwd=ROOT,check=True,timeout=60)
commands = [
    [shutil.which('java'), '-Duser.language=en', '-Duser.country=US', '-jar',
     str(ROOT / 'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
     '-load-config=' + str(UI / 'board-config.xml'), '-output=' + str(SWF),
     '-source-path=' + str(SOURCE_DIR),
     '-source-path+=' + str(EXPORTER.parents[3] / 'r4data/gameplay/gui_new/actionscript'),
     '-includes+=scaleform.gfx.KeyboardEventEx',
     str(SOURCE_DIR / (root_class+'.as'))],
    [str(EXPORTER), '-i', 'TGA', '-lwr', '-o', str(BUILD), '-d', str(BUILD), str(SWF)],
    [str(EXPORTER), '-i', 'DDS', '-d5', '-quick', '-ptresize', 'mult4',
     '-o', str(DDS_BUILD), '-d', str(DDS_BUILD), str(SWF)],
]
runs = []
for index, command in enumerate(commands):
    result = subprocess.run(command, cwd=UI, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            creationflags=subprocess.CREATE_NO_WINDOW, timeout=240)
    log = result.stdout.decode('utf-8', errors='replace')
    log_path = BUILD / (stem+'-'+['compile.log', 'export.log', 'export-dds.log'][index])
    log_path.write_text(log, encoding='utf-8')
    runs.append(dict(command=command, exitCode=result.returncode, log=str(log_path)))
    if result.returncode or 'Error:' in log or 'Failed to' in log:
        print(log)
        raise SystemExit(result.returncode or 1)

def inspect(path):
    data = path.read_bytes()
    signature, version = data[:3].decode('ascii'), data[3]
    if signature not in ('FWS', 'CWS', 'GFX', 'CFX'):
        raise SystemExit('Unknown movie signature')
    body = zlib.decompress(data[8:]) if signature in ('CWS', 'CFX') else data[8:]
    declared = struct.unpack_from('<I', data, 4)[0]
    if declared != len(body) + 8:
        raise SystemExit('Movie length mismatch')
    rect_bytes = (5 + 4 * (body[0] >> 3) + 7) // 8
    offset = rect_bytes + 4
    symbols = []
    while offset < len(body):
        header = struct.unpack_from('<H', body, offset)[0]
        offset += 2
        tag, size = header >> 6, header & 63
        if size == 63:
            size = struct.unpack_from('<I', body, offset)[0]
            offset += 4
        payload = body[offset:offset + size]
        if len(payload) != size:
            raise SystemExit('Truncated movie tag')
        if tag == 76:
            count = struct.unpack_from('<H', payload)[0]
            pos = 2
            for _ in range(count):
                character_id = struct.unpack_from('<H', payload, pos)[0]
                pos += 2
                end = payload.index(0, pos)
                symbols.append(dict(characterId=character_id, className=payload[pos:end].decode()))
                pos = end + 1
        offset += size
        if tag == 0:
            break
    if not any(s['characterId'] == 0 and s['className'] == root_class for s in symbols):
        raise SystemExit('Board root class missing')
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                signature=signature, version=version, symbols=symbols)

assets = []
source_root = ROOT / 'LegacyGwent-diy(1)/LegacyGwent-diy/src/Cynthia.Card.Unity/src/Cynthia.Unity.Card/Assets/Resources/Sprites/Background'
for source_name, target_name in [('GamBackground.png', 'board_classic.png'), ('GameBackground2.png', 'board_wide.png')]:
    source, target = source_root / source_name, UI / 'assets' / target_name
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    if source_hash != target_hash:
        raise SystemExit('Copied DIY board does not match source')
    assets.append(dict(source=str(source), copy=str(target), sha256=target_hash, unchanged=True))
report = dict(entry=args.entry,rootClass=root_class,runs=runs, assets=assets, movies=[inspect(SWF), inspect(BUILD / (stem+'.gfx'))],
              textures=[str(p) for p in BUILD.iterdir() if p.suffix.lower() == '.tga'],
              nativeDDSDirectory=str(DDS_BUILD),
              nativeDDSTextures=[str(p) for p in DDS_BUILD.glob('*.dds')],
              textureFormat='TGA preview; GFx-exported DXT5 DDS for embedded native atlas', redswfCreated=False,
              menuRegistered=False, runtimeVerified=False, scope='Development board presentation, not a complete Beta match.')
(ROOT / ('docs/evidence/board-build'+('' if args.entry=='BetaGwentBoard' else '-'+args.entry)+'.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('Board movies built; native resource/registration/runtime pending.')
