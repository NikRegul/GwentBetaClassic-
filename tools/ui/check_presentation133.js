// Execute the production AS timing and intro methods; no SWF build/deployment.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){
 const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);let depth=1,end=open+1;
 if(start<0)throw Error(name);for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(String|Object|void|int|Number|Array|Boolean|Event|MouseEvent)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
}
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
const c=vm.createContext({Math,int:x=>x|0,Number,String,getTimer:()=>c.now,MouseEvent:{CLICK:1},BetaGwentTextLanguage:{assign(f,v){if(f)f.text=v;},track(){},forget(){}}});
vm.runInContext(`var now=100,playing=true,fastReplay=false,FAST_REPLAY_SCALE=.25,
 animationRate=1,animationOffset=0,animationStarted=0,animationBaseDuration=700,frameAnimationTempo=1,
 frameDuration=700,frameDeadline=700,audioCueAt=400,replayHint={text:'УСКОРИТЬ'},reducedMotion=false,
 activeCue={kind:1},skipCount=0,renderCount=0;
 function skipReplay(){skipCount++;}function render(){renderCount++;}
 `+['retimeReplay','accelerateReplay','cueImpactDelay','collapseSweeps'].map(extract).join('\n'),c);
const before=c.animationOffset+(c.now-c.animationStarted)*c.animationRate;
c.accelerateReplay();
check(c.frameDeadline===250&&c.audioCueAt===175,'accelerating active frame rescales pending sound before frame ends');
check(c.animationOffset+(c.now-c.animationStarted)*c.animationRate===before,'movement progress stays continuous at acceleration');
check(c.renderCount===0&&c.replayHint.text==='ПРОПУСТИТЬ','acceleration preserves existing sprites and changes the hint');
c.now=175;
check(c.animationOffset+(c.now-c.animationStarted)*c.animationRate===400,'projectile and number impact meet the sound at virtual 400 ms');
c.retimeReplay(2/3);check(c.audioCueAt===175,'already due audio is not delayed by tempo change');
c.audioCueAt=0;c.retimeReplay(2);check(c.audioCueAt===0,'played audio is never rearmed');
c.accelerateReplay();check(c.skipCount===1,'second acceleration command skips replay');
function frame(kind,source,target){return {cue:{kind,source,target,title:'hit',attackCount:1},cards:[],revision:target};}
for(const barrier of [3,8,9,24,25,26,5,6]){
 const input=[frame(2,10,1),frame(barrier,20,2),frame(2,10,3)];
 check(c.collapseSweeps(input).length===3,'sweep keeps semantic barrier '+barrier);
}
check(c.collapseSweeps([frame(2,10,1),frame(2,20,2),frame(2,10,3)]).length===1,'sweep still groups separate targets with power reactions');
check(c.collapseSweeps([frame(2,10,1),frame(2,10,1)]).length===2,'repeated hits on one target remain separate');
vm.runInContext(`var introStart=100,introSkipAt=0,introSerial=7,introAudioPending=true,
 INTRO_MS=4600,INTRO_TIMEOUT_MS=30000,introParts=[],sent=[],
 introLayer={numChildren:0,alpha:1,mouseEnabled:true,removeEventListener(){},graphics:{clear(){}}};
 function send(name,args){sent.push({name,args});}
 `+['setIntroAudioState','skipIntro','finishIntro','animateIntroBody'].map(extract).join('\n'),c);
c.now=5000;c.animateIntroBody(null);
check(c.introStart===100&&c.introSkipAt===0&&c.introLayer.alpha===1,'long voice keeps introduction visible beyond old 4.6-second cutoff');
c.setIntroAudioState(6,false);check(c.introAudioPending,'stale audio acknowledgement cannot finish current intro');
c.setIntroAudioState(7,false);c.animateIntroBody(null);check(c.introSkipAt===5000,'completed voices start the final fade');
c.now=5380;c.animateIntroBody(null);check(c.introStart===0&&!c.introLayer.mouseEnabled,'mulligan unlocked only after audio and fade');
c.introStart=1;c.introSkipAt=0;c.introAudioPending=true;c.now=1;c.skipIntro(null);
check(c.introSkipAt===1&&!c.introAudioPending&&c.sent.at(-1).name==='OnBetaGwentAudioIntroCancel','skip at movie start cancels leader voices without zero-clock trap');
c.introStart=100;c.introSkipAt=0;c.introAudioPending=true;c.now=30100;c.animateIntroBody(null);
check(c.introStart===0,'broken bridge cannot leave permanent intro overlay');
check(source.includes('animationBaseDuration-70/frameAnimationTempo')&&source.includes('cueImpactDelay()*animationRate'),'real animation loop shares virtual timing for movement and counters');
const report={checks,actualActionScript:true,nativeGameTested:false,releaseBuildStarted:false,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as')).digest('hex')};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
