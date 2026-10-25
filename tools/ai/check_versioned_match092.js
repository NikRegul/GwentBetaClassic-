// Verify policy dispatch, historical identity mapping and serialization parity.
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),v=require('./versioned_match092.js');
const config=JSON.parse(fs.readFileSync(path.resolve(process.argv[2]),'utf8'));let checks=0;
function check(x,message){assert.ok(x,message);checks++;}
const a=v.load({...config,nativeTransfer:true,validationDigest:true}),b=v.load({...config,nativeTransfer:false,validationDigest:true});
let expected=[],dispatches={'0.9.1':0,'0.9.2':0};
for(const [version,h]of Object.entries(a.hosts)){
 const step=h.step.bind(h);h.step=()=>{const s=h.view(),chooser=s.mulligan?1-s.actor:s.actor;check(expected[chooser]===version,'each real action uses its entrant version');dispatches[version]++;return step();};
 const mulligan=h.initialMulligan.bind(h);h.initialMulligan=()=>{check(expected[1]===version,'initial AI exchange belongs to the right entrant');dispatches[version]++;return mulligan();};
}
const pairs=[[54,155],[154,55],[154,155],[54,55]],results=[];
for(let i=0;i<pairs.length;i++){
 const [left,right]=pairs[i],seed=923101300+i;expected=[left>=100?'0.9.1':'0.9.2',right>=100?'0.9.1':'0.9.2'];
 const actual=a.play(left,right,seed),json=b.play(left,right,seed);check(!actual.error&&!json.error,'native and JSON transfer complete');assert.deepEqual(actual,json);checks++;
 results.push(actual);
}
check(dispatches['0.9.1']>0&&dispatches['0.9.2']>0,'both original and current policies actually execute');
const control=v.load({...config,oldPolicy:config.snapshot,nativeTransfer:true});
const meta=a.meta.decks,equal=meta.filter(d=>d.version==='0.9.2'&&meta.some(o=>o.version==='0.9.1'&&o.basePreset===d.basePreset&&o.leader===d.leader&&JSON.stringify(o.templateIds)===JSON.stringify(d.templateIds)));
check(equal.length>=2,'at least two unchanged historical rosters permit an identity control');
for(const reverse of [false,true]){
 const x=equal[0].presetId,y=equal[1].presetId,seed=923101399;
 const normal=control.play(reverse?y:x,reverse?x:y,seed),offset=control.play(reverse?y:x,reverse?x+100:y+100,seed);
 check(!normal.error&&!offset.error&&normal.winner===offset.winner&&normal.steps===offset.steps,'entrant offset preserves identical-policy game result and sequence');
}
if(process.argv.includes('--vm')){
 const vm=v.load({...config,nativeTransfer:true,validationDigest:true},'vm');
 for(let i=0;i<2;i++){
  const [left,right]=pairs[i],seed=923101450+i;expected=[left>=100?'0.9.1':'0.9.2',right>=100?'0.9.1':'0.9.2'];
  const actual=a.play(left,right,seed),other=vm.play(left,right,seed);check(!actual.error&&!other.error,'both execution loaders complete');assert.deepEqual(actual,other);checks++;
 }
}
const report={checks,dispatches,results,identityControlRosters:equal.slice(0,2).map(d=>d.presetId),nativeTransferEqualsJson:true,simulationOnly:true};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
