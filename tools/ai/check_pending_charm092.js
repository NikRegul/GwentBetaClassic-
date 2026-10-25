// Deferred charm credit must survive tutor simulation and disappear under a real counter.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function position(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.presetTwo=56;g.leaderTemplateTwo=201743;
 g.archetypeAI.Initialize(g,[],56,201743);g.match.roundNumber=2;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=0;
 g.aiStartingDeckOne=[113301];const miruna=add(g,132108,2,0,2);miruna.cardState.timerValue=2;
 add(g,132305,1,0,2,6);add(g,112405,1,0,1,10);
 const cross=add(g,113209,8,0,2),own=add(g,112405,8,1,2,6);add(g,112405,8,2,2,6);
 const pugach=add(g,132204,16,0,2);add(g,132304,16,1,2);add(g,132304,16,2,2);
 const enemy=[];for(let i=0;i<4;i++)enemy.push(add(g,112405,8,i,1,6));g.archetypeAI.Refresh();return {g,miruna,cross,pugach,own,enemy};}
const {g,miruna,cross,pugach,own,enemy}=position();
const tempo=g.AiExactTempo(cross),future=g.aiLastStrategicValue;
console.log('EXACT_CROSS',JSON.stringify({tempo,future}));
const resolved=g.AiSimClone();check(resolved.AiSimPlay(cross.Snapshot().instanceId)!==-2147483647,'actual tutor resolves');
const gift=resolved.FindCard(pugach.Snapshot().instanceId).Snapshot().power.currentPower;
check(tempo===-gift,'a future charm does not pretend to be immediate catch-up points');
check(future>=gift*2,'actual tutor simulation retains the deferred swing of the actually boosted spy');
const root=resolved.AiSimClone();
check(resolved.Play(1,enemy[0].Snapshot().instanceId,4),'first actual non-intervening enemy body');
check(resolved.Play(2,own.Snapshot().instanceId,1),'actual own follow-up advances the timer');
const before=resolved.Score(2)-resolved.Score(1);
check(resolved.Play(1,enemy[1].Snapshot().instanceId,4),'second actual enemy body');
check(resolved.FindCard(pugach.Snapshot().instanceId).Snapshot().positionPlayerId===2,'the actual timer charms Pugach back');
check(resolved.Score(2)-resolved.Score(1)-before===gift*2-6,'actual deferred swing equals twice current spy power, with enemy body counted separately');
const model=new CBetaGwentPublicResponseAI();model.Initialize(root,1);model.keepBranches097=true;model.BeginApply(root);
let extra=null,killed=false;
for(let tick=0;tick<10;tick++){
 const done=model.ApplyStep(root);
 if(model.lastReply097&&model.lastTemplate097===113301){extra=model.lastExtra097;killed=model.lastReply097.FindCard(miruna.Snapshot().instanceId).Snapshot().locationMask===32;}
 if(done)break;
}
check(killed,'modeled public removal actually kills the pending Miruna');
check(extra===root.FindCard(miruna.Snapshot().instanceId).Snapshot().power.currentPower+gift*2,'counter risk includes both the real killed body and cancelled deferred points');
{
 const {g}=position();g.live.filter(c=>c.Snapshot().locationMask===2&&c.Snapshot().positionPlayerId===2).forEach(c=>c.Move(2,512,0));
 const a=add(g,132108,2,0,2),b=add(g,132108,2,1,2);a.cardState.timerValue=b.cardState.timerValue=1;add(g,132204,2,0,1,13);
 check(g.AiPendingCharmValue(2)===26,'copies sharing one row never count the same prospective victim twice');
}
// A small first-round deficit is not a lost position when a real charm can
// take a forty-point unit. Check the ensuing abilities, not the forecast alone.
for(const strength of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.presetTwo=56;g.leaderTemplateTwo=201743;
 g.archetypeAI.Initialize(g,[],56,201743);g.match.roundNumber=1;g.match.playerOne.crowns=g.match.playerTwo.crowns=0;
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();
 add(g,112101,1,0,2,40);add(g,112101,2,0,2,30);const victim=add(g,112101,1,0,1,40);add(g,112101,2,0,1,32);
 add(g,132201,32,0,2);add(g,122107,32,1,2);
 const nekker=add(g,132305,8,0,2),emptyA=add(g,200539,8,1,2),emptyB=add(g,200539,8,2,2),mira=add(g,132108,8,3,2);add(g,113209,8,4,2);
 add(g,132204,16,0,2);add(g,132107,16,1,2);add(g,122107,16,2,2);
 const replies=[];for(let i=0;i<4;i++)replies.push(add(g,112101,8,i,1,6));
 check(g.OpponentStep()&&!g.IsFatal(),'optional-round decision completes '+strength);
 check((mira.Snapshot().locationMask&7)!==0&&!g.Snapshot().playerTwo.hasPassed,'real high-value charm is tried instead of declaring every card held '+strength);
 check(emptyA.Snapshot().locationMask===8&&emptyB.Snapshot().locationMask===8,'targetless Slyzards are still preserved '+strength);
 const h=g.AiSimClone();check(h.Play(1,replies[0].Snapshot().instanceId,4),'actual first ordinary reply '+strength);
 check(h.Play(2,nekker.Snapshot().instanceId,4),'actual remaining own card advances pending timer '+strength);
 const before=h.Score(2)-h.Score(1);
 check(h.Play(1,replies[1].Snapshot().instanceId,4),'actual second ordinary reply '+strength);
 check(h.FindCard(victim.Snapshot().instanceId).Snapshot().positionPlayerId===2,'actual continuation charms the forty-point unit '+strength);
 check(h.Score(2)-h.Score(1)-before===80-6,'real charm realizes eighty material points separately from opposing body '+strength);
}
globalThis.report={checks,tempo,future,gift,counterExtra:extra,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
