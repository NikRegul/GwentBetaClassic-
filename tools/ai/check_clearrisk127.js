// Clear Skies risk lowers the reason to hold weather in hand.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
let tested=0;
for(const id of [200018,113101,113302,113311,200067]){
 const d=BetaGwentDuelDefinition(id);if(!d||d.weatherToken===0&&id!==200018)continue;
 const safe=fixture();safe.live.filter(c=>c.cardState.positionPlayerId===1&&c.cardState.locationMask===8).forEach(c=>c.Move(1,512,0));
 const risky=fixture();for(let i=0;i<6;i++)add(risky,112101,8,6+i,1);
 const a=safe.AiPublicClearRisk(),b=risky.AiPublicClearRisk(),ra=safe.AiReserveCost(d),rb=risky.AiReserveCost(d);
 console.log('weather',id,'risk',a,b,'reserve',ra,rb);
 check(b>a,'risk grows with the opponent hand '+id);
 check(rb<=ra,'reserve never grows with clear risk '+id);
 if(ra>0){check(rb<ra,'reserve shrinks under clear risk '+id);tested++;}
}
check(tested>0,'at least one weather card has a reserve to shrink');
globalThis.clearReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'clearrisk127.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.clearReport,null,2)+'\n');
