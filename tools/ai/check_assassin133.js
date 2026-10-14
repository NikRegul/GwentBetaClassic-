// The Assassin kills the unit on its left: with Fringilla in hand it must still
// be placed right of its best victim, not used as a Fringilla setup spy.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
for(const [fringilla,riderFirst] of [[false,false],[true,false],[false,true],[true,true]]){
 const g=fixture();clearHand(g,2);g.match.roundNumber=1;
 add(g,131101,2,0,1,5);const mage=add(g,200026,2,riderFirst?2:1,1,3);const rider=add(g,132310,2,riderFirst?1:2,1,10);
 add(g,162307,1,0,2,10);for(const r of [1,2,4])g.weather.ApplyHazard(2,r,1);
 const assassin=add(g,200115,8,0,2);if(fringilla)add(g,162205,8,1,2);
 check(g.OpponentStep()&&!g.IsFatal(),'AI decides with the Assassin'+(fringilla?' and Fringilla':'')+(riderFirst?', Rider in the middle':', Rider rightmost'));
 check(assassin.Snapshot().locationMask!==8,'Assassin is played'+(fringilla?' with Fringilla in hand':''));
 check((rider.Snapshot().locationMask&7)===0,'Wild Hunt Rider is killed'+(fringilla?' with Fringilla in hand':''));
 check((mage.Snapshot().locationMask&7)!==0,'weak Wild Hunt Mage survives'+(fringilla?' with Fringilla in hand':''));
}
globalThis.assassinReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'assassin133.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.assassinReport,null,2)+'\n');
