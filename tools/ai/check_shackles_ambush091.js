// The direct UI event must lock/reveal an ambush, then damage only an enemy.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const template of [142204,142208,142210,142307])for(const side of [1,2])for(const row of [1,2,4]){
 const g=fixture(1),trap=add(g,template,row,0,side,12),other=add(g,112101,row,1,side,7),spell=add(g,113319,8,4,1);
 check((trap.Snapshot().tokenMask&8)!==0,'fixture is concealed '+template);
 check(g.PlayOnTarget(1,spell.Snapshot().instanceId,trap.Snapshot().instanceId),'direct Shackles event accepts ambush '+template+'/'+side+'/'+row);
 check((trap.Snapshot().tokenMask&12)===4,'ambush is face up and locked');
 check(trap.Snapshot().power.currentPower===(side===2?8:12),'four damage only to enemy');
 check(other.Snapshot().power.currentPower===7,'locking does not execute the reveal ability');
 check(!g.IsFatal()&&!g.IsPending()&&spell.Snapshot().locationMask===32,'play completes and spends the spell');
}
// This distinct ambush cancels an opposing bronze/silver special as it is played,
// before the target request. Allowing the UI selection must not bypass that reaction.
{
 const g=fixture(1),trap=add(g,201779,1,0,2,12),spell=add(g,113319,8,4,1);
 g.PlayOnTarget(1,spell.Snapshot().instanceId,trap.Snapshot().instanceId);
 check((trap.Snapshot().tokenMask&12)===0,'counterspell ambush reveals by its own reaction, without being locked');
 check(trap.Snapshot().power.currentPower===12&&spell.Snapshot().locationMask===32,'counterspell still cancels the special before damage');
 check(!g.IsFatal()&&!g.IsPending(),'counterspell reaction completes safely');
}
for(const immune of [false,true]){
 const g=fixture(1),trap=add(g,142204,1,0,2,12),spell=add(g,immune?113319:113301,8,4,1);
 if(immune)trap.AddTokens(256);
 check(!g.PlayOnTarget(1,spell.Snapshot().instanceId,trap.Snapshot().instanceId),immune?'immune ambush rejected':'ordinary damage still rejects hidden ambush');
 check(spell.Snapshot().locationMask===8&&(trap.Snapshot().tokenMask&8)!==0&&!g.IsFatal(),'rejected target neither spends the spell nor reveals the ambush');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'shackles-ambush091.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify(context.report));
