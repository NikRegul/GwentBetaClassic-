// Thunderbolt must value restarting a stripped Redanian Squire, including an adjacent one.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function position(){
 const g=fixture();
 // Reported melee row: 31, 32 (stripped squire), 36, 30, 43.
 // Allocate 30 first, so the old tie picks it and misses the squire.
 const plain=add(g,122316,1,3,2,4);add(g,122316,1,4,2,4);
 const left=add(g,122311,1,0,2,5),squire=add(g,123301,1,1,2,1),right=add(g,122316,1,2,2,5);
 squire.power.currentArmor=0;
 return {g,plain,left,squire,right};
}
{
 const {g,plain,left,squire,right}=position();
 const before=JSON.stringify(g.live.map(c=>c.Snapshot()));
 check(g.TargetValue(squire.Snapshot(),2,3,3,false,2)>g.TargetValue(plain.Snapshot(),2,3,3,false,2),'restoring the engine beats the equal nine-point ordinary triple');
 check(g.TargetValue(squire.Snapshot(),2,3,3,true,2)===9,'immediate power estimate excludes future engine ticks');
 check(g.TargetValue(squire.Snapshot(),2,3,3,false,0)===9,'boost without armour cannot restart the engine');
 check(g.TargetValue(squire.Snapshot(),1,3,3,false,2)<-9,'restoring an enemy engine is a cost');
 check(JSON.stringify(g.live.map(c=>c.Snapshot()))===before,'valuation leaves the live board unchanged');
 squire.power.currentArmor=2;
 check(g.TargetValue(squire.Snapshot(),2,3,3,false,2)===9,'existing armour gets no duplicate activation bonus');
 squire.power.currentArmor=0;squire.cardState.tokenMask|=4;
 check(g.TargetValue(squire.Snapshot(),2,3,3,false,2)===9,'armour does not restart a locked engine');
 squire.cardState.tokenMask&=~4;
 g.match.playerOne.hasPassed=true;
 check(g.TargetValue(squire.Snapshot(),2,3,3,false,2)===11,'after a pass count the current end-turn tick only');
 right.Move(2,512,0);
 check(g.TargetValue(left.Snapshot(),2,3,3,false,2)===7,'a squire adjacent to the selected pivot also restarts, with one real neighbour');
 left.Move(2,512,0);
 check(g.TargetValue(squire.Snapshot(),2,3,3,false,2)===3,'isolated squire has no phantom neighbour boosts');
}
for(const fromKeira of [false,true]){
 const {g,squire,left,right}=position();
 const card=add(g,fromKeira?122108:113311,8,4,2);
 check(g.Play(2,card.Snapshot().instanceId,4),'play '+(fromKeira?'Keira':'Thunderbolt'));
 let steps=0;while(g.IsPending()&&steps++<12)__pending(g);
 check(!g.IsPending()&&!g.IsFatal(),'nested play completes');
 check(squire.Snapshot().power.armor===2&&squire.Snapshot().power.currentPower===4,'Thunderbolt restores the stripped squire');
 check(left.Snapshot().power.currentPower===9&&right.Snapshot().power.currentPower===9,'both neighbours receive +3 and the restored end-turn +1');
 if(fromKeira)check(g.live.some(c=>c.TemplateId()===113311),'Keira creates Thunderbolt');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'armor-restore165.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log('PASS '+context.report.checks+' armour restoration checks');
