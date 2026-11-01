'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const file='data/beta924/design/rules_audit096_creators20_sources.json',raw=fs.readFileSync(file),source=JSON.parse(raw),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const {catalog}=require('./source_graph095.cjs');function stable(v){if(Array.isArray(v))return v.map(stable);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,stable(v[k])]));return v;}
assert(source.independentExpectationsBeforeHandlers&&source.records.length===20);
for(const r of source.records)for(const graph of r.graphs){const g=catalog.abilities.find(g=>g.templateId===r.id&&g.nid===graph.nid);assert.equal(sha(JSON.stringify(stable(g.sourceTree))),graph.sha256);}
for(const [n,h]of Object.entries(source.commonClasses))assert.equal(sha(fs.readFileSync('BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay/'+n+'.cs')),h);
const evidence={file,sha256:sha(raw),records:source.records},snapshot=process.argv[2],{rt,add,snap,id,check,flush,run,begin,trace,finish}=require('./fixture_batch100096.cjs')(snapshot,evidence),context=require('./diagnose_strategy096.js').load(path.resolve(snapshot)).context;
const sameSet=(a,b)=>JSON.stringify([...a].sort((a,b)=>a-b))===JSON.stringify([...b].sort((a,b)=>a-b));
for(const record of source.records)for(const side of [1,2])run(record.id,side,'source definition pool and real creation',g=>{
 const tid=record.id,pool=[];for(const name of ['BetaGwentMonsterTemplates','BetaGwentNorthernPool','BetaGwentNilfPool','BetaGwentScoiaPool','BetaGwentSkelligePool','BetaGwentNeutralPool']){const p={v:require('vm').runInContext('[]',context)};context[name](tid,p);if(p.v.length)pool.push(...p.v);}
 check(sameSet([...new Set(pool)],record.pool),'complete emitted definition set equals independent BaseSet/Normal/source filters');
 const rng=trace(g),owner=begin(g,tid,side),offered=[...g.pendingIds];check(g.pendingChoice&&g.IsPending(),'real template choice');
 if(record.randomThree){check(offered.length===Math.min(3,record.pool.length)&&new Set(offered).size===offered.length&&offered.every(x=>record.pool.includes(x)),'up to3 distinct source-eligible definitions');check(rng.length===record.pool.length-1,'shuffle entire independent pool N-1');
  const expected=record.pool.slice();for(let k=expected.length-1,i=0;k>0;k--,i++){const draw=rng[i];check(!!draw&&draw.n===k+1,'source shuffle bound');if(draw)[expected[k],expected[draw.v]]=[expected[draw.v],expected[k]];}
  check(JSON.stringify(offered)===JSON.stringify(expected.slice(0,3)),'source dictionary order and exact shuffled offer');}
 else check(JSON.stringify(offered)===JSON.stringify(record.pool),'fixed choices preserve source order/no added options');
 const chosen=offered[0],before=new Set(g.live.map(id));check(g.SelectTemplateChoice(g.requestId,chosen),'offered template accepted');flush(g);
 check(g.live.some(c=>!before.has(id(c))&&c.TemplateId()===chosen),'selected definition actually creates new instance');
 check(snap(owner).power.currentPower===30,'parent ability preserves source current power in this empty-board fixture');
 // Child may have its own required choice; that child ability is a separate card obligation.
});
finish(process.argv[3],'20 new cards: independent full definition pools, source list order, full shuffle size, actual template selection/creation. Children/all branches deferred.');
