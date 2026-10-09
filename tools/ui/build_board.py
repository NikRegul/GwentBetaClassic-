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
import time

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / 'BetaGwent/ui'
BUILD = UI / 'build'
BUILD.mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--entry', choices=['BetaGwentBoard','DeckBuilder','GwintGame','BetaGwentKeg'], default='BetaGwentBoard')
parser.add_argument('--reuse-assets', action='store_true')
parser.add_argument('--native-only',action='store_true',help='Export DDS/GFx only; skip unused TGA previews')
parser.add_argument('--source-dir',type=Path,help='Isolated localized source directory; requires --reuse-assets')
args = parser.parse_args()
SOURCE_DIR=args.source_dir.resolve() if args.source_dir else UI/'src'
if args.source_dir and not args.reuse_assets:raise SystemExit('Use --reuse-assets with isolated sources')
stem, root_class = {'BetaGwentBoard':('betagwent_board','BetaGwentBoard'), 'DeckBuilder':('betagwent_decks','BetaGwentDeckMenu'), 'GwintGame':('betagwent_npc00','BetaGwentNpcMenu'), 'BetaGwentKeg':('betagwent_kegop','BetaGwentKegMenu')}[args.entry]
# Stage 109: each menu embeds only the art pages it uses (55 MiB GUI budget per menu).
# Pages 0-8 cards, 10-12 interface/effects, 14 card faces, 15 HUD/buttons; 21+ keg troll flipbook and Beta backs (keg menu only).
import re as _re
PAGES={'BetaGwentKeg':set(range(0,9))|{11,14,15}|set(range(21,40))}.get(args.entry,set(range(0,21)))
def filtered_sources(source):
    target=source.parent/('src-'+args.entry)
    if target.exists():shutil.rmtree(target)
    shutil.copytree(source,target)
    art=target/'BetaGwentHDArt.as';raw=art.read_bytes();text=raw.decode('utf-8-sig')
    for page in map(int,_re.findall(r'private static var Page(\d+):Class;',text)):
        if page in PAGES:continue
        text,n=_re.subn(r'[ \t]*\[Embed\([^\]]*\)\] private static var Page%d:Class;\r?\n'%page,'',text)
        if n!=1:raise SystemExit('Page embed not found: %d'%page)
        text=_re.sub(r'(private static var types:Array=\[[^\]]*?)\bPage%d\b'%page,r'\1null',text)
    art.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8'))
    return target
SOURCE_DIR=filtered_sources(SOURCE_DIR)
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
    [str(Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')) if Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe').exists() else shutil.which('java'), '-Xmx3g', '-Duser.language=en', '-Duser.country=US', '-jar',
     str(ROOT / 'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
     '-load-config=' + str(UI / 'board-config.xml'), '-output=' + str(SWF),
     '-source-path=' + str(SOURCE_DIR),
     '-source-path+=' + str(EXPORTER.parents[3] / 'r4data/gameplay/gui_new/actionscript'),
     '-includes+=scaleform.gfx.KeyboardEventEx',
     str(SOURCE_DIR / (root_class+'.as'))],
    [str(EXPORTER), '-i', 'TGA', '-lwr', '-o', str(BUILD), '-d', str(BUILD), str(SWF)],
    # Keep the shipped atlas dimensions; fast BC compression avoids minutes per
    # page in the updated exporter. This does not downscale artwork.
    [str(EXPORTER), '-i', 'DDS', '-quick', '-d5', '-ptresize', 'mult4',
     '-o', str(DDS_BUILD), '-d', str(DDS_BUILD), str(SWF)],
]
runs = []
for index, command in enumerate(commands):
    if args.native_only and index==1:continue
    log_path = BUILD / (stem+'-'+['compile.log', 'export.log', 'export-dds.log'][index])
    completed_by_output = False
    with log_path.open('wb') as handle:
        process = subprocess.Popen(command, cwd=UI, stdout=handle, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        started = time.time(); previous = None; stable_since = None
        while process.poll() is None:
            log = log_path.read_text('utf8', errors='replace')
            if index == 2 and 'Total images written:' in log and 'Saving stripped SWF file' in log and 'Error:' not in log:
                paths = [DDS_BUILD / (stem+'.gfx'), *DDS_BUILD.glob('*.dds')]
                if len(paths)>1 and all(p.exists() and p.stat().st_size>128 for p in paths):
                    state = [(p.name,p.stat().st_size,p.stat().st_mtime_ns) for p in paths]
                    if state != previous: previous=state;stable_since=time.time()
                    elif time.time()-stable_since>=8:
                        completed_by_output=True;process.kill();process.wait(timeout=10);break
            if time.time()-started>600:
                process.kill();process.wait(timeout=10)
                raise RuntimeError('Build command timed out; partial log: '+str(log_path))
            time.sleep(1)
    log = log_path.read_text('utf8', errors='replace')
    code = 0 if completed_by_output else process.returncode
    runs.append(dict(command=command, exitCode=code, processExitCode=process.returncode,
                     completedByOutput=completed_by_output, log=str(log_path)))
    if code or 'Error:' in log or 'Failed to' in log:
        print(log)
        raise SystemExit(code or 1)
    if index==0:
        # Stage 104: embed the original Gwent Beta TMP fonts as DefineFont3 tags.
        fonts=subprocess.run([sys.executable,str(ROOT/'tools/ui/build_beta_fonts104.py'),'inject',str(SWF)],cwd=ROOT,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        (BUILD/(stem+'-fonts.log')).write_text(fonts.stdout.decode('utf-8','replace'),encoding='utf-8')
        if fonts.returncode:print(fonts.stdout.decode('utf-8','replace'));raise SystemExit(fonts.returncode)
if args.native_only:
    shutil.copyfile(DDS_BUILD/(stem+'.gfx'),BUILD/(stem+'.gfx'))

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
