'use strict';
const {rt,add,snap,id,check,flush,run,begin,choose,trace,categoryTemplate,finish}=require('./fixture_batch80096.cjs')(process.argv[2]);
for(const side of [1,2])for(const spying of [false,true])run(162305,side,'Disloyal damage/'+spying,g=>{
 const target=add(g,132209,3-side,1,0,30,2,spying?128:0);begin(g,162305,side);choose(g,target);check(snap(target).power.currentPower===30-((spying?6:3)-2),'CURRENT3 or6 based on token128');
});
for(const side of [1,2])run(200046,side,'Tuirseach category BASE1',g=>{
 const tid=categoryTemplate(536870912,{exclude:[200046]}),records=[];for(const seat of [side,3-side])for(const zone of [1,8,16,32]){const c=add(g,tid,seat,zone,0,30,4);records.push({c,b:snap(c),hit:seat===side&&zone!==32});}const source=begin(g,200046,side);for(const {c,b,hit}of records)check(snap(c).power.basePower===b.power.basePower+(hit?1:0)&&snap(c).power.currentPower===30+(hit?1:0),'BASE1 source category own active/hand/deck only');check(snap(source).power.currentPower===30,'owner explicitly removed');
});
for(const side of [1,2])run(200519,side,'three rows sequential random boost',g=>{
 const targets=[1,2,4].map(row=>add(g,132209,side,row,0,30)),draws=trace(g),atPower=[],orig=g.NilfPowerChanged.bind(g);g.NilfPowerChanged=(...a)=>{if(targets.includes(a[1]))atPower.push(draws.length);return orig(...a);};begin(g,200519,side);check(targets.every(c=>snap(c).power.currentPower===34),'each own row singleton CURRENT4');check(draws.length===3&&draws.every(x=>x.n===1),'one singleton RNG per row');check(JSON.stringify(atPower)==='[1,2,3]','boost action completes before next row random selection',{atPower});
});
for(const side of [1,2])for(const mage of [false,true])run(201630,side,'other Mage current row/'+mage,g=>{
 const target=add(g,132209,3-side,1,0,30,2);if(mage)add(g,categoryTemplate(33554432,{exclude:[201630]}),side,2,0,30);begin(g,201630,side,2);check(!!g.IsPending()===mage,'executing self Mage excluded, another Mage required');if(mage)choose(g,target);check(snap(target).power.currentPower===(mage?25:30),'CURRENT7 when row Mage exists');
});
for(const side of [1,2])for(const seat of [side,3-side])run(201657,side,'own boost/enemy damage/'+seat,g=>{
 const target=add(g,132209,seat,1,0,30,4);begin(g,201657,side);choose(g,target);check(snap(target).power.currentPower===(seat===side?42:22),'same-side CURRENT12 boost else damage12');check(snap(target).power.armor===(seat===side?4:0),'enemy armor only consumed');
});
for(const side of [1,2])for(const power of [2,3,4,10])for(const armor of [0,4])run(142305,side,'survival/'+power+'/'+armor,g=>{
 const target=add(g,132209,3-side,1,0,power,armor),source=begin(g,142305,side);choose(g,target);const alive=power-Math.max(0,3-armor)>0;check(snap(source).power.currentPower===30+(alive?3:0),'owner CURRENT3 iff damaged target survived');
});
for(const side of [1,2])for(const count of [1,2])run(152203,side,'whole set and BASE2N/'+count,g=>{
 const targets=Array.from({length:count},(_,i)=>add(g,132209,side,1,i,30)),source=begin(g,152203,side),base=snap(source).power.basePower;for(let i=0;i<count;i++){choose(g,targets[i]);if(i+1<count)check(targets.every(c=>snap(c).power.currentPower===30)&&snap(source).power.basePower===base,'whole required set before damage and strengthen');}
 check(targets.every(c=>snap(c).power.currentPower===29),'damage1 each selected own unit');check(snap(source).power.basePower===base+2*count&&snap(source).power.currentPower===30+2*count,'owner BASE strengthen2*selected count');
});
for(const side of [1,2])for(const revealed of [false,true])run(200041,side,'Reveal in original played hand/'+revealed,g=>{
 const targets=[1,2,4].map(row=>add(g,132209,3-side,row,0,30)),source=begin(g,200041,side,2,30,0,8,revealed?64:0);for(const c of targets)check(snap(c).power.currentPower===30-(revealed||snap(c).locationMask!==2?1:0),'revealed during deploy hits all enemy rows, else excludes same row');check((snap(source).tokenMask&64)===0,'Reveal removed at final arrival');
});
for(const side of [1,2])for(const power of [1,2,3,9,10,19])run(200055,side,'IntMultiply ceil half/'+power,g=>{
 const target=add(g,132209,3-side,1,0,power,7),source=begin(g,200055,side),drain=Math.ceil(power/2);choose(g,target);check(snap(source).power.currentPower===30+drain,'owner boosts saved CEIL50%, not floor');if(power>1)check(snap(target).power.currentPower===power-drain,'damage CEIL50% ignores armor');check(snap(target).power.armor===(snap(target).locationMask===32?rt.definition(132209).header.armor:7),'armor unchanged while alive; grave reset allowed');
});
for(const side of [1,2])run(200235,side,'template matching secondary',g=>{
 const pivot=add(g,132209,3-side,1,0,30,2),same=add(g,132209,3-side,2,0,30,2,256),other=add(g,132303,3-side,4,0,30,2),own=add(g,132209,side,1,0,30,2);begin(g,200235,side);choose(g,pivot);check(snap(pivot).power.currentPower===28&&snap(same).power.currentPower===28,'all matching enemy template CURRENT4 incl NotTargetable secondary');check(snap(other).power.currentPower===30&&snap(own).power.currentPower===30,'different template/side excluded');
});
for(const side of [1,2])run(200530,side,'highest ties reverse physical',g=>{
 const rows=[];for(const row of [1,2,4]){const units=[2,0,1].map(i=>add(g,132209,3-side,row,i,30,2));rows.push(units);}const draws=trace(g);begin(g,200530,side);check(draws.length===3&&draws.every(d=>d.n===3),'one choice among3 highest per row');for(let row=0;row<3;row++){const sorted=rows[row].slice().sort((a,b)=>snap(b).locationIndex-snap(a).locationIndex),chosen=sorted[draws[row]?.v];for(const c of rows[row])check(snap(c).power.currentPower===30-(c===chosen?4:0),'reverse stable highest tie ordering exact victim');}
});
for(const side of [1,2])for(const token of [0,1,2])run(132102,side,'Frost conditional/'+token,g=>{
 const target=add(g,132209,3-side,1,0,30,2);if(token){g.weather.ApplyHazard(3-side,1,token);flush(g);target.power.SetCurrentPair(30,2);}begin(g,132102,side);choose(g,target);check(snap(target).power.currentPower===30-((token===1?8:4)-2),'CURRENT8 iff current target row Frost1 else4');
});
for(const side of [1,2])for(const power of [6,7,8,20])run(162310,side,'spying kill BASE4/'+power,g=>{
 const target=add(g,132209,3-side,1,0,power,0,128),other=add(g,132209,3-side,1,1,20),source=begin(g,162310,side),base=snap(source).power.basePower;check(!g.pendingIds.includes(id(other)),'nonspying excluded');choose(g,target);check(snap(source).power.basePower===base+(power<=7?4:0),'owner BASE4 only when selected CURRENT==0');
});
for(const side of [1,2])run(200161,side,'ten same-row singleton attacks',g=>{
 const target=add(g,132209,3-side,2,0,30,4),other=add(g,132209,3-side,1,0,30),draws=trace(g);begin(g,200161,side,2);check(draws.length===10&&draws.every(d=>d.n===1),'ten fresh singleton RNG calls');check(snap(target).power.currentPower===24&&snap(target).power.armor===0,'ten separate CURRENT1 hits after armor4');check(snap(other).power.currentPower===30,'other row untouched');
});
for(const side of [1,2])run(201661,side,'Soldier selection and singleton RNG',g=>{
 const soldier=categoryTemplate(67108864,{exclude:[201661]}),a=add(g,soldier,side,1,0,30),b=add(g,soldier,side,4,0,30,0,256),enemy=add(g,soldier,3-side,1,0,30),draws=trace(g);begin(g,201661,side);choose(g,a);check(snap(a).power.currentPower===32&&snap(b).power.currentPower===32,'all matching own active instances boosted2');check(snap(enemy).power.currentPower===30,'enemy copy unchanged');check(draws.length===1&&draws[0].n===1,'chosen-singleton random node still consumes RNG');
});
for(const side of [1,2])run(113401,side,'capture wounded before clear',g=>{
 const wounded=add(g,132209,side,1,0,4,3),healthy=add(g,132209,side,1,1,30,3),other=add(g,132209,side,2,0,4,3);g.weather.ApplyHazard(side,1,1);flush(g);wounded.power.SetCurrentPair(4,3);begin(g,113401,side);check(snap(wounded).power.currentPower===6,'wounded in previously hazardous row boosted2');check(snap(healthy).power.currentPower===30&&snap(other).power.currentPower===4,'healthy/row without hazard excluded');check(g.WeatherToken(side,1)===0,'hazard removed');
});
for(const side of [1,2])run(122310,side,'equal current/source category32',g=>{
 const matching=categoryTemplate(32,{exclude:[122310]}),nonmatching=add(g,142103,side,4,0,30),a=add(g,matching,side,1,0,30),b=add(g,matching,side,8,0,30),c=add(g,matching,side,16,0,29),enemy=add(g,matching,3-side,1,0,30),source=begin(g,122310,side);check(snap(a).power.currentPower===31&&snap(b).power.currentPower===31,'equal current own category32 active/hand/deck');check(snap(c).power.currentPower===29&&snap(enemy).power.currentPower===30,'unequal/other side excluded');check(snap(nonmatching).power.currentPower===30,'equal-current non-category target excluded');check(snap(source).power.currentPower===31,'owner explicitly appended');
});
for(const side of [1,2])for(const targetPower of [8,9])run(142103,side,'kill/hand Elf boost/'+targetPower,g=>{
 const target=add(g,132209,3-side,1,0,targetPower),elf=add(g,142103,side,8,0,20),other=add(g,132209,side,8,1,20);begin(g,142103,side);choose(g,target);check(snap(elf).power.currentPower===20+(targetPower===8?1:0),'hand Elf boosted1 only on kill');check(snap(other).power.currentPower===20,'non-Elf hand unchanged');
});
for(const side of [1,2])for(const graveSide of [side,3-side])run(200020,side,'banish then boost current/'+graveSide,g=>{
 const grave=add(g,132209,graveSide,32,0,17,4,4),target=add(g,132209,side,1,0,30);begin(g,200020,side);choose(g,grave);check(snap(grave).locationMask===512,'banish precedes active target request');choose(g,target);check(snap(target).power.currentPower===47,'CURRENT boost uses17 retained through Grave->Void');
});
for(const side of [1,2])run(200135,side,'all row choices before any damage',g=>{
 const targets=[1,2,4].map(row=>add(g,132209,3-side,row,0,30)),draws=trace(g),atPower=[],orig=g.NilfPowerChanged.bind(g);g.NilfPowerChanged=(...a)=>{if(targets.includes(a[1]))atPower.push(draws.length);return orig(...a);};begin(g,200135,side);check(targets.every(c=>snap(c).power.currentPower===27),'CURRENT3 chosen singleton each row');check(draws.length===3&&atPower.every(n=>n===3),'all three row RNG selections precede first damage');
});
finish(process.argv[3],'Third20 of independent80: conditionals, categories, initial revelation, ceil arithmetic, grouped/sequential random actions and exact instance banish.');
