// Stage 131: False Ciri returns to the AI when the opponent passes; play her
// while the opponent is still in the round, never after the opponent passed.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
for(const [name,own,enemy,passed,round] of [['behind',10,12,false,3],['ahead',17,12,false,2],['last card round one',10,12,false,1],['after enemy pass',17,12,true,2]]){
 const g=fixture();clearHand(g,2);g.match.roundNumber=round;
 add(g,112101,1,0,2,own);add(g,112101,1,0,1,enemy);g.match.playerOne.hasPassed=passed;
 const ciri=add(g,162212,8,0,2);
 check(g.OpponentStep()&&!g.IsFatal(),'AI decides with False Ciri: '+name);
 if(passed){check(ciri.Snapshot().locationMask===8,'False Ciri kept after enemy pass');continue;}
 check(ciri.Snapshot().locationMask!==8&&ciri.Snapshot().positionPlayerId===1,'False Ciri spies: '+name);
 g.match.currentPlayerId=1;check(g.Pass(1),'enemy passes: '+name);
 check(ciri.Snapshot().positionPlayerId===2&&(ciri.Snapshot().locationMask&7)!==0,'False Ciri returns to AI: '+name);
 check(g.Score(2)>own,'AI score gains her power: '+name);
}
globalThis.ciriReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'ciri131.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.ciriReport,null,2)+'\n');
