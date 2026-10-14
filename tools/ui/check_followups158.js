'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8'),pad=fs.readFileSync('BetaGwent/ui/src/BetaGwentController.as','utf8');
function extract(source,name){
 const at=source.indexOf('function '+name+'('),start=source.indexOf('{',at);let end=start+1,depth=1;assert(at>=0,name);
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:(Sprite|TextField|MouseEvent|Event|String|Function|Object|Rectangle|void|int|uint|Number|Array|Boolean|BetaGwentLeaderPreview)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
class Graphics{constructor(){this.circles=[];}clear(){}lineStyle(){}drawRect(){}drawRoundRect(){}moveTo(){}lineTo(){}beginFill(){}endFill(){}drawCircle(...v){this.circles.push(v);}}
class Sprite{constructor(){this.graphics=new Graphics();this.children=[];}addChild(c){this.children.push(c);return c;}removeChildAt(i){this.children.splice(i,1);}removeEventListener(){}get numChildren(){return this.children.length;}}
const c=vm.createContext({console,Math,String,Object,Sprite,int:v=>v|0,MouseEvent:{CLICK:'click'}});
// The elemental engine has its own production-code regression (check_elements164).
c.elementCueFloor164=()=>0;c.drawElementCue164=()=>null;
let checks=0;function check(v,n){assert(v,n);checks++;}
vm.runInContext(`var now=200,introStart=100,introSkipAt=0,introInputUntil=0,introSerial=1,introAudioPending=false,introParts=[],introLeaderMovies=[],introLayer=new Sprite();
var BetaGwentUi138={helpLabels:true,intensity:1,chains:true};var actions=0,sends=[],owner={};
function getTimer(){return now;}function send(name,args){sends.push([name,args]);}function trace(){}function uiSound(){}
function state(){return controllerContext();}function invoke(name){controllerCommand(name);}
function getFocus(){return {action(){actions++;}};}
`+['controllerContext','controllerCommand','skipIntro','finishIntro'].map(n=>extract(board,n)).join('\n')+extract(pad,'activate'),c);
for(let i=0;i<10;i++)c.activate();
check(c.actions===0&&c.introSkipAt===200,'A skips intro without activating the underlying mulligan');
check(c.sends.filter(x=>x[0]==='OnBetaGwentAudioIntroCancel').length===1,'repeated A does not repeatedly skip intro');
c.finishIntro();for(let i=0;i<10;i++)c.activate();
check(c.actions===0&&c.introInputUntil===650,'post-intro input guard swallows repeated confirmation');
c.now=700;c.state=()=>({accept:true,replay:false});c.activate();check(c.actions===1,'fresh confirmation works after the guard');
vm.runInContext(`var content=new Sprite(),activeCue={kind:2,templateId:200224,source:7,target:1,attackCount:4,hitTargets:[1,2,3,4],title:''};
var displayedCards={1:{x:600,y:100,width:80,height:100,side:2,zone:1,delta:-4},2:{x:700,y:100,width:80,height:100,side:2,zone:1,delta:-4},3:{x:600,y:300,width:80,height:100,side:2,zone:2,delta:-4},4:{x:600,y:500,width:80,height:100,side:2,zone:4,delta:-4}};
var previousPoses={},departedPoses={},cardDetails={},animations=[],cards=[],skin=3,reducedMotion=false,lastRoundResult=null,flags=0,waves=0,bolts=[];
var BetaGwentFullCatalog={find(){return null;}},BetaGwentSpecialVfx={profile(){return {element:1024,method:1};},tint(e,t){return t;}};
function drawChainCue(){}function drawRecoveryCue(){}function drawWeatherCast(){}function drawBetaHit(){}function drawBoostCue(){}function drawStrike173(){}function strikeTint173(){return 0;}
function cueImpactTime(){return 380;}function poseW(p){return p.width;}function poseH(p){return p.height;}
function poseX(p){return p.x+p.width/2;}function poseY(p){return p.y+p.height/2;}
function rowGeometry(side,row){return {x:500,y:row*100,w:800,h:100};}
function drawSpecialProjectile(fx,sx,sy,tx,ty,profile,tint,delay,branch){bolts.push({tx,ty,profile,tint,delay,branch});}
function drawRowWaves(){waves++;}
`+['drawCrowProjectiles','drawVisualCue'].map(n=>extract(board,n)).join('\n'),c);
c.drawVisualCue();check(c.bolts.length===3&&c.waves===0,'Crow sends one glob to each hit row and no field-wide attack wave');
check(c.bolts.every(b=>b.profile.element===1024&&b.tint===0xD45BFF&&b.delay===380),'Crow uses synchronized purple projectiles');
c.activeCue={kind:13,source:1,target:0,title:''};c.content=new Sprite();c.drawVisualCue();
check(c.content.children.every(s=>s.graphics.circles.length===0),'deathwish has no generic sun marker');
vm.runInContext(`var redraws=0;function render(){redraws++;}function closeControllerMenu(){}function openControllerMenu(){}`+extract(board,'changePresentationOption')+extract(board,'setBoardHelp'),c);
c.changePresentationOption(5)();check(!c.BetaGwentUi138.helpLabels&&c.redraws===1,'help toggle applies immediately to the board');
check(c.sends.some(x=>x[0]==='OnBetaGwentBoardHelp'&&x[1][0]===false),'help preference is sent for persistence');
c.setBoardHelp(true);check(c.BetaGwentUi138.helpLabels,'saved help preference is restored');
vm.runInContext(`var current=2,playing=false,nativeEvents=[];
var _NATIVE_callGameEvent=function(name,args){nativeEvents.push([name,args]);if(name==='OnBetaGwentAudioTick'){now+=487;current=1;}};`
+extract(board,'bridgeClock')+extract(board,'send'),c);
c.send('OnBetaGwentAudioTick',[c.now]);
check(c.nativeEvents.length===2&&c.nativeEvents[1][0]==='OnBetaGwentPerf'&&c.nativeEvents[1][1][1]===487,'UI clock reports the complete planning call even after the turn changes');
console.log(JSON.stringify({checks,actualActionScript:true,nativeGameTested:false}));
