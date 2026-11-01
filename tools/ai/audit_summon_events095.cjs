'use strict';
// Targeted card/trigger audit. Trigger dispatch is invoked directly where the
// public game event API does not expose an equivalent fixture action; this is
// deliberately narrower than a full ability or interaction proof.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');
const {graph}=require('./source_graph095.cjs');
const fixtureApi=require('./audit_fixture095.cjs');
const records=JSON.parse(fs.readFileSync(path.join(root,'BetaGwent/build/rules-audit-20261028-04/static-source-review.json'),'utf8')).records;
const ids=[112210,142313,142211,122311,122313,162301,132301,132315,132305,132407,200529,200177,152316];
const checks=[],failures=[],cases=[];
const check=(ok,name,detail)=>{checks.push({name,pass:!!ok,...(detail||{})});if(!ok)failures.push(name);};
const sources=[];
for(const id of ids){
 const rec=records.find(x=>x.templateId===id);assert(rec,`missing static review record ${id}`);
 for(const nid of rec.graphs){const g=graph(id,nid),ev=g.evidence(rec.sourceEvidence.classes.map(x=>path.basename(x.file,'.cs')));
  assert.equal(ev.graphSha256,rec.sourceEvidence.graphSha256,`graph source changed ${id}/${nid}`);
  for(const cls of ev.classes){const expected=rec.sourceEvidence.classes.find(x=>x.file===cls.file);assert(expected&&expected.sha256===cls.sha256,`C# source changed ${id}/${cls.file}`);}
  sources.push({templateId:id,graph:nid,graphSha256:ev.graphSha256,expectedGraphSha256:rec.sourceEvidence.graphSha256,independentExpected:rec.independentExpected,classes:ev.classes});
 }
}
const runtime=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]||path.join(root,'BetaGwent/build/rules-audit-20261028-03/rules03')));
const {fixture,add,fill}=fixtureApi(runtime);
function deckTwin(g,id,side,index=0){return add(g,id,side,16,index);}
function snapshot(card){return card.Snapshot();}
function eventCase(name,setup,invoke,verify,side=1){const g=fixture(side,13031+side);g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;g.match.currentPlayerId=side;g.match.roundActive=g.match.turnActive=true;const x=setup(g);invoke(g,x);const result=verify(g,x);for(const c of result.checks)check(c.ok,`${name}: ${c.name}`,c.detail);cases.push({name,side,...result.data});}

// Roach's graph reacts to any moved hand card entering any active side. The
// baseline handler gates on playFromLocation and the acting side.
for(const side of [1,2])eventCase('roach Gold hand movement',g=>{
 const roach=deckTwin(g,112210,side),moved=add(g,112101,side,8,0);return {roach,moved};
},(g,x)=>{
 const old=snapshot(x.moved);x.moved.playFromLocation=0;x.moved.Move(3-side,1,0);g.MonsterMoved(old);g.FlushEffects();
},(g,x)=>({checks:[{ok:x.roach.Snapshot().locationMask!==16,name:'Roach leaves owner deck after Gold hand movement',detail:{roach:snapshot(x.roach)}}],data:{roach:snapshot(x.roach),moved:snapshot(x.moved),draws:g.random.DrawCount()}}),side);
for(const side of [1,2])eventCase('Roach Bronze excluded',g=>({roach:deckTwin(g,112210,side),moved:add(g,132403,side,8,0)}),(g,x)=>{
 const old=snapshot(x.moved);x.moved.Move(side,1,0);g.MonsterMoved(old);g.FlushEffects();
},(g,x)=>({checks:[{ok:x.roach.Snapshot().locationMask===16,name:'Roach source filter excludes Bronze',detail:{roach:snapshot(x.roach)}}],data:{roach:snapshot(x.roach)}}),side);

