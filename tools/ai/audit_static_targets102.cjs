'use strict';
// Audit: for every card whose ability asks for a unit target, compare the AI's
// own choice with the best first pick found by trying every candidate on a
// clone (later picks are finished by the AI itself). 16 board units, so the
// exact-choice simulation cap (14) is exceeded and the static score decides.
// Usage: node audit_static_targets102.cjs <rules-dir> <out.jsonl> [offset] [limit] [ids]
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
const out=process.argv[3],offset=+(process.argv[4]||0),limit=+(process.argv[5]||100000);
let ids=process.argv[6]?process.argv[6].split(',').map(Number):null;
if(!ids){const src=fs.readFileSync(path.join(__dirname,'../../BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'),'utf8');
 ids=[...new Set([...src.matchAll(/value\.header\.templateId = (\d+);/g)].map(m=>+m[1]).filter(id=>id>1000))].sort((a,b)=>a-b);}
function lead(g){return g.Score(2)-g.Score(1);}
function prepare(g){let t=0;while(!g.AiPreparationStep())if(++t>12000)throw Error('stalled');}
// Variants: plain; own Raging Berserker; own boosted / enemy damaged; enemy armour.
function board(id,variant){
 const g=fixture(2);g.externalPolicyMask=0;g.match.roundNumber=2;
 let own=[2,4,6,8,10,3,5,7],enemy=[3,5,7,9,11,4,6,8],armor=0;
 if(variant==='boosted'){own=own.map(p=>p+8);enemy=enemy.map(p=>Math.max(1,p-2));}
 if(variant==='armour')armor=3;
 own.forEach((p,i)=>add(g,i===3&&variant==='berserker'?152301:112405,2,[1,2,4][i%3],Math.floor(i/3),p));
 enemy.forEach((p,i)=>add(g,112405,1,[1,2,4][i%3],Math.floor(i/3),p,i%2?armor:0));
 const src=add(g,id,2,8);add(g,112405,1,8);add(g,112405,1,8);return {g,src};}
const VARIANTS=(process.env.VARIANTS||'plain,berserker,boosted,armour').split(',');
for(const id of ids.slice(offset,offset+limit))for(const variant of VARIANTS){
 const r={id,variant};
 try{
  let {g,src}=board(id,variant);const base=rt.cloneSession(g),l0=lead(g);
  // Force the play; the AI policy still makes every target choice.
  const logs=[];rt.host.log=s=>logs.push(s);let row=0;
  try{for(const r0 of [1,2,4]){const k=rt.cloneSession(base);k.externalPolicyMask=3;if(k.Play(2,src.Snapshot().instanceId,r0)){row=r0;break;}}
   if(row){g.Play(2,src.Snapshot().instanceId,row);for(let i=0;i<6&&g.IsPending();i++){prepare(g);g.OpponentStep();}g.FlushDeaths();}}finally{rt.host.log=null;}
  if(!row||!logs.some(s=>/TARGET_SELECT/.test(s))){r.skip=row?'no_unit_choice':'not_playable';fs.appendFileSync(out,JSON.stringify(r)+'\n');continue;}
  r.ai=lead(g)-l0;r.sel=logs.filter(s=>/TARGET_SELECT/.test(s)).map(s=>+s.match(/target=(\d+)/)[1]);
  const h=rt.cloneSession(base);h.externalPolicyMask=3;
  if(!h.Play(2,src.Snapshot().instanceId,row)||!h.pendingIds.length){r.skip='replay_failed';fs.appendFileSync(out,JSON.stringify(r)+'\n');continue;}
  let best=-1e9,bestId=0;const all=[];
  for(const t of [...h.pendingIds]){const k=rt.cloneSession(h);k.externalPolicyMask=0;k.aiSimulating=true;
   if(!k.SelectTarget(k.requestId,t))continue;for(let i=0;i<6&&k.IsPending();i++){prepare(k);k.OpponentStep();}
   k.FlushDeaths();if(k.IsFatal())continue;const v=lead(k)-l0;all.push([t,v]);if(v>best){best=v;bestId=t;}}
  r.best=best;r.bestId=bestId;if(process.env.DETAIL)r.all=all.map(([t,v])=>{const c=h.FindCard(t).Snapshot();return [t,c.positionPlayerId,c.power.currentPower,c.power.basePower,v];});r.gap=best-r.ai;r.candidates=all.length;
 }catch(e){r.err=String(e.message).slice(0,100);}
 fs.appendFileSync(out,JSON.stringify(r)+'\n');
}
