"""Compose a Nexus header from preserved game art; no generated illustrations."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy

def main():
 out=ROOT/'BetaGwent/release/nexus';out.mkdir(exist_ok=True)
 dest=out/'GwentBetaClassic-header-v2.png'
 if dest.exists():raise RuntimeError('Preserve previous header; choose another filename')
 inputs={}
 def remember(p):inputs[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 bundle=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/spriteatlases/uber/logo_en-us'
 remember(bundle)
 logo=next(o.read().image.convert('RGBA') for o in UnityPy.load(str(bundle)).objects if o.type.name=='Sprite')
 logo=logo.crop(logo.getchannel('A').getbbox())
 manifest=json.loads((ROOT/'docs/evidence/card-art-build.json').read_text('utf8'))
 canvas=Image.new('RGBA',(1800,600),(15,18,19,255))
 for ident,side in ((112103,0),(112101,1)):
  c=next(x for x in manifest['cards'] if x['templateId']==ident)
  p=Path(c['source']);remember(p)
  art=ImageOps.fit(Image.open(p).convert('RGBA').crop(c['crop']),(490,700),method=Image.Resampling.LANCZOS)
  art=art.crop((0,30,490,630));mask=Image.new('L',art.size);d=ImageDraw.Draw(mask)
  for x in range(490):
   edge=x if side==0 else 489-x
   opacity=max(0,min(230,int((490-edge)/175*230)))
   d.line((x,0,x,599),fill=opacity)
  art.putalpha(mask);canvas.alpha_composite(art,(0 if side==0 else 1310,0))
 logo.thumbnail((640,380),Image.Resampling.LANCZOS)
 canvas.alpha_composite(logo,((1800-logo.width)//2,18))
 draw=ImageDraw.Draw(canvas)
 font=ImageFont.truetype('C:/Windows/Fonts/MyriadPro-Cond.otf',82)
 small=ImageFont.truetype('C:/Windows/Fonts/MyriadPro-Cond.otf',27)
 draw.text((900,429),'BETA CLASSIC',font=font,anchor='mm',fill=(229,225,214))
 draw.line((670,493,1130,493),fill=(100,111,105),width=1)
 draw.text((900,538),'THE WITCHER 3 MOD   /   0.9.24',font=small,anchor='mm',fill=(160,171,166))
 canvas.convert('RGB').save(dest)
 canvas.convert('RGB').save(dest.with_suffix('.jpg'),quality=95,subsampling=0)
 assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest for p,digest in inputs.items())
 report=dict(image=str(dest),size=[1800,600],generatedArt=False,sources=inputs,method='Original Beta logo and Ciri/Geralt art with flat typography and edge fades; deterministic Pillow composition.')
 (out/'GwentBetaClassic-header-v2-sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
