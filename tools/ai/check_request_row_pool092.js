/* Pure shared-engine row candidates versus the authoritative mutation itself. */
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
let stamp=911000000,positions=0;
function state(g){return JSON.stringify({cards:g.live.map(c=>c.Snapshot()),match:g.Snapshot(),pending:g.pendingIds,request:g.requestId,
 rng:g.random.words,draws:g.random.DrawCount(),cursor:g.random.cursor,remaining:g.random.remaining});}
function verify(g,expected,label){
 const before=state(g),pairs=[];
 for(const side of [1,2])for(const row of [1,2,4])if(g.CanSelectRow(g.requestId,side,row))pairs.push(side+':'+row);
 check(JSON.stringify(pairs)===JSON.stringify(expected),label+' exact candidate pool');
 check(!g.CanSelectRow(g.requestId-1,1,1)&&!g.CanSelectRow(g.requestId,0,1)&&!g.CanSelectRow(g.requestId,1,3),label+' invalid id/side/row');
 check(state(g)===before,label+' pool read leaves cards/match/request/RNG untouched');
 for(const side of [1,2])for(const row of [1,2,4]){
  const clone=new CBetaGwentCloner().CloneSession(g,++stamp),want=pairs.includes(side+':'+row);
  check(clone.SelectRow(clone.requestId,side,row)===want,label+' authoritative action agrees '+side+'/'+row);positions++;
 }
}
for(const side of [1,2])for(const id of [113305,113312,113206,153301]){
 const g=fixture(side);g.externalPolicyMask=3;add(g,112101,1,0,3-side,15);const c=add(g,id,8,4,side);
 check(g.Play(side,c.Snapshot().instanceId,1),'actual row source '+id+'/'+side);
 const expected=[];for(const s of [1,2])for(const row of [1,2,4])if((id===153301||s===3-side)&&(id!==113206||row!==4))expected.push(s+':'+row);
 verify(g,expected,id+'/'+side);
}
for(const side of [1,2]){
 const g=fixture(side);g.externalPolicyMask=3;add(g,200169,64,0,side);
 for(let i=0;i<9;i++)add(g,112405,2,i,side,5);
 check(g.UseLeader(side),'actual leader request');verify(g,[side+':1',side+':4'],'leader capacity '+side);
}
for(const side of [1,2]){
 const g=fixture(side);g.externalPolicyMask=3;add(g,113208,16,0,side);const order=add(g,200019,8,4,side);
 check(g.Play(side,order.Snapshot().instanceId,1)&&g.pendingRally,'actual tutor placement');verify(g,[side+':1',side+':2',side+':4'],'tutor '+side);
}
globalThis.report={checks,positions,scope:'Read-only CanSelectRow versus real SelectRow on cloned weather/WhiteFrost/Lacerate/leader/tutor requests, both seats. Same shared validation, no alternate rules engine.',nativeGameplayVerified:false};
`,context,{timeout:120000});
const report={...context.report,fingerprint:JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8')).fingerprint};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
