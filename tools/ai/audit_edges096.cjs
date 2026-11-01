'use strict';
// Close the nine explicitly deferred audit198 obligations against extracted
// Beta graphs/C#; exercise the common WS engine, including all Shupe modes.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {catalog,graph}=require('./source_graph095.cjs');
const classes=['GameSharedData','GetCardsDefinitionsNode','MoveCardsNode','ExecutionStack','Location','PlayCardsNode','PlayStack','GetCardPlayerIdNode','AGetDataNode','AVar','IntGetRandomNode','ARequestTargetsAction','GetRandomLocationTokenNode'];
const evidence={graphs:[...new Set([201633,162212,200162,133302,200146,201780,201725,201731])].map(id=>{const a=catalog.abilities.find(a=>a.templateId===id);return graph(id,a.nid).evidence(classes);}),sourceOrder:'Templates.sourceIndex -> insertion-only SharedRuntimeTemplates.Values; no removal/reinsert in GameSharedData'};
graph(162212,387).edge(120,'DV',89,'Index');
graph(133302,372).edge(153,'FlowOut',352,'FlowIn');
graph(200162,334).edge(293,'FlowOut',159,'FlowIn');
graph(201731,1551).value(1062,'PlayerId',3);
const {rt,add,snap,id,check,flush,run,begin,trace,finish}=require('./fixture_batch100096.cjs')(process.argv[2],evidence);
const sorted=x=>JSON.stringify(x.slice().sort((a,b)=>a-b));
function place(g,side,row=4){let k=0;while(g.IsPending()&&(g.pendingRally||g.pendingRow)&&k++<8){let ok=false;for(const r of [row,1,2,4])if(!ok&&g.CanSelectRow(g.requestId,side,r))ok=g.SelectRow(g.requestId,side,r);check(ok,'child row can be chosen');if(!ok)break;flush(g);}}
for(const side of [1,2]){
 for(const full of [false,true])run(201633,side,'empty target / capacity '+full,g=>{
  if(full)for(const r of [1,2,4])for(let i=0;i<9;i++)add(g,132403,side,r,i,30,0,256);
  const rng=trace(g),before=new Set(g.live.map(id));begin(g,201633,side);const created=g.live.filter(c=>!before.has(id(c))&&c.TemplateId()===201758);
  check(created.length===(full?0:1),'spawn after skipped target request; full rows create none');
  if(!full){check((snap(created[0]).locationMask&7)!==0&&snap(created[0]).positionPlayerId===side,'spawn own random row');check(rng.length===1&&rng[0].n===3,'one random available row draw');}
  check(!g.IsPending(),'no empty target pause');
 });
 for(const row of [1,2,4])for(const at of [0,1,3])for(const size of [0,2,5,9])run(162212,side,`pass index ${row}/${at}/${size}`,g=>{
  for(let i=0;i<at;i++)add(g,132403,side,row,i,30);const c=add(g,162212,side,row,at,8,0,128);add(g,132403,side,row,at+1,30);
  const other=Array.from({length:size},(_,i)=>add(g,132403,3-side,row,i,30));const cause=c.Snapshot();cause.positionPlayerId=side;
  g.monsters.NilfTrigger(7,cause);flush(g);
  const expected=other.map(id);if(size<9)expected.splice(Math.min(at,size),0,id(c));
  const actual=g.live.filter(c=>snap(c).positionPlayerId===3-side&&snap(c).locationMask===row).sort((a,b)=>snap(a).locationIndex-snap(b).locationIndex).map(id);
  check(JSON.stringify(actual)===JSON.stringify(expected),'pass MoveCards preserves index, clamps to end, respects capacity',{actual,expected});
  check(size<9?snap(c).positionPlayerId===3-side:snap(c).positionPlayerId===side,'side changes only if destination has capacity');
 });
 for(const kind of ['empty','skip','take'])run(200146,side,'RNG '+kind,g=>{
  const deck=[add(g,132403,side,16,0),add(g,112103,side,16,1),add(g,132209,side,16,2)];
  const grave=kind==='empty'?null:add(g,132403,side,32,0);const rng=trace(g);begin(g,200146,side);
  if(kind==='skip')check(g.FinishTarget(g.requestId),'optional request can be skipped');else if(kind==='take')check(g.SelectTarget(g.requestId,id(grave)),'grave choice');flush(g);
  check(rng.length===1&&rng[0].n===(kind==='take'?4:1),'IntGetRandom is evaluated even with empty selected list',{rng});
  if(kind==='take')check(snap(grave).locationMask===16&&snap(grave).locationIndex===rng[0].v,'random exact insertion index');
  else check(deck.every((c,i)=>snap(c).locationMask===16&&snap(c).locationIndex===i),'empty/skip changes no deck order');
 });
 run(201780,side,'empty grave resolves directly',g=>{begin(g,201780,side);check(!g.IsPending(),'no informational request outside Beta graph');});
 for(const childId of [132201,132302])run(133302,side,'boost before placement '+childId,g=>{
  const owner=begin(g,133302,side);check(g.pendingChoice,'Nest template request');check(g.SelectTemplateChoice(g.requestId,childId),'select child');flush(g);
  const child=g.pendingRally;check(!!child&&snap(child).locationMask===128,'child still awaiting placement');
  if(child)check(snap(child).power.currentPower===rt.definition(childId).header.power+1,'boost already applied before child deploy');
  place(g,side);check(!g.IsPending(),'child resolved');
 });
 for(const childId of [132403,113401])for(const locked of [false,true])run(200162,side,`BeforeTurnEnd ${childId}/${locked}`,g=>{
  const bounce=add(g,132403,side,1,0,20),hand=add(g,childId,side,8,0);const em=begin(g,200162,side);
  check(g.pendingIds.includes(id(hand)),'first hand request');check(g.SelectTarget(g.requestId,id(hand)),'play hand card');flush(g);place(g,side);
  // Clear Skies resolves on its own. No target bounce until BeforeTurnEnd.
  check(!g.IsPending()&&snap(bounce).locationMask===1,'child return does not request bounce');
  check(em.nilfTurnArmed,'actual chosen-card move arms persistent counter');
  if(locked)em.AddTokens(4);
  g.match.currentPlayerId=3-side;g.monsters.nilf.BeforeTurnEnd(3-side);flush(g);check(!g.IsPending(),'enemy end does not fire');
  g.match.currentPlayerId=side;g.monsters.nilf.BeforeTurnEnd(side);flush(g);
  if(locked){check(!g.IsPending()&&em.nilfTurnArmed,'locked leader does not fire');return;}
  check(g.IsPending()&&g.pendingIds.includes(id(bounce))&&em.monsterStage===2,'own BeforeTurnEnd asks for return');
  check(g.SelectTarget(g.requestId,id(bounce)),'return selected');flush(g);check(snap(bounce).locationMask===8,'returned to hand');
  g.monsters.nilf.BeforeTurnEnd(side);flush(g);check(!g.IsPending(),'counter resets after return');
 });
}