// Harpy's graph is AfterMoved from a Beast into its owner's grave. This direct
// event fixture holds movement cause and origin explicit.
for(const side of [1,2])eventCase('harpy Beast death',g=>{
 const harpy=deckTwin(g,132315,side),beast=add(g,132209,side,1,0);return {harpy,beast};
},(g,x)=>{
 const old=snapshot(x.beast);x.beast.Move(side,32,0);g.MonsterMoved(old);g.events.Flush();g.FlushEffects();
},(g,x)=>({checks:[{ok:x.harpy.Snapshot().locationMask!==16,name:'Harpy summoned from deck on active-turn Beast death',detail:{harpy:snapshot(x.harpy)}}],data:{harpy:snapshot(x.harpy),beast:snapshot(x.beast),draws:g.random.DrawCount()}}),side);
for(const side of [1,2])eventCase('Harpy opponent-turn Beast death excluded',g=>({harpy:deckTwin(g,132315,side),beast:add(g,132209,side,1,0)}),(g,x)=>{
 g.match.currentPlayerId=3-side;const old=snapshot(x.beast);x.beast.Move(side,32,0);g.MonsterMoved(old);g.events.Flush();g.FlushEffects();
},(g,x)=>({checks:[{ok:x.harpy.Snapshot().locationMask===16,name:'Harpy waits for its owner current turn',detail:{harpy:snapshot(x.harpy)}}],data:{harpy:snapshot(x.harpy)}}),side);

// Cerys and Raider use their public Skellige moved-trigger dispatcher. Both
// checks distinguish owner/turn and grave-to-board movement. The graph also
// contains additional whitelist/reason branches, kept open below.
for(const side of [1,2])eventCase('Cerys grave-counter return',g=>{
 const source=add(g,200177,side,32,0),other=add(g,132403,side,32,1);source.ChangeTimer(3,0);return {source,other};
},(g,x)=>{
 const old=snapshot(x.other);x.other.Move(side,1,0);g.MonsterMoved(old);g.FlushEffects();
},(g,x)=>({checks:[{ok:x.source.Snapshot().locationMask!==32,name:'Cerys returns after own grave card moves this turn',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source),other:snapshot(x.other),draws:g.random.DrawCount()}}),side);
for(const side of [1,2])eventCase('Cerys off-turn non-whitelist excluded',g=>{
 const source=add(g,200177,side,32,0),other=add(g,132209,side,32,1);source.ChangeTimer(3,0);return {source,other};
},(g,x)=>{g.match.currentPlayerId=3-side;const old=snapshot(x.other);x.other.Move(side,1,0);g.MonsterMoved(old);g.FlushEffects();},(g,x)=>({checks:[{ok:x.source.Snapshot().locationMask===32&&x.source.Snapshot().timerValue===1,name:'Cerys ignores off-turn non-whitelist movement',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source)}}),side);
for(const side of [1,2])eventCase('Cerys off-turn owner-side whitelist',g=>{
 const source=add(g,200177,side,32,0),chosen=add(g,112207,side,32,1);source.ChangeTimer(3,0);return {source,chosen};
},(g,x)=>{g.match.currentPlayerId=3-side;const old=snapshot(x.chosen);x.chosen.Move(side,1,0);g.MonsterMoved(old);g.FlushEffects();},(g,x)=>({checks:[{ok:x.source.Snapshot().timerValue===0&&x.source.Snapshot().locationMask!==32,name:'Cerys accepts owner-side whitelist movement from own grave',detail:{source:snapshot(x.source),chosen:snapshot(x.chosen)}}],data:{source:snapshot(x.source),chosen:snapshot(x.chosen)}}),side);
for(const side of [1,2])eventCase('Cerys enemy grave excluded',g=>{
 const source=add(g,200177,side,32,0),enemy=add(g,132209,3-side,32,1);source.ChangeTimer(3,0);return {source,enemy};
},(g,x)=>{const old=snapshot(x.enemy);x.enemy.Move(3-side,1,0);g.MonsterMoved(old);g.FlushEffects();},(g,x)=>({checks:[{ok:x.source.Snapshot().timerValue===1&&x.source.Snapshot().locationMask===32,name:'Cerys ignores cards leaving opponent grave',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source)}}),side);
for(const side of [1,2])for(const turnSide of [side,3-side])eventCase('Raider hand discard current-turn gate',g=>({source:add(g,152316,side,8,0)}),(g,x)=>{
 const old=snapshot(x.source);x.source.Move(side,32,0);g.MonsterMoved(old);g.FlushEffects();
},(g,x)=>({checks:[{ok:(x.source.Snapshot().locationMask!==32)===(side===turnSide),name:'Raider returns only on its owner current turn',detail:{source:snapshot(x.source),turnSide}}],data:{source:snapshot(x.source),turnSide,draws:g.random.DrawCount()}}),turnSide);

