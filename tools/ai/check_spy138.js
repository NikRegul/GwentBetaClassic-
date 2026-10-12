// 0.6.2 draw-spy card pressure: execute the frozen production WitcherScript.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function position(lead,round=1){
 const g=fixture();g.match.roundNumber=round;
 g.live.filter(c=>c.Snapshot().locationMask!==256).forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));
 add(g,112101,1,0,2,50+lead);add(g,112101,1,0,1,50);
 add(g,112101,16,0,2,8);return g;
}
const spies=[122203,132204,142203,152214,162210];
for(const id of spies)check(position(0).AiDrawSpy(id),'draw spy recognized '+id);
check(position(0).AiSpyCardEdge(12)===4,'ordinary early-round spy adds one-card pressure');
check(position(21).AiSpyCardEdge(12)===4,'nine-point remaining lead gives no safe-lead discount');
check(position(22).AiSpyCardEdge(12)===10,'ten-point remaining lead discounts half the gifted points');
check(position(-14).AiSpyCardEdge(12)===4,'fourteen-point deficit gives no concession discount');
check(position(-15).AiSpyCardEdge(12)===10,'fifteen-point deficit discounts half the gifted points');
for(const lead of [0,22,-15])check(position(lead,3).AiSpyCardEdge(12)===0,'round three retains full point cost '+lead);
{
 const g=position(22);g.match.playerOne.hasPassed=true;
 check(g.AiSpyCardEdge(12)===0,'opponent pass prevents phantom chase pressure');
}
{
 const g=position(22);g.live.filter(c=>c.Snapshot().locationMask===16).forEach(c=>c.Move(2,512,0));
 check(g.AiSpyCardEdge(12)===0,'empty deck prevents phantom card advantage');
}
{
 const g=position(-15,2);g.match.playerOne.crowns=1;
 check(g.AiSpyCardEdge(12)===4,'match-point round does not use the concession discount');
}
globalThis.report={stage:138,checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'check_spy138.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify(context.report));
