'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const b=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8'),e=fs.readFileSync('BetaGwent/ui/src/BetaGwentElement164.as','utf8');
const recipes=JSON.parse(fs.readFileSync('BetaGwent/ui/assets/elements164/recipes.json','utf8'));
function fn(src,name){const a=src.indexOf('function '+name+'('),o=src.indexOf('{',a);assert(a>=0,name);let i=o+1,d=1;while(d){if(src[i]==='{')d++;if(src[i]==='}')d--;i++;}return src.slice(a,i).replace(/:(?:String|Object|Sprite|TextField|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
const c=vm.createContext({Math,String,Number,Object,int:v=>v|0});
vm.runInContext(`var activeCue={},reducedMotion=false,draws=[],animations=[],revision=1,previousPoses={},BetaGwentUi138={chains:true,helpLabels:false};
function rowGeometry(side,row){return {x:500,y:(side==1?550:100)+[1,2,4].indexOf(row)*110,w:900,h:100};}
function drawElement164(fx,name,x,y,w,h,delay,budget,cap,flight,sx,sy,branch){draws.push({name,x,y,w,h,delay,flight});return true;}
function cueImpactTime(){return 380;}function poseX(p){return p.x+p.width/2;}function poseY(p){return p.y+p.height/2;}function poseW(p){return p.width;}function poseH(p){return p.height;}
var BetaGwentElementData164={preset(name){return recipes.presets[name];}},BetaGwentSpecialVfx={prefabs(id,hurting){return id==200301?{element:32,method:3,attack:'PowerSideIce'}:null;},projectile(){return false;}};
var boosts=0;function drawBoostCue(){boosts++;}function cardById(){return {};}
`+['drawWeatherCast','elementCueFloor164','drawElementCue164','drawRecoveryCue'].map(n=>fn(b,n)).join('\n')+fn(e,'decoration'),c);c.recipes=recipes;
let checks=0;const check=(v,n)=>{assert(v,n);checks++;};
for(const id of [113303,113401]){c.activeCue={kind:4,templateId:id,side:1,row:0};c.draws=[];c.drawWeatherCast({});check(c.draws.length===1&&c.draws[0].name==='BoardEffect_ClearWeather','original clear prefab for direct and generated Clear Skies '+id);check(c.draws[0].w>=1920&&c.draws[0].h>=1080,'stage 175: clear-sky shafts cover the whole screen (Beta Dawn footage) '+id);check(c.elementCueFloor164(c.activeCue)>=recipes.presets.BoardEffect_ClearWeather.duration*1000,'clear rays complete before next snapshot '+id);}
c.activeCue={kind:4,templateId:113401,side:1,row:0};c.reducedMotion=true;c.draws=[];c.drawWeatherCast({});check(c.draws.length===0&&c.elementCueFloor164(c.activeCue)===0,'reduced motion has no long shafts');c.reducedMotion=false;
c.activeCue={kind:2,templateId:200301,source:100};c.draws=[];c.boosts=0;
const hits=Array.from({length:4},(_,i)=>({id:i+1,side:1,zone:1,delta:1,armorDelta:0,x:600+i*90,y:500,width:80,height:110}));
const handled=c.drawElementCue164({},hits,800,800,{});
check(hits.every(h=>handled[h.id])&&c.boosts===4,'all Hunt boosts receive a compact arrival');
check(c.draws.length===0,'boost never invokes an attack prefab or side-wide crescent');
for(const s of recipes.presets.PowerLightMagicProjectile.static){const d=c.decoration(s,80,80/22,80/22,true,false);check(d.w<=80&&d.h<=9&&d.a<=.35,'Parasite trail is a thin translucent ribbon');}
for(const s of recipes.presets.PowerPhysicalProjectile.static){const d=c.decoration(s,80,80/22,80/22,true,true);check(Math.abs(d.w-s.size[0]*80/22)<1e-6&&Math.abs(d.h-s.size[1]*80/22)<1e-6,'stage 174: physical shot keeps source proportions (Beta footage)');check(d.angle===(s.trail?180:90),'trail head leads, tip points along the flight axis');}
// Runtime plan deliberately omits the requested late rainbow wave; source recipes stay pinned.
check(/e\.name\.indexOf\("Rainbow"\)==0\)continue/.test(fn(e,'plan')),'late blue/rainbow wave omitted from direct light boost');
check(!fn(b,'drawRecoveryCue').includes('graphics'),'recovery has no ellipse or plus-sign overlay');
c.BetaGwentUi138.effect=()=> 'recovery';c.activeCue={target:1};c.boosts=0;c.drawRecoveryCue({},hits[0]);check(c.boosts===1,'recovery uses one finite soft arrival');
const ice=recipes.presets.PowerSideIce.emitters.filter(x=>x.name==='HailLeft'||x.name==='HailRight');check(ice.length===2&&ice.every(x=>x.tile[4]===36),'ice hail samples the 6x6 sheet instead of displaying its grid');
check(recipes.presets.BoardEffect_ClearWeather.static.some(s=>s.name==='LayeredShaft'),'original clear-weather light-shaft mesh included');
check(!/hintVisible:BetaGwentUi138.helpLabels/.test(fn(b,'controllerContext')),'service text switch does not hide controller hints');
check(b.includes('if(!controller.active)drawBetaHint("Удерживайте ПКМ · ускорить"'),'mouse acceleration hint remains visible');
check(b.includes('if(activeCue.title&&BetaGwentUi138.helpLabels)')&&fn(b,'drawChainCue').includes('if(BetaGwentUi138.helpLabels)'),'field actor labels and effect strip honor the service text switch');
check(!fn(b,'drawWeatherImpact').includes('BoardEffect_ClearWeather'),'sun shafts are a weather cast, never a per-card weather damage tick');
check(!b.includes('text(content,!BetaGwentUi138.helpLabels'),'sidebar state and errors remain part of the interface');
const report={stage:168,checks,actualActionScript:true,nativeGameTested:false,clearWeatherSource:'BoardEffect_ClearWeather/LayeredShaft',atlasMiB:JSON.parse(fs.readFileSync('docs/evidence/elements164.json','utf8')).inlineDDSBytes/1048576};
fs.writeFileSync('docs/evidence/vfx168.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
