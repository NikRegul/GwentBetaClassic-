"""Extract a stable 24 fps crop from the owner's original Beta recording (no AI upscale)."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageFilter
import av
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('video',type=Path);a=p.parse_args()
 out=ROOT/'BetaGwent/ui/assets/keg109/src/frames111';out.mkdir(parents=True,exist_ok=True)
 start=33.30;fps=24;count=48;scene=(0,140,2240,1400);moving=(640,140,1600,1400)
 c=av.open(str(a.video));c.seek(int(start*av.time_base));targets=[start+i/fps for i in range(count)];j=0;times=[]
 for f in c.decode(video=0):
  while j<count and f.time>=targets[j]:
   im=f.to_image().convert('RGB')
   if j==0:im.crop(scene).resize((1440,810),Image.Resampling.LANCZOS).save(out.parent/'scene111.png')
   im.crop(moving).resize((640,840),Image.Resampling.LANCZOS).filter(ImageFilter.UnsharpMask(radius=.6,percent=35,threshold=3)).save(out/f'{j+1:03}.png')
   times.append(f.time);j+=1
  if j==count:break
 if j!=count:raise ValueError('Video ended before the full opening')
 m={'video':str(a.video),'sha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),'fps':fps,'frames':count,'sceneCrop':scene,'movingCrop':moving,'timestamps':times,'sceneSize':[1440,810],'frameSize':[640,840],'interpolation':False}
 (out.parent/'capture111.json').write_text(json.dumps(m,indent=2),'utf8');print(m['frames'],'frames',m['frameSize'])
if __name__=='__main__':main()
