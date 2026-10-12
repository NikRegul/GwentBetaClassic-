// Execute optional selections and Aard relocation through the real WitcherScript.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const limits=[[122204,2],[162103,2],[200163,4],[200159,3],[200209,2]];
for(const [template,maximum] of limits)for(let picked=0;picked<=maximum;picked++){
 const g=fixture(1),source=add(g,template,8,4,1),hand=g.live.filter(c=>c.Snapshot().locationMask===8&&c.Snapshot().positionPlayerId===1&&c!==source);
 for(let i=0;i<6;i++)add(g,122314,16,i,1);
 check(g.Play(1,source.cardState.instanceId,1),'play optional '+template+'/'+picked);
 let r=g.GetRequestSnapshot();
 check(r.limits.minimum===0&&r.limits.maximum===maximum&&r.selectedCount===0,'initial optional limits '+template+'/'+picked);
 const beforeOwn=hand.filter(c=>(c.Snapshot().tokenMask&64)!==0).length;
 const chosen=[];
 for(let i=0;i<picked;i++){
  const target=g.pendingIds[0];chosen.push(g.FindCard(target));
  check(g.SelectTarget(g.requestId,target),'select '+template+'/'+picked+'/'+i);
  if(i+1<maximum){r=g.GetRequestSnapshot();check(r.limits.minimum===0&&r.selectedCount===i+1,'partial count '+template+'/'+picked+'/'+i);}
 }
 if(picked<maximum){const id=g.requestId;check(!g.FinishTarget(id-1),'stale finish rejected '+template+'/'+picked);check(g.FinishTarget(id),'early finish '+template+'/'+picked);}
 // Saskia must give one Bronze replacement for each committed hand card.
 if(template===200209&&picked>0){
  let count=0;
  while(g.IsPending()){
   r=g.GetRequestSnapshot();check(r.limits.minimum===1&&!g.FinishTarget(g.requestId),'Saskia committed replacement mandatory');
   check(g.SelectTarget(g.requestId,g.pendingIds[0]),'Saskia replacement');count++;if(count>2)throw Error('replacement loop');
  }
  check(count===picked,'Saskia exact replacement count');
 }
 check(!g.IsPending()&&!g.IsFatal(),'optional resolves '+template+'/'+picked);
 if(template===162103){
  const revealed=side=>g.live.filter(c=>c.Snapshot().positionPlayerId===side&&c.Snapshot().locationMask===8&&(c.Snapshot().tokenMask&64)!==0).length;
  check(revealed(1)-beforeOwn===picked&&revealed(2)===picked,'Vattier reveals exactly chosen number on each side');
 }
 if(template===200163)check(g.live.filter(c=>c.Snapshot().locationMask===8&&(c.Snapshot().tokenMask&64)!==0).length===picked,'Morvran reveals exact count');
 if(template===200159)check(chosen.every(c=>c.Snapshot().locationMask===32&&c.Snapshot().power.basePower===c.Definition().header.power+1),'Bran strengthens and discards chosen only');
 if(template===122204||template===200209)check(g.CountLocation(1,8)===4,'swap preserves hand size');
}
// An exhausted candidate pool completes instead of waiting for nonexistent cards.
for(const [template] of limits){
 const g=fixture(1);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const source=add(g,template,8,0,1);
 check(g.Play(1,source.cardState.instanceId,1)&&!g.IsPending()&&!g.IsFatal(),'empty optional pool '+template);
}
// Mandatory multi-target damage is not turned into "up to" by the shared mechanism.
// AI can choose fewer targets when the remaining candidates have no positive value.
for(const [template] of limits)for(const stopAfter of [0,1]){
 const g=fixture(2),source=add(g,template,8,4,2);
 for(let i=0;i<6;i++)add(g,122314,16,i,2);
 g.AiAbilityChoiceValue=()=>source.monsterIds.length<stopAfter?5:-5;
 check(g.Play(2,source.cardState.instanceId,1)&&!g.IsPending()&&!g.IsFatal(),'AI optional stop '+template+'/'+stopAfter);
 if(template===162103)check(g.live.filter(c=>c.Snapshot().locationMask===8&&(c.Snapshot().tokenMask&64)!==0).length===stopAfter*2,'AI Vattier stops at chosen count');
}
{
 const g=fixture(1),enemy=add(g,122314,1,0,2),aard=add(g,112111,8,4,1);
 check(g.Play(1,aard.cardState.instanceId,1),'mandatory Aard play');
 check(g.GetRequestSnapshot().limits.minimum===1&&!g.FinishTarget(g.requestId),'Aard still requires available targets');
}
// Aard uses semantic row order on both halves, applies damage, and never wraps siege.
for(const side of [1,2])for(const row of [1,2,4]){
 const g=fixture(side),enemy=3-side,target=add(g,122314,row,0,enemy,10),aard=add(g,112111,8,4,side);
 check(g.Play(side,aard.cardState.instanceId,1),'Aard plays '+side+'/'+row);
 if(side===1)check(g.SelectTarget(g.requestId,target.cardState.instanceId),'Aard target '+row);
 check(target.Snapshot().locationMask===(row===4?4:row*2),'Aard moves upwards '+side+'/'+row);
 check(target.Snapshot().power.currentPower===7&&!g.IsPending()&&!g.IsFatal(),'Aard damage and completion '+side+'/'+row);
}
// A full destination prevents relocation but never suppresses damage.
{
 const g=fixture(1),target=add(g,122314,1,0,2,10),aard=add(g,112111,8,4,1);
 for(let i=0;i<9;i++)add(g,122314,2,i,2,10);
 check(g.Play(1,aard.cardState.instanceId,1)&&g.SelectTarget(g.requestId,target.cardState.instanceId),'Aard full-row target');
 check(target.Snapshot().locationMask===1&&target.Snapshot().power.currentPower===7,'Aard respects row capacity');
}
globalThis.optionalReport={checks,actualWitcherScript:true,nativeGameTested:false,optionalCards:limits.map(x=>x[0])};
`,context);
fs.writeFileSync(process.argv[3]||'docs/evidence/optional124.json',JSON.stringify(context.optionalReport,null,2)+'\n');
console.log(JSON.stringify(context.optionalReport));
