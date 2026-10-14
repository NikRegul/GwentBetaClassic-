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
    }
}
