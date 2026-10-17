"""Generate Classic UI bitmap classes for native, pixel-preserving subimages."""
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/classic081-bitmap-fix11'
OUT = ROOT / 'BetaGwent/build/classic081-subimages-fix12'
PAGES = {12,13,14,15,16,17,18,20}


def write(path, text):
    path.write_bytes(b'\xef\xbb\xbf' + text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))


def main():
    assert not OUT.exists(), 'Keep prior builds immutable'
    ui = OUT / 'ui'
    shutil.copytree(SOURCE / 'ui', ui)
    text = (ui / 'src/BetaGwentHDArt.as').read_text('utf-8-sig')
    slots = json.loads(re.search(r'private static var slots:Object=(\{.*?\});', text).group(1))
    entries = []
    for key, slot in slots.items():
        if slot[0] not in PAGES: continue
        assert all(int(v) == v for v in slot)
        page, x, y, width, height = map(int, slot)
        parts = [(0,0,width,height)]
        if int(key) == -3708:  # The deck leader's nine-slice frame.
            sx, sy = min(24,width/3), min(24,height/3)
            for row in range(3):
                for col in range(3):
                    parts.append(([0,sx,width-sx][col], [0,sy,height-sy][row],
                                  [sx,width-sx*2,sx][col], [sy,height-sy*2,sy][row]))
        for index, (cx,cy,cw,ch) in enumerate(parts):
            assert all(int(v) == v for v in (cx,cy,cw,ch))
            name = 'BetaGwentClassicAtlas' + ('N' if int(key)<0 else 'P') + str(abs(int(key))) + '_' + str(index)
            entries.append(dict(id=int(key),page=page,x=x+int(cx),y=y+int(cy),width=int(cw),height=int(ch),
                                clip=[int(cx),int(cy),int(cw),int(ch)],className=name))
    mapping = ',\n'.join('"'+':'.join(map(str,[r['id'],*r['clip']]))+'":'+r['className'] for r in entries)
    registry = '''package {
 public class BetaGwentClassicSubImages {
  private static var classes:Object={'''+mapping+'''};
  public static function find(id:int,x:Number,y:Number,w:Number,h:Number):Class {
   return classes[id+":"+x+":"+y+":"+w+":"+h] as Class;
  }
 }
}
'''
    marker = '  try {\n   if(nativeUI[page]) {'
    assert text.count(marker) == 1
    text = text.replace(marker, '''  try {
   var fragment:Class=BetaGwentClassicSubImages.find(id,x,y,cw,ch);
   if(fragment) {
    // The native DefineSubImage already crops the atlas. No scrollRect,
    // BitmapData access or bitmap fill is needed on this Classic UI route.
    bitmap=new fragment() as Bitmap;
    if(!bitmap||bitmap.width<=0||bitmap.height<=0)throw new Error("Native fragment has no extent");
    reportAtlas(page,bitmap,"native-subimage");
    var fragmentView:Sprite=new Sprite();fragmentView.mouseEnabled=false;fragmentView.mouseChildren=false;
    bitmap.pixelSnapping="never";bitmap.smoothing=true;
    fragmentView.addChild(bitmap);fragmentView.scaleX=w/bitmap.width;fragmentView.scaleY=h/bitmap.height;
    return fragmentView;
   }
   if(nativeUI[page]) {''')
    # The subimage path must not query BitmapData either.
    text = text.replace('if(route!="native-bitmap")try', 'if(route=="atlas-fill")try')
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        target = ui / folder
        write(target / 'BetaGwentHDArt.as', text)
        write(target / 'BetaGwentClassicSubImages.as', registry)
        for row in entries:
            name=row['className']
            write(target/(name+'.as'), 'package {\n import mx.core.BitmapAsset;\n public class '+name+' extends BitmapAsset {\n  public function '+name+'(){super();}\n }\n}\n')
    manifest = json.loads((SOURCE/'ui-inputs.json').read_text('utf8'))
    manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ui/'src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    (OUT/'subimages.json').write_text(json.dumps(dict(pages=sorted(PAGES),entries=entries),indent=2),'utf8')
    print('Prepared native UI fragments:',len(entries),'in five Classic source copies')


if __name__=='__main__':main()
