'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {graph}=require('./source_graph095.cjs');
const graphs=[graph(132104,129),graph(132314,720),graph(200218,140),graph(142206,212),graph(142302,236),graph(142311,756),graph(200147,109),graph(201609,879),graph(200225,184)];
const [car,drown,jot,kia,brig,merc,flam,slave,muzzle]=graphs;
car.variable('MaxTargets',1);drown.variable('Damage',2);drown.variable('Damage2',4);jot.variable('MaxTargets',3);jot.variable('Damage',2);jot.variable('Damage2',3);merc.variable('Boost',3);flam.variable('MaxTargets',2);slave.variable('Power',3);muzzle.variable('Power',8);
car.edge(38,'FlowOut',78,'FlowIn');car.edge(7,'DV',17,'LocationId');car.value(7,'LocationMask',7);
drown.edge(425,'FlowOut',673,'FlowIn');drown.edge(711,'Out',673,'List');drown.value(711,'TokenType',1);drown.edge(701,'DV',711,'PlayerMask');drown.edge(683,'DV',711,'LocationMask');
jot.edge(50,'FlowOut',101,'FlowIn');jot.value(83,'TokenMask',1);jot.edge(35,'SelectedTargets',90,'Targets');jot.edge(35,'SelectedTargets',115,'Targets');
kia.value(28,'Ignore',256);kia.edge(7,'FlowOut',172,'FlowIn');kia.edge(172,'FlowOutFalse',185,'FlowIn');
brig.edge(25,'DV',47,'LocationId');brig.value(25,'LocationMask',7);brig.edge(173,'FlowOut',7,'FlowIn');
merc.edge(684,'DV',666,'LocationId');merc.value(684,'LocationMask',7);merc.edge(545,'FlowOut',716,'FlowIn');merc.edge(716,'FlowSuccess',443,'FlowIn');
flam.edge(16,'DV',42,'LocationId');flam.value(16,'LocationMask',7);flam.edge(86,'FlowOut',21,'FlowIn');
slave.edge(818,'Out',829,'List');slave.edge(829,'FlowFor',854,'FlowIn');slave.edge(844,'DV',836,'LocationMask');slave.value(785,'Tier',2);slave.value(790,'Tokens',264);
muzzle.edge(122,'Out',129,'List');muzzle.value(173,'Tier',6);muzzle.value(178,'Tokens',264);
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));const {add,fixture,fill}=require('./audit_fixture095.cjs')(rt);
let checks=0;const failures=[],cases=[];const check=(v,label)=>{checks++;if(!v)failures.push(label);};
function finish(g,label){g.FlushEffects();g.FlushDeaths();check(!g.IsFatal()&&!g.IsPending(),label+' complete');}
// The three original graphs do NOT prefilter full destinations. MoveCards
// truncates its input, but its FlowOut still reaches weather/damage actions.
for(const id of [132104,132314,200218])for(const side of [1,2])for(const full of [false,true])for(const hazard of [0,1,2,32]){
 const row=2,oldRow=1,g=fixture(side),enemy=3-side;const occupied=fill(g,enemy,row,full?9:0);
 // Use the engine's reaction context to finish this ability without starting
 // the next turn. Otherwise a separate weather tick obscures its damage.
 // This group proves the ability branch, not normal turn scheduling.
 g.mulliganReactions=true;
 const target=add(g,132403,enemy,oldRow,0,30,1);if(hazard)g.weather.ApplyHazard(enemy,full?oldRow:row,hazard);
 const same=full?occupied[0]:add(g,132403,enemy,row,0,30);g.Reindex(enemy,row);
 const c=add(g,id,side,8,0);check(g.Play(side,c.Snapshot().instanceId,row),'move play '+id+'/'+side+'/'+full+'/'+hazard);
 check(g.pendingIds.includes(target.Snapshot().instanceId),'full destinations retain target request '+id+'/'+side+'/'+full+'/'+hazard);
 if(g.pendingIds.includes(target.Snapshot().instanceId)){
  check(g.SelectTarget(g.requestId,target.Snapshot().instanceId),'select '+id);
  if(g.IsPending()&&id===200218)check(g.SelectTarget(g.requestId,0),'finish optional Jotunn');
 }
 finish(g,'move '+id);
 const t=target.Snapshot(),damage=id===132104?0:id===132314?(hazard?4:2):(!full&&hazard===1?3:2);
 check(t.locationMask===(full?oldRow:row),'capacity affects move only '+id+'/'+full);
 check(t.power.currentPower===30-Math.max(0,damage-1),'post-move graph damage '+id+'/'+side+'/'+full+'/'+hazard+' actual '+t.power.currentPower);
 if(id===132104)check(g.WeatherToken(enemy,row)===1,'Caranthir Frost even if destination full');
 cases.push({id,side,full,hazard,actual:t});
}
// Other-row ally/opponent movement: full destination only skips MoveCards;
// Kiaran still toggles lock; Mercenary still boosts selected ally AFTER the move.
for(const id of [142206,142302,142311,200147])for(const side of [1,2])for(const friendly of [false,true]){
 if(id===200147&&!friendly)continue;
 const g=fixture(side),targetSide=friendly?side:3-side,row=2;
 const target=add(g,132403,targetSide,1,0,20),same=add(g,132403,targetSide,row,0,20),hidden=add(g,132403,targetSide,4,0,20,0,8);
 const card=add(g,id,side,8,0);check(g.Play(side,card.Snapshot().instanceId,row),'target play '+id);
 const pool=[...g.pendingIds];check(pool.includes(target.Snapshot().instanceId),'other-row legal '+id);
 check(!pool.includes(card.Snapshot().instanceId),'execution-stack owner excluded '+id+'/'+side+'/'+friendly);
 check(pool.includes(same.Snapshot().instanceId)===(id===142206),'same-row restriction '+id+'/'+side+'/'+friendly);
 check(pool.includes(hidden.Snapshot().instanceId)===(id===142206),'hidden target follows Ignore256/264 '+id);
 if(pool.includes(target.Snapshot().instanceId))g.SelectTarget(g.requestId,target.Snapshot().instanceId);
 if(g.IsPending()&&id===200147)g.SelectTarget(g.requestId,0);finish(g,'target '+id);
 const t=target.Snapshot();check(t.positionPlayerId===targetSide&&t.locationMask===row,'movement keeps side '+id);
 check(t.power.currentPower===20+(id===142311&&friendly?3:0),'mercenary boost only allies '+id);
 if(id===142206)check((t.tokenMask&4)!==0,'Kiaran lock toggle');
 cases.push({id,side,friendly,pool});
}
for(const side of [1,2])for(const targetSide of [1,2]){
 const g=fixture(side),target=add(g,132403,targetSide,1,0,20,3,8),card=add(g,142206,side,8,0);
 check(g.Play(side,card.Snapshot().instanceId,2),'Kiaran hidden target play');check(g.pendingIds.includes(target.Snapshot().instanceId),'hidden target available');
 check(g.SelectTarget(g.requestId,target.Snapshot().instanceId),'choose hidden Kiaran target');finish(g,'Kiaran hidden');
 const t=target.Snapshot();check((t.tokenMask&12)===4&&t.locationMask===2&&t.positionPlayerId===targetSide,'lock reveals then moves hidden card');
 check(t.power.currentPower===20&&t.power.armor===3,'Kiaran hidden preserves power and armor');
}
// Charm pools are built from own AVAILABLE rows before power/tier filters.
for(const id of [201609,200225])for(const side of [1,2])for(const full of [false,true])for(const power of [3,4,8,9]){
 const g=fixture(side),row=2,enemy=3-side;fill(g,side,row,full?9:0);
 const target=add(g,132403,enemy,row,0,power,2),hidden=add(g,132403,enemy,4,0,1,0,8),immune=add(g,132403,enemy,4,1,1,0,256);
 const card=add(g,id,side,8,0),placement=id===201609?1:row;check(g.Play(side,card.Snapshot().instanceId,placement),'charm play');
 const pool=[...g.pendingIds],eligible=!full&&power<=(id===201609?3:8);
 check(pool.includes(target.Snapshot().instanceId)===eligible,'charm row capacity/power '+id+'/'+side+'/'+full+'/'+power);
 check(!pool.includes(hidden.Snapshot().instanceId)&&!pool.includes(immune.Snapshot().instanceId),'charm hidden/not-targetable');
 if(eligible&&pool.includes(target.Snapshot().instanceId)){
  g.SelectTarget(g.requestId,target.Snapshot().instanceId);finish(g,'charm');const t=target.Snapshot();
  check(t.positionPlayerId===side&&t.locationMask===row&&t.power.currentPower===power&&t.power.armor===2,'charm preserves power/armor/row');
 }
 cases.push({id,side,full,power,pool});
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:graphs.map(g=>g.evidence(['MoveCardsNode','RequestCardTargetsNode','GetCardsNode','GetAvailableLocationsNode','Location'])),scope:'Target masks and movement FlowOut at capacity; selected movement and follow-up power/weather. External reaction order and exact RNG sequence remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'Fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failures,cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
