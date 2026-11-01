'use strict';
const {rt,add,snap,id,check,flush,run,begin,choose,trace,categoryTemplate,finish}=require('./fixture_batch80096.cjs')(process.argv[2]);
for(const side of [1,2])run(201659,side,'Machines all tiers',g=>{
 const machine=categoryTemplate(2199023255552,{exclude:[201659]}),targets=[];for(const seat of [side,3-side])for(const zone of [1,8,16])targets.push({c:add(g,machine,seat,zone,0,30,4),hit:seat===side&&zone===1});const immune=add(g,machine,side,4,0,30,4,256),gold=add(g,machine,side,4,1,30,4);gold.cardState.runtimeTierMask=8;const source=begin(g,201659,side);
 for(const {c,hit}of targets)check(snap(c).power.currentPower===30+(hit?3:0),'Machine active own CURRENT3');check(snap(immune).power.currentPower===33&&snap(gold).power.currentPower===33,'NotTargetable/Gold allowed');check(snap(source).power.currentPower===0,'special resolves to grave/reset');
});
for(const side of [1,2])for(const count of [0,1,4])run(132404,side,'random enemy/current physical/'+count,g=>{
 const order=count===4?[3,0,2,1]:Array.from({length:count},(_,i)=>i),targets=order.map(i=>add(g,132209,3-side,1,i,30,0,i===0?256:0)),hidden=add(g,142307,3-side,4,0,30),draws=trace(g);begin(g,132404,side);
 check(draws.length===(count?1:0),'one candidate RNG even singleton');if(count&&draws.length){const sorted=targets.slice().sort((a,b)=>snap(a).locationIndex-snap(b).locationIndex),chosen=sorted[draws[0].v];for(const c of targets)check(snap(c).power.currentPower===(c===chosen?29:30),'physical enemy candidate ordering');}check(snap(hidden).power.currentPower===30,'hidden excluded');
});
for(const side of [1,2])for(const move of [false,true])run(142309,side,'deploy-or-hand-deck/'+move,g=>{
 const elf=add(g,142103,side,1,0,30),immune=add(g,142103,side,4,0,30,0,256),enemy=add(g,142103,3-side,1,0,30),hand=add(g,142103,side,8,0,30);
 if(move){const source=add(g,142309,side,8,1,30);g.MoveInactiveToIndex(source,side,16,0);flush(g);}else begin(g,142309,side);
 check(snap(elf).power.currentPower===31&&snap(immune).power.currentPower===31,'own active Elf CURRENT1');check(snap(enemy).power.currentPower===30&&snap(hand).power.currentPower===30,'enemy/inactive Elf excluded');
});
for(const side of [1,2])for(const token of [128,256,1])run(201744,side,'boon removal/'+token,g=>{
 const target=add(g,132209,3-side,1,0,30,1),immune=add(g,132209,3-side,1,1,30,1,256);g.weather.ApplyHazard(3-side,1,token);flush(g);target.power.SetCurrentPair(30,1);immune.power.SetCurrentPair(30,1);begin(g,201744,side);check(g.SelectRow(g.requestId,3-side,1),'selected enemy row');flush(g);
 check(snap(target).power.currentPower===29&&snap(immune).power.currentPower===29,'CURRENT damage2 first, immune secondary allowed');check(g.WeatherToken(3-side,1)===(token&~384),'only boon bits removed');
});
for(const side of [1,2])for(const count of [1,2,3])run(112111,side,'whole Aard targets/'+count,g=>{
 const targets=Array.from({length:count},(_,i)=>add(g,132209,3-side,1,i,30,1));begin(g,112111,side);
 for(let i=0;i<count;i++){choose(g,targets[i]);if(i+1<count)check(targets.every(c=>snap(c).power.currentPower===30&&snap(c).locationMask===1),'all targets collected before damage/push');}
 check(targets.every(c=>snap(c).power.currentPower===28&&snap(c).locationMask===2),'all damage3 then forward melee to ranged');check(!g.IsPending(),'clamped set complete');
});
for(const side of [1,2])for(const count of [0,1,3])run(122201,side,'optional shuffled deck set/'+count,g=>{
 const targets=Array.from({length:4},(_,i)=>add(g,132209,side,16,i,30)),draws=trace(g);begin(g,122201,side);check(draws.length===3,'shuffle whole4 even before optional zero selection');
 for(let i=0;i<count;i++){choose(g,targets[i]);if(i+1<count)check(targets.every(c=>snap(c).power.currentPower===30),'entire optional set before any boost');}if(g.IsPending())check(g.FinishTarget(g.requestId),'optional zero/partial finish');flush(g);for(let i=0;i<targets.length;i++){check(snap(targets[i]).power.currentPower===30+(i<count?2:0),'selected deck CURRENT2');check(snap(targets[i]).locationMask===16&&snap(targets[i]).locationIndex===i,'shuffled list does not reorder actual deck');}
});
for(const tid of [142401,201634,200008,200009,132408])for(const side of [1,2])for(const count of [1,4,8])run(tid,side,'shuffle/physical'+count,g=>{
 const ownerSide=[142401,200008].includes(tid),seat=ownerSide?side:3-side,zone=tid===142401?8:2,order=count===8?[7,1,5,0,4,6,2,3]:Array.from({length:count},(_,i)=>i),targets=order.map(i=>add(g,i===0?112101:132209,seat,zone,i,30,1,i===1?256:0));
 const hidden=add(g,142307,seat,zone===8?4:1,0,30),outside=add(g,132209,3-seat,1,0,30),draws=trace(g);begin(g,tid,side,2);
 const cap=tid===142401?2:tid===201634?10:tid===132408?5:6,expected=targets.slice().sort((a,b)=>snap(a).locationIndex-snap(b).locationIndex);
 check(draws.length===count-1,'full eligible list N-1 RNG');let correct=draws.length===count-1;for(let n=count-1,k=0;n>0;n--,k++){if(draws[k]?.n!==n+1){correct=false;break;}const j=draws[k].v;[expected[n],expected[j]]=[expected[j],expected[n]];}check(correct,'source Fisher-Yates bounds');
 if(correct){const chosen=expected.slice(0,cap);for(const c of targets){const hit=chosen.includes(c),delta=hit?tid===142401?1:tid===200008?2:-1:0;check(snap(c).power.currentPower===30+delta,'exact shuffled subset current formula');check(snap(c).power.armor===(hit&&![142401,200008].includes(tid)?0:1),'damage armor applied');}}
 check(snap(hidden).power.currentPower===30&&snap(outside).power.currentPower===30,'hidden/opposite side excluded');
});
for(const side of [1,2])run(152311,side,'BASE2 then armor2',g=>{
 const target=add(g,132209,side,1,0,30,4),before=snap(target),states=[];const orig=g.NilfPowerChanged.bind(g);g.NilfPowerChanged=(...a)=>{if(id(a[1])===id(target))states.push(snap(target));return orig(...a);};begin(g,152311,side);choose(g,target);
 check(snap(target).power.basePower===before.power.basePower+2&&snap(target).power.currentPower===32,'BASE2 retains current offset');check(snap(target).power.armor===6,'add armor2');check(states[0]?.power.basePower===before.power.basePower+2&&states[0]?.power.armor===4,'strengthening precedes armor');
});
for(const side of [1,2])for(const count of [0,1,3])run(200124,side,'initial Alchemy count/'+count,g=>{
 const alchemy=categoryTemplate(8589934592,{type:2}),initial=Array(count).fill(alchemy);if(side===1)g.nilfInitialOne=initial;else g.nilfInitialTwo=initial;add(g,alchemy,side,16,0);const target=add(g,132209,3-side,1,0,30);begin(g,200124,side);
 check(!!g.IsPending()===(count>0),'zero initial count skips request despite current-deck Alchemy');if(count)choose(g,target);check(snap(target).power.currentPower===30-count,'CURRENT damage initial count including duplicates');
});
for(const side of [1,2])for(const count of [0,1,3])run(201774,side,'initial family count/'+count,g=>{
 const initial=Array(count).fill(112111);initial.push(132209);if(side===1)g.nilfInitialOne=initial;else g.nilfInitialTwo=initial;add(g,112111,side,16,0);const source=begin(g,201774,side);
 check(snap(source).power.currentPower===30+3*count,'CURRENT3 per initial listed definition, duplicates count');check(!g.IsPending(),'no request');
});
for(const side of [1,2])for(const power of [9,17,41])run(112201,side,'copy mutable current/'+power,g=>{
 const target=add(g,132209,3-side,1,0,power,4),source=begin(g,112201,side,2,30,3),base=snap(source).power.basePower;choose(g,target);check(snap(source).power.currentPower===power,'SET owner CURRENT selected current');check(snap(source).power.basePower===base&&snap(source).power.armor===3,'owner base/armor retained');check(snap(target).power.currentPower===power&&snap(target).power.armor===4,'target unchanged');
});
for(const side of [1,2])for(const hidden of [false,true])run(162205,side,'Fringilla both neighbours/'+hidden,g=>{
 const left=add(g,hidden?142307:132209,3-side,1,0,17,4),right=add(g,132209,3-side,1,1,30,3,256),other=add(g,132209,side,4,0,30);g.mulliganReactions=true;const source=add(g,162205,side,8,0,30);check(g.PlayBefore(side,id(source),id(right)),'Fringilla insertion');flush(g);
 check(snap(right).power.currentPower===17,'right CURRENT SET from left even hidden/immune');check(snap(right).power.armor===3&&snap(left).power.currentPower===17,'left and armor unchanged');check(snap(other).power.currentPower===30,'other row unchanged');
});
for(const [tid,hits,damage]of [[163101,2,8],[112205,3,2]])for(const side of [1,2])run(tid,side,'repeat surviving exact instance',g=>{
 const target=add(g,132209,3-side,1,0,60,3);begin(g,tid,side);for(let i=0;i<hits;i++){choose(g,target);check(!!g.IsPending()===(i+1<hits),'exact source loop count '+i);}check(snap(target).power.currentPower===60-Math.max(0,hits*damage-3),'repeated current damage with armor');check(g.random.DrawCount()===0,'no RNG');
});
for(const side of [1,2])for(const from of [8,16,32])run(201578,side,'source From damage/'+from,g=>{
 const target=add(g,132209,3-side,1,0,30,2);begin(g,201578,side,2,30,0,from);choose(g,target);check(snap(target).power.currentPower===30-((from===32?6:4)-2),'CURRENT4 or6 only Grave source');
});
for(const side of [1,2])for(const token of [0,1,2048])run(132409,side,'target row weather/'+token,g=>{
 const target=add(g,132209,3-side,1,0,30,2);if(token){g.weather.ApplyHazard(3-side,1,token);flush(g);target.power.SetCurrentPair(30,2);}begin(g,132409,side);choose(g,target);check(snap(target).power.currentPower===30-((token===2048?7:4)-2),'Ekhidna row2048 CURRENT7 else4');
});
finish(process.argv[3],'Second20 of independent80: group/category/current/formula, shuffle physical pools and explicit choice/action sequencing; full external interaction proof remains open.');
