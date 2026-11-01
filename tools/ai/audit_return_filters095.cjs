'use strict';
// Expectations come from the five source graphs, not from the shared WS/JS.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {graph}=require('./source_graph095.cjs');
const graphs=[[122210,266],[142104,397],[122212,161],[162202,200],[162108,226]].map(x=>graph(...x));
const [pav,mil,nen,ass,xar]=graphs;
pav.value(17,'CardTypes',4);pav.value(17,'CardTiers',6);pav.value(129,'Ignore',8);pav.value(80,'CardTiers',14);pav.value(163,'Ignore',8);
mil.value(16,'Ignore',1032);mil.value(339,'CardTiers',15);mil.value(368,'CardTiers',15);
nen.value(16,'CardTypes',4);nen.value(16,'CardTiers',6);nen.value(111,'CardTiers',14);
ass.value(153,'CardTypes',14);ass.value(153,'CardTiers',6);ass.value(111,'CardTiers',15);
xar.value(23,'CardTiers',14);xar.value(23,'Ignore',0);
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0;const failures=[],cases=[];const check=(v,s)=>{checks++;if(!v)failures.push(s);};
function observe(g){const draws=[],next=g.RandomIndex.bind(g);g.RandomIndex=n=>{const result=next(n);draws.push({bound:n,result});return result;};return draws;}
function deck(g,side){return [add(g,132403,side,16,0),add(g,113205,side,16,1),add(g,112101,side,16,2),add(g,132403,side,16,3,undefined,0,8),add(g,131101,side,16,4)];}
for(const id of [122210,142104])for(const side of [1,2])for(const mode of ['tie','singleton','empty-own','empty-enemy'])for(let seed=1;seed<=12;seed++){
 const g=fixture(side,seed);g.mulliganReactions=true;const chosen={},excluded=[];
 for(const owner of [side,3-side]){
  deck(g,owner);const empty=mode===(owner===side?'empty-own':'empty-enemy'),p=id===122210?2:30,decoy=id===122210?1:40;
  chosen[owner]=empty?[]:[add(g,132403,owner,1,0,p,0,256)];
  if(!empty&&mode==='tie')chosen[owner].push(add(g,132403,owner,2,0,p));
  const stubborn=add(g,132403,owner,4,0,p,0,1024);
  if(!empty&&id===122210)chosen[owner].push(stubborn);else{if(empty)stubborn.Move(owner,512,0);excluded.push(stubborn);}
  excluded.push(add(g,132403,owner,2,1,decoy,0,8),add(g,112101,owner,1,1,decoy),add(g,113205,owner,4,1,decoy));
 }
 const source=add(g,id,side,8,0);source.power.SetCurrentPair(id===122210?30:1,0);const draws=observe(g);
 check(g.Play(side,source.Snapshot().instanceId,4),'return resolves '+id);
 const order=id===122210?[side,3-side]:[3-side,side],expectedBounds=[];
 for(const owner of order)if(chosen[owner].length)expectedBounds.push(chosen[owner].length,id===142104?6:owner===side?5:4);
 check(JSON.stringify(draws.map(d=>d.bound))===JSON.stringify(expectedBounds),'graph target/insertion RNG bounds '+id+'/'+side+'/'+mode+'/'+seed);
 for(const owner of order){const moved=chosen[owner].filter(c=>c.Snapshot().locationMask===16);check(moved.length===(chosen[owner].length?1:0),'one eligible extreme per side '+id);}
 check(excluded.every(c=>c.Snapshot().locationMask!==16),'Gold/special/ambush and Milva Stubborn excluded '+id);
 check(source.Snapshot().locationMask===4,'source is not own target '+id);
 check(!g.IsPending()&&!g.IsFatal(),'ability completes '+id);
 cases.push({id,side,mode,seed,expectedBounds,actualDraws:draws});
}
for(const id of [122212,162202])for(const side of [1,2]){
 const g=fixture(side);g.mulliganReactions=true;deck(g,side);deck(g,3-side);
 const own=add(g,132403,side,32,0,undefined,0,4|8|256|1024),enemy=add(g,132403,3-side,32,0),special=add(g,113205,side,32,1),gold=add(g,112101,side,32,2),leader=add(g,131101,side,32,3),hand=add(g,132403,side,8,0);
 const source=add(g,id,side,8,1),draws=observe(g);check(g.Play(side,source.Snapshot().instanceId,1),'grave request opens '+id);
 const expected=id===122212?[own]:[own,enemy,special];
 check(JSON.stringify([...g.pendingIds].sort((a,b)=>a-b))===JSON.stringify(expected.map(c=>c.Snapshot().instanceId).sort((a,b)=>a-b)),'grave side/type/tier/token filters '+id);
 check(g.SelectTarget(g.requestId,own.Snapshot().instanceId),'grave choice accepted '+id);
 check(draws[0]?.bound===(id===122212?5:6),'grave insertion GetCards tier mask '+id);
 check(own.Snapshot().positionPlayerId===side&&own.Snapshot().locationMask===16,'chosen card remains in its current side deck '+id);
 check(g.pendingIds.every(i=>i!==own.Snapshot().instanceId),'selected instance is not offered again '+id);
 cases.push({id,side,expectedChoices:expected.map(c=>c.Snapshot().instanceId),actualDraws:draws});
}
// Shuffle is Fisher-Yates on the choice list. Include a hidden card and an
// event, exclude Leader tier, then choose an existing instance (not template).
for(const side of [1,2]){
 const g=fixture(side);g.mulliganReactions=true;const enemy=3-side,cards=deck(g,enemy),source=add(g,162108,side,8,0),draws=observe(g);
 check(g.Play(side,source.Snapshot().instanceId,1),'Xarthisius mixed deck request');
 const expected=cards.slice(0,4).map(c=>c.Snapshot().instanceId);check(JSON.stringify([...g.pendingIds].sort((a,b)=>a-b))===JSON.stringify(expected.sort((a,b)=>a-b)),'Xarthisius includes hidden/event, excludes Leader');
 check(g.random.DrawCount()===3,'four-card choice shuffle consumes three draws');
 check(cards.every((c,i)=>c.Snapshot().locationIndex===i),'shuffle does not move physical cards');
 check(g.SelectTarget(g.requestId,cards[0].Snapshot().instanceId),'Xarthisius select original instance');
 check(cards[0].Snapshot().locationIndex===4&&g.random.DrawCount()===3,'bottom uses actual location end and no extra random');
 cases.push({id:162108,side,draws});
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:graphs.map(g=>g.evidence(['GetCardsNode','Location','FilterPowerLevelNode','IntGetRandomNode','AListGetRandomElementNode','ListExt','GetLastAvailableIndexNode'])),scope:'Five return ability filters, extreme tie sets, source-in-stack, empty sides, random call bounds/order, filtered insertion count and physical bottom; exact candidate order, optional choices and all external reactions remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failureCount:failures.length,firstFailures:failures.slice(0,12),cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
