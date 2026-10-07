"""Stage 104 UI: decode attack size from setVisualCue kind (kind + 256*targets) and play
one projectile + impact per affected card simultaneously (original ACardAttack visuals)."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
src = ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
raw = src.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
t = raw.decode('utf-8-sig').replace('\r\n', '\n')
def rep(old, new):
    global t
    n = t.count(old)
    if n != 1: raise SystemExit(f'anchor {n}x: {old[:80]!r}')
    t = t.replace(old, new)
rep("""            if(!incoming||rev!=incoming.revision)return;
            incoming.cue={kind:kind,source:source,target:target,side:side,row:row,
                templateId:templateId,duration:duration,title:title};""",
"""            if(!incoming||rev!=incoming.revision)return;
            // kind + 256 * targets: one original Beta attack may hit many cards at once.
            var attackCount:int=Math.max(1,kind>>8);kind=kind&255;
            incoming.cue={kind:kind,source:source,target:target,side:side,row:row,
                templateId:templateId,duration:duration,title:title,attackCount:attackCount};""")
rep("""                if(target&&activeCue.kind==2){
                    var tx:Number=target.x+target.width/2;var ty:Number=target.y+target.height/2;""",
"""                var hits:Array=[];
                if(activeCue.kind==2){
                    if(int(activeCue.attackCount)>1){for(var hitKey:String in displayedCards){var hitPose:Object=displayedCards[hitKey];if(hitPose&&(int(hitPose.delta)!=0||int(hitPose.armorDelta)!=0))hits.push(hitPose);}}
                    if(hits.length==0&&target)hits.push(target);
                }
                for each(target in hits){
                    tint=target.delta>0?0x8FE0AE:target.delta<0?0xEE8B70:0xA7DCEE;
                    var tx:Number=target.x+target.width/2;var ty:Number=target.y+target.height/2;""")
out = t.replace('\n', '\r\n') if crlf else t
src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + out.encode('utf8')); print('ok')
