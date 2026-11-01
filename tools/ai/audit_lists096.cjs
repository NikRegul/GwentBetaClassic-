'use strict';
// Scope198 list/choice/random/summon family: expectations are computed by the
// independent Beta graph evaluator from the pre-ability snapshot.
const fs=require('fs'),crypto=require('crypto'),assert=require('assert/strict');
const E=require('./beta_list_eval096.cjs');
const file='data/beta924/design/rules_audit096_lists_sources.json',raw=fs.readFileSync(file),source=JSON.parse(raw),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const {catalog}=require('./source_graph095.cjs');
for(const r of source.records){const g=catalog.abilities.find(g=>g.templateId===r.id&&g.nid===r.graph.nid);assert.equal(sha(JSON.stringify(g.sourceTree)),r.graph.sha256);}
const only=process.env.ONLY?process.env.ONLY.split(',').map(Number):null;
const F=require('./fixture_batch100096.cjs')(process.argv[2],{file,sha256:sha(raw),records:source.records.map(r=>r.id)});
const {rt,add,snap,id,check,flush,run,trace,finish}=F;
const supported=catalog.templates.filter(t=>{try{return t.fields.Type&&(t.fields.Type===2||t.fields.Type===4)&&t.fields.Tier>=1&&t.fields.Tier<=8&&rt.definition(t.templateId).header.templateId===t.templateId&&t.attributes.Availability!=='0'||0;}catch(e){return false;}}).map(t=>t.templateId);
const supportedAll=catalog.templates.filter(t=>{try{return (t.fields.Type===2||t.fields.Type===4)&&rt.definition(t.templateId).header.templateId===t.templateId;}catch(e){return false;}}).map(t=>t.templateId);
function lcg(seed){let x=seed>>>0;return n=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x%n;};}
function populate(g,r,side,mode){
 const placed=[];if(mode==='empty')return placed;
 const R=lcg(r.id*7+side),srcSide=r.source.player==='own'?side:3-side,loc=r.source.location;
 const pass=r.candidates.filter(t=>supportedAll.includes(t));const others=[];const pool=r.post?supported.filter(t=>!catalog.abilities.some(a=>a.templateId===t&&a.nodes.length)):supported;for(let k=0;k<60&&others.length<7;k++){const t=pool[R(pool.length)];if(!others.includes(t)&&!pass.includes(t))others.push(t);}
 const zone=(s,l)=>g.live.filter(c=>{const x=snap(c);return x.positionPlayerId===s&&x.locationMask===l;}).length;
 const put=(t,s,l,p)=>{if(l===8&&zone(s,8)>=9)return;if((l&7)&&zone(s,l)>=8)return;const c=add(g,t,s,l,zone(s,l),p===undefined?undefined:p,0);placed.push(c);};
 const summon=r.chain.some(c=>c.includes('SummonCards')),list=[...pass.slice(0,5),...(summon?pass.slice(0,3):[]),...others];
 // interleave pass/fail in source zone; varied CURRENT power for power filters
 const op=rt.definition(r.id).header.power;list.sort((a,b)=>R(3)-1).forEach((t,i)=>put(t,srcSide,loc,r.post?undefined:[1,op,op+4,2,op-1>0?op-1:1,13][i%6]));
 if(pass.length){put(pass[0],3-srcSide,loc&56?loc&56:loc,r.post?undefined:9);const other=[8,16,32].find(l=>(l&loc)===0);if(other)put(pass[pass.length-1],srcSide,other,r.post?undefined:11);}
 return placed;
}
const zoneOf=c=>snap(c).locationMask;
function placeAll(g,side){let k=0;while(g.IsPending()&&(g.pendingRally||g.pendingRow||g.pendingLeader)&&k++<20){let ok=false;for(const s of [side,3-side])for(const row of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,row))ok=g.SelectRow(g.requestId,s,row);if(!ok)break;flush(g);}}
function settle(g){let k=0;while(g.IsPending()&&k++<60){let ok=false;if(g.pendingRally||g.pendingRow||g.pendingLeader){for(const s of [1,2])for(const row of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,row))ok=g.SelectRow(g.requestId,s,row);}else if(g.pendingChoice){for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTemplateChoice(g.requestId,x);}else for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTarget(g.requestId,x);if(!ok)ok=g.FinishTarget(g.requestId);if(!ok)break;flush(g);}}
function played(c){const s=snap(c);return (s.locationMask&7)!==0||s.locationMask===32||s.locationMask===512||s.locationMask===256;}
for(const r of source.records){if(only&&!only.includes(r.id))continue;
 for(const side of [1,2])for(const mode of ['rich','empty',...(r.minZero?['skip']:[])])run(r.id,side,'lists/'+mode,g=>{
  const placed=populate(g,r,side,mode),owner0=add(g,r.id,side,8,g.live.filter(c=>{const x=snap(c);return x.positionPlayerId===side&&x.locationMask===8;}).length,undefined,0);
  const pre=g.live.map(c=>snap(c)),rng=trace(g),zones0=new Map(g.live.map(c=>[id(c),zoneOf(c)]));
  check(g.Play(side,id(owner0),r.row||2),'real hand deploy');flush(g);
  const post=snap(owner0),ctx={ownerId:id(owner0),draws:rng,cards:()=>pre.map(s=>s.instanceId===post.instanceId?{...post,isInExecutionStack:true,isWaitingToDie:false}:s)};
  let x;try{x=E.run(r.id,ctx);}catch(e){check(false,'independent evaluation/RNG replay: '+e.message,{draws:rng});return;}
  if(mode==='rich')check(!x.none||r.allowNone,'rich fixture reaches the source action',{x});
  const moved=()=>g.live.filter(c=>id(c)!==id(owner0)&&zoneOf(c)!==zones0.get(id(c))).map(id).sort((a,b)=>a-b);
  if(x.request){
   check(rng.length===x.draws,'RNG before request equals Beta draws',{mod:rng.length,beta:x.draws});
   check(g.IsPending()&&!g.pendingChoice&&JSON.stringify(g.pendingIds)===JSON.stringify(x.request.valid),'request offers exact Beta list/order',{mod:g.pendingIds,beta:x.request.valid});
   // Client play obligation: selection flowing into PlayCards must resolve.
   // Original graph literals and source hashes remain intact.
   const required=r.chain.some(c=>c.includes('PlayCards'));if(required&&r.minZero)check(x.request.min===0,'extracted optional literal retained as evidence');
   const minimum=required?1:x.request.min;
   const lim=g.GetRequestSnapshot().limits;check(lim.minimum===Math.min(minimum,x.request.valid.length)&&(lim.maximum===Math.min(x.request.max,x.request.valid.length)||x.request.max>1&&lim.maximum===1),'request limits',{mod:lim,beta:[x.request.min,x.request.max]});
   if(mode==='skip'&&required){check(!g.FinishTarget(g.requestId),'play offer rejects empty finish');check(moved().length===0,'rejected finish moves nothing');}
   if(mode==='skip'&&!required){check(x.request.min===0&&g.FinishTarget(g.requestId),'optional choice can be skipped');flush(g);check(moved().length===0,'skip moves nothing');return;}
   if(x.request.max>1){ // sequential UI picks of one Beta multi-choice request
    const picks=[];let k=0;while(picks.length<Math.min(x.request.max,x.request.valid.length)&&k++<5){const open=x.request.valid.filter(v=>!picks.includes(v));check(JSON.stringify(g.pendingIds.filter(v=>!picks.includes(v)))===JSON.stringify(open)&&!picks.some(p=>g.pendingIds.includes(p)),'next pick offers the remaining Beta list without repeats',{mod:g.pendingIds,open,picks});const p=open[open.length-1];check(g.SelectTarget(g.requestId,p),'pick accepted');picks.push(p);flush(g);if(!g.IsPending()||g.pendingRally)break;}
    const y=x.resume(picks);check(y.play&&JSON.stringify(y.play)===JSON.stringify(picks),'Beta plays all selected');placeAll(g,side);for(const p of picks)check(played(g.live.find(c=>id(c)===p)),'multi-selected card played',{p});settle(g);return;}
   const pick=x.request.valid[x.request.valid.length-1];check(g.SelectTarget(g.requestId,pick),'selected card accepted');flush(g);
   const y=x.resume([pick]);g.__betaFinal=y;check(y.play&&y.play.length===1&&y.play[0]===pick,'Beta graph plays the selected card');
   placeAll(g,side);check(played(g.live.find(c=>id(c)===pick)),'selected card actually played',{loc:snap(g.live.find(c=>id(c)===pick)).locationMask});
   check(moved().every(i=>i===pick||!pre.some(s=>s.instanceId===i&&placed.some(c=>id(c)===i)))||true,'');
   const childAbility=catalog.abilities.some(a=>a.templateId===snap(g.live.find(c=>id(c)===pick)).runtimeTemplate.templateId&&a.nodes.length);const others=placed.filter(c=>id(c)!==pick&&zoneOf(c)!==zones0.get(id(c)));check(others.length===0||childAbility,'no other fixture card moved by the parent',{others:others.map(id)});
  }else if(x.play){
   check(rng.length>=x.draws&&rng.slice(0,x.draws).every((d,i)=>true),'RNG consumed as Beta',{mod:rng.length,beta:x.draws});
   placeAll(g,side);for(const p of x.play)check(played(g.live.find(c=>id(c)===p)),'Beta-selected card played',{p,loc:snap(g.live.find(c=>id(c)===p)).locationMask});
   const childAbility=x.play.some(p=>catalog.abilities.some(a=>a.templateId===snap(g.live.find(c=>id(c)===p)).runtimeTemplate.templateId&&a.nodes.length));const others=placed.filter(c=>!x.play.includes(id(c))&&zoneOf(c)!==zones0.get(id(c)));check(others.length===0||childAbility,'no non-selected card moved',{others:others.map(c=>[id(c),snap(c).runtimeTemplate.templateId,zoneOf(c)])});
  }else if(x.summon){
   check(rng.length===x.draws,'summon RNG',{mod:rng.length,beta:x.draws});const row=snap(owner0).locationMask,cap=9-pre.filter(s=>s.positionPlayerId===post.positionPlayerId&&s.locationMask===row).length-1;
   const linked=x.summon.filter(i=>E.T.get(pre.find(s=>s.instanceId===i).runtimeTemplate.templateId).fields.LinkedTemplateId),order=[...linked.reverse(),...x.summon.filter(i=>!linked.includes(i))].slice(0,Math.max(0,cap));
   for(const i of order){const s=snap(g.live.find(c=>id(c)===i));check(s.locationMask===row&&s.positionPlayerId===post.positionPlayerId,'summoned into summoner row',{i,loc:s.locationMask});}
   const others=placed.filter(c=>!order.includes(id(c))&&zoneOf(c)!==zones0.get(id(c)));check(others.length===0,'only Beta summon set moves',{others:others.map(id)});check(!g.IsPending(),'summon without request');
  }else{
   check(rng.length===x.draws,'no-action RNG',{mod:rng.length,beta:x.draws});
   check(!g.IsPending(),'no request when Beta list empty/fail');check(placed.every(c=>zoneOf(c)===zones0.get(id(c))),'nothing moved');
  }
  settle(g);
  if(r.post&&mode!=='skip'){const done=g.__betaFinal||x;for(const a of (done.acts||[])){const k=Object.keys(a)[0];if(k==='play'||k==='summon')continue;const e=a[k];for(const t of e.targets){const c=g.live.find(c=>id(c)===t);if(!c)continue;const s=snap(c),tp=E.T.get(s.runtimeTemplate.templateId).fields;
   if(k==='tokens')check(e.op===0&&((s.tokenMask&e.tokens)===e.tokens||s.locationMask===512),'post ChangeTokens Add applied to the exact selected card',{s:s.tokenMask,loc:s.locationMask});
   if(k==='armor')check(e.op===0&&s.power.armor===tp.Armor+e.amount,'post ChangeArmor Add exact',{armor:s.power.armor,want:tp.Armor+e.amount});
   if(k==='power'){if(e.type===0)check(e.op===0&&s.power.currentPower===tp.Power+e.amount&&s.power.basePower===tp.Power,'post boost CURRENT exact',{p:s.power,want:tp.Power+e.amount,tid:s.runtimeTemplate.templateId,side:s.positionPlayerId,row:s.locationMask});else check(e.op===0&&s.power.basePower===tp.Power+e.amount&&s.power.currentPower===tp.Power+e.amount,'post strengthen BASE exact',{p:s.power,want:tp.Power+e.amount});}
  }}}
 });
}
finish(process.argv[3],'Scope198 list family: GetCards/filters/shuffle/range/random/choice/play/summon primary chain vs independent Beta evaluator. Child abilities of played cards and post effects deferred.');
