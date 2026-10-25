'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function empty(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();return g;}
const results=[];
for(const power of [3,11,19]){
 const g=empty();g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 add(g,112405,8,0,1,8);const card=add(g,112405,8,0,2);
 card.power.ResetTemplatePower(11,0);card.power.SetCurrentPair(power,0);
 const tempo=g.AiExactTempo(card),future=g.aiLastStrategicValue;
 check(tempo===power,'actual played body uses its current power '+power);
 check(future===0,'playing that same body neither cancels its boost nor refunds its debuff '+power);
}
for(const count of [1,2,5,10]){
 const g=empty();add(g,112405,8,0,2,8);add(g,112405,8,1,2,8);add(g,112405,8,0,1,8);
 for(let i=0;i<count;i++)add(g,112405,16,i,2,8);
 const leader=add(g,200168,64,0,2),tempo=g.AiExactTempo(leader),future=g.aiLastStrategicValue;
 const actual=g.AiSimClone();check(actual.AiSimPlay(leader.Snapshot().instanceId)!==-2147483647,'actual Foltest ability resolves '+count);
 const hand=actual.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8);
 const deck=actual.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===16);
 check(hand.every(c=>c.Snapshot().power.currentPower===9)&&deck.every(c=>c.Snapshot().power.currentPower===9),'all real hand/deck units receive +1 '+count);
 check(future===2+Math.floor(count/2),'fractional deck credit survives aggregation '+count);
 results.push({deckCards:count,tempo,future});
}
// Independent oracle: a spent drawing spy has no remaining draw. Increasing
// its body by three must worsen the actual replay by exactly three points.
const swings=[],credits=[];
for(const extra of [0,3]){
 const g=empty();add(g,112405,8,0,1,8);add(g,112405,8,1,2,8);
 const spy=add(g,162210,8,0,2);spy.cardState.timerValue=0;
 if(extra)spy.ChangePower(extra,false);credits.push(g.AiSimBanked());
 const h=g.AiSimClone();swings.push(h.AiSimPlay(spy.Snapshot().instanceId));
 check(!h.IsFatal()&&!h.IsPending(),'spent spy real replay completes '+extra);
}
check(swings[1]-swings[0]===-3,'boosted spent spy gives the opponent three extra actual points');
check(credits[1]-credits[0]===swings[1]-swings[0],'future hand credit agrees with signed replay');
{
 const g=empty(),mage=add(g,200091,8,0,2),spy=add(g,132204,16,0,2);
 add(g,112405,8,0,1,8);add(g,112405,16,0,1,8);
 const h=g.AiSimClone();check(h.AiSimPlay(mage.Snapshot().instanceId)!==-2147483647,'actual Stregobor draw resolves');
 const drawn=h.FindCard(spy.Snapshot().instanceId).Snapshot();
 check(drawn.locationMask===8&&drawn.power.currentPower===1,'Stregobor really reduces the drawn spy to one power');
 check(h.aiLastStrategicValue>=12,'reducing a thirteen-power gift to one is beneficial future utility');
}
globalThis.result={checks,results,spySwings:swings,spyCredits:credits,actualWitcherScript:true};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
