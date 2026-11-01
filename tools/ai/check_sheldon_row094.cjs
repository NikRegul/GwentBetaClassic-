// Row choice judged by independently executing the real deploy in every legal row.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],records=[];let serial=-1780000000;
function verify(v,name){checks++;if(!v)failures.push(name);}
function build(counts,side=2,seed=91241){
 const g=fixture(side);g.random.Initialize(seed);
 for(const [row,n]of [[1,counts[0]],[2,counts[1]],[4,counts[2]]])for(let i=0;i<n;i++)add(g,112101,row,i,side,5);
 const card=add(g,142212,8,4,side);g.archetypeAI.Refresh();return [g,card];
}
function probe(g,card,row,side){
 const h=new CBetaGwentCloner().CloneSession(g,--serial),own=h.FindCard(card.Snapshot().instanceId);
 const power=own.Snapshot().power.currentPower,before=h.Score(side);
 verify(h.Play(side,own.Snapshot().instanceId,row)&&!h.IsPending()&&!h.IsFatal(),'actual deploy completes '+side+'/'+row);
 return {row,boost:own.Snapshot().power.currentPower-power,gain:h.Score(side)-before};
}
const sets=[[2,2,1],[4,1,0],[1,4,0],[1,0,4],[8,0,0],[9,7,0],[8,9,9],[0,0,0]];
for(const strength of [1,2,3,4])for(const side of [1,2])for(const counts of sets)for(const seed of [91241,91242]){
 Host.strength=strength;Host.matchStrength=[strength,strength];const [g,card]=build(counts,side,seed);
 const before=JSON.stringify([g.Snapshot(),g.live.map(x=>x.Snapshot()),g.random.DrawCount()]);
 const chosen=g.BestCardRow(side,card.Definition());
 verify(JSON.stringify([g.Snapshot(),g.live.map(x=>x.Snapshot()),g.random.DrawCount()])===before,'placement estimation leaves live state/RNG intact');
 const options=[1,2,4].filter(row=>g.CountLocation(side,row)<9).map(row=>probe(g,card,row,side));
 const selected=options.find(x=>x.row===chosen),best=Math.max(...options.map(x=>x.boost));
 verify(selected&&selected.boost===best,'choose maximum actual deploy boost '+strength+'/'+side+'/'+counts+'/'+seed);
 records.push({strength,side,counts,seed,chosen,options});
}
Host.strength=4;Host.matchStrength=[4,4];
// Public-equivalent reconstruction of game 5, decision 11 in the preserved user log.
{const g=fixture(),specs=[[142312,2,8],[142106,2,13],[142101,1,11],[200535,1,7],[201589,4,4]];
 for(const [template,row,power]of specs)add(g,template,row,g.CountLocation(2,row),2,power);
 const card=add(g,142212,8,4,2,10);g.archetypeAI.Refresh();const row=g.BestCardRow(2,card.Definition());
 const options=[1,2,4].map(r=>probe(g,card,r,2));
 verify([1,2].includes(row),'logged 2/2/1 formation uses a two-unit row');
 verify(options.find(x=>x.row===row).boost===2&&options.find(x=>x.row===4).boost===1,'real engine proves one extra point in logged public formation');
 records.push({publicLogEquivalent:true,chosen:row,options,historicalFullStateReplay:false});}
{const [g,card]=build([9,9,9]);verify(g.BestCardRow(2,card.Definition())===0,'all full rows remain illegal');}
{const [g,card]=build([4,1,0]);g.weather.ApplyHazard(2,1,32);g.archetypeAI.Refresh();
 verify(g.BestCardRow(2,card.Definition())!==1,'severe weather can override the largest row');}
// The generic spreading preference of ordinary units must remain unchanged.
{const [g]=build([4,1,0]);verify(g.BestCardRow(2,BetaGwentDuelDefinition(112101))===4,'ordinary units retain their row policy');}
// Only public rows/occupancy are needed; changing the unseen enemy hand is irrelevant.
{const outcomes=[];for(const hidden of [false,true]){const [g,card]=build([1,4,2]);
 if(hidden)for(const x of g.live){const s=x.Snapshot();if(s.positionPlayerId===1&&[8,16].includes(s.locationMask)){x.definition=BetaGwentDuelDefinition(112405);x.cardState.runtimeTemplate=x.definition.header;x.power.SetCurrentPair(99,12);}}
 outcomes.push(g.BestCardRow(2,card.Definition()));}
 verify(outcomes[0]===outcomes[1],'unseen enemy identities/powers do not change placement');}
globalThis.result={checks,failures,records,actualWitcherScript:true,independentOracle:'Real Play for every legal row; actual self boost and material gain',nativeGameTested:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({fingerprint:report.fingerprint,checks:report.checks,failures:report.failures,cases:report.records.length}));
if(report.failures.length)process.exitCode=1;
