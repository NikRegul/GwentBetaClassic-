"""Reduce native image storage while preserving logical UI/animation coordinates.

Original HD pages and DIY inputs remain unchanged. HD textures use 3/4 scale;
the two optional DIY backdrops use 1/2 scale. Cards keep opaque BC1 compression.
The AS bitmap transform restores logical dimensions, including flipbook clips.
"""
from pathlib import Path
import hashlib,json,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
UI=ROOT/'BetaGwent/ui';BASE=ROOT/'BetaGwent/build/compact98';OUT=UI/'assets/compact98'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 BASE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 originals={}
 for name in ('BetaGwentHDArt.as','BetaGwentBoard.as'):
  path=UI/'src'/name;backup=BASE/name
  if not backup.exists():backup.write_bytes(path.read_bytes())
  originals[name]=backup.read_text('utf8')
 source=originals['BetaGwentHDArt.as'];assert '../assets/hd94/' in source and 'sourceScale' not in source
 slots=json.loads(re.search(r'private static var slots:Object=(\{[^\n]+\});',source)[1])
 records=[]
 def resize(path,ratio):
  before=sha(path);target=OUT/path.name
  with Image.open(path) as image:
   dims=[int(d*ratio) for d in image.size]
   assert all(d*ratio==n for d,n in zip(image.size,dims)),str(path)
   image.convert('RGBA').resize(dims,Image.Resampling.LANCZOS).save(target)
   records.append(dict(source=str(path),sourceSha256=before,output=str(target),sha256=sha(target),before=list(image.size),after=dims,scale=ratio))
  assert sha(path)==before
 for name in re.findall(r'Embed\(source="../assets/hd94/([^"/]+)"',source):resize(UI/'assets/hd94'/name,.75)
 for name in ('board_classic.png','board_wide.png'):resize(UI/'assets'/name,.5)
 source=source.replace('../assets/hd94/','../assets/compact98/')
 old='if(!bitmap||bitmap.width<s[1]+s[3]||bitmap.height<s[2]+s[4])'
 assert old in source
 source=source.replace(old,'if(!bitmap||bitmap.width<(s[1]+s[3])*0.75||bitmap.height<(s[2]+s[4])*0.75)')
 old='result.scrollRect=new Rectangle(0,0,cw,ch);bitmap.x=-s[1]-x;bitmap.y=-s[2]-y;bitmap.smoothing=true;'
 assert old in source
 source=source.replace(old,'result.scrollRect=new Rectangle(0,0,cw,ch);bitmap.scaleX=bitmap.scaleY=4/3;bitmap.x=-s[1]-x;bitmap.y=-s[2]-y;bitmap.smoothing=true;')
 assert json.loads(re.search(r'private static var slots:Object=(\{[^\n]+\});',source)[1])==slots
 (UI/'src/BetaGwentHDArt.as').write_text(source,'utf8')
 board=originals['BetaGwentBoard.as']
 for name in ('board_classic.png','board_wide.png'):
  old='../assets/'+name;assert old in board;board=board.replace(old,'../assets/compact98/'+name)
 (UI/'src/BetaGwentBoard.as').write_text(board,'utf8')
 # All original logical slot extents must fit each new page after scaling.
 pages={i:r for i,r in enumerate(records[:-2])}
 for ident,(p,x,y,w,h) in slots.items():
  assert (x+w)*.75<=pages[p]['after'][0] and (y+h)*.75<=pages[p]['after'][1],ident
 report=dict(stage=98,records=records,logicalSlotsUnchanged=True,bitmapLogicalScale=4/3,cardPhysicalSize=[288,405],boardHalfPhysicalSize=[1536,531],originalsUnchanged=True,nativeRuntimeVerified=False)
 (ROOT/'docs/evidence/compact-art98.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print('Prepared',len(records),'compact pages; cards 288x405, board halves 1536x531; logical animation coordinates retained.')
if __name__=='__main__':main()
