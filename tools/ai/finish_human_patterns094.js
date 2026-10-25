// Continue the exact saved audit positions under one frozen policy, reporting raw seats.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const [snapshot,output]=process.argv.slice(2),ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
ctx.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(snapshot,'tunes.json'),'utf8')));ctx.bridge.setStrength(4);
const fixtures=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/human_patterns094.json.gz')))),results=[];
for(const f of fixtures.cases){
 ctx.bridge.load(f.state);const actor=ctx.bridge.view().actor,logs=[];ctx.bridge.setLog(s=>logs.push(s));let result=null;
 for(let step=0;step<500;step++){
  let v=ctx.bridge.view();if(v.fatal)throw Error(v.message);
  if(v.winner){const winner=v.reversed?((v.winner&1)<<1)|((v.winner&2)>>1):v.winner;result={winner,wonForActingSeat:winner===actor+1,steps:step};break;}
  if(!v.mulligan&&!v.pending&&!v.waiting&&v.current===1)ctx.bridge.swap();ctx.bridge.step();
 }
 if(!result)throw Error('decision limit');
 results.push({game:f.game,step:f.step,actor:actor+1,...result,firstSelection:logs.find(s=>/event=SELECT\b/.test(s))||logs.find(s=>/event=PASS\b/.test(s))});
}
const report={snapshot,fingerprint:JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8')).fingerprint,source:fixtures.origin,results,limitation:'Both seats use this policy for continuation. These diagnosis positions are not independent paired benchmark blocks.'};
fs.writeFileSync(output,JSON.stringify(report,null,2));console.log(JSON.stringify(results));
