'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const side of [1,2])for(const power of [8,15]){
 const g=fixture(side),target=add(g,142317,1,0,side===2&&power===8?1:side,power),spell=add(g,200078,8,4,side);
 check(!spell.IsMonsterAbility(),'Trial uses special handler '+side+'/'+power);
 check(g.Play(side,spell.cardState.instanceId,1),'Trial plays '+side+'/'+power);
 if(side===1){
  const s=g.GetRequestSnapshot();
  check(s.limits.minimum===1&&s.limits.maximum===1,'mandatory single-target snapshot '+power);
  check(g.pendingIds.includes(target.cardState.instanceId),'target is offered '+power);
  check(!g.FinishTarget(g.requestId),'cannot skip a legal target '+power);
  check(g.SelectTarget(g.requestId,target.cardState.instanceId),'player can select target '+power);
 }
 check(!g.IsFatal()&&!g.IsPending(),'Trial resolves '+side+'/'+power);
 check(power===8?!alive(target):target.Snapshot().power.currentPower===25,'damage then boost only survivor '+side+'/'+power);
}
{
 const g=fixture(1),witcher=add(g,112101,1,0,1,5),spell=add(g,200078,8,4,1);
 check((witcher.Definition().unitTraits&1)!==0,'witcher fixture');
 check(g.Play(1,spell.cardState.instanceId,1),'Trial with witcher plays');
 check(g.SelectTarget(g.requestId,witcher.cardState.instanceId),'witcher selection');
 check(witcher.Snapshot().power.currentPower===25,'witcher boosted without damage');
}
globalThis.trialReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'trial178.bundle.js',timeout:120000});
console.log(JSON.stringify(context.trialReport));
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.trialReport,null,2)+'\n');