// Wardancer is driven by Nilf's public deck-swap reaction dispatcher. The
// same instance must return; another card sharing its template is not a proxy.
for(const side of [1,2])eventCase('Wardancer same-instance hand-to-deck',g=>{
 const source=add(g,142313,side,8,0),twin=add(g,142313,side,8,1);return {source,twin};
},(g,x)=>{
 g.NorthMoveInactive(x.source,side,16,false);g.FlushEffects();
},(g,x)=>({checks:[{ok:x.source.Snapshot().locationMask!==16,name:'Wardancer instance returns from own deck',detail:{source:snapshot(x.source)}},{ok:x.twin.Snapshot().locationMask===8,name:'other matching instance is not moved',detail:{twin:snapshot(x.twin)}}],data:{source:snapshot(x.source),twin:snapshot(x.twin),draws:g.random.DrawCount()}}),side);

// Aelirenn's census counts owner-side active Elves and fires after either
// player's turn; test the threshold and one-short branch for both owners.
for(const side of [1,2])for(const count of [5,4])eventCase(`Aelirenn Elf threshold ${count}`,g=>{
 const source=deckTwin(g,142211,side);const elves=Array.from({length:count},(_,i)=>add(g,142103,side,1,i));return {source,elves};
},(g,x)=>{g.monsters.NilfTrigger(6,{positionPlayerId:3-side});g.FlushEffects();},(g,x)=>({checks:[{ok:(x.source.Snapshot().locationMask!==16)===(count>=5),name:'Aelirenn threshold counts own active Elves only',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source),count,draws:g.random.DrawCount()}}),side);

// Blue Stripes Commando: equal-power Soldier play summons a matching copy;
// power mismatch remains an explicit negative case.
for(const side of [1,2])for(const power of [3,4])eventCase(`Commando equal-power ${power}`,g=>{
 const source=deckTwin(g,122311,side);source.power.SetCurrentPair(3,0);const played=add(g,122310,side,8,0);played.power.SetCurrentPair(power,0);return {source,played};
},(g,x)=>{g.events.NorthTrigger(5,snapshot(x.played));g.events.Flush();g.FlushEffects();},(g,x)=>({checks:[{ok:(x.source.Snapshot().locationMask!==16)===(power===3),name:'Commando matches current power and Soldier category',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source),played:snapshot(x.played),power,draws:g.random.DrawCount()}}),side);

// The shared Commando trigger chooses from ALL matching deck copies, and
// the played template must differ from Commando's own template.
for(const side of [1,2])for(const sameTemplate of [false,true])eventCase('Commando pool and template exclusion '+sameTemplate,g=>{
 const first=deckTwin(g,122311,side,0),matching=deckTwin(g,122311,side,1),played=add(g,sameTemplate?122311:122310,side,1,0,5);first.power.SetCurrentPair(3,0);matching.power.SetCurrentPair(5,0);return {first,matching,played};
},(g,x)=>{g.events.NorthTrigger(5,snapshot(x.played));g.FlushEffects();},(g,x)=>({checks:[{ok:x.first.Snapshot().locationMask===16,name:'mismatching first owner stays in deck'},{ok:(x.matching.Snapshot().locationMask!==16)===!sameTemplate,name:'matching pool is used but own played template excluded'},{ok:g.random.DrawCount()===(sameTemplate?0:2),name:'one card choice plus random row, no index draw for Last position'}],data:{first:snapshot(x.first),matching:snapshot(x.matching),sameTemplate,draws:g.random.DrawCount()}}),side);

