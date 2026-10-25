'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
g.presetTwo=95;g.leaderTemplateTwo=201580;g.archetypeAI.Initialize(g,[],95,201580);
add(g,201580,64,0,2);add(g,112405,1,0,2,6);add(g,112405,2,0,2,7);add(g,112405,1,0,1,10);
const held=[],deck=[];for(let i=0;i<10;i++)held.push(add(g,112405,8,i,2,6));for(let i=0;i<12;i++)deck.push(add(g,112405,16,i,2,6));
const handSpy=add(g,132204,8,10,2),deckSpy=add(g,132204,16,12,2);add(g,112405,8,0,1,6);
const d=BetaGwentDuelDefinition(200168),normal=g.AiCreatedOptionValue(d,2,false),immediate=g.AiCreatedOptionValue(d,2,true);
check(normal===5+2+10+6,'created Foltest values actual board, hand and aggregate discounted deck boosts');
check(immediate===7,'immediate value does not pretend hand/deck boosts are board points');
let seed=0,offer=[];
for(let n=1;n<=2000;n++){
 const p={v:[]};BetaGwentNilfPool(201580,p);g.random.Initialize(n);g.ShuffleIds(p);const ids=p.v.slice(0,3);
 if(ids.includes(200168)&&ids.every(id=>id===200168||g.AiCreatedOptionValue(BetaGwentDuelDefinition(id),2,false)<normal)&&
  ids.some(id=>id!==200168&&g.AiCreatedOptionValue(BetaGwentDuelDefinition(id),2,false)>5)){seed=n;offer=ids;break;}
}
check(seed>0,'a real random three-leader offer exercises the missing boost valuation');
const powers=[...held,...deck].map(c=>c.Snapshot().power.currentPower),spyPowers=[handSpy,deckSpy].map(c=>c.Snapshot().power.currentPower);
g.random.Initialize(seed);check(g.UseLeader(2)&&!g.IsPending()&&!g.IsFatal(),'actual Usurper creation completes');
check(g.live.some(c=>c.TemplateId()===200168&&c.Snapshot().positionPlayerId===2&&(c.Snapshot().locationMask&7)!==0),'Usurper actually chooses Foltest from the offered leaders');
check([...held,...deck].every((c,i)=>c.Snapshot().power.currentPower===powers[i]+1),'created Foltest really boosts all twenty-two held/deck bodies');
check([handSpy,deckSpy].every((c,i)=>c.Snapshot().power.currentPower===spyPowers[i]),'held/deck spies really remain unboosted');
globalThis.report={checks,seed,offer,normal,immediate,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
