"""Adopt the audited Beta ValidVFX without growing the native texture atlas.

One-time integration. Original source particles, timing, RGB/alpha convention
and root offset are retained; the widget scales 400 source units to 372 pixels.
"""
import hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
def main():
 candidate=ROOT/'BetaGwent/build/deck-valid094a-texture-candidate-20261027-01'
 report=json.loads((candidate/'report.json').read_text())
 spec=ROOT/'data/beta924/design/editor_vfx094.json'
 assert sha(spec)==report['previousMetadataSha256']
 assert report['assignedPixelsUnchanged'] and report['allBlocksOutsideUnusedSlotUnchanged'] and report['addedTextureBytes']==0
 for src,dst in [('Elements.png','BetaGwent/ui/assets/elements164/Elements.png'),('append-bc3.bin','BetaGwent/ui/assets/editor094/append-bc3.bin'),('editor_vfx094.json','data/beta924/design/editor_vfx094.json')]:
  shutil.copy2(candidate/src,ROOT/dst)
 data=json.loads(spec.read_text());rect=data['rects'][28]
 packets=ROOT/'BetaGwent/build/deck-valid094a-recipes-20261027-02/packets.json'
 frames=json.loads(packets.read_text())['ValidVFX'];assert len(frames)==48
 compact=[[[round(p['pose'][k],6) for k in ['x','y','w','h','angle','r','g','b','a']] for p in f['particles']] for f in frames]
 duration=frames[-1]['seconds']*1000
 source='''package {
    // Beta ValidVFX, original 48 source samples / 158 particles, not card VFX.
    public class BetaGwentEditorValidData095 {
        public static const MS:Number=%s;
        public static const RECT:Array=%s;
        public static const FRAMES:Array=%s;
    }
}
'''%(round(duration,6),json.dumps(rect,separators=(',',':')),json.dumps(compact,separators=(',',':')))
 write(ROOT/'BetaGwent/ui/src/BetaGwentEditorValidData095.as',source)
 boardfiles=[ROOT/'BetaGwent/ui'/folder/'BetaGwentBoard.as' for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']]+[ROOT/'tools/features091/BetaGwentBoard_classic093.as']
 for p in boardfiles:
  s=p.read_text(encoding='utf-8-sig')
  old='if(!pending.bulk)editorFlight={id:pending.id,amount:pending.amount,origin:pending.origin};'
  new='''if(!pending.bulk){
                    var beforeTotal:int=0,afterTotal:int=0;
                    for(key in pending.before)beforeTotal+=int(pending.before[key]);
                    for(key in now)afterTotal+=int(now[key]);
                    editorFlight={id:pending.id,amount:pending.amount,origin:pending.origin,
                        valid095:pending.amount==1&&beforeTotal==24&&afterTotal==25&&revision>pending.revision&&editorState.leader==pending.leader};
                }'''
  assert s.count(old)==1;s=s.replace(old,new)
  old='editorPending={id:id,amount:amount,before:editorCounts(),slot:editorState.slot,faction:editorState.faction,origin:'
  new='editorPending={id:id,amount:amount,before:editorCounts(),revision:revision,leader:editorState.leader,slot:editorState.slot,faction:editorState.faction,origin:'
  assert s.count(old)==1;s=s.replace(old,new)
  old='''                if(c){var tile:Sprite=new Sprite();content.addChild(tile);tile.mouseEnabled=false;tile.mouseChildren=false;'''
  new='''                if(editorFlight.valid095&&skin==3&&BetaGwentUi138.flashes){
                    var validFx:BetaGwentEditorValid095=new BetaGwentEditorValid095(360);
                    if(validFx.available){validFx.x=232;validFx.y=214;content.addChild(validFx);
                        animations.push({sprite:validFx,editorValid095:validFx,fromX:232,fromY:214,toX:232,toY:214,remove:true,duration:BetaGwentEditorValidData095.MS});}
                }
'''+old
  assert s.count(old)==1;s=s.replace(old,new)
  old='''                if(motion.editorFx094){'''
  new='''                if(motion.editorValid095)motion.editorValid095.render(elapsed<delay?-1:progress);
'''+old
  assert s.count(old)==1;s=s.replace(old,new);write(p,s)
 # All source copies, including helpers, use the normal build's canonical list.
 p=ROOT/'tools/features091/prepare_ui091.py';s=p.read_text(encoding='utf-8-sig')
 s=s.replace("'BetaGwentEditorFxData094.as']","'BetaGwentEditorFxData094.as','BetaGwentEditorValid095.as','BetaGwentEditorValidData095.as']")
 for source,old in [(boardfiles[0],'615a0b1d89ec3126fe2bb7bb6f2796a404cb5e4979b1931aafe4c3b7aaa687c8'),(boardfiles[-1],'a385ae0c2ec71eda0896ec2356561eefb8047001ba2370234c6ed8e120358753')]:
  assert s.count(old)==1;s=s.replace(old,sha(source))
 p.write_text(s,encoding='utf8')
 print(json.dumps(dict(sourcePacketsSha256=sha(packets),frames=len(frames),particles=sum(map(len,compact)),atlasBytesAdded=0,boardCopies=len(boardfiles))))
if __name__=='__main__':main()
