'use strict';
// Exact public effects before the next AI turn, and free end-turn catches.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const snapshot=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);let checks=0;
const ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.seatIndex=1;Host.random=()=>.37;
function check(v,n){if(!v)throw Error(n);globalThis.checks=(globalThis.checks||0)+1;}
function add(g,id,side,zone,power,armor=0){const key={v:0};g.registry.Allocate(key);const c=new CBetaGwentDuelCard();c.Setup(g,key.v,id,side,zone,g.CountLocation(side,zone));c.power.SetCurrentPair(power,armor);g.registry.Put(key.v,c);g.live.push(c);return c;}
function blank(p){const g=new CBetaGwentDuelSession();g.InitializeWithPresets(54,p);for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.pendingChoice=false;g.pendingPileChoice=false;g.pendingRow=false;g.pendingIds=[];g.waiting=false;g.recordVisuals=false;
 g.match.roundNumber=1;g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;g.match.playerOne.crowns=g.match.playerTwo.crowns=0;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;return g;}
const specs=[
 {id:'two-squires',setup(g){for(const side of [1,2]){add(g,112405,side,1,10);add(g,123301,side,1,6,2);add(g,112405,side,1,10);}}},
 {id:'own-storm-knight',setup(g){add(g,122308,2,1,10,0);add(g,112405,2,1,10);g.weather.ApplyHazard(2,1,64);add(g,112405,1,1,15);}},
 {id:'enemy-storm-elite',setup(g){add(g,122317,1,1,10,2);add(g,112405,1,1,10);g.weather.ApplyHazard(1,1,64);add(g,112405,2,1,15);}},
 {id:'opposing-weather',setup(g){for(const side of [1,2]){add(g,112405,side,1,2);add(g,112405,side,1,9);add(g,112405,side,1,9);g.weather.ApplyHazard(side,1,64);}}},
 {id:'locked-squire',setup(g){add(g,112405,1,1,10);add(g,123301,1,1,6,2).AddTokens(4);add(g,112405,1,1,10);add(g,112405,2,1,15);}},
 {id:'squire-hidden-neighbour',setup(g){add(g,112405,1,1,10).AddTokens(8);add(g,123301,1,1,6,2);add(g,112405,1,1,10);add(g,112405,2,1,15);}}
];
let epoch=70000;const results=[];
// For weather already on the AI's row, its current turn ends BEFORE the next
// weather tick. An unarmoured Knight restores armour before receiving Storm.
for(const preset of [54,80])for(const ticks of [1,2,3]){
 const g=blank(preset);add(g,122308,2,1,10,0);add(g,112405,1,1,20);
 for(const side of [1,2])for(let i=0;i<4;i++)add(g,112405,side,8,1);
 const predicted=g.weather.ForecastTokenLoss(2,1,64,ticks*10);
 const baseline=new CBetaGwentCloner().CloneSession(g,++epoch),actual=new CBetaGwentCloner().CloneSession(g,++epoch);baseline.aiSimulating=actual.aiSimulating=true;
 actual.weather.ApplyHazard(2,1,64);
 for(let i=0;i<ticks;i++)for(const side of [2,1])for(const state of [baseline,actual]){
  const card=state.live.find(c=>c.Snapshot().positionPlayerId===side&&c.Snapshot().locationMask===8);
  check(state.Play(side,card.Snapshot().instanceId,4),'own weather turn progression');
 }
 check(predicted===baseline.Score(2)-actual.Score(2),'own-row forecast accounts for end before first tick');
 results.push({preset,id:'own-weather-phase-'+ticks,predicted});
}
for(const preset of [54,80])for(const spec of specs){
 const g=blank(preset);spec.setup(g);const a=add(g,112405,2,8,1),b=add(g,112405,1,8,1);add(g,112405,2,8,1);
 const before=JSON.stringify(g.live.map(c=>c.Snapshot())),draws=g.random.DrawCount();
 const predicted=new CBetaGwentCloner().CloneSession(g,++epoch);predicted.aiSimulating=true;
 check(predicted.AiSimPlay(a.Snapshot().instanceId)!==-2147483647,spec.id+' own action');
 const immediate=predicted.Score(2)-predicted.Score(1);check(predicted.AiSimSkipTurn(),spec.id+' next turn');const lead=predicted.Score(2)-predicted.Score(1);
 const actual=new CBetaGwentCloner().CloneSession(g,++epoch);actual.aiSimulating=true;
 check(actual.Play(2,a.Snapshot().instanceId,4)&&actual.Play(1,b.Snapshot().instanceId,4),spec.id+' neutral response');
 check(lead===actual.Score(2)-actual.Score(1)+1,spec.id+' known ticks agree with neutral real reply');
 check(before===JSON.stringify(g.live.map(c=>c.Snapshot()))&&draws===g.random.DrawCount(),spec.id+' read-only');
 results.push({preset,id:spec.id,afterOwnPlay:immediate,beforeNextOwnTurn:lead,realReplyLead:actual.Score(2)-actual.Score(1)});
}
// The second pass closes the round WITHOUT AfterTurn. Do not invent a free tick.
for(const preset of [54,80])for(const id of [122308,123301,122315]){
 const g=blank(preset);g.match.playerOne.hasPassed=true;
 const engine=add(g,id,2,1,6,id===123301?2:0);
 if(id===123301){add(g,112405,2,1,10);add(g,112405,1,1,17);}else add(g,112405,1,1,id===122315?6:7);
 const hand=add(g,112405,2,8,11);add(g,112405,1,8,11);
 check(g.AiPublicPassLead(true)<=0,'second pass must not invent an engine tick '+id);
 check(g.OpponentStep()&&!g.IsFatal()&&!g.IsPending(),'engine decision '+id);
 check(hand.Snapshot().locationMask!==8&&!g.match.playerTwo.hasPassed,'play to trigger engine rather than concede '+id);
 check(g.Score(2)>g.Score(1),'actual play secures catch '+id);
 check(g.OpponentStep()&&g.match.playerTwo.crowns===1,'stop after sufficient catch '+id);
 results.push({preset,id:'second-pass-no-tick-'+id,passedAfterCatch:true});
}
globalThis.turnForecastReport={checks:globalThis.checks,results,gameplayVerified:false};
`,ctx,{timeout:60000});
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(ctx.turnForecastReport,null,2));console.log(JSON.stringify({checks:ctx.turnForecastReport.checks,scenarios:ctx.turnForecastReport.results.length}));
