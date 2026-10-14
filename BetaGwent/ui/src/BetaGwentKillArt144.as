package {
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.ColorTransform;
    import flash.geom.Rectangle;
    import flash.geom.Matrix;
    // Beta textures for DestroyDestroyFire, DestroyDestroyPoison and IgniIgnition
    // (8x4 cells of 128 px). White cells are tinted at runtime.
    public class BetaGwentKillArt144 {
        private static var shared:BitmapData;
        [Embed(source="../assets/special144/kill_beta.png",compression="true",quality="100")] private static var Atlas:Class;
        // Second sheet (indices 32+): DestroyDestroyBlood, [201525]PowerBoardPhysical (Yrden), ResetPhysicalBuff.
        [Embed(source="../assets/special144/kill2_beta.png",compression="true",quality="100")] private static var Atlas2:Class;
        private static var shared2:BitmapData;
        public static const GLOW:int=0,SOFT_GLOW:int=1,MAGIC_SMOKE:int=2,IGNI_SIGN:int=3,SOFT_SMOKE:int=4,DUST:int=5,RING:int=6,SPLASH:int=7,
            ASH:int=8,BUBBLE:int=12,WHITE_SMOKE:int=16,SAND:int=20,BLUR_SPARK:int=22,SPARK:int=23,FLAME:int=24,
            YRDEN_SIGN:int=32,YRDEN_CIRCLE:int=33,YRDEN_TRIANGLE:int=34,YRDEN_LINE:int=35,VIGNETTE:int=36,WAVE_RECT:int=37,LIGHT_SHAFT:int=38,SOFT_DOT:int=39,
            BLOOD_SPARK:int=40,BLOOD_SPLAT:int=44,BLOOD_BORDER:int=45;
        // Cells whose Beta material is additive (Glow01_Alpha, basicSoftGlow, IgniSign,
        // BurningDust embers, Additive(Soft) sand, BlurredSpark, Flames, Yrden sign/
        // circle/triangle/line, VignetteMask, light shaft, round faint glow).
        // Shared textures used by both kinds (SPARK, MAGIC_SMOKE) are chosen per call.
        private static const ADDITIVE:Object={0:1,1:1,3:1,8:1,9:1,10:1,11:1,20:1,21:1,22:1,24:1,25:1,26:1,27:1,28:1,29:1,30:1,31:1,32:1,33:1,34:1,35:1,36:1,38:1,39:1};
        public static function additive(index:int):Boolean {return ADDITIVE.hasOwnProperty(String(index));}
        public static function cell(index:int,w:Number,h:Number,tint:int=-1,alpha:Number=1,light:int=-1):Sprite {
            var add:Boolean=light<0?additive(index):light>0;
            var bitmap:Bitmap;
            if(index>=32){index-=32;bitmap=shared2?new Bitmap(shared2):new Atlas2() as Bitmap;if(!bitmap)return null;if(!shared2)shared2=bitmap.bitmapData;}
            else {bitmap=shared?new Bitmap(shared):new Atlas() as Bitmap;if(!bitmap)return null;if(!shared)shared=bitmap.bitmapData;}
            bitmap.smoothing=true;
            var clip:Sprite=new Sprite();clip.mouseEnabled=false;clip.mouseChildren=false;
            // Submit only this quad. Nested scrollRect on a rotated/scaled atlas
            // leaks the entire sheet in the game's GFx renderer.
            var sx:Number=w/127,sy:Number=h/127;
            clip.graphics.beginBitmapFill(bitmap.bitmapData,new Matrix(sx,0,0,sy,-((index%8)*128+.5)*sx,-(int(index/8)*128+.5)*sy),false,true);
            clip.graphics.drawRect(0,0,w,h);clip.graphics.endFill();clip.x=-w/2;clip.y=-h/2;
            var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;holder.addChild(clip);
            if(tint>=0)holder.transform.colorTransform=new ColorTransform(((tint>>16)&255)/255,((tint>>8)&255)/255,(tint&255)/255,alpha);
            else if(alpha<1)holder.alpha=alpha;
            if(add)holder.blendMode="add";
            return holder;
        }
    }
}
