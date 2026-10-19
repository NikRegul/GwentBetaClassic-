'use strict';
// Stage 173/174: battle effects matched to Beta 0.9.24 footage.
// Original Direct prefabs per card, original physical shot, additive light,
// impacts clamped to ~2.5 card widths, Beta-style centred numbers.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const engine=fs.readFileSync('BetaGwent/ui/src/BetaGwentElement164.as','utf8');
const blend=fs.readFileSync('BetaGwent/ui/src/BetaGwentElementBlend173.as','utf8');
function fn(src,name){const start=src.indexOf('function '+name+'(');assert(start>=0,name);let i=src.indexOf('{',start)+1,d=1;while(d){if(src[i]==='{')d++;if(src[i]==='}')d--;i++;}
 return src.slice(start,i).replace(/:(?:String|Object|Sprite|Number|Array|Boolean|int|uint|void)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/var (\w+):\w+/g,'var $1')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
let checks=0;function check(v,n){assert(v,n);checks++;}
class Sprite{constructor(){this.children=[];}addChild(c){this.children.push(c);return c;}}
const c=vm.createContext({Math,String,Number,Object,Array,Error,Sprite,int:v=>v|0,uint:v=>v>>>0});
Object.assign(c,{activeCue:{},reducedMotion:false,draws:[],strikes:[],boosts:[],cueImpactTime:()=>180,
 poseX:p=>p.x+p.width/2,poseY:p=>p.y+p.height/2,poseW:p=>p.width,poseH:p=>p.height,rowGeometry:(s,r)=>({x:500,y:r*100,w:900,h:100}),
 BetaGwentElementData164:{preset:n=>n&&!/Side|Row|Board/.test(n)?{duration:n.indexOf('Physical')>=0?0.6:1.1,method:0}:null},
 drawElement164:(fx,name,x,y,w,h,delay,budget,cap,flight,sx,sy,branch,soft)=>{c.draws.push({name,delay,flight,cap,soft:!!soft});return true;},
 drawStrike173:(fx,hit)=>c.strikes.push(hit.id),drawBoostCue:(fx,hit)=>c.boosts.push(hit.id)});
let prefabs=null;c.BetaGwentSpecialVfx={prefabs:(id,h)=>typeof prefabs==='function'?prefabs(h):prefabs,projectile:()=>prefabs&&prefabs.method==1};
vm.runInContext(['drawElementCue164','elementCueFloor164'].map(n=>fn(board,n)).join('\n'),c);
const card=(id,delta)=>({id,side:1,zone:1,delta,armorDelta:0,x:100+id*90,y:600,width:80,height:110});
const run=(p,hits,source=99)=>{prefabs=p;c.draws=[];c.strikes=[];c.boosts=[];c.activeCue={kind:2,source,templateId:1};return c.drawElementCue164(new Sprite(),hits,960,430,null);};
// Unbound unit damage (Beta footage): one original shot per target, then the Direct flash.
run(null,[1,2,3].map(i=>card(i,-1)));
check(c.draws.filter(d=>d.name==='PowerPhysicalProjectile'&&d.flight===180).length===3,'each target receives its own physical shot');
check(c.draws.filter(d=>d.name==='PowerDirectPhysical'&&d.delay===180).length===3,'each target flashes at the impact instant');
// Self-damage / trigger: no flight.
run(null,[card(5,-1)],5);check(c.draws.map(d=>d.name).join()==='PowerDirectPhysical','no shot from a card to itself');
// Unbound boost (Ale in the footage): Direct light magic on the card, no flight.
run(null,[1,2].map(i=>card(i,4)));check(c.draws.length===2&&c.draws.every(d=>d.name==='PowerDirectLightMagic'&&!d.flight&&d.soft),'boost is the per-card Beta starburst, drawn soft');
run(null,[card(1,-2)]);check(c.draws.every(d=>!d.soft),'hits keep full strength');
// Side/Row/Board bindings never stretch over the field: their per-card impact is used.
for(const attack of ['PowerSideLightMagic','PowerRowLightMagic','PowerBoardLightMagic'])
 {run({attack,impact:'PowerDirectLightMagic',method:3,element:512},[1,2,3,4].map(i=>card(i,1)));check(c.draws.length===4&&c.draws.every(d=>d.name==='PowerDirectLightMagic'),'per-card boost for '+attack);}
run({attack:'PowerSideIce',impact:null,method:3,element:32},[card(1,-2),card(2,-2)]);check(c.draws.length===0&&c.strikes.length===2,'ice side without Direct prefab falls back to the bounded strike');
run({attack:'AirTokenAttack',impact:null,method:3,element:256},[card(1,-2)]);check(c.draws.map(d=>d.name).join()==='AirTokenAttack','Aard keeps its per-unit impact');
run({attack:'PowerFireProjectile',impact:'PowerDirectFire',method:1,element:16},[card(1,-2)]);check(c.draws.map(d=>d.name).join()==='PowerFireProjectile,PowerDirectFire','bound spell shot and impact');
run({attack:'PowerLightningProjectile',impact:'PowerDirectLightning',method:1,element:64},[card(1,-2)]);check(c.draws.length===0,'approved lightning renderer untouched');
c.reducedMotion=true;run(null,[card(1,3)]);check(c.draws.length===0&&c.boosts.length===0,'reduced motion: no decorative boost');c.reducedMotion=false;
prefabs=null;check(c.elementCueFloor164({kind:2,source:1,templateId:1})===1100+180+30,'floor covers the longest Direct prefab');
// Renderer: additive table, clamp, shot proportions, no paper tip.
const ids=[...blend.matchAll(/"(\d+)":1/g)].map(m=>+m[1]);check(ids.length>=90&&ids.includes(3399)&&ids.includes(3156),'original 90 additive emitters preserved alongside new presentation particles');
check(engine.includes('if(BetaGwentElementBlend173.additive(int(particle.e.id)))cell.blendMode="add";'),'additive materials render as light');
check(engine.includes('public static const MAX_UNITS:Number=55;')&&engine.includes('!model.preset.projectile&&model.preset.method<2&&biggest>limit'),'card impacts clamped to ~2.5 card widths');
check(engine.includes('if(s.name=="ArrowTipShape")continue;'),'no opaque paper tip');
check(engine.includes('grown:Number=Math.max(.02,Math.min(1,progress*travelPx/full))')&&engine.includes('sprite.x=full*.05-full*grown/2;'),'shot starts at the card centre: trail grows with distance flown');
check(engine.includes('color.alphaMultiplier=out.a*intensity*')&&board.includes('(soft?0.45:1)*strength,soft?35:BetaGwentElement164.MAX_UNITS'),'boost: 45% strength, at most 1.6 card widths');
// Board details.
const cards=fn(board,'drawCards'),visual=fn(board,'drawVisualCue');
check(cards.includes('flash.visible=false;'),'no card wash: the prefab is the flash');
check(cards.includes('number.y=cardHeight*.55')&&cards.includes('Math.max(20,cardHeight*.32)')&&cards.includes('new GlowFilter(0x000000'),'Beta-style large outlined number in the card centre');
check(!visual.includes('drawRowWaves('),'no sweeping row bands');
for(const dir of ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])for(const f of ['BetaGwentBoard.as','BetaGwentElement164.as','BetaGwentElementBlend173.as'])
 check(fs.readFileSync('BetaGwent/ui/'+dir+'/'+f,'utf8')===fs.readFileSync('BetaGwent/ui/src/'+f,'utf8'),'mirror '+dir+'/'+f);
