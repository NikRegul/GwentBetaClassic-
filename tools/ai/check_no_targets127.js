'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const side of [1,2]){
 const g=fixture(side),c=add(g,122102,8,4,side);g.recordVisuals=true;g.visualFrames=[];
 check(g.Play(side,c.cardState.instanceId,1),'empty damage ability resolves '+side);
 check(!g.IsFatal()&&!g.IsPending(),'empty ability leaves no stuck request '+side);
 check(g.visualFrames.filter(f=>f.kind===18).length===1,'one no-target cue for empty damage '+side);
}
{const g=fixture(1),c=add(g,122204,8,4,1);g.recordVisuals=true;g.visualFrames=[];
 check(g.Play(1,c.cardState.instanceId,2)&&g.IsPending(),'optional ability offers a legal target');
 check(g.FinishTarget(g.requestId),'player can decline optional ability');
 check(g.visualFrames.every(f=>f.kind!==18),'voluntary skip is not reported as missing targets');}
globalThis.noTargetsReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'no-targets127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.noTargetsReport,null,2)+'\n');
