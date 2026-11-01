'use strict';
// Independent graph obligations are recorded before reading the handlers.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const sourceEvidence=require('./source_reactions096.cjs');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add,fill}=require('./audit_fixture095.cjs')(rt);
let checks=0,label='';const failures=[],cases=[],snap=c=>c.Snapshot(),id=c=>snap(c).instanceId;
const check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});};
function flush(g){g.FlushEffects();g.FlushDeaths();while(g.nilfJobs.length&&!g.IsPending()){g.NilfNextReaction();g.FlushEffects();g.FlushDeaths();}}
function run(tid,side,mode,body){label=tid+'/'+side+'/'+mode;const g=fixture(side,29573+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id:tid,side,mode});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
function full(g,side){for(const row of [1,2,4])fill(g,side,row,9);}
function trace(g){const draws=[],orig=g.random.NextBounded.bind(g.random);g.random.NextBounded=n=>{const v=orig(n);draws.push({n,v});return v;};return draws;}
for(const side of [1,2])for(const zone of [1,8,16])for(const owner of [side,3-side])for(const turn of [side,3-side])for(const banish of [false,true])run(132305,side,`consume/${zone}/${owner}/${turn}/${banish}`,g=>{
 const source=add(g,132305,side,zone,0,10),attacker=add(g,132209,owner,2,0,10),victim=add(g,132209,owner,banish?8:4,0,4);g.match.currentPlayerId=turn;
 check(g.QueueConsume(attacker,victim),'consume accepted');flush(g);
 check(snap(source).power.currentPower===10+(owner===side?1:0),'clean consume owner gate independent of current turn',{source:snap(source)});
 check(snap(victim).locationMask===32,'nonDoomed positive-base consumed Hand/Active unit goes Grave');
});
for(const side of [1,2])for(const zone of [1,8,16])run(132305,side,'Lock/'+zone,g=>{
 const source=add(g,132305,side,zone,0,10,0,4),attacker=add(g,132209,side,2,0,10),victim=add(g,132209,side,4,0,4);
 g.QueueConsume(attacker,victim);flush(g);check(snap(source).power.currentPower===10,'Lock suppresses consume');
});
for(const side of [1,2])for(const tier of [1,2,4,8])run(132305,side,'death-copy-tier/'+tier,g=>{
 const source=add(g,132305,side,2,2,10),copy=add(g,132305,side,16,0),enemy=add(g,132209,3-side,1,0,20);copy.cardState.runtimeTierMask=tier;
 const draws=trace(g);g.MonsterOperation(enemy,source,4,0,7);flush(g);
 check(snap(source).locationMask===32,'source destroyed');check((snap(copy).locationMask===2)===(tier!==1),'same definition current non-Leader tier copied');
 check(snap(copy).positionPlayerId===side,'same original side');check(draws.length===(tier===1?0:1)&&(tier===1||draws[0].n===1),'candidate RNG only, exact From destination',{draws});
});
for(const side of [1,2])for(const reason of [1,2,4])for(const zone of [8,16])for(const gate of ['open','lock','offturn','full'])run(152316,side,`move/${reason}/${zone}/${gate}`,g=>{
 const source=add(g,152316,side,zone,0),twin=add(g,152316,side,8,1);if(gate==='lock')source.AddTokens(4);if(gate==='offturn')g.match.currentPlayerId=3-side;if(gate==='full')full(g,side);
 const old=snap(source);source.Move(side,32,0);const draws=trace(g);g.MonsterMoved(old,false,reason);flush(g);
 const moved=gate==='open'&&reason!==4;check(((snap(source).locationMask&7)!==0)===moved,'reason mask3 and location/turn/lock/capacity');
 check(snap(twin).locationMask===8,'same template twin not substituted');check(draws.length===(moved?1:0),'row RNG only when returning',{draws});
});
for(const side of [1,2])for(const zone of [8,16])run(152316,side,'natural-killed-waiting/'+zone,g=>{
 const source=add(g,152316,side,zone,0),old=snap(source);old.isWaitingToDie=true;source.Move(side,32,0);g.MonsterMoved(old);flush(g);check(snap(source).locationMask===32,'natural dying cause is Killed and excluded');
});
for(const side of [1,2])for(const gate of ['open','full','lock','offturn'])run(200529,side,'AfterTurn/'+gate,g=>{
 const source=add(g,200529,side,32,0,13,4);source.power.SetPermanentPowerAndArmor(2,4);source.power.SetCurrentPair(13,4);const before=snap(source);if(gate==='lock')source.AddTokens(4);if(gate==='full')full(g,side);const draws=trace(g);
 g.NorthTurn(2,gate==='offturn'?3-side:side);flush(g);const after=snap(source),applied=gate==='open'||gate==='full';
 check(after.power.basePower===(applied?1:before.power.basePower),'SET BASE1 even with full board');check(after.power.currentPower===before.power.currentPower+(applied?1-before.power.basePower:0),'current offset retained');
 check(after.power.permanentPower===2&&after.power.armor===4,'permanent/armor retained');check(((after.locationMask&7)!==0)===(gate==='open'),'placement gate');
 check(draws.length===(gate==='open'?2:0),'row+index only for available placement',{draws});
});
for(const side of [1,2])run(200529,side,'actual-second-pass',g=>{
 const source=add(g,200529,side,32,0,13),before=snap(source);g.match.currentPlayerId=3-side;check(g.Pass(3-side),'first pass');
 const afterFirst=snap(source);check(afterFirst.locationMask===32,'opponent AfterTurn does not return source');const draws=g.random.DrawCount();
 check(g.Pass(side),'actual second pass');check(snap(source).locationMask===32&&snap(source).power.basePower===before.power.basePower,'RoundEnd has no AfterTurn return');check(g.random.DrawCount()===draws,'no second-pass return RNG');
});
for(const side of [1,2])for(const otherId of [132209,112207,152209,200529])for(const turn of [side,3-side])for(const destSide of [side,3-side])run(200177,side,`resurrection/${otherId}/${turn}/${destSide}`,g=>{
 const source=add(g,200177,side,32,0),other=add(g,otherId,side,32,1);source.ChangeTimer(4,2);g.match.currentPlayerId=turn;
 const old=snap(other);other.Move(destSide,1,0);g.MonsterMoved(old);flush(g);const expected=turn===side||(otherId!==132209&&destSide===side);
 check(snap(source).timerValue===(expected?3:4),'other-card owner-turn/whitelist/current-side filter');check(snap(source).locationMask===32,'timer not yet zero');
});
for(const side of [1,2])run(200177,side,'full-board-zero',g=>{
 const source=add(g,200177,side,32,0),other=add(g,132209,side,32,1);source.ChangeTimer(1,2);full(g,side);const old=snap(other);other.Move(3-side,1,0);const draws=trace(g);g.MonsterMoved(old);flush(g);
 check(snap(source).timerValue===0&&snap(source).locationMask===32,'timer0 persists when full');check(draws.length===0,'full board uses no placement RNG');
 const next=add(g,132209,side,32,1),old2=snap(next);next.Move(3-side,2,0);g.MonsterMoved(old2);flush(g);check(snap(source).timerValue===0&&draws.length===0,'zero timer does not repeatedly trigger');
});
for(const side of [1,2])for(const blocked of [false,true])run(142313,side,'actual-mulligan/'+blocked,g=>{
 const source=add(g,142313,side,8,0),twin=add(g,142313,side,8,1),incoming=add(g,132209,side,16,0);add(g,132403,side,16,1);if(blocked)full(g,side);
 g.mulligan=true;g.mulliganSide=side;g.mulliganBudget=2;g.mulliganUsed=0;g.blacklistedTemplates=[];g.reservedCards=[];g.pendingIds=[id(source),id(twin)];g.requestId++;
 const draws=trace(g);check(g.SelectMulligan(g.requestId,id(source)),'actual mulligan accepted');flush(g);
 check(snap(source).locationMask===(blocked?16:snap(source).locationMask)&&((snap(source).locationMask&7)!==0)===!blocked,'intercept exact outgoing or continue to deck when full');
 check(snap(incoming).locationMask===8&&snap(incoming).locationIndex===0,'replacement still drawn to original index');check(snap(twin).locationMask===8,'other same-template instance stays');
 check(draws.length===(blocked?1:2)&&draws[0].n===2,'mulligan deck-count RNG before incoming removal, plus optional row RNG',{draws});
});
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,sourceEvidence,scope:'25 recorded obligations, test group1: clean consume/death copy, movement reasons, Ronvid state, Cerys and actual Mulligan. Full ability proof remains open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,failures:failures.length,firstFailures:failures.slice(0,12),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
