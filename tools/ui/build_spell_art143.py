"""Adapt the verified DestroyFire and Lightning materials into small native textures."""
from pathlib import Path
import gzip, hashlib, json, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ui'))
from beta_visual_sources import light_alpha

def main():
    manifest=json.loads((ROOT/'BetaGwent/build/special-vfx142/manifest.json').read_text('utf8'))
    out=ROOT/'BetaGwent/ui/assets/special143';out.mkdir(parents=True,exist_ok=True)
    records=[]
    # These are actual renderer material bindings, not similarly named unused textures.
    for name,material,texture,grid in [('fire',211,728,(5,5)),('frame',214,631,(1,1)),('lightning',103,488,(1,1)),('sparks',251,735,(2,2))]:
        mat=next(e for e in manifest['exported'] if e.get('sourceAsset')=='sharedassets8.assets' and e['pathId']==material)
        data=json.loads(gzip.decompress((ROOT/mat['configuration']).read_bytes()))
        assert any(v['m_Texture']['m_PathID']==texture for _,v in data['m_SavedProperties']['m_TexEnvs'])
        item=next(e for e in manifest['exported'] if e.get('sourceAsset')=='sharedassets8.assets' and e['pathId']==texture)
        image,conversion=light_alpha(Image.open(ROOT/item['image']))
        cols,rows=grid
        if name=='fire':
            # Unity UV rows start at the bottom. Repack in playback order, with a
            # transparent gutter so DDS bilinear sampling cannot bleed adjacent frames.
            sheet=Image.new('RGBA',(5*100,5*132))
            for i in range(25):
                x,y=i%5,4-i//5
                tile=image.crop((round(x*image.width/5),round(y*image.height/5),round((x+1)*image.width/5),round((y+1)*image.height/5)))
                sheet.paste(tile.resize((96,128),Image.Resampling.LANCZOS),((i%5)*100+2,(i//5)*132+2))
            image=sheet
        elif name=='lightning':image=image.resize((512,256),Image.Resampling.LANCZOS)
        else:image=image.resize((256,256),Image.Resampling.LANCZOS)
        target=out/(name+'.png');image.save(target)
        records.append(dict(name=name,material=material,texture=texture,source=item['image'],sourceSha256=hashlib.sha256((ROOT/item['image']).read_bytes()).hexdigest(),output=str(target.relative_to(ROOT)),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),conversion=conversion,grid=grid))
    (ROOT/'docs/evidence/spell-art143.json').write_text(json.dumps(dict(stage=143,originalMaterials=True,textures=records),indent=2)+'\n','utf8')
    preview=Image.new('RGB',(640,420),'#25343f')
    for n,name in enumerate(('fire','frame','lightning','sparks')):
        im=Image.open(out/(name+'.png'));im.thumbnail((300,180));preview.paste(im,((n%2)*320,(n//2)*210),im)
    preview.save(out/'contact.png')
    print('Adapted original burn and lightning textures')
if __name__=='__main__':main()
