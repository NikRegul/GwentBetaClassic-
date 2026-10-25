'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const {createRuntime}=require('./beta_js092/session.cjs');
const runtime=createRuntime(path.resolve(process.argv[2])),observe=process.argv.includes('--observe');
const fixture=name=>JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures',name+'093c.json.gz'))));
const spyFixture=fixture('spy-concession'),leaderFixture=fixture('bran-continuation');
const load=f=>runtime.deserialize(JSON.parse(JSON.stringify(f.state)));
let checks=0,peakPlays=0;const failures=[],cases=[];
function check(ok,name){checks++;if(!ok){failures.push(name);if(!observe)throw Error(name);}}
const publicState=g=>JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId});
const proto=runtime.newSession().constructor.prototype,play=proto.AiSimPlay;let calls=0;
proto.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
function prepare(g){const before=publicState(g);let ticks=0;
 while(true){calls=0;const ready=g.AiPreparationStep();peakPlays=Math.max(peakPlays,calls);
  check(calls<=1,'preparation keeps one simulated card/leader play per callback');
  check(publicState(g)===before,'preparation preserves live match/cards/RNG');
  if(ready)return ticks;if(++ticks>10000)throw Error('Preparation stalled');}
}
function commit(g){for(let i=0;i<4;i++){if(g.OpponentStep())return true;prepare(g);}return false;}
for(const strength of [3,4])for(const damp of [0,40,70])for(const staged of [false,true]){
 runtime.host.strength=strength;runtime.host.matchStrength=[strength,strength];const g=load(spyFixture);g.aiSimDamp=damp;
 const spy=g.live.find(c=>c.TemplateId()===122203&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8),hand=g.CountLocation(2,8);
 check(Boolean(spy)&&hand===4&&g.CountLocation(1,8)===4,'historical developed first round has four cards each');
 check(typeof g.AiSpyConcessionWindow==='function'&&g.AiSpyConcessionWindow(),'a developed optional round permits a hand-preserving concession');
 if(staged)prepare(g);const logs=[];runtime.host.log=s=>logs.push(s);let ok;
 try{ok=commit(g);}finally{runtime.host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'actual spy decision resolves');
 const played=spy.Snapshot().locationMask!==8;
 check(played,'convert the spy before committing another hand card');
 check(g.CountLocation(2,8)===hand,'real draw keeps the complete hand');
 if(played){check(g.Pass(1),'opponent may take the proposed cheap pass');check(commit(g),'our concession resolves');
  check(g.Snapshot().playerTwo.hasPassed&&g.CountLocation(2,8)===hand,'post-spy policy concedes without spending a catch-up card');
  check(g.Snapshot().playerOne.crowns===1&&g.Snapshot().playerTwo.crowns===0&&!g.Snapshot().matchWinnerMask,'conceding the optional round keeps the match alive');}
 cases.push({kind:'historical-spy',strength,damp,staged,played,hand:g.CountLocation(2,8),logs:logs.filter(s=>/event=(SELECT|PASS|SPY_CONCESSION_OPTION)/.test(s))});
}
runtime.host.strength=4;runtime.host.matchStrength=[4,4];
for(const scenario of ['fresh-opening','smaller-hand','must-survive','already-passed','too-short','already-ahead']){
 const g=load(spyFixture);
 if(scenario==='fresh-opening')g.aiRoundHandTwo=g.CountLocation(2,8);
 if(scenario==='smaller-hand'){const c=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===16);c.Move(1,8,g.CountLocation(1,8));}
 if(scenario==='must-survive'){g.match.roundNumber=2;g.match.playerOne.crowns=1;}
 if(scenario==='already-passed')g.match.playerOne.hasPassed=true;
 if(scenario==='too-short'){const c=g.live.find(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8);c.Move(2,512,0);}
 if(scenario==='already-ahead'){const c=g.live.find(c=>c.Snapshot().positionPlayerId===2&&(c.Snapshot().locationMask&7));const s=c.Snapshot();c.power.SetCurrentPair(s.power.currentPower+50,s.power.armor);}
 check(typeof g.AiSpyConcessionWindow==='function'&&!g.AiSpyConcessionWindow(),'strict recovery retained outside the concession plan: '+scenario);
}
for(const staged of [false,true]){
 const g=load(leaderFixture);g.aiSimDamp=40;const leader=g.Leader(2),id=leader.Snapshot().instanceId;
 const corsair=g.live.find(c=>c.TemplateId()===200145&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8);
 const before=g.AiExactTempo(corsair),shadow=g.AiSimClone();
 check(shadow.AiSimPlay(id)!==-2147483647&&shadow.AiSimSkipTurn(),'independent leader then neutral reply is legal');
 const after=shadow.AiSimPlay(corsair.Snapshot().instanceId);check(after>before,'actual discard setup improves the following resurrection, not just printed leader power');
 check(typeof g.AiLeaderSequencePlanning==='function'&&g.AiLeaderSequencePlanning(),'leader may evaluate its own continuation');
 if(staged){prepare(g);check(g.aiPreparedUpliftIds.includes(id),'prepared leader continuation is available to the same scorer');}
 const logs=[];runtime.host.log=s=>logs.push(s);try{check(commit(g),'leader comparison commits a legal action');}finally{runtime.host.log=null;}
 check(logs.some(s=>s.includes('event=LEADER_SEQUENCE')),'real policy evaluates the enabled hand continuation');
 cases.push({kind:'historical-leader',staged,before,after,sequence:logs.filter(s=>/event=(LEADER_SEQUENCE|LEADER_OPTION|SELECT)/.test(s))});
}
// Changing unseen opposing identities cannot change either new public plan.
for(const f of [spyFixture,leaderFixture]){
 const rows=[];
 for(const changed of [false,true]){const g=load(f);if(changed)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&[8,16].includes(s.locationMask)&&(s.tokenMask&64)===0)c.cardState.runtimeTemplate.templateId=112405;}
  const logs=[];runtime.host.log=s=>logs.push(s);try{commit(g);}finally{runtime.host.log=null;}
  rows.push(logs.filter(s=>/event=(SELECT|LEADER_SEQUENCE|SPY_CONCESSION_OPTION)/.test(s)));
 }
 check(JSON.stringify(rows[0])===JSON.stringify(rows[1]),'new planning ignores private opposing hand/deck identities');
}
proto.AiSimPlay=play;
const report={fingerprint:runtime.fingerprint,checks,failures,cases,peakPlays,actualHistoricalFixtures:true,actualWitcherScript:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({fingerprint:report.fingerprint,checks,failures,peakPlays,cases:cases.length}));if(failures.length)process.exitCode=1;