// Brigade: strict score lead greater than 25 at own BeforeTurn. The two
// threshold sides make 25 and 26 distinguishable.
for(const side of [1,2])for(const lead of [25,26])eventCase(`Brigade score lead ${lead}`,g=>{
 const source=deckTwin(g,122313,side),enemy=add(g,132209,3-side,2,0);enemy.power.SetCurrentPair(lead,0);return {source,enemy};
},(g)=>{g.BeforeTurnWithEvents(side);g.FlushEffects();},(g,x)=>({checks:[{ok:(x.source.Snapshot().locationMask!==16)===(lead>25),name:'Brigade requires strict opponent lead above 25',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source),lead,draws:g.random.DrawCount()}}),side);
for(const side of [1,2])eventCase('Brigade random row and random index',g=>{
 const source=deckTwin(g,122313,side),enemy=add(g,132209,3-side,2,0);enemy.power.SetCurrentPair(26,0);for(const row of [1,2,4])fill(g,side,row,2);enemy.power.SetCurrentPair(g.Score(side)+26,0);return {source,beforeDraws:g.random.DrawCount()};
},(g)=>{g.BeforeTurnWithEvents(side);g.FlushEffects();},(g,x)=>{
 const s=snapshot(x.source),rowCount=s.locationMask>0?g.CountLocation(side,s.locationMask):0;
 return {checks:[{ok:s.positionPlayerId===side&&[1,2,4].includes(s.locationMask)&&s.locationIndex>=0&&s.locationIndex<=2,name:'Brigade uses an available own row and a valid random index',detail:{source:s}},{ok:g.random.DrawCount()-x.beforeDraws===2,name:'Brigade consumes one row and one index draw',detail:{draws:g.random.DrawCount()-x.beforeDraws}}],data:{source:s,draws:g.random.DrawCount()-x.beforeDraws,rowCount}};
},side);
for(const side of [1,2])eventCase('Brigade full rows suppress move',g=>{
 const source=deckTwin(g,122313,side),enemy=add(g,132209,3-side,2,0);enemy.power.SetCurrentPair(26,0);for(const row of [1,2,4])fill(g,side,row,9);enemy.power.SetCurrentPair(g.Score(side)+26,0);return {source,beforeDraws:g.random.DrawCount()};
},(g)=>{g.BeforeTurnWithEvents(side);g.FlushEffects();},(g,x)=>({checks:[{ok:x.source.Snapshot().locationMask===16,name:'Brigade remains in deck without any available row',detail:{source:snapshot(x.source)}},{ok:g.random.DrawCount()===x.beforeDraws,name:'Brigade does not draw placement RNG when full',detail:{draws:g.random.DrawCount()-x.beforeDraws}}],data:{source:snapshot(x.source),draws:g.random.DrawCount()-x.beforeDraws}}),side);

// Daerlan reveals its own hand copy on its owner's turn; Golem responds to an
// opponent-side revealed unit only while the Golem owner has the turn.
for(const side of [1,2])for(const turnSide of [side,3-side])eventCase(`Daerlan reveal turn ${turnSide}`,g=>({source:add(g,162301,side,8,0),deck:deckTwin(g,162301,side)}),(g,x)=>{g.match.currentPlayerId=turnSide;g.NilfReveal(x.source,true);g.FlushEffects();while(g.nilfJobs.Size()>0)g.NilfNextReaction();g.FlushEffects();},(g,x)=>({checks:[{ok:(x.source.Snapshot().locationMask!==8)===(turnSide===side),name:'Daerlan owner-turn reveal gate',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source),draws:g.random.DrawCount()}}),side);
for(const side of [1,2])for(const turnSide of [side,3-side])eventCase(`Golem revealed enemy turn ${turnSide}`,g=>({source:deckTwin(g,132407,side),revealed:add(g,132403,3-side,8,0)}),(g,x)=>{g.match.currentPlayerId=turnSide;g.NilfReveal(x.revealed,true);g.FlushEffects();},(g,x)=>({checks:[{ok:(x.source.Snapshot().locationMask!==16)===(turnSide===side),name:'Golem requires source owner current turn',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source),revealed:snapshot(x.revealed),draws:g.random.DrawCount()}}),side);

