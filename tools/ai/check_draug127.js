// Draug: resurrects own graveyard units as Draugirs; the AI waits for a filled graveyard.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
for(const side of [1,2]){
 const g=fixture(side);g.match.currentPlayerId=side;for(let i=0;i<4;i++)add(g,112101,32,i,side,3);add(g,113302,32,4,side);
 const c=add(g,132101,8,6,side);
 check(g.Play(side,c.cardState.instanceId,1)&&!g.IsFatal()&&!g.IsPending(),'Draug resolves for side '+side);
 check(g.CountLocation(side,1)===5&&g.CountLocation(side,32)===1,'four units rise as Draugirs, the special stays '+side);
}
{const g=fixture();g.match.currentPlayerId=2;for(let i=0;i<9;i++)add(g,112101,32,i,2,3);for(let i=0;i<7;i++)add(g,112101,1,i,2,2);
 const c=add(g,132101,8,6);check(g.Play(2,c.cardState.instanceId,1)&&g.CountLocation(2,1)===9,'Draug stops when the row is full');}
{const g=fixture();g.match.currentPlayerId=2;add(g,112101,32,0,1,3);const c=add(g,132101,8,6);
 check(g.Play(2,c.cardState.instanceId,1)&&g.CountLocation(2,1)===1,'the opponent graveyard is never raised');}
{const g=fixture();clearHand(g,2);for(const row of [1,2])add(g,112101,row,0,1,5);
 const draug=add(g,132101,8,0,2);for(let i=1;i<4;i++)add(g,112101,8,i,2,6);
 check(g.OpponentStep()&&draug.Snapshot().locationMask===8,'round one with an empty graveyard keeps Draug in hand');}
{const g=fixture();clearHand(g,2);g.match.roundNumber=3;for(const row of [1,2])add(g,112101,row,0,1,5);
 for(let i=0;i<6;i++)add(g,112101,32,i,2,3);
 const draug=add(g,132101,8,0,2);for(let i=1;i<4;i++)add(g,112101,8,i,2,6);
 check(g.OpponentStep()&&(draug.Snapshot().locationMask&7)!==0,'final round with a full graveyard plays Draug');}
globalThis.draugReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'draug127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.draugReport,null,2)+'\n');
