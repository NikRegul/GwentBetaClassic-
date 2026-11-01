'use strict';
// Scope198 multi-step flows (draw/move/shuffle/choice/play/power) checked against the
// independent Beta evaluator (beta_list_eval096) with a simulated pre-ability state.
const fs=require('fs'),crypto=require('crypto'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const E=require('./beta_list_eval096.cjs'),{catalog}=require('./source_graph095.cjs');
const file='data/beta924/design/rules_audit096_flow_sources.json',raw=fs.readFileSync(file),source=JSON.parse(raw);
const F=require('./fixture_batch100096.cjs')(process.argv[2],{file,sha256:sha(raw),records:source.records.map(r=>r.id)});
const {rt,add,snap,id,check,flush,run,trace,finish}=F;
const only=process.env.ONLY?process.env.ONLY.split(',').map(Number):null;
const ZONES={1:[132209,132310],2:[122209,142306],16:[132403,113301,132209,112103,132310,113302,142306,201576],8:[112405,200171,113312],32:[132403,132310,122209,142306,113301]};
const EXTRA={152305:{16:[152305,152305]},152213:{}};
function populate(g,tid,side,mode){
 const put=(t,s,l)=>{const n=g.live.filter(c=>{const x=snap(c);return x.positionPlayerId===s&&x.locationMask===l;}).length;return add(g,t,s,l,n);};
 if(mode==='empty'){return;}
 for(const s of [side,3-side])for(const [l,list] of Object.entries(ZONES))for(const t of (s===side?list:list.slice(0,3)))put(t,s,+l);
 for(const [l,list] of Object.entries((EXTRA[tid]||{})))for(const t of list)put(t,side,+l);
 put(132403,side,1);put(132403,3-side,1);
 if(tid===201631){put(200164,side,64);}
}
function placeAll(g){let k=0;while(g.IsPending()&&(g.pendingRally||g.pendingRow)&&k++<20){let ok=false;for(const s of [1,2])for(const r of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,r))ok=g.SelectRow(g.requestId,s,r);if(!ok)break;flush(g);}}
function settle(g){let k=0;while(g.IsPending()&&k++<60){let ok=false;if(g.pendingRally||g.pendingRow||g.pendingLeader){for(const s of [1,2])for(const row of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,row))ok=g.SelectRow(g.requestId,s,row);}else if(g.pendingChoice){for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTemplateChoice(g.requestId,x);}else for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTarget(g.requestId,x);if(!ok)ok=g.FinishTarget(g.requestId);if(!ok)break;flush(g);}}
for(const r of source.records){if(only&&!only.includes(r.id))continue;
 for(const side of [1,2])for(const mode of ['rich','first','empty','skip'])run(r.id,side,'flow/'+mode,g=>{
  const firstPick=mode==='first';
  populate(g,r.id,side,mode==='first'?'rich':mode);const owner=add(g,r.id,side,8,g.live.filter(c=>{const x=snap(c);return x.positionPlayerId===side&&x.locationMask===8;}).length);
  const pre=g.live.map(snap),rng=trace(g);if(r.id===200162)g.mulliganReactions=true;check(g.Play(side,id(owner),2),'real hand deploy');flush(g);
  const post=snap(owner),ctx={ownerId:id(owner),hasPassed:p=>(p===1?g.match.playerOne:g.match.playerTwo).hasPassed,rowToken:(p,l)=>g.weather.Token(p,l),initialDeck:p=>(p===1?g.nilfInitialOne:g.nilfInitialTwo).slice(),draws:rng,optionalDraws:mode!=='rich',cards:()=>pre.map(s=>s.instanceId===post.instanceId?{...post,isInExecutionStack:true,isWaitingToDie:false}:s)};
  let x;try{x=E.run(r.id,ctx);}catch(e){check(false,'independent evaluation: '+e.message,{rng});return;}
  let steps=0,skipped=false;
  while(x.request&&steps++<6){
   const q=x.request;
   // Reviewed PlayCards/SpawnCard branches: the live client requires selection.
   // Keep original q.min and source graphs intact, including optional non-play targets.
   const required=!q.targets&&[122205,131102,142107,200102,200162,200539,201621].includes(r.id);
   if(required&&q.min===0&&mode==='skip'&&!skipped){check(!g.FinishTarget(g.requestId),'play offer rejects empty finish');skipped=true;}
   const clientMin=required?Math.max(1,q.min):q.min;check(rng.length>=x.draws,'RNG reached Beta draws before request',{mod:rng.length,beta:x.draws});
   if(q.templates){const pool=((x.log||[]).filter(l=>l.pool).pop()||{}).pool||q.valid;
    if(q.orderUncertain)check(g.IsPending()&&g.pendingChoice&&g.pendingIds.length===q.valid.length&&g.pendingIds.every(t=>pool.includes(t))&&new Set(g.pendingIds).size===g.pendingIds.length,'template request: Beta pool members, exact count (native dictionary order open)',{mod:g.pendingIds,beta:q.valid,pool});
    else check(g.IsPending()&&g.pendingChoice&&JSON.stringify(g.pendingIds)===JSON.stringify(q.valid),'template request offers exact Beta list/order',{mod:g.pendingIds,beta:q.valid});
    const lim=g.GetRequestSnapshot().limits;check(lim.minimum===clientMin&&lim.maximum<=Math.max(1,q.max),'template limits',{lim,beta:[q.min,q.max]});
    if(mode==='skip'&&clientMin===0&&!skipped){skipped=true;check(g.FinishTarget(g.requestId),'Min0 template choice can finish empty');flush(g);x=x.resume([]);continue;}
    const src=q.orderUncertain?g.pendingIds:q.valid,pick=firstPick?src[0]:src[src.length-1];check(g.SelectTemplateChoice(g.requestId,pick),'template choice accepted',{pick});flush(g);x=x.resume([pick]);placeAll(g);continue;}
   if(q.targets)check(g.IsPending()&&!g.pendingChoice&&JSON.stringify([...g.pendingIds].sort())===JSON.stringify([...q.valid].sort()),'target request offers exact Beta target set',{mod:g.pendingIds,beta:q.valid});
   else check(g.IsPending()&&!g.pendingChoice&&JSON.stringify(g.pendingIds)===JSON.stringify(q.valid),'request offers exact Beta list/order',{mod:g.pendingIds,beta:q.valid});
   const lim=g.GetRequestSnapshot().limits,mn=Math.min(clientMin,q.valid.length),mx=Math.min(q.max,q.valid.length);
   check((lim.minimum===mn||mn>1&&lim.minimum===1)&&(lim.maximum===mx||lim.maximum===1&&mx>1),'request limits (UI may drain a fixed multi-pick one by one)',{mod:lim,beta:[mn,mx]});
   if(mode==='skip'&&mn===0&&!skipped){skipped=true;check(g.FinishTarget(g.requestId),'Min0 request can finish empty');flush(g);x=x.resume([]);continue;}
   if(q.targets){const picks=[];for(let k=0;k<q.min;k++){const open=q.valid.filter(v=>!picks.includes(v)),p=firstPick?open[0]:open[open.length-1];if(!g.SelectTarget(g.requestId,p)){check(false,'target accepted',{p});break;}picks.push(p);flush(g);}x=x.resume(picks);placeAll(g);continue;}
   const picks=[];const want=Math.max(mn,Math.min(mx,mode==='skip'?mn:mx));
   for(let k=0;k<want;k++){const open=q.valid.filter(v=>!picks.includes(v));const p=firstPick?open[0]:open[open.length-1];check(g.IsPending()&&g.pendingIds.includes(p),'next pick still offered',{p,mod:g.pendingIds});if(!g.SelectTarget(g.requestId,p)){check(false,'pick accepted');break;}picks.push(p);flush(g);}
   x=x.resume(picks);placeAll(g);
  }
  check(!x.request,'request chain bounded');settle(g);
  const preIds=new Set(pre.map(s=>s.instanceId)),news=g.live.filter(c=>!preIds.has(id(c))),map=new Map();
  for(const a of x.acts||[])if(a.spawn)for(const f of a.spawn.cards){const c=news.find(c=>![...map.values()].includes(c)&&snap(c).runtimeTemplate.templateId===a.spawn.def);if(c)map.set(f,c);}
  const cardOf=(g,i)=>typeof i==='string'?map.get(i):g.live.find(c=>id(c)===i);
  for(const a of x.acts||[])if(a.spawn){check(a.spawn.cards.every(f=>map.has(f)),'every Beta spawn exists in the mod',{def:a.spawn.def,n:a.spawn.cards.length,news:news.map(c=>snap(c).runtimeTemplate.templateId)});
   for(const f of a.spawn.cards){const c=map.get(f);if(!c)continue;const s=snap(c),played=(x.acts||[]).some(b=>b.play&&b.play.includes(f));if(!played)check(s.positionPlayerId===a.spawn.pos.player&&s.locationMask===a.spawn.pos.loc,'spawn destination',{s:[s.positionPlayerId,s.locationMask],pos:a.spawn.pos});}}
  const totalSpawn=(x.acts||[]).reduce((n,a)=>n+(a.spawn?a.spawn.cards.length:0),0);check(news.length===totalSpawn||news.length>totalSpawn&&(x.acts||[]).some(a=>a.play),'no extra created cards',{news:news.map(c=>snap(c).runtimeTemplate.templateId),beta:totalSpawn});
  for(const a of x.acts||[]){const k=Object.keys(a)[0],e=a[k];
   if(k==='draw')for(const c of e.cards){const s=snap(cardOf(g,c));check(s.locationMask===8||s.locationMask!==16,'Beta-drawn card left the deck top',{c,loc:s.locationMask});}
   if(k==='move')for(const m of e.res){const s=snap(cardOf(g,m.id)),doomed=(E.T.get(s.runtimeTemplate.templateId).fields.Tokens&512)&&e.to.loc===32;const fin=x.sim&&x.sim.find(c=>c.instanceId===m.id),later=fin&&(fin.locationMask!==e.to.loc||fin.positionPlayerId!==e.to.player),playedLater=(x.acts||[]).some(b=>b.play&&b.play.includes(m.id));if(later||playedLater){if(!playedLater)check(s.positionPlayerId===fin.positionPlayerId&&s.locationMask===fin.locationMask,'moved card final zone follows later Beta actions',{m,s:[s.positionPlayerId,s.locationMask],fin:[fin.positionPlayerId,fin.locationMask]});continue;}check(s.positionPlayerId===e.to.player&&s.locationMask===(doomed?512:e.to.loc),'moved to Beta destination zone',{m,s:[s.positionPlayerId,s.locationMask,s.locationIndex],to:e.to});if(e.to.loc===16){const fin=x.sim&&x.sim.find(c=>c.instanceId===m.id);check(s.locationIndex===(fin?fin.locationIndex:m.index),'exact deck insertion index, including multi-card MoveCards',{mod:s.locationIndex,beta:fin?fin.locationIndex:m.index});}}
   if(k==='spawn'||k==='categories'||k==='rowTokens'||k==='timer')continue;
   if(k==='tokens'){for(const t of e.targets){const c=cardOf(g,t);if(!c)continue;const s=snap(c);if(e.op===0)check((s.tokenMask&e.tokens)===e.tokens||s.locationMask===512||s.locationMask===32,'tokens Add on Beta target',{t,tok:s.tokenMask,want:e.tokens});}continue;}
   if(k==='destroy')for(const t of e.targets){const s=snap(cardOf(g,t));check(e.removal===1?s.locationMask===512:(s.locationMask===32||s.locationMask===512),'destroy/banish applied',{t,loc:s.locationMask,removal:e.removal});}
   if(k==='play')for(const c of e.cards||e){if(!cardOf(g,c))continue;const s=snap(cardOf(g,c));check((s.locationMask&7)||[32,256,512].includes(s.locationMask),'played',{c,loc:s.locationMask});}
   if(k==='power'){for(const t of e.targets){const s=snap(cardOf(g,t)),tp=E.T.get(s.runtimeTemplate.templateId).fields;if(e.op===1){const p0=pre.find(p=>p.instanceId===t);const total=(x.acts||[]).filter(b=>b.power&&b.power.op===1&&b.power.targets.includes(t)).reduce((a,b)=>a+b.power.amount,0);if(p0&&(s.locationMask&7)&&!e._seen){e._seen=true;const ar=p0.power.armor,abs=e.ignoreArmor?0:Math.min(ar,total);check(s.power.currentPower===p0.power.currentPower-(total-abs)&&s.power.armor===ar-abs,'damage exact (armor first, all hits)',{p0:p0.power,p:s.power,total});}}
    else if(e.type===1)check(s.power.basePower===tp.Power+e.amount,'strengthen BASE exact',{p:s.power,want:tp.Power+e.amount});else check(s.power.currentPower===tp.Power+e.amount,'boost CURRENT exact',{p:s.power,want:tp.Power+e.amount,loc:s.locationMask});}}
  }
  if(mode!=='rich'||true){const touched=new Set([id(owner)]);for(const a of x.acts||[]){const e=Object.values(a)[0];for(const c of (Array.isArray(e)?e:(e.cards||e.targets||e.res&&e.res.map(m=>m.id)||[])))touched.add(c);}
   const chosenAbility=[...touched].some(c=>c!==id(owner)&&catalog.abilities.some(a=>a.templateId===snap(cardOf(g,c)).runtimeTemplate.templateId&&a.nodes.length));
   const moved=pre.filter(s=>!touched.has(s.instanceId)&&(()=>{const n=snap(cardOf(g,s.instanceId));return n.locationMask!==s.locationMask||n.positionPlayerId!==s.positionPlayerId;})());
   check(moved.length===0||chosenAbility,'no card outside the Beta action set changed zone',{moved:moved.map(s=>[s.instanceId,s.runtimeTemplate.templateId,s.locationMask]),acts:x.acts,rng});}
 });
}
finish(process.argv[3],'Scope198 flow family: draw/move/shuffle/choice/play/power primary chains vs independent evaluator.');
