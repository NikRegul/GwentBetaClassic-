'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {entrants,playMatch}=require('./beta_js092/matches.cjs');
const config=JSON.parse(fs.readFileSync(path.resolve(process.argv[2]),'utf8')),out=path.resolve(process.argv[3]);if(fs.existsSync(out))throw Error('Fresh output required');
const list=entrants(config),find=k=>{const d=list.find(x=>x.key===k);assert(d,'entrant '+k);return d;};
const report={scope:'Four-group policy/deck dispatch technical smoke; not a strength schedule',ratingPermitted:false,nativeProcessesAllowed:false,
 informationAsymmetry:'Beta may see full hands/decks; 0.9.1/0.9.2 keep their own original information restrictions.',groups:Object.fromEntries(['091','092','beta092','betaOriginal'].map(g=>[g,list.filter(d=>d.group===g).length])),records:[]};
const original=list.find(d=>d.group==='betaOriginal'&&d.asset==='d_Skellige_Practice_Easy');assert(original);
const schedule=[['091:55','092:55'],['beta092:55','091:55'],['091:55','beta092:55'],[original.key,'092:55']];
for(let i=0;i<schedule.length;i++){
 const [left,right]=schedule[i],r=playMatch(config,find(left),find(right),924024001+i);report.records.push(r);
 fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...r,trace:undefined}));assert.equal(r.status,'complete',r.error);
}
report.complete=true;fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
