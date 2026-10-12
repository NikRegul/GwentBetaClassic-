package
{
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.geom.Matrix;
    import flash.utils.getTimer;

    // Prototype for the isolated 0.6.0 builder. Not a 0.5.4 menu source.
    [SWF(width="256",height="312",frameRate="30",backgroundColor="#000000")]
    public class BetaLeaderMovie extends Sprite
    {
        [Embed(source="atlas.png",compression="true",quality="90")]
        private static var Atlas:Class;
        private const FRAME_COUNT:int=40;
        private var pixels:BitmapData=(new Atlas() as Bitmap).bitmapData;
        
        private var previous:int=-1;
        private var matrix:Matrix=new Matrix();

        public function BetaLeaderMovie()
        {
            mouseEnabled=false;mouseChildren=false;
            addEventListener(Event.ENTER_FRAME,tick);
            addEventListener(Event.REMOVED_FROM_STAGE,removed);
            tick(null);
        }

        private function tick(e:Event):void
        {
            var frame:int=int(getTimer()*.012)%FRAME_COUNT;
            if(frame==previous)return;
            previous=frame;
            matrix.identity();matrix.translate(-(frame%8)*256,-int(frame/8)*312);
            graphics.clear();graphics.beginBitmapFill(pixels,matrix,false,true);
            graphics.drawRect(0,0,256,312);graphics.endFill();
        }

        private function removed(e:Event):void
        {
            removeEventListener(Event.ENTER_FRAME,tick);
            removeEventListener(Event.REMOVED_FROM_STAGE,removed);
            graphics.clear();pixels.dispose();
        }
    }
}
