'use strict';
// Scope198 individual primary branches with hand-written independent expectations (see sources JSON).
const fs=require('fs'),crypto=require('crypto'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const file='data/beta924/design/rules_audit096_misc_sources.json',raw=fs.readFileSync(file),source=JSON.parse(raw);
const F=require('./fixture_batch100096.cjs')(process.argv[2],{file,sha256:sha(raw),records:source.records.map(r=>r.id)});
const {rt,add,snap,id,check,flush,run,begin,trace,finish}=F;
const only=process.env.ONLY?process.env.ONLY.split(',').map(Number):null;const want=t=>!only||only.includes(t);
const fresh=(g,pre)=>g.live.filter(c=>!pre.has(id(c))).map(snap),ids=g=>new Set(g.live.map(id));
function place(g){let k=0;while(g.IsPending()&&(g.pendingRally||g.pendingRow)&&k++<10){let ok=false;for(const s of [1,2])for(const r of [2,1,4])if(!ok&&g.CanSelectRow(g.requestId,s,r))ok=g.SelectRow(g.requestId,s,r);if(!ok)break;flush(g);}}
const same=(a,b)=>JSON.stringify([...a].sort())===JSON.stringify([...b].sort());
globalThis.__misc={rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want};
for(const f of fs.readdirSync(__dirname).filter(f=>/^misc096_.*\.cjs$/.test(f)).sort())require('./'+f);
finish(process.argv[3],'Scope198 individual primary branches (hand-written expectations per card).');
