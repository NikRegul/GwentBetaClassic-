"""Build one-shot entrances; keep the existing loops as fallback and previews."""
import io
import json
from pathlib import Path
from PIL import Image
import build_leaders136 as native

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'BetaGwent/build/leader-intro-resources142'
CAPTURE=ROOT/'BetaGwent/build/leader-intros142'
DEPOT='gameplay/gui_new/swf/betagwentleaderintros'

def main():
    bindings=json.loads((ROOT/'BetaGwent/build/release060-preparation/leaders/BetaGwentLeaderCatalog.json').read_text('utf8'))
    assert len(bindings)==21 and (CAPTURE/'complete.txt').exists()
    native.WORK=WORK;native.TARGET=WORK/'resources'/DEPOT;native.DEPOT=DEPOT
    template=native.compile_template(Image.new('RGB',(1152,936)),Path(__file__).parent/'leaders060/BetaLeaderMovie137.as')
    reference,_=native.validate_resource(ROOT/'GwentB/myproject1/workspace/betagwent/betagwent_board.redswf')
    root,_=reference.properties_at(reference.exports[0]['data']);texture,_=reference.properties_at(reference.exports[1]['data'])
    imports=next(raw for code,p,raw in native.movie_parts(native.unpack_root(reference)[1])[1] if code==1000)
    arts={};resources={}
    for art in sorted(set(bindings.values())):
        folder=CAPTURE/art;meta=folder/'complete.json'
        if not meta.exists():
            assert (folder/'missing-intro.txt').exists();continue
        d=json.loads(meta.read_text('utf8'));frames=sorted(folder.glob('*.png'))
        assert d['entranceOnly'] and not d['loopOnly'] and len(frames)==d['frames'] and d['fps']==24
        assert len({native.sha(p.read_bytes()) for p in frames})>1,'static entrance'
        images=[Image.open(p).convert('RGB') for p in frames]
        for start in range(0,len(images),24):
            atlas=Image.new('RGB',(1152,936))
            for i in range(24):atlas.paste(images[min(start+i,len(images)-1)],((i%6)*192,(i//6)*234))
            stream=io.BytesIO();atlas.save(stream,format='DDS',pixel_format='DXT1')
            name=art+'_intro_p'+str(start//24).zfill(3)
            resources[name]=native.native_movie(name,atlas,template,reference,root,texture,imports,dds=stream.getvalue(),portrait=(192,234))
        arts[art]=dict(frames=len(images),duration=d['duration'],pages=(len(images)+23)//24,once=True)
        print('Entrance',art,len(images),'frames',flush=True)
    assert len(arts)==12
    source=['package { public class BetaGwentLeaderIntroCatalog {',
        'private static const ARTS:Object='+json.dumps(bindings,separators=(',',':'))+';',
        'private static const INTROS:Object='+json.dumps(arts,separators=(',',':'))+';',
        'public static function info(id:int):Object {var art:String=ARTS[String(id)];return art?INTROS[art]:null;}',
        'public static function path(id:int,page:int):String {var art:String=ARTS[String(id)],d:Object=info(id);if(!d||page<0||page>=d.pages)return null;var n:String=String(page);while(n.length<3)n="0"+n;return "swf/betagwentleaderintros/"+art+"_intro_p"+n+".swf";}',
        '} }']
    (ROOT/'BetaGwent/ui/src/BetaGwentLeaderIntroCatalog.as').write_text('\n'.join(source)+'\n','utf8')
    report=dict(stage=142,bindings={id:art for id,art in bindings.items() if art in arts},loopFallback=[int(id) for id,art in bindings.items() if art not in arts],arts=arts,resources=resources,once=True,nativeGameTested=False)
    (ROOT/'docs/evidence/leader-intros142.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('Built',len(resources),'native entrance pages; 12 entrances, 9 current-loop fallbacks')

if __name__=='__main__':main()
