// Execute the production AS layout/history/hold methods without packaging a menu.
'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name,text=source){
 if(typeof text!=='string')text=source;
 const start=text.indexOf('function '+name+'('),open=text.indexOf('{',start);let end=open+1,depth=1;
 if(start<0)throw Error(name);
 for(;depth;end++){if(text[end]==='{')depth++;if(text[end]==='}')depth--;}
 return text.slice(start,end).replace(/:(String|Function|Object|void|int|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
const b=vm.createContext({Math,Number,console});
const helper=fs.readFileSync('BetaGwent/ui/src/BetaGwentUi138.as','utf8');
const cardAspect=source.match(/BETA_CARD_ASPECT\s*:\s*Number\s*=\s*([0-9.]+)\s*\/\s*([0-9.]+)/);
if(!cardAspect)throw Error('Production card aspect ratio is missing');
vm.runInContext(`var actionHistory=[],historyScores=[0,0],playing=true,aiPauseIndex=2,aiTurnShown=false,reducedMotion=false;
var cards=[],displayedCards={},departedPoses={},BetaGwentFullCatalog={find(){return null;}};
var BETA_CARD_ASPECT=${Number(cardAspect[1])/Number(cardAspect[2])},heldPileMask=0,heldPileRequest=false,revision=10,pileView=null,pileOpen=false,draws=0;
var ready=true,detailOpen=false,controllerMenuOpen=false,nameOpen=false,sends=[],renders=0,focusReads=0,introStart=0,introInputUntil=0;
var previewLayer={numChildren:0},controller={getFocus(){focusReads++;}};
function int(v){return v|0;} function canInspectPile(){return ready&&!playing;}
function closePileView(){pileView=null;pileOpen=false;}
function closeCardDetail(){detailOpen=false;} function render(){renders++;}
function send(name,args){sends.push({name,args});} function drawPileView(){draws++;}
`+extract('publicCard',helper)+'\n'+extract('view',helper)+'\nvar BetaGwentUi138={publicCard,view};\n'+
 ['safeHistoryCard','recordHistoryDetails','noteHistory','historyLine','aiTurnDelay','overviewLayout','abilityOverviewLayout','inspectPile','beginPileView','finishPileView'].map(extract).join('\n'),b);
// This is the unmodified hold branch from controllerCommand, before unrelated commands.
vm.runInContext(extract('controllerCommand').split('if(name=="trace")')[0]+'}',b);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
for(let n=1;n<=60;n++){
 const l=b.abilityOverviewLayout(n);
 check(l.rows<=3&&l.cols*l.rows>=n,'all choices fit one page '+n);
 check(l.blockH<=704&&l.w>0&&l.h>0,'choices stay above footer '+n);
 check(l.cols*l.w+(l.cols-1)*18<=1380,'choices stay left of preview '+n);
 if(n<=10)check(l.rows<=2,'small sets keep familiar two rows '+n);
 if(n>=19&&n<=40)check(l.rows===3&&l.w>=80,'large deck uses readable three rows '+n);
}
b.noteHistory({title:'Same card',kind:1},[5,0]);
b.noteHistory({title:'Same card',kind:1},[10,0]);
check(b.actionHistory.length===2,'consecutive identical cards are separate events');
b.noteHistory({title:'Frost',kind:2,source:0,row:1},[10,2]);
b.noteHistory({title:'damage',kind:2,source:7,row:0},[10,4]);
check(b.actionHistory[1].end[1]===0,'weather is not attributed to preceding card');
check(b.historyLine(b.actionHistory[0]).includes('+4'),'weather entry includes all tick deltas');
for(let i=0;i<80;i++)b.noteHistory({title:'play '+i,kind:1},[10+i,4]);
check(b.actionHistory.length===64&&b.actionHistory[0].title==='play 79','history keeps latest 64');
for(const reduced of [false,true])for(let setting=1;setting<=4;setting++){
 b.reducedMotion=reduced;b.aiPauseIndex=setting;
 check(b.aiTurnDelay({current:2,cue:{kind:1}})===(setting-1)*400,'AI pause independent of reduced effects '+setting+'/'+reduced);
}
b.aiTurnShown=true;check(b.aiTurnDelay({current:2,cue:{kind:1}})===0,'no repeat pause within turn');
b.aiTurnShown=false;check(b.aiTurnDelay({current:1,cue:{kind:1}})===0&&b.aiTurnDelay({current:2,cue:{kind:2}})===0,'no pause before player or effect');
b.playing=false;
for(const [mask,side,zone] of [[1,1,32],[2,1,16],[3,2,32]]){
 b.controllerCommand('pileHold',{mask});
 check(b.sends.at(-1).args.join(',')===[10,side,zone].join(','),'trigger opens expected pile '+mask);
 b.beginPileView(10,side,zone,0);b.finishPileView(10);
 check(b.pileOpen,'held pile opens '+mask);
 b.detailOpen=true;b.controllerCommand('pileHold',{mask:0});
 check(!b.pileOpen&&!b.detailOpen&&b.heldPileMask===0,'release closes pile and detail '+mask);
}
b.controllerCommand('pileHold',{mask:2});b.controllerCommand('pileHold',{mask:0});
b.beginPileView(10,1,16,0);b.finishPileView(10);
check(!b.pileOpen,'late native response cannot reopen after release');
b.controllerCommand('pileHold',{mask:1});b.controllerCommand('pileHold',{mask:3});
b.beginPileView(10,1,32,0);b.finishPileView(10);
check(!b.pileOpen,'old trigger response cannot replace newer pile');
b.beginPileView(10,2,32,0);b.finishPileView(10);check(b.pileOpen,'latest trigger response opens');
b.controllerCommand('pileHold',{mask:0});b.inspectPile(1,16);b.beginPileView(10,1,16,0);b.finishPileView(10);
b.controllerCommand('pileHold',{mask:0});check(b.pileOpen,'unheld manual pile is not closed by unrelated trigger release');
b.ready=false;const count=b.sends.length;b.controllerCommand('pileHold',{mask:1});
check(b.sends.length===count,'disabled inspection sends no request');
const report={stage:127,checks,actualActionScript:true,nativeControllerTested:false,releaseBuildStarted:false};
fs.writeFileSync('docs/evidence/followups-ui127.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
