'use strict';const fs=require('fs'),path=require('path'),vm=require('vm');const {load}=require('./diagnose_strategy096.js');
const dir=path.resolve(process.argv[2]),{context:ctx,manifest}=load(dir),fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
check=(v,n)=>{if(!v)throw Error(n);checks++;};
function setup(preset,leader,round=1){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=round;g.match.playerOne.crowns=g.match.playerTwo.crowns=round===3?1:0;
 g.presetTwo=preset;g.leaderTemplateTwo=leader;g.archetypeAI.Initialize(g,[],preset,leader);return g;}
for(const strength of [2,3,4]){Host.strength=strength;Host.matchStrength=[strength,strength];
 const g=setup(93,200166),held=[];for(let i=0;i<3;i++)held.push(add(g,142316,8,i,2));
 for(let i=0;i<7;i++)add(g,142307,8,i+3,2);for(let i=0;i<6;i++)add(g,142310,16,i,2);
 g.archetypeAI.Refresh();check(g.archetypeAI.Mulligan(held[0])>0,'muster duplicates are exchange candidates at level '+strength);
 g.AiMulligan(3);check(g.live.filter(c=>c.TemplateId()===142316&&c.Snapshot().locationMask===8).length===1,'mulligan keeps one muster seed');
 check(g.live.filter(c=>c.TemplateId()===142316&&[8,16].includes(c.Snapshot().locationMask)).length===3,'mulligan preserves all three copies');
 const ships=setup(89,200159);add(ships,200159,64,0,2);const ship=add(ships,152309,16,0,2),corsair=add(ships,200145,8,0,2);
 add(ships,200145,16,1,2);add(ships,200145,16,2,2);add(ships,152211,8,1,2);const cerys=add(ships,200177,16,3,2);
 for(let i=0;i<3;i++)add(ships,112405,8,i,1,10);ships.archetypeAI.Refresh();
 check(ships.archetypeAI.DiscardValue(ship)>ships.archetypeAI.DiscardValue(corsair),'Bran seeds a Corsair target instead of throwing away the resurrector');
 const priority=ships.archetypeAI.LeaderPriority(BetaGwentDuelDefinition(200159));check(priority>=19,'Cerys with sufficient resurrection supply merits early setup');
 ship.Move(2,32,0);check(ships.archetypeAI.DiscardValue(ship)<55,'existing machine grave target removes seed bonus');
 cerys.Move(2,8,4);ships.archetypeAI.Refresh();check(ships.archetypeAI.Mulligan(cerys)>0,'Cerys can go back to deck for Bran');
}
Host.strength=4;Host.matchStrength=[4,4];
function line(first){const g=setup(58,201595,3);add(g,112405,1,0,1,20);
 const rev=add(g,201624,8,0,2),flail=add(g,201633,8,1,2);g.archetypeAI.Refresh();
 const a=first?rev:flail,b=first?flail:rev;check(g.AiSimPlay(a.Snapshot().instanceId)!==-2147483647,'first combo action resolves');
 check(g.Pass(1),'legal opponent pass');check(g.AiSimPlay(b.Snapshot().instanceId)!==-2147483647,'second combo action resolves');return g.Score(2)-g.Score(1);}
check(line(true)===line(false)+4,'Revenant before Flail creates four actual extra points');
const g=setup(58,201595,3),rev=add(g,201624,8,0,2),flail=add(g,201633,8,1,2);for(let i=0;i<3;i++)add(g,112405,8,i,1,9);
g.archetypeAI.Refresh();const withItem=g.archetypeAI.Priority(rev.Definition());flail.Move(2,512,0);g.archetypeAI.Refresh();
check(withItem>g.archetypeAI.Priority(rev.Definition()),'setup value needs a concrete trigger in own hand');
{
 const g=setup(58,201595),rev=add(g,201624,8,0,2);
 add(g,201628,8,1,2);add(g,201628,8,2,2);
 const first=add(g,201633,16,0,2),second=add(g,201633,16,1,2);
 for(let i=0;i<4;i++)add(g,112405,8,i,1,9);
 g.archetypeAI.Refresh();const two=g.archetypeAI.Priority(rev.Definition());
 second.Move(2,512,0);g.archetypeAI.Refresh();const one=g.archetypeAI.Priority(rev.Definition());
 first.Move(2,512,0);g.archetypeAI.Refresh();const none=g.archetypeAI.Priority(rev.Definition());
 check(two>one&&one>none,'consecutive Revenant setup credit follows actual Mage target supply');
}
globalThis.report098={checks,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:120000});const report={fingerprint:manifest.fingerprint,...ctx.report098};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
