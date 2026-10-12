// Stage 131: a hand play that only loses points is replaced by a pass.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
{
 const g=fixture();clearHand(g,2);g.match.roundNumber=3;
 const own=add(g,112101,1,0,2,12);add(g,112101,1,0,1,6);
 const scorch=add(g,113309,8,0,2);
 check(g.OpponentStep()&&!g.IsFatal(),'AI decides with only a self-hitting Scorch');
 check(scorch.Snapshot().locationMask===8,'Scorch stays in hand');
 check(g.match.playerTwo.hasPassed===true,'AI passes instead');
 check(own.Snapshot().locationMask===1,'own strongest unit survives');
}
{
 const g=fixture();clearHand(g,2);g.match.roundNumber=3;
 add(g,112101,1,0,2,6);const enemy=add(g,112101,1,0,1,12);
 const scorch=add(g,113309,8,0,2);
 check(g.OpponentStep()&&!g.IsFatal(),'AI decides with a useful Scorch');
 check(scorch.Snapshot().locationMask!==8,'useful Scorch is played');
 check((enemy.Snapshot().locationMask&7)===0,'enemy strongest unit is burnt');
}
globalThis.losingReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'losing131.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.losingReport,null,2)+'\n');
