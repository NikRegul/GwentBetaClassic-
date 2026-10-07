package
{
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.Rectangle;
    public class BetaGwentCardArt
    {
        private static var seen:Object={};
        public static var successes:int=0;
        public static var failures:int=0;
        public static var lastError:String="";
        public static function view(id:int,w:Number,h:Number):Sprite
        {
            if(BetaGwentHDArt.has(id)){
                if(seen.hasOwnProperty(id)&&seen[id]===false)return null;
                var hd:Sprite=BetaGwentHDArt.view(id,w,h);
                if(hd){if(!seen.hasOwnProperty(id)){seen[id]=true;successes++;}return hd;}
                if(!seen.hasOwnProperty(id))failures++;
                seen[id]=false;lastError=BetaGwentHDArt.lastError;return null;
            }
            // Stage 108: the legacy TW3 weather atlas is no longer shipped.
            return null;
        }
        private static var IDS:Array=[-1,-2,-3,-4,-5,-6,-7,-8];
        public static function release():void
        { BetaGwentHDArt.release();seen={};successes=0;failures=0;lastError=""; }
    }
}
