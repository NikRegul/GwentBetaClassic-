'use strict';
// CardData.OnWillMove/OnCardMoved and the actual consumers of MoveCards.
// The small transition oracle follows the statically read C# contract; it is
// test-only, and does not execute complete graphs or advance another engine.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {catalog,graph}=require('./source_graph095.cjs');
const pav=graph(122210,266),mil=graph(142104,397),nen=graph(122212,161),ass=graph(162202,200),xar=graph(162108,226);
pav.value(17,'CardTiers',6);pav.value(17,'Ignore',8);pav.value(27,'PowerFilter',3);pav.edge(103,'FlowOut',253,'FlowIn');
mil.value(16,'CardTiers',6);mil.value(16,'Ignore',1032);mil.value(27,'PowerFilter',1);mil.edge(56,'FlowOut',81,'FlowIn');
nen.value(47,'Location',16);nen.edge(21,'SelectedChoices',34,'List');nen.edge(136,'Out',47,'Index');
ass.value(47,'Location',16);ass.value(153,'LocationId',32);ass.edge(21,'SelectedChoices',34,'List');
xar.edge(193,'FlowOut',151,'FlowIn');xar.edge(151,'FlowOut',31,'FlowIn');xar.edge(218,'Out',46,'Index');xar.node(218,'GetLastAvailableIndexNode');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
const templates=new Map(catalog.templates.map(t=>[t.templateId,t]));let checks=0;const failures=[],cases=[];const check=(v,label)=>{checks++;if(!v)failures.push(label);};
function altered(g,id,side,zone,index=0,delta=7,tokens=4|64|128|256|1024){const c=add(g,id,side,zone,index);c.ChangeBasePower(4,true);c.power.SetPermanentPowerAndArmor(2,6);const p=c.Snapshot().power;c.power.SetCurrentPair(p.basePower+p.permanentPower+delta,6);c.cardState.timerValue=2;c.AddTokens(tokens);return c;}
function expectMove(s,t,to,index){
 const active=(s.locationMask&7)!==0,nextActive=(to&7)!==0,p={...s.power};let tokens=s.tokenMask,timer=s.timerValue;
 if(s.locationMask===to&&s.locationIndex===index)return {power:p,tokens,timer};
 if(!active&&nextActive)tokens&=~4; // OnWillMove, before active re-entry.
 if(s.locationMask===32&&to!==32)tokens&=~4;
 if(s.locationMask===8&&to!==8)tokens&=~64;
 if(!active&&nextActive)tokens|=Number(t.fields.Tokens)&9;
 else if(active&&!nextActive||to===32){
  if(to===32||to===8||to===16){tokens&=to===32?1796:1792;p.currentPower=p.basePower+p.permanentPower;if(t.resetInInactive)timer=Number(t.fields.InitialTimer);}
  p.armor=Number(t.fields.Armor);
 }
 return {power:p,tokens,timer};
}
// Distinguish active->inactive, inactive->inactive and active re-entry.
for(const side of [1,2])for(const id of [132209,142204,142306,112206])for(const from of [1,8,16,32])for(const to of [1,8,16,32])for(const delta of [-3,0,7]){
 const g=fixture(side),c=altered(g,id,side,from,0,delta),before=c.Snapshot(),expected=expectMove(before,templates.get(id),to,1);
 c.Move(side,to,1);const after=c.Snapshot(),label=side+'/'+id+'/'+from+'->'+to+'/'+delta;
 check(after.power.basePower===expected.power.basePower&&after.power.permanentPower===expected.power.permanentPower,'instance base and permanent preserved '+label);
 check(after.power.currentPower===expected.power.currentPower&&after.power.armor===expected.power.armor,'power/armor according to zone transition '+label);
 check(after.tokenMask===expected.tokens,'tokens according to zone transition '+label);
 check(after.timerValue===expected.timer,'ResetInInactive timer guard '+label);
 cases.push({kind:'primitive',id,side,from,to,delta,before,expected,actual:after});
}
// A no-op position does not reset a graveyard card a second time.
for(const side of [1,2]){const g=fixture(side),c=altered(g,132209,side,32);const before=c.Snapshot();c.Move(side,32,0);check(JSON.stringify(c.Snapshot())===JSON.stringify(before),'identical-position no-op '+side);}
// Updating other cards' indexes is Location.UpdateIndexes, not another Move
// event. Removing a grave card must not heal or reset its remaining neighbours.
for(const side of [1,2]){
 const g=fixture(side),left=altered(g,132209,side,32,0,7,4|256),middle=altered(g,132209,side,32,1,-3,4),right=altered(g,132209,side,32,2,7,4|256),before=[left,right].map(c=>c.Snapshot());
 g.NorthMoveInactive(middle,side,16,false);
 [left,right].forEach((c,i)=>{const s=c.Snapshot();check(JSON.stringify(s.power)===JSON.stringify(before[i].power)&&s.tokenMask===before[i].tokenMask&&s.timerValue===before[i].timerValue,'reindex does not reset unrelated grave neighbour '+side+'/'+i);});
 check(right.Snapshot().locationIndex===1,'grave indexes compact after removal');
 const hand=altered(g,132209,side,8,0,7,64|4),other=add(g,132209,side,8,1),old=hand.Snapshot();g.NorthMoveInactive(hand,side,8,false);
 const s=hand.Snapshot();check(s.tokenMask===old.tokenMask&&JSON.stringify(s.power)===JSON.stringify(old.power)&&s.timerValue===old.timerValue,'hand reorder is not a fake Hand->Limbo->Hand move');
}
// Return weakest/strongest units, preserving identity, base and permanent
// strength but removing damage/boost and temporary statuses on leaving board.
for(const id of [122210,142104])for(const side of [1,2])for(const row of [1,2,4]){
 const g=fixture(side);g.mulliganReactions=true;const victims=[side,3-side].map(s=>altered(g,132209,s,row,0,id===122210?-15:20,4|64|128|256));
 const source=add(g,id,side,8,0);if(id===122210)source.power.SetCurrentPair(30,0);
 check(g.Play(side,source.Snapshot().instanceId,row),'actual return ability '+id);g.FlushEffects();g.FlushDeaths();
 for(const v of victims){const t=v.Snapshot();check(t.locationMask===16,'returned existing card '+id+'/'+side+'/'+row);check(t.power.currentPower===t.power.basePower+t.power.permanentPower&&t.power.armor===0,'return-to-deck restores effective base '+id);check(t.tokenMask===256,'return-to-deck transient tokens cleared '+id);}
 check(source.Snapshot().locationMask===row&&!g.IsFatal()&&!g.IsPending(),'source completes on board '+id);cases.push({id,side,row,kind:'ability',victims:victims.map(c=>c.Snapshot())});
}
for(const side of [1,2]){const g=fixture(side);g.mulliganReactions=true;const c=add(g,122210,side,8,0);check(g.Play(side,c.Snapshot().instanceId,1),'Pavetta empty board play');check(c.Snapshot().locationMask===1,'Pavetta owner in execution stack is not a weakest candidate');}
// Grave->deck is NOT an active reset: modified inactive power/armor/timer
// survive, while Lock is removed as the card leaves its graveyard.
for(const id of [122212,162202])for(const side of [1,2]){
 const g=fixture(side);g.mulliganReactions=true;const victims=id===122212?[altered(g,132209,side,32,0,-3,4|256)]:[altered(g,132209,side,32,0,-3,4|256),altered(g,132209,3-side,32,0,7,4|256)];
 const before=victims.map(c=>c.Snapshot()),source=add(g,id,side,8,0);check(g.Play(side,source.Snapshot().instanceId,1),'grave return play '+id);
 for(const v of victims)check(g.SelectTarget(g.requestId,v.Snapshot().instanceId),'select grave return '+id);
 g.FlushEffects();g.FlushDeaths();victims.forEach((v,i)=>{const s=v.Snapshot();check(s.locationMask===16&&s.positionPlayerId===before[i].positionPlayerId,'returns to its own deck '+id);check(JSON.stringify(s.power)===JSON.stringify(before[i].power)&&s.timerValue===before[i].timerValue,'inactive data retained '+id);check(s.tokenMask===256,'grave exit removes Lock '+id);});
 check(!g.IsFatal()&&!g.IsPending(),'grave return completes '+id);cases.push({id,side,kind:'ability',victims:victims.map(c=>c.Snapshot())});
}
// Xarthisius shuffles the CHOICE list before asking; it does not shuffle the
// physical deck. Moving its chosen card to the bottom consumes no extra RNG.
for(const side of [1,2])for(const size of [1,2,4]){
 const g=fixture(side);g.mulliganReactions=true;const enemy=3-side,cards=Array.from({length:size},(_,i)=>altered(g,132209,enemy,16,i,7,4|64|256));
 const source=add(g,162108,side,8,0),draws=g.random.DrawCount(),before=cards[0].Snapshot();check(g.Play(side,source.Snapshot().instanceId,1),'Xarthisius play');
 check(g.random.DrawCount()-draws===size-1,'Xarthisius choice-list shuffle draw count '+size);
 check(cards.every((c,i)=>c.Snapshot().locationIndex===i),'choice-list shuffle leaves physical deck unchanged');
 check(g.SelectTarget(g.requestId,cards[0].Snapshot().instanceId),'choose card for bottom');g.FlushEffects();g.FlushDeaths();const s=cards[0].Snapshot();
 check(s.locationMask===16&&s.locationIndex===size-1,'chosen existing card placed at bottom');
 check(JSON.stringify(s.power)===JSON.stringify(before.power)&&s.tokenMask===before.tokenMask&&s.timerValue===before.timerValue,'deck-to-deck move preserves inactive state');
 check(g.random.DrawCount()-draws===size-1,'bottom placement draws no insertion random');cases.push({id:162108,side,size,kind:'ability',actual:s});
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:[pav,mil,nen,ass,xar].map(g=>g.evidence(['MoveCardsNode','CardData','CardPower','CardTokens','Location','CardListShuffleNode','ListExt'])),scope:'Non-Doomed zone-transition state contract and five actual ability branches. Doomed move ordering, all external reactions and complete choice semantics remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failureCount:failures.length,firstFailures:failures.slice(0,15),cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
