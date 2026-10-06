"""Apply compact atlas sampling and stable card/controller body bounds.

Runs after the compact98 builder. Existing images and WS sources are untouched.
Back up the three presentation sources once; subsequent invocations are no-ops.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];UI=ROOT/'BetaGwent/ui/src';BACK=ROOT/'BetaGwent/build/render99'

def change(source,old,new):
    assert old in source,old[:90]
    return source.replace(old,new)

def main():
    BACK.mkdir(parents=True,exist_ok=True)
    for name in ('BetaGwentHDArt.as','BetaGwentBoard.as','BetaGwentController.as'):
        current=UI/name;backup=BACK/name
        if not backup.exists():backup.write_bytes(current.read_bytes())
    hd=(UI/'BetaGwentHDArt.as').read_text('utf8')
    if 'Atlas quad sampling' not in hd:
        assert '../assets/compact98/' in hd
        hd=change(hd,'import flash.geom.Rectangle;','import flash.geom.Rectangle;\n import flash.geom.Matrix;')
        start=hd.index(' public static function clip(');end=hd.index(' public static function release()',start)
        hd=hd[:start]+''' public static function clip(id:int,w:Number,h:Number,x:Number,y:Number,cw:Number,ch:Number):Sprite {
  if(!has(id)||w<=0||h<=0||cw<=0||ch<=0)return null;
  var s:Array=slots[id];var page:int=s[0];var bitmap:Bitmap;
  try {
   if(shared[page]) {try{bitmap=new Bitmap(shared[page]);}catch(e:Error){bitmap=new types[page]() as Bitmap;}}
   else {bitmap=new types[page]() as Bitmap;if(bitmap)shared[page]=bitmap.bitmapData;}
   if(!bitmap||bitmap.width<(s[1]+s[3])*0.75||bitmap.height<(s[2]+s[4])*0.75)throw new Error("Compact page extent mismatch");
   var result:Sprite=new Sprite();result.mouseEnabled=false;result.mouseChildren=false;
   var left:Number=(s[1]+x)*0.75,top:Number=(s[2]+y)*0.75,pw:Number=cw*0.75,ph:Number=ch*0.75;
   // Atlas quad sampling: draw only the destination rectangle, rather than
   // submitting the entire atlas through nested fractional scrollRect transforms.
   // Half-texel inset prevents filtering the neighbouring card/board sprite.
   var data:BitmapData=shared[page] as BitmapData;
   if(data&&data.width>0&&data.height>0){
    try {
     var ix:Number=Math.min(0.5,pw/4),iy:Number=Math.min(0.5,ph/4);
     var sx:Number=w/(pw-2*ix),sy:Number=h/(ph-2*iy);
     result.graphics.beginBitmapFill(data,new Matrix(sx,0,0,sy,-(left+ix)*sx,-(top+iy)*sy),false,true);
     result.graphics.drawRect(0,0,w,h);result.graphics.endFill();return result;
    }catch(fillError:Error){result.graphics.clear();}
   }
   // Preserve the proven native Bitmap route if this GFx exposes no BitmapData.
   // Clip in physical pixels and apply a single scale. Never snap atlas pages.
   result.scrollRect=new Rectangle(0,0,pw,ph);
   bitmap.pixelSnapping="never";bitmap.smoothing=true;bitmap.x=-left;bitmap.y=-top;
   result.addChild(bitmap);result.scaleX=w/pw;result.scaleY=h/ph;return result;
  }catch(error:Error){lastError=id+": "+error.toString();return null;}
 }
''' + hd[end:]
        (UI/'BetaGwentHDArt.as').write_text(hd,'utf8')
    board=(UI/'BetaGwentBoard.as').read_text('utf8')
    if 'Stable card body bounds' not in board:
        board=change(board,'p.graphics.drawRect(0,0,handWidth,140);paintBetaCorners(p,cardWidth,cardHeight,0xC7FFF5);',
                     'p.graphics.drawRect(1.5,1.5,cardWidth-3,cardHeight-3);paintBetaCorners(p,cardWidth,cardHeight,0xC7FFF5);')
        board=change(board,'p.graphics.drawRect(-2,-2,cardWidth+4,cardHeight+4);','p.graphics.drawRect(2,2,cardWidth-4,cardHeight-4);')
        board=change(board,'controller.registerControl(p,c.title,null,c,detail,c.zone==8&&c.side==1?"hand":"card");',
                     '// Stable card body bounds exclude text fields, halos and transient effects.\n            var body:Rectangle=new Rectangle(0,0,bodyWidth>0?bodyWidth:p.width/p.scaleX,bodyHeight>0?bodyHeight:p.height/p.scaleY);\n            controller.registerControl(p,c.title,null,c,detail,c.zone==8&&c.side==1?"hand":"card",null,body);')
        board=change(board,'attachInspect(card,c,{description:c.description});','attachInspect(card,c,{description:c.description},230,150);')
        board=change(board,'attachInspect(p,c,cardDetails[c.id]);','attachInspect(p,c,cardDetails[c.id],140,198);')
        board=change(board,'controller.registerControl(p,title,callback);','controller.registerControl(p,title,callback,null,null,"control",null,new Rectangle(0,0,w,h));')
        board=change(board,'"row",{rowOnly:true,side:side,zone:zone});','"row",{rowOnly:true,side:side,zone:zone},new Rectangle(0,0,176,28));')
        board=change(board,'mark.graphics.drawRect(-2,-2,w+4,h+4);','mark.graphics.drawRect(focused?2:1,focused?2:1,w-(focused?4:2),h-(focused?4:2));')
        # Choice cards and tier borders use the same interior edge as focus.
        board=change(board,'p.graphics.drawRect(0,0,140,198);','p.graphics.drawRect(2,2,136,194);')
        board=change(board,'p.graphics.drawRect(0,0,cardWidth,cardHeight);','p.graphics.drawRect(1,1,cardWidth-2,cardHeight-2);')
        (UI/'BetaGwentBoard.as').write_text(board,'utf8')
    controller=(UI/'BetaGwentController.as').read_text('utf8')
    if 'private function bodyCorners' not in controller:
        controller=change(controller,'import flash.geom.Rectangle;','import flash.geom.Rectangle;\n    import flash.geom.Point;')
        controller=change(controller,'tag:String="control",placement:Object=null):void','tag:String="control",placement:Object=null,body:Rectangle=null):void')
        controller=change(controller,'if(placement!=null)n.placement=placement;','if(body!=null)n.body=body.clone();\n            if(placement!=null)n.placement=placement;')
        controller=change(controller,'var rect:Rectangle=sprite.getBounds(owner);','var rect:Rectangle=bodyBounds(n);')
        controller=change(controller,'var r:Rectangle=n.sprite.getBounds(owner);','var r:Rectangle=bodyBounds(n);')
        controller=change(controller,'var r:Rectangle=n?n.sprite.getBounds(owner):null;','var r:Rectangle=n?bodyBounds(n):null;')
        marker='        private function prune():void'
        helpers='''        private function bodyCorners(n:Object):Array
        {
            var b:Rectangle=n.body;
            var result:Array=[];
            for each(var point:Point in [new Point(b.left,b.top),new Point(b.right,b.top),new Point(b.right,b.bottom),new Point(b.left,b.bottom)])
                result.push(owner.globalToLocal(n.sprite.localToGlobal(point)));
            return result;
        }
        private function bodyBounds(n:Object):Rectangle
        {
            if(!n.body)return n.sprite.getBounds(owner);
            var points:Array=bodyCorners(n);var left:Number=points[0].x,top:Number=points[0].y,right:Number=left,bottom:Number=top;
            for each(var p:Point in points){left=Math.min(left,p.x);right=Math.max(right,p.x);top=Math.min(top,p.y);bottom=Math.max(bottom,p.y);}
            return new Rectangle(left,top,right-left,bottom-top);
        }
'''
        controller=change(controller,marker,helpers+marker)
        old='''graphics.lineStyle(5,0xF5E6A7,1);graphics.drawRoundRect(r.x-3,r.y-3,r.width+6,r.height+6,6,6);
                graphics.lineStyle(1,0x131A20,1);graphics.drawRoundRect(r.x-6,r.y-6,r.width+12,r.height+12,8,8);'''
        new='''graphics.lineStyle(3,0xF5E6A7,1);
                if(n.body){
                    var corners:Array=bodyCorners(n);graphics.moveTo(corners[0].x,corners[0].y);
                    for(var i:int=1;i<4;i++)graphics.lineTo(corners[i].x,corners[i].y);
                    graphics.lineTo(corners[0].x,corners[0].y);
                }else graphics.drawRoundRect(r.x,r.y,r.width,r.height,4,4);'''
        controller=change(controller,old,new)
        (UI/'BetaGwentController.as').write_text(controller,'utf8')
    report=dict(stage=99,compactPixelsUnchanged=True,nativeRuntimeVerified=False,
                fixes=['atlas quad and half-texel sampling','physical-pixel fallback without snapping','card selection size','controller body bounds and rotation'],
                sources={n:hashlib.sha256((UI/n).read_bytes()).hexdigest() for n in ('BetaGwentHDArt.as','BetaGwentBoard.as','BetaGwentController.as')})
    (ROOT/'docs/evidence/render99-preparation.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('Prepared rendering and body bounds; compact images unchanged.')

if __name__=='__main__':main()
