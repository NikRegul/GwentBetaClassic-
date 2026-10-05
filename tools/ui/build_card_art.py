"""Pack existing DIY artwork into an embedded atlas for native DDS export."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageOps, ImageChops
from card_art_sources import resolve
from native_weather_sources import extract as extract_weather

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'LegacyGwent-diy(1)/LegacyGwent-diy/src/Cynthia.Card.Unity/src/Cynthia.Unity.Card/Assets/Addressables/Cards'
UI = ROOT / 'BetaGwent/ui'
IDS = [v['templateId'] for v in json.loads((ROOT/'data/beta924/duel/slice.json').read_text(encoding='utf-8'))['cards']]
runtime_ids=set(IDS)
mode_views={v['templateId'] for item in json.loads((ROOT/'data/beta924/duel/modes.json').read_text(encoding='utf-8'))['cards'] for v in item['choices']}
runtime_ids |= mode_views
mode_views |= {201666,201667,201719,201720,201721,201722}
mode_views |= {int(v) for v in json.loads((ROOT/'data/beta924/duel/nilfgaard.json').read_text(encoding='utf-8'))['views']}
mode_views |= {int(v) for v in json.loads((ROOT/'data/beta924/duel/scoiatael.json').read_text(encoding='utf-8'))['views']}
mode_views |= {201717,201718}
mode_views |= {int(v) for v in json.loads((ROOT/'data/beta924/duel/neutral.json').read_text(encoding='utf-8'))['views']}
runtime_ids |= mode_views
full=json.loads((ROOT/'data/beta924/planning/full_catalog.json').read_text(encoding='utf-8'))['cards']
all_ids=runtime_ids|{v['templateId'] for v in full}
missing=[ident for ident in sorted(all_ids) if resolve(ident)[0] is None]
if runtime_ids.intersection(missing):raise RuntimeError('Implemented artwork missing: '+str(runtime_ids.intersection(missing)))
IDS=sorted(all_ids-set(missing))
WIDTH, HEIGHT, COLS = 128, 180, 32
weather = extract_weather()
ROWS = (len(IDS)+len(weather)+COLS-1)//COLS
ATLAS_WIDTH, ATLAS_HEIGHT = COLS*WIDTH, ROWS*HEIGHT
entries = []
preview = Image.new('RGB', (COLS * 152, ROWS * 220), '#16191e')
for ordinal, template in enumerate(IDS):
    source, binding = resolve(template)
    artwork_id = source.stem
    original = Image.open(source).convert('RGBA')
    # Unity exports have an opaque square canvas with black/white padding.
    # Alpha bbox includes it; use the uniform bottom-right canvas colour.
    rgb = original.convert('RGB')
    canvas = Image.new('RGB', rgb.size, rgb.getpixel((rgb.width-1,rgb.height-1)))
    bounds = ImageChops.difference(rgb, canvas).getbbox()
    if not bounds: raise ValueError('Empty artwork: ' + str(source))
    cropped = original.crop(bounds).convert('RGB')
    thumb = ImageOps.fit(cropped, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    indexed = thumb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    target = UI / 'assets/cards' / (str(template)+'.png')
    target.parent.mkdir(parents=True, exist_ok=True)
    indexed.convert('RGB').save(target)
    preview.paste(indexed.convert('RGB'), ((ordinal%COLS)*152+12,(ordinal//COLS)*220+12))
    entries.append(dict(templateId=template,source=str(source),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        crop=list(bounds),thumbnail=str(target),thumbnailSha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        size=[WIDTH,HEIGHT],paletteColors=256,atlasTile=[ordinal%COLS,ordinal//COLS],artworkTemplateId=artwork_id,bindingPolicy=binding))

atlas=Image.new('RGBA',(ATLAS_WIDTH,ATLAS_HEIGHT),(0,0,0,255))
for ordinal, template in enumerate(IDS):
    thumb=Image.open(UI/'assets/cards'/(str(template)+'.png')).convert('RGBA')
    atlas.paste(thumb,((ordinal%COLS)*WIDTH,(ordinal//COLS)*HEIGHT))
for ordinal, item in enumerate(weather, len(IDS)):
    # Paste RGBA verbatim: compositing onto black would destroy weather alpha.
    atlas.paste(Image.open(item['thumbnail']).convert('RGBA'), ((ordinal%COLS)*WIDTH,(ordinal//COLS)*HEIGHT))
atlas.save(UI/'assets/card_atlas.png')
runtime = """package
{
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.Rectangle;
    public class BetaGwentCardArt
    {
        [Embed(source=\"../assets/card_atlas.png\",compression=\"true\",quality=\"100\")]
        private static var NativeAtlas:Class;
        private static var seen:Object={};
        private static var sharedAtlas:BitmapData;
        private static var slots:Object;
        public static var successes:int=0;
        public static var failures:int=0;
        public static var lastError:String=\"\";
        public static function view(id:int,w:Number,h:Number):Sprite
        {
            if(!slots){slots={};for(var i:int=0;i<IDS.length;i++)slots[IDS[i]]=i;}
            if(!slots.hasOwnProperty(id))return null;
            var slot:int=int(slots[id]);
            if(seen[id]===false)return null;
            try {
                var bitmap:Bitmap;
                if(sharedAtlas){
                    try { bitmap=new Bitmap(sharedAtlas); }
                    catch(sharedError:Error){ bitmap=new NativeAtlas() as Bitmap; }
                } else {
                    bitmap=new NativeAtlas() as Bitmap;
                    // Keep the proven native Bitmap path if this GFx build exposes no BitmapData.
                    if(bitmap)sharedAtlas=bitmap.bitmapData;
                }
                if(!bitmap || bitmap.width<768 || bitmap.height<360)throw new Error(\"Native atlas missing or invalid extent\");
                var result:Sprite=new Sprite();
                result.mouseEnabled=false;result.mouseChildren=false;
                result.scrollRect=new Rectangle(0,0,128,180);
                bitmap.x=-(slot%6)*128;bitmap.y=-int(slot/6)*180;
                bitmap.smoothing=true;result.addChild(bitmap);
                result.scaleX=w/128;result.scaleY=h/180;
                if(!seen.hasOwnProperty(id)){seen[id]=true;successes++;}
                return result;
            } catch(error:Error) {
                if(!seen.hasOwnProperty(id))failures++;
                seen[id]=false;lastError=id+\": \"+error.toString();return null;
            }
        }
        private static var IDS:Array=[IDS_LIST];
        public static function release():void
        { seen={};successes=0;failures=0;lastError=\"\"; }
    }
}
""".replace('IDS_LIST',','.join(map(str,IDS+[item['atlasId'] for item in weather]))).replace('slot%6',f'slot%{COLS}').replace('slot/6',f'slot/{COLS}').replace('bitmap.width<768',f'bitmap.width<{ATLAS_WIDTH}').replace('bitmap.height<360',f'bitmap.height<{ATLAS_HEIGHT}')
(UI/'src/BetaGwentCardArt.as').write_text(runtime,encoding='utf-8')
preview.save(UI/'build/card-art-contact-sheet.png')
(ROOT/'docs/evidence/card-art-build.json').write_text(json.dumps(dict(cards=entries,
    atlasSize=[ATLAS_WIDTH,ATLAS_HEIGHT],missingTemplateIds=missing,weatherSprites=weather,
    encoding='Native embedded DXT5 atlas; Shared immutable BitmapData; constant-time atlas slots; Sprite.scrollRect tiles128x180; no pixel writes',
    sourcePolicy='DIY artwork only; rules/description remain canonical Beta. Originals unchanged.',
    nativeRuntimeVerified=False,
    pipeline='Royale Embed -> GFxExport DDS -> CSwfTexture/SubImage resource; original board texture chunks retained'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Packed{len(IDS)} DIY illustration bindings in native atlas{ATLAS_WIDTH}x{ATLAS_HEIGHT}/DXT5; runtime pending.')
