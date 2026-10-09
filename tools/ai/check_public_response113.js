// Native WS counterplay and seat-copy regressions; no alternative AI implementation.
const fs=require('fs'),path=require('path'),vm=require('vm');
const dir=path.resolve(process.argv[2]),ctx=vm.createContext({console});
const src=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n');
vm.runInContext(src+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
function check(ok,label){if(!ok)throw Error(label);console.log('PASS',label);}
function add(g,t,side,zone,index){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,t,side,zone,index);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,88))throw Error('fixture');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;
 g.weatherProfile=false;g.recordVisuals=false;g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=2;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 add(g,123301,2,2,0);add(g,112101,2,2,1);add(g,122104,1,1,0);add(g,122104,2,32,0);
 for(let i=0;i<3;i++)add(g,112101,1,8,i);
 return g;}
function state(g){return JSON.stringify({cards:g.live.map(c=>c.Snapshot()),match:g.match.Snapshot(),
 hazards:g.weather.hazards,dream:g.weather.dreamRows,seed:g.random.InitialSeed(),draw:g.random.DrawCount(),request:g.requestId,waiting:g.waiting});}
const g=fixture();g.weather.hazards=[1,2,4,16,32,64];g.weather.dreamRows=[0,4];
const spy=add(g,132204,1,4,0);spy.Move(2,1,0);
const leader=add(g,g.leaderTemplateOne,1,64,0);
const ours=[123301,112101,122106].map(t=>add(g,t,2,8,0));
const before=state(g),copy=g.AiSimClone(),reverse=copy.AiReverseClone();
check(reverse.FindCard(spy.cardState.instanceId).cardState.ownerId===2 && reverse.FindCard(spy.cardState.instanceId).cardState.positionPlayerId===1,'spy owner/controller/board side reverse separately');
check(JSON.stringify(reverse.weather.hazards)==='[16,32,64,1,2,4]' && JSON.stringify(reverse.weather.dreamRows)==='[3,1]','six weather slots and dream rows reverse');
check(reverse.match.Snapshot().currentPlayerId===1 && reverse.match.Snapshot().playerTwo.playerId===2,'turn and nested player structs reverse');
check(reverse.live.every(c=>c.game===reverse && c.power.card===c),'deep-copy references point into shadow session');
const restored=reverse.AiReverseClone();
check(state(restored)===state(copy),'double reversal restores cards/match/weather/RNG/request');
function evaluate(){return ours.map(c=>{
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,3);
 const uplift=g.AiSequenceUplift(c,ours.map(x=>x.cardState.instanceId),ours.map(x=>g.AiExactTempo(x)),model);
 return {pool:model.templates,weights:model.weights,profiles:model.eligibleProfiles,replies:model.evaluated,rejected:model.rejected,risk:model.penalty,uplift};
});}
const first=evaluate();check(first.some(x=>x.replies>0),'native model executes legal replies');
check(first.every(x=>x.replies<=4 && x.pool.length<=3),'bounded three hand replies plus known leader');
check(state(g)===before,'search preserves actual cards/match/weather/RNG/request');
g.live.filter(c=>c.cardState.positionPlayerId===1 && c.cardState.locationMask===8).forEach(c=>{
 c.definition=BetaGwentDuelDefinition(122106);c.cardState.runtimeTemplate=c.definition.header;c.cardState.power.currentPower=40;c.power.currentPower=40;
});g.presetOne=90;
check(JSON.stringify(evaluate())===JSON.stringify(first),'hidden identities/powers/exact preset do not alter public search');
g.match.playerOne.hasPassed=true;const model=new CBetaGwentPublicResponseAI();model.Initialize(g,3);
check(model.Apply(g.AiSimClone())===null && model.evaluated===0 && model.penalty===0,'no invented reply or penalty after player pass');
console.log(JSON.stringify({nativeCounterplay:true,results:first},null,2));
`,ctx,{filename:'native-response113.bundle.js',timeout:180000});
