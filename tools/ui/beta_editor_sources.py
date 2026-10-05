"""Extract Beta 0.9.24 deckbuilder sprites without changing Unity bundles."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
SOURCE=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui'
OUTPUT=ROOT/'BetaGwent/ui/assets/beta-editor'
SPECS={
    'deckbuilder':[(-1200,'db_background',4,2),(-1210,'db_create_shelf_horizontal',1,1),
                   (-1211,'db_create_shelf_vertical',1,1),(-1212,'db_create_shelf_side',1,1),
                   (-1213,'db_card_copies_bg',1,1),(-1214,'db_filter_tier_all',1,1)],
    'deckpicker':[(-1220,'dp_slot_bronze',1,1),(-1221,'dp_slot_silver',1,1),(-1222,'dp_slot_gold',1,1)],
    'filterbuttons':[(-1230,'db_filter_tier_bronze',1,1),(-1231,'db_filter_tier_silver',1,1),(-1232,'db_filter_tier_gold',1,1)],
    'factioniconsmedium':[(-1240,'monsters_icon_med',1,1),(-1241,'nilfgaard_icon_med',1,1),
                          (-1242,'northern_icon_med',1,1),(-1243,'scoia_icon_med',1,1),(-1244,'skellege_icon_med',1,1)],
    'sidepreview':[(-1250,'side_preview_title_bg_MON',1,1),(-1251,'side_preview_title_bg_NIL',1,1),
                   (-1252,'side_preview_title_bg_NR',1,1),(-1253,'side_preview_title_bg_SCO',1,1),
                   (-1254,'side_preview_title_bg_SKE',1,1),(-1260,'side_preview_info_bg_MON',1,1),
                   (-1261,'side_preview_info_title_bg_NIL_GENERAL',1,1),(-1262,'side_preview_info_bg_NR',1,1),
                   (-1263,'side_preview_info_bg_SCO',1,1),(-1264,'side_preview_info_bg_SKE',1,1),
                   (-1270,'general_metal_title_line',1,1)]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract():
    OUTPUT.mkdir(parents=True,exist_ok=True);entries=[];sources={};originals=[]
    for bundle,specs in SPECS.items():
        source=SOURCE/'spriteatlases/uber'/bundle;digest=sha(source);sources[str(source)]=digest
        env=UnityPy.load(str(source));sprites={o.read().m_Name:o for o in env.objects if o.type.name=='Sprite'}
        for first,name,columns,rows in specs:
            obj=sprites[name];image=obj.read().image.convert('RGBA');original=OUTPUT/(name+'.png');image.save(original)
            originals.append((name,image))
            for i in range(columns*rows):
                col,row=i%columns,i//columns
                crop=[round(col*image.width/columns),round(row*image.height/rows),round((col+1)*image.width/columns),round((row+1)*image.height/rows)]
                target=OUTPUT/(str(first-i)+'.png');image.crop(crop).resize((128,180),Image.Resampling.LANCZOS).save(target)
                entries.append(dict(atlasId=first-i,name=name,pathId=obj.path_id,source=str(source),sourceSha256=digest,
                    originalSize=list(image.size),grid=[columns,rows],crop=crop,thumbnail=str(target),thumbnailSha256=sha(target)))
    prefab=SOURCE/'prefabs/deckbuilder_base';sources[str(prefab)]=sha(prefab)
    env=UnityPy.load(str(prefab));objects={o.path_id:o for o in env.objects};layout=[]
    for obj in env.objects:
        if obj.type.name!='RectTransform':continue
        tree=obj.read_typetree();go=objects.get(tree['m_GameObject']['m_PathID'])
        layout.append(dict(pathId=obj.path_id,name=go.read().m_Name if go else '',transform=tree))
    (OUTPUT/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n','utf8')
    sheet=Image.new('RGB',(1000,((len(originals)+3)//4)*200),'#202020');draw=ImageDraw.Draw(sheet)
    for i,(name,image) in enumerate(originals):
        image=image.copy();image.thumbnail((240,160));x=i%4*250;y=i//4*200
        sheet.paste(image,(x,y),image);draw.text((x,y+163),name,fill='white')
    sheet.save(ROOT/'BetaGwent/ui/build/beta-editor92.png')
    assert all(sha(Path(p))==digest for p,digest in sources.items())
    (ROOT/'docs/evidence/beta-editor92.json').write_text(json.dumps(dict(stage=92,sources=sources,sprites=entries,
        rectTransforms=len(layout),sourceUnmodified=True,nativeRuntimeVerified=False),ensure_ascii=False,indent=2)+'\n','utf8')
    return entries
if __name__=='__main__':print('Extracted',len(extract()),'deckbuilder atlas tiles')
