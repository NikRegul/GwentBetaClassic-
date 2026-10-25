// Visible field/hand target pools use the arrow; private piles keep a choice panel.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const tpl of [162206,162209,162309]){
 const g=fixture(1);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const enemy=add(g,142305,1,0,2),own=add(g,142305,1,0,1),source=add(g,tpl,8,0,1);
 add(g,142305,16,0,2);add(g,112101,8,0,2);
 check(g.Play(1,source.cardState.instanceId,2),'play visible-target ability '+tpl);
 check(g.IsPending()&&!g.IsPileChoice()&&!g.pendingChoice,'ability uses direct target request '+tpl);
 const target=tpl===162309?own:enemy;
 check(g.pendingIds.includes(target.cardState.instanceId),'original field target remains legal '+tpl);
 check(g.SelectTarget(g.requestId,target.cardState.instanceId)&&!g.IsFatal(),'direct field target resolves '+tpl);
}
for(const zone of [1,2,4,8,16,32])for(const enemy of [false,true]){
 const g=fixture(1),source=add(g,162206,1,0,1),target=add(g,142305,zone,3,enemy?2:1);
 const ids=[target.cardState.instanceId];g.MonsterRequest(source,ids,2,1,1);
 const visible=(zone&7)!==0||zone===8&&!enemy;
 check(g.IsPileChoice()!==visible,'field/own hand direct, private piles remain choices '+zone+'/'+enemy);
 check(g.pendingIds.length===1&&g.pendingIds[0]===target.cardState.instanceId,'normalization preserves exact candidate pool');
}
{
 const g=fixture(1),source=add(g,162206,1,0,1),field=add(g,142305,2,0,2),hand=add(g,142305,8,3,2);hand.cardState.tokenMask|=64;
 g.MonsterRequest(source,[field.cardState.instanceId,hand.cardState.instanceId],2,1,1);
 check(!g.IsPileChoice()&&g.pendingIds.length===2,'mixed board/revealed hand uses direct selection without dropping a target');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'visible-targets.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
