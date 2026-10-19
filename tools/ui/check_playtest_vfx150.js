'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const art=fs.readFileSync('BetaGwent/ui/src/BetaGwentKillArt144.as','utf8');
const dissolve=fs.readFileSync('BetaGwent/ui/src/BetaGwentDissolve144.as','utf8');
function extract(source,name){
 const at=source.indexOf('function '+name+'(');assert(at>=0,name);const start=source.indexOf('{',at);let end=start+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:(Sprite|TextField|Shape|Event|String|Function|Object|Rectangle|void|int|uint|Number|Array|Boolean|Bitmap)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/:\*/g,'').replace(/\s+as (Sprite|Bitmap)\b/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
class Graphics{constructor(){this.rects=[];}clear(){this.rects=[];}beginFill(){}endFill(){}beginBitmapFill(data,m){this.matrix=m;this.data=data;}drawRect(...r){this.rects.push(r);}}
class Sprite{constructor(){this.graphics=new Graphics();this.children=[];this.transform={};this.visible=true;}addChild(c){this.children.push(c);return c;}}
class Bitmap{constructor(data){this.bitmapData=data||{width:1024,height:512};}}
class Matrix{constructor(...args){this.values=args;}}
const c=vm.createContext({Math,Object,Number,String,Sprite,Bitmap,Matrix,ColorTransform:class{},int:v=>v|0});
// The elemental engine has its own production-code regression (check_elements164).
c.statusFloor191=()=>0;c.presentationFloor178=()=>0;c.elementCueFloor164=()=>0;c.statusBudget191={remaining:600};c.drawElementCue164=()=>null;
let checks=0;function check(v,label){assert(v,label);checks++;}
vm.runInContext(`var shared=null,shared2=null;function Atlas(){return new Bitmap();}function Atlas2(){return new Bitmap({width:1024,height:256});}`+extract(art,'additive')+extract(art,'cell')+';var ADDITIVE={0:1,1:1};',c);
for(let index=0;index<48;index++)for(const size of [[80,100],[240,60],[8,4]]){
 const sprite=c.cell(index,...size),quad=sprite.children[0];
 check(quad.children.length===0&&quad.graphics.rects.length===1,'atlas is submitted as one destination quad '+index);
 const [a,b,cc,d,tx,ty]=quad.graphics.matrix.values,logical=index%32;
 const left=-tx/a,top=-ty/d;
 check(Math.abs(left-((logical%8)*128+.5))<1e-7&&Math.abs(top-(Math.floor(logical/8)*128+.5))<1e-7,'quad samples exact original cell '+index);
 check(quad.graphics.rects[0].join(',')===[0,0,...size].join(','),'quad bounds exclude neighbouring cells '+index);
}
vm.runInContext(`var cards=[],activeCue={},animationTempo=1,visualTimeScale=1,AUTO_MASS_CONSUME=false,MASS_TICK_MS=20;
var reducedMotion=false,replayFrames=[];`+['collapseMourntart','collapseProjectileDeaths','collapseSweeps','killEffectStyle','cueMinimumDuration','prepareReplayTiming'].map(n=>extract(board,n)).join('\n'),c);
for(let count=2;count<=24;count++){
 let state=[{id:1,power:4,armor:0,tokens:0,zone:1,side:1},{id:2,power:3,armor:0,tokens:0,zone:1,side:1}];c.cards=state;
 const frames=[];
 for(let i=0;i<count;i++){
  frames.push({revision:i*3,cue:{kind:11,source:1,target:100+i,templateId:132202,targetView:{zone:512,templateId:142317,side:1}},cards:state});
  frames.push({cue:{kind:8,source:2,target:2,templateId:132303},cards:state});
  state=state.map(x=>({...x,power:x.power+1}));frames.push({cue:{kind:2,source:2,target:2,templateId:132303},cards:state});
 }
 const original=JSON.stringify(frames),group=c.collapseMourntart(frames);
 check(group.length===2&&group[0].cue.massTargets.length===count,'Mourntart includes Nekker trigger announcements '+count);
 check(group[1].cards===state&&group[0].cue.massGrouped&&group[1].cue.massConsumeBoost,'one simultaneous swallow precedes committed counters '+count);
 check(JSON.stringify(frames)===original,'Mourntart history is immutable '+count);
}
for(const id of [113309,112107,112102,113308,200530,200224,152304]){
 const style=c.killEffectStyle(id);
 check((style===1||style===3)===[113309,112107,112102].includes(id),'fire is exclusive to the three burn causes '+id);
 c.activeCue={templateId:999};c.replayFrames=[{cue:{kind:3,templateId:id,deathTargets:[1,2,3]}}];c.prepareReplayTiming();
 check(c.replayFrames[0].cue.floor===(id===112102?2200:[113309,112107].includes(id)?1500:id===113308?1500:740),'grouped destruction keeps its own full duration '+id);
}
const crow=[];
for(let i=0;i<3;i++){
 crow.push({revision:i*2,cue:{kind:2,source:7,target:i+1,templateId:200224},cards:[]});
 crow.push({revision:i*2+1,cue:{kind:3,source:7,target:i+1,templateId:200224},cards:[]});
}
const grouped=c.collapseProjectileDeaths(crow);
check(grouped.length===1&&grouped[0].cue.projectileDeaths&&grouped[0].cue.hitTargets.join(',')==='1,2,3','all lethal Crow projectiles share one arrival');
check(grouped[0].historyFrames.length===6,'every original Crow damage and death remains in history');
const deathwish={cue:{kind:13,source:1,templateId:132316},cards:[]};
check(c.collapseProjectileDeaths([...crow.slice(0,2),deathwish,...crow.slice(2)]).length===3,'Crow grouping does not cross deathwish reactions');
const impacts=[{revision:1,cue:{kind:2,source:7,target:1,audioKind:20},cards:[]},{revision:2,cue:{kind:2,source:7,target:7,audioKind:21},cards:[]}];
check(c.collapseSweeps(impacts)[0].cue.soundRevisions.join(',')==='1,2','damage and boost each retain their native sound');
// Reproduce the GFx stencil rule: overlapping contours XOR and cause striping.
vm.runInContext(`var face={visible:true},cut=new Sprite(),edge=new Sprite(),w=88,h=120,band=.12;
var ramp=[1,2,3,4,5,6],alphas=[1,1,1,1,1,1],noise=Array.from({length:44*60},(_,i)=>((i*73)%255)/254);
var BetaGwentDissolveData144={W:44,H:60};`+extract(dissolve,'render'),c);
for(let step=0;step<20;step++){
 c.render(step/20);const rects=c.cut.graphics.rects;
 for(let i=0;i<rects.length;i++)for(let j=i+1;j<rects.length;j++){
  const [x,y,w,h]=rects[i],[xx,yy,ww,hh]=rects[j];
  if(Math.min(x+w,xx+ww)-Math.max(x,xx)>1e-7&&Math.min(y+h,yy+hh)-Math.max(y,yy)>1e-7)throw Error('overlapping dissolve contours');
 }
 checks++;
}
c.render(1);check(!c.face.visible,'consume and burn finish without a remaining face');
// A second confirmation casts automatic specials directly from the hand.
vm.runInContext(`var ready=true,playing=false,detailOpen=false,pileOpen=false,editingDeck=false,selectingDecks=false,current=1,flags=0,requestId=0;
var controllerMenuOpen=false,nameOpen=false,mulliganConfirm=false,browsingCatalog=false;
var selected=0,keyboardFocusId=0,focusedRow=0,revision=25,controllerInspectBoard=false;
var focusHandAfterReplay=false,focusBoardAfterReplay=false,submitted=[],renders=0,focuses=[];
var playRules={1:{kind:3},2:{kind:1},3:{kind:2},4:{kind:0},5:{kind:0}},cardDetails={1:{typeMask:2},2:{typeMask:2},3:{typeMask:2},4:{typeMask:2},5:{typeMask:4}};
cards=[1,2,3,4,5].map(id=>({id,side:1,zone:8,canPlay:true}));
function canPlaceBefore(){return false;}function canDirectTarget(){return false;}function canPlaceSelected(){return selected===5;}
function render(){renders++;}function submitBoard(event,args){submitted.push({event,args});ready=false;}
function openCardDetail(){}var controller={focusKey:key=>focuses.push(key),focusTag:tag=>focuses.push(tag)};
`+['canAct','controllerQuickSpecial','controllerCardAction','restoreTurnHandFocus'].map(n=>extract(board,n)).join('\n'),c);
for(const id of [1,4]){
 c.ready=true;c.selected=0;c.submitted=[];c.controllerCardAction(id);
 check(c.selected===id&&c.submitted.length===0,'first A selects automatic special '+id);
 check(c.focuses.at(-1)==='battle:hand:card'+id,'first A keeps focus on the same hand card '+id);
 c.controllerCardAction(id);check(c.submitted.length===1&&c.submitted[0].args.join(',')===`25,${id},1`,'second A submits spell without aiming at the board '+id);
 c.controllerCardAction(id);check(c.submitted.length===1,'held/repeated confirmation cannot submit twice '+id);
}
for(const id of [2,3,5]){c.ready=true;c.selected=id;c.submitted=[];c.controllerCardAction(id);check(c.submitted.length===0,'targeted cards and units never auto-cast '+id);}
for(const modal of ['detailOpen','pileOpen','controllerMenuOpen','nameOpen','mulliganConfirm','browsingCatalog']){
 c.ready=true;c.selected=0;c.focusHandAfterReplay=true;c.controllerInspectBoard=true;c[modal]=true;
 check(c.restoreTurnHandFocus()===false&&c.focusHandAfterReplay&&c.controllerInspectBoard,'new turn does not steal '+modal);
 c[modal]=false;check(c.restoreTurnHandFocus()===true&&!c.focusHandAfterReplay&&!c.controllerInspectBoard,'returning to battle restores the hand after '+modal);
}
c.focusHandAfterReplay=true;c.playing=true;check(!c.restoreTurnHandFocus(),'hand return waits for replay completion');c.playing=false;
c.current=2;check(!c.restoreTurnHandFocus(),'hand return waits for the player turn');c.current=1;
check(c.restoreTurnHandFocus()&&!c.restoreTurnHandFocus(),'hand focus is restored exactly once per turn');
vm.runInContext(`var consumedVisualIds={42:true},skin=3,BETA_CARD_ASPECT=17.64/21.46;
var BetaGwentBoardLayout={deck:{1:[1701.5,926.1,125.1,148.9],2:[1701.5,5,125.1,148.9]},grave:{1:[1575.1,926.1,125.1,148.9],2:[1575.1,5,125.1,148.9]}};
`+['betaPilePoint','consumePilePose','consumedTombstone'].map(n=>extract(board,n)).join('\n'),c);
for(const side of [1,2])for(const zone of [16,32]){
 const pose=c.consumePilePose({templateId:142317,power:4,side,zone});
 check(pose.x>1500&&pose.y>=8&&pose.y+pose.height<=1072,'pile consumption stays next to its visible pile '+side+'/'+zone);
 check((zone===16?pose.x>1700:pose.x<1700),'deck and grave consumption use distinct origins '+side+'/'+zone);
}
for(const elapsed of [0,1700,10000,1000000]){c.getTimer=()=>elapsed;check(c.consumedTombstone(42),'consumed identity never reappears due to elapsed time '+elapsed);}
delete c.consumedVisualIds[42];check(!c.consumedTombstone(42),'real resurrection can release consumed identity');
const confirm=extract(board,'drawBetaConfirm');
check(!confirm.includes('no,!mulliganAnswer')&&!confirm.includes('yes,mulliganAnswer'),'confirmation buttons use interaction focus instead of permanent chosen colour');
const report={stage:150,checks,passed:true,actualActionScript:true,nativeGameTested:false};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
