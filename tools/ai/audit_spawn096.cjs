'use strict';
// Scope198 spawn family: expectations written from the Beta graphs and the cited C#
// (SpawnCardNode, SpawnCardsAction, Location.GetValidIndex/GetPositionOnLeft/Right,
// AGetRandomPositionNode, GetLastAvailableIndexNode=-3, MakeCardPosition, KilledTrigger).
const fs=require('fs'),crypto=require('crypto'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const file='data/beta924/design/rules_audit096_spawn_sources.json',raw=fs.readFileSync(file),source=JSON.parse(raw);
const F=require('./fixture_batch100096.cjs')(process.argv[2],{file,sha256:sha(raw),records:source.records.map(r=>r.id)});
const {rt,add,snap,id,check,flush,run,begin,trace,finish}=F;
const only=process.env.ONLY?process.env.ONLY.split(',').map(Number):null;
const want=t=>!only||only.includes(t);
const row=(g,side,loc)=>g.live.map(snap).filter(s=>s.positionPlayerId===side&&s.locationMask===loc&&!s.isWaitingToDie).sort((a,b)=>a.locationIndex-b.locationIndex);
const tids=(g,side,loc)=>row(g,side,loc).map(s=>s.runtimeTemplate.templateId);
const fresh=(g,pre)=>g.live.filter(c=>!pre.has(id(c))).map(snap);
const ids=g=>new Set(g.live.map(id));
function place(g){let k=0;while(g.IsPending()&&k++<10){let ok=false;for(const s of [1,2])for(const r of [2,1,4])if(!ok&&(g.pendingRally||g.pendingRow)&&g.CanSelectRow(g.requestId,s,r))ok=g.SelectRow(g.requestId,s,r);if(!ok)break;flush(g);}}
// adjacency spawns
for(const [tid,left,right] of [[132217,[132316,132316],[]],[200523,[201576,201576],[201576,201576]],[201636,[],[201636]],[132210,[],[132404,132404,132404]]])if(want(tid))for(const side of [1,2])for(const mode of ['open','full'])run(tid,side,'adjacent spawn/'+mode,g=>{
 const a=add(g,132403,side,2,0,30),b=add(g,132403,side,2,1,30);if(mode==='full')for(let i=2;i<7;i++)add(g,132403,side,2,i,30);
 const pre=ids(g),rng=trace(g);const owner=add(g,tid,side,8,0);check(g.Play(side,id(owner),2),'deploy at row end');flush(g);
 const order=tids(g,side,2),oi=row(g,side,2).findIndex(s=>s.instanceId===id(owner)),cap=9-(mode==='full'?7:2)-1;
 const n=fresh(g,pre).filter(s=>s.instanceId!==id(owner));const total=left.length+right.length;
 check(n.length===Math.min(total,Math.max(0,cap)),'spawn count limited by row capacity (SpawnCardsAction drops requests into a full location)',{n:n.map(s=>s.runtimeTemplate.templateId),cap});
 if(mode==='open'){check(JSON.stringify(order.slice(oi-left.length,oi))===JSON.stringify(left)&&JSON.stringify(order.slice(oi+1,oi+1+right.length))===JSON.stringify(right),'spawned at Beta left index/right index+1',{order,oi});}
 check(n.every(s=>s.positionPlayerId===side&&s.locationMask===2),'own row only');check(rng.length===0&&!g.IsPending(),'no RNG/request');
 if(tid===201636)check(n.every(s=>(s.tokenMask&512)!==0),'copy gets Doomed512 (ChangeTokens Add)');
});
// Harald: left Wilfred, right Wilhelm, enemy same row/index Wilmar with Disloyal128
if(want(200043))for(const side of [1,2])run(200043,side,'three brothers',g=>{
 add(g,132403,side,2,0,30);for(let i=0;i<4;i++)add(g,132403,3-side,2,i,30);const pre=ids(g),owner=add(g,200043,side,8,0);check(g.Play(side,id(owner),2),'deploy at index1');flush(g);
 const order=tids(g,side,2),oi=order.indexOf(200043);check(order[oi-1]===201573&&order[oi+1]===201574,'Wilfred left, Wilhelm right',{order});
 const en=row(g,3-side,2),w=en.find(s=>s.runtimeTemplate.templateId===201572);check(!!w&&w.locationIndex===oi&&(w.tokenMask&128)!==0,'Wilmar opponent row at owner current index (after left spawn) with Disloyal',{en:en.map(s=>[s.runtimeTemplate.templateId,s.locationIndex,s.tokenMask]),oi});
 check(fresh(g,pre).length===4&&!g.IsPending(),'exactly three spawns');
});
// Hjalmar: Lord of Undvik on opponent side, owner location, end index, Disloyal
if(want(152101))for(const side of [1,2])for(const r of [1,2,4])run(152101,side,'undvik/'+r,g=>{
 add(g,132403,3-side,r,0,30);const pre=ids(g),owner=add(g,152101,side,8,0);check(g.Play(side,id(owner),r),'deploy');flush(g);place(g);
 const n=fresh(g,pre).filter(s=>s.instanceId!==id(owner));check(n.length===1&&n[0].runtimeTemplate.templateId===152401&&n[0].positionPlayerId===3-side&&n[0].locationMask===r&&n[0].locationIndex===1&&(n[0].tokenMask&128)!==0,'Undvik enemy same row last index Disloyal',{n:n.map(s=>[s.runtimeTemplate.templateId,s.positionPlayerId,s.locationMask,s.locationIndex,s.tokenMask])});
});
// Leshen: 3 wolves own Melee end; Set fog2 on opponent row with Leshen's location
if(want(132103))for(const side of [1,2])for(const r of [2,4])run(132103,side,'wolves/'+r,g=>{
 add(g,132403,side,1,0,30);g.weather.ApplyHazard(3-side,r,1);flush(g);const pre=ids(g),owner=add(g,132103,side,8,0);check(g.Play(side,id(owner),r),'deploy');flush(g);
 const m=tids(g,side,1);check(JSON.stringify(m)===JSON.stringify([132403,132403,132403,132403]),'three wolves appended to own Melee',{m});
 check(g.weather.Token(3-side,r)===2&&g.weather.Token(side,r)===0,'Set fog on opponent row matching Leshen row',{t:g.weather.Token(3-side,r)});
});
// Deck/stack spawns
for(const [tid,def,where] of [[162401,200219,'enemyDeckTop'],[132220,200067,'stackPlay'],[142304,143301,'stackPlay'],[162302,162402,'stackPlay'],[200144,152406,'stackPlay'],[152201,152403,'stackPlay']])if(want(tid))for(const side of [1,2])run(tid,side,'spawn '+where,g=>{
 for(let i=0;i<3;i++)add(g,132403,3-side,16,i,undefined);const pre=ids(g),owner=add(g,tid,side,8,0),rng=trace(g);check(g.Play(side,id(owner),2),'deploy');flush(g);
 let n=fresh(g,pre).filter(s=>s.instanceId!==id(owner));
 if(where==='enemyDeckTop'){check(n.length===1&&n[0].runtimeTemplate.templateId===def&&n[0].positionPlayerId===3-side&&n[0].locationMask===16&&n[0].locationIndex===0,'spawned into opponent deck index0',{n:n.map(s=>[s.runtimeTemplate.templateId,s.positionPlayerId,s.locationMask,s.locationIndex])});check(!g.IsPending(),'no request');return;}
 const t=rt.definition(def),unit=t.header.typeMask===4;
 if(unit){check(g.IsPending()&&!!g.pendingRally,'spawned unit handed to PlayCards placement',{msg:g.GetMessage()});const sides=[1,2].filter(s=>[1,2,4].some(r=>g.CanSelectRow(g.requestId,s,r)));const enemyPlaced=E_place(def);check(JSON.stringify(sides)===JSON.stringify([enemyPlaced?3-side:side]),'placement side follows the spawned template placement',{sides});place(g);}
 n=fresh(g,pre).filter(s=>s.instanceId!==id(owner));check(n.length===1&&n[0].runtimeTemplate.templateId===def,'exactly one spawned definition',{n:n.map(s=>s.runtimeTemplate.templateId)});
 if(unit)check((n[0].locationMask&7)!==0,'spawned unit played on board');else check(n[0].locationMask===32||n[0].locationMask===512||n[0].locationMask===256,'spawned special played/resolving',{loc:n[0].locationMask});
});
function E_place(def){const {catalog}=require('./source_graph095.cjs');const t=catalog.templates.find(t=>t.templateId===def);return +t.placement.PlayerSide===0&&+t.placement.OpponentSide!==0;}
// Killed spawns at random available own row (GetRandomLastAvailablePosition over Active of owner position player)
for(const [tid,def] of [[112209,200320],[152104,152402]])if(want(tid))for(const side of [1,2])for(const full of [false,true])run(tid,side,'deathwish random row/'+(full?'melee full':'open'),g=>{
 const victim=add(g,tid,side,2,0,5);if(full)for(let i=0;i<9;i++)add(g,132403,side,1,i,30);const pre=ids(g),rng=trace(g);g.QueueDestroy(victim);flush(g);place(g);
 const n=fresh(g,pre),rows=full?[2,4]:[1,2,4],d=rng.find(x=>x.n===rows.length);
 check(n.length===1&&n[0].runtimeTemplate.templateId===def,'one deathwish spawn',{n:n.map(s=>s.runtimeTemplate.templateId),rng});
 if(n.length===1)check(!!d&&n[0].locationMask===rows[d.v]&&n[0].positionPlayerId===snap(victim).positionPlayerId,'RNG Next(available rows) picks non-full row of the dead card position player',{loc:n[0].locationMask,rng,side:n[0].positionPlayerId,victim:snap(victim).positionPlayerId});
});
// Wilmar deathwish: bear for the opponent of Wilmar's side only when that player is current
if(want(201572))for(const side of [1,2])for(const turn of [1,2])run(201572,side,'wilmar/turn'+turn,g=>{
 g.match.currentPlayerId=turn;const w=add(g,201572,side,2,0,3);const pre=ids(g),rng=trace(g);g.QueueDestroy(w);flush(g);place(g);
 const n=fresh(g,pre);if(3-side===turn){check(n.length===1&&n[0].runtimeTemplate.templateId===152406&&n[0].positionPlayerId===3-side&&rng.some(x=>x.n===3),'bear for current opponent-of-position player',{n:n.map(s=>[s.runtimeTemplate.templateId,s.positionPlayerId]),rng});}
 else check(n.length===0,'no bear when opponent-of-position is not current',{n:n.map(s=>s.runtimeTemplate.templateId)});
});
// D'ao: two Lesser D'ao appended to its row (Current or From position), both kill kinds
if(want(132213))for(const side of [1,2])for(const how of ['destroy','damage'])run(132213,side,'dao/'+how,g=>{
 add(g,132403,side,4,0,30);const d=add(g,132213,side,4,1,2);const pre=ids(g);if(how==='destroy')g.QueueDestroy(d);else g.QueuePower(d,-5,false);flush(g);
 const n=fresh(g,pre);check(n.length===2&&n.every(s=>s.runtimeTemplate.templateId===132405&&s.positionPlayerId===side&&s.locationMask===4),'two Lesser Dao in the dead card row',{n:n.map(s=>[s.runtimeTemplate.templateId,s.positionPlayerId,s.locationMask]),loc:snap(d).locationMask});
});
finish(process.argv[3],'Scope198 spawn family: adjacency/capacity, opponent side/index/tokens, deck top, stack spawn + PlayCards placement, deathwish random rows/conditions.');
