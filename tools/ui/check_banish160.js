'use strict';
// Beta BanishCardEffect regression: data from tools/ui/build_banish160.py, routing,
// replay floor, dissolve masks and the particle timeline (actual ActionScript).
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=process.argv[2]&&fs.existsSync(path.join(process.argv[2],'BetaGwent'))?process.argv[2]:'.';
const src=f=>fs.readFileSync(path.join(root,'BetaGwent/ui/src',f),'utf8');
const board=src('BetaGwentBoard.as'),data=src('BetaGwentDissolveData144.as'),dissolve=src('BetaGwentDissolve144.as'),atlas=src('BetaGwentBanish160.as');
let checks=0;function check(v,label){assert(v,label);checks++;}
function extract(source,name){
 const at=source.indexOf('function '+name+'(');assert(at>=0,name);const start=source.indexOf('{',at);let end=start+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:(Sprite|TextField|Shape|Event|String|Function|Object|Rectangle|void|int|uint|Number|Array|Boolean|Bitmap|BetaGwentDissolve144)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/:\*/g,'').replace(/\s+as (Sprite|Bitmap)\b/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))')
 .replace(/(\w+) is Array/g,'Array.isArray($1)').replace(/(\w+) is Number/g,"(typeof $1=='number')");
}
// Generated data
const noise=/BANISH:String="([0-9a-f]+)"/.exec(data);check(noise&&noise[1].length===44*60*2,'noise grid 44x60');
const ramp=/BANISH_RAMP:Array=\[([^\]]+)\]/.exec(data);check(ramp&&ramp[1].split(',').length===6,'six ramp bands');
check(/BANISH_MS:int=1200;/.test(data),'1.2 s dissolve from CardBanishVisualEffect');
const values=noise[1].match(/../g).map(h=>parseInt(h,16));
check(Math.max(...values)<=254&&values[0]<values[22*44+22],'soft edge noise: border dissolves before centre');
check(/BANISH:int=4/.test(dissolve)&&/kind==BANISH\)\{band=\.15;ramp=BetaGwentDissolveData144\.BANISH_RAMP/.test(dissolve)&&/kind==BANISH\?BetaGwentDissolveData144\.BANISH:/.test(dissolve),'dissolve kind routes to banish data');
const png=fs.readFileSync('BetaGwent/ui/assets/special144/banish_beta.png');
check(png.readUInt32BE(16)===256&&png.readUInt32BE(20)===448,'atlas 256x448');
check(/banish_beta\.png/.test(atlas)&&/beginBitmapFill/.test(atlas)&&!/\.scrollRect=/.test(atlas),'atlas drawn as one quad');
check(fs.existsSync('docs/evidence/banish160.json'),'extraction evidence');
// Routing
const c=vm.createContext({Math,Object,Number,String,Array,int:v=>v|0,cards:[]});
// The elemental engine has its own production-code regression (check_elements164).
c.statusFloor191=()=>0;c.presentationFloor178=()=>0;c.elementCueFloor164=()=>0;c.statusBudget191={remaining:600};c.drawElementCue164=()=>null;
vm.runInContext(extract(board,'banishCueTarget'),c);
check(c.banishCueTarget({kind:12,target:7,templateId:1},7),'BanishOrdinary target');
check(!c.banishCueTarget({kind:12,target:7,templateId:201523},7),'Yrden reset is not a banish');
check(c.banishCueTarget({kind:4,audioKind:12,target:9},9),'banish sound operation');
check(c.banishCueTarget({kind:12,target:1,templateId:5,hitTargets:[3,4]},4)&&c.banishCueTarget({kind:12,target:1,templateId:5,deathTargets:[{id:6}]},6),'grouped targets');
check(!c.banishCueTarget({kind:3,target:7},7)&&!c.banishCueTarget({kind:12,target:7,templateId:5},8)&&!c.banishCueTarget(null,7),'ordinary deaths still go to the graveyard');
// Execute the current routing condition: it also recognises the authoritative
// destination when a banish arrives after its cue. A grave move must not banish.
const route=board.match(/if\((\(int\(previous\.tokens\)&512\)[^\n]+)\)\{\s*drawBanishDeparture/);
check(route,'actual departure routing exists');
const routesToBanish=new Function('previous','activeCue','oldId','cardDestinations082','banishCueTarget','int','return '+route[1]);
const routed=(tokens,cue,dest)=>!!routesToBanish({tokens},cue,9,dest,c.banishCueTarget,v=>v|0);
check(routed(512,null,{})&&routed(0,{kind:4,audioKind:12,target:9},{})&&routed(0,null,{9:{zone:512}}),'doomed, explicit and delayed banish departures use the effect');
check(!routed(0,null,{9:{zone:32}})&&!routed(0,{kind:3,target:9},{}),'ordinary grave departures do not use banish');
const departure=board.indexOf('drawBanishDeparture(previous'),fire=board.indexOf('drawDissolveDeparture(previous');
check(fire>0&&fire<departure,'Execution/Igni/Epidemic burning keeps priority');
// Replay floor
vm.runInContext(`var activeCue=null,MASS_TICK_MS=20,AUTO_MASS_CONSUME=false,animationTempo=1,visualTimeScale=1,reducedMotion=false;
var BetaGwentVisualTimings={FROST_INTRO:1,FOG_INTRO:1,RAIN_INTRO:1};`+['killEffectStyle','cueMinimumDuration','prepareReplayTiming'].map(n=>extract(board,n)).join('\n'),c);
const unit=(id,tokens=0)=>({id,zone:1,side:1,power:3,tokens});
c.cards=[unit(1),unit(2),unit(3,512)];
c.replayFrames=[
 {cue:{kind:12,target:1,templateId:5},cards:[unit(2),unit(3,512)]},
 {cue:{kind:12,target:2,templateId:5},cards:[unit(2),unit(3,512)]},
 {cue:{kind:3,target:3,templateId:0},cards:[unit(2)]},
 {cue:{kind:4,audioKind:12,target:2},cards:[]}];
vm.runInContext('prepareReplayTiming()',c);
const floors=c.replayFrames.map(f=>f.cue.floor);
check(floors[0]>=1300&&floors[1]===460&&floors[2]>=1300&&floors[3]>=1300,'banish frames last the full dissolve '+floors);
// Dissolve masks
class Graphics{constructor(){this.rects=[];this.fills=[];}clear(){this.rects=[];this.fills=[];}beginFill(c,a){this.fills.push([c,a]);}endFill(){}drawRect(...r){this.rects.push(r);}}
class Sprite{constructor(){this.graphics=new Graphics();this.children=[];this.visible=true;}addChild(x){this.children.push(x);return x;}}
const dctx=vm.createContext({Math,Object,Number,String,Array,parseInt,int:v=>v|0,Sprite,Shape:Sprite,BetaGwentDissolveData144:{W:44,H:60,BANISH:noise[1],FIRE:noise[1],POISON:noise[1],BLOOD:noise[1],BANISH_RAMP:ramp[1].split(',').map(Number)}});
const body=dissolve.slice(dissolve.indexOf('public class BetaGwentDissolve144'));
vm.runInContext(`var FIRE=1,POISON=2,BLOOD=3,BANISH=4,cache={};function values(kind){${extract(body,'values').replace(/^[^{]*\{/,'').replace(/\}$/,'')}}`,dctx);
// Render via a minimal instance using the real render body.
vm.runInContext(`var inst={cut:new Shape(),edge:new Shape(),face:new Sprite(),w:88,h:120,noise:values(BANISH),band:.15,ramp:BetaGwentDissolveData144.BANISH_RAMP,alphas:[1,1,1,.95,.8,.5]};`,dctx);
const area=p=>{vm.runInContext(`(function(){with(inst){${extract(body,'render').replace(/^[^{]*\{/,'').replace(/\}$/,'').replace(/progress=Math/,'var progress='+p+';progress=Math')}}})()`,dctx);
 const r=dctx.inst.cut.graphics.rects;return r.reduce((s,x)=>s+x[2]*x[3],0);};
const full=88*120;check(Math.abs(area(0)-full)<1e-6,'whole card before the dissolve');
const mid=area(.3);check(mid>0&&mid<full,'partial dissolve at 0.36 s');
check(dctx.inst.edge.graphics.rects.length>0&&dctx.inst.edge.graphics.fills.every(f=>f[0]===0x7900CD||f[0]===0xFFC5FF||f[0]===0xFFFFFF||f[0]===0xFF8FFF||f[0]===0x7300C7),'violet/white edge from EpicHighlightGradient');
area(1);check(dctx.inst.face.visible===false,'card removed at the end');
// Particle timeline
const motions=[],cells=[];
const p=vm.createContext({Math,Object,Number,String,Array,int:v=>v|0,Sprite,reducedMotion:false,animations:motions,content:new Sprite(),
 BetaGwentDissolve144:function(){this.isDissolve=true;},BetaGwentDissolveData144:{BANISH_MS:1200},
 BetaGwentBanish160:{HIT:0,SHARD:1,cell:(kind,index,w,h,r,g,b)=>{const s=new Sprite();s.kind=kind;s.w=w;s.h=h;s.tint=[r,g,b];cells.push(s);return s;}},
 poseW:q=>q.width,poseH:q=>q.height,paintPlacementCard:(face,pose)=>{face.tokens=pose.tokens;}});
p.BetaGwentDissolve144.BANISH=4;
vm.runInContext(['killMotion','drawBanishDeparture','banishShards'].map(n=>extract(board,n)).join('\n'),p);
vm.runInContext('drawBanishDeparture({x:100,y:200,width:88,height:92,tokens:516,timer:2,armor:3},40)',p);
const dissolveMotion=motions.find(m=>m.dissolve);
check(dissolveMotion&&dissolveMotion.duration===1200&&dissolveMotion.delay===40,'card dissolves for 1.2 s');
const parts=motions.filter(m=>!m.dissolve);
check(parts.length===57&&cells.filter(s=>s.kind===0).length===8&&cells.filter(s=>s.kind===1).length===49,'8 BackLines + 25 Mid + 24 Rim particles');
const lines=parts.slice(0,8),shards=parts.slice(8);
check(lines.every(m=>m.delay===70&&m.duration>=180&&m.duration<=300&&m.fromScaleX===0&&m.toScaleX===1&&m.scene&&!m.fade),'BackLines grow 0 -> 1 at 0.03 s');
check(cells.slice(0,8).every(s=>s.tint[1]===0&&s.tint[2]<=2*.176*.26+1e-9),'BackLines are dark indigo');
check(shards.slice(0,25).every(m=>m.delay>=220&&m.delay<=220+330)&&shards.slice(25).every(m=>m.delay>=270&&m.delay<=270+330),'Mid at 0.18 s, Rim at 0.23 s over 0.33 s');
check(shards.every(m=>m.fromScaleY>m.toScaleY&&Math.abs(m.toScaleY/m.fromScaleY-.308/.875)<1e-9),'shards shrink .875 -> .308');
check(parts.every(m=>m.delay+m.duration<=40+1200),'particles finish within the dissolve');
const u=88/22;check(shards.every(m=>Math.hypot(m.toX-m.fromX,m.toY-m.fromY)<=75*.5*u+1e-6||Math.hypot(m.toX-m.fromX,m.toY-m.fromY)<=120*.6*u),'speed clamps bound travel');
motions.length=0;cells.length=0;p.reducedMotion=true;vm.runInContext('drawBanishDeparture({x:0,y:0,width:80,height:84,tokens:0},0)',p);
check(motions.length===1&&motions[0].duration===200&&cells.length===0,'reduced motion: short dissolve only');
console.log(JSON.stringify({stage:160,checks,actualActionScript:true,nativeGameTested:false}));