// Foglet reacts to Fog added on the opposing side; both sides are symmetric.
for(const side of [1,2])eventCase('Foglet opposing Fog row',g=>({source:deckTwin(g,132301,side),ally:add(g,132403,side,1,0)}),(g,x)=>{
 g.MonsterWeatherChanged(3-side,1,0,2);g.events.Flush();g.FlushEffects();
},(g,x)=>({checks:[{ok:x.source.Snapshot().positionPlayerId===side&&x.source.Snapshot().locationMask===1,name:'Foglet summons on its owner row matching the enemy Fog row',detail:{source:snapshot(x.source)}},{ok:x.source.Snapshot().locationIndex===1,name:'Foglet appends after existing own-row units',detail:{source:snapshot(x.source)}},{ok:g.random.DrawCount()===1,name:'Foglet uses only the singleton deck-choice draw',detail:{draws:g.random.DrawCount()}}],data:{source:snapshot(x.source),ally:snapshot(x.ally),draws:g.random.DrawCount()}}),side);
for(const side of [1,2])eventCase('Foglet full destination suppresses summon',g=>({source:deckTwin(g,132301,side)}),(g,x)=>{
 fill(g,side,1,9);g.MonsterWeatherChanged(3-side,1,0,2);g.events.Flush();g.FlushEffects();
},(g,x)=>({checks:[{ok:x.source.Snapshot().locationMask===16,name:'Foglet has no fallback when its selected row is full',detail:{source:snapshot(x.source)}},{ok:g.random.DrawCount()===1,name:'Foglet randomizes deck choice but not a full-row fallback',detail:{draws:g.random.DrawCount()}}],data:{source:snapshot(x.source),draws:g.random.DrawCount()}}),side);
for(const side of [1,2])eventCase('Foglet own-side Fog excluded',g=>({source:deckTwin(g,132301,side)}),(g,x)=>{
 g.MonsterWeatherChanged(side,1,0,2);g.events.Flush();g.FlushEffects();
},(g,x)=>({checks:[{ok:x.source.Snapshot().locationMask===16,name:'Foglet ignores own-side Fog',detail:{source:snapshot(x.source)}}],data:{source:snapshot(x.source)}}),side);

// Nekker: consume compares the attacker side with the owner's side; target is a
// real Beast and the source copy remains a distinct deck instance.
for(const side of [1,2])for(const attackerSide of [side,3-side])eventCase(`Nekker attacker owner ${attackerSide}`,g=>({source:add(g,132305,side,1,0),attacker:add(g,132202,attackerSide,1,1),target:add(g,132209,attackerSide,1,2)}),(g,x)=>{
 const before=x.source.Snapshot().power.currentPower;g.match.currentPlayerId=3-side;g.QueueConsume(x.attacker,x.target);g.FlushEffects();g.FlushDeaths();x.before=before;
},(g,x)=>({checks:[{ok:x.source.Snapshot().power.currentPower===x.before+(attackerSide===side?1:0),name:'Nekker compares attacker owner with source owner, independent of turn',detail:{source:snapshot(x.source),attacker:snapshot(x.attacker),target:snapshot(x.target)}}],data:{source:snapshot(x.source),attacker:snapshot(x.attacker),target:snapshot(x.target),attackerSide,before:x.before,draws:g.random.DrawCount()}}),side);

