'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0,label='';const failures=[],cases=[];const check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});},snap=c=>c.Snapshot();
function flush(g){g.FlushEffects();g.FlushDeaths();}
function run(tid,side,mode,body){label=tid+'/'+side+'/'+mode;const g=fixture(side,63179+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id:tid,side,mode});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
for(const side of [1,2])for(const passSide of [side,3-side])for(const row of [1,2,4])for(const locked of [false,true])run(142204,side,`${passSide}/${row}/${locked}`,g=>{
 const owner=add(g,142204,side,row,4,10,0,8|(locked?4:0)),units=[0,1,2,3,5,6,7,8].map(i=>add(g,i===6?142307:132209,side,row,i,20,0,i===2?16:0)),other=add(g,132209,side,row===4?2:4,0,20);g.monsters.NilfTrigger(7,{positionPlayerId:passSide});flush(g);
 const trigger=passSide!==side&&!locked;check(((snap(owner).tokenMask&8)===0)===trigger,'only opponent pass unambushes unlocked owner');check(snap(owner).power.currentPower===10,'shape excludes owner');for(const c of units){const s=snap(c),hit=trigger&&[2,3,5,6].includes(s.locationIndex)&&(s.tokenMask&8)===0;check(s.power.currentPower===(hit?22:20),'shape exact neighbour index'+s.locationIndex+' including weather immune, excluding hidden');}check(snap(other).power.currentPower===20,'no other row boost');
});
for(const side of [1,2])for(const zone of [1,8,16,32])for(const hidden of [false,true])for(const locked of [false,true])run(142307,side,`directTimer/${zone}/${hidden}/${locked}`,g=>{
 const owner=add(g,142307,side,zone,0,10);owner.cardState.tokenMask=(hidden?8:0)|(locked?4:0);owner.cardState.timerValue=1;owner.ChangeTimer(0,2);flush(g);check(snap(owner).timerValue===0,'timer set0');check(((snap(owner).tokenMask&8)!==0)===(hidden&&locked),'direct TimerTriggered removes Ambush in any zone unless Lock');check(snap(owner).power.currentPower===10,'no power effect');
});
for(const side of [1,2])for(const turn of [side,3-side])run(142307,side,'two owner ticks/'+turn,g=>{
 g.mulliganReactions=true;const owner=add(g,142307,side,8,0);check(g.Play(side,snap(owner).instanceId,2),'actual deploy');flush(g);check(snap(owner).timerValue===2&&(snap(owner).tokenMask&8)!==0,'deploy timer2 hidden');g.match.currentPlayerId=turn;g.BeforeTurnWithEvents(turn);flush(g);check(snap(owner).timerValue===(turn===side?1:2),'only owner beforeturn ticks');g.BeforeTurnWithEvents(turn);flush(g);check(snap(owner).timerValue===(turn===side?0:2),'second tick0');check(((snap(owner).tokenMask&8)===0)===(turn===side),'second own tick reveals');
});
// Morenn records an AfterPlayed instance and waits for its arrival. AfterPlayed
// alone must not reveal or deal damage; the same identity must arrive later.
for(const side of [1,2])for(const mode of ['correct','other-instance','from-active','hidden-arrival','own-play'])run(142208,side,mode,g=>{
 const owner=add(g,142208,side,2,0,10,0,8),playedSide=mode==='own-play'?side:3-side,target=add(g,132209,playedSide,8,0,25,3),twin=add(g,132209,playedSide,8,1,25,3);target.playFromLocation=mode==='from-active'?1:8;const from=snap(target);if(mode==='from-active')from.locationMask=1;
 // This direct notification preserves the original From position explicitly.
 g.monsters.NilfTrigger(4,from);flush(g);check((snap(owner).tokenMask&8)!==0&&snap(target).power.currentPower===25,'AfterPlayed only records pending identity');
 const moved=mode==='other-instance'?twin:target,old=snap(moved);if(mode==='from-active')old.locationMask=1;moved.Move(playedSide,1,0);if(mode==='hidden-arrival')moved.AddTokens(8);g.MonsterMoved(old);flush(g);const trigger=mode==='correct';
 check(((snap(owner).tokenMask&8)===0)===trigger,'only correct same-instance inactive arrival triggers');check(snap(moved).power.currentPower===(trigger?21:25),'seven damage after armor3 only on correct arrival');if(trigger){const power=snap(moved).power.currentPower;const later=snap(moved);moved.Move(playedSide,4,0);g.MonsterMoved(later);flush(g);check(snap(moved).power.currentPower===power,'one-shot cleared after firing');}
});
for(const side of [1,2])run(142208,side,'actual deploy then arrival',g=>{
 const owner=add(g,142208,side,2,0,10,0,8),victim=add(g,132209,side,4,0,40),played=add(g,142103,3-side,8,0,30,3);g.match.currentPlayerId=3-side;g.mulliganReactions=true;check(g.Play(3-side,snap(played).instanceId,1),'actual opponent unit play');flush(g);
 check((snap(owner).tokenMask&8)!==0&&snap(played).power.currentPower===30,'Morenn waits while deploy target request is open');check(g.IsPending()&&g.pendingIds.includes(snap(victim).instanceId),'opponent deploy target request');if(g.IsPending()){check(g.SelectTarget(g.requestId,snap(victim).instanceId),'opponent deploy resolved');flush(g);}check((snap(owner).tokenMask&8)===0,'Morenn reveals at play completion');check(snap(played).power.currentPower===26,'post-deploy7damage armor3');check(snap(victim).power.currentPower<40,'deploy still resolved');
});
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,scope:'Three ambush graph branches. Morenn uses explicit AfterPlayed/AfterMoved notifications to isolate identity and From filtering; complete native play sequence remains separate.',semanticCoverageComplete:false};if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,failures:failures.length,firstFailures:failures.slice(0,12),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
