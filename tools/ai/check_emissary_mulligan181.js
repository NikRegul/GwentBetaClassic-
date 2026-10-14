// Deck-only Emissary/Recruit mulligan valuation, including the reported round-three hand.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g){g.live.filter(c=>c.cardState.positionPlayerId===2&&c.cardState.locationMask===8).forEach(c=>c.Move(2,512,0));}
function finalHand(){
 const g=fixture();clearHand(g);g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;
 const emissary=add(g,162314,8,0),peter=add(g,162204,8,1),menno=add(g,162102,8,2);
 // Real remaining bronze unit pool: one Recruit, with no other bronze soldier.
 const replacement=add(g,200031,16,0),recruit=add(g,201617,16,1);
 return {g,emissary,peter,menno,replacement,recruit};
}
{
 const {g,emissary,peter,menno,replacement}=finalHand();
 check(g.AiTutorMulliganPriority(emissary)===30,'reported dead Emissary receives replacement priority');
 check(g.AiTutorTargetCount(emissary)===1,'Emissary recognises its one legal bronze unit');
 check(g.AiMulliganTutorTempo(emissary,[])===-1,'Emissary plus empty Recruit is minus one');
 check(g.AiCardKeepValue(emissary)===-1,'static spy floor no longer hides a negative remaining chain');
 const logs=[];Host.log=s=>logs.push(s);g.AiMulligan(1);Host.log=null;
 check(emissary.Snapshot().locationMask===16&&replacement.Snapshot().locationMask===8,'actual one-swap mulligan replaces the dead Emissary');
 check(peter.Snapshot().locationMask===8&&menno.Snapshot().locationMask===8,'useful Peter and Menno stay in hand');
 check(logs.some(s=>s.includes('event=MULLIGAN_WEAK_TUTOR')&&s.includes('expectedTempo=-1')),'log explains the weak remaining chain');
 check(logs.some(s=>s.includes('DUEL_AI_MULLIGAN outgoing='+emissary.cardState.instanceId)&&s.includes('priority=30')),'log records the actual Emissary exchange');
 check(!g.IsFatal()&&!g.IsPending(),'mulligan leaves no fatal or pending action');
}
for(const round of [1,2,3]){
 const g=fixture();g.match.roundNumber=round;const emissary=add(g,162314,8,4);
 add(g,113301,16,0);add(g,162204,16,1);add(g,112101,16,2);
 check(g.AiTutorTargetCount(emissary)===0,'special/silver/gold cards cannot fill Emissary pool round '+round);
 check(g.AiMulliganTutorTempo(emissary,[])===-2,'empty Emissary retains its real spy cost round '+round);
 check(g.AiTutorMulliganPriority(emissary)===30&&g.AiCardKeepValue(emissary)===-2,'empty Emissary is replaced round '+round);
}
{
 const g=fixture(),emissary=add(g,162314,8,4),recruit=add(g,201617,16,0),soldier=add(g,162308,16,1,2,8);
 check(g.AiTutorTargetCount(recruit)===1,'Recruit uses the real soldier category filter');
 check(g.AiMulliganTutorTempo(recruit,[])>=9,'Recruit values its remaining eight-power soldier and deploy');
 check(g.AiMulliganTutorTempo(emissary,[])>=7,'Emissary can choose Recruit and its useful soldier');
 check(g.AiTutorMulliganPriority(emissary)===0&&g.AiCardKeepValue(emissary)>=11,'healthy Emissary keeps the prior archetype valuation');
 check(g.AiTutorMulliganPriority(recruit)===0,'healthy Recruit has no forced swap priority');
}
{
 const g=fixture(),emissary=add(g,162314,8,4),recruit=add(g,201617,16,0);
 add(g,201617,16,1);add(g,162314,16,2);add(g,132305,16,3);
 check(g.AiTutorTargetCount(recruit)===0,'Recruit cannot pull another Recruit, Emissary or a nonsoldier');
 check(g.AiMulliganTutorTempo(recruit,[])===1&&g.AiTutorMulliganPriority(recruit)===30,'empty Recruit keeps only its one-power body and is replaceable');
}
{
 const g=fixture(),emissary=add(g,162314,8,4);add(g,162314,16,0);add(g,162314,16,1);
 check(g.AiMulliganTutorTempo(emissary,[])===-6,'three different Emissaries are consumed once each without recursive reuse');
 check(g.AiTutorMulliganPriority(emissary)===30,'spy-only nested chain is rejected at mulligan');
}
{
 const g=fixture(),emissary=add(g,162314,8,4);
 const cards=[add(g,142317,16,0,2,12),add(g,142317,16,1,2,14),add(g,142317,16,2,2,20)];
 check(g.AiMulliganTutorTempo(emissary,[])===16,'random two-card offer uses average of pair maxima, not best of whole deck');
 cards[0].Move(2,16,2);cards[2].Move(2,16,0);
 check(g.AiMulliganTutorTempo(emissary,[])===16,'valuation ignores hidden own deck order');
}
{
 const g=fixture(),emissary=add(g,162314,8,4);add(g,162315,16,0);
 check(g.AiMulliganTutorTempo(emissary,[])>0&&g.AiTutorMulliganPriority(emissary)===0,'useful two-power Ambassador is valued by its boost ability, not only its spy body');
}
{
 const {g,emissary,recruit}=finalHand(),before=JSON.stringify(g.live.map(c=>c.Snapshot())),rng=g.random.DrawCount();
 g.AiTutorMulliganPriority(emissary);g.AiCardKeepValue(emissary);g.AiMulliganTutorTempo(emissary,[]);
 check(JSON.stringify(g.live.map(c=>c.Snapshot()))===before&&g.random.DrawCount()===rng,'forecast mutates neither live state nor RNG');
 add(g,162308,16,9,1,100);add(g,142317,8,9,1,100);
 check(g.AiMulliganTutorTempo(emissary,[])===-1,'opponent hidden cards cannot improve own tutor chain');
 recruit.power.SetCurrentPair(4,0);
 check(g.AiMulliganTutorTempo(emissary,[])===2&&g.AiTutorMulliganPriority(emissary)===0,'strengthened Recruit can make the same chain useful');
 emissary.power.SetCurrentPair(5,0);
 check(g.AiMulliganTutorTempo(emissary,[])===-1&&g.AiTutorMulliganPriority(emissary)===30,'spy cost uses strengthened current Emissary power');
}
{
 const g=fixture();clearHand(g);const emissary=add(g,162314,8,0),recruit=add(g,201617,16,0);
 check(g.AiMulliganTutorTempo(emissary,[])===-1,'isolated dead chain forecast');
 check(g.Play(2,emissary.cardState.instanceId,1)&&alive(recruit),'real Emissary plays the last Recruit');
 check(g.Score(2)-g.Score(1)===-1&&!g.IsPending()&&!g.IsFatal(),'forecast equals the actual dead-chain result');
}
{
 const g=fixture(),emissary=add(g,162314,16,0),recruit=add(g,201617,16,1);
 check(g.AiMulliganTutorTempo(emissary,[])===-1,'evaluating a replacement candidate excludes its own deck instance');
 recruit.cardState.isWaitingToDie=true;
 check(g.AiTutorTargetCount(emissary)===0&&g.AiMulliganTutorTempo(emissary,[])===-2,'dying deck cards are not legal continuations');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'emissary-mulligan181.bundle.js',timeout:180000});
console.log(JSON.stringify(context.report));
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
