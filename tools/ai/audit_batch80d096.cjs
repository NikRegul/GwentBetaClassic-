'use strict';
const {rt,add,fill,snap,id,check,flush,run,begin,choose,trace,categoryTemplate,finish}=require('./fixture_batch80096.cjs')(process.argv[2]);
for(const side of [1,2])for(const moon of [false,true])run(201599,side,'capture Moon targets before chosen hit/'+moon,g=>{
 const target=add(g,132209,3-side,1,0,30,0),immune=add(g,132209,3-side,1,1,30,0,256),outside=add(g,132209,3-side,4,0,30);if(moon){g.weather.ApplyHazard(3-side,1,2048);flush(g);target.power.SetCurrentPair(30,0);immune.power.SetCurrentPair(30,0);}begin(g,201599,side);choose(g,target);check(snap(target).power.currentPower===(moon?24:25),'chosen receives damage5 plus captured Moon1');check(snap(immune).power.currentPower===(moon?29:30),'NotTargetable Moon secondary eligible');check(snap(outside).power.currentPower===30,'other row unchanged');
});
function crewSetup(g,side,n,row=2){const crew=categoryTemplate(35184372088832,{exclude:[200168,200169,200170]}),left=n?add(g,crew,side,row,0,30):null,right=n>1?add(g,crew,side,row,1,30):add(g,132209,side,row,n?1:0,30);return {left,right};}
function crewBegin(g,tid,side,n){const {left,right}=crewSetup(g,side,n);g.mulliganReactions=true;const source=add(g,tid,side,8,0,30);check(g.PlayBefore(side,id(source),id(right)),'real insertion among captured Crew');flush(g);return source;}
for(const side of [1,2])for(const n of [0,1,2])run(122304,side,'Crew count boosts/'+n,g=>{
 const source=crewBegin(g,122304,side,n);check(snap(source).power.currentPower===30+2*(n+1),'separate CURRENT2 for base plus each Crew');
});
for(const side of [1,2])for(const count of [0,1,3])run(132214,side,'WildHunt hand census/'+count,g=>{
 const hunt=categoryTemplate(1024,{tier:2,exclude:[132214]}),target=add(g,132209,3-side,1,0,30,2);for(let i=0;i<count;i++)add(g,hunt,side,8,i,30);begin(g,132214,side);choose(g,target);check(snap(target).power.currentPower===30-(6+count-2),'CURRENT damage6+eligible hand count');
});
for(const side of [1,2])for(const power of [1,2,3,8])run(132313,side,'clipped drain/'+power,g=>{
 const target=add(g,132209,3-side,1,0,power,7),source=begin(g,132313,side);choose(g,target);check(snap(source).power.currentPower===30+Math.min(3,power),'boost clipped min3/current');if(power>3)check(snap(target).power.currentPower===power-3&&snap(target).power.armor===7,'IgnoreArmor true current drain3');
});
for(const side of [1,2])for(const witcher of [false,true])for(const power of [9,11,30])run(200078,side,'Witcher or survival/'+witcher+'/'+power,g=>{
 const target=add(g,witcher?categoryTemplate(2147483648):132209,3-side,1,0,power,0);begin(g,200078,side);choose(g,target);if(witcher||power>10)check(snap(target).power.currentPower===25,'SET CURRENT25 Witcher directly or non-Witcher survives damage10');else check((snap(target).locationMask&7)===0,'dead non-Witcher not set25');
});
for(const side of [1,2])for(const seat of [side,3-side])run(200518,side,'revealed hand exact power exchange/'+seat,g=>{
 const target=add(g,132209,seat,8,0,17,4,64),hidden=add(g,132209,seat,8,1,19,3),immune=add(g,132209,seat,8,2,19,3,64|256),source=begin(g,200518,side,2,30,2),base=snap(source).power.basePower;check(!g.pendingIds.includes(id(hidden))&&!g.pendingIds.includes(id(immune)),'only revealed nonimmune hand candidates');choose(g,target);check(snap(source).power.currentPower===17&&snap(target).power.currentPower===30,'swap saved CURRENT values');check(snap(source).power.basePower===base&&snap(source).power.armor===2&&snap(target).power.armor===4,'base/armor retained');
});
for(const side of [1,2])for(const n of [0,1,2])run(122303,side,'Crew-dependent three-shape/'+n,g=>{
 const targets=Array.from({length:3},(_,i)=>add(g,132209,3-side,1,i,30,0,i===0?256:0));crewBegin(g,122303,side,n);choose(g,targets[1]);check(targets.every(c=>snap(c).power.currentPower===30-(n+1)),'shape damage1/2/3 according to captured Crew, immune secondary allowed');
});
for(const side of [1,2])for(const frostSide of [side,3-side])for(const prior of [false,true])run(132212,side,'one persistent boost any Frost side/'+frostSide+'/'+prior,g=>{
 if(prior){g.weather.ApplyHazard(frostSide,1,1);flush(g);}const source=begin(g,132212,side,2);if(!prior){g.weather.ApplyHazard(frostSide,1,1);flush(g);}check(snap(source).power.currentPower===36,'one CURRENT6 from any Frost row');g.weather.ApplyHazard(3-frostSide,4,1);flush(g);check(snap(source).power.currentPower===36,'persistent Counter prevents second boost');
});
for(const side of [1,2])for(const killed of [false,true])run(152207,side,'kill then highest grave strengthen/'+killed,g=>{
 const target=add(g,132209,3-side,1,0,killed?6:7),grave=add(g,132209,side,32,0,30),low=add(g,132303,side,32,1,20),base=snap(grave).power.basePower,draws=trace(g);begin(g,152207,side);choose(g,target);check(snap(grave).power.basePower===base+(killed?3:0),'highest current Grave BASE3 iff target dies');check(snap(low).power.currentPower===20,'lower grave unchanged');check(draws.length===(killed?1:0),'only on kill singleton highest RNG');
});
function duel(a,b,aa,ab){let n=0;while(a>0&&b>0&&n++<100){const hit=a;b=Math.max(0,b-Math.max(0,hit-ab));ab=Math.max(0,ab-hit);if(!b)break;const back=b;a=Math.max(0,a-Math.max(0,back-aa));aa=Math.max(0,aa-back);}return {a,b,aa,ab};}
for(const tid of [201618,152202])for(const side of [1,2])for(const a of [7,13])for(const b of [8,25])for(const armor of [0,3])run(tid,side,`alternating duel/${a}/${b}/${armor}`,g=>{
 const target=add(g,132209,3-side,1,0,b,armor),source=begin(g,tid,side,2,a,0),expected=duel(a,b,0,armor);choose(g,target);check(((snap(source).locationMask&7)!==0)===(expected.a>0),'owner alive according to source alternating CURRENT duel');check(((snap(target).locationMask&7)!==0)===(expected.b>0),'target alive according to source duel');if(expected.a>0)check(snap(source).power.currentPower===expected.a&&snap(source).power.armor===expected.aa,'surviving owner exact current/armor; unused Armor3 not granted');if(expected.b>0)check(snap(target).power.currentPower===expected.b&&snap(target).power.armor===expected.ab,'surviving target exact current/armor');
});
for(const side of [1,2])for(const n of [0,1,2])run(122302,side,'Crew sequential requests/'+n,g=>{
 const target=add(g,132209,3-side,1,0,30,2);crewBegin(g,122302,side,n);for(let i=0;i<n+1;i++){choose(g,target);check(!!g.IsPending()===(i<n),'one request per base+Crew attack');}check(snap(target).power.currentPower===30-Math.max(0,2*(n+1)-2),'each CURRENT2 after armor');
});
for(const side of [1,2])run(142314,side,'deploy CURRENT2',g=>{
 const target=add(g,132209,3-side,1,0,30,1);begin(g,142314,side);choose(g,target);check(snap(target).power.currentPower===29&&snap(target).power.armor===0,'chosen enemy CURRENT damage2 armor-aware');check(g.random.DrawCount()===0,'deploy selection no RNG');
});
for(const side of [1,2])for(const reason of [2,4])run(152314,side,'Played then discard reason/'+reason,g=>{
 const target=add(g,132209,3-side,1,0,30),source=begin(g,152314,side),discard=add(g,132209,side,8,0,20);check(snap(target).power.currentPower===28,'Played random CURRENT2');const old=snap(discard);discard.Move(side,32,0);g.MonsterMoved(old,false,reason);flush(g);check(snap(target).power.currentPower===(reason===2?26:28),'discard mask3 accepts Moved2 and excludes Killed4');
});
for(const side of [1,2])for(const zone of [1,8])run(162209,side,'active or revealed hand/'+zone,g=>{
 const target=add(g,132209,3-side,zone,0,30,3,zone===8?64:0),unrevealed=add(g,132209,3-side,8,1,30);begin(g,162209,side);check(!g.pendingIds.includes(id(unrevealed)),'unrevealed hand excluded');choose(g,target);check(snap(target).power.currentPower===(zone===8?1:26),'SET CURRENT1 hand else damage7 armor-aware');check(snap(target).power.armor===(zone===8?3:0),'hand armor retained');
});
for(const side of [1,2])for(const token of [1,128])run(162309,side,'clear exact To then boost/'+token,g=>{
 const target=add(g,132209,side,1,0,30,0,256),hand=add(g,132209,side,8,0,30,0,64),unrevealed=add(g,132209,side,8,1,30);g.weather.ApplyHazard(side,2,token);g.weather.ApplyHazard(side,4,1);flush(g);const source=begin(g,162309,side,2);check(!g.pendingIds.includes(id(source)),'executing source excluded');check(g.WeatherToken(side,2)===(token&~3711),'remove3711 exact To row, retain boon');check(g.WeatherToken(side,4)===1,'other own row untouched');check(!g.pendingIds.includes(id(unrevealed)),'unrevealed hand excluded');choose(g,target);check(snap(target).power.currentPower===33,'own active NotTargetable eligible CURRENT3');
});
for(const side of [1,2])for(const dead of [false,true])run(201620,side,'zero targets/current row Burn/'+dead,g=>{
 const target=add(g,132209,3-side,1,0,dead?1:20),other=add(g,132209,3-side,2,0,20);begin(g,201620,side);check(g.WeatherToken(3-side,1)===(dead?32:0),'SET Burn on captured zero-power active row before deferred grave move');check(g.WeatherToken(3-side,2)===0&&snap(other).power.currentPower===19,'surviving other row no Burn');
});
for(const side of [1,2])for(const power of [3,4])for(const frost of [false,true])run(132309,side,'kill OR surviving Frost/'+power+'/'+frost,g=>{
 const target=add(g,132209,3-side,1,0,power);if(frost){g.weather.ApplyHazard(3-side,1,1);flush(g);target.power.SetCurrentPair(power,0);}const source=begin(g,132309,side);choose(g,target);check(snap(source).power.currentPower===30+(power===3||frost?2:0),'one owner CURRENT2 on kill OR Frost, never double');
});
for(const side of [1,2])for(const killed of [false,true])run(142209,side,'kill boosts template traps',g=>{
 const target=add(g,132209,3-side,1,0,killed?30:31),trap=add(g,142307,side,8,0,20),activeTrap=add(g,142307,side,1,0,20);activeTrap.cardState.tokenMask=0;const source=begin(g,142209,side);choose(g,target);check(snap(trap).power.currentPower===20+(killed?1:0)&&snap(activeTrap).power.currentPower===20+(killed?1:0),'template Ambush8 includes revealed trap copies hand/active');check(snap(source).power.currentPower===30,'owner in execution excluded');
});
for(const side of [1,2])for(const n of [0,1,2])run(201748,side,'Crew damage then push/'+n,g=>{
 const target=add(g,132209,3-side,1,0,30,1);crewBegin(g,201748,side,n);for(let i=0;i<n+1;i++){choose(g,target);check(!!g.IsPending()===(i<n),'base+Crew request count');}check(snap(target).power.currentPower===30-(2*(n+1)-1),'CURRENT2 each iteration');check(snap(target).locationMask===(n===0?2:4),'Forward push after each hit, siege stops');
});
finish(process.argv[3],'Fourth20 of independent80: captured weather/death branches, Crew counts, alternating duels, revealed hand, passive reason and persistent Frost. Full arbitrary external reaction order remains open.');
