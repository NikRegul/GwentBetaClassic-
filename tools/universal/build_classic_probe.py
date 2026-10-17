"""Build a tiny diagnostic overlay for DeckBuilder; no game launch/install."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import sys
import zipfile
import zlib

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/classic081-minimal-probe'
PREVIOUS=ROOT/'BetaGwent/build/classic081-boot-fix4'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import Resource,write_bundle,sha,header_crc,bundle_entries,classic_metadata_hash_rows,cook_guid_map
from build_resources import read_vlq,vlq
sys.path.insert(0,str(ROOT/'tools/ui'))
from cr2w_gui_write109 import Res,prop
from update_board_resource import movie_parts


def minimal_metadata(source,bundle,out):
    data=source.read_bytes();assert struct.unpack_from('<I',data,4)[0]==6
    size,pos=read_vlq(data,16);strings=data[pos:pos+size];pos+=size;arrays=[]
    for width in [32,20,24,4,8,12,16]:
        count,pos=read_vlq(data,pos)
        arrays.append([data[i:i+width] for i in range(pos,pos+count*width,width)])
        pos+=count*width
    assert pos==len(data) and not arrays[3]
    with bundle.open('rb') as stream:
        header=stream.read(32);table=stream.read(struct.unpack_from('<I',header,16)[0])
    entries={}
    for i in range(0,len(table),320):
        row=table[i:i+320];name=row[:256].split(b'\0')[0].decode()
        size,packed,offset=struct.unpack_from('<III',row,276);entries[name]=(size,packed,offset)
    selected=[]
    for i,row in enumerate(arrays[0]):
        off=struct.unpack_from('<I',row)[0];name=strings[off:strings.index(0,off)].decode()
        if name in entries:selected.append((i,name,row))
    assert len(selected)==len(entries)>0
    ids={old:new for new,(old,_,_) in enumerate(selected,1)}
    file_rows=[bytes(32)];entry_rows=[bytes(20)]
    for new,(_,name,row) in enumerate(selected,1):
        size,packed,offset=entries[name];row=bytearray(row)
        struct.pack_into('<4I',row,8,packed,size,new,0)
        file_rows.append(row);entry_rows.append(struct.pack('<5I',new,1,offset,packed,0))
    record=bytearray(arrays[2][1]);name=struct.unpack_from('<I',record)[0]
    start=32+len(table)
    bundles=[bytes(24),struct.pack('<6I',name,1,len(entries),bundle.stat().st_size-start,start,0)]
    init=[]
    for row in arrays[5]:
        old,di,no=struct.unpack('<3I',row)
        if old in ids:init.append(struct.pack('<3I',ids[old],di,no))
    hashes=[]
    for row in arrays[6]:
        h,old,flags=struct.unpack('<QII',row)
        if old in ids:hashes.append(struct.pack('<QII',h,ids[old],flags))
    assert len(init)==len(hashes)==len(entries)
    hashes=classic_metadata_hash_rows(hashes,len(file_rows))
    maximum=max(x[0] for x in entries.values())
    result=bytearray(b'\x03VTM'+struct.pack('<3I',6,maximum,maximum)+vlq(len(strings))+strings)
    for rows in [file_rows,entry_rows,bundles,[],arrays[4],init,hashes]:result+=vlq(len(rows))+b''.join(rows)
    out.write_bytes(result)


def main():
    assert not BASE.exists(),'Keep probe artifacts immutable'
    BASE.mkdir();source=(PREVIOUS/'menus/ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    bindings=json.loads((PREVIOUS/'menus/menus.json').read_text('utf8'))['scriptBindings']
    stubs=[]
    for name in bindings:
        match=re.search(r'public function '+name+r'\(([^)]*)\)\s*:\s*(\w+)',source)
        assert match,name
        params,kind=match.groups();body=''
        if name=='finishDeckSelection':body='status.text="CLASSIC PROBE: MENU_CONFIG completed.\\nClick anywhere or press Escape to close.";'
        elif name=='requestCloseFromGame':body='closeProbe();'
        elif kind!='void':body='return false;' if kind=='Boolean' else 'return null;'
        stubs.append('public function '+name+'('+params+'):'+kind+'{'+body+'}')
    as3='''package {
import flash.display.MovieClip;
import flash.events.Event;
import flash.events.MouseEvent;
import flash.events.KeyboardEvent;
import flash.external.ExternalInterface;
import flash.text.TextField;
import flash.text.TextFormat;
[SWF(width="1920",height="1080",frameRate="30",backgroundColor="#101113")]
public class BetaGwentDeckMenu extends MovieClip {
 public var _NATIVE_callGameEvent:Function;
 public var _NATIVE_registerDataBinding:Function;
 public var _NATIVE_unregisterDataBinding:Function;
 public var _NATIVE_registerChild:Function;
 public var _NATIVE_unregisterChild:Function;
 public var _NATIVE_registerRenderTarget:Function;
 public var _NATIVE_unregisterRenderTarget:Function;
 private var status:TextField=new TextField();
 private var attached:Boolean=false,connected:Boolean=false;
 public function BetaGwentDeckMenu(){
  stop();graphics.beginFill(0x101113);graphics.drawRect(0,0,1920,1080);graphics.endFill();
  status.defaultTextFormat=new TextFormat("$NormalFont",34,0xF2EEE4);
  status.text="CLASSIC PROBE: document constructed; waiting for native bridge.";
  status.x=100;status.y=340;status.width=1720;status.height=300;status.multiline=true;status.wordWrap=true;status.mouseEnabled=false;addChild(status);
  addEventListener(Event.ADDED_TO_STAGE,attach);addEventListener(Event.ENTER_FRAME,tick);
  if(stage)attach(null);
 }
 private function attach(event:Event):void{
  if(attached)return;attached=true;removeEventListener(Event.ADDED_TO_STAGE,attach);
  stage.addEventListener(KeyboardEvent.KEY_DOWN,key);addEventListener(MouseEvent.CLICK,click);
  ExternalInterface.call("registerMenu","DeckBuilder",this);
 }
 private function tick(event:Event):void{
  if(connected||_NATIVE_callGameEvent==null)return;connected=true;
  this._NATIVE_callGameEvent("OnBetaGwentControllerTrace",[0,"MINIMAL_MOVIECLIP_PROBE","classic_probe",""]);
  this._NATIVE_callGameEvent("OnConfigUI",[]);
 }
 private function closeProbe():void{if(_NATIVE_callGameEvent!=null)this._NATIVE_callGameEvent("OnBetaGwentBoardClose",[]);}
 private function key(event:KeyboardEvent):void{if(event.keyCode==27)closeProbe();}
 private function click(event:MouseEvent):void{closeProbe();}
'''+ '\n'.join(stubs)+'\n}}'
    (BASE/'BetaGwentDeckMenu.as').write_text(as3,'utf8')
    java='C:/Program Files/Microsoft/jdk-11.0.12.7-hotspot/bin/java.exe'
    jar=ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'
    swf=BASE/'probe.swf'
    with (BASE/'compile.log').open('wb') as log:
        subprocess.run([java,'-jar',str(jar),'-load-config='+str(ROOT/'BetaGwent/ui/board-config.xml'),
            '-source-path='+str(BASE),'-swf-version=12','-target-player=10.3','-output='+str(swf),str(BASE/'BetaGwentDeckMenu.as')],
            stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    old=Resource((PREVIOUS/'resources-classic/resources/betagwent/betagwent_decks.redswf').read_bytes())
    _,p=old.properties(old.chunks[0]);size=struct.unpack_from('<I',old.chunks[0],p)[0]
    exporter=next(raw for kind,_,raw in movie_parts(old.chunks[0][p+4:p+4+size])[1] if kind==1000)
    prefix,tags,tail=movie_parts(swf.read_bytes());assert not tail
    native_body=prefix+exporter+b''.join(raw for _,_,raw in tags)
    gfx=b'CFX\x0c'+struct.pack('<I',len(native_body)+8)+zlib.compress(native_body,9)
    raw=bytearray(old.data);struct.pack_into('<I',raw,4,164);struct.pack_into('<I',raw,32,header_crc(raw))
    resource=Res(raw);resource.exports=resource.exports[:1]
    properties,_=old.properties(old.chunks[0])
    linkage=next(value for n,_,value in properties if old.names[n]=='linkageName')
    root=b'\0'+prop(resource,'linkageName','String',linkage)+prop(resource,'textures','array:2,0,handle:CSwfTexture',struct.pack('<I',0))+b'\0\0'
    resource.payloads=[root+struct.pack('<I',len(gfx))+gfx+bytes(4)]
    minimal=Resource(resource.build()).classic()
    assert Resource(minimal).classes==['CSwfResource']
    package=BASE/'package';content=package/'Mods/mod000BetaGwentClassic132Probe/content';content.mkdir(parents=True)
    movie=BASE/'betagwent_decks.redswf';movie.write_bytes(minimal)
    menu=PREVIOUS/'resources-classic/resources/gameplay/gui_new/guirsrc/r4deck_builder.menu'
    files={'betagwent/betagwent_decks.redswf':movie,'gameplay/gui_new/guirsrc/r4deck_builder.menu':menu}
    entries=write_bundle(files,content/'blob0.bundle',guids=cook_guid_map(ROOT/'BetaGwent/build/release202/ru/cooked/cook.db'))
    minimal_metadata(PREVIOUS/'resources-classic/metadata.store',content/'blob0.bundle',content/'metadata.store')
    (content.parent/'info.json').write_text(json.dumps(dict(name='Classic 1.32 minimal menu diagnostic',version='probe1',gameVersion='1.32'),indent=2),'utf8')
    (package/'README_RU.txt').write_text('''Это диагностическая накладка, не исправление и не игровой пакет.

Закройте игру. Оставьте основной modBetaGwentClassic132 (fix4) на месте.
Скопируйте Mods из архива в корень игры: появится mod000BetaGwentClassic132Probe.
Запустите 1.32 и откройте обычный просмотр колод. Ожидается простой тёмный
экран CLASSIC PROBE с текстом, без карт и оформления. Клик или Escape закрывает
его. Не начинайте партию и не сохраняйте игру во время этой проверки.
Сообщите, появился ли экран и что на нём написано. После закрытия игры сохраните
scriptslog.txt; затем удалите только mod000BetaGwentClassic132Probe из Mods.
Основной пакет менять или удалять не нужно. Отсутствие окна не означает,
что проверена причина: потребуется также подтвердить загрузку самой накладки.
''','utf-8-sig')
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-1.32-MinimalMenu-Probe.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in package.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    receipt=dict(archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),
                 resourceBytes=len(minimal),resources=len(entries),scriptBindings=len(stubs),
                 root='MovieClip',swfVersion=12,textures=0,scriptsChanged=False,gameplayVerified=False)
    (BASE/'probe.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    archive.with_suffix('.zip.sha256').write_text(receipt['sha256']+'  '+archive.name+'\n','ascii')
    print(json.dumps(receipt,indent=2),flush=True)


if __name__=='__main__':main()
