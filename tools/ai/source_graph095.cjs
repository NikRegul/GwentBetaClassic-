'use strict';
// Static evidence only. This module does not execute or reinterpret Beta rules.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/normalized/catalog.json'),'utf8'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function graph(id,nid){
 const g=catalog.abilities.find(a=>a.templateId===id&&a.nid===nid);assert(g,`graph ${id}/${nid}`);
 return {raw:g,node(i,type){const n=g.nodes.find(n=>n.nodeId===i);assert(n,`node ${id}/${nid}/${i}`);if(type)assert.equal(n.type,type);return n;},
 variable(name,value){const vars=g.sourceTree.children.filter(x=>x.tag.endsWith('Variables')).flatMap(x=>x.children);const v=vars.find(x=>x.attributes.Name===name);assert(v,`${id}/${nid} variable ${name}`);assert.equal(v.attributes.V,String(value));},
 value(i,f,v){const n=g.nodes.find(n=>n.nodeId===i),x=n.sourceTree.children.find(x=>x.tag===f);assert(x,`${i}.${f}`);assert.equal(x.attributes.V,String(v));},
 edge(a,f,b,h){assert(g.connections.some(e=>e.sourcePort.nodeId===a&&e.sourcePort.field===f&&e.destinationPort.nodeId===b&&e.destinationPort.field===h),`${id}/${nid}: ${a}.${f} -> ${b}.${h}`);},
 evidence(classes){return {templateId:id,graph:nid,graphSha256:sha(JSON.stringify(g)),catalog:'data/beta924/normalized/catalog.json',nodes:g.nodes.map(n=>({id:n.nodeId,type:n.type})),classes:classes.map(n=>{const file='BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay/'+n+'.cs';return {file,sha256:sha(fs.readFileSync(path.join(root,file)))};})};}};
}
module.exports={catalog,graph};
