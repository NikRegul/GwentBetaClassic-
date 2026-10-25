'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const nested of [false,true]){
 const g=fixture(1);g.recordVisuals=true;
 const old=add(g,112101,1,0,1),enemy=add(g,112101,1,0,2,15);
 const caster=add(g,113208,nested?16:8,0,1);
 if(nested){const order=add(g,200019,8,6,1);check(g.Play(1,order.Snapshot().instanceId,1),'play Marching Orders');
  check(g.IsRallyRowRequest(),'nested caster waits for placement');check(g.SelectRow(g.requestId,1,1),'place Vaedermakar');}
 else check(g.Play(1,caster.Snapshot().instanceId,1),'play Vaedermakar directly');
 check(g.PendingAimSourceId()===caster.Snapshot().instanceId,'mode choice belongs to Vaedermakar');
 check(g.SelectTemplateChoice(g.requestId,113301),'create Alzur Thunder');
 const child=g.pendingCard;check(child&&child.TemplateId()===113301,'actual request retains the special');
 check(g.PendingSourceId()===child.Snapshot().instanceId,'authoritative request is not redirected');
 check(g.PendingAimSourceId()===caster.Snapshot().instanceId,'aim uses nearest board caster '+nested);
 check(g.PendingAimSourceId()!==old.Snapshot().instanceId,'previous unit cannot own aiming arrow');
 check(g.SelectTarget(g.requestId,enemy.Snapshot().instanceId),'choose actual Thunder target');
 check(enemy.Snapshot().power.currentPower===6&&!g.IsPending()&&!g.IsFatal(),'nine damage and complete play are unchanged');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2));
console.log(JSON.stringify(context.report));
