"""Stage 104: Beta small-card faces on the board/hand (skin 3): cropped art (aspect of the
SmallCardFull plane 17.64x21.46), tier frame (-1600..-1602), faction banner (-1610..-1615)
with the power digit on it. Fail-closed anchors; BOM/CRLF kept."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
src = ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
raw = src.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
t = raw.decode('utf-8-sig').replace('\r\n', '\n')
def rep(old, new):
    global t
    n = t.count(old)
    if n != 1: raise SystemExit(f'anchor {n}x: {old[:90]!r}')
    t = t.replace(old, new)
if 'paintBetaFace' in t: raise SystemExit('already applied')
# Helpers.
rep("        private function paintCardBack(parent:Sprite,w:Number,h:Number,side:int):void\n",
"""        // Beta small card (SmallCardFull: 17.64 x 21.46 units). Banner 4.4 x 8.2 at (0.12,0.33).
        private static const BETA_CARD_ASPECT:Number=17.64/21.46;
        private function betaBannerRect(w:Number,h:Number):Array{return [w*.12/17.64,h*.33/21.46,w*4.4/17.64,h*8.2/21.46];}
        private function paintBetaFace(p:Sprite,templateId:int,w:Number,h:Number):void
        {
            var size:Array=BetaGwentHDArt.size(templateId);
            if(size){
                var sw:Number=size[0],sh:Number=size[1];var ch:Number=Math.min(sh,sw*h/w);var cw:Number=Math.min(sw,ch*w/h);
                var art:Sprite=BetaGwentHDArt.clip(templateId,w,h,(sw-cw)/2,(sh-ch)*.25,cw,ch);
                if(art)p.addChild(art);else paintArt(p,templateId,w,h,0,0);
            }else paintArt(p,templateId,w,h,0,0);
            var entry:Object=BetaGwentFullCatalog.find(templateId);
            var tier:int=entry?int(entry.tier):2;var faction:int=entry?int(entry.faction):1;
            paintArt(p,tier==8||tier==1?-1602:tier==4?-1601:-1600,w,h,0,0);
            var b:Array=betaBannerRect(w,h);
            paintArt(p,-1610-(faction==2?0:faction==4?1:faction==8?2:faction==16?3:faction==32?4:5),b[2],b[3],b[0],b[1]);
        }
        private function betaPowerField(p:Sprite,value:String,w:Number,h:Number,color:uint):TextField
        {
            var b:Array=betaBannerRect(w,h);var size:int=Math.max(14,Math.round(h*.2));
            var field:TextField=text(p,value,b[0]-4,b[1]+b[3]*.06,b[2]+8,size,color);field.height=size*1.5;
            field.defaultTextFormat=new TextFormat("$NormalFont",size,color,true,null,null,null,null,"center");field.setTextFormat(field.defaultTextFormat);
            field.filters=[new GlowFilter(0x000000,1,3,3,6,1)];
            return field;
        }
        private function paintCardBack(parent:Sprite,w:Number,h:Number,side:int):void
""")
if 'import flash.filters.GlowFilter;' not in t:
    rep("    import flash.geom.Rectangle;\n", "    import flash.geom.Rectangle;\n    import flash.filters.GlowFilter;\n")
# Row cards: Beta aspect.
rep("""            var step:Number=Math.min((g.h-8)*256/360+8,(g.w-24)/Math.max(1,count));""",
    """            var step:Number=Math.min((g.h-8)*(skin==3?BETA_CARD_ASPECT:256/360)+8,(g.w-24)/Math.max(1,count));""")
# Hand cards: Beta aspect and original hand line.
rep("""            var handWidth:Number=skin==3?100:Math.min(112,970/Math.max(1,handCount))-8;""",
    """            var handWidth:Number=skin==3?104:Math.min(112,970/Math.max(1,handCount))-8;""")
rep("""                var g:Object=isHand?{x:handLeft+c.index*step,y:(selected==c.id?900:920)-Math.abs(handAngle)*1.5,h:140}:rowGeometry(c.side,c.zone);""",
    """                var g:Object=isHand?{x:handLeft+c.index*step,y:(skin==3?(selected==c.id?926:944):(selected==c.id?900:920))-Math.abs(handAngle)*1.5,h:skin==3?Math.round(104/BETA_CARD_ASPECT):140}:rowGeometry(c.side,c.zone);""")
rep("""                var cardWidth:Number=isHand?handWidth:layout.w;var cardHeight:Number=isHand?140:g.h-8;""",
    """                var cardWidth:Number=isHand?handWidth:layout.w;var cardHeight:Number=isHand?g.h:g.h-8;""")
rep("""                if(concealed)paintCardBack(p,cardWidth,cardHeight,c.side);else paintArt(p,c.templateId,cardWidth-6,cardHeight-6);""",
    """                if(concealed)paintCardBack(p,cardWidth,cardHeight,c.side);else if(skin==3)paintBetaFace(p,c.templateId,cardWidth,cardHeight);else paintArt(p,c.templateId,cardWidth-6,cardHeight-6);""")
# Power on the banner (Beta) instead of the dark badge; no caption band on Beta hand cards.
rep("""                if(isHand){var band:Sprite=panel(p,3,cardHeight-36,cardWidth-6,33,0x101315,.84);band.mouseEnabled=false;}
                var badge:Sprite=panel(p,3,3,34,34,0x101315,.85);badge.mouseEnabled=false;
                var powerValue:String=concealed?"?":c.power>0||!isHand?String(c.power):"★";
                var powerBadge:TextField=text(p,powerValue,7,2,40,isHand?28:25,concealed?0xE9C46A:powerColor(c));""",
"""                if(isHand&&skin!=3){var band:Sprite=panel(p,3,cardHeight-36,cardWidth-6,33,0x101315,.84);band.mouseEnabled=false;}
                if(skin!=3){var badge:Sprite=panel(p,3,3,34,34,0x101315,.85);badge.mouseEnabled=false;}
                var powerValue:String=concealed?"?":c.power>0||!isHand?String(c.power):(skin==3?"":"★");
                var powerBadge:TextField=skin==3&&!concealed?betaPowerField(p,powerValue,cardWidth,cardHeight,powerColor(c)):text(p,powerValue,7,2,40,isHand?28:25,concealed?0xE9C46A:powerColor(c));""")
rep("""                if(isHand){var caption:TextField=text(p,c.title,7,cardHeight-34,cardWidth-12,13);caption.height=32;}""",
    """                if(isHand&&skin!=3){var caption:TextField=text(p,c.title,7,cardHeight-34,cardWidth-12,13);caption.height=32;}""")
# Power-change pulse keeps its own field position.
rep("""                    animations.push({sprite:powerBadge,fromX:7,fromY:2,toX:7,toY:2,""",
    """                    animations.push({sprite:powerBadge,fromX:powerBadge.x,fromY:powerBadge.y,toX:powerBadge.x,toY:powerBadge.y,""")
out = t.replace('\n', '\r\n') if crlf else t
src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + out.encode('utf8')); print('card faces applied')
