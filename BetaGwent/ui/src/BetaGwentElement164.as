package {
    import flash.display.Sprite;
    import flash.geom.ColorTransform;
    import flash.geom.Matrix;
    // Finite source-driven particle simulation. Pure plan/packet methods are
    // also executed by Node for regression and offline previews.
    public class BetaGwentElement164 extends Sprite {
        private var model:Object;
        private var cells:Array=[];
        private var ux:Number,uy:Number;
        private var reduced:Boolean;
        public var durationMs:Number;
        public var particleCount:int;
        public static const MAX_UNITS:Number=55;
        // Boosts are drawn quieter and smaller than hits (user: minimalism).
        private var intensity:Number=1,maxUnits:Number=MAX_UNITS,travelPx:Number=0;
        private var shafts:Array,wash:Sprite;
        public function BetaGwentElement164(name:String,w:Number,h:Number,seed:uint,cap:int=120,flightMs:Number=0,travel:Number=0,small:Boolean=false,strength:Number=1,sizeLimit:Number=55) {
            mouseEnabled=false;mouseChildren=false;reduced=small;intensity=strength;maxUnits=sizeLimit;travelPx=travel;
            var preset:Object=BetaGwentElementData164.preset(name);if(!preset)return;
            ux=preset.method>=2?w/preset.extent[0]:w/22;
            uy=preset.method>=2?h/preset.extent[1]:w/22;
            model=plan(preset,seed,small?4:cap,flightMs/1000,travel/Math.max(.1,ux));
            durationMs=small?220:model.duration*1000;
            for each(var particle:Object in model.particles){
                var cell:Sprite=BetaGwentElementArt164.cell(particle.e.tile[1],1,1);addChild(cell);
                // Stage 174: additive materials are light. Normal blending turned
                // the 2x-tinted glows into opaque white sheets and row-wide bars.
                if(BetaGwentElementBlend173.additive(int(particle.e.id)))cell.blendMode="add";
                cells.push({sprite:cell,particle:particle,packet:{},color:new ColorTransform(),frame:-1});
            }
            particleCount=cells.length;
            if(name=="BoardEffect_ClearWeather")buildShafts(w,h,seed);
            for each(var s:Object in preset.static){
                if(s.name=="LayeredShaft")continue;
                // The Beta footage shows only the two trail heads ("arrow") of a
                // physical shot; the opaque baked tip mesh read as a paper dart.
                if(s.name=="ArrowTipShape")continue;
                var layout:Object=decoration(s,w,ux,uy,preset.projectile,name=="PowerPhysicalProjectile");
                var image:Sprite=BetaGwentElementArt164.cell(s.tile[1],layout.w,layout.h);addChildAt(image,0);
                if(preset.projectile)image.blendMode="add";
                image.rotation=layout.angle;image.x=layout.x;image.y=layout.y;
                image.transform.colorTransform=new ColorTransform(s.rgb[0],s.rgb[1],s.rgb[2],s.alpha);
                cells.push({sprite:image,static:s,trail:s.trail&&preset.projectile,physical:name=="PowerPhysicalProjectile",layout:layout});
            }
            render(0);
        }
        // Beta LightShaft (VFX/Special/ClearWeather/LightShaft) as seen in the Dawn
        // footage: warm golden shafts at about 33 degrees across the whole screen,
        // over the warm additive constantGlow. Vector gradients, additive.
        private function buildShafts(w:Number,h:Number,seed:uint):void {
            var state:Object={seed:seed};shafts=[];
            wash=new Sprite();wash.mouseEnabled=false;wash.blendMode="add";
            wash.graphics.beginFill(0x6E5238,1);wash.graphics.drawRect(-w/2,-h/2,w,h);wash.graphics.endFill();addChildAt(wash,0);
            var angle:Number=33,a:Number=angle*Math.PI/180,length:Number=Math.sqrt(w*w+h*h)*1.15;
            var span:Number=Math.abs(w*Math.sin(a))+Math.abs(h*Math.cos(a));
            for(var i:int=0;i<16;i++){
                var width:Number=30+random(state)*100,offset:Number=(i+random(state)*.8)/16*span-span/2;
                var shaft:Sprite=new Sprite();shaft.mouseEnabled=false;shaft.blendMode="add";
                var m:Matrix=new Matrix();m.createGradientBox(length,width,Math.PI/2,-length/2,-width/2);
                var peak:Number=width<60?0.38:0.26;
                shaft.graphics.beginGradientFill("linear",[0xFFC27A,0xFFD9A0,0xFFC27A],[0,peak,0],[0,128,255],m);
                shaft.graphics.drawRect(-length/2,-width/2,length,width);shaft.graphics.endFill();
                shaft.rotation=angle;var nx:Number=-Math.sin(a),ny:Number=Math.cos(a);
                shaft.x=nx*offset;shaft.y=ny*offset;addChildAt(shaft,1);
                shafts.push({sprite:shaft,x:shaft.x,y:shaft.y,phase:random(state)*6.28,nx:nx,ny:ny,drift:w*.025});
            }
        }
        public function render(progress:Number):void {
            if(!model)return;
            if(shafts){
                var envelope:Number=Math.max(0,Math.min(1,progress/.15,(1-progress)/.35));
                wash.alpha=envelope*.85*intensity;
                for each(var sh:Object in shafts){
                    sh.sprite.alpha=envelope*intensity*(.7+.3*Math.sin(sh.phase+progress*7));
                    sh.sprite.x=sh.x+sh.nx*sh.drift*progress;sh.sprite.y=sh.y+sh.ny*sh.drift*progress;
                }
            }
            var seconds:Number=progress*model.duration;
            for each(var item:Object in cells){
                var sprite:Sprite=item.sprite;
                if(item.static){
                    sprite.alpha=Math.min(1,progress*12,(1-progress)*8)*item.static.alpha*(item.trail&&!item.physical?0.35:1)*intensity;
                    if(item.trail&&item.physical&&travelPx>0){
                        // The shot leaves the centre of its card: the trail grows
                        // with the distance flown instead of trailing behind the source.
                        var full:Number=item.layout.w,grown:Number=Math.max(.02,Math.min(1,progress*travelPx/full));
                        sprite.scaleX=grown;sprite.x=full*.05-full*grown/2;
                    }
                    continue;
                }
                var out:Object=packet(item.particle,reduced?Math.min(model.duration*.4,.32):seconds,item.packet);
                sprite.visible=out.visible&&progress<1;if(!sprite.visible)continue;
                var tile:int=int(item.particle.e.tile[1])+int(out.frame);
                var width:Number=out.w*ux,height:Number=out.h*uy;
                if(reduced){width=Math.min(width,22*ux);height=Math.min(height,22*uy);}
                // Calibrated on Beta footage: a card impact never exceeds about
                // 2.5 card widths (the role of Unity's max particle size). Big
                // glows (GlowBig 150, flash 120 units) otherwise flood the row.
                var limit:Number=maxUnits*ux;var biggest:Number=Math.max(width,height);
                if(!model.preset.projectile&&model.preset.method<2&&biggest>limit){width*=limit/biggest;height*=limit/biggest;}
                // The quad is re-painted only when its UV cell changes; scaling
                // and ColorTransform reuse objects on ordinary animation ticks.
                if(item.frame!=tile){BetaGwentElementArt164.paint(sprite,tile,1,1);item.frame=tile;}
                sprite.x=out.x*ux;sprite.y=out.y*uy;sprite.scaleX=width;sprite.scaleY=height;sprite.rotation=out.angle;
                var color:ColorTransform=item.color;color.redMultiplier=out.r;color.greenMultiplier=out.g;color.blueMultiplier=out.b;
                color.alphaMultiplier=out.a*intensity*(reduced ? 0.45*(1-progress) : 1);sprite.transform.colorTransform=color;
            }
        }
        public static function random(state:Object):Number {
            state.seed=uint(Number(state.seed)*1664525+1013904223);return Number(state.seed)/4294967296;
        }
        public static function decoration(s:Object,w:Number,ux:Number,uy:Number,projectile:Boolean,physical:Boolean):Object {
            // Stage 174: the Beta video shows the original proportions (a chevron
            // about one card wide, a thin trail two to three cards long), so the
            // meshes keep their source size; only placement is projected.
            // Trail textures start at their left edge (Unity TrailRenderer u=0 is
            // the head), so they are turned to lead with the crescent.
            // Spell trails keep the approved thin ribbon (Parasite read as cloth).
            if(projectile&&!physical){
                var tw:Number=s.trail?w*.72:w*.2,th:Number=s.trail?w*.06:w*.11;
                return {w:tw,h:th,x:s.trail?-tw*.45:-s.p[1]*ux,y:s.trail?0:s.p[0]*uy,angle:0,
                    a:s.alpha*(s.trail?0.35:1),r:s.rgb[0],g:s.rgb[1],b:s.rgb[2]};
            }
            var sw:Number=s.size[0]*ux,sh:Number=s.size[1]*(projectile?ux:uy);
            return {w:sw,h:sh,x:projectile?(s.trail?-sw*.45:-s.p[1]*ux):s.p[0]*ux,
                y:projectile?(s.trail?0:s.p[0]*uy):-s.p[1]*uy,angle:physical&&!s.trail?90:projectile&&s.trail?180:0,
                a:s.alpha,r:s.rgb[0],g:s.rgb[1],b:s.rgb[2]};
        }
        public static function sample(values:*,t:Number):Number {
            if(values is Number)return Number(values);
            var n:int=values.length-1;var f:Number=Math.max(0,Math.min(n,t*n));var i:int=Math.min(n-1,int(f));
            return Number(values[i])+(Number(values[i+1])-Number(values[i]))*(f-i);
        }
        public static function pick(curve:Array,t:Number,r:Number):Number {
            var a:Number=sample(curve[0],t);return a+(sample(curve[1],t)-a)*r;
        }
        public static function rotate(q:Array,v:Array):Array {
            var x:Number=q[0],y:Number=q[1],z:Number=q[2],w:Number=q[3];
            var tx:Number=2*(y*v[2]-z*v[1]),ty:Number=2*(z*v[0]-x*v[2]),tz:Number=2*(x*v[1]-y*v[0]);
            return [v[0]+w*tx+y*tz-z*ty,v[1]+w*ty+z*tx-x*tz,v[2]+w*tz+x*ty-y*tx];
        }
        public static function colorKey(keys:Array,t:Number,channel:int):Number {
            if(t<=keys[0][0])return keys[0][channel];
            for(var i:int=1;i<keys.length;i++)if(t<=keys[i][0]){
                var a:Array=keys[i-1],b:Array=keys[i];var f:Number=(t-a[0])/Math.max(.00001,b[0]-a[0]);return a[channel]+(b[channel]-a[channel])*f;
            }
            return keys[keys.length-1][channel];
        }
        public static function gradientValue(pair:Array,t:Number,r:Number,channel:int):Number {
            var field:String=channel==3?"a":"c";var index:int=channel==3?1:channel+1;
            var lo:Number=colorKey(pair[0][field],t,index);return lo+(colorKey(pair[1][field],t,index)-lo)*r;
        }
        public static function plan(preset:Object,seed:uint,cap:int,flight:Number=0,travel:Number=0):Object {
            var state:Object={seed:seed};var groups:Array=[];var total:int=0;var result:Array=[];
            for each(var e:Object in preset.emitters){
                if(preset.family==0&&preset.method==0&&e.name.indexOf("Rainbow")==0)continue;
                if(preset.extent[0]==1000&&e.name=="constantGlow")continue;
                var delay:Number=pick(e.delay,0,random(state));var births:Array=[];
                for each(var birth:Number in e.births)if(!preset.projectile||birth+delay<flight)births.push(birth+delay);
                if(births.length){groups.push({e:e,births:births});total+=births.length;}
            }
            // Keep at least one sample from every nonempty source emitter,
            // then distribute the budget proportionally. No per-frame spawning.
            var available:int=Math.max(0,cap);var duration:Number=preset.projectile?flight:preset.duration;
            for(var gi:int=0;gi<groups.length&&available>0;gi++){
                var group:Object=groups[gi];e=group.e;births=group.births;
                var count:int=Math.min(births.length,Math.max(1,int(cap*births.length/Math.max(1,total))));
                count=Math.min(count,Math.max(1,available-(groups.length-gi-1)));available-=count;
                for(var bi:int=0;bi<count;bi++){
                    var index:int=Math.min(births.length-1,int((bi+.5)*births.length/count));
                    // Single burst/core emitters keep their exact first birth.
                    if(count==births.length)index=bi;
                    var p:Object=spawn(e,births[index],state,preset.projectile,flight,travel);
                    result.push(p);
                }
            }
            return {particles:result,duration:Math.max(.04,duration),preset:preset};
        }
        public static function spawn(e:Object,birth:Number,state:Object,projectile:Boolean,flight:Number,travel:Number):Object {
            var r:Array=[];for(var i:int=0;i<9;i++)r.push(random(state));
            var phase:Number=Math.min(1,birth/Math.max(.001,e.duration));
            var life:Number=Math.max(.02,pick(e.lifetime,phase,r[0]));var speed:Number=pick(e.speed,phase,r[1]);
            var sh:Object=e.shape;var point:Array=[0,0,0],direction:Array=[0,0,1];
            if(sh.enabled){
                var angle:Number=r[2]*Math.PI*2;var radius:Number=sh.radius*Math.sqrt(r[3]);
                if(sh.type==5||sh.type==15||sh.type==16){point=[(r[2]-.5)*sh.scale[0],(r[3]-.5)*sh.scale[1],(r[4]-.5)*sh.scale[2]];}
                else if(sh.type<=3){
                    var z:Number=2*r[4]-1;var ring:Number=Math.sqrt(Math.max(0,1-z*z));direction=[Math.cos(angle)*ring,Math.sin(angle)*ring,z];
                    var radial:Number=sh.type==1||sh.type==3?sh.radius:sh.radius*Math.pow(r[3],1/3);point=[direction[0]*radial,direction[1]*radial,direction[2]*radial];
                }else{
                    point=[Math.cos(angle)*radius,Math.sin(angle)*radius,0];
                    var spread:Number=sh.angle*Math.PI/180*Math.sqrt(r[4]);direction=[Math.cos(angle)*Math.sin(spread),Math.sin(angle)*Math.sin(spread),Math.cos(spread)];
                }
                if(sh.random>0){var az:Number=r[5]*Math.PI*2;var dz:Number=r[6]*2-1;var rr:Number=Math.sqrt(1-dz*dz);direction=[Math.cos(az)*rr,Math.sin(az)*rr,dz];}
            }
            for(i=0;i<3;i++)point[i]=(point[i]+sh.position[i])*e.scale[i];
            point=rotate(e.q,point);var velocity:Array=rotate(e.q,[direction[0]*speed,direction[1]*speed,direction[2]*speed]);
            var current:Array=[e.p[0]+point[0],e.p[1]+point[1],e.p[2]+point[2]];
            var rotation:Number=pick(e.rotation,phase,r[4]);var path:Array=[current.concat([rotation])];var dt:Number=life/24;
            for(var step:int=1;step<=24;step++){
                var t:Number=(step-.5)/24;var force:Array=[0,0,0],added:Array=[0,0,0];
                if(e.force){force=rotate(e.q,[pick(e.force[0],t,r[5]),pick(e.force[1],t,r[5]),pick(e.force[2],t,r[5])]);}
                if(e.velocity){added=rotate(e.q,[pick(e.velocity[0],t,r[6]),pick(e.velocity[1],t,r[6]),pick(e.velocity[2],t,r[6])]);}
                velocity[1]-=9.81*pick(e.gravity,t,r[5])*dt;
                for(i=0;i<3;i++)velocity[i]=(velocity[i]+force[i]*dt)*Math.exp(-Math.max(0,pick(e.drag,t,r[7]))*dt);
                if(e.clamp){
                    var len:Number=Math.sqrt(velocity[0]*velocity[0]+velocity[1]*velocity[1]+velocity[2]*velocity[2]);var limit:Number=Math.max(0,pick(e.clamp,t,r[7]));
                    if(len>limit&&len>0)for(i=0;i<3;i++)velocity[i]*=limit/len;
                }
                for(i=0;i<3;i++)current[i]+=(velocity[i]+added[i])*dt;
                rotation+=pick(e.spin,t,r[8])*dt;path.push(current.concat([rotation]));
            }
            return {e:e,birth:birth,life:life,r:r,path:path,phase:phase,projectile:projectile,flight:flight,travel:travel};
        }
        public static function packet(p:Object,time:Number,out:Object=null):Object {
            if(!out)out={};var age:Number=time-p.birth;var t:Number=age/p.life;out.visible=t>=0&&t<1;
            if(!out.visible)return out;
            var e:Object=p.e,r:Array=p.r;var f:Number=t*24;var i:int=Math.min(23,int(f));f-=i;
            var a:Array=p.path[i],b:Array=p.path[i+1];var x:Number=a[0]+(b[0]-a[0])*f,y:Number=a[1]+(b[1]-a[1])*f;
            out.x=p.projectile?-y:x;out.y=p.projectile?x:-y;
            if(p.projectile&&e.world){
                var now:Number=Math.max(0,Math.min(1,time/Math.max(.001,p.flight))),born:Number=Math.max(0,Math.min(1,p.birth/Math.max(.001,p.flight)));
                now=now*now*now*(now*(now*6-15)+10);born=born*born*born*(born*(born*6-15)+10);out.x-=(now-born)*p.travel;
            }
            var scale:Number=Math.max(Math.abs(e.sizeScale[0]),Math.abs(e.sizeScale[1]),Math.abs(e.sizeScale[2]));
            var size:Number=Math.abs(pick(e.size,p.phase,r[3])*pick(e.sizeOver,t,r[4])*scale);
            out.w=Math.max(.02,size);out.h=e.sizeY?Math.max(.02,Math.abs(pick(e.sizeY,p.phase,r[3])*pick(e.sizeOver,t,r[4])*scale)):out.w;
            out.angle=(a[3]+(b[3]-a[3])*f)*180/Math.PI;
            if(e.stretched){
                var dx:Number=b[0]-a[0],dy:Number=b[1]-a[1];out.angle=Math.atan2(p.projectile?dx:-dy,p.projectile?-dy:dx)*180/Math.PI;
                out.w*=Math.max(1,e.length);
            }
            out.r=e.rgb[0]*gradientValue(e.color,r[5],r[6],0)*(e.over?gradientValue(e.over,t,r[7],0):1);
            out.g=e.rgb[1]*gradientValue(e.color,r[5],r[6],1)*(e.over?gradientValue(e.over,t,r[7],1):1);
            out.b=e.rgb[2]*gradientValue(e.color,r[5],r[6],2)*(e.over?gradientValue(e.over,t,r[7],2):1);
            out.a=Math.min(1,e.alpha*gradientValue(e.color,r[5],r[6],3)*(e.over?gradientValue(e.over,t,r[7],3):1));
            var uv:Number=pick(e.uvStart,p.phase,r[8]);if(e.sheetAnimation)uv+=pick(e.uv,t,r[8])*e.cycles;
            else if(e.tile[4]>1)uv+=r[8];
            out.frame=Math.min(e.tile[4]-1,Math.max(0,int((uv-Math.floor(uv))*e.tile[4])));
            return out;
        }
    }
}
