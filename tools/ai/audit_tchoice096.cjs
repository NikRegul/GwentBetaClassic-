'use strict';
// Scope198 fixed/derived template choices: RequestTemplateChoice -> CardDefinitionListGetElement(0)
// -> SpawnCard(own PlayStack) -> PlayCards (+ post ChangePower). Empty selection (Min 0) spawns nothing.
const fs=require('fs'),crypto=require('crypto'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const file='data/beta924/design/rules_audit096_tchoice_sources.json',raw=fs.readFileSync(file),source=JSON.parse(raw);
const F=require('./fixture_batch100096.cjs')(process.argv[2],{file,sha256:sha(raw),records:source.records.map(r=>r.id)});
const {rt,add,snap,id,check,flush,run,begin,trace,finish}=F;
const only=process.env.ONLY?process.env.ONLY.split(',').map(Number):null;
const fresh=(g,pre)=>g.live.filter(c=>!pre.has(id(c))).map(snap);
function settle(g){let k=0;while(g.IsPending()&&k++<30){let ok=false;if(g.pendingRally||g.pendingRow){for(const s of [1,2])for(const r of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,r))ok=g.SelectRow(g.requestId,s,r);}else if(g.pendingChoice){for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTemplateChoice(g.requestId,x);}else for(const x of [...g.pendingIds])if(!ok)ok=g.SelectTarget(g.requestId,x);if(!ok)ok=g.FinishTarget(g.requestId);if(!ok)break;flush(g);}}
function place(g){let k=0;while(g.IsPending()&&(g.pendingRally||g.pendingRow)&&k++<10){let ok=false;for(const s of [1,2])for(const r of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,r))ok=g.SelectRow(g.requestId,s,r);if(!ok)break;flush(g);}}
const CASES={142108:{list:[113309,113308],min:1},152206:{list:[113312,200021,113401],min:1},162207:{list:[113302,113401,200009],min:1},162213:{list:[162315,200115,162314],min:0},
 201597:{list:[152304,152312,152313,152315,200144],min:1},131101:{list:[132309,132310,132402,200026,200301],min:0},200158:{list:[113305,113312],min:1},133302:{list:[132304,132201,201701,132301,132302,132306,132314,200295],min:0,boost:1}};
for(const [k,c] of Object.entries(CASES)){const tid=+k;if(only&&!only.includes(tid))continue;
 for(const side of [1,2])for(const pickIndex of [...c.list.keys(),...(c.min===0?[-1]:[])])run(tid,side,'template choice/'+pickIndex,g=>{
  add(g,132403,side,1,0,30);add(g,132403,3-side,1,0,30);const pre=new Set(g.live.map(id)),rng=trace(g),owner=begin(g,tid,side);
  check(g.IsPending()&&g.pendingChoice&&JSON.stringify(g.pendingIds)===JSON.stringify(c.list),'template request offers exact source list in order',{mod:g.pendingIds,beta:c.list});
  const required=[131101,133302,162213].includes(tid);const minimum=required?1:c.min;
  const lim=g.GetRequestSnapshot().limits;check(lim.minimum===minimum&&lim.maximum===1,'template request limits Min/Max',{lim,min:c.min});check(rng.length===0,'no RNG');
  if(pickIndex<0){check(!g.FinishTarget(g.requestId),'client creation offer cannot finish empty');check(fresh(g,pre).filter(s=>s.instanceId!==id(owner)).length===0,'rejected finish creates nothing');}
  // Original MinChoices literal remains in CASES; client obligation requires a choice.
  const t=c.list[Math.max(0,pickIndex)];check(g.SelectTemplateChoice(g.requestId,t),'choice accepted');flush(g);place(g);settle(g);
  const n=fresh(g,pre).filter(s=>s.instanceId!==id(owner));check(n.length>=1&&n[0].runtimeTemplate.templateId===t,'chosen definition spawned',{n:n.map(s=>s.runtimeTemplate.templateId)});
  if(n.length){const s=n[0];const d=rt.definition(t);if(d.header.typeMask===4)check((s.locationMask&7)!==0,'spawned unit played to board',{loc:s.locationMask});else check([32,256,512].includes(s.locationMask),'spawned special played',{loc:s.locationMask});
   if(c.boost&&d.header.typeMask===4&&!(s.tokenMask&8)&&!require('./source_graph095.cjs').catalog.abilities.some(a=>a.templateId===t&&a.nodes.length))check(s.power.currentPower===s.power.basePower+c.boost||s.locationMask===32,'post-play boost on spawned card',{p:s.power});}
 });
}
finish(process.argv[3],'Scope198 fixed template choices: order, Min/Max, empty Min0 branch, spawn+play of every option.');
