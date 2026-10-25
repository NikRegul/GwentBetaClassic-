// A shadow action must use its current seat/board, not the previous actor's cache.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function blank(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=56;g.leaderTemplateTwo=201743;g.archetypeAI.Initialize(g,[],56,201743);
 g.match.roundNumber=2;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=0;return g;}
const combos=[];
{
 const g=blank();
 // Fill our melee row so the actual Miruna play must choose another row.
 for(let i=0;i<9;i++)add(g,112405,1,i,2,2);
 add(g,113209,1,0,1,10);
 const miruna=add(g,132108,8,0,2);miruna.cardState.timerValue=2;
 const cross=add(g,113209,8,1,2),pugach=add(g,132204,16,0,2);
 add(g,132304,16,1,2);add(g,132304,16,2,2);
 const enemy=add(g,112405,8,0,1,6);add(g,112405,8,1,1,6);
 g.archetypeAI.Refresh();
 const first=g.AiSimClone();check(first.AiSimPlay(miruna.Snapshot().instanceId)!==-2147483647,'first actual simulated Miruna play resolves');
 const row=first.FindCard(miruna.Snapshot().instanceId).Snapshot().locationMask;
 check(row===2,'Miruna actually enters the open ranged row');
 check(first.Play(1,enemy.Snapshot().instanceId,4),'actual opposing body advances the turn');
 const second=first.AiSimClone();
 check(second.AiSimPlay(cross.Snapshot().instanceId)!==-2147483647,'second actual simulated tutor play resolves');
 const result=second.FindCard(pugach.Snapshot().instanceId).Snapshot();
 console.log('TWO_ACTION_SHADOW',JSON.stringify({mirunaRow:row,spySide:result.positionPlayerId,spyRow:result.locationMask}));
 check(result.positionPlayerId===1&&result.locationMask===row,'second node preserves the Miruna/Pugach combination created by the first node');
}
for(const timer of [1,2]){
 const g=blank(),miruna=add(g,132108,2,0,2);miruna.cardState.timerValue=timer;
 add(g,132305,1,0,2,6);add(g,113209,1,0,1,10);
 const cross=add(g,113209,8,0),pugach=add(g,132204,16,0);
 add(g,132304,16,1);add(g,132304,16,2);add(g,132305,8,1);
 for(let i=0;i<4;i++)add(g,112101,8,i,1,6);
 // Deliberately do not refresh a private cache manually. This is exactly
 // how a new node or reversed public response is handed to the simulator.
 const h=g.AiSimClone();check(h.AiSimPlay(cross.Snapshot().instanceId)!==-2147483647,'actual Cross action resolves without caller cache repair '+timer);
 const result=h.FindCard(pugach.Snapshot().instanceId).Snapshot();
 console.log('CROSS_SHADOW',JSON.stringify({timer,side:result.positionPlayerId,row:result.locationMask}));
 check(result.positionPlayerId===1&&result.locationMask===2,'shadow tutor puts Pugach under the actual pending Miruna '+timer);
 combos.push({timer,side:result.positionPlayerId,row:result.locationMask});
}
{
 const g=blank();add(g,112405,1,0,2,7);add(g,112405,2,0,1,9);
 add(g,122103,8,0,2);add(g,113301,8,0,1);g.archetypeAI.Refresh();
 const h=g.AiSimClone().AiReverseClone();
 const actualBoard=h.live.filter(c=>c.Snapshot().positionPlayerId===2&&(c.Snapshot().locationMask&7)!==0).map(c=>c.Snapshot().instanceId).sort();
 const actualHand=h.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8).map(c=>c.Snapshot().instanceId).sort();
 check(JSON.stringify(h.archetypeAI.board.map(c=>c.Snapshot().instanceId).sort())===JSON.stringify(actualBoard),'reversed response observes its own current board');
 check(JSON.stringify(h.archetypeAI.hand.map(c=>c.Snapshot().instanceId).sort())===JSON.stringify(actualHand),'reversed response observes anonymized own hand, not original actor hand');
}
globalThis.report={checks,combos,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
