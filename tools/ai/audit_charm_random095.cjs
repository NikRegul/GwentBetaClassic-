'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {graph}=require('./source_graph095.cjs'),gsrc=graph(142210,230);
gsrc.variable('Counter',2);gsrc.variable('Power',5);gsrc.variable('MaxTargets',1);
gsrc.value(1,'IsAmbushing','True');gsrc.edge(9,'Out',1,'PlayerIdFilter');gsrc.edge(1,'FlowOut',85,'FlowIn');gsrc.edge(93,'FlowOut',29,'FlowIn');gsrc.edge(29,'FlowOut',136,'FlowIn');gsrc.value(115,'CardTiers',6);gsrc.value(115,'Ignore',8);gsrc.value(154,'PowerType',0);gsrc.value(154,'Op',4);gsrc.value(146,'PowerFilter',1);gsrc.edge(136,'FilteredCards',146,'Cards');gsrc.edge(146,'FilteredCards',176,'List');gsrc.edge(176,'Element',202,'DS');gsrc.edge(202,'DV',184,'Location');gsrc.edge(184,'FlowOut',214,'FlowIn');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add,fill}=require('./audit_fixture095.cjs')(rt);
let checks=0;const failures=[],cases=[];const check=(v,label)=>{checks++;if(!v)failures.push(label);};
for(const side of [1,2])for(const mode of ['tie','singleton','empty','full-best','locked','other-turn'])for(let seed=1;seed<=12;seed++){
 const g=fixture(side,seed),enemy=3-side,source=add(g,142210,side,4,0);source.cardState.timerValue=1;
 const a=add(g,132403,enemy,1,0,5,2,256),b=add(g,132403,enemy,2,0,mode==='singleton'||mode==='full-best'?4:5,1),hidden=add(g,132403,enemy,2,1,5,0,8),high=add(g,132403,enemy,1,1,6),gold=add(g,112101,enemy,4,0,5);
 if(mode==='full-best')fill(g,side,1,9);
 if(mode==='empty'){a.power.SetCurrentPair(6,2);b.power.SetCurrentPair(6,1);}
 if(mode==='locked')source.ToggleLock();
 const before=g.random.DrawCount();g.BeforeTurnWithEvents(mode==='other-turn'?enemy:side);g.FlushEffects();g.FlushDeaths();
 const active=!['locked','other-turn'].includes(mode),picked=[a,b].filter(c=>c.Snapshot().positionPlayerId===side),expectedDraw=active&&mode!=='empty'?1:0;
 check(!g.IsFatal()&&!g.IsPending(),'Malena automatic ability completes');
 check(g.random.DrawCount()-before===expectedDraw,'exact random-element draw count '+side+'/'+mode+'/'+seed);
 check(((source.Snapshot().tokenMask&8)===0)===active||mode==='locked','reveal only at own trigger '+mode);
 if(!active)check(source.Snapshot().timerValue===1,'suppressed timer unchanged '+mode);
 else check(source.Snapshot().timerValue===0,'trigger timer reaches zero');
 if(mode==='tie')check(picked.length===1,'one of tied strongest eligible cards');
 if(mode==='singleton')check(picked.length===1&&picked[0]===a,'unique strongest current-power card, NotTargetable allowed');
 if(mode==='full-best')check(picked.length===0&&a.Snapshot().positionPlayerId===enemy&&b.Snapshot().positionPlayerId===enemy,'full row does not cause fallback to weaker target');
 if(['empty','locked','other-turn'].includes(mode))check(picked.length===0,'no eligible trigger/target gives no charm');
 check(hidden.Snapshot().positionPlayerId===enemy&&high.Snapshot().positionPlayerId===enemy&&gold.Snapshot().positionPlayerId===enemy,'ambush, power6 and Gold excluded');
 for(const c of picked){const t=c.Snapshot();check(t.power.currentPower===5&&t.power.armor===(c===a?2:1),'charm keeps current power and armor');}
 cases.push({side,mode,seed,picked:picked.map(c=>c.Snapshot().instanceId),draws:g.random.DrawCount()-before});
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:gsrc.evidence(['BeforeTurnTrigger','TimerTriggered','FilterCardPowerNode','FilterPowerLevelNode','ListExt','AListGetRandomElementNode','MoveCardsNode']),scope:'Malena timer/reveal, current-power/tier/token filters, strongest tie set, singleton/empty random consumption and full-row no fallback. Exact candidate order and all external reactions remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failures,cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
