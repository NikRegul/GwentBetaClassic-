'use strict';
// Beta: one CardBanishAttackAction -> one AfterBanished trigger; KillWaitingToDie only without ability instances.
// node tools/ai/check_consume_batch097.cjs <rules-snapshot> [report.json]
const F=require('./fixture_batch100096.cjs')(process.argv[2]);
const {add,snap,id,check,flush,run,begin,choose,finish}=F;
for(const side of [1,2])run(132202,side,'one batch consume reaction',g=>{
 const nek=add(g,132305,side,8,0,4),beh=add(g,132201,side,1,0,8);beh.timerValue=4;
 add(g,132209,side,32,0,5);add(g,132209,side,32,1,5);add(g,132303,side,32,2,5);
 const before=snap(nek).power.currentPower,count=()=>g.live.filter(c=>{const s=snap(c);return s.positionPlayerId===side&&(s.locationMask&7)&&s.runtimeTemplate.templateId!==132201&&s.runtimeTemplate.templateId!==132202;}).length;
 const c0=count();const owner=begin(g,132202,side);
 check(snap(owner).power.currentPower===33,'Mourntart +3',snap(owner).power);
 check(snap(nek).power.currentPower===before+1,'Nekker +1 once',snap(nek).power);
 check(count()-c0===1,'Behemoth one spawn',{spawned:count()-c0,timer:snap(beh).timerValue});
});
for(const side of [1,2])run(201743,side,'deathwish after whole Queen',g=>{
 const n1=add(g,132305,side,1,0,4),n2=add(g,132305,side,1,1,4),deck=[add(g,132305,side,16,0,4),add(g,132305,side,16,1,4)],x=add(g,132209,side,1,2,5);
 g.mulliganReactions=true;const owner=add(g,201743,side,64,0,7);g[side===1?'leaderTemplateOne':'leaderTemplateTwo']=201743;check(g.UseLeader(side),'leader');if(g.pendingLeader)check(g.SelectRow(g.requestId,side,2),'place');flush(g);
 const pick=c=>{check(g.SelectTarget(g.requestId,id(c)),'pick');g.events.Flush();g.FlushEffects();};
 pick(n1);check(deck.every(c=>snap(c).locationMask===16),'no summon before 2nd pick',deck.map(snap).map(s=>s.locationMask));
 pick(n2);pick(x);flush(g);
 check(deck.every(c=>(snap(c).locationMask&7)!==0),'deck Nekkers summoned at end',deck.map(snap).map(s=>s.locationMask));
});
finish(process.argv[3],'Mourntart batch consume reacts once; Arachas Queen deathwishes after whole ability');
