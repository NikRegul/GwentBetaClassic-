package {
    import flash.display.Bitmap;
    import flash.display.Sprite;
    import flash.geom.Rectangle;
    public class BetaGwentSpellArt143 {
        [Embed(source="../assets/special143/fire.png",compression="true",quality="100")] private static var Fire:Class;
        [Embed(source="../assets/special143/frame.png",compression="true",quality="100")] private static var Frame:Class;
        [Embed(source="../assets/special143/lightning.png",compression="true",quality="100")] private static var Lightning:Class;
        [Embed(source="../assets/special143/sparks.png",compression="true",quality="100")] private static var Sparks:Class;
        public static function clip(name:String,w:Number,h:Number,frame:int=0):Sprite {
            var nativeFrame:int=0;
            if(name=="fire")nativeFrame=Math.max(0,Math.min(24,frame));
            else if(name=="sparks")nativeFrame=frame%4;
            var nativeView:Sprite=BetaGwentClassicEffects.view("spell:"+name+":"+nativeFrame,w,h);
            if(nativeView)return nativeView;
            var type:Class=name=="fire"?Fire:name=="frame"?Frame:name=="lightning"?Lightning:Sparks;
            var bitmap:Bitmap=new type() as Bitmap;if(!bitmap)return null;
            var sprite:Sprite=new Sprite();sprite.mouseEnabled=false;sprite.mouseChildren=false;
            bitmap.smoothing=true;
            var sw:Number=bitmap.width,sh:Number=bitmap.height;
            if(name=="fire"){
                frame=Math.max(0,Math.min(24,frame));sw=96;sh=128;
                bitmap.x=-(frame%5)*100-2;bitmap.y=-int(frame/5)*132-2;
            }else if(name=="sparks"){
                frame=frame%4;sw=128;sh=128;bitmap.x=-(frame%2)*128;bitmap.y=-int(frame/2)*128;
            }
            sprite.scrollRect=new Rectangle(0,0,sw,sh);sprite.addChild(bitmap);
            sprite.scaleX=w/sw;sprite.scaleY=h/sh;return sprite;
        }
    }
}
