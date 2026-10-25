// A returned, exhausted drawing spy has no second draw and gifts its body on replay.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const cases=[];
for(const strength of [2,3,4])for(const tpl of [122203,132204,142203,152214,162210]){
 Host.strength=strength;const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 add(g,112101,8,0,1);add(g,112101,8,0,2);add(g,112101,16,0,2);add(g,112101,16,1,2);
 const leader=add(g,200162,1,0,2);leader.monsterStage=2;
 const spy=add(g,tpl,1,1,2,13);spy.cardState.timerValue=0;spy.cardState.tokenMask|=128;
 const ordinary=add(g,142305,1,2,2,14);
 g.pendingCard=leader;g.pendingIds=[spy.cardState.instanceId,ordinary.cardState.instanceId];g.playStack.PushBack(leader);
 check(g.match.ClaimInitialMove(2)===0,'leader return belongs to a real turn');
 const spyValue=g.AiAbilityChoiceValue(leader,spy,0),ordinaryValue=g.AiAbilityChoiceValue(leader,ordinary,0);
 const selected=strength>=3?g.AiSimChoice(leader,g.pendingIds,ordinaryValue>spyValue?ordinary.cardState.instanceId:spy.cardState.instanceId):(ordinaryValue>spyValue?ordinary.cardState.instanceId:spy.cardState.instanceId);
 check(selected===ordinary.cardState.instanceId,'Emhyr keeps the spent spy on his board, strength '+strength+', template '+tpl);
 const enemyScore=g.Score(1),ownHand=g.CountLocation(2,8),deck=g.CountLocation(2,16);
 g.pendingCard=null;g.pendingIds=[];g.playStack.Clear();g.NorthMoveInactive(spy,2,8,true);
 check(spy.Snapshot().timerValue===0,'return preserves exhausted once-only ability '+tpl);
 g.match.currentPlayerId=2;g.match.turnActive=true;g.match.playerTwo.hasMadeInitialMoveForCurrentTurn=false;
 check(g.Play(2,spy.cardState.instanceId,2),'returned spy can be played '+tpl);
 let ticks=0;while(g.IsPending()&&ticks++<8)__pending(g);
 check(!g.IsFatal()&&g.CountLocation(2,16)===deck&&g.CountLocation(2,8)===ownHand,'spent spy gives no second draw '+tpl);
 check(g.Score(1)===enemyScore+13,'spent spy gives its 13 points to the opponent '+tpl);
 cases.push({strength,template:tpl,spyValue,ordinaryValue});
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'emhyr-spent-spy.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
