"""Adapt the original Beta lock meshes/textures to a compact GFx overlay.

Reads the client only. Keeps the existing HUD, adds no new texture page, and
records the original show/hide clip timings (Unity shaders are not emulated).
"""
from pathlib import Path
import hashlib,json,re,sys
from PIL import Image,ImageOps
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from beta_board_sources import bake

def main():
    source=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    out=ROOT/'BetaGwent/ui/assets/lock126';out.mkdir(exist_ok=True)
    env=UnityPy.load(str(source));objects={o.path_id:o for o in env.objects}
    overlay=Image.new('RGBA',(192,268));records=[]
    for texture,mesh in [(752,856),(513,819),(651,849)]:
        t=objects[texture].read();m=objects[mesh].read()
        png=out/(t.m_Name+'.png');obj=out/(m.m_Name+'.obj')
        t.image.save(png);obj.write_text(m.export(),'utf8')
        # Shared card coordinates, not separate bounding boxes: preserve the
        # crossing angles and lock position of the original mesh assembly.
        layer=bake(obj,png,[1,1],[0,0],size=overlay.size,
                   world_bounds=([-10,-14,-1],[10,14,1]),frontmost=True)
        # Original battle camera looks towards +Z; keep screen handedness.
        overlay.alpha_composite(ImageOps.mirror(layer))
        records.append(dict(texture=texture,mesh=mesh,name=t.m_Name))
    overlay.save(out/'lock-overlay.png')
    timings={}
    for pid in [967,968,969]:
        clip=objects[pid].read_typetree()
        timings[clip['m_Name']]=round(clip['m_MuscleClip']['m_StopTime']*1000)
    codepath=ROOT/'BetaGwent/ui/src/BetaGwentHDArt.as'
    code=codepath.read_text('utf-8-sig')
    slots=json.loads(re.search(r'private static var slots:Object=(\{.*?\});',code)[1])
    page=Image.open(ROOT/'BetaGwent/ui/assets/battle120/hud120.png').convert('RGBA')
    # Reuse transparent, unregistered HUD space before extending the page.
    occupied=np.asarray(page)[:,:,3]>0
    for ident,slot in slots.items():
        if slot[0]==15 and int(ident) not in [-3770,-3771]:
            _,x,y,w,h=slot;occupied[y:y+h,x:x+w]=True
    for ident,art in [(-3770,overlay),(-3771,objects[651].read().image.resize((32,48),Image.Resampling.LANCZOS))]:
        w,h=art.size;integral=np.pad(occupied.astype(np.int32),((1,0),(1,0))).cumsum(0).cumsum(1)
        chosen=None
        for y in range(2,page.height-h-2,4):
            for x in range(2,page.width-w-2,4):
                if integral[y+h+2,x+w+2]-integral[y-2,x+w+2]-integral[y+h+2,x-2]+integral[y-2,x-2]==0:
                    chosen=(x,y);break
            if chosen:break
        if chosen is None:
            chosen=(2,page.height+2)
            extended=Image.new('RGBA',(page.width,page.height+h+4));extended.paste(page,(0,0));page=extended
            occupied=np.pad(occupied,((0,h+4),(0,0)))
        x,y=chosen;page.paste(art,(x,y));occupied[y-2:y+h+2,x-2:x+w+2]=True
        slots[str(ident)]=[15,x,y,w,h]
    page.save(out/'hud126.png')
    code=re.sub(r'private static var slots:Object=\{.*?\};','private static var slots:Object='+json.dumps(slots,separators=(',',':'))+';',code)
    code=re.sub(r'\[Embed\(source="[^"]+"([^\n]+)private static var Page15:Class;',r'[Embed(source="../assets/lock126/hud126.png"\1private static var Page15:Class;',code)
    codepath.write_text(code,'utf-8-sig')
    (ROOT/'BetaGwent/ui/src/BetaGwentLock126.as').write_text(
        'package { public class BetaGwentLock126 {\n'
        ' public static const OVERLAY:int=-3770; public static const ICON:int=-3771;\n'
        f' public static const SHOW_MS:int={timings["TokenLockShowAnimation"]};\n'
        f' public static const HIDE_MS:int={timings["TokenLockHideAnimation"]};\n'
        '} }\n','utf-8-sig')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise ValueError('Original client changed')
    report=dict(source=str(source),sha256=digest,sourceUnchanged=True,records=records,
                timings=timings,atlasSize=page.size,extraTexturePages=0,
                adaptation='Original meshes, UVs and textures; orthographic GFx, original clip durations. Unity shaders omitted.')
    (out/'provenance.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report))

if __name__=='__main__':main()
