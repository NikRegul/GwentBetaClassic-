/* Compare default-policy complete games before/after opt-in decision hooks. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
function load(folder){
 const source=['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(folder,f),'utf8')).join('\n');
 const tunes=JSON.parse(fs.readFileSync(path.join(folder,'tunes.json'),'utf8'));
 return new Function('tunes',source+'\nHost.tunes=[tunes,tunes];return __harness;')(tunes);
}
const a=load(path.resolve(process.argv[2])),b=load(path.resolve(process.argv[3]));
const schedules=[[91,56,924020101],[56,91,924020102],[57,78,924020103],[78,57,924020104]];
const games=[];
for(const [left,right,seed]of schedules){
 const old=a.play(left,right,seed,4,4,200),fresh=b.play(left,right,seed,4,4,200);
 assert(!old.error,JSON.stringify(old));assert(!fresh.error,JSON.stringify(fresh));assert.deepEqual(fresh,old);
 games.push(fresh);console.log(JSON.stringify(fresh));
}
const report={games:games.length,completeOutcomesAndStepCountsIdentical:true,schedule:games,
 scope:'Default existing policy only; external Beta policy not exercised.'};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(report,null,2)+'\n');
