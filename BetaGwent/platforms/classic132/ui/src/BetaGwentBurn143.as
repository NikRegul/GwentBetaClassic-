package {
    import flash.display.Shape;
    import flash.display.Sprite;
    import flash.filters.GlowFilter;
    import flash.geom.ColorTransform;
    // GFx replacement for the beta's material dissolve: the card burns in place.
    public class BetaGwentBurn143 extends Sprite {
        private var face:Sprite;
        private var cut:Shape=new Shape();
        private var edge:Shape=new Shape();
        private var flames:Sprite=new Sprite();
        private var frame:Sprite;
        private var frames:Array=[];
        private var w:Number,h:Number;
        public function BetaGwentBurn143(card:Sprite,width:Number,height:Number,brightness:Number) {
            mouseEnabled=false;mouseChildren=false;w=width;h=height;face=card;
            addChild(face);addChild(cut);face.mask=cut;
            frame=BetaGwentSpellArt143.clip("frame",w,h);addChild(frame);
            frame.transform.colorTransform=new ColorTransform(1,.38,.05,1,0,0,0,0);
            frame.alpha=brightness;frame.filters=[new GlowFilter(0xFF6A0A,.7,8,8,1,1)];
            addChild(edge);edge.alpha=brightness;
            addChild(flames);flames.alpha=brightness;
            for(var i:int=0;i<25;i++){
                var f:Sprite=BetaGwentSpellArt143.clip("fire",w*1.5,h*1.15,i);
                f.x=-w*.25;f.y=-h*.85;flames.addChild(f);frames.push(f);
            }
            render(0);
        }
        public function render(progress:Number):void {
            progress=Math.max(0,Math.min(1,progress));
            var burn:Number=Math.max(0,Math.min(1,(progress-.08)/.82));
            cut.graphics.clear();edge.graphics.clear();
            var strips:int=18;
            cut.graphics.beginFill(0xFFFFFF);
            for(var i:int=0;i<strips;i++){
                var x:Number=i*w/strips;
                var noise:Number=Math.sin(i*2.17)*h*.07+Math.cos(i*4.71)*h*.04;
                var y:Number=burn>=1?0:Math.max(0,Math.min(h,h*(1-burn)+noise*Math.sin(burn*Math.PI)));
                cut.graphics.drawRect(x,0,w/strips+1,y);
                if(burn>0&&burn<1){edge.graphics.beginFill(i%3==0?0xFFE188:0xF85A0A,.9);edge.graphics.drawRect(x,Math.max(0,y-3),w/strips+1,3);edge.graphics.endFill();}
            }
            cut.graphics.endFill();
            face.transform.colorTransform=new ColorTransform(1-burn*.72,1-burn*.87,1-burn*.94,1,0,0,0,0);
            frame.alpha=flames.alpha*Math.max(0,1-progress*1.4);
            flames.y=h*(1-burn);flames.visible=progress<.97;
            var cell:int=Math.min(24,int(progress*25));
            for(i=0;i<frames.length;i++)frames[i].visible=i==cell;
        }
    }
}
