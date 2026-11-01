'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {graph}=require('./source_graph095.cjs'),ciri=graph(112101,381),ocv=graph(112206,353);
ciri.value(345,'Priority',15);ciri.value(122,'Location',8);ciri.value(122,'Index',0);ciri.value(47,'Op',2);ciri.edge(282,'DV',47,'A');ciri.edge(285,'DV',47,'B');ciri.edge(81,'FlowOutTrue',122,'FlowIn');
ocv.variable('Counter',4);ocv.variable('Damage',1);ocv.variable('Remove',1);ocv.value(80,'Index',0);ocv.value(80,'Location',8);ocv.value(48,'Ignore',8);ocv.value(334,'In',0);ocv.value(302,'Operation',0);ocv.value(285,'Operation',2);
ocv.edge(295,'FlowOut',334,'FlowIn');ocv.edge(334,'FlowOut',60,'FlowIn');ocv.edge(60,'FlowOut',80,'FlowIn');ocv.edge(259,'FlowOutBigger',285,'FlowIn');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0;const failures=[],cases=[];const check=(v,s)=>{checks++;if(!v)failures.push(s);};
function hand(g,side,n=3){return Array.from({length:n},(_,i)=>add(g,132209,side,8,i));}
function flush(g){g.FlushEffects();g.FlushDeaths();}
for(const side of [1,2])for(const row of [1,2,4])for(const result of ['loss','tie','win'])for(const mode of ['ordinary','resilient','locked','hidden']){
 const g=fixture(side),held=hand(g,side,12),source=add(g,112101,side,row,0);source.ChangeBasePower(3,true);source.power.SetPermanentPowerAndArmor(2,6);const base=source.Snapshot().power.basePower+2;source.power.SetCurrentPair(base+7,6);source.AddTokens(64|128|256);
 if(mode==='resilient')source.AddTokens(1);if(mode==='locked')source.AddTokens(4);if(mode==='hidden')source.AddTokens(8);
 const ownScore=g.Score(side);add(g,132209,3-side,2,0,Math.max(1,ownScore+(result==='loss'?2:result==='win'?-2:0)));
 const shouldReturn=result==='loss'&&!['locked','hidden'].includes(mode);
 check(g.Pass(g.Snapshot().currentPlayerId)&&g.Pass(g.Snapshot().currentPlayerId),'two genuine round-ending passes');flush(g);const s=source.Snapshot();
 check(s.locationMask===(shouldReturn?8:row),'Ciri score/passive gates '+side+'/'+row+'/'+result+'/'+mode);
 if(shouldReturn){check(s.locationIndex===0,'Ciri graph inserts at hand index0');check(s.power.currentPower===base&&s.power.armor===2&&s.tokenMask===256,'Ciri return resets temporary state, keeps base/permanent/NotTargetable');check(held.every((c,i)=>c.Snapshot().locationIndex===i+1),'Ciri shifts existing hand, including >10 cards');}
 check(!g.IsFatal()&&!g.IsPending(),'Ciri round event completes');cases.push({id:112101,side,row,result,mode,shouldReturn,actual:s});
}
for(const side of [1,2])for(const row of [1,2,4])for(const ticks of [1,2,4]){
 const g=fixture(side),held=hand(g,side,12),source=add(g,112206,side,row,0),enemy=3-side;source.cardState.timerValue=ticks;source.ChangeBasePower(2,true);source.power.SetPermanentPowerAndArmor(3,5);source.power.SetCurrentPair(30,5);source.AddTokens(64|128|256);
 const plain=add(g,132209,enemy,1,0,10),armored=add(g,132209,enemy,2,0,10,2),immune=add(g,112101,enemy,4,0,10,0,256),hidden=add(g,132209,enemy,1,1,10,0,8),special=add(g,113205,enemy,2,1,10),friendly=add(g,132209,side,4,1,10);
 g.BeforeTurnWithEvents(enemy);flush(g);check(source.Snapshot().timerValue===ticks,'Ocvist ignores other turn');
 for(let i=0;i<ticks;i++){g.BeforeTurnWithEvents(side);flush(g);if(i+1<ticks)check(source.Snapshot().locationMask===row&&source.Snapshot().timerValue===ticks-i-1&&plain.Snapshot().power.currentPower===10,'Ocvist decrements positive owner timer without early burst');}
 const s=source.Snapshot();check(s.locationMask===8&&s.locationIndex===0,'Ocvist returns to hand index0');check(s.timerValue===0,'Ocvist spent timer stays zero (ResetInInactive=false)');check(s.power.currentPower===s.power.basePower+s.power.permanentPower&&s.power.armor===0&&s.tokenMask===256,'Ocvist active return resets power/armor/tokens');
 check(plain.Snapshot().power.currentPower===9&&immune.Snapshot().power.currentPower===9,'one damage includes Gold and NotTargetable');check(armored.Snapshot().power.currentPower===10&&armored.Snapshot().power.armor===1,'damage consumes armor');check(hidden.Snapshot().power.currentPower===10&&special.Snapshot().power.currentPower===10&&friendly.Snapshot().power.currentPower===10,'hidden/special/friendly excluded');check(held.every((c,i)=>c.Snapshot().locationIndex===i+1),'Ocvist has no hand-capacity gate');
 // Once spent, ordinary replay leaves timer0 and does not burst again.
 g.match.currentPlayerId=side;g.match.turnActive=true;g.mulliganReactions=true;check(g.Play(side,s.instanceId,row),'replay spent Ocvist');flush(g);check(source.Snapshot().timerValue===0&&source.Snapshot().locationMask===row&&plain.Snapshot().power.currentPower===9,'spent replay does not rearm or burst');
 // Counter is persistent, not inferred solely from the current timer. Restore
 // positive timer externally, then replay: Played sets it to Counter=0.
 g.NorthMoveInactive(source,side,8,true);source.ChangeTimer(2,2);flush(g);
 // Start a fresh actual turn boundary: the previous replay already claimed
 // the initial move. Merely writing currentPlayerId cannot reset that claim.
 g.match.ApplyTurnEnded();g.match.ApplyTurnStarted(enemy);g.match.ApplyTurnEnded();g.match.ApplyTurnStarted(side);g.mulliganReactions=true;
 const clone=rt.cloneSession(g),copy=clone.FindCard(s.instanceId);clone.mulliganReactions=true;check(clone.Play(side,s.instanceId,row),'spent-counter clone replay');flush(clone);check(copy.Snapshot().timerValue===0&&copy.Snapshot().locationMask===8,'clone retains exhausted Counter even after timer restored');
 check(g.Play(side,s.instanceId,row),'spent-counter live replay');flush(g);check(source.Snapshot().timerValue===0&&source.Snapshot().locationMask===8&&plain.Snapshot().power.currentPower===8,'persistent Counter0 replays into timer-triggered burst');
 check(!g.IsFatal()&&!g.IsPending(),'Ocvist owner trigger completes');cases.push({id:112206,side,row,ticks,kind:'owner-turn',actual:s});
}
// Played reinitializes a positive timer from the persistent Counter (initial4).
for(const side of [1,2])for(const timer of [-1,0,1,2,4]){
 const g=fixture(side);g.mulliganReactions=true;const c=add(g,112206,side,8,0);c.cardState.timerValue=timer;check(g.Play(side,c.Snapshot().instanceId,1),'Ocvist unspent play');check(c.Snapshot().timerValue===(timer>0?4:timer),'Played positive timer set from initial Counter4; zero/negative unchanged');
}
// TimerTriggered is a direct trigger. AbilityManager only gates it by Lock,
// not by the passive OwnerLocation/Ambush gates of BeforeTurn.
for(const side of [1,2])for(const zone of [1,8,16,32])for(const locked of [false,true])for(const hidden of [false,true]){
 const g=fixture(side),held=hand(g,side),c=add(g,112206,side,zone,zone===8?3:0),target=add(g,132209,3-side,2,0,10);c.cardState.timerValue=2;if(locked)c.AddTokens(4);if(hidden)c.AddTokens(8);
 c.ChangeTimer(0,2);flush(g);check(c.Snapshot().locationMask===(locked?zone:8),'direct Ocvist TimerTriggered source zones/Lock gate');if(!locked)check(c.Snapshot().locationIndex===0,'direct timer hand index0');check(target.Snapshot().power.currentPower===(locked?10:9),'direct timer burst includes hidden owner but respects Lock');
 c.ChangeTimer(0,2);flush(g);check(target.Snapshot().power.currentPower===(locked?10:9),'zero->zero does not trigger again');check(!g.IsFatal(),'direct timer completes');cases.push({id:112206,side,zone,locked,hidden,kind:'direct-timer'});
}
for(const side of [1,2])for(const mode of ['locked','hidden','zero','negative']){const g=fixture(side),c=add(g,112206,side,1,0),t=add(g,132209,3-side,2,0,10);c.cardState.timerValue=mode==='zero'?0:mode==='negative'?-1:2;if(mode==='locked')c.AddTokens(4);if(mode==='hidden')c.AddTokens(8);const before=c.Snapshot();g.BeforeTurnWithEvents(side);flush(g);check(c.Snapshot().timerValue===before.timerValue&&c.Snapshot().locationMask===1&&t.Snapshot().power.currentPower===10,'Ocvist passive gate '+mode);}
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:[ciri,ocv].map(g=>g.evidence(['AfterRoundTrigger','BeforeTurnTrigger','APassiveTrigger','PlayerGetScoreNode','IntCompareNode','CardTimer','CardData','ChangeCardTimerNode','AbilityManager','TimerTriggered','ChangePowerNode','MoveCardsNode'])),scope:'Ciri round-loss gate and return state/index; Ocvist owner turn, timer direct trigger, Counter persistence/replay/clone, target filters, armor and return state/index. Arbitrary external event ordering, Ciri priority interactions and all damage/death reactions remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failureCount:failures.length,firstFailures:failures.slice(0,12),cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
