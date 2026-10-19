'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function scenario(strength,weatherProfile,nested,deckSpecials){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 const g=fixture();g.weatherProfile=weatherProfile;g.match.roundNumber=2;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=0;
 // The log: only gold Iorveth on our board, enemy ahead, Outlaw through Decree.
 add(g,142103,1,0,2,6);add(g,112101,1,0,1,30);
 const outlaw=add(g,201615,nested?16:8,0),decoys=[];
 for(const id of deckSpecials)decoys.push(add(g,id,16,1+decoys.length));
 const source=nested?add(g,200154,8,8):outlaw;
 const logs=[];Host.log=s=>logs.push(s);let played;
 try{played=g.Play(2,source.Snapshot().instanceId,2);}finally{Host.log=null;}
 check(played&&!g.IsFatal()&&!g.IsPending(),'Outlaw completes '+[strength,weatherProfile,nested,deckSpecials]);
 check(!logs.some(s=>s.includes('DUEL_NESTED_SKIP template=113201')),'no dead Decoy chosen '+[strength,weatherProfile,nested,deckSpecials]);
 return {g,outlaw,source,decoys,logs};
}
for(const strength of [2,3,4])for(const weatherProfile of [false,true])for(const nested of [false,true]){
 const r=scenario(strength,weatherProfile,nested,[113201,113209]);
 check(r.logs.some(s=>s.includes('TARGET_SELECT source=201615')&&s.includes('target=201716')),'Create preferred over illegal Decoy / empty tutor');
 check(r.g.live.some(c=>c.createdCopy&&(c.Snapshot().locationMask&7)!==0&&c.Snapshot().positionPlayerId===2),'created silver elf actually appears');
 check(r.decoys[0].Snapshot().locationMask===16,'unplayable Decoy stays in deck');
 const empty=scenario(strength,weatherProfile,nested,[]);
 check(empty.logs.some(s=>s.includes('TARGET_SELECT source=201615')&&s.includes('target=201716')),'empty special deck uses Create');
 const dead=scenario(strength,weatherProfile,nested,[113201]);
 check(dead.logs.some(s=>s.includes('target=201716')),'Decoy-only special deck uses Create');
}
// Scorch is genuinely better: burn three opposing 30-point units, do not create.
for(const weatherProfile of [false,true]){
 const g=fixture();g.weatherProfile=weatherProfile;add(g,142103,1,0,2,6);
 for(const row of [1,2,4])add(g,112101,row,0,1,30);
 const outlaw=add(g,201615,8,4),decoy=add(g,113201,16,0),scorch=add(g,113309,16,1);
 const logs=[];Host.log=s=>logs.push(s);try{check(g.Play(2,outlaw.Snapshot().instanceId,2),'strong special path starts');}finally{Host.log=null;}
 check(logs.some(s=>s.includes('TARGET_SELECT source=201615')&&s.includes('target=201715')),'use powerful special instead of Create');
 check(g.Score(1)===0&&scorch.Snapshot().locationMask!==16&&decoy.Snapshot().locationMask===16,'real Scorch resolves and invalid Decoy remains');
}
// The side used for a borrowed special must be the actor, not its grave owner.
for(const side of [1,2]){
 const g=fixture(),d=BetaGwentDuelDefinition(113201),other=side===1?2:1;
 check(!g.HasRequiredPlayTargetForSide(d,side),'empty side has no Decoy target');
 add(g,142103,1,0,side,20);check(!g.HasRequiredPlayTargetForSide(d,side),'gold body is not a Decoy target');
 add(g,122308,2,0,other,8);check(!g.HasRequiredPlayTargetForSide(d,side),'opposing bronze is not a Decoy target');
 add(g,122308,2,0,side,8);check(g.HasRequiredPlayTargetForSide(d,side),'own legal bronze enables Decoy');
}
// Branch estimates are read-only and do not peek at or advance random offers.
{const g=fixture(),outlaw=add(g,201615,8,4);add(g,113201,16,0);
 const before=JSON.stringify([g.random,g.live.map(c=>c.Snapshot())]);
 const special=g.AiOutlawBranchValue(201715,2,false),created=g.AiOutlawBranchValue(201716,2,false);
 check(special<0&&created>0,'unavailable special has lower value than real Create pool');
 check(created===g.AiOutlawBranchValue(201716,2,false),'expected Create value deterministic');
 check(before===JSON.stringify([g.random,g.live.map(c=>c.Snapshot())]),'forecast does not mutate RNG, cards or hidden offers');
 check(g.AiManagedDeployValue(outlaw.Definition(),2,false)>0,'tutors now include Outlaw ability value');}
globalThis.outlawReport={checks,actualWitcherScript:true,loggedScenarioReproduced:true,nativeGameTested:false};
`,context,{filename:'isengrim090.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.outlawReport,null,2)+'\n');
