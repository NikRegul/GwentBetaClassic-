"""Install workspace-only menu overrides for the native Gwent entry points."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import zlib
from read_gui_resource import GuiResource
from register_board import WORKSPACE, ORIGINAL
from update_board_resource import header_crc, validate_resource, unpack_root, movie_parts

ROOT = Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
source=WORKSPACE/'betagwent/betagwent_board.menu'
data=source.read_bytes()
expected={'menuClass':'CR4BetaGwentBoardMenu','menuFlashSwf':r'betagwent\betagwent_board.redswf'}
if GuiResource(source).menu()!=expected:raise SystemExit('Unexpected board menu')
config=GuiResource(ORIGINAL).config()
rows=[]
for entry in config['menus']:
    if entry['menuName'] not in ('DeckBuilder','GwintGame'):continue
    target=(WORKSPACE/entry['menuResource']).resolve()
    if not target.is_relative_to(WORKSPACE.resolve()):raise SystemExit('Target escaped project')
    stem={'DeckBuilder':'betagwent_decks','GwintGame':'betagwent_npc00'}[entry['menuName']]
    movie=WORKSPACE/('betagwent/'+stem+'.redswf')
    resource,_=validate_resource(movie)
    _,gfx,swf=unpack_root(resource)
    root={'DeckBuilder':'BetaGwentDeckMenu','GwintGame':'BetaGwentNpcMenu'}[entry['menuName']]
    if not any(code==76 and (root.encode()+b'\0') in payload for code,payload,_ in movie_parts(gfx)[1]):
        raise SystemExit('Dedicated entry root missing: '+root)
    new_path='betagwent\\'+stem+'.redswf'
    patched=bytearray(data)
    r=GuiResource(source);offset,count,_=r.tables[0]
    old_path=expected['menuFlashSwf'].encode();replacement=new_path.encode()
    if len(old_path)!=len(replacement) or r.strings.count(old_path+b'\0')!=1:raise SystemExit('Unexpected menu path layout')
    patched[offset:offset+count]=r.strings.replace(old_path+b'\0',replacement+b'\0')
    struct.pack_into('<I',patched,48,zlib.crc32(patched[offset:offset+count]))
    struct.pack_into('<I',patched,32,header_crc(patched))
    patched=bytes(patched)
    target_expected=dict(expected,menuFlashSwf=new_path)
    if target.exists() and target.read_bytes() not in (data,patched):raise SystemExit('Unexpected user menu override: '+str(target))
    original=ORIGINAL.parents[3]/entry['menuResource']
    original_hash=hashlib.sha256(original.read_bytes()).hexdigest()
    if args.apply and (not target.exists() or target.read_bytes()!=patched):
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            backup=ROOT/'BetaGwent/build/resource-backups'/('entry-'+hashlib.sha256(target.read_bytes()).hexdigest()+'.menu')
            backup.parent.mkdir(parents=True,exist_ok=True)
            if not backup.exists():backup.write_bytes(target.read_bytes())
        pending=target.with_suffix('.menu.pending')
        with pending.open('xb') as output:output.write(patched);output.flush();os.fsync(output.fileno())
        os.replace(pending,target)
    if args.apply and GuiResource(target).menu()!=target_expected:raise SystemExit('Menu round-trip mismatch')
    if hashlib.sha256(original.read_bytes()).hexdigest()!=original_hash:raise SystemExit('Native source changed')
    rows.append(dict(menuName=entry['menuName'],target=str(target),original=str(original),originalSha256=original_hash,
                     sourceUnchanged=True,applied=args.apply,movie=str(movie),rootClass=root,menuProperties=target_expected,overrideSha256=hashlib.sha256(patched).hexdigest()))
if len(rows)!=2:raise SystemExit('Native entry points not found')
report=dict(entries=rows,applied=args.apply,installedGameModified=False,depotModified=False,
            questRuntimeVerified=False,note='Dedicated root movies register DeckBuilder/GwintGame exactly. DeckBuilder uses library unless native NPC pending/request flags select prebattle. NPC fade and result signalling are owned by nativeGwentEntry/developmentBoardMenu.')
(ROOT/'docs/evidence/native-gwent-entry79f.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
