package {
    import flash.display.GradientType;
    import flash.display.Shape;
    import flash.display.Sprite;
    import flash.geom.ColorTransform;
    import flash.geom.Matrix;
    // Beta pass hold on the turn coin (level8 CoinRoot, GwentUnity.CoinVisualsControl).
    // SetPercentage(hold): fill=m_FillProgressCurve(hold); the effect root turns
    // 355*fill about the coin axis, so its emitters travel clockwise from 12 o'clock
    // on a 55 px circle; Mist and Sparks simulate in world space (they stay behind
    // as a trail), the Flare in local space (it rides the head). The coin material's
    // _Blend=fill sweeps the CoinMask angular ring band. CoinShake uses
    // m_CoinShakeCurve(hold) with 0.5 unit / 15 degree offsets. EndGlow bursts once at
    // hold>=0.97. Hover: PassCoinOver (rollover ring), MistEdge and
    // SideFragmentEmitter on their circle arcs. Emitter numbers are the source
    // ParticleSystem modules; the source textures are drawn as gradients (the
    // native atlas has no free room for them) and the custom coin shader as a ring.
    public class BetaGwentPassCoin096 extends Sprite {
        private static const K:Number=5.75;          // px per source unit at the coin
        private static const HK:Number=6.2;          // px per unit on the hover canvas
        private static const HEAD_R:Number=55;
        private static const RING_IN:Number=47,RING_OUT:Number=65;
        private static const FILL:Array=[[0,0,1,1.5384616],[0.65,1,1.5384616,0.0000027],[1,1.000001,0.0000027,0]];
        private static const SHAKE:Array=[[0,0,1,0],[0.615,0,0,6.3271475],[0.7703474,0.982906,0.0650015,0.0650015],[0.9231707,0.9842594,-0.0016142,-0.0016142],[0.9956108,0.3376071,-7.0101986,-7.0101986]];
        private var ring:Shape=new Shape();
        private var hover:Sprite=new Sprite(),hoverRing:Shape=new Shape();
        private var layer:Sprite=new Sprite();
        private var parts:Array=[];
        private var free:Object={};
        private var acc:Object={mist:0,sparks:0,flare:0,edge:0,frag:0};
        private var last:int=0;
        private var fill:Number=0;
        private var emitting:Boolean=false,endPlayed:Boolean=false;
        private var hoverAlpha:Number=0,hoverWarm:Boolean=false;
        public var baseX:Number=0,baseY:Number=0;
        public var shakeX:Number=0,shakeY:Number=0,shakeScale:Number=1;
        public function BetaGwentPassCoin096() {
            mouseEnabled=false;mouseChildren=false;
            addChild(hover);hover.addChild(hoverRing);addChild(ring);addChild(layer);
            ring.blendMode="add";hoverRing.blendMode="add";hover.alpha=0;
            // placeholder_coin_rolloverFX: a soft blue halo just outside the rim.
            var m:Matrix=new Matrix();m.createGradientBox(230,230,0,-115,-115);
            hoverRing.graphics.beginGradientFill(GradientType.RADIAL,[0x48C8F3,0x48C8F3,0x2FA0F0,0x2FA0F0],[0,0.55,0.25,0],[130,160,200,255],m);
            hoverRing.graphics.drawCircle(0,0,115);hoverRing.graphics.endFill();
        }
        public static function curve(keys:Array,t:Number):Number {
            if(t<=keys[0][0])return keys[0][1];
            for(var i:int=1;i<keys.length;i++)if(t<=keys[i][0]){
                var a:Array=keys[i-1],b:Array=keys[i],dt:Number=b[0]-a[0],s:Number=(t-a[0])/dt,s2:Number=s*s,s3:Number=s2*s;
                return (2*s3-3*s2+1)*a[1]+(s3-2*s2+s)*a[3]*dt+(-2*s3+3*s2)*b[1]+(s3-s2)*b[2]*dt;
            }
            return keys[keys.length-1][1];
        }
        private static function lerpKeys(keys:Array,t:Number):Number {
            if(t<=keys[0][0])return keys[0][1];
            for(var i:int=1;i<keys.length;i++)if(t<=keys[i][0]){var a:Array=keys[i-1],b:Array=keys[i];return a[1]+(b[1]-a[1])*(t-a[0])/Math.max(.0001,b[0]-a[0]);}
            return keys[keys.length-1][1];
        }
        private static function rand(a:Number,b:Number):Number {return a+(b-a)*Math.random();}
        private function shape(kind:String):Shape {
            var list:Array=free[kind];if(list&&list.length){var reused:Shape=list.pop();reused.visible=true;return reused;}
            var s:Shape=new Shape();s.blendMode="add";var m:Matrix=new Matrix();m.createGradientBox(100,100,0,-50,-50);
            if(kind=="flare"){
                // temp_Flare: tight core with a long horizontal streak.
                s.graphics.beginGradientFill(GradientType.RADIAL,[0xFFFFFF,0x8FD4FF,0x2F8CFF],[1,.55,0],[0,40,255],m);s.graphics.drawCircle(0,0,14);s.graphics.endFill();
                m.createGradientBox(100,10,0,-50,-5);
                s.graphics.beginGradientFill(GradientType.RADIAL,[0xDDF2FF,0x3A9CFF],[.9,0],[0,255],m);s.graphics.drawEllipse(-50,-5,100,10);s.graphics.endFill();
            }else if(kind=="mist"||kind=="edge"){
                s.graphics.beginGradientFill(GradientType.RADIAL,[0xFFFFFF,0xFFFFFF,0xFFFFFF],[.85,.35,0],[0,120,255],m);s.graphics.drawCircle(0,0,50);s.graphics.endFill();
            }else if(kind=="frag"){
                s.graphics.beginFill(0xFFFFFF,.9);s.graphics.moveTo(0,-50);s.graphics.lineTo(28,18);s.graphics.lineTo(-22,34);s.graphics.lineTo(0,-50);s.graphics.endFill();
            }else{
                s.graphics.beginGradientFill(GradientType.RADIAL,[0xFFFFFF,0xFFFFFF],[1,0],[0,255],m);s.graphics.drawCircle(0,0,50);s.graphics.endFill();
            }
            return s;
        }
        private function spawn(kind:String,parent:Sprite,x:Number,y:Number,o:Object):void {
            var s:Shape=shape(kind);parent.addChild(s);
            o.kind=kind;o.sprite=s;o.x=x;o.y=y;o.age=0;if(o.vx==null)o.vx=0;if(o.vy==null)o.vy=0;if(o.spin==null)o.spin=0;
            o.parent=parent;parts.push(o);
        }
        private function headX():Number {return Math.sin(Math.PI/180*355*fill)*HEAD_R;}
        private function headY():Number {return -Math.cos(Math.PI/180*355*fill)*HEAD_R;}
        private function disc(r:Number):Array {var a:Number=Math.random()*Math.PI*2,d:Number=Math.sqrt(Math.random())*r;return [Math.cos(a)*d,Math.sin(a)*d];}
        // Hover emitters on the PassCoinOver canvas (Circle shape, arc from +X counter-clockwise).
        private function hoverEmit(kind:String):void {
            var arc:Number=kind=="edge"?129.3:108,tilt:Number=kind=="edge"?-18.4:0,r:Number=(kind=="edge"?12.4:11.64)*HK;
            var a:Number=(rand(0,arc)+tilt)*Math.PI/180,x:Number=Math.cos(a)*r,y:Number=-Math.sin(a)*r;
            if(kind=="edge")spawn("edge",hover,x,y,{life:rand(1.3,2.5),size:rand(2.7,9)*1.5*HK,rot:rand(-360,360),spin:rand(-45,45),rgb:[0.043,0.6,1],a:0.31});
            else{var out:Number=0.8*HK;spawn("frag",hover,x,y,{life:rand(1,2.3),size:rand(1.4,2.3)*HK,rot:rand(-360,360),vx:Math.cos(a)*out,vy:-Math.sin(a)*out,wobble:rand(0,6.28),rgb:[0,0.463,1],a:1});}
        }
        // hold: 0..1 while the pass is being held, <0 otherwise.
        public function update(now:int,hold:Number,hovering:Boolean,reduced:Boolean):void {
            var dt:Number=last>0?Math.min(.1,(now-last)/1000):0;last=now;
            // Hover highlight (CoinHighlight) fades with the rollover.
            var hoverTarget:Number=hovering||hold>=0?1:0;
            hoverAlpha=hoverTarget>hoverAlpha?Math.min(1,hoverAlpha+dt*7):Math.max(0,hoverAlpha-dt*5);hover.alpha=hoverAlpha;hover.visible=hoverAlpha>0;
            if(hoverAlpha>0&&!reduced){
                if(!hoverWarm){hoverWarm=true;for(var w:int=0;w<20;w++){hoverEmit("edge");parts[parts.length-1].age=rand(0,1.2);}
                    for(w=0;w<5;w++){hoverEmit("frag");parts[parts.length-1].age=rand(0,1);}}
                acc.edge+=dt*30;while(acc.edge>=1){acc.edge--;hoverEmit("edge");}
                acc.frag+=dt*10;while(acc.frag>=1){acc.frag--;hoverEmit("frag");}
            }else if(hoverAlpha<=0)hoverWarm=false;
            // SetPercentage
            fill=hold>=0?curve(FILL,Math.min(1,hold)):0;
            var on:Boolean=hold>=0&&fill>0.01;
            if(!on&&emitting){emitting=false;
                for(var i:int=parts.length-1;i>=0;i--)if(parts[i].kind=="mist"||parts[i].kind=="sparks"||parts[i].kind=="flare")retire(i);}
            if(on)emitting=true;
            if(hold<0)endPlayed=false;
            var shake:Number=hold>=0?curve(SHAKE,Math.min(1,hold)):0;
            if(shake>0.1&&!reduced){shakeX=shake*rand(-.5,.5)*K;shakeY=shake*rand(-.5,.5)*K;shakeScale=Math.cos(shake*rand(-15,15)*Math.PI/180);}
            else{shakeX=0;shakeY=0;shakeScale=1;}
            x=baseX+shakeX;y=baseY+shakeY;
            drawRing();
            if(on&&!reduced){
                var hx:Number=headX(),hy:Number=headY(),p:Array;
                acc.mist+=dt*50;while(acc.mist>=1){acc.mist--;p=disc(1.5*K);spawn("mist",layer,hx+p[0],hy+p[1],{life:rand(.15,.4),size:rand(8,14)*K,rot:rand(-180,180),spin:rand(-110,110),rgb:[.212,.675,1],a:.573});}
                acc.sparks+=dt*100;while(acc.sparks>=1){acc.sparks--;p=disc(1.5*K);spawn("sparks",layer,hx+p[0],hy+p[1],{life:rand(.1,.28),size:rand(.6,1)*K,rot:0,vx:rand(-6,6)*K,vy:rand(-6,6)*K,rgb:[1,1,1],a:1});}
                acc.flare+=dt*8;while(acc.flare>=1){acc.flare--;spawn("flare",layer,hx,hy,{life:.11,size:30*K,rot:rand(-60,-40),rgb:[.55,.8,1],a:1,local:true});}
            }
            if(hold>=0.97&&!endPlayed){endPlayed=true;
                for(var g:int=0;g<3;g++)spawn("glow",layer,0,0,{life:.18,size:45*K,rot:0,rgb:[.092,.499,.838],a:1,end:true});}
            for(i=parts.length-1;i>=0;i--){
                var q:Object=parts[i];q.age+=dt;var t:Number=q.age/q.life;
                if(t>=1){retire(i);continue;}
                if(q.local){q.x=headX();q.y=headY();}
                else{
                    if(q.kind=="frag"){var wob:Number=Math.sin(q.wobble+t*12.6);q.x+=(q.vx+wob*7.2*HK*.15)*dt;q.y+=(q.vy+wob*5*HK*.15)*dt;}
                    else{q.x+=q.vx*dt;q.y+=q.vy*dt;}
                }
                q.rot+=q.spin*dt;
                var size:Number,alpha:Number,bright:Number=1;
                if(q.kind=="mist"){size=q.size*lerpKeys([[0,.341],[1,.023]],t);alpha=lerpKeys([[0,0],[.15,.596],[.374,.561],[1,0]],t)*q.a*1.8;}
                else if(q.kind=="sparks"){size=q.size*lerpKeys([[0,.827],[1,.187]],t);alpha=lerpKeys([[0,0],[.106,1],[.235,0],[.362,1],[.562,0],[.762,1],[1,0]],t);bright=6;}
                else if(q.kind=="flare"){size=q.size*lerpKeys([[0,0],[.694,1],[1,.738]],t);alpha=lerpKeys([[0,0],[.535,1],[1,0]],t);bright=1.6;}
                else if(q.kind=="glow"){size=q.size*lerpKeys([[0,0],[.077,1],[1,.758]],t);alpha=lerpKeys([[0,0],[.203,1],[.526,.948],[1,0]],t);bright=2.2;}
                else if(q.kind=="edge"){size=q.size*1.5*lerpKeys([[0,1],[.924,.364],[.934,0]],t)/1.5;var grey:Number=lerpKeys([[0,0],[.197,1],[.441,1],[.835,0]],t);alpha=q.a*grey*lerpKeys([[0,1],[.326,1],[.747,0]],t)*1.5;}
                else{size=q.size*lerpKeys([[0,1],[1,.241]],t);alpha=lerpKeys([[0,0],[.071,1],[.706,1],[1,0]],t);bright=2.5;}
                var s:Shape=q.sprite;s.x=q.x;s.y=q.y;s.rotation=q.rot;s.scaleX=s.scaleY=Math.max(.001,size/100);
                var k:Number=Math.min(4,alpha*bright);
                s.transform.colorTransform=new ColorTransform(q.rgb[0]*k,q.rgb[1]*k,q.rgb[2]*k,Math.min(1,alpha));
            }
        }
        private function retire(i:int):void {
            var q:Object=parts[i];parts.splice(i,1);q.sprite.visible=false;if(q.sprite.parent)q.sprite.parent.removeChild(q.sprite);
            var list:Array=free[q.kind];if(!list){list=[];free[q.kind]=list;}if(list.length<64)list.push(q.sprite);
        }
        // TurnCoinShader _Blend: CoinMask R is an angular gradient over the rim band
        // (r 0.7..1.0), 255 at 12 o'clock falling clockwise; fill lights it up to
        // 360*fill degrees.
        private function drawRing():void {
            ring.graphics.clear();if(fill<=0.01)return;
            var end:Number=Math.min(360,360*fill),steps:int=Math.max(2,int(end/4));
            ring.graphics.beginFill(0x2E8FE8,.5);
            var i:int,a:Number;
            for(i=0;i<=steps;i++){a=(end*i/steps-90)*Math.PI/180;var px:Number=Math.cos(a)*RING_OUT,py:Number=Math.sin(a)*RING_OUT;if(i==0)ring.graphics.moveTo(px,py);else ring.graphics.lineTo(px,py);}
            for(i=steps;i>=0;i--){a=(end*i/steps-90)*Math.PI/180;ring.graphics.lineTo(Math.cos(a)*RING_IN,Math.sin(a)*RING_IN);}
            ring.graphics.endFill();
            ring.graphics.lineStyle(2,0x9FDCFF,.85);
            for(i=0;i<=steps;i++){a=(end*i/steps-90)*Math.PI/180;if(i==0)ring.graphics.moveTo(Math.cos(a)*RING_OUT,Math.sin(a)*RING_OUT);else ring.graphics.lineTo(Math.cos(a)*RING_OUT,Math.sin(a)*RING_OUT);}
        }
    }
}
