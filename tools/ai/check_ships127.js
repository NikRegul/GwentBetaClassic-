// Skellige longship engines: removal prefers a live longship over a bigger ordinary body.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const ship of [152309,152314]){
 {
  const g=fixture(),boat=add(g,ship,1,0,1),plain=add(g,112101,1,1,1,9);
  plain.power.basePower=9;plain.power.permanentPower=0;
  check(g.AiEngineValue(boat.Snapshot(),2)>=6,'longship has engine value '+ship);
  check(g.TargetValue(boat.Snapshot(),2,1,9)>g.TargetValue(plain.Snapshot(),2,1,9),'removal prefers longship over nine points '+ship);
  boat.cardState.tokenMask|=4;
  check(g.AiEngineValue(boat.Snapshot(),2)===0,'locked longship is no engine '+ship);
 }
 for(const source of [113301,122102]){
  const g=fixture(),boat=add(g,ship,1,0,1),plain=add(g,112101,1,1,1,9),c=add(g,source,8,4,2);
  plain.power.basePower=9;plain.power.permanentPower=0;
  check(g.Play(2,c.cardState.instanceId,2)&&!g.IsFatal(),'AI plays removal '+source+' vs '+ship);
  check(boat.Snapshot().locationMask===32,'removal kills longship '+ship+' with '+source);
  check(plain.Snapshot().power.currentPower===9,'bigger body is preserved '+ship+' with '+source);
 }
}
globalThis.shipReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'ships127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.shipReport,null,2)+'\n');
