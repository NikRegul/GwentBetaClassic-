'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const run=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]),base=path.join(run,'frozen/tools/ai/beta_js092');
const {personality}=require(path.join(base,'profiles.cjs')),raw=require(path.join(base,'data/personalities.json'));
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
const signatures={};for(const name of Object.keys(raw)){const p=personality(name);delete p.name;signatures[name]=crypto.createHash('sha256').update(JSON.stringify(canonical(p))).digest('hex');}
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify({scope:'Exact effective source values and ordered associations; only diagnostic profile name excluded',sourceProfilesSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(base,'data/personalities.json'))).digest('hex'),signatures},null,2)+'\n');
console.log(JSON.stringify({profiles:Object.keys(signatures).length,effectiveGroups:new Set(Object.values(signatures)).size,out}));
