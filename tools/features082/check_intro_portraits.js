'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.resolve(root,process.argv[2]||'BetaGwent/build/release082-rc3');let checks=0;
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let n=1,i=b+1;for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:BetaGwentLeaderPreview|Loader|TimerEvent|Sprite|Object|String|int|Number|void|Boolean|Array|Event)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');}
function check(v,n){assert(v,n);checks++;}
for(const platform of ['nextgen','classic']){
 const source=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentLeaderPreview.as'),'utf8');
 const old=fs.readFileSync(path.join(root,'BetaGwent/build/release082-rc2',platform,'ui/src/BetaGwentLeaderPreview.as'),'utf8');
 function Delegate(){this.ready=false;this.hasFrame=()=>this.ready;}
 const c=vm.createContext({Math,Number,int:v=>v|0,now:500,metadata:{once:true,duration:2.3,frames:56,pages:3},playbackStart:300,loopOrigin:0,waitingForSignal:false,idle:null,shown:null,slots:{},cardId:201743,
  releases:[],removed:[],getTimer:()=>c.now,BetaGwentLeaderPreview:Delegate,addChild(){},releasePage:p=>{c.releases.push(p);delete c.slots[p];},removeEventListener:(event,handler)=>c.removed.push(event),Event:{ENTER_FRAME:'frame'},tick(){}});
 vm.runInContext(['frameAt','waitForVoice','startAt','hasFrame','continueIdle'].map(n=>fn(source,n)).join('\n'),c);
 c.waitForVoice();check(c.frameAt(100000)===0,'queued Queen holds first frame through a long prior voice');c.startAt(6400);check(c.frameAt(6400)===0&&c.frameAt(7550)===28,'shared voice clock drives the original entrance pace');
 check(c.frameAt(12000)===55,'entrance frame index remains bounded');
 c.shown={};c.slots={1:{loader:c.shown},2:{loader:{}}};c.continueIdle();check(c.idle&&!c.idle.ready&&c.releases.join(',')==='2'&&c.hasFrame(),'visible entrance retained until idle page is ready');
 c.idle.ready=true;c.continueIdle();check(!Object.keys(c.slots).length&&c.removed.includes('frame')&&c.hasFrame(),'entrance hands off to a continuing idle movie');
 for(const name of ['releasePage','retire','reap'])check(fn(source,name)===fn(old,name),'deferred native cleanup preserved '+name);
 check(source.includes('getTimer()<Number(failedPages[page])')&&source.includes('failedPages[page]=getTimer()+500'),'transient page failures have bounded retry delay');
 const board=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentBoard.as'),'utf8');let starts=[];
 const b=vm.createContext({int:v=>v|0,introSerial:4,introStart:100,introSkipAt:0,introVoiceSeen:{},leaderIds:[201743,201743],introSideMovies:{1:{startAt:t=>starts.push([1,t])},2:{startAt:t=>starts.push([2,t])}}});
 vm.runInContext(fn(board,'setIntroVoiceStart'),b);
 b.setIntroVoiceStart(3,1,201743,500);check(!starts.length,'stale intro callback ignored');b.setIntroVoiceStart(4,2,201743,800);b.setIntroVoiceStart(4,1,201743,6400);b.setIntroVoiceStart(4,1,201743,6500);
 check(JSON.stringify(starts)==='[[2,800],[1,6400]]','both seats including mirrored Queen start once at their own voice event');
 b.introSkipAt=1;b.introVoiceSeen={};b.setIntroVoiceStart(4,1,201743,9000);check(starts.length===2,'skip cannot restart a portrait');
}
const report={checks,actualActionScript:true,idleHandoff:true,queuedQueenClock:true,nativePlaybackVerified:false};fs.writeFileSync(path.join(build,'intro-portrait-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
