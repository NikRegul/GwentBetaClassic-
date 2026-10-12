// Run the real replay timing policy without exporting or deploying a menu.
'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){
 const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);let depth=1,end=open+1;
 if(start<0)throw Error(name);
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(String|Object|void|int|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
}
const c=vm.createContext({Math,Number,BetaGwentVisualTimings:{FROST_INTRO:1,FOG_INTRO:1,RAIN_INTRO:1}});
const autoMass=/AUTO_MASS_CONSUME:Boolean=true/.test(source);
vm.runInContext('var replayFrames=[],animationTempo=1,visualTimeScale=1,MASS_TICK_MS=70,AUTO_MASS_CONSUME='+autoMass+';'+extract('cueMinimumDuration')+extract('prepareReplayTiming'),c);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
function cue(kind,source=0,row=1){return {cue:{kind,source,row,duration:260,target:1}};}
for(const tempo of [1,2]){
 c.animationTempo=tempo;c.replayFrames=[cue(2,0,1),cue(2,0,2),cue(2,0,4)];c.prepareReplayTiming();
 check(c.replayFrames.every(f=>f.cue.floor===930),'all three weather rows have the same hit duration at tempo '+tempo);
 check(c.visualTimeScale===1/tempo,'only the chosen tempo changes animation speed '+tempo);
 c.replayFrames=Array.from({length:40},()=>cue(2,99));c.prepareReplayTiming();
 check(c.replayFrames.every(f=>f.cue.floor===930),'long damage sequence never accelerates subsequent hits '+tempo);
 check(c.visualTimeScale===1/tempo,'batch size does not compress damage '+tempo);
}
// Stage 131: automatic mass-consume speed-up is off; the player presses Speed up instead.
c.animationTempo=1;c.replayFrames=[cue(11,10),...Array.from({length:6},(_,i)=>cue(2,20+i)),cue(11,10),...Array.from({length:6},(_,i)=>cue(2,20+i)),cue(11,10),cue(2,0,4)];
c.prepareReplayTiming();
if(autoMass){
 check(c.replayFrames[0].cue.massTargets.length===3,'mass consume survives six intervening Nekker reactions');
 check(c.replayFrames.slice(1,-1).every(f=>f.cue.massFollow&&f.cue.floor===70),'mass consume bookkeeping stays fast');
}else{
 check(c.replayFrames.every(f=>!f.cue.massFollow&&!f.cue.massTargets),'no automatic mass-consume merge');
 check(c.replayFrames.filter(f=>f.cue.kind===11).every(f=>f.cue.floor===c.cueMinimumDuration(11)),'every consume keeps its normal duration');
 check(c.replayFrames.filter(f=>f.cue.kind===2).every(f=>f.cue.floor===930),'Nekker reactions keep their normal duration');
}
check(!c.replayFrames.at(-1).cue.massFollow&&c.replayFrames.at(-1).cue.floor===930,'weather after consumes keeps normal speed');
c.replayFrames=[cue(11,10),cue(11,11),cue(11,10),cue(1,10),cue(11,10)];c.prepareReplayTiming();
check(c.replayFrames.every(f=>!f.cue.massFollow),'different consumers and card plays never merge into one consume');
check(/function accelerateReplay\(/.test(source)&&/drawBetaHint\(fastReplay\?"Пропустить":"Ускорить"/.test(source),'Speed up control replaces automatic acceleration');
const report={stage:126,checks,actualActionScript:true,nativeVisualVerified:false,releaseBuildStarted:false};
fs.writeFileSync('docs/evidence/timing126.json',JSON.stringify(report,null,2)+'\n');
