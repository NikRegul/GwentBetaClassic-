// 0.6.2 audit of "immediate score only" mistakes:
// - resilient units keep their power into the next round (damage choice must count it);
// - Scoia'tael board-target abilities with Beta Ignore=256 never target the card itself.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
for(const round of [1,2,3]){
 const g=fixture();clearHand(g,2);clearHand(g,1);g.match.roundNumber=round;
 const plain=add(g,112101,1,0,1,5);const res=add(g,112101,1,1,1,5);res.cardState.tokenMask|=1;
 add(g,112101,1,0,2,8);add(g,112101,8,0,1);add(g,112106,8,0,2);
 check(g.OpponentStep(),'AI plays Triss in round '+round);let n=0;while(g.IsPending()&&n++<5)__pending(g);
 const killedRes=(res.Snapshot().locationMask&7)===0,killedPlain=(plain.Snapshot().locationMask&7)===0;
 if(round<3)check(killedRes&&!killedPlain,'round '+round+': equal targets, the resilient one is killed (denies carry-over)');
 else check(killedRes!==killedPlain,'round 3: one target killed');
}
for(const tpl of [142310,142206,142302,142311]){
 const g=fixture();clearHand(g,2);clearHand(g,1);add(g,112101,8,0,1);
 const a=add(g,tpl,8,0,2);const before=a.Snapshot().power.currentPower;
 check(g.Play(2,a.Snapshot().instanceId,1)&&!g.IsFatal(),tpl+' played on an otherwise empty board');
 let n=0;while(g.IsPending()&&n++<5)__pending(g);
 check(a.Snapshot().power.currentPower===before,tpl+' never targets itself');
}
{ const g=fixture();clearHand(g,2);clearHand(g,1);add(g,112101,8,0,1);const e=add(g,112101,1,0,1,6);
 const a=add(g,142310,8,0,2);g.Play(2,a.Snapshot().instanceId,1);let n=0;while(g.IsPending()&&n++<5)__pending(g);
 check(a.Snapshot().power.currentPower===7&&e.Snapshot().power.currentPower===2,'Dol Blathanna Archer hits the enemy 3+1'); }
for(const brigade of [false,true]){ // Impera Enforcer: an enemy unit, not our own spy.
 const g=fixture();clearHand(g,2);clearHand(g,1);add(g,112101,8,0,1);
 const spyCard=add(g,162314,1,0,1,2);spyCard.cardState.tokenMask|=128;const enemy=add(g,112101,1,1,1,3);
 if(brigade)add(g,162307,16,0,2);
 const e=add(g,162308,8,0,2);check(g.OpponentStep()&&!g.IsFatal(),'AI plays Impera Enforcer (brigade in deck: '+brigade+')');
 let n=0;while(g.IsPending()&&n++<5)__pending(g);
 check((spyCard.Snapshot().locationMask&7)!==0&&enemy.Snapshot().power.currentPower<3,'own spy kept, enemy unit damaged (brigade '+brigade+')');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'deferred062.bundle.js',timeout:120000});
console.log('PASS: '+context.report.checks+' deferred-value and self-target regressions');
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
