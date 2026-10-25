// Regressions captured from actual 0.9.1d matches, plus public-information guards.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const dir=path.resolve(process.argv[2]),ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
ctx.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(dir,'tunes.json'),'utf8')));ctx.bridge.setStrength(4);
const fixtures=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/deck_order091e.json.gz'))));
let checks=0;const cases=[];function check(v,label){checks++;if(!v)throw Error(label);}
for(const f of fixtures.cases){
 function decide(mutate,staged){ctx.bridge.load(f.state);ctx.mutate=mutate;let logs=[];ctx.bridge.setLog(s=>logs.push(s));
  vm.runInContext(`if(mutate){for(const c of active.live){const s=c.Snapshot();if(s.positionPlayerId===1&&(s.locationMask===8||s.locationMask===16)&&(s.tokenMask&64)===0){c.definition=BetaGwentDuelDefinition(122106);c.cardState.runtimeTemplate=c.definition.header;c.power.SetCurrentPair(40,9);}}}`,ctx);
  if(staged){let ticks=0;while(!vm.runInContext('active.AiPreparationStep()',ctx)){if(++ticks>400)throw Error('Preparation stalled');}}
  ctx.bridge.step();const line=logs.find(s=>/event=SELECT\b/.test(s))||logs.find(s=>/event=PASS\b/.test(s))||'';
  const m=/template=(\d+)/.exec(line);return {template:m&&Number(m[1]),line,view:ctx.bridge.view()};
 }
 const normal=decide(false,false),hidden=decide(true,false),staged=decide(false,true);
 check(normal.template===f.expected,f.name+' expected '+f.expected+' got '+normal.line);
 check(normal.template===hidden.template,f.name+' unknown enemy cards do not change order');
 check(normal.template===staged.template,f.name+' cooperative and synchronous choice agree');
 check(!normal.view.fatal&&!normal.view.pending,f.name+' turn resolves');cases.push({name:f.name,expected:f.expected,selected:normal.line});
 ctx.bridge.load(f.state);
 if(vm.runInContext('typeof active.AiLateOrderWindow==="function"',ctx)){
  check(vm.runInContext('active.AiLateOrderWindow()',ctx),f.name+' window active');
  vm.runInContext('active.match.playerOne.hasPassed=true',ctx);check(!vm.runInContext('active.AiLateOrderWindow()',ctx),f.name+' no delay after pass');
  ctx.bridge.load(f.state);ctx.bridge.setStrength(3);check(!vm.runInContext('active.AiLateOrderWindow()',ctx),f.name+' lower difficulty unchanged');ctx.bridge.setStrength(4);
 }
}
const report={checks,cases,actualWitcherScript:true,nativeGameTested:false};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,1));
