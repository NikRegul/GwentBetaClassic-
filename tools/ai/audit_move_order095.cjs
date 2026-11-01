'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {graph}=require('./source_graph095.cjs'),s=graph(142212,1444),n=graph(200089,253),j=graph(200218,140);
s.edge(665,'FilteredCards',1113,'List');s.edge(1113,'Element',1330,'DS');s.edge(1330,'DV',1351,'Cards');
n.edge(18,'Cards',228,'Cards');n.edge(228,'FilteredCards',67,'List');n.edge(67,'Element',170,'DS');n.edge(170,'DV',146,'Cards');n.value(248,'Tokens',8);
j.edge(35,'SelectedTargets',50,'Cards');j.edge(35,'SelectedTargets',90,'Targets');j.edge(35,'SelectedTargets',115,'Targets');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));const {add,fixture,fill}=require('./audit_fixture095.cjs')(rt);
let checks=0;const failures=[],cases=[];const check=(v,label)=>{checks++;if(!v)failures.push(label);};
// Creation order deliberately differs from row order. The single free slot
// must be taken by the leftmost eligible instance, not earliest allocation.
for(const id of [142212,200089])for(const side of [1,2])for(const pickedSide of [1,2]){
 if(id===142212&&pickedSide!==side)continue;
 const g=fixture(side),right=add(g,132403,pickedSide,1,2),left=add(g,132403,pickedSide,1,0),middle=add(g,132403,pickedSide,1,1),hidden=add(g,132403,pickedSide,1,3,undefined,0,8);
 fill(g,pickedSide,2,8);fill(g,pickedSide,4,9);
 const c=add(g,id,side,8,0),base=c.Snapshot().power.currentPower;check(g.Play(side,c.Snapshot().instanceId,1),'row-order play '+id);
 if(id===200089)check(g.SelectRow(g.requestId,pickedSide,1),'select Nivellen row');
 g.FlushEffects();g.FlushDeaths();check(!g.IsFatal()&&!g.IsPending(),'row order complete');
 check(left.Snapshot().locationMask===2&&right.Snapshot().locationMask===1&&middle.Snapshot().locationMask===1,'leftmost eligible gets capacity '+id+'/'+side+'/'+pickedSide);
 check(hidden.Snapshot().locationMask===1,'hidden stays '+id);check(c.Snapshot().locationMask===1,'played source stays '+id);
 if(id===142212)check(c.Snapshot().power.currentPower===base+1,'Sheldon one actual move');
 cases.push({id,side,pickedSide,left:left.Snapshot(),source:c.Snapshot()});
}
for(const side of [1,2]){
 const g=fixture(side),c=add(g,200089,side,8,0);check(g.Play(side,c.Snapshot().instanceId,1),'Nivellen source-only play');const draws=g.random.DrawCount();
 check(g.SelectRow(g.requestId,side,1),'Nivellen own source-only row');g.FlushEffects();g.FlushDeaths();
 check(c.Snapshot().locationMask===1,'Nivellen does not move owner in execution stack '+side);
 check(g.random.DrawCount()===draws,'Nivellen empty original row list does not draw RNG '+side);
}
// One list of THREE picks is independent of remaining capacity. MoveCards
// accepts the available prefix; subsequent damage uses all selected instances.
for(const side of [1,2])for(const capacity of [0,1,2,3]){
 const g=fixture(side),enemy=3-side,row=2;g.mulliganReactions=true;fill(g,enemy,row,9-capacity);
 const targets=[0,1,2].map(i=>add(g,132403,enemy,1,i,20,1)),c=add(g,200218,side,8,0);check(g.Play(side,c.Snapshot().instanceId,row),'Jotunn batch play');
 for(const t of targets){const ready=g.pendingIds.includes(t.Snapshot().instanceId);check(ready,'Jotunn retains all three picks capacity '+capacity);if(ready)check(g.SelectTarget(g.requestId,t.Snapshot().instanceId),'Jotunn pick');}
 g.FlushEffects();g.FlushDeaths();check(!g.IsFatal()&&!g.IsPending(),'Jotunn three-target batch completes');
 targets.forEach((t,i)=>{const x=t.Snapshot();check(x.locationMask===(i<capacity?row:1),'MoveCards prefix '+side+'/'+capacity+'/'+i);check(x.power.currentPower===19&&x.power.armor===0,'damage entire list '+side+'/'+capacity+'/'+i);});
 cases.push({id:200218,side,capacity,targets:targets.map(t=>t.Snapshot())});
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:[s,n,j].map(g=>g.evidence(['MoveCardsNode','Location','GetLocationCards','LocationListGetCardsNode','AListForeachNode','PlayedTrigger'])),scope:'Row order versus allocation order, source-in-stack exclusion, partial capacity and complete selected-list damage. Exact RNG stream and external reaction ordering remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failures,cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
