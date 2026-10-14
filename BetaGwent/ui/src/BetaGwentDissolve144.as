package {
    import flash.display.Shape;
    import flash.display.Sprite;
    // GFx replacement for the Beta card dissolve shader: the face is clipped by
    // the original dissolve noise (vector mask, no BitmapData) and the band
    // next to the cut is painted with the material's _DissolveRamp colours.
    public class BetaGwentDissolve144 extends Sprite {
        public static const FIRE:int=1,POISON:int=2,BLOOD:int=3,BANISH:int=4;
        private static var cache:Object={};
        private var face:Sprite;private var cut:Shape=new Shape();private var edge:Shape=new Shape();
        private var w:Number,h:Number,noise:Array,band:Number,ramp:Array,alphas:Array;
        public function BetaGwentDissolve144(card:Sprite,width:Number,height:Number,kind:int) {
            mouseEnabled=false;mouseChildren=false;w=width;h=height;face=card;
            addChild(face);addChild(cut);face.mask=cut;addChild(edge);
            noise=values(kind);
            // Banish_Small_Material: violet EpicHighlightGradient edge, white-hot centre.
            if(kind==BANISH){band=.15;ramp=BetaGwentDissolveData144.BANISH_RAMP;alphas=[1,1,1,.95,.8,.5];}
            else if(kind==BLOOD){band=.12;ramp=[0x140202,0x6A0C0C,0xC23030,0xF2DADA,0xE4B4B4,0x7A1414];alphas=[1,1,1,1,.85,.5];}
            else if(kind==POISON){band=.2;ramp=[0x020802,0x0B5A06,0x2FD00E,0x86E012,0x63CC21,0x126A0A];alphas=[1,1,1,.95,.75,.45];}
            else {band=.15;ramp=[0x140402,0x7A0E06,0xF0281A,0xFF5A1E,0xFF8A2E,0xFFB86A];alphas=[1,1,1,1,.85,.5];}
            render(0);
        }
        private static function values(kind:int):Array {
            if(cache[kind])return cache[kind];
            var s:String=kind==BANISH?BetaGwentDissolveData144.BANISH:kind==BLOOD?BetaGwentDissolveData144.BLOOD:kind==POISON?BetaGwentDissolveData144.POISON:BetaGwentDissolveData144.FIRE;
            var out:Array=[];for(var i:int=0;i<s.length;i+=2)out.push(parseInt(s.substr(i,2),16)/254);
            cache[kind]=out;return out;
        }
        public function render(progress:Number):void {
            progress=Math.max(0,Math.min(1,progress));
            var t:Number=progress*(1+band)-band;
            var gw:int=BetaGwentDissolveData144.W,gh:int=BetaGwentDissolveData144.H;
            var cw:Number=w/gw,ch:Number=h/gh;
            cut.graphics.clear();edge.graphics.clear();
            if(progress>=1){face.visible=false;return;}
            cut.graphics.beginFill(0xFFFFFF);
            var buckets:Array=[[],[],[],[],[],[]];
            for(var y:int=0;y<gh;y++){
                var run:int=-1;var bRun:int=-1;var bStart:int=0;
                for(var x:int=0;x<=gw;x++){
                    var v:Number=x<gw?noise[y*gw+x]-t:-1;
                    var on:Boolean=v>0;
                    if(on&&run<0)run=x;
                    // Nonoverlapping contours avoid GFx stencil cancellation.
                    if(!on&&run>=0){cut.graphics.drawRect(run*cw,y*ch,(x-run)*cw,ch);run=-1;}
                    var b:int=on&&v<band?Math.min(5,int(v/band*6)):-1;
                    if(b!=bRun){if(bRun>=0)buckets[bRun].push(bStart,y,x-bStart);bRun=b;bStart=x;}
                }
            }
            cut.graphics.endFill();
            for(var k:int=0;k<6;k++){
                var list:Array=buckets[k];if(list.length==0)continue;
                edge.graphics.beginFill(ramp[k],alphas[k]);
                for(var i:int=0;i<list.length;i+=3)edge.graphics.drawRect(list[i]*cw,list[i+1]*ch,list[i+2]*cw,ch);
                edge.graphics.endFill();
            }
        }
    }
}
