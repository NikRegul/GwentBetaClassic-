'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function position(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.presetTwo=95;g.leaderTemplateTwo=201580;
 for(let i=0;i<3;i++){add(g,112405,8,i,2,6);add(g,112405,16,i,2,6);add(g,112405,8,i,1,6);}g.archetypeAI.Initialize(g,[],95,201580);g.archetypeAI.Refresh();return g;}
const values=[];
for(const id of [131101,200160,201595,201597]){
 const g=position(),d=BetaGwentDuelDefinition(id),estimate=g.AiCreatedOptionValue(d,2,false),leader=add(g,id,64,0,2),before=g.Score(2)-g.Score(1);
 check(g.UseLeader(2)&&!g.IsFatal()&&!g.IsPending(),'actual supported leader resolves '+id);
 const material=g.Score(2)-g.Score(1)-before;check(estimate===material,'a simple leader option includes its actual additional played/created body '+id);
 values.push({id,estimate,material});
}
// Independent enumeration of distinct offers, including equal and negative values.
for(const xs of [[-5,2,4],[1,1,3,8],[2,4,6,8,10],[-3,-2,0,1,7,12]]){
 const g=position();let total=0,n=0;for(let i=0;i<xs.length;i++)for(let j=i+1;j<xs.length;j++)for(let k=j+1;k<xs.length;k++){total+=Math.max(xs[i],xs[j],xs[k]);n++;}
 check(g.AiExpectedBestThree(xs.slice())===Math.trunc(total/n),'random-three estimate equals all actual distinct triples');
}
const g=position();add(g,201580,64,0,2);const value=g.AiCreatedOptionValue(BetaGwentDuelDefinition(131101),2,false);let seed=0,offer=[];
for(let n=1;n<=3000;n++){
 const pool={v:[]};BetaGwentNilfPool(201580,pool);g.random.Initialize(n);g.ShuffleIds(pool);const ids=pool.v.slice(0,3);
 if(ids.includes(131101)&&ids.every(id=>id===131101||g.AiCreatedOptionValue(BetaGwentDuelDefinition(id),2,false)<value)&&ids.some(id=>BetaGwentDuelDefinition(id).header.power>5)){seed=n;offer=ids;break;}
}
check(seed>0,'a real Usurper offer separates body-only from complete leader valuation');
g.random.Initialize(seed);check(g.UseLeader(2)&&!g.IsFatal()&&!g.IsPending(),'actual Usurper choice completes');
check(g.live.some(c=>c.TemplateId()===131101&&c.Snapshot().positionPlayerId===2&&(c.Snapshot().locationMask&7)!==0),'Usurper actually selects Eredin over the larger printed bodies');
globalThis.report={checks,values,seed,offer,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
