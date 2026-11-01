'use strict';
// This validates immutable source evidence; it executes no Beta C#.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict'),{catalog}=require('./source_graph095.cjs');
const root=path.resolve(__dirname,'../..'),file='data/beta924/design/rules_audit096_power_sources.json',raw=fs.readFileSync(path.join(root,file)),review=JSON.parse(raw),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
for(const r of review.records){for(const g of r.graphs){const current=catalog.abilities.find(a=>a.templateId===r.templateId&&a.nid===g.nid);assert(current,'source graph exists');assert.equal(sha(JSON.stringify(current)),g.sha256,'source graph changed');}for(const c of r.classes)assert.equal(sha(fs.readFileSync(path.join(root,c.file))),c.sha256,'C# source changed '+c.file);}
module.exports={file,sha256:sha(raw),records:review.records};
