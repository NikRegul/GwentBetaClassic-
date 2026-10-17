"""Replace only auxiliary movie ABC and bind 24 frames to each original atlas."""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import zlib

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui')]
from formats import Resource,require
from update_board_resource import movie_parts
from install_native_hd93 import symbols,tag
from build_classic_bitmap_fix import native,image_names

BUILD=ROOT/'BetaGwent/build/classic081-effect-state-fix16'
CLASSES=['BetaGwentClassicLeaderFrame'+str(i).zfill(2) for i in range(24)]


def run(args,log):
    with log.open('wb') as output:
        p=subprocess.run(list(map(str,args)),stdout=output,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,timeout=180)
    require(p.returncode==0,log.read_text('utf8',errors='replace')[-4000:])


def prepare():
    work=BUILD/'leader-template';require(not (work/'verification.json').exists(),'Keep verified template immutable');work.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'BetaGwent/build/leaders137/atlas.png',work/'atlas.png')
    source=(ROOT/'tools/ui/leaders060/BetaLeaderMovieClassic.as').read_text('utf8').replace('FRAME_CLASSES',','.join(CLASSES))
    (work/'BetaLeaderMovie.as').write_text(source,'utf8')
    for name in CLASSES:
        (work/(name+'.as')).write_text('package { import mx.core.BitmapAsset; public class '+name+' extends BitmapAsset { public function '+name+'(){super();} } }','utf8')
    java=Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')
    lib=ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib'
    run([java,'-Xmx1g','-jar',lib/'mxmlc.jar','-load-config='+str(ROOT/'BetaGwent/ui/board-config.xml'),
         '-source-path='+str(work),'-source-path+='+str(BUILD/'ui/src'),'-output='+str(work/'premium.swf'),work/'BetaLeaderMovie.as'],work/'compile.log')
    exporter=Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\tools\GFx4\gfxexport_mult4fix.exe')
    run([exporter,'-i','DDS','-quick','-d1','-o',work,'-d',work,work/'premium.swf'],work/'export.log')
    raw=(work/'premium.gfx').read_bytes()
    if raw[:3]==b'GFX':raw=b'FWS'+raw[3:]
    tags=movie_parts(raw)[1]
    bindings=symbols(tags);require(set(bindings)=={0,2},'Original atlas linkage IDs differ')
    require(bindings[0]==b'BetaLeaderMovie','Document class changed')
    run([java,'-jar',lib/'compiler-swfdump.jar','-abc',work/'premium.swf'],work/'abc.txt')
    dump=(work/'abc.txt').read_text('utf8',errors='replace')
    require('getproperty  bitmapData' not in dump and 'beginBitmapFill' not in dump,'Leader still samples BitmapData')
    (work/'verification.json').write_text(json.dumps(dict(nativeFrames=24,bindingIds=sorted(bindings),
        originalPixelsUsed=True,bitmapDataGetterRemoved=True,nativeGameplayVerified=False),indent=2),'utf8')
    print('Compiled one native-frame ABC for all 322 existing leader/intro atlases.')


class Editor:
    def __init__(self):
        raw=(BUILD/'leader-template/premium.gfx').read_bytes()
        if raw[:3]==b'GFX':raw=b'FWS'+raw[3:]
        tags=movie_parts(raw)[1]
        self.abc=next(raw for code,p,raw in tags if code==82)
        self.bindings=symbols(tags)
        self.reports=[]

    def edit(self,name,raw):
        if not name.replace('\\','/').startswith(('gameplay/gui_new/swf/betagwentleaders/','gameplay/gui_new/swf/betagwentleaderintros/')):return raw
        resource=Resource(raw);pos,movie=native(resource);prefix,tags,tail=movie_parts(movie);old=symbols(tags)
        require(set(old)==set(self.bindings)=={0,2},'Unexpected leader binding set')
        images={struct.unpack_from('<H',p)[0]:struct.unpack('<6H',p) for c,p,_ in tags if c==1008}
        require(set(images)=={1,2} and images[2][2:]==(0,0,1152,936),'Unexpected leader atlas bounds')
        image=images[2][1];add=[];mapping=bytearray()
        for frame,className in enumerate(CLASSES):
            cid=3+frame;x=frame%6*192;y=frame//6*234
            add.append(tag(1008,struct.pack('<6H',cid,image,x,y,x+192,y+234)))
            mapping+=struct.pack('<H',cid)+className.encode('ascii')+b'\0'
        add.append(tag(76,struct.pack('<H',24)+mapping))
        aliases={old[k]:self.bindings[k] for k in old};body=bytearray(prefix)
        for code,p,encoded in tags:
            if code==82:body+=b''.join(add)+self.abc;continue
            if code==76:
                group=symbols([(code,p,encoded)])
                encoded=tag(76,struct.pack('<H',len(group))+b''.join(struct.pack('<H',k)+self.bindings[k]+b'\0' for k in group))
            elif code==1009:
                n=p[10];oldName=p[11:11+n];newName=aliases.get(oldName,oldName)
                encoded=tag(1009,p[:10]+bytes([len(newName)])+newName+p[11+n:])
            body+=encoded
        edited=movie[:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+tail,9)
        require(image_names(edited)==image_names(movie),'Leader texture filename changed')
        checked=movie_parts(edited)[1];newSymbols=symbols(checked)
        require(newSymbols[0]==old[0] and all(newSymbols[3+i]==n.encode('ascii') for i,n in enumerate(CLASSES)),'Lost frame class')
        definitions={struct.unpack_from('<H',p)[0]:struct.unpack('<6H',p) for c,p,_ in checked if c==1008}
        require(all(definitions[k]==v for k,v in images.items()),'Original atlas definitions changed')
        for i in range(24):
            x=i%6*192;y=i//6*234;require(definitions[3+i]==(3+i,image,x,y,x+192,y+234),'Wrong leader frame rectangle')
        root=resource.chunks[0][:pos]+struct.pack('<I',len(edited))+edited+struct.pack('<I',0)
        result=resource.replace_chunks([root,*resource.chunks[1:]]);verified=Resource(result)
        require(verified.chunks[1:]==resource.chunks[1:] and verified.imports==resource.imports,'Leader pixels/dependencies changed')
        require(len(result)<=0x2000000,'Classic cap exceeded')
        self.reports.append(dict(path=name,frames=24,textureChunksPreserved=True,originalImageDefinitionsPreserved=True))
        return result


if __name__=='__main__':prepare()
