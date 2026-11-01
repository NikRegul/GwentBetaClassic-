'use strict';
// Immutable independent graph/C# expectations, recorded before handler review.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const {catalog}=require('./source_graph095.cjs'),root=path.resolve(__dirname,'../..');
const file='data/beta924/design/rules_audit096_batch100_sources.json',raw=fs.readFileSync(path.join(root,file)),review=JSON.parse(raw);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function stable(v){if(Array.isArray(v))return v.map(stable);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,stable(v[k])]));return v;}
assert(review.completeIndependentExpectationsBeforeHandlers&&review.scope===100);
for(const row of review.records)for(const graph of row.graphs){
 const current=catalog.abilities.find(g=>g.templateId===row.id&&g.nid===graph.nid);assert(current,'source graph exists');
 assert.equal(sha(JSON.stringify(stable(current.sourceTree))),graph.sha256,'source graph changed '+row.id);
}
for(const [name,digest]of Object.entries(review.commonClasses))assert.equal(sha(fs.readFileSync(path.join(root,'BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay',name))),digest,'C# source changed '+name);
module.exports={file,sha256:sha(raw),records:review.records};
