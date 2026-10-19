// Execute production routing, target grouping, timing and projectile helpers.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const routing=fs.readFileSync('BetaGwent/ui/src/BetaGwentSpecialVfx.as','utf8');
function extract(source,name){
 const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);assert(start>=0,name);
 let depth=1,end=open+1;for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(Sprite|TextField|Event|Error|String|Object|void|int|uint|Number|Array|Boolean|\*)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
class Sprite{constructor(){this.graphics=new Proxy({},{get:()=>()=>{}});this.children=[];this.scaleX=this.scaleY=this.alpha=1;this.rotation=0;}addChild(s){s.parent=this;this.children.push(s);return s;}removeChild(s){s.parent=null;this.children=this.children.filter(c=>c!==s);}}
const c=vm.createContext({console,Math,Number,String,Object,Sprite,int:x=>x|0,GlowFilter:class{}});
// The elemental engine has its own production-code regression (check_elements164).
c.elementCueFloor164=()=>0;c.statusBudget191={remaining:600};c.drawElementCue164=()=>null;
c.drawElement164=(parent,name)=>{assert(name==='BoardEffect_ClearWeather');const sprite=new Sprite();parent.addChild(sprite);c.animations.push({sprite,duration:2100});return true;};
const bindings=routing.match(/BINDINGS:Object=(\{.*\});/)[1];
vm.runInContext('var BINDINGS='+bindings+';'+['profile','projectile','tint'].map(n=>extract(routing,n)).join('\n')+'\nvar BetaGwentSpecialVfx={profile,projectile,tint};',c);
vm.runInContext(`var animations=[],bursts=[],histories=[],displayedCards={},previousPoses={},departedPoses={},cardDetails={};
var content=new Sprite(),activeCue={},reducedMotion=false,skin=3,flags=0,lastRoundResult=null;
var frameAnimationTempo=1,animationRate=1,animationBaseDuration=930;
var BetaGwentUi138={intensity:1};
function betaVisual(id,w,h,tint){var s=new Sprite();s.artId=id;s.tint=tint;return s;}
function betaBurst(...a){bursts.push(a);}function betaLabel(){return {filters:[]};}
function panel(parent){return parent.addChild(new Sprite());}function paintArt(){}
function drawChainCue(){}function drawRecoveryCue(){}function drawLeaderScene(){}function drawWeatherCast(){}function cuePileOrigin(){return null;}
var BetaGwentKillArt144={SOFT_GLOW:1};function killSprite(parent){return parent.addChild(new Sprite());}function killMotion(sprite,x,y,tx,ty,delay,duration){animations.push({sprite,duration});}function drawBoostCue(){}
function drawRowWaves(){}function drawWeatherImpact(){}function drawStrike173(){}function strikeTint173(){return 0xFFFFFF;}
function rowGeometry(side,row){return {x:300,y:row==1?100:row==2?300:500,w:80,h:100};}
function noteHistory(cue,scores,cards){histories.push({cue,scores,cards});}var BetaGwentFonts={BODY:'body'};
`+['collapseSweeps','collapseWeatherCasts','collapseTriggerBoosts','noteFrameHistory','poseX','poseY','poseW','poseH','cueImpactTime','cueImpactDelay','drawCrowProjectiles','drawSpecialProjectile','drawDamageProjectile','drawBetaHit','drawVisualCue'].map(n=>extract(board,n)).join('\n'),c);
let checks=0;function check(v,n){assert(v,n);checks++;}
check(c.profile(200224,true).element===1024&&c.projectile(200224),'Crow Eye uses original DarkMagic projectile routing');
check(c.profile(200224,false)===null,'damage routing cannot recolor an unrelated allied boost');
check(c.profile(999999,true)===null,'unknown spells keep existing fallback');
const frame=(source,target)=>({cue:{kind:2,source,target,templateId:200224},cards:[],scores:[0,0]});
const frames=[frame(1,2),frame(99,90),frame(1,3),frame(1,4)],original=JSON.stringify(frames);
const group=c.collapseSweeps(frames);
check(group.length===1&&Array.from(group[0].cue.hitTargets).join(',')==='2,3,4','reaction boosts never become projectile targets');
check(JSON.stringify(frames)===original,'sweep never mutates input snapshots');
c.noteFrameHistory(group[0]);check(c.histories.length===4,'history preserves each hit and intervening reaction');
for(const targets of [1,2,3])for(const reduced of [false,true])for(const tempo of [1,1.5,2])for(const rate of [1,4]){
 c.animations=[];c.bursts=[];c.reducedMotion=reduced;c.frameAnimationTempo=tempo;c.animationRate=rate;c.animationBaseDuration=930/tempo;
 c.activeCue={kind:2,source:1,target:2,templateId:200224,attackCount:targets,hitTargets:Array.from({length:targets},(_,i)=>i+2)};
 c.displayedCards={90:{id:90,x:1200,y:800,width:80,height:100,delta:2,side:2,zone:1}};
 for(let i=0;i<targets;i++)c.displayedCards[i+2]={id:i+2,x:300,y:100+i*200,width:80,height:100,delta:-4,side:1,zone:[1,2,4][i]};
 c.content=new Sprite();c.drawVisualCue();
 const bolts=c.animations.filter(a=>a.betaFlight);
 check(bolts.length===(reduced?0:targets*3),'one small bolt with two faint ghosts per actual target; reduced motion disables it');
 if(!reduced){
  check(Math.abs(c.cueImpactDelay()-380/tempo/rate)<1e-8,'audio shares spell arrival time at all replay speeds');
  check(bolts.every(b=>(b.delay||0)+b.duration===380),'bolt and every trailing ghost arrive together');
  check(bolts.every(b=>b.toX===340&&[150,350,550].includes(b.toY)),'no projectile points at the allied reaction');
  check(bolts.every(b=>b.sprite.parent&&!b.sprite.mouseEnabled&&!b.sprite.mouseChildren),'spell layers cannot intercept input');
 }
}
for(const element of [16,32,64,512,1024]){
 c.animations=[];c.bursts=[];c.drawSpecialProjectile(new Sprite(),0,0,200,300,{element,method:0},0xffffff,180,0);
 check(c.animations.length===0&&c.bursts.length===0,'direct effects add no flight and no extra burst (strike is drawn at the card) '+element);
}
for(let count=2;count<=18;count++){
 const initial=Array.from({length:count},(_,i)=>({id:i+1,templateId:132305,power:5,armor:0,zone:1,side:1}));
 let state=initial.map(x=>({...x}));const inputs=[];
 for(let i=0;i<count;i++){state=state.map(x=>x.id===i+1?{...x,power:6}:x);inputs.push({cue:{kind:2,source:i+1,target:i+1,templateId:132305},cards:state,scores:[count*5+i+1,0]});}
 const old=JSON.stringify(inputs),merged=c.collapseTriggerBoosts(inputs,initial);
 check(merged.length===1&&merged[0].cue.hitTargets.length===count,'all adjacent triggered boosts resolve in one visual beat '+count);
 check(merged[0].cards===inputs[count-1].cards&&merged[0].scores[0]===count*6,'group uses the exact final rules snapshot '+count);
 check(JSON.stringify(inputs)===old,'boost grouping preserves immutable input '+count);
 check(c.collapseSweeps(merged).length===1,'the following damage sweep pass keeps the grouped trigger atomic');
 c.histories=[];c.noteFrameHistory(merged[0]);check(c.histories.length===count,'history preserves every triggered source '+count);
 for(const barrier of [3,4,5,9,11,13,15,16]){
  const separated=[inputs[0],{cue:{kind:barrier,source:99},cards:inputs[0].cards,scores:inputs[0].scores},...inputs.slice(1)];
  check(c.collapseTriggerBoosts(separated,initial).length>=3,'boosts do not cross a semantic barrier '+barrier);
 }
}
for(const id of [113206,113101,200018])for(const count of [2,3]){
 const frames=Array.from({length:count},(_,i)=>({cue:{kind:4,source:10,templateId:id,side:2,row:1<<i},cards:[],weatherRows:[i],scores:[0,0]}));
 const before=JSON.stringify(frames),group=c.collapseWeatherCasts(frames);
 check(group.length===1&&group[0].cue.weatherCastRows.length===count,'weather is one cast across the affected rows '+id);
 check(group[0].weatherRows===frames[count-1].weatherRows&&JSON.stringify(frames)===before,'weather uses final snapshot without mutating originals');
 c.histories=[];c.noteFrameHistory(group[0]);check(c.histories.length===count,'weather retains each changed row in history');
 const repeated=[frames[0],{...frames[1],cue:frames[0].cue}];check(c.collapseWeatherCasts(repeated).length===2,'separate casts on the same row stay separate');
}
vm.runInContext(`var BetaGwentWeather107={FROST_SPIKES:1,DROUGHT_SAND:2,RAGH_VEINS:3,FROTH_FOAM:4,NOVA:5};
function rowGeometry(side,zone){if(![1,2,4].includes(zone))throw Error('invalid weather row');return {x:100,y:side*400+Math.log2(zone)*100,w:800,h:90};}
function drawRagnarok080(parent){var s=new Sprite();parent.addChild(s);animations.push({sprite:s,duration:2017});}
`+extract(board,'drawWeatherCast'),c);
for(const id of [113206,113101,200018,201749,113303]){
 c.reducedMotion=false;c.animations=[];c.bursts=[];c.activeCue={kind:4,templateId:id,side:1,row:id===113303?0:1,weatherCastRows:[{side:1,zone:1},{side:1,zone:2}]};
 const parent=new Sprite();c.drawWeatherCast(parent);
 check(parent.children.length===1,'one entry overlay for the complete weather cast '+id);
 check(c.animations.length===1&&(id===113303?c.animations[0].duration===2100:id===113101?c.animations[0].duration===2017:c.animations[0].duration<=800),'one weather scene per cast; original clear shafts and Ragnarok retain their lifetime');
 c.reducedMotion=true;const quiet=new Sprite();c.drawWeatherCast(quiet);check(quiet.children.length===0,'reduced motion retains state without entry animation');
}
// Brightness affects alpha only, independently of tempo and arrival time.
c.reducedMotion=false;c.BetaGwentUi138.intensity=.25;c.activeCue={kind:2,source:1,target:2,templateId:200224,hitTargets:[2]};
c.content=new Sprite();c.drawVisualCue();check(c.content.children[0].alpha===.25,'brightness applies only to the VFX layer');
vm.runInContext(`var playing=false,ready=true,flags=0,current=1,requestId=0,requestKind=0,rowRequest=false,selected=10;
var playRules={10:{kind:1,side:2,types:4,tiers:6,ignore:8,maximum:9}},cardDetails={20:{typeMask:4,tier:2}};
function canPlacePending(){return false;}function findRequestCard(id){return id===20?{}:null;}
`+extract(board,'battleDisabledReason'),c);
const candidate={id:20,side:2,zone:1,power:8,tokens:0};
check(c.battleDisabledReason(candidate)==='','legal target has no false disabled warning');
check(c.battleDisabledReason({...candidate,side:1}).includes('вражеский'),'wrong-side reason is explicit');
check(c.battleDisabledReason({...candidate,power:10}).includes('9'),'power-limit reason includes the authoritative limit');
check(c.battleDisabledReason({...candidate,tokens:8}).includes('статус'),'protected/hidden target remains ineligible');
c.current=2;check(c.battleDisabledReason(candidate).includes('ход соперника'),'opponent turn explained');c.current=1;
c.requestId=1;c.requestKind=2;check(c.battleDisabledReason({...candidate,id:21}).includes('допустимые цели'),'pending ability respects actual native target whitelist');
c.requestId=0;c.reducedMotion=false;c.animations=[];c.content=new Sprite();
c.BetaGwentFullCatalog={find(id){return id===131101?{leader:true}:null;}};
c.activeCue={kind:1,source:50,target:50,templateId:131101,side:1};
c.displayedCards={50:{id:50,x:500,y:500,width:80,height:100,delta:0}};
c.drawVisualCue();check(c.content.children[0].children.length===0&&c.animations.length===0,'leader play adds no scene, burst, aura or landing marker');
const report={stage:142,checks,actualActionScript:true,nativeGameTested:false,sourceSha256:crypto.createHash('sha256').update(board).digest('hex')};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
