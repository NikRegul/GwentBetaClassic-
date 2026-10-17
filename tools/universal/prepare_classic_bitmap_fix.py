"""Prepare a Classic-only native Bitmap UI path and one-shot atlas diagnostics."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/classic081-boot-fix4'
OUT = ROOT / 'BetaGwent/build/classic081-bitmap-fix11'


def main():
    assert not OUT.exists(), 'Keep previous builds immutable'
    ui = OUT / 'ui'
    shutil.copytree(SOURCE / 'ui', ui)
    art_path = ui / 'src/BetaGwentHDArt.as'
    art = art_path.read_text('utf-8-sig')
    old = ' private static var shared:Array=[];'
    assert art.count(old) == 1
    art = art.replace(old, old + '''
 // Classic UI uses native linked Bitmap characters directly. Keep the card,
 // board and accepted weather/effect sampling paths unchanged.
 private static var nativeUI:Object={10:true,11:true,12:true,13:true,14:true,15:true,16:true,17:true,18:true,20:true};
 private static var atlasReports:Object={};
 private static var atlasPending:Array=[];
 public static function takeAtlasReports():Array {var result:Array=atlasPending;atlasPending=[];return result;}
 private static function reportAtlas(page:int,bitmap:Bitmap,route:String):void {
  if(atlasReports.hasOwnProperty(page))return;
  atlasReports[page]=true;
  var dataSize:String="unread";
  if(route!="native-bitmap")try{var data:BitmapData=bitmap.bitmapData;dataSize=data?data.width+"x"+data.height:"null";}catch(error:Error){dataSize=error.toString();}
  atlasPending.push("page="+page+" bitmap="+bitmap.width+"x"+bitmap.height+" data="+dataSize+" route="+route);
 }
''')
    old = '''  try {
   if(shared[page])'''
    assert art.count(old) == 1
    art = art.replace(old, '''  try {
   if(nativeUI[page]) {
    // A new embedded instance retains the native GFx image binding. Do not
    // construct it from the BitmapData getter of an external DDS character.
    bitmap=new types[page]() as Bitmap;
    if(!bitmap||bitmap.width<(s[1]+s[3])*pixelScale||bitmap.height<(s[2]+s[4])*pixelScale)throw new Error("Native UI page extent mismatch");
    reportAtlas(page,bitmap,"native-bitmap");
    var nativeView:Sprite=new Sprite();nativeView.mouseEnabled=false;nativeView.mouseChildren=false;
    var nativeW:Number=cw*pixelScale,nativeH:Number=ch*pixelScale;
    nativeView.scrollRect=new Rectangle(0,0,nativeW,nativeH);
    bitmap.pixelSnapping="never";bitmap.smoothing=true;
    bitmap.x=-(s[1]+x)*pixelScale;bitmap.y=-(s[2]+y)*pixelScale;
    nativeView.addChild(bitmap);nativeView.scaleX=w/nativeW;nativeView.scaleY=h/nativeH;
    return nativeView;
   }
   if(shared[page])''')
    old = '   var result:Sprite=new Sprite();result.mouseEnabled=false;result.mouseChildren=false;'
    assert art.count(old) == 1
    art = art.replace(old, '   reportAtlas(page,bitmap,"atlas-fill");\n' + old)
    art = art.replace('shared=[];lastError="";', 'shared=[];lastError="";atlasReports={};atlasPending=[];')
    board = (ui / 'src/BetaGwentBoard.as').read_text('utf-8-sig')
    old = '            artworkReportPending=false;'
    assert board.count(old) == 1
    board = board.replace(old, old + '''
            for each(var atlasReport:String in BetaGwentHDArt.takeAtlasReports())
                send("OnBetaGwentControllerTrace",[0,"ATLAS_STATE","classic_bitmap_fix11",atlasReport]);''')
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name, text in [('BetaGwentBoard.as', board), ('BetaGwentHDArt.as', art)]:
            data = b'\xef\xbb\xbf' + text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
            (ui / folder / name).write_bytes(data)
    manifest = json.loads((SOURCE / 'ui-inputs.json').read_text('utf8'))
    manifest['sources'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ui / 'src').glob('*.as')}
    (OUT / 'ui-inputs.json').write_text(json.dumps(manifest, indent=2), 'utf8')
    print('Prepared five isolated Classic UI copies with native Bitmap rendering and atlas logs')


if __name__ == '__main__':
    main()
