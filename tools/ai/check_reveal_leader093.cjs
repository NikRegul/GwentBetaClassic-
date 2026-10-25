// Four reveals through the actual leader path, beyond the two-card Alchemist cases.
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs'),{personality}=require('./beta_js092/profiles.cjs');
const {BetaTurnController}=require('./beta_js092/controller.cjs');
const runtime=createRuntime(path.resolve(process.argv[2])),records=[];let checks=0;
const check=(v,n)=>{checks++;assert(v,n);};
function add(g,id,zone,index,side){const r={v:0};g.registry.Allocate(r);const c=runtime.newCard();c.Setup(g,r.v,id,side,zone,index);g.registry.Put(r.v,c);g.live.push(c);return c;}
function setup(){
 const g=runtime.newSession();g.externalPolicyMask=3;g.InitializeWithPresets(72,72);g.externalPolicyMask=0;
 for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.pendingCard=g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;
 const m=g.match;m.roundNumber=3;m.currentPlayerId=2;m.roundActive=m.turnActive=true;m.playerOne.crowns=m.playerTwo.crowns=1;m.playerOne.hasPassed=m.playerTwo.hasPassed=false;
 m.results.push({roundNumber:1,winnerMask:0x101,scoreOne:20,scoreTwo:10},{roundNumber:2,winnerMask:0x202,scoreOne:10,scoreTwo:20});
 add(g,200163,64,0,2);const own=[add(g,112405,8,0,2),add(g,112101,8,1,2)];
 const enemy=Array.from({length:4},(_,i)=>add(g,112405,8,i,1));
 const golems=Array.from({length:3},(_,i)=>add(g,132407,16,i,2));add(g,112405,1,0,1);
 return {g,own,enemy,golems};
}
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 runtime.host.strength=strength;runtime.host.matchStrength=[strength,strength];const {g,own,enemy,golems}=setup();g.aiSimDamp=damp;
 check(g.UseLeader(2),'Voorhis may use actual leader path');check(!g.IsFatal()&&!g.IsPending(),'four reveals finish');
 check(enemy.every(c=>(c.Snapshot().tokenMask&64)!==0),'all four enemy cards revealed');
 check(own.every(c=>(c.Snapshot().tokenMask&64)===0),'no useless own disclosure');
 check(golems.every(c=>(c.Snapshot().locationMask&7)!==0),'all three distinct golems enter');
 records.push({mode:'ordinary',strength,damp,reveals:4,golems:3});
}
const proto=runtime.newSession().constructor.prototype;
for(const n of ['AiMulligan','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','AiAbilityChoiceValue','AiAdjacencyIndex'])proto[n]=()=>{throw Error('Ordinary selector forbidden: '+n);};
for(const profile of ['p_Nilfgaard_Practice','ch_fac_skellige_1']){
 const {g,own,enemy,golems}=setup();g.externalPolicyMask=3;
 // Exhaust ordinary hand bodies so this is the leader's real search/replay path.
 for(const c of own)c.Move(2,512,0);
 const controller=new BetaTurnController(runtime,personality(profile),{now:()=>0});controller.start(g);let count=0;
 while(!controller.finished){controller.step();assert(++count<20000);}
 check(!g.IsFatal()&&!g.IsPending(),'original leader search/replay completes');
 check(enemy.every(c=>(c.Snapshot().tokenMask&64)!==0),'original leader reveals all four opposing cards');
 check(golems.every(c=>(c.Snapshot().locationMask&7)!==0),'original leader deploys all three distinct golems');
 records.push({mode:'Classic',profile,callbacks:count,reveals:4,golems:3});
}
const report={checks,records,fingerprint:runtime.fingerprint,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
