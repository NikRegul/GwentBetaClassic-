// Engine removal: execute the real translated target selection and effect queues.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function enemies(g){
 const revenant=add(g,201624,1,0,1),plain=add(g,112101,1,1,1,9);
 plain.power.basePower=9;plain.power.permanentPower=0;
 return {revenant,plain};
}
{
 const g=fixture(),{revenant,plain}=enemies(g),r=revenant.Snapshot();
 check(g.AiEngineValue(r,2)>0,'armed Revenant has future copy value');
 check(g.TargetValue(r,2,1,9)>g.TargetValue(plain.Snapshot(),2,1,9),'removal prefers armed Revenant over nine ordinary points');
 check(g.LockToggleValue(r,2)>g.LockToggleValue(plain.Snapshot(),2),'lock values Revenant ability');
 revenant.cardState.tokenMask|=4;
 check(g.AiEngineValue(revenant.Snapshot(),2)===0,'locked Revenant has no active copy value');
 check(g.LockToggleValue(revenant.Snapshot(),2)<0,'do not unlock enemy Revenant');
 revenant.cardState.tokenMask&=~4;revenant.cardState.timerValue=0;
 check(g.AiEngineValue(revenant.Snapshot(),2)===0,'spent Revenant has no phantom future copies');
 check(g.TargetValue(revenant.Snapshot(),2,1,9)<g.TargetValue(plain.Snapshot(),2,1,9),'ordinary points can outweigh an exhausted Revenant');
}
for(const weatherProfile of [false,true])for(const source of [113301,122211,122102]){
 const g=fixture(),{revenant,plain}=enemies(g),c=add(g,source,8,4,2);
 g.weatherProfile=weatherProfile;
 check(g.Play(2,c.cardState.instanceId,2),'AI plays removal/control '+source);
 check(!g.IsFatal()&&!g.IsPending(),'target choice completes '+source);
 if(source===122211)check((revenant.Snapshot().tokenMask&4)!==0,'Margarita locks armed Revenant after exact target simulation');
 else check(revenant.Snapshot().locationMask===32,'damage kills armed Revenant '+source);
 check(plain.Snapshot().power.currentPower===9,'higher ordinary body is preserved '+source);
}
globalThis.engineReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'engines126.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.engineReport,null,2)+'\n');
