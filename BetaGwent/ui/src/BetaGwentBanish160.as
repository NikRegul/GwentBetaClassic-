package {
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.ColorTransform;
    import flash.geom.Matrix;
    // Gwent 0.9.24 BanishCardEffect particles (tools/ui/build_banish160.py):
    // BanishHit 2x2 (BackLines) and BanishSparks 1 3x3 (EmissionElementMid/Rim).
    // VFX/Common/AlphaBlended = 2 x _TintColor x vertex colour x texture.
    public class BetaGwentBanish160 {
        private static var shared:BitmapData;
        [Embed(source="../assets/special144/banish_beta.png",compression="true",quality="100")] private static var Atlas:Class;
        public static const HIT:int=0,SHARD:int=1;
        // One destination quad per particle (nested scrollRect leaks the sheet in GFx).
        public static function cell(kind:int,index:int,w:Number,h:Number,r:Number,g:Number,b:Number,pivotX:Number=.5):Sprite {
            if(!shared){var bitmap:Bitmap=new Atlas() as Bitmap;if(!bitmap)return null;shared=bitmap.bitmapData;}
            var size:int=kind==HIT?128:64;var x:int,y:int;
            if(kind==HIT){index=Math.max(0,index)%4;x=(index%2)*128;y=int(index/2)*128;}
            else{index=Math.max(0,index)%9;x=(index%3)*64;y=256+int(index/3)*64;}
            var quad:Sprite=new Sprite();quad.mouseEnabled=false;quad.mouseChildren=false;
            var sx:Number=w/(size-1),sy:Number=h/(size-1);
            quad.graphics.beginBitmapFill(shared,new Matrix(sx,0,0,sy,-(x+.5)*sx,-(y+.5)*sy),false,true);
            quad.graphics.drawRect(0,0,w,h);quad.graphics.endFill();quad.x=-w*pivotX;quad.y=-h/2;
            var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;holder.addChild(quad);
            holder.transform.colorTransform=new ColorTransform(r,g,b,1);
            return holder;
        }
    }
}
