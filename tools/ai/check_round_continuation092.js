// Real replay plus bounded public-reply continuations with changed targets.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
ctx.saved=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/round-engine-pass092.json.gz'))));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:g.random.DrawCount(),request:g.requestId});}
const cases=[];
for(const strength of [4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 bridge.load(saved.state);const g=active;
 check(g.CountLocation(2,8)===9&&g.Score(1)===17&&g.Score(2)===0,'real lost-game position reconstructed '+strength);
 const engine=g.FindCard(12),logs=[];Host.log=s=>logs.push(s);
 check(g.OpponentStep()&&!g.IsFatal()&&!g.IsPending(),'real replay decision finishes '+strength);Host.log=null;
 check(!g.Snapshot().playerTwo.hasPassed,'viable remaining engine package prevents premature concession '+strength);
 check((engine.Snapshot().locationMask&7)!==0,'real replay installs replacement engine '+strength);
 cases.push({strength,pass:false,selected:logs.filter(s=>/event=SELECT/.test(s))});
}
const simPlay=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,peak=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...a){calls++;return simPlay.apply(this,a);};
for(const strength of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=0;g.aiStartingDeckOne=[112405];
 add(g,112405,1,0,2,9);add(g,112405,1,0,1,5);
 const own=[add(g,112405,8,0,2,8),add(g,112405,8,1,2,4),add(g,112405,8,2,2,2),add(g,113309,8,3,2),add(g,112405,8,4,2,3)];
 add(g,112405,8,0,1,20).AddTokens(64);
 const ids=own.map(c=>c.Snapshot().instanceId),values=own.map(c=>g.AiExactTempo(c));
 const response=new CBetaGwentPublicResponseAI();response.Initialize(g,1);
 const job=new CBetaGwentAIReplyTree097();job.Initialize(g,ids[4],ids,values,response);const before=state(g);
 let ticks=0;while(true){calls=0;const done=job.Step();peak=Math.max(peak,calls);check(calls<=1,'one simulated play per callback '+strength);if(done)break;if(++ticks>100)throw Error('reply search stalled');}
 check(state(g)===before,'reply search preserves source state and RNG '+strength);
 check(job.branches===1&&job.follows>0,'real revealed reply and continuations resolved '+strength);
 check(job.continuationIds[0]===ids[3],'newly profitable Scorch enters fixed shortlist beyond old prefix '+strength);
 check(job.branchScores[0]>0,'exact continuation confirms improved reply target '+strength);
 cases.push({strength,continuation:job.continuationIds[0],branchScores:job.branchScores.slice(),follows:job.follows,ticks});
}
CBetaGwentDuelSession.prototype.AiSimPlay=simPlay;
globalThis.result={checks,cases,peakSearchPlays:peak,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.result};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));
console.log(JSON.stringify(report));
