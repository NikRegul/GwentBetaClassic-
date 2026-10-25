'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const rows=[];
for(const targetRow of [1,2,4]){
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const leader=add(g,200161,64,0,2),victim=add(g,112405,targetRow,0,1,15);
 add(g,112405,1,0,2,6);add(g,112405,2,0,2,5);for(let i=0;i<3;i++){add(g,112405,8,i,1,6);add(g,112405,8,i,2,6);}
 g.archetypeAI.Refresh();const before=g.Score(2)-g.Score(1),exact=g.AiExactTempo(leader);
 check(exact===16,'shadow leader play includes all ten actual shots '+targetRow);
 check(g.UseLeader(2)&&!g.IsPending()&&!g.IsFatal(),'real Harald play completes '+targetRow);
 check(leader.Snapshot().locationMask===targetRow,'leader stands opposite the real target row '+targetRow);
 check(victim.Snapshot().power.currentPower===5,'the ten native single shots really hit '+targetRow);
 check(g.Score(2)-g.Score(1)-before===16,'native material swing is body plus ten damage '+targetRow);
 rows.push({targetRow,exact,actualGain:g.Score(2)-g.Score(1)-before});
}
globalThis.report={checks,rows,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