// Ronvid returns from Grave on own AfterTurn and resets BASE power before
// placement; an opponent turn and a full board are separate negative cases.
for(const side of [1,2])for(const turnSide of [side,3-side])eventCase(`Ronvid grave return turn ${turnSide}`,g=>{
 const source=add(g,200529,side,32,0);source.ChangeBasePower(5,true);source.power.SetPermanentPowerAndArmor(4,2);source.power.SetCurrentPair(30,2);return {source,before:snapshot(source)};
},(g)=>{g.EndTurnWithEvents();g.FlushEffects();},(g,x)=>({checks:[{ok:(x.source.Snapshot().locationMask!==32)===(turnSide===side),name:'Ronvid returns only on own turn',detail:{source:snapshot(x.source)}},{ok:turnSide!==side||(x.source.Snapshot().power.basePower===1&&x.source.Snapshot().power.permanentPower===x.before.power.permanentPower&&x.source.Snapshot().power.armor===x.before.power.armor&&x.source.Snapshot().power.currentPower===x.before.power.currentPower+1-x.before.power.basePower),name:'Ronvid changes base power to 1 while preserving permanent power and armor',detail:{before:x.before.power,after:snapshot(x.source).power}}],data:{source:snapshot(x.source),before:x.before,turnSide,draws:g.random.DrawCount()}}),turnSide);

// Cerys TimerTriggered is direct: no passive zone gate, Lock suppresses it.
for(const side of [1,2])for(const zone of [1,8,16,32])for(const locked of [false,true])eventCase('Cerys direct timer '+zone+'/'+locked,g=>{
 const source=add(g,200177,side,zone,0);source.cardState.timerValue=1;if(locked)source.AddTokens(4);return {source};
},(g,x)=>{x.source.ChangeTimer(0,2);g.FlushEffects();g.FlushDeaths();},(g,x)=>{
 const state=snapshot(x.source),draws=g.random.DrawCount();const results=[{ok:state.timerValue===0,name:'Cerys timer remains zero'},{ok:draws===(locked?0:1),name:'Cerys direct timer random row once unless locked',detail:{draws}},{ok:locked?state.locationMask===zone:state.positionPlayerId===side&&[1,2,4].includes(state.locationMask),name:'Cerys direct timer moves same instance from any zone unless locked',detail:{source:state}}];
 if(!locked){const prior=snapshot(x.source);x.source.Move(side,32,0);g.MonsterMoved(prior);const other=add(g,132209,side,32,1),old=snapshot(other);other.Move(side,1,0);g.MonsterMoved(old);g.FlushEffects();results.push({ok:snapshot(x.source).locationMask===32&&g.random.DrawCount()===draws,name:'Cerys zero timer does not retrigger after later own resurrection'});}
 return {checks:results,data:{source:snapshot(x.source),zone,locked,draws:g.random.DrawCount()}};
},side);

const report={schema:3,fingerprint:runtime.fingerprint,baseline:runtime.fingerprint,invalidPreviousReports:['summon-events-before.json used a Bronze Roach trigger and a Doomed Wolf as a Beast death fixture.','summon-events-before-v2.json corrected those fixtures but included source-hash checks in the behavioral count.','summon-events-before-v3.json predates the corrected Nekker owner-vs-turn predicate, Daerlan reaction drain, Wardancer move action, Brigade power, and Cerys non-Doomed movement.','summon-events-before-v4-final.json directly invoked the wrong Roach kind-4 dispatcher and omitted additional capacity/index assertions.','summon-events-before-v5.json placed too little enemy power for the Brigade RNG/capacity cases after adding friendly units, and wrongly required an end index. The corrected fixture uses enemy-own=26 and any valid random index.'],checks:checks.length,failures:failures.map(name=>({name})),checkResults:checks,cases,sources,
 scope:'13 source graph/C# hash records are evidence only, not behavior checks. Meaningful JS fixture assertions cover both seats for Roach, Wardancer, Aelirenn, Commando, Brigade, Daerlan, Foglet, Harpy, Nekker, Golem, Ronvid, Cerys, and Raider; each test is a targeted branch fixture, not a complete ability proof. Full source graph filtering, every capacity/RNG/index branch, all event ordering/reaction chains, and native behavior remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report path required');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({fingerprint:report.baseline,checks:report.checks,failures:failures.length,cases:cases.length,firstFailures:failures.slice(0,12)}));
if(failures.length)process.exitCode=1;
