'use strict';
// Ten independently read Beta graphs: choice -> move/draw/create contracts.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),{graph}=require('./source_graph095.cjs');
const pairs=[[112211,295],[112212,685],[122203,353],[122204,631],[152214,336],[162210,357],[200071,297],[200048,331],[200083,156],[201638,195]],graphs=pairs.map(x=>graph(...x));
graphs[0].value(14,'Index',0);graphs[0].edge(7,'FlowOut',238,'FlowIn');graphs[1].value(373,'Random','True');graphs[2].edge(283,'FlowOut',80,'FlowIn');graphs[3].edge(628,'Out',550,'ValidCards');graphs[4].edge(195,'FlowOut',226,'FlowIn');graphs[5].edge(133,'Out',32,'MinChoices');graphs[6].edge(282,'FlowOutTrue',287,'FlowIn');graphs[7].edge(18,'Out',25,'DS');graphs[8].edge(138,'FlowOut',29,'FlowIn');graphs[9].edge(191,'Out',153,'ValidCards');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);let checks=0;const failures=[],cases=[];let label='';const check=(v,s)=>{checks++;if(!v)failures.push(label+': '+s);};
function flush(g){g.FlushEffects();g.FlushDeaths();}
function begin(g,id,side,timer){g.mulliganReactions=true;const c=add(g,id,side,8,20);if(timer!==undefined)c.cardState.timerValue=timer;check(g.Play(side,c.Snapshot().instanceId,1),'actual deploy accepted');return c;}
function choose(g,c){if(!g.IsPending()){check(false,'expected choice request');return false;}const id=typeof c==='number'?c:c.Snapshot().instanceId;const ok=g.SelectTarget(g.requestId,id);check(ok,'chosen existing instance accepted');flush(g);return ok;}
function observe(g){const draws=[],next=g.RandomIndex.bind(g);g.RandomIndex=n=>{const result=next(n);draws.push({bound:n,result});return result;};return draws;}
const ids=cs=>cs.map(c=>c.Snapshot().instanceId).sort((a,b)=>a-b),sameSet=(a,b)=>JSON.stringify([...a].sort((a,b)=>a-b))===JSON.stringify([...b].sort((a,b)=>a-b));
// Godling discards before checking whether a definition can be generated.
for(const side of [1,2])for(const mode of ['duplicates','empty-pool','current-tier']){
 label='Godling/'+side+'/'+mode;const g=fixture(side),held=add(g,132209,side,8,0),target=add(g,132209,side,8,1),oldGrave=add(g,132209,side,32,0);target.ChangeBasePower(4,true);target.power.SetPermanentPowerAndArmor(2,5);if(mode==='current-tier')target.cardState.runtimeTierMask=4;
 const initial=mode==='duplicates'?[132209,132209,142315]:[112101];if(side===1)g.nilfInitialTwo=initial;else g.nilfInitialOne=initial;const count=g.live.length;begin(g,112211,side);choose(g,target);
 check(target.Snapshot().locationMask===32&&target.Snapshot().locationIndex===0,'selected card discarded to grave index0 even with empty source pool');check(oldGrave.Snapshot().locationIndex===1,'grave neighbours shifted');
 const created=g.live.slice(count+1);check(created.length===(mode==='duplicates'?1:0),'create only when initial-deck filtered pool is nonempty');
 if(created.length){const s=created[0].Snapshot();check([132209,142315].includes(s.runtimeTemplate.templateId)&&s.instanceId!==target.Snapshot().instanceId,'fresh instance from unique initial definitions');check(s.locationMask===8&&s.locationIndex===0&&s.power.basePower===s.runtimeTemplate.power&&s.power.permanentPower===0,'created hand index0 with template state');check(held.Snapshot().locationIndex===1,'existing hand shifts after creation');}
 check(g.random.DrawCount()===(mode==='duplicates'?1:0),'unique definition random count');check(!g.IsFatal()&&!g.IsPending(),'completes');cases.push({id:112211,side,mode});
}
// Sarah may replace an instance with another copy of the SAME template. Her
// original deck snapshot excludes only the returned instance, not its template.
for(const side of [1,2])for(const mode of ['same-template','tier-pool']){
 label='Sarah/'+side+'/'+mode;const g=fixture(side),target=add(g,132209,side,8,0),held=add(g,112101,side,8,1),card=add(g,mode==='same-template'?132209:112101,side,16,0),draws=observe(g);begin(g,112212,side);
 if(mode==='tier-pool'){check(sameSet(g.pendingIds,ids([held])),'only hand tiers present in original deck are offered');choose(g,held);}else{choose(g,target);check(target.Snapshot().locationMask===16&&card.Snapshot().locationMask===8,'same-template distinct instance replacement');check(card.Snapshot().locationIndex===1,'draw appends after existing hand');check(g.random.DrawCount()===3,'insertion + random candidate + singleton random DrawCards');check(draws.length>=2&&draws[0].bound===2&&draws[1].bound===1,'insertion before original candidate selection');}
 check(!g.IsFatal()&&!g.IsPending(),'completes');cases.push({id:112212,side,mode});
}
// Three drawing spies have different source filters, choices and move/draw
// semantics. Counter equality (not merely >0) is explicitly encoded.
for(const id of [122203,152214,162210])for(const side of [1,2])for(const timer of [-1,0,1,2]){
 label=id+'/'+side+'/timer'+timer;const g=fixture(side),held=add(g,132209,side,8,0),grave=add(g,132209,side,32,0),watcher=add(g,162312,side,4,0,10),deck=[132209,112101,113205,142315].map((tid,i)=>add(g,tid,side,16,i));const source=begin(g,id,side,timer);
 if(timer!==1){check(!g.IsPending(),'timer other than1 does not request');check(deck.every((c,i)=>c.Snapshot().locationMask===16&&c.Snapshot().locationIndex===i),'disabled ability does not move deck');check(watcher.Snapshot().power.currentPower===10,'disabled ability emits no draw');}
 else{
  check(deck.every((c,i)=>c.Snapshot().locationMask===16&&c.Snapshot().locationIndex===i),'choice does not provisionally move candidates to hand');check(watcher.Snapshot().power.currentPower===10,'no draw event before selection');check(g.random.DrawCount()===(id===162210?0:3),'shuffle entire four-card eligible list, except Cantarella');
  const options=[...g.pendingIds];check(options.length===2,'first two candidates after graph list operation');if(id===162210)check(sameSet(options,ids(deck.slice(0,2))),'Cantarella uses top2, no shuffle');
  const selected=g.FindCard(options[0]);if(selected&&choose(g,selected)){
   check(selected.Snapshot().locationMask===8&&selected.Snapshot().positionPlayerId===side,'selected returns to actor hand');check(selected.Snapshot().locationIndex===(id===122203?0:1),'Thaler inserts0, DrawCards appends');check(watcher.Snapshot().power.currentPower===11,'Alba reacts to Deck-Hand movement for MoveCards and DrawCards');check(source.Snapshot().timerValue===0,'single-use timer consumed');
   const other=g.FindCard(options[1]);if(id===152214)check(other.Snapshot().locationMask===32&&other.Snapshot().locationIndex===0&&grave.Snapshot().locationIndex===1,'Udalryk unchosen goes directly to grave front');
   if(id===162210)check(other.Snapshot().locationMask===16&&other.Snapshot().locationIndex===2,'Cantarella unchosen goes to actual deck bottom');
   if(id===122203)check(other.Snapshot().locationMask===16,'Thaler unchosen remains in deck');check(g.random.DrawCount()===(id===162210?0:3),'no extra insertion/random draws after choice');
  }
 }
 check(!g.IsFatal(),'no fatal test error');cases.push({id,side,timer});
}
for(const side of [1,2])for(const mode of ['ordinary','own-empty','enemy-empty','enemy-passed']){
 label='Shilard/'+side+'/'+mode;const g=fixture(side),enemy=3-side,own=mode==='own-empty'?null:add(g,132209,side,16,0),other=mode==='enemy-empty'?null:add(g,112101,enemy,16,0),held=add(g,132209,side,8,0),enemyHeld=add(g,132209,enemy,8,0),watch=add(g,162312,side,4,0,10);if(mode==='enemy-passed')g.match[enemy===1?'playerOne':'playerTwo'].hasPassed=true;begin(g,200071,side);
 if(mode!=='ordinary'){check(!g.IsPending(),'requires both decks and opponent not passed');check((!own||own.Snapshot().locationMask===16)&&(!other||other.Snapshot().locationMask===16),'gated branch moves neither deck');}
 else{check(sameSet(g.pendingIds,ids([own,other])),'top eligible card of each deck');check(own.Snapshot().locationMask===16&&other.Snapshot().locationMask===16,'choice has no provisional hand transfer');choose(g,other);check(other.Snapshot().locationMask===8&&other.Snapshot().positionPlayerId===side&&other.Snapshot().locationIndex===1,'chosen foreign instance to own hand end');check(own.Snapshot().locationMask===8&&own.Snapshot().positionPlayerId===enemy&&own.Snapshot().locationIndex===1,'unchosen own instance to enemy hand end');}
 check(watch.Snapshot().power.currentPower===(mode==='ordinary'?12:10),'Alba reacts to both Deck-Hand moves regardless current player');check(g.random.DrawCount()===0,'no random choice or insertion');cases.push({id:200071,side,mode});
}
for(const side of [1,2])for(const mode of ['ordinary','no-special']){
 label='BanArd/'+side+'/'+mode;const g=fixture(side),target=add(g,112101,side,8,0),held=add(g,132209,side,8,1),spell=mode==='ordinary'?add(g,113303,side,16,0):null;add(g,132209,side,16,1);add(g,112101,side,16,2);const draws=observe(g);begin(g,200048,side);
 if(!spell)check(!g.IsPending(),'no Bronze special in deck means no hand request');else{choose(g,target);check(target.Snapshot().locationMask===16,'selected hand return commits before second choice');check(draws[0]?.bound===2,'insertion bound counts Bronze specials, not whole deck');check(sameSet(g.pendingIds,ids([spell])),'second request Bronze special');choose(g,spell);check(spell.Snapshot().locationMask===8&&spell.Snapshot().locationIndex===0&&held.Snapshot().locationIndex===1,'selected special moves to hand front');}
 check(!g.IsFatal(),'no fatal');cases.push({id:200048,side,mode});
}
for(const side of [1,2]){
 label='Bianca/'+side;const g=fixture(side),a=add(g,132209,side,8,0),b=add(g,112101,side,8,1),deck=[add(g,142315,side,16,0),add(g,113205,side,16,1),add(g,132209,side,16,2)];begin(g,122204,side);check(sameSet(g.pendingIds,ids([a,b])),'original hand selection pool');choose(g,a);check(a.Snapshot().locationMask===8,'multi-choice collected before moving first selected card');check(sameSet(g.pendingIds,ids([b])),'second choice excludes selected instance and any newly drawn card');choose(g,b);check(a.Snapshot().locationMask===16&&b.Snapshot().locationMask===16,'both selected original instances returned');check(deck[0].Snapshot().locationMask===8&&deck[1].Snapshot().locationMask===8&&deck[2].Snapshot().locationMask===16,'draw first two from original captured deck');check(g.random.DrawCount()===2,'only two insertion draws, no random replacement');check(!g.IsFatal()&&!g.IsPending(),'completes');cases.push({id:122204,side});
}
for(const side of [1,2]){
 label='IrisCompanions/'+side;const g=fixture(side),held=add(g,132209,side,8,0),grave=add(g,132209,side,32,0),deck=[132209,113205,112101,142315].map((id,i)=>add(g,id,side,16,i));begin(g,200083,side);check(sameSet(g.pendingIds,ids(deck)),'choice list includes entire eligible deck');check(g.random.DrawCount()===3,'choice list shuffled before request');const chosen=deck[0];choose(g,chosen);const discarded=[held,chosen].filter(c=>c.Snapshot().locationMask===32);check(discarded.length===1,'discard from current hand including just drawn instance');if(discarded.length)check(discarded[0].Snapshot().locationIndex===0&&grave.Snapshot().locationIndex===1,'discard at grave front');check(g.random.DrawCount()===4,'shuffle plus one current-hand random discard');check(!g.IsFatal()&&!g.IsPending(),'completes');cases.push({id:200083,side});
}
for(const side of [1,2]){
 label='ElfScout/'+side;const g=fixture(side),a=add(g,132209,side,8,0),held=add(g,112101,side,8,1),deck=[add(g,132209,side,16,0),add(g,112101,side,16,1)],draws=observe(g);a.ChangeBasePower(3,true);a.power.SetPermanentPowerAndArmor(2,5);const before=a.Snapshot();begin(g,201638,side);choose(g,a);check(a.Snapshot().locationMask===16&&JSON.stringify(a.Snapshot().power)===JSON.stringify(before.power),'returned inactive instance retains modified state');check(deck[0].Snapshot().locationMask===8&&deck[0].Snapshot().locationIndex===1,'top original deck instance drawn to hand end');check(draws.length===1&&draws[0].bound===3,'only insertion RNG with Tier15 count+1');check(!g.IsFatal()&&!g.IsPending(),'completes');cases.push({id:201638,side});
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:graphs.map(g=>g.evidence(['RequestCardChoiceNode','MoveCardsNode','DrawCardsNode','DrawAction','SpawnCardNode','GetInitialDeckDefinitions','AGetDeckDefinitions','CardData','ListExt'])),scope:'Ten choice/move branches with actual deploys, both actors, captured lists, current tier, initial unique definitions, choice timing, front/end indexes, filtered insertion bounds and draw-vs-move events. Full UI choice protocol and arbitrary external reactions remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failureCount:failures.length,firstFailures:failures.slice(0,12),cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
