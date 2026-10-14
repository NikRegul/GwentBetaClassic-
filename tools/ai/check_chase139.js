// Replay crowded-hand catch-up decisions using the production WitcherScript.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const decisions=[];
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 Host.strength=strength;
 const g=fixture();g.aiSimDamp=damp;
 g.live.filter(c=>c.cardState.locationMask===8&&c.cardState.positionPlayerId===2).forEach(c=>c.Move(2,512,0));
 g.match.playerOne.hasPassed=true;g.match.roundNumber=2;g.match.playerOne.crowns=1;
 add(g,112101,1,0,1,6);
 // A legal rarity mix: four golds and six silvers, plus an ordinary answer.
 const expensive=[];for(let i=0;i<10;i++){const c=add(g,112101,8,i,2,20+i);c.definition.header.tierMask=i<4?8:4;expensive.push(c);}
 const cheap=add(g,112101,8,10,2,7),logs=[];cheap.definition.header.tierMask=2;Host.log=s=>logs.push(s);
 const draws=g.random.DrawCount();
 check(g.OpponentStep(),'crowded hand completes '+strength+'/'+damp);Host.log=null;
 const selected=cheap.Snapshot().locationMask!==8?'ordinary':'rare';
 decisions.push({strength,damp,selected,reason:logs.filter(s=>/event=(CHASE|SELECT|PASS)/.test(s))});
 check(selected==='ordinary'&&expensive.every(c=>c.Snapshot().locationMask===8),'cheap winning answer survives search cap '+strength+'/'+damp);
 check(g.random.DrawCount()===draws,'search does not consume live RNG '+strength+'/'+damp);
 check(!g.IsFatal()&&!g.IsPending(),'no pending/fatal after catch-up '+strength+'/'+damp);
}
globalThis.report={stage:139,checks,decisions,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'check_chase139.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify(context.report));
