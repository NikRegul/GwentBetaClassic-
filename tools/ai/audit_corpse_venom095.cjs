'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {catalog,graph}=require('./source_graph095.cjs'),source=graph(201662,243);
source.node(144,'GetCardCategoryNode');source.value(137,'CompareMethod',1);source.value(137,'Negate','False');source.edge(144,'DV',137,'CardCategory');source.edge(234,'Out',53,'Cards');source.value(234,'Ignore',8);source.edge(53,'FilteredCards',107,'Targets');source.variable('Damage',2);
source.value(149,'CardTiers',6);source.value(149,'Ignore',264);source.value(175,'Faction',1);source.edge(156,'SelectedTargets',182,'Targets');
const exclude=source.node(144).sourceTree.children.find(x=>x.tag==='Exclude').children[0].children.map(x=>BigInt(x.attributes.V));
const templates=new Map(catalog.templates.map(t=>[t.templateId,t]));
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0;const failures=[],cases=[];const check=(v,label)=>{checks++;if(!v)failures.push(label);};
for(const side of [1,2])for(const chosen of [112101,142201,152104])for(const armor of [0,1,3]){
 const g=fixture(side),enemy=3-side,specs=[chosen,112104,132209,200080,122309],cards=specs.map((id,i)=>add(g,id,enemy,1,i,30,armor));
 const hidden=add(g,chosen,enemy,2,0,30,armor,8),untargetable=add(g,chosen,enemy,2,1,30,armor,256),friendly=add(g,chosen,side,1,0,30,armor),spell=add(g,201662,side,8,0);
 check(g.Play(side,spell.Snapshot().instanceId,1),'Corpse Venom play');check(g.SelectTemplateChoice(g.requestId,201713),'choose Poison');
 check(g.pendingIds.includes(cards[0].Snapshot().instanceId),'Gold/Bronze selected template legal');check(g.SelectTarget(g.requestId,cards[0].Snapshot().instanceId),'choose Poison target');g.FlushEffects();g.FlushDeaths();check(!g.IsFatal()&&!g.IsPending(),'Poison resolves');
 const words=templates.get(chosen).categoryWords.map((w,i)=>BigInt(w.decimal)&~(exclude[i]||0n));
 for(const c of [...cards,hidden,untargetable,friendly]){
  const t=c.Snapshot(),shares=templates.get(c.TemplateId()).categoryWords.some((w,i)=>(BigInt(w.decimal)&(words[i]||0n))!==0n),hit=t.positionPlayerId===enemy&&(t.tokenMask&8)===0&&shares;
  const damage=hit?2:0;check(t.power.currentPower===30-Math.max(0,damage-armor)&&t.power.armor===Math.max(0,armor-damage),'Poison Exclude mask / no forced self inclusion '+side+'/'+chosen+'/'+armor+'/'+c.TemplateId());
 }
 cases.push({side,chosen,armor,eligibleCategoryWords:words.map(String),actual:cards.map(c=>c.Snapshot())});
}
for(const side of [1,2])for(const targetSide of [1,2]){
 const g=fixture(side),target=add(g,112202,targetSide,1,0,30,9),gold=add(g,112103,targetSide,1,1,30),nonNeutral=add(g,132403,targetSide,1,2,30),hidden=add(g,112202,targetSide,2,0,30,0,8),immune=add(g,112202,targetSide,2,1,30,0,256),spell=add(g,201662,side,8,0);
 check(g.Play(side,spell.Snapshot().instanceId,1),'Acid play');check(g.SelectTemplateChoice(g.requestId,201714),'choose Acid');
 check(g.pendingIds.includes(target.Snapshot().instanceId)&&![gold,nonNeutral,hidden,immune].some(c=>g.pendingIds.includes(c.Snapshot().instanceId)),'Acid neutral Bronze/Silver filter on both sides');
 check(g.SelectTarget(g.requestId,target.Snapshot().instanceId),'choose Acid target');g.FlushEffects();g.FlushDeaths();check(!g.IsFatal()&&!g.IsPending(),'Acid resolves');
 check(target.Snapshot().locationMask===32,'Acid destroys independent of power and armor');cases.push({side,targetSide,branch:'Acid',actual:target.Snapshot()});
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:source.evidence(['GetCardCategoryNode','FilterCardCategoryNode','GetCardsNode','ChangePowerNode','FilterCardFactionNode','DestroyCardsNode']),scope:'Poison: graph-specific category exclusions, no unconditional selected-target hit, owner side, Gold, hidden/NotTargetable and armor. Acid: neutral Bronze/Silver on either side, hidden/NotTargetable/Gold/faction exclusions and unconditional destruction. Arbitrary external reactions and dynamic category mutations remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failureCount:failures.length,firstFailures:failures.slice(0,12),cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
