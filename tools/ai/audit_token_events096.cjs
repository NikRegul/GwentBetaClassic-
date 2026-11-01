'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0,label='';const failures=[],cases=[];const check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});};const snap=c=>c.Snapshot(),id=c=>snap(c).instanceId;
function flush(g){g.FlushEffects();g.FlushDeaths();}
function run(tid,side,mode,body){label=tid+'/'+side+'/'+mode;const g=fixture(side,53231+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id:tid,side,mode,draws:g.random.DrawCount()});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
function begin(g,tid,side){g.mulliganReactions=true;const c=add(g,tid,side,8,30);check(g.Play(side,id(c),2),'actual play accepted');flush(g);return c;}
function choose(g,c){check(g.IsPending()&&g.pendingIds.includes(id(c)),'exact target offered');if(!g.IsPending())return false;check(g.SelectTarget(g.requestId,id(c)),'target accepted');flush(g);return true;}
for(const tid of [162107,162201])for(const side of [1,2])for(const passed of [false,true])run(tid,side,'passed'+passed,g=>{
 const enemy=3-side,held=add(g,132209,side,8,0),enemyHeld=add(g,132209,enemy,8,0),gold=add(g,112101,enemy,16,0),bronze=add(g,132403,enemy,16,1),silver=add(g,132209,enemy,16,2),own=add(g,112405,side,16,0);const chosen=tid===162107?bronze:gold,order=[];
 const orig=g.monsters.NilfTrigger.bind(g.monsters);g.monsters.NilfTrigger=(kind,cause,...rest)=>{if(kind===2)order.push({kind,card:cause.instanceId,side:cause.positionPlayerId,own:snap(own).locationMask,enemy:snap(chosen).locationMask,tibor:g.live.find(c=>c.TemplateId()===162107)?.Snapshot().power.currentPower});return orig(kind,cause,...rest);};
 if(passed)g.match[enemy===1?'playerOne':'playerTwo'].hasPassed=true;const source=begin(g,tid,side),base=rt.definition(tid).header.power;
 if(passed){check(snap(source).power.currentPower===base,'passed skips boost');check(snap(chosen).locationMask===16&&snap(own).locationMask===16,'passed skips all draws');check(order.length===0,'no draw event');return;}
 check(snap(chosen).locationMask===8&&snap(chosen).locationIndex===1,'enemy captured first eligible drawn to hand END');check((snap(chosen).tokenMask&64)!==0,'same captured enemy card revealed');check(snap(silver).locationMask===16,'later eligible remains');
 if(tid===162107){check(snap(gold).locationMask===16,'Bronze draw excludes earlier Gold');check(snap(source).power.currentPower===base+15,'Tibor15boost');check(order[0]?.tibor===base+15,'Tibor boost applied before draw event');check(snap(own).locationMask===16,'Tibor does not draw own');check(order.length===1&&order[0].card===id(bronze),'one enemy Drawn event');}
 else{check(snap(own).locationMask===8&&snap(own).locationIndex===1,'own draw appends after held');check(order.length===2&&order[0].side===enemy&&order[1].side===side,'enemy draw before own');check(order[0]?.own===16,'own card remains in deck at enemy draw');}
 check(g.random.DrawCount()===0,'nonrandom DrawCards no RNG');
});
for(const side of [1,2])for(const targetSide of [side,3-side])run(162105,side,'destroy side'+targetSide,g=>{
 const enemy=3-side,target=add(g,132209,targetSide,2,0,20,5),own=add(g,112405,side,16,0),gold=add(g,112101,enemy,16,0),bronze=add(g,132403,enemy,16,1),held=add(g,132209,enemy,8,0);begin(g,162105,side);choose(g,target);
 check(snap(target).locationMask===32,'Destroy is applied before continuation');
 if(targetSide===side){check(g.pendingRally===own,'top own card exact instance awaits placement');if(g.pendingRally){check(g.SelectRow(g.requestId,side,1),'child placed');flush(g);}check((snap(own).locationMask&7)!==0,'own top card played');check(snap(bronze).locationMask===16,'own branch does not enemy draw');}
 else{check(snap(bronze).locationMask===8&&snap(bronze).locationIndex===1&&(snap(bronze).tokenMask&64)!==0,'enemy Bronze draw revealed at hand end');check(snap(gold).locationMask===16&&snap(own).locationMask===16,'earlier Gold and own deck unchanged');}
});
// Self-reveal ability in hand: current player is independent of affected side.
for(const side of [1,2])for(const turn of [side,3-side])for(const zone of [8,16,1])for(const locked of [false,true])run(162306,side,`self/${turn}/${zone}/${locked}`,g=>{
 const source=add(g,162306,side,zone,0,10,0,locked?4:0),other=add(g,162306,side,8,1),enemy=add(g,132209,3-side,2,0,30,3);g.match.currentPlayerId=turn;g.mulliganReactions=true;
 g.NilfReveal(source,true);flush(g);if(g.NilfNextReaction())flush(g);
 const should=turn===side&&zone===8&&!locked;check(!!g.IsPending()===should,'Scorpion reacts only own exact hand reveal on own turn');if(should){choose(g,enemy);check(snap(enemy).power.currentPower===28&&snap(enemy).power.armor===0,'five damage armor-aware');}else check(snap(enemy).power.currentPower===30,'off-turn/zone/lock no damage');check((snap(other).tokenMask&64)===0,'other Scorpion not auto-revealed');
});
for(const side of [1,2])for(const turn of [side,3-side])for(const hidden of [false,true])for(const immune of [false,true])run(162317,side,`${turn}/${hidden}/${immune}`,g=>{
 const source=add(g,162317,side,1,0,10),enemy=add(g,132209,3-side,2,0,40,0,(hidden?8:0)|(immune?256:0)),a=add(g,132209,side,8,0),b=add(g,132209,3-side,8,0);g.match.currentPlayerId=turn;
 g.NilfReveal(a,true);g.NilfReveal(b,true);flush(g);const hit=turn===side&&!hidden;check(snap(enemy).power.currentPower===(hit?36:40),'two reveal actions2damage each; Ignore8 allows NotTargetable');check(g.random.DrawCount()===(hit?2:0),'singleton consumes1 per attack, empty none');
});
for(const side of [1,2])run(162317,side,'batch with priority5 Golems',g=>{
 const mangonel=add(g,162317,side,1,0,10),enemy=add(g,132209,3-side,2,0,60),golems=[add(g,132407,side,16,0),add(g,132407,side,16,1)],targets=[add(g,132209,3-side,8,0),add(g,132209,3-side,8,1)];const obs=[];const orig=g.NilfPowerChanged.bind(g);g.NilfPowerChanged=(...args)=>{if(args[0]===mangonel)obs.push(golems.map(c=>snap(c).locationMask));return orig(...args);};begin(g,162316,side);choose(g,targets[0]);check(targets.every(c=>(snap(c).tokenMask&64)===0),'batch selection reveals nothing until complete');choose(g,targets[1]);check(golems.every(c=>(snap(c).locationMask&7)!==0),'two reveals summon two Golems');check(obs.length===2&&obs.every(z=>z.every(v=>(v&7)!==0)),'priority5 Golem completes whole batch before priority0 Mangonel');check(snap(enemy).power.currentPower===56,'Mangonel iterates two targets');
});
// Brigade reacts once per AddDisloyal ACTION, not once per target. All current
// movement causes tested below use real single-card Move notifications.
for(const side of [1,2])for(const mode of ['inactive-enemy','own-enemy','enemy-row','own-own','self'])run(162307,side,mode,g=>{
 const source=add(g,162307,side,1,0,10),fromSide=mode==='own-enemy'||mode==='own-own'?side:3-side,fromZone=mode==='inactive-enemy'?16:2;
 const target=mode==='self'?source:add(g,132209,fromSide,fromZone,0,20,0,128),old=snap(target),toSide=mode==='own-own'?side:3-side;target.Move(toSide,4,0);if(mode==='own-enemy')target.cardState.tokenMask|=128;g.MonsterMoved(old);flush(g);const should=mode==='inactive-enemy'||mode==='own-enemy';check(snap(source).power.currentPower===(should?12:10),'exact from/to/disloyal movement filter');
});
for(const side of [1,2])run(162308,side,'first own-turn reveal is deferred',g=>{
 const source=add(g,162308,side,1,0,10),target=add(g,132209,3-side,2,0,20,0,128);g.NilfSpyingAdded(snap(target));flush(g);check(!g.IsPending()&&snap(target).power.currentPower===20,'token addition only stores obligation');g.EndTurnWithEvents();flush(g);check(!g.IsPending()&&snap(target).power.currentPower===20,'initial persistent Bool=false skips first own turn end');
});
for(const side of [1,2])for(const mode of ['two-tokens','played-spy','locked-counter'])run(162308,side,'armed/'+mode,g=>{
 const source=add(g,162308,side,1,0,10),a=add(g,132209,3-side,2,0,40,0,128),b=add(g,132209,3-side,4,0,40,0,128),observations=[];
 g.monsters.NilfTrigger(6,{positionPlayerId:side});flush(g); // prior own AfterTurn arms Bool
 if(mode==='played-spy')g.monsters.ScoiaHistory(a);
 else{g.NilfSpyingAdded(snap(a));if(mode==='two-tokens')g.NilfSpyingAdded(snap(b));flush(g);if(mode==='locked-counter'){source.AddLock();source.ToggleLock();}}
 const orig=g.monsters.NilfTrigger.bind(g.monsters);g.monsters.NilfTrigger=(kind,cause,...rest)=>{if(kind===6)observations.push(snap(a).power.currentPower);return orig(kind,cause,...rest);};
 g.EndTurnWithEvents();flush(g);const times=mode==='two-tokens'?2:1;check(!!g.IsPending(),'BeforeTurnEnd requests accumulated damage');for(let n=0;n<times;n++){if(!g.IsPending())break;choose(g,a);}
 check(snap(a).power.currentPower===40-times*2,'one2damage request per token target or played-spy history');check(observations.length===1&&observations[0]===40-times*2,'all damage resolved BEFORE AfterTurn');check(source.nilfCounter===0,'own AfterTurn resets count after actions');
});
// Nested ExecutionStack play: the spy whose ability brings the Brigade into play
// is counted by the deploy clause only. Its AfterMoved notification pops after the
// nested play, so reacting to it again would multiply the boost by the chain depth.
for(const side of [1,2])for(const spies of [1,2,3])run(162307,side,'emissary chain spies'+spies,g=>{
 const enemy=3-side,base=rt.definition(162307).header.power,brigade=add(g,162307,side,16,0),source=add(g,162314,side,8,30);
 for(let n=1;n<spies;n+=1)add(g,162314,side,16,n);
 g.mulliganReactions=true;check(g.Play(side,id(source),2),'actual Emissary play accepted');flush(g);
 let guard=0;
 while(g.IsPending()&&guard++<24){
  if(g.pendingRally){if(!g.SelectRow(g.requestId,side,2)&&!g.SelectRow(g.requestId,enemy,2)&&!g.SelectRow(g.requestId,enemy,1)&&!g.SelectRow(g.requestId,side,1))break;flush(g);continue;}
  const list=(g.pendingIds||[]).slice();if(!list.length)break;
  let pick=list.find(i=>g.registry.Find(i).TemplateId()===162314);if(pick===undefined)pick=list.find(i=>g.registry.Find(i).TemplateId()===162307);if(pick===undefined)pick=list[0];
  check(g.SelectTarget(g.requestId,pick),'Emissary chain choice accepted');flush(g);
 }
 flush(g);
 const playedSpies=g.live.filter(c=>c.TemplateId()===162314&&(snap(c).locationMask&7)!==0).length;
 check(playedSpies===spies,'all Emissaries entered play on the enemy side');
 check(g.live.every(c=>c.TemplateId()!==162314||(snap(c).locationMask&7)===0||snap(c).positionPlayerId===enemy),'every Emissary that entered play sits on the opponent half');
 check(snap(brigade).power.currentPower===base+2*spies,'deploy counts each already present spying unit exactly once');
 const later=add(g,132209,enemy,16,9,20,0,128),old=snap(later);later.Move(enemy,1,0);g.MonsterMoved(old);flush(g);
 check(snap(brigade).power.currentPower===base+2*spies+2,'a spying unit that appears afterwards still boosts');
});
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,scope:'Ten draw/deploy/reveal/spying event branches, two seats. Direct self-reveal reaction drain is explicit; full stack/network semantics not claimed.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,failures:failures.length,firstFailures:failures.slice(0,14),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;
