// Run the actual ActionScript replay helpers with bounded display-list stubs.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){
 const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);assert(start>=0,name);
 let depth=1,end=open+1;for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(Sprite|TextField|Event|Error|String|Object|void|int|uint|Number|Array|Boolean|\*)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))')
  .replace(/\s+as\s+(?:Sprite|TextField|MovieClip|DisplayObject|Bitmap|Object|Array|String)\b/g,'');
}
class Sprite{constructor(){this.graphics=new Proxy({},{get:()=>()=>{}});this.children=[];}addChild(s){this.children.push(s);return s;}}
const c=vm.createContext({console,Math,Number,String,Object,Sprite,int:x=>x|0});
vm.runInContext(`var BETA_CARD_ASPECT=17.64/21.46,BetaGwentBoardLayout={leader:{1:[501.8,912.5,146.2,200.2],2:[501.8,-32.7,146.2,200.2]}};
var histories=[],animations=[],labels=[],activeCue={},reducedMotion=false;
function noteHistory(cue,scores,cards){histories.push({cue,scores,cards});}
function panel(parent,x,y,w,h){var s=new Sprite();s.x=x;s.y=y;parent.addChild(s);return s;}
function betaLabel(...a){labels.push(a);}var BetaGwentFonts={TITLE:'title'};
`+['collapseDeathSweeps','noteFrameHistory','betaLeaderRect','drawPassCue','cueMinimumDuration','cueImpactDelay','cueImpactTime'].map(extract).join('\n'),c);
let checks=0;function check(v,n){assert(v,n);checks++;}
const frame=(id,kind=3,source=7)=>({revision:id,cue:{kind,source,target:id,templateId:123,side:2},scores:[id,20-id],cards:[{id,zone:32}]});
for(let count=1;count<=18;count++){
 const frames=Array.from({length:count},(_,i)=>frame(i+1)),before=JSON.stringify(frames);
 const grouped=c.collapseDeathSweeps(frames);check(grouped.length===1,'contiguous deaths share one presentation');
 check(grouped[0].revision===count&&grouped[0].cards===frames[count-1].cards,'use the committed final snapshot');
 check(JSON.stringify(frames)===before,'input snapshots remain unchanged');
 c.histories=[];c.noteFrameHistory(grouped[0]);
 check(c.histories.length===count&&c.histories.every((h,i)=>h.cue.target===i+1),'every original death survives in history');
}
for(const barrier of [frame(90,2),frame(90,11),frame(90,15),frame(90,16),frame(90,6),frame(90,3,8),{...frame(90),cue:{...frame(90).cue,side:1}}]){
 const grouped=c.collapseDeathSweeps([frame(1),frame(2),barrier,frame(3),frame(4)]);
 check(grouped.length===3,'do not cross reaction, resurrection, round or actor barriers');
}
check(c.collapseDeathSweeps([frame(1),frame(1)]).length===2,'repeated victim is a separate event');
for(const side of [1,2]){
 const r=c.betaLeaderRect(side);check(Math.abs(r[3]-r[2]/(17.64/21.46))<=.5,'leader uses ordinary card proportions within pixel rounding');
 check(r[1]>=8&&r[1]+r[3]<=1072,'entire leader stays in the viewport');
 for(const reduced of [false,true]){
  c.reducedMotion=reduced;c.animations=[];c.labels=[];c.activeCue={kind:5,side};const parent=new Sprite();c.drawPassCue(parent);
  check(c.labels[0][1]===(side===2?'Соперник спасовал.':'Вы спасовали.'),'pass explicitly identifies the player');
  check(parent.children.length===1&&!parent.children[0].mouseEnabled&&!parent.children[0].mouseChildren,'pass panel cannot intercept input');
  check(c.animations.length===(reduced?0:1),'reduced motion keeps the label without movement');
 }
}
// Execute the complete production frame transition: fast replay and reduced
// motion must still hold the opponent pass for 900 ms of real time.
vm.runInContext(`
var replayFrames=[],crowns=[0,0],scores=[0,0],enemyHand=0,requestId=0,flags=0;
var focusBoardAfterReplay=false,selectingDecks=false,detailOpen=false,pileOpen=false;
var skin=3,introStart=1,previousTurn=2,animationTempo=1,visualTimeScale=1,fastReplay=false;
var frameAnimationTempo=1,animationRate=1,animationBaseDuration=900;
var FAST_REPLAY_SCALE=.25,MASS_TICK_MS=80,aiTurnShown=false,skipAudio=false,serverRevision=4;
var consumedVisualIds={},playing=false,now=1000,revision=0,mouseReplayBoosted=false;
function releaseReplayMouse(){}
function clearDrag(){}function isMulliganHand(){return false;}function maybeStartIntro(){}
function render(){}function reportUIError(w,e){throw e;}function reportArtwork(){}
function canNextRound(){return false;}function send(){}function aiTurnDelay(){return 0;}
function getTimer(){return now;}var BetaGwentFullCatalog={find(){return null;}};
var BetaGwentUi138={sceneDuration(){return 700;}};
`+extract('showNextFrame')+'\n'+extract('skipReplay'),c);
const state={requestId:0,crowns:[0,0],scores:[15,12],flags:0,current:1,round:2,rowMode:0,requestKind:0,requestMessage:'',requestCards:[],cards:[],cue:{kind:5,side:2,duration:380,title:'Pass'}};
for(const reduced of [false,true])for(const fast of [false,true])for(const tempo of [1,1.5,2]){
 c.reducedMotion=reduced;c.fastReplay=fast;c.animationTempo=tempo;c.replayFrames=[state,{...state,cue:{kind:0}}];
 c.showNextFrame();check(c.frameDeadline-c.now>=900,'opponent pass has a readable hold at every speed');
 check(c.scores===state.scores&&c.flags===0,'pass does not manufacture a round result');
}
c.histories=[];c.playing=true;c.consumedVisualIds={15:1001};
c.replayFrames=[...c.collapseDeathSweeps([frame(1),frame(2),frame(3)]),{...state,cue:{kind:0}}];
c.skipReplay();check(c.histories.filter(h=>h.cue.kind===3).length===3,'skip preserves every grouped death in history');
check(Object.keys(c.consumedVisualIds).length===0&&!c.playing,'skip clears consume tombstones and reaches final state');
for(const tempo of [1,1.5,2])for(const rate of [1,4]){
 c.reducedMotion=false;c.activeCue={kind:11};c.frameAnimationTempo=tempo;c.animationRate=rate;c.animationBaseDuration=900/tempo;
 check(Math.abs(c.cueImpactDelay()-390/tempo/rate)<1e-8,'consume audio arrives with the meal');
 check(Math.abs(c.cueImpactTime()-390)<1e-8,'consume effects share the source clock');
}
const draw=extract('drawCards');
check(draw.includes('|| isConsumeVictim(oldId)'),'consume avoids a duplicate generic departure');
check(draw.indexOf('delete consumedVisualIds[c.id]')<draw.indexOf('if(consumedTombstone(c.id)'),'explicit resurrection releases the tombstone before drawing');
vm.runInContext(`var displayedCards={},previousPoses={4:{id:4,templateId:112101,power:8,side:2,zone:1,x:120,y:400,width:104,height:127}},cardSprites={},painted=[];
var CONSUME_TOMBSTONE_MS=900;function setTimeout(){}function renderAfterTombstone(){}
function paintPlacementCard(...args){painted.push(args);}function drawMassConsume(){throw Error('unexpected mass consume');}var bloods=[];function getTimer(){return 0;}function drawBloodConsume(fx,pose,d){bloods.push([pose,d]);}var BETA_CARD_ASPECT=17.64/21.46;
`+['poseW','poseH','drawConsumeCue'].map(extract).join('\n'),c);
c.animations=[];c.activeCue={kind:11,target:4,targetView:{templateId:112101,power:8,side:2,zone:1}};
c.drawConsumeCue(new Sprite(),{x:600,y:400,width:104,height:127});
check(c.bloods.length===1&&c.bloods[0][0]===c.previousPoses[4],'consume dissolves the complete previous public card face');
check(c.bloods[0][1]===0&&c.consumedVisualIds[4]>0,'consume starts at once and tombstones the victim');
const report={stage:140,checks,actualActionScript:true,nativeGameTested:false,sourceSha256:crypto.createHash('sha256').update(source).digest('hex')};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
