'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync('tools/ai/check_consume_self.js','utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
function state(g){return JSON.stringify({m:g.match.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:g.random.DrawCount(),frames:g.visualFrames.length});}
for(const passed of [false,true]){
 const g=fixture();g.match.playerOne.hasPassed=passed;
 const ordinary=add(g,132314,1,0,1,11),undvik=add(g,152401,1,1,1,5),hjalmar=add(g,152101,2,0,2,6);
 const before=state(g);
 check(g.AiDamageChoice(undvik.Snapshot(),2,5)===15,'lethal Undvik includes the friendly Hjalmar deathwish '+passed);
 check(g.AiDamageChoice(undvik.Snapshot(),2,4)===4,'nonlethal Undvik hit does not grant the deathwish '+passed);
 check(g.AiDamageChoice(undvik.Snapshot(),2,5,true)===15,'immediate tempo includes resolved Hjalmar boost '+passed);
 g.pendingIds=[ordinary.Snapshot().instanceId,undvik.Snapshot().instanceId];
 check(g.BestTarget(2,1,5)===undvik.Snapshot().instanceId,'five-damage target is Undvik, not the first equal-power target '+passed);
 check(state(g)===before,'target evaluation leaves the match and RNG unchanged '+passed);
 const second=add(g,152101,4,0,2,6);
 check(g.AiDamageChoice(undvik.Snapshot(),2,5)===25,'all living friendly Hjalmars benefit');
 undvik.cardState.tokenMask|=4;
 check(g.AiDamageChoice(undvik.Snapshot(),2,5)===5,'locked Undvik has no deathwish');
 undvik.cardState.tokenMask&=~4;hjalmar.Move(2,32,0);second.Move(2,32,1);
 check(g.AiDamageChoice(undvik.Snapshot(),2,5)===5,'Hjalmar in the graveyard gets no boost');
 hjalmar.Move(2,2,0);
 g.pendingIds=[];const hunter=add(g,152304,8,4,2);check(g.Play(2,hunter.Snapshot().instanceId,4),'hunter resolves');
 check(undvik.Snapshot().locationMask===512&&hjalmar.Snapshot().power.currentPower===16,'chosen lethal hit actually resolves the expected ten-point boost (doomed token vanishes)');
}
function moon(){
 const g=fixture();clearHand(g,2);g.aiSimDamp=0;g.match.playerOne.hasPassed=true;
 for(let i=4;i<8;i++)add(g,112101,8,i,1);
 [6,10,4,11,3].forEach((p,i)=>add(g,132314,1,i,1,p));
 add(g,132314,1,0,2,5);add(g,132314,2,0,2,5);
 [132313,132220,200067,132409,132303,200112,200112].forEach((t,i)=>add(g,t,8,i,2));
 add(g,201587,64,0,2);return g;
}
for(const strength of [2,3,4]){
 Host.strength=strength;const g=moon(),before=g.CountLocation(2,8),draws=g.random.DrawCount();
 const logs=[];Host.log=s=>logs.push(s);check(g.OpponentStep(),'optional chase completes '+strength);Host.log=null;
 check(g.CountLocation(2,8)===before&&g.match.playerTwo.hasPassed,'preserve Moon and leader when two-action chase loses card economy '+strength);
 check(g.random.DrawCount()===draws,'chase search preserves live RNG');
}
Host.strength=4;
{
 const sync=moon(),staged=moon(),initial=state(staged);let ticks=0,maxClones=0;
 const original=staged.AiSimClone;staged.AiSimClone=function(){clones++;return original.call(this);};let clones=0;
 while(!staged.AiPreparationStep()){maxClones=Math.max(maxClones,clones);clones=0;check(state(staged)===initial,'preparation has no live effects');if(++ticks>300)throw Error('stalled');}
 check(!staged.OpponentStep()&&!staged.AiPreparationIsReady(),'final chase yields before any live play');
 check(state(staged)===initial,'starting chase job leaves live match untouched');
 while(!staged.AiPreparationStep()){check(state(staged)===initial,'each chase branch has no live effects');if(++ticks>400)throw Error('chase stalled');}
 check(sync.OpponentStep()===staged.OpponentStep()&&state(sync)===state(staged),'staged and synchronous Moon decision agree');
 check(maxClones<=1,'ordinary preparation creates at most one root clone per step');
}
{
 const g=fixture();g.aiSimDamp=0;g.AiPerfFeedback(400,90);check(g.aiSimDamp===25,'a short total with a long blocking step reduces search cost');
 g.AiPerfFeedback(400,30);check(g.aiSimDamp===25,'medium steps do not immediately undo damping');
 g.AiPerfFeedback(400,12);check(g.aiSimDamp===15,'fast steps recover gradually');
}
globalThis.report={stage:188,checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify(context.report));
