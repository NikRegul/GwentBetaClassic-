'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
function run(folder){const ctx=vm.createContext({console:{log(){}}});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(folder,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=40;
 const finisher=add(g,112101,8,0,1,30);finisher.AddTokens(64);
 add(g,112101,1,0,1,16);add(g,112101,1,0,2,6);
 const control=add(g,113309,8),body=add(g,112101,8,1,2,12);
 check(g.OpponentStep(),'first real decision');const first=control.Snapshot().locationMask===8?'body':'control';
 check(g.Play(1,finisher.Snapshot().instanceId,1),'real enemy finisher');
 check(g.OpponentStep(),'last real decision');
 globalThis.result={first,own:g.Score(2),enemy:g.Score(1),draws:g.random.DrawCount(),fatal:g.IsFatal(),pending:g.IsPending()};
 `,ctx,{timeout:120000});return JSON.parse(JSON.stringify(ctx.result));}
const old=run(path.resolve(process.argv[2])),current=run(path.resolve(process.argv[3]));
if(!(old.first==='control'&&old.own<old.enemy&&current.first==='body'&&current.own>current.enemy&&!current.fatal&&!current.pending))throw Error(JSON.stringify({old,current}));
const result={old,current,actualWitcherScript:true,nativeGameTested:false};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(result,null,2));console.log(JSON.stringify(result));
