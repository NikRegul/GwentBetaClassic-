package {
    import flash.display.Sprite;
    // Beta deck editor UIDBCardAdd / UIDBCardRemove (gui/prefabs/deckbuilder_base).
    // Frames are baked offline from the source shaders/particles; the ordinary
    // (UI/UIGlow, SrcAlpha/OneMinusSrcAlpha) layer stays under the additive
    // light layer, as in the prefab. 30 Hz over the 1 s pooled lifetime.
    public class BetaGwentEditorFx094 extends Sprite {
        private var adding:Boolean;
        private var unit:Number;
        private var normal:Sprite=new Sprite();
        private var light:Sprite=new Sprite();
        private var cells:Object={};
        private var shown:int=-2;
        public var available:Boolean=true;
        // cardWidth: on-screen width of the Beta card face the effect plays on.
        public function BetaGwentEditorFx094(adding:Boolean,cardWidth:Number) {
            mouseEnabled=false;mouseChildren=false;this.adding=adding;
            unit=cardWidth/BetaGwentEditorFxData094.CARD_X;
            light.blendMode="add";addChild(normal);addChild(light);
            // A menu whose native atlas was not extended has no frames: no effect.
            var probe:Array=BetaGwentEditorFxData094.frame(adding,1);
            for each(var layer:* in probe)if(layer is Array&&!cell(layer))available=false;
            render(0);
        }
        public static function frameIndex(progress:Number):int {
            if(!(progress>=0)||progress>=1)return -1;
            return Math.min(BetaGwentEditorFxData094.FRAMES-1,int(progress*BetaGwentEditorFxData094.FRAMES));
        }
        private function cell(layer:Array):Sprite {
            var key:String=String(layer[0]);if(cells.hasOwnProperty(key))return cells[key];
            var rect:Array=BetaGwentEditorFxData094.RECTS[int(layer[0])],sprite:Sprite=null;
            if(rect)sprite=BetaGwentElementArt164.region(int(layer[0]),rect,rect[2]/BetaGwentEditorFxData094.TEXELS*unit,rect[3]/BetaGwentEditorFxData094.TEXELS*unit);
            if(sprite){sprite.mouseEnabled=false;sprite.mouseChildren=false;sprite.visible=false;}
            cells[key]=sprite;return sprite;
        }
        private function place(parent:Sprite,layer:*):void {
            if(!(layer is Array))return;
            var sprite:Sprite=cell(layer as Array);if(!sprite)return;
            var rect:Array=BetaGwentEditorFxData094.RECTS[int(layer[0])];
            // region() is centred on its quad; layer offsets are the quad's top-left.
            sprite.x=(Number(layer[1])+rect[2]/BetaGwentEditorFxData094.TEXELS/2)*unit;
            sprite.y=(Number(layer[2])+rect[3]/BetaGwentEditorFxData094.TEXELS/2)*unit;
            if(sprite.parent!=parent)parent.addChild(sprite);sprite.visible=true;
        }
        public function render(progress:Number):void {
            var index:int=frameIndex(progress);if(index==shown)return;shown=index;
            for(var key:String in cells)if(cells[key])cells[key].visible=false;
            if(index<0||!available)return;
            var pair:Array=BetaGwentEditorFxData094.frame(adding,index);
            place(normal,pair[0]);place(light,pair[1]);
        }
    }
}
