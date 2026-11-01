package {
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.Matrix;
    // Original material/UV cells. One bounded quad; no scrollRect on atlases.
    public class BetaGwentElementArt164 {
        [Embed(source="../assets/elements164/Elements.png",compression="true",quality="100")] private static var Elements:Class;
        private static var types:Array=[Elements];
        private static var bitmaps:Array=[];
        public static function paint(sprite:Sprite,index:int,w:Number,h:Number):void {
            var rect:Array=BetaGwentElementData164.RECTS[index];if(!rect)return;
            var family:int=int(rect[0]);
            if(!bitmaps[family]){var type:Class=types[family];var bitmap:Bitmap=new type() as Bitmap;bitmaps[family]=bitmap.bitmapData;}
            var sx:Number=w/(rect[3]-1),sy:Number=h/(rect[4]-1);
            sprite.graphics.clear();
            sprite.graphics.beginBitmapFill(bitmaps[family],new Matrix(sx,0,0,sy,-w/2-(rect[1]+.5)*sx,-h/2-(rect[2]+.5)*sy),false,true);
            sprite.graphics.drawRect(-w/2,-h/2,w,h);sprite.graphics.endFill();
        }
        public static function cell(index:int,w:Number,h:Number):Sprite {
            var sprite:Sprite=new Sprite();sprite.mouseEnabled=false;sprite.mouseChildren=false;paint(sprite,index,w,h);return sprite;
        }
        // Deck editor frames appended below the original cells (0.9.4a). Centred
        // quad of one atlas rectangle; null when this menu's atlas lacks the rows.
        public static function region(index:int,rect:Array,w:Number,h:Number):Sprite {
            if(!rect||!(w>0)||!(h>0))return null;
            if(bitmaps[0]===undefined){
                try{var bitmap:Bitmap=new Elements() as Bitmap;bitmaps[0]=bitmap?bitmap.bitmapData:null;}catch(error:Error){bitmaps[0]=null;}
            }
            var atlas:BitmapData=bitmaps[0] as BitmapData;
            if(!atlas||atlas.width<rect[0]+rect[2]||atlas.height<rect[1]+rect[3])return null;
            var sprite:Sprite=new Sprite();sprite.mouseEnabled=false;sprite.mouseChildren=false;
            var sx:Number=w/rect[2],sy:Number=h/rect[3];
            sprite.graphics.beginBitmapFill(atlas,new Matrix(sx,0,0,sy,-w/2-rect[0]*sx,-h/2-rect[1]*sy),false,true);
            sprite.graphics.drawRect(-w/2,-h/2,w,h);sprite.graphics.endFill();
            return sprite;
        }
    }
}
