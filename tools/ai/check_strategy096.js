// Meaningful diagnostic contracts. Written now; execution waits for tournament.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const snapshot=path.resolve(process.argv[2]),output=process.argv[3],{context:ctx,manifest}=load(snapshot);
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function empty(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));return g;}
function observe(g,actor=2,known=true){return new CBetaGwentStrategyObserve096().Capture(g,actor,known);}
function resources(g){return new CBetaGwentStrategyHand096().Evaluate(observe(g));}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),
  request:g.requestId,draws:g.random.DrawCount(),initialSeed:g.random.InitialSeed(),hazards:g.weather.hazards,
  dream:g.weather.dreamRows,waiting:g.waiting,pending:g.pendingIds,startingOne:g.aiStartingDeckOne,startingTwo:g.aiStartingDeckTwo});}
function probe(g,cap=64){const p=new CBetaGwentStrategyProbe096();p.Initialize(g,cap);let steps=0;
  while(!p.Step())if(++steps>65)throw Error('stalled diagnostic');return p;}
// A boolean capability must not retain a card/session reference in the JS host.
{
 const g=empty();add(g,200164,64,0,1);add(g,200164,64,0,2);const v=observe(g);
 check(v.ownLeader===true&&v.enemyLeader===true,'leader capabilities are primitive booleans');
 check(typeof JSON.stringify(v)==='string','strategy observation contains no circular game references');
}
// Unknown identity, power, timer, deck order and private preset cannot affect the view.
{
 const g=empty();add(g,112405,8,0,2);const hidden=add(g,113309,8,0,1),deck=add(g,112103,16,0,1),trap=add(g,142306,1,0,1);
 trap.AddTokens(8);const before=JSON.stringify(observe(g));
 for(const c of [hidden,deck,trap]){c.definition=BetaGwentDuelDefinition(122106);c.cardState.runtimeTemplate=c.definition.header;
   c.power.SetCurrentPair(40,9);c.cardState.timerValue=7;}
 deck.cardState.locationIndex=55;g.presetOne=99;g.nilfInitialOne=[122106];g.nilfSpellOne=113309;
 check(JSON.stringify(observe(g))===before,'unknown information cannot change complete strategy view');
 hidden.SetRevealed(true);check(observe(g).enemyRevealedHand.length===1,'public reveal changes permitted observation');
}
// Capture never sorts the live starting-list arrays or exports private deck order.
{
 const g=empty();g.aiStartingDeckOne=[113309,112405,112103];const before=JSON.stringify(g.aiStartingDeckOne);
 const high=observe(g);check(JSON.stringify(g.aiStartingDeckOne)===before,'capture preserves live starting list');
 check(high.knowsStartingList&&high.startingList.length===3,'authorized maximum receives initial multiset');
 Host.strength=3;const low=observe(g);check(!low.knowsStartingList&&low.startingList.length===0,'normal does not inherit extra information');Host.strength=4;
 check(!observe(g,2,false).knowsStartingList,'explicit information restriction is respected');
}
// The last setup matters to resource features; two alternative setup relations
// must not count a single held payoff as two independently playable finishers.
{
 const g=empty();const setup=add(g,162308,8,0,2);add(g,162315,8,1,2);
 const ready=resources(g);setup.Move(2,512,0);const orphan=resources(g);
 check(ready.heldLinks>orphan.heldLinks&&orphan.noVisibleSetup>ready.noVisibleSetup,'last held setup changes residual-hand features');
 const c=add(g,162308,1,0,2);check(resources(g).activeLinks>0,'live setup changes held link into active link');
 c.AddLock();check(resources(g).activeLinks===0,'locked setup supplies no active link');
}
// Resource accounting does not count banked strength twice.
{
 const g=empty(),c=add(g,112405,8,0,2);const before=resources(g);c.ChangePower(5,false);const after=resources(g);
 check(after.bodyPower-before.bodyPower===5&&after.estimate-before.estimate===5,'hand boost enters estimate once');
}
// An ordinary opening play is resolved by rules, at most once per callback.
{
 const g=empty();add(g,112405,8,0,2);add(g,112405,8,0,1);const before=state(g);
 const nativePlay=CBetaGwentDuelSession.prototype.Play;let calls=0,peak=0;
 CBetaGwentDuelSession.prototype.Play=function(...args){calls++;return nativePlay.apply(this,args);};
 let p;try{p=new CBetaGwentStrategyProbe096();p.Initialize(g,64);let steps=0;
   do{calls=0;const done=p.Step();peak=Math.max(peak,calls);if(done)break;if(++steps>65)throw Error('stalled');}while(true);
 }finally{CBetaGwentDuelSession.prototype.Play=nativePlay;}
 check(peak<=1,'one callback resolves at most one card play');
 check(state(g)===before,'probe preserves real cards, match, requests and RNG');
 const rows=p.results.filter(r=>r.action.kind===2&&r.status===1);
 check(rows.length===3&&rows.every(r=>r.cardsSpent===1&&r.needsEnemyReply),'explicit rows stop at active opponent frontier');
 check(p.results.find(r=>r.action.kind===1).status!==2,'own pass alone is not declared a terminal win');
}
// Empty-handed opponent already passed: pass really closes the match.
{
 const g=empty();g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 g.match.playerOne.hasPassed=true;add(g,112405,1,0,2,10);
 const p=probe(g);check(p.results[0].status===2&&p.results[0].winner===2,'actual pass resolves known terminal victory');
}
// Hidden trap is unsupported until a real hypothesis model is implemented.
{
 const g=empty();add(g,112405,8,0,2);const trap=add(g,142306,1,0,1);trap.AddTokens(8);
 const p=probe(g);check(p.results.length>0&&p.results.every(r=>r.status===3),'hidden trap does not become a harmless anonymous body');
}
// Stale analysis and an exhausted budget must be visible to the caller.
{
 const g=empty();const body=add(g,112405,8,0,2),p=new CBetaGwentStrategyProbe096();p.Initialize(g,64);
 body.ChangePower(1,false);check(p.Step()&&p.invalidated&&p.results.length===0,'changed public/own observation invalidates prepared actions');
 const limited=probe(g,1);check(limited.truncated&&limited.candidateCount>limited.results.length,'truncation does not claim complete action coverage');
}
globalThis.strategyResult={checks,policyEnabled:true,nativeGameplayVerified:false};
`,ctx,{timeout:120000});
const report={fingerprint:manifest.fingerprint,...ctx.strategyResult};
if(output)fs.writeFileSync(output,JSON.stringify(report,null,2));
console.log(JSON.stringify(report));