// All FIVE modes, each in all THREE offered positions. Seed selection depends
// only on the standalone Fisher-Yates shuffle, then real card play repeats it.
for(const tid of [201725,201731])for(const side of [1,2])for(let mode=tid+1;mode<=tid+5;mode++)for(const slot of [0,1,2])run(tid,side,`all modes ${mode}/slot${slot}`,g=>{
 let seed=1,pool;for(;seed<300;seed++){g.random.Initialize(872000+seed);const probe=rt.cloneSession(g),p={v:Array.from({length:5},(_,i)=>tid+i+1)};probe.ShuffleIds(p);if(p.v[slot]===mode){pool=p.v.slice(0,3);break;}}
 check(seed<300,'seed offers selected mode in requested slot');g.random.Initialize(872000+seed);
 const own=add(g,132209,side,1,0,30,3),own2=add(g,132403,side,4,0,5),enemy=[0,1,2].map((i)=>add(g,132403,3-side,1,i,30,3));
 const hidden=add(g,132403,3-side,2,0,30,0,8),untargetable=add(g,132403,3-side,4,0,30,0,256);
 const deckUnit=add(g,132403,side,16,0),special=add(g,113401,side,16,1);add(g,112103,side,16,2);
 if(mode===201735){g.MonsterWeather(side,1,1);g.MonsterWeather(side,2,128);flush(g);}
 const rng=trace(g),owner=begin(g,tid,side);check(g.pendingChoice&&JSON.stringify(g.pendingIds)===JSON.stringify(pool),'exact shuffled three-mode offer');
 check(g.SelectTemplateChoice(g.requestId,mode),'every offered slot selectable');flush(g);
 if(mode===201726)check(snap(deckUnit).locationMask===8,'draws one top card');
 if(mode===201727){const candidates=[...enemy,untargetable];const d=rng[4];check(!!d&&d.n===4,'random charm includes NotTargetable, excludes Ambush');if(d)check(snap(candidates[d.v]).positionPlayerId===side,'exact randomly chosen enemy is charmed');}
 if(mode===201728){const h=[1,2,4,16,32,64,512,1024,2048];for(let i=0;i<3;i++){const d=rng[4+i];check(!!d&&d.n===9&&g.weather.Token(3-side,[1,2,4][i])===h[d.v],'three independent random hazards in enemy rows');}}
 if(mode===201729){check(g.pendingIds.includes(id(enemy[1])),'enemy target present');g.SelectTarget(g.requestId,id(enemy[1]));flush(g);check(enemy.map(c=>snap(c).power.currentPower).join(',')==='28,23,28','10 on target, 5 on each neighbour, armor first');}
 if(mode===201730||mode===201736){const pick=mode===201730?special:deckUnit;check(JSON.stringify(g.pendingIds)===JSON.stringify([id(pick)]),'tutor exact Bronze/Silver special or unit filter');g.SelectTarget(g.requestId,id(pick));flush(g);place(g,side);check((snap(pick).locationMask&7)!==0||[32,512].includes(snap(pick).locationMask),'tutor plays selected card; Doomed events banished',{s:snap(pick)});}
 if(mode===201732){check(sorted(g.pendingIds)===sorted([own,own2,...enemy].map(id)),'15 damage targets both sides, excluding executing owner/Ambush/NotTargetable',{actual:g.pendingIds.slice(),expected:[own,own2,...enemy].map(id)});g.SelectTarget(g.requestId,id(own));flush(g);check(snap(own).power.currentPower===18&&snap(own).power.armor===0,'15 damage can target own unit');}
 if(mode===201733){const hits=[...enemy,untargetable],loss=hits.reduce((n,c)=>n+(30-snap(c).power.currentPower)+(3-(c===untargetable?3:snap(c).power.armor)),0);check(loss===16,'eight hits of two, armor first',{loss});check(rng.length===12&&rng.slice(4).every(d=>d.n===4),'eight independent random target draws');}
 if(mode===201734){check(sorted(g.pendingIds)===sorted([own,own2].map(id)),'replay own Bronze/Silver targets');g.SelectTarget(g.requestId,id(own));flush(g);check(g.pendingRally===own&&snap(own).power.currentPower===rt.definition(132209).header.power+5,'reset in hand and boost five before replay');place(g,side);}
 if(mode===201735){check(g.weather.Token(side,1)===0&&g.weather.Token(side,2)===128,'clears own hazards and preserves boon');check(snap(own).power.currentPower===31&&snap(own2).power.currentPower===6&&snap(owner).power.currentPower===31,'boosts all own visible units one');}
 check(snap(hidden).positionPlayerId===3-side&&snap(hidden).power.currentPower===30,'enemy Ambush remains untouched');
 check(!g.IsPending(),'selected mode resolves fully');
});
finish(process.argv[3],'Nine deferred audit198 obligations; all Shupe Mage/Hunter modes in every offered slot. Full arbitrary external-reaction equivalence remains open.');
