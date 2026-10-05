package
{
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.Rectangle;
    public class BetaGwentCardArt
    {
        [Embed(source="../assets/card_atlas.png",compression="true",quality="100")]
        private static var NativeAtlas:Class;
        private static var seen:Object={};
        private static var sharedAtlas:BitmapData;
        private static var slots:Object;
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
            if(!slots){slots={};for(var i:int=0;i<IDS.length;i++)slots[IDS[i]]=i;}
            if(!slots.hasOwnProperty(id))return null;
            var slot:int=int(slots[id]);
            if(seen[id]===false)return null;
            try {
                var bitmap:Bitmap;
                if(sharedAtlas){
                    try { bitmap=new Bitmap(sharedAtlas); }
                    catch(sharedError:Error){ bitmap=new NativeAtlas() as Bitmap; }
                } else {
                    bitmap=new NativeAtlas() as Bitmap;
                    // Keep the proven native Bitmap path if this GFx build exposes no BitmapData.
                    if(bitmap)sharedAtlas=bitmap.bitmapData;
                }
                if(!bitmap || bitmap.width<2048 || bitmap.height<720)throw new Error("Native atlas missing or invalid extent");
                var result:Sprite=new Sprite();
                result.mouseEnabled=false;result.mouseChildren=false;
                result.scrollRect=new Rectangle(0,0,128,180);
                bitmap.x=-(slot%16)*128;bitmap.y=-int(slot/16)*180;
                bitmap.smoothing=true;result.addChild(bitmap);
                result.scaleX=w/128;result.scaleY=h/180;
                if(!seen.hasOwnProperty(id)){seen[id]=true;successes++;}
                return result;
            } catch(error:Error) {
                if(!seen.hasOwnProperty(id))failures++;
                seen[id]=false;lastError=id+": "+error.toString();return null;
            }
        }
        private static var IDS:Array=[-1,-2,-3,-4,-5,-6,-7,-8,-101,-102,-103,-104,-105,-106,-107,-108,-201,-202,-203,-210,-211,-212,-213,-214,-215,-216,-217,-218,-219,-220,-221,-222,-223,-224,-225,-226,-227,-228,-229,-230,-231,-232,-233,-234,-235,-236,-237,-238,-239,-240,-241,-242,-243,-250,-251,-252,-253];
        public static function release():void
        { BetaGwentHDArt.release();seen={};successes=0;failures=0;lastError=""; }
    }
}
