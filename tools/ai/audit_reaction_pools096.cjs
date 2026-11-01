'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),sourceEvidence=require('./source_reactions096.cjs');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add,fill}=require('./audit_fixture095.cjs')(rt);
let checks=0,label='';const failures=[],cases=[],snap=c=>c.Snapshot(),id=c=>snap(c).instanceId,check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});};
function flush(g){g.FlushEffects();g.FlushDeaths();while(g.nilfJobs.length&&!g.IsPending()){g.NilfNextReaction();g.FlushEffects();g.FlushDeaths();}}
function run(tid,side,mode,body){label=tid+'/'+side+'/'+mode;const g=fixture(side,39573+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id:tid,side,mode});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
function trace(g){const draws=[],orig=g.random.NextBounded.bind(g.random);g.random.NextBounded=n=>{const v=orig(n);draws.push({n,v});return v;};return draws;}
for(const side of [1,2])for(const doom of [false,true])run(132315,side,'Beast/'+doom,g=>{
 const copies=[add(g,132315,side,16,3),add(g,132315,side,16,0),add(g,132315,side,16,2,10,0,4)],attacker=add(g,132209,side,1,0,20),victim=add(g,132209,side,2,0,5,0,doom?512:0),draws=trace(g);
 check(g.QueueConsume(attacker,victim),'consume Beast');flush(g);
 const moved=copies.filter(c=>(snap(c).locationMask&7)!==0);check(moved.length===(doom?0:1),'shared AbortForAbility returns one matching Harpy for Grave Beast only');
 check(moved.every(c=>snap(c).locationMask===2&&snap(c).locationIndex===0),'original victim From position');check(draws.length===(doom?0:1),'only candidate RNG, no destination draw',{draws});
 if(!doom&&draws.length===1){const physical=[copies[1],copies[2],copies[0]];check(moved[0]===physical[draws[0].v],'candidate physical deck order, locked candidate selectable');}
 check(snap(victim).locationMask===(doom?512:32),'Doomed ends Void, clean ends Grave');
});
for(const side of [1,2])for(const fullBoard of [false,true])for(const targets of [1,2])run(132407,side,`batch/${fullBoard}/${targets}`,g=>{
 const copies=Array.from({length:5},(_,i)=>add(g,132407,side,16,i,10,0,i===0?4:0)),revealed=Array.from({length:targets},(_,i)=>add(g,132209,3-side,8,i));
 if(fullBoard)for(const row of [1,2,4])fill(g,side,row,9);const draws=trace(g);g.NilfRevealCards(revealed.map(id),true);flush(g);
 const moved=copies.filter(c=>(snap(c).locationMask&7)!==0);
 check(moved.length===(fullBoard?0:targets),'one shared source ability executes entire target batch then aborts sibling sources',{moved:moved.map(id)});
 check(draws.length===(fullBoard?4*targets:2*targets),'full-board no-action siblings each draw candidates; successful source aborts siblings',{draws});
 check(revealed.every(c=>(snap(c).tokenMask&64)!==0),'all reveal tokens applied');
});
for(const side of [1,2])for(const tier of [2,4,8])for(const hidden of [false,true])run(112210,side,'Gold-current-tier/'+tier+'/'+hidden,g=>{
 const copies=[add(g,112210,side,16,0),add(g,112210,side,16,1),add(g,112210,side,16,2,10,0,4)],moved=add(g,hidden?142307:112101,side,8,0);moved.cardState.runtimeTierMask=tier;
 const old=snap(moved);moved.Move(3-side,2,0);const draws=trace(g);g.MonsterMoved(old);flush(g);const trigger=tier===8&&!hidden;
 check(copies.filter(c=>(snap(c).locationMask&7)!==0).length===(trigger?2:0),'each unlocked Roach independently follows Gold visible Hand arrival to either side');check(snap(copies[2]).locationMask===16,'locked owner suppressed');
 check(draws.length===(trigger?2:0),'each Roach random ROW then END, no extra RNG',{draws});
});
for(const side of [1,2])run(122311,side,'whole-equal-power-pool',g=>{
 const copies=[add(g,122311,side,16,3,3),add(g,122311,side,16,0,7),add(g,122311,side,16,2,7,0,4)],played=add(g,122310,side,1,0,7),draws=trace(g);
 g.events.NorthTrigger(5,snap(played));flush(g);const moved=copies.filter(c=>(snap(c).locationMask&7)!==0);
 check(moved.length===1,'shared source triggers only one matching copy');check(snap(copies[0]).locationMask===16,'first scheduled owner need not match power');check(draws.length===2&&draws[0].n===2,'candidate then row, no index',{draws});
 if(draws.length===2)check(moved[0]===[copies[1],copies[2]][draws[0].v],'candidate physical deck order and lock ignored in pool');
});
for(const side of [1,2])for(const room of [1,3])run(122313,side,'captured-whole-pool-room/'+room,g=>{
 for(const row of [1,2,4])fill(g,side,row,row===2?9-room:9);
 const copies=Array.from({length:3},(_,i)=>add(g,122313,side,16,i,10)),enemy=add(g,132209,3-side,1,0);enemy.power.SetCurrentPair(g.Score(side)+26,0);const draws=trace(g);
 g.BeforeTurnWithEvents(side);flush(g);const moved=copies.filter(c=>(snap(c).locationMask&7)!==0);
 check(moved.length===room,'all captured Bronze copies move despite score dropping below threshold after first');check(draws.length===2*room,'each available placement row+index; full later attempts no RNG',{draws});
 check(moved.every(c=>snap(c).locationMask===2),'only non-full row');
});
for(const side of [1,2])for(const blocked of [false,true])run(162301,side,'two-reveals-capacity/'+blocked,g=>{
 const sources=[add(g,162301,side,8,0),add(g,162301,side,8,1)],drawn=[add(g,132209,side,16,0),add(g,132403,side,16,1)];if(blocked)for(const row of [1,2,4])fill(g,side,row,9);
 const draws=trace(g);g.NilfRevealCards(sources.map(id),true);flush(g);
 check(sources.every(c=>blocked?snap(c).locationMask===8:(snap(c).locationMask&7)!==0),'each exact source reacts once');check(drawn.every(c=>snap(c).locationMask===8),'each source draws even with full-board failed move');check(draws.length===(blocked?0:2),'row RNG per source only',{draws});
});
for(const side of [1,2])for(const blocked of [false,true])for(const hidden of [false,true])run(142211,side,'Elf-count-capacity/'+blocked+'/'+hidden,g=>{
 const source=add(g,142211,side,16,0),elves=Array.from({length:5},(_,i)=>add(g,142103,side,1,i,10,0,i===3?256:0));elves[0].cardState.runtimeTierMask=8;
 if(hidden){const old=elves[4];old.Move(side,512,0);add(g,142307,side,1,4);}
 if(blocked){for(const row of [1,2,4])fill(g,side,row,row===1?4:9);}const draws=trace(g);g.monsters.NilfTrigger(6,{positionPlayerId:3-side});flush(g);
 check(((snap(source).locationMask&7)!==0)===(!blocked&&!hidden),'Elf threshold counts Gold/immune but excludes hidden, respects full board');check(draws.length===(!blocked&&!hidden?1:0),'random row only after threshold/capacity',{draws});
});
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,sourceEvidence,scope:'25 obligations group2: candidate pools, shared abort, capacity, current tiers and physical RNG order. All full abilities remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,failures:failures.length,firstFailures:failures.slice(0,20),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
