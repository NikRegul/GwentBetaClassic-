'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),ctx=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const strength of [2,3,4])for(const tpl of [122203,132204,142203,152214,162210]){
 Host.strength=strength;const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const spy=add(g,tpl,8,0,2);spy.cardState.timerValue=0;
 add(g,112101,16,0,2);add(g,112101,16,1,2);add(g,112101,8,0,1);
 const other=add(g,112101,8,1,2,14),d=spy.Definition();
 check(!g.AiDrawingSpy(spy),'spent spy is not a drawing action '+tpl+'/'+strength);
 check(g.AiDrawUtility(d,2,spy)===0,'spent instance has zero draw utility');
 check(g.AiPileCandidateValue(spy,2,false,0)===-spy.Snapshot().power.currentPower,'tutors and resurrection do not restore spent draw value');
 check(g.AiCardTempo(spy,true,0,0)===-spy.Snapshot().power.currentPower,'spent instance has only its signed body');
 spy.cardState.timerValue=1;check(g.AiDrawingSpy(spy)&&g.AiDrawUtility(d,2,spy)>0,'fresh copy still has its draw');spy.cardState.timerValue=0;
 const logs=[];Host.log=s=>logs.push(s);check(g.OpponentStep(),'real decision with spent spy resolves');Host.log=null;
 check((other.Snapshot().locationMask&7)!==0&&spy.Snapshot().locationMask===8,'AI plays useful body before spent spy');
 check(!logs.some(s=>/event=(SPY_CARD_EDGE|DRAW_ORDER|SPY_FORECAST)\b/.test(s)),'no fictional extra card is credited');
 check(!g.IsFatal()&&!g.IsPending(),'no unresolved request');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{filename:'spent-spy.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(ctx.report,null,2)+'\n');
