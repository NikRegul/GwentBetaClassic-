// Compare simulation work per UI callback against the frozen pre-fix sources.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const fixture=fs.readFileSync('tools/ai/check_consume_self.js','utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
const definitions=fs.readFileSync('tools/ai/check_cooperative156.js','utf8').split('function position(kind)')[1].split('for(const strength')[0];
function run(directory){
 const ctx=vm.createContext({console:{log(){}}});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(directory,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+'\nfunction position(kind)'+definitions+String.raw`
 const original=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0;
 CBetaGwentDuelSession.prototype.AiSimPlay=function(id){calls++;return original.call(this,id);};
 const rows=[];Host.strength=4;
 for(const kind of [0,1,2,3,4,5]){
  const g=position(kind);let ticks=0,peak=0,total=0,done=false,result=false;
  do {
   do {calls=0;done=g.AiPreparationStep();peak=Math.max(peak,calls);total+=calls;if(++ticks>500)throw Error('stalled');}while(!done);
   calls=0;result=g.OpponentStep();peak=Math.max(peak,calls);total+=calls;
  }while(!result&&!g.AiPreparationIsReady());
  rows.push({kind,ticks,peakSearchPlaysPerCallback:peak,totalSearchPlays:total,state:state(g),result});
 }
 globalThis.rows=rows;
 `,ctx,{timeout:180000});return JSON.parse(JSON.stringify(ctx.rows));
}
const before=run(path.resolve(process.argv[2])),after=run(path.resolve(process.argv[3]));
for(let i=0;i<before.length;i++)assert(before[i].result===after[i].result&&before[i].state===after[i].state,'same resolved decision in portfolio '+i);
const report={actualWitcherScript:true,nativeTimingMeasured:false,identicalDecisions:before.length,
 beforeFingerprint:JSON.parse(fs.readFileSync(path.join(process.argv[2],'manifest.json'),'utf8')).fingerprint,
 afterFingerprint:JSON.parse(fs.readFileSync(path.join(process.argv[3],'manifest.json'),'utf8')).fingerprint,
 before:before.map(({state,...r})=>r),after:after.map(({state,...r})=>r)};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
