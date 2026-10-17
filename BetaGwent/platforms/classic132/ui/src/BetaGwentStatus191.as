package {
    import flash.display.Sprite;
    // Original Beta show/hide curves projected onto the existing HUD layout.
    public class BetaGwentStatus191 extends Sprite {
        private var clip:Object;
        private var parts:Array=[];
        private var unit:Number;
        private var hiding:Boolean;
        public var durationMs:Number;
        public function BetaGwentStatus191(name:String,phase:String,width:Number) {
            mouseEnabled=false;mouseChildren=false;unit=width/22;hiding=phase=="hide";
            clip=BetaGwentStatusData191.clip(name,phase);durationMs=clip?clip.ms:0;
        }
        public function addPart(sprite:Sprite,key:String,x:Number,y:Number):void {
            addChild(sprite);parts.push({sprite:sprite,key:key,x:x,y:y});sprite.x=x;sprite.y=y;
        }
        public static function sample(values:Array,p:Number):Number {
            var at:Number=Math.max(0,Math.min(1,p))*(values.length-1);
            var a:int=int(at),b:int=Math.min(values.length-1,a+1);
            return values[a]+(values[b]-values[a])*(at-a);
        }
        public function render(progress:Number):void {
            if(!clip)return;
            for each(var part:Object in parts){
                var data:Object=clip.parts[part.key];if(!data)continue;
                var sprite:Sprite=part.sprite;
                sprite.scaleX=Math.max(0,sample(data.sx,progress));sprite.scaleY=Math.max(0,sample(data.sy,progress));
                sprite.x=part.x+sample(data.dx,progress)*unit;sprite.y=part.y-sample(data.dy,progress)*unit;
                sprite.alpha=Math.max(0,Math.min(1,sample(data.alpha,progress)));
                if(hiding&&progress>=1)sprite.visible=false;
            }
        }
    }
}
