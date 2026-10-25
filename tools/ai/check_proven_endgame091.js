// New public endgame proof must also obey the game's cooperative search budget.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),ctx=vm.createContext({console:{log(){}}});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function position(damp,n){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.aiSimDamp=damp;
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 add(g,112405,1,0,1,12+n);add(g,112405,1,0,2,4);
 const enemy=add(g,112405,8,0,1,28+n);enemy.AddTokens(64);
 add(g,113309,8);add(g,112405,8,1,2,9+n);return g;}
function state(g){return JSON.stringify({match:g.match.Snapshot(),live:g.live.map(c=>c.Snapshot()),draws:g.random.DrawCount(),fatal:g.IsFatal(),pending:g.IsPending()});}
const original=CBetaGwentDuelSession.prototype.AiSimPlay;let plays=0,callbacks=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(id){plays++;return original.call(this,id);};
for(const damp of [0,40,70,100])for(let n=0;n<8;n++){
 const sync=position(damp,n),staged=position(damp,n),initial=state(staged);let ticks=0;
 while(true){plays=0;const done=staged.AiPreparationStep();callbacks++;
  check(plays<=1,'bounded callback');check(state(staged)===initial,'live match and RNG unchanged');
  if(done)break;if(++ticks>200)throw Error('stalled preparation');}
 check(sync.OpponentStep()&&staged.OpponentStep(),'both decisions complete');
 check(state(sync)===state(staged),'synchronous and cooperative endgame agree '+damp+'/'+n);
 const control=staged.live.find(c=>c.TemplateId()===113309&&c.Snapshot().positionPlayerId===2);
 check(control.Snapshot().locationMask===8,'prepared proof retains last response '+damp+'/'+n);
}
globalThis.report={checks,callbacks,positions:32,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:240000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(ctx.report,null,2));console.log(JSON.stringify(ctx.report));