for(const f of ['BetaGwentBoard.as','BetaGwentElement164.as','BetaGwentElementBlend173.as']){const raw=fs.readFileSync('BetaGwent/ui/src/'+f);check(raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString('utf8')),'BOM and CRLF '+f);}
// Stage 175: light, not paint, in the remaining Beta effects.
const kill=fs.readFileSync('BetaGwent/ui/src/BetaGwentKillArt144.as','utf8');
check(/ADDITIVE:Object=\{0:1,1:1,3:1,8:1/.test(kill)&&kill.includes('if(add)holder.blendMode="add";'),'kill atlas glows, flames, embers and Yrden draw as light');
check(!/[{,]2:1/.test(kill.match(/ADDITIVE:Object=\{[^}]*\}/)[0])&&!/[{,]23:1/.test(kill.match(/ADDITIVE:Object=\{[^}]*\}/)[0]),'shared smoke/spark textures are decided per call');
check((board.match(/BetaGwentKillArt144\.SPARK,1[46]\+Math\.random\(\)\*1[02],[^;]*,cx,cy,1,5,1\);/g)||[]).length===2,'fire and Igni sparks are additive; poison and blood drops stay paint');
check((board.match(/MAGIC_SMOKE,size\*1\.[36],0x12EC00,cx,cy,[^)]*,-1,1\)/g)||[]).length===2,'poison glow is Additive (Soft) as in Beta');
check(fn(board,'betaBurst').includes('if(id==-103||id==-105||id==-106||id==BetaGwentWeather107.SPARKLE||id==BetaGwentWeather107.NOVA)burst.blendMode="add";'),'star/streak/sparkle bursts are light');
check(engine.includes('if(name=="BoardEffect_ClearWeather")buildShafts(w,h,seed);')&&engine.includes('if(s.name=="LayeredShaft")continue;')&&board.includes('drawElement164(fx,"BoardEffect_ClearWeather",960,540,2400,1080'),'Clear Sky: warm additive shafts over the whole screen');
for(const dir of ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])check(fs.readFileSync('BetaGwent/ui/'+dir+'/BetaGwentKillArt144.as','utf8')===kill,'mirror KillArt '+dir);
const report={stage:175,checks,actualActionScriptMethods:true,reference:'Beta 0.9.24 footage (user video): Ale boost, unit shot and impact',nativeGameTested:false,releaseBuilt:false};
fs.writeFileSync('docs/evidence/presentation175.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
