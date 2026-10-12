package {
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.Matrix;
    [SWF(width="192",height="234",frameRate="30",backgroundColor="#000000")]
    public class BetaLeaderMovie extends Sprite {
        [Embed(source="atlas.png",compression="true",quality="90")] private static var Atlas:Class;
        private var pixels:BitmapData=(new Atlas() as Bitmap).bitmapData;
        private var previous:int=-1;
        private var matrix:Matrix=new Matrix();
        public function BetaLeaderMovie(){mouseEnabled=false;mouseChildren=false;renderAt(0);}
        // The owning menu supplies its clock. Loading/reparenting never resets it.
        public function renderAt(frame:int):void {
            if(!pixels)return;
            frame=frame%24;if(frame==previous)return;previous=frame;
            matrix.identity();matrix.translate(-(frame%6)*192,-int(frame/6)*234);
            graphics.clear();graphics.beginBitmapFill(pixels,matrix,false,true);
            graphics.drawRect(0,0,192,234);graphics.endFill();
        }
        // Atlas is an engine-owned CSwfTexture. BitmapData.dispose incorrectly
        // enters Scaleform DICommand_Dispose for this native image and crashes.
        // Clear AS references; the Loader owns the resource lifetime.
        public function release():void {graphics.clear();pixels=null;previous=-1;}
    }
}
