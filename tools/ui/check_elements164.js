'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path'),crypto=require('crypto'),{performance}=require('perf_hooks');
const root=path.resolve(__dirname,'../..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const board=read('BetaGwent/ui/src/BetaGwentBoard.as'),engine=read('BetaGwent/ui/src/BetaGwentElement164.as'),data=read('BetaGwent/ui/src/BetaGwentElementData164.as'),routing=read('BetaGwent/ui/src/BetaGwentSpecialVfx.as');
function extract(src,name){
 const start=src.indexOf('function '+name+'(');assert(start>=0,name);const open=src.indexOf('{',start);let end=open+1,depth=1;
 for(;depth;end++){if(src[end]==='{')depth++;if(src[end]==='}')depth--;}
 return src.slice(start,end).replace(/:(?:Event|Sprite|TextField|String|Function|Object|Rectangle|void|int|uint|Number|Array|Boolean|Bitmap|Class|ColorTransform|BetaGwentElement164)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/:\*/g,'').replace(/\s+as (?:Sprite|Bitmap|TextField)\b/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))')
 .replace(/(\w+) is Number/g,"(typeof $1==='number')").replace(/(\w+) is TextField/g,'$1 instanceof TextField');
}
class Sprite{constructor(){this.children=[];this.transform={};this.graphics={clear(){},beginBitmapFill(...a){this.fill=a;},drawRect(...a){this.rect=a;},endFill(){}};}addChild(s){s.parent=this;this.children.push(s);return s;}}
class Matrix{constructor(...values){this.values=values;}}
const c=vm.createContext({Math,Number,Object,String,Array,Sprite,Matrix,int:v=>v|0,uint:v=>v>>>0});
const recipes=JSON.parse(read('BetaGwent/ui/assets/elements164/recipes.json'));
const factories=[...data.matchAll(/function ((?:family|preset|emitter)\d+)\(/g)].map(x=>x[1]);
vm.runInContext(factories.map(n=>extract(data,n)).join('\n')+`var groups=[family0(),family1(),family2(),family3(),family4(),family5(),family6(),family7()];`+extract(data,'preset')+extract(data,'names'),c);
c.BetaGwentElementData164={preset:c.preset,RECTS:recipes.rects};
const modelFns=['random','sample','pick','rotate','colorKey','gradientValue','plan','spawn','packet','decoration'];
vm.runInContext(modelFns.map(n=>extract(engine,n)).join('\n'),c);
const bindings=JSON.parse(/BINDINGS:Object=(\{[^\n]+\});/.exec(routing)[1]),prefabs=JSON.parse(/PREFABS:Object=(\{[^\n]+\});/.exec(routing)[1]);
c.BINDINGS=bindings;c.PREFABS=prefabs;vm.runInContext(['profile','projectile','prefabs'].map(n=>extract(routing,n)).join('\n'),c);
c.BetaGwentSpecialVfx={prefabs:c.prefabs,projectile:c.projectile};
let checks=0;const check=(v,n)=>{assert(v,n);checks++;};
check(c.names().length===33,'23 accepted presets plus 10 presentation prefabs; approved lightning excluded');
for(const name of c.names()){
 const p=c.preset(name);assert.deepStrictEqual(JSON.parse(JSON.stringify(p)),JSON.parse(JSON.stringify(recipes.presets[name])),'compiled AS data equals recipe '+name);checks++;
 for(const cap of [4,32,64,180]){
  const plan=c.plan(p,173,cap,p.projectile?.38:0,120);
  check(plan.particles.length<=cap,'bounded particle count '+name);
  check(JSON.stringify(plan)===JSON.stringify(c.plan(p,173,cap,p.projectile?.38:0,120)),'deterministic visual-only seed '+name);
  let visible=0;
  for(const particle of plan.particles)for(let t=0;t<plan.duration;t+=.04){
   const out=c.packet(particle,t,{});if(!out.visible)continue;visible++;
   check(['x','y','w','h','angle','r','g','b','a','frame'].every(k=>Number.isFinite(out[k])),'finite particle pose '+name);
   check(out.frame>=0&&out.frame<particle.e.tile[4]&&out.a>=0&&out.a<=1,'bounded UV/alpha '+name);
  }
  check(visible>0||plan.particles.length===0,'visible source emission '+name);
 }
}
// Execute the actual atlas quad painter with graphics/bitmap shims.
c.bitmaps=Array.from({length:7},()=>({}));c.types=[];
vm.runInContext(extract(read('BetaGwent/ui/src/BetaGwentElementArt164.as'),'paint'),c);
for(let index=0;index<recipes.rects.length;index++){
 const sprite=new Sprite();c.paint(sprite,index,80,100);const r=recipes.rects[index];
 check(sprite.graphics.rect.join(',')==='-40,-50,80,100','one bounded quad '+index);
 const [a,,,d,tx,ty]=sprite.graphics.fill[1].values;
 check(Math.abs((-40-tx)/a-r[1]-.5)<1e-6&&Math.abs((-50-ty)/d-r[2]-.5)<1e-6,'half-texel inset '+index);
}
let models=[];
c.BetaGwentElement164=class extends Sprite{constructor(name,w,h,seed,cap,flight,travel,small){super();this.model=c.plan(c.preset(name),seed,small?4:cap,flight/1000,travel/(w/22));this.particleCount=this.model.particles.length;this.durationMs=small?220:this.model.duration*1000;this.name=name;models.push(this);}};
vm.runInContext(`var activeCue={},revision=9,reducedMotion=false,animations=[];function poseX(p){return p.x+p.width/2;}function poseY(p){return p.y+p.height/2;}function poseW(p){return p.width;}function poseH(p){return p.height;}function cueImpactTime(){return 380;}function rowGeometry(side,row){return {x:500,y:(side==1?550:100)+([1,2,4].indexOf(row))*110,w:900,h:100};}var BetaGwentKillArt144={SOFT_GLOW:1};function killSprite(fx){return fx.addChild(new Sprite());}function killMotion(){}function betaVisual(){return new Sprite();}`+
 ['elementRegion164','drawElement164','drawElementCue164','elementCueFloor164','compactProjectile173','strikeTint173','drawStrike173'].map(n=>extract(board,n)).join('\n'),c);
const hit=(id,side=1,zone=1,delta=-4)=>({id,side,zone,delta,armorDelta:0,x:550+id*50,y:600,width:80,height:100});
for(const count of [1,3,9])for(const small of [false,true]){
 models=[];c.animations=[];c.reducedMotion=small;c.activeCue={kind:2,source:100,target:1,templateId:200224};
 const hits=Array.from({length:count},(_,i)=>hit(i+1,1,[1,2,4][i%3]));const handled=c.drawElementCue164(new Sprite(),hits,960,430,null);
 check(hits.every(h=>handled[h.id]),'Crow targets handled by original elements');
 check(models.filter(m=>m.name==='PowerDarkMagicProjectile').length===(small?0:Math.min(3,count)),'Crow one original projectile per row');
 check(models.reduce((n,m)=>n+m.particleCount,0)<=600,'nine-target frame stays inside shared budget');
 check(c.animations.filter(a=>a.element164&&a.betaFlight).every(a=>a.duration===380),'projectiles land at cue impact');
 check(c.animations.filter(a=>a.element164&&!a.betaFlight).every(a=>a.delay===380),'impacts begin at cue impact');
}
c.reducedMotion=false;c.activeCue={kind:2,source:100,templateId:113301};models=[];
check(c.drawElementCue164(new Sprite(),[hit(1)],0,0,null)===null&&models.length===0,'Alzur retains approved renderer');
const lightning=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentLightning144.as'));
check(crypto.createHash('sha256').update(lightning).digest('hex')==='6947dbbbc1d85d1b928e95a503409c717eda85803ae0819d1409ae01098783be','approved lightning source unchanged');
c.activeCue={kind:2,source:100,templateId:200224,triggerBoost:true};check(c.elementCueFloor164(c.activeCue)===620,'summed trigger boosts remain quick');
c.activeCue={kind:2,source:0,row:1,templateId:113305};check(c.elementCueFloor164(c.activeCue)===0,'weather pipeline unchanged');
const start=performance.now();for(let run=0;run<3;run++)for(let i=0;i<9;i++)c.plan(c.preset('PowerDirectDarkMagic'),100+i,46,0,0);
const planningMs=(performance.now()-start)/3;
// Execute the production replay tick: a delayed impact must become visible
// after waiting, and leave no persistent sprite at the end of its lifetime.
class TextField{}
c.TextField=TextField;c.clock164=0;c.getTimer=()=>c.clock164;
for(const name of ['updateAimPreview','updateActionPreview','tickUiMotions','showHoverPreview'])c[name]=()=>{};
vm.runInContext(`var targetPulses=[],placementMotions=[],pendingImpacts=[],placementGhostAt=0,hoverPreviewAt=0,animationOffset=0,animationStarted=0,animationRate=1,frameAnimationTempo=1,playing=true,animationBaseDuration=1000;`+
 extract(board,'animateCardsBody').replace('BetaGwentElement164(motion.element164)','motion.element164'),c);
const layer=new Sprite();layer.removeChild=s=>{layer.children=layer.children.filter(x=>x!==s);s.parent=null;};
const impact=new Sprite();Object.assign(impact,{scaleX:1,scaleY:1,rotation:0,alpha:1,render:p=>{impact.progress=p;}});layer.addChild(impact);
c.animations=[{sprite:impact,element164:impact,fromX:0,fromY:0,toX:0,toY:0,delay:180,duration:400,hideBeforeDelay:true,remove:true}];
for(const [time,alpha] of [[0,0],[179,0],[180,1],[380,1]]){c.clock164=time;c.animateCardsBody(null);check(impact.alpha===alpha,'delayed impact visibility at '+time);}
c.clock164=580;c.animateCardsBody(null);check(!impact.parent&&c.animations.length===0,'impact is removed with no persistent glow');
if(process.argv.includes('--preview')){
 const output=process.argv[process.argv.indexOf('--preview')+1];const previews=[];
 for(const name of c.names()){
  const preset=c.preset(name),plan=c.plan(preset,173,180,preset.projectile?.38:0,80);const frames=[];
  const w=preset.method>=2?220:52,ux=preset.method>=2?w/preset.extent[0]:w/22,uy=preset.method>=2?110/preset.extent[1]:ux;
  for(const progress of [.12,.32,.57,.82])frames.push({seconds:progress*plan.duration,particles:plan.particles.map(p=>({pose:c.packet(p,progress*plan.duration,{}),tile:p.e.tile,particleId:p.e.id})),static:preset.static.map(s=>({...s,layout:c.decoration(s,w,ux,uy,preset.projectile,name==='PowerPhysicalProjectile')}))});
  previews.push({name,preset:{method:preset.method,extent:preset.extent},frames});
 }
 fs.writeFileSync(output,JSON.stringify({rects:recipes.rects,previews}));
}
const report={stage:164,checks,presets:c.names().length,sharedParticleBudget:600,nineTargetPlanningMs:planningMs,actualActionScript:true,nativeGameTested:false};
console.log(JSON.stringify(report));
