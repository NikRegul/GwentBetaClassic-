package {
    import flash.display.Bitmap;
    import flash.display.Sprite;
    [SWF(width="192",height="234",frameRate="30",backgroundColor="#000000")]
    public class BetaLeaderMovie extends Sprite {
        [Embed(source="atlas.png",compression="true",quality="90")] private static var Atlas:Class;
        // Retain the original atlas binding; each frame is a native subimage.
        private var atlasLink:Class;
        private static var frames:Array=[FRAME_CLASSES];
        private var previous:int=-1;
        private var shown:Bitmap;
        public function BetaLeaderMovie(){atlasLink=Atlas;previous=-1;mouseEnabled=false;mouseChildren=false;renderAt(0);}
        public function renderAt(frame:int):void {
            frame=((frame%24)+24)%24;if(frame==previous)return;
            var type:Class=frames[frame] as Class;var image:Bitmap=new type() as Bitmap;
            if(!image||image.width<=0||image.height<=0)return;
            image.smoothing=true;image.pixelSnapping="never";
            if(shown&&shown.parent==this)removeChild(shown);
            shown=image;addChild(shown);previous=frame;
        }
        public function release():void {
            if(shown&&shown.parent==this)removeChild(shown);shown=null;previous=-1;atlasLink=null;
        }
    }
}
