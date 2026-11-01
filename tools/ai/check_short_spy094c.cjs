// Independent resource contract for a drawing spy in a lost optional round.
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const {createRuntime}=require('./beta_js092/session.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]));
const fixtures=[16,18].map(t=>JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures',`short-spy-concession094c-t${t}.json.gz`)))));
let checks=0,peakPlays=0;const failures=[],cases=[];
function check(ok,name){checks++;if(!ok)failures.push(name);}
const load=f=>runtime.deserialize(JSON.parse(JSON.stringify(f.state)));
const publicState=g=>JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId});
const proto=runtime.newSession().constructor.prototype,play=proto.AiSimPlay;let calls=0;
proto.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
function prepare(g){const before=publicState(g);let ticks=0;
 while(true){calls=0;const ready=g.AiPreparationStep();peakPlays=Math.max(peakPlays,calls);
  check(calls<=1,'one simulated action per preparation callback');
  check(publicState(g)===before,'preparation preserves live cards/match/RNG');
  if(ready)return;if(++ticks>10000)throw Error('Preparation stalled');}
}
function commit(g){for(let i=0;i<4;i++){if(g.OpponentStep())return true;prepare(g);}return false;}
for(const [f,index] of fixtures.map((f,i)=>[f,i]))for(const strength of [3,4])for(const damp of [0,40,70])for(const staged of [false,true]){
 runtime.host.strength=strength;runtime.host.matchStrength=[strength,strength];
 const g=load(f);g.aiSimDamp=damp;const hand=g.CountLocation(2,8),spy=g.FindCard(40),leaderBefore=g.LeaderAvailable(2);
 check(g.Snapshot().roundNumber===1&&g.Snapshot().playerOne.crowns===0&&g.Snapshot().playerTwo.crowns===0,'round can be conceded without losing match');
 check(g.Score(2)<g.Score(1)&&hand===2-index&&hand<g.CountLocation(1,8),'public short-hand deficit fixture');
 check(g.AiSpyConcessionWindow(),'short-hand conversion is considered independently of a one-card catch');
 if(staged)prepare(g);const logs=[];runtime.host.log=s=>logs.push(s);
 try{check(commit(g),'spy decision commits');}finally{runtime.host.log=null;}
 const converted=spy.Snapshot().locationMask!==8;
 check(converted,'convert drawing spy before spending remaining answer/leader');
 if(converted){
  check(g.CountLocation(2,8)===hand,'actual draw preserves hand count');
  check(Boolean(g.LeaderAvailable(2))===Boolean(leaderBefore),'conversion preserves unused leader');
  check(g.Pass(1),'opponent may take cheapest reply: pass');
  check(commit(g),'concession resolves after opposing pass');
  check(g.CountLocation(2,8)===hand&&g.Snapshot().playerTwo.hasPassed,'do not spend another hand card catching the gifted points');
  check(g.Snapshot().playerOne.crowns===1&&!g.Snapshot().matchWinnerMask,'optional concession keeps match alive');
 }
 cases.push({index,strength,damp,staged,converted,handBefore:hand,handAfter:g.CountLocation(2,8),logs:logs.filter(s=>/event=(SELECT|SPY_FORECAST|SPY_CONCESSION_OPTION)/.test(s))});
}
runtime.host.strength=4;runtime.host.matchStrength=[4,4];
for(const f of fixtures)for(const scenario of ['fresh','mandatory','passed','ahead','hidden-trap','equal-short-hand']){
 const g=load(f);
 if(scenario==='fresh')g.aiRoundHandTwo=g.CountLocation(2,8);
 if(scenario==='mandatory'){g.match.roundNumber=2;g.match.playerOne.crowns=1;}
 if(scenario==='passed')g.match.playerOne.hasPassed=true;
 if(scenario==='ahead'){const c=g.live.find(c=>c.Snapshot().positionPlayerId===2&&(c.Snapshot().locationMask&7));c.power.SetCurrentPair(c.Snapshot().power.currentPower+200,c.Snapshot().power.armor);}
 if(scenario==='hidden-trap'){const c=g.live.find(c=>c.Snapshot().positionPlayerId===1&&(c.Snapshot().locationMask&7));c.cardState.tokenMask|=8;}
 if(scenario==='equal-short-hand'){const c=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8);c.Move(1,512,0);}
 check(!g.AiSpyConcessionWindow(),'strict recovery retained: '+scenario);
}
for(const f of fixtures){const outcomes=[];
 for(const hidden of [false,true]){const g=load(f);g.aiSimDamp=40;
  if(hidden)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&[8,16].includes(s.locationMask)&&(s.tokenMask&64)===0)c.cardState.runtimeTemplate.templateId=112405;}
  const logs=[];runtime.host.log=s=>logs.push(s);try{commit(g);}finally{runtime.host.log=null;}
  outcomes.push(logs.filter(s=>/event=(SELECT|SPY_FORECAST|SPY_CONCESSION_OPTION)/.test(s)));
 }
 check(JSON.stringify(outcomes[0])===JSON.stringify(outcomes[1]),'decision ignores true opposing hidden identities');
}
proto.AiSimPlay=play;
const report={fingerprint:runtime.fingerprint,checks,failures,peakPlays,cases,actualHistoricalFixtures:true,actualWitcherScript:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({fingerprint:runtime.fingerprint,checks,failures,peakPlays,cases:cases.length}));if(failures.length)process.exitCode=1;
