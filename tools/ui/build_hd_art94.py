"""Keep original Beta UI pixels and world-space board proportions in HD pages.

Never edits Unity bundles. Card illustrations use their source crop, without
the previous 128x180 palette conversion. Atlas rectangle aliases share pixels.
"""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageOps,ImageDraw
from beta_board_sources import bake
ROOT=Path(__file__).resolve().parents[2]
UI=ROOT/'BetaGwent/ui';OUT=UI/'assets/hd94'
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

EXTRA={
 'buttons':[(-1400,'btn_wide_idle_450'),(-1401,'btn_wide_hovered_450'),
            (-1402,'btn_wide_down_450'),(-1403,'btn_wide_inactive_300'),
            (-1404,'btn_square_idle'),(-1405,'btn_square_hovered'),(-1406,'btn_square_toggle')],
 'shared':[(-1410,'textsearch_idle'),(-1411,'textsearch_icon'),(-1412,'large_image_frame'),
           (-1413,'woodpanel_large_bg'),(-1414,'woodpanel_small_bg'),(-1415,'card_count_background'),
           (-1416,'divider_metal_vertical'),(-1417,'scrollbar_handle')],
 'deckpicker':[(-1420,'dp_stats_mon_bg'),(-1421,'dp_stats_nil_bg'),(-1422,'dp_stats_nor_bg'),
               (-1423,'dp_stats_sco_bg'),(-1424,'dp_stats_ske_bg'),
               (-1430,'dp_ornament_mon_bg'),(-1431,'dp_ornament_nil_bg'),(-1432,'dp_ornament_nor_bg'),
               (-1433,'dp_ornament_sco_bg'),(-1434,'dp_ornament_ske_bg'),
               (-1440,'dp_icon_crown'),(-1441,'dp_slot_diamond_bg'),(-1442,'dp_icon_valid')],
 'board':[(-1450,'tooltip-background_big (1)'),(-1451,'CommonBigCardPreviewDivider'),
          (-1452,'floating_big-bar_GRAY'),(-1453,'floating_big-bar_GREEN'),(-1454,'floating_big-bar_RED')]
}

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((ROOT/'docs/evidence/card-art-build.json').read_text('utf8'))
 board=json.loads((ROOT/'docs/evidence/beta-boards91.json').read_text('utf8'))
 editor=json.loads((ROOT/'docs/evidence/beta-editor92.json').read_text('utf8'))
 slots={};pages=[];sources={};originals=[]
 def remember(path):sources[str(path)]=sha(path)
 def save_page(image,name):
  path=OUT/(name+'.png');image.save(path)
  pages.append(dict(path=str(path),size=list(image.size),sha256=sha(path)))
  return len(pages)-1
 cards=manifest['cards']
 for first in range(0,len(cards),70):
  group=cards[first:first+70];height=((len(group)+9)//10)*540
  image=Image.new('RGBA',(3840,height));page=len(pages)
  for i,c in enumerate(group):
   source=Path(c['source']);remember(source)
   crop=Image.open(source).convert('RGBA').crop(c['crop'])
   art=ImageOps.fit(crop,(384,540),method=Image.Resampling.LANCZOS)
   x,y=i%10*384,i//10*540;image.paste(art,(x,y))
   slots[c['templateId']]=[page,x,y,384,540]
  save_page(image,'cards-'+str(first//70))
  print('HD illustrations',first+len(group),flush=True)
 page=len(pages);image=Image.new('RGBA',(4096,3540));board_info=[]
 for i,half in enumerate(board['halves']):
  tile=next(t for t in board['tiles'] if t.get('faction')==half['faction'] and t.get('side')==half['side'])
  mesh,texture=Path(tile['mesh']),Path(tile['source']);remember(mesh);remember(texture)
  directory=mesh.parent
  go=next(json.loads(p.read_text('utf8')) for p in directory.glob('*-GameObject.json')
          if json.loads(p.read_text('utf8'))['m_Name']==('board_bottom' if half['side']==1 else 'board_top'))
  material=next(json.loads(p.read_text('utf8')) for p in directory.glob('*-Material.json')
                if any(k=='_MainTex' and v['m_Texture']['m_PathID']==int(texture.name.split('-')[1] if texture.name.startswith('-') else texture.name.split('-')[0])*(-1 if texture.name.startswith('-') else 1)
                       for k,v in json.loads(p.read_text('utf8'))['m_SavedProperties']['m_TexEnvs']))
  binding=next(v for k,v in material['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex')
  bounds=([-124,-95,0],[160,3,0]) if half['side']==1 else ([-124,-3,0],[160,95,0])
  art=bake(mesh,texture,[binding['m_Scale'][k] for k in ('x','y')],
           [binding['m_Offset'][k] for k in ('x','y')],size=(2048,708),world_bounds=bounds,frontmost=True)
  path=OUT/f"board-{half['faction']}-{half['side']}.png";art.save(path)
  x,y=i%2*2048,i//2*708;image.paste(art,(x,y));ident=-1300-i
  slots[ident]=[page,x,y,2048,708]
  # Keep older quarter bindings at source resolution for existing consumers.
  for j,alias in enumerate(half['atlasIds']):slots[alias]=[page,x+j*512,y,512,708]
  board_info.append(dict(id=ident,faction=half['faction'],side=half['side'],worldBounds=bounds,
                         mesh=str(mesh),texture=str(texture),image=str(path),size=[2048,708]))
  print('HD board',half['faction'],half['side'],flush=True)
 save_page(image,'boards')
 pending=[];background=next(Path(t['source']) for t in board['tiles'] if t['atlasId']==-1100)
 remember(background);pending.append((-1311,'battle-background',Image.open(background).convert('RGBA')))
 remember(UI/'assets/beta-editor/db_background.png')
 pending.append((-1310,'editor-background',Image.open(UI/'assets/beta-editor/db_background.png').convert('RGBA')))
 for t in editor['sprites']:
  if t['name']=='db_background':continue
  source=UI/'assets/beta-editor'/(t['name']+'.png');remember(source)
  pending.append((t['atlasId'],t['name'],Image.open(source).convert('RGBA')))
 # Keep the original Beta hit/weather textures and flipbook cells at full
 # resolution too. The extractor's 'original' PNGs are raw Unity textures:
 # additive RGB-on-black must become straight alpha just like the thumbnails.
 # Otherwise a native HD highlight paints black across the target's card.
 from beta_visual_sources import light_alpha
 environments={}
 for effect in manifest['betaVisuals']:
  source=Path(effect['source']);remember(source)
  if effect.get('original'):
   original=Path(effect['original']);remember(original)
   art,conversion=light_alpha(Image.open(original))
   if effect['atlasId']==-101:
    # Match the cropped legacy frame; its centre must remain transparent.
    art=art.crop(art.getchannel('A').getbbox())
    assert art.getpixel((art.width//2,art.height//2))[3]==0
    assert art.getchannel('A').getextrema()[1]>0
   if effect['atlasId'] in (-101,-102,-103,-105,-106):
    assert conversion=='additive-light-to-straight-alpha',effect['name']
  else:
   key=str(source)
   if key not in environments:environments[key]={o.path_id:o for o in UnityPy.load(key).objects}
   art,_=light_alpha(environments[key][effect['pathId']].read().image)
   if effect.get('crop'):art=art.crop(effect['crop'])
  pending.append((effect['atlasId'],effect['name'],art))
 for bundle,specs in EXTRA.items():
  source=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/spriteatlases/uber'/bundle
  remember(source);env=UnityPy.load(str(source))
  sprites={o.read().m_Name:o for o in env.objects if o.type.name=='Sprite'}
  for ident,name in specs:
   art=sprites[name].read().image.convert('RGBA');art.save(OUT/(name.replace('/','_')+'.png'))
   pending.append((ident,name,art))
 canvas=Image.new('RGBA',(4096,4096));x=y=row=0;page=len(pages)
 for ident,name,art in sorted(pending,key=lambda v:-v[2].height):
  if x+art.width+4>4096:x=0;y+=row+4;row=0
  if art.width>4096 or art.height>4096:raise RuntimeError('Original sprite exceeds native page limit: '+name)
  if y+art.height>4096:
   save_page(canvas.crop((0,0,4096,(y+row+3)//4*4)),'interface-'+str(page))
   canvas=Image.new('RGBA',(4096,4096));x=y=row=0;page=len(pages)
  canvas.paste(art,(x,y));slots[ident]=[page,x,y,art.width,art.height]
  originals.append(dict(id=ident,name=name,size=list(art.size)))
  x+=art.width+4;row=max(row,art.height)
 save_page(canvas.crop((0,0,4096,(y+row+3)//4*4)),'interface-'+str(page))
 for whole,start in [(-1310,-1200),(-1311,-1100)]:
  p,x,y,w,h=slots[whole]
  for i in range(8):slots[start-i]=[p,x+(i%4)*w//4,y+(i//4)*h//2,w//4,h//2]
 code='''package {
 import flash.display.Bitmap;
 import flash.display.BitmapData;
 import flash.display.Sprite;
 import flash.geom.Rectangle;
 public class BetaGwentHDArt {
 EMBEDS
 private static var types:Array=[TYPES];
 private static var shared:Array=[];
 private static var slots:Object=SLOTS;
 public static var lastError:String="";
 public static function has(id:int):Boolean {return slots.hasOwnProperty(id);}
 public static function size(id:int):Array {return has(id)?[slots[id][3],slots[id][4]]:null;}
 public static function view(id:int,w:Number,h:Number):Sprite {
  if(!has(id))return null;
  return clip(id,w,h,0,0,slots[id][3],slots[id][4]);
 }
 public static function clip(id:int,w:Number,h:Number,x:Number,y:Number,cw:Number,ch:Number):Sprite {
  if(!has(id))return null;
  var s:Array=slots[id];var page:int=s[0];var bitmap:Bitmap;
  try {
   if(shared[page]) {try{bitmap=new Bitmap(shared[page]);}catch(e:Error){bitmap=new types[page]() as Bitmap;}}
   else {bitmap=new types[page]() as Bitmap;if(bitmap)shared[page]=bitmap.bitmapData;}
   if(!bitmap||bitmap.width<s[1]+s[3]||bitmap.height<s[2]+s[4])throw new Error("HD page extent mismatch");
   var result:Sprite=new Sprite();result.mouseEnabled=false;result.mouseChildren=false;
   result.scrollRect=new Rectangle(0,0,cw,ch);bitmap.x=-s[1]-x;bitmap.y=-s[2]-y;bitmap.smoothing=true;
   result.addChild(bitmap);result.scaleX=w/cw;result.scaleY=h/ch;return result;
  }catch(error:Error){lastError=id+": "+error.toString();return null;}
 }
 public static function release():void {shared=[];lastError="";}
 }
}
'''
 embeds='\n'.join(f'[Embed(source="../assets/hd94/{Path(p["path"]).name}",compression="true",quality="100")] private static var Page{i}:Class;' for i,p in enumerate(pages))
 code=code.replace('EMBEDS',embeds).replace('TYPES',','.join('Page'+str(i) for i in range(len(pages))))
 code=code.replace('SLOTS','{'+','.join('"'+str(k)+'":'+json.dumps(v,separators=(',',':')) for k,v in slots.items())+'}')
 (UI/'src/BetaGwentHDArt.as').write_text(code,'utf8')
 path=UI/'src/BetaGwentCardArt.as';code=path.read_text('utf8')
 marker='            if(!slots){slots={};for(var i:int=0;i<IDS.length;i++)slots[IDS[i]]=i;}'
 if 'BetaGwentHDArt.has' not in code:
  code=code.replace(marker,'''            if(BetaGwentHDArt.has(id)){
                if(seen.hasOwnProperty(id)&&seen[id]===false)return null;
                var hd:Sprite=BetaGwentHDArt.view(id,w,h);
                if(hd){if(!seen.hasOwnProperty(id)){seen[id]=true;successes++;}return hd;}
                if(!seen.hasOwnProperty(id))failures++;
                seen[id]=false;lastError=BetaGwentHDArt.lastError;return null;
            }
'''+marker)
  code=code.replace('{ seen={};successes=0;failures=0;lastError=""; }','{ BetaGwentHDArt.release();seen={};successes=0;failures=0;lastError=""; }')
 # Only particles/weather stay in the small atlas. Cards and interface use HD.
 extras=manifest['weatherSprites'];cols=8
 assert len(extras)==8
 height=((len(extras)+cols-1)//cols)*180
 small=Image.new('RGBA',(1024,height))
 for i,t in enumerate(extras):small.paste(Image.open(t['thumbnail']).convert('RGBA'),(i%cols*128,i//cols*180))
 small.save(UI/'assets/legacy_weather95.png')
 code=code.replace('../assets/card_atlas.png','../assets/legacy_weather95.png')
 import re
 code=re.sub(r'private static var IDS:Array=\[[^\]]*\];','private static var IDS:Array=['+','.join(str(t['atlasId']) for t in extras)+'];',code)
 code=re.sub(r'slot%\d+',f'slot%{cols}',code);code=re.sub(r'slot/\d+',f'slot/{cols}',code)
 code=re.sub(r'bitmap.width<\d+',f'bitmap.width<1024',code)
 code=re.sub(r'bitmap.height<\d+',f'bitmap.height<{height}',code)
 path.write_text(code,'utf8')
 manifest['atlasSize']=[1024,height];manifest['hdManifest']='docs/evidence/hd-art94.json'
 manifest['encoding']='HD cards/interface pages plus small particle/weather atlas; native DXT5; shared immutable bitmaps'
 (ROOT/'docs/evidence/card-art-build.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 assert all(sha(Path(path))==digest for path,digest in sources.items())
 report=dict(stage=94,pages=pages,bindings=len(slots),cards=len(cards),boards=board_info,interface=originals,
             sourceHashes=sources,originalsUnchanged=True,paletteReduction=False,nativeRuntimeVerified=False,
             projection='Shared world-space orthographic bounds; no nonuniform board scaling or Unity lighting')
 (ROOT/'docs/evidence/hd-art94.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 print('HD pages',[(p['size']) for p in pages],'bindings',len(slots),flush=True)
if __name__=='__main__':main()
