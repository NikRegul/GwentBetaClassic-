package {
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.Rectangle;
    // Alzur's Thunder, rebuilt from the Beta prefabs PowerLightningProjectile
    // (glow orb + lighting3 crackle + jagged core trail + sparks) and
    // PowerDirectLightning (glow, flare, Electric_2x2 shockwave, sparks, smoke).
    // Additive Unity textures are pre-converted to straight alpha and pre-tinted.
    public class BetaGwentLightning144 {
        private static var shared:BitmapData;
        [Embed(source="../assets/special144/lightning_beta.png",compression="true",quality="100")] private static var Atlas:Class;
        public static const BOLT:int=0,SHOCK:int=1,SPARK:int=2,RIM:int=3,CORE:int=4,FLARE:int=5,SMOKE:int=6;
        // Centered cell of the atlas scaled to w*h.
        public static function cell(kind:int,index:int,w:Number,h:Number):Sprite {
            var nativeFrame:int=Math.max(0,index)%4;
            var nativeView:Sprite=BetaGwentClassicEffects.view("lightning:"+kind+":"+nativeFrame,w,h);
            if(nativeView){
                nativeView.x=-w/2;nativeView.y=-h/2;
                var nativeHolder:Sprite=new Sprite();nativeHolder.mouseEnabled=false;nativeHolder.mouseChildren=false;
                nativeHolder.addChild(nativeView);return nativeHolder;
            }
            var bitmap:Bitmap=shared?new Bitmap(shared):new Atlas() as Bitmap;if(!bitmap)return null;if(!shared)shared=bitmap.bitmapData;bitmap.smoothing=true;
            var x:int=0,y:int=0,cw:int=128,ch:int=128;index=Math.max(0,index)%4;
            if(kind==BOLT){x=index*128;y=0;cw=128;ch=256;}
            else if(kind==SHOCK){x=index*128;y=256;cw=128;ch=64;}
            else if(kind==SPARK){x=index*64;y=320;cw=64;ch=64;}
            else if(kind==RIM){x=256;y=320;}
            else if(kind==CORE){x=384;y=320;}
            else if(kind==FLARE){x=0;y=384;}
            else {x=128;y=384;}
            bitmap.x=-x;bitmap.y=-y;
            var clip:Sprite=new Sprite();clip.mouseEnabled=false;clip.mouseChildren=false;
            clip.scrollRect=new Rectangle(0,0,cw,ch);clip.addChild(bitmap);
            clip.scaleX=w/cw;clip.scaleY=h/ch;clip.x=-w/2;clip.y=-h/2;
            var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;holder.addChild(clip);
            return holder;
        }
    }
}
