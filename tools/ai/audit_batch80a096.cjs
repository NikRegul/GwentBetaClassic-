'use strict';
const {rt,add,fill,snap,id,check,flush,run,begin,choose,trace,categoryTemplate,finish}=require('./fixture_batch80096.cjs')(process.argv[2]);
for(const tid of [152208,152303])for(const side of [1,2])for(const armor of [0,1,4])run(tid,side,'self1/armor'+armor,g=>{
 const source=begin(g,tid,side,2,30,armor);check(snap(source).power.currentPower===30-(armor?0:1),'self CURRENT damage1 armor-aware');check(snap(source).power.armor===Math.max(0,armor-1),'self armor consumed first');check(!g.IsPending(),'no target request');
});
for(const [tid,damage,enemyOnly]of [[132303,5,true],[152304,5,false],[200073,8,false],[201643,10,false]])for(const side of [1,2])for(const seat of [side,3-side])for(const armor of [0,2,9])run(tid,side,`single/${seat}/${armor}`,g=>{
 const valid=add(g,tid===200073?122310:132209,seat,1,0,30,armor),immune=add(g,132209,3-side,4,0,30,0,256),hidden=add(g,142307,3-side,4,1,30),extra=tid===200073?add(g,132303,3-side,1,1,30):null;
 const elf=tid===201643?add(g,142103,3-side,1,1,30):null,source=begin(g,tid,side);
 check(!g.pendingIds.includes(id(source)),'executing owner excluded');check(!g.pendingIds.includes(id(immune))&&!g.pendingIds.includes(id(hidden)),'NotTargetable/Ambush excluded');if(extra)check(!g.pendingIds.includes(id(extra)),'Monster faction excluded');if(elf)check(!g.pendingIds.includes(id(elf)),'Elf category excluded');
 if(enemyOnly&&seat===side){check(!g.IsPending(),'enemy-only empty pool');check(snap(valid).power.currentPower===30,'own target unchanged');}
 else{choose(g,valid);check(snap(valid).power.currentPower===30-Math.max(0,damage-armor),'source numeric damage');check(snap(valid).power.armor===Math.max(0,armor-damage),'armor reduction');}check(g.random.DrawCount()===0,'no RNG');
});
for(const side of [1,2])for(const count of [1,2,3])run(152315,side,'whole3/'+count,g=>{
 const targets=Array.from({length:count},(_,i)=>add(g,132209,i%2?3-side:side,1,i,30)),source=begin(g,152315,side);
 for(let i=0;i<targets.length;i++){choose(g,targets[i]);if(i+1<count)check(targets.every(c=>snap(c).power.currentPower===30),'all picks before any damage');}
 check(targets.every(c=>snap(c).power.currentPower===29),'each selected gets CURRENT1');check(!g.IsPending(),'whole clamped set complete');
});
for(const side of [1,2])for(const row of [1,2,4])for(const hidden of [false,true])run(200115,side,'left-neighbour/'+row+'/'+hidden,g=>{
 const left=add(g,hidden?142307:132209,3-side,row,0,30,3),right=add(g,132209,3-side,row,1,30,3);g.mulliganReactions=true;const source=add(g,200115,side,8,0,30);
 check(g.PlayBefore(side,id(source),id(right)),'spy inserted before right anchor');flush(g);
 check(snap(source).locationIndex===1,'actual To index1');check(snap(left).power.currentPower===(hidden?30:23),'left-only damage10 after armor3');check(snap(right).power.currentPower===30,'right unchanged');check(!g.IsPending(),'no target request');
});
for(const side of [1,2])run(200168,side,'all tiers/zones/template-placement',g=>{
 const cards=[];for(const seat of [side,3-side])for(const zone of [1,8,16,32]){const normal=add(g,132209,seat,zone,0,30,3),spy=add(g,200115,seat,zone,1,30,3);cards.push({c:normal,hit:seat===side&&zone!==32});cards.push({c:spy,hit:false});}const gold=add(g,112101,side,4,0,30),leader=add(g,132209,side,4,1,30);leader.cardState.runtimeTierMask=1;const source=begin(g,200168,side);
 for(const {c,hit}of cards)check(snap(c).power.currentPower===30+(hit?1:0),'CURRENT1 own normal template placement only');check(snap(gold).power.currentPower===31,'Gold eligible');check(snap(leader).power.currentPower===30,'Leader excluded');check(snap(source).power.currentPower===30,'executing owner excluded');
});
for(const tid of [201660,132218])for(const side of [1,2])run(tid,side,'category base strengthening',g=>{
 const mask=tid===201660?33816576:64,matching=categoryTemplate(mask,{exclude:[tid]}),records=[];check(!!matching,'independent source-category fixture exists');
 for(const seat of [side,3-side])for(const zone of [1,8,16,32,512]){const c=add(g,matching,seat,zone,0,30,4);records.push({c,before:snap(c),hit:seat===side&&(zone===1||zone===8||zone===16||zone===512&&tid===201660)});}const source=begin(g,tid,side);
 for(const {c,before,hit}of records){check(snap(c).power.basePower===before.power.basePower+(hit?1:0),'category BASE1 correct side/zone');check(snap(c).power.currentPower===30+(hit?1:0),'current offset preserved');check(snap(c).power.armor===4,'armor retained');}check(snap(source).power.currentPower===30,'executing source excluded');
});
for(const side of [1,2])for(const count of [0,1,4])run(122216,side,'hand-count/'+count,g=>{
 for(let i=0;i<count;i++)add(g,i===0?113301:132209,side,8,i,30);const target=add(g,132209,3-side,1,0,30,1);begin(g,122216,side);
 check(!!g.IsPending()===(count>0),'zero count skips request, executing source not counted');if(count)choose(g,target);check(snap(target).power.currentPower===30-Math.max(0,count-1),'damage captured own hand Type14 count incl Special');
});
for(const side of [1,2])for(const count of [0,1,2])run(152205,side,'optional grave choices/'+count,g=>{
 const targets=[add(g,132209,side,32,0,30,4),add(g,132303,side,32,1,30,4)],enemy=add(g,132209,3-side,32,0,30);const before=targets.map(snap);begin(g,152205,side);check(!g.pendingIds.includes(id(enemy)),'own grave only');
 for(let i=0;i<count;i++){choose(g,targets[i]);if(i+1<count)check(targets.every((c,j)=>snap(c).power.basePower===before[j].power.basePower),'collect choices before strengthening');}if(g.IsPending())check(g.FinishTarget(g.requestId),'optional zero/partial finish accepted');flush(g);
 for(let i=0;i<targets.length;i++){check(snap(targets[i]).power.basePower===before[i].power.basePower+(i<count?3:0),'selected exact BASE3');check(snap(targets[i]).power.currentPower===30+(i<count?3:0),'current offset retained');}check(g.random.DrawCount()===0,'no RNG');
});
for(const side of [1,2])for(const from of [8,16,32])run(152313,side,'original From/'+from,g=>{
 const base=rt.definition(152313).header.power,source=begin(g,152313,side,2,30,4,from);check(snap(source).power.basePower===base+(from===32?3:0),'only Grave origin self BASE3');check(snap(source).power.currentPower===30+(from===32?3:0),'current offset retained');check(snap(source).power.armor===4,'armor unchanged');
});
for(const side of [1,2])for(const seat of [side,3-side])for(const row of [1,2,4])run(153301,side,'row/'+seat+'/'+row,g=>{
 const plain=add(g,132209,seat,row,0,30,1),immune=add(g,132209,seat,row,1,30,1,256),hidden=add(g,142307,seat,row,2,30),other=add(g,132209,seat,row===1?4:1,0,30);begin(g,153301,side);check(g.SelectRow(g.requestId,seat,row),'any-side row accepted');flush(g);
 check(snap(plain).power.currentPower===28&&snap(immune).power.currentPower===28,'all tier/immune row damage3 armor-aware');check(snap(hidden).power.currentPower===30&&snap(other).power.currentPower===30,'hidden/other row excluded');
});
for(const side of [1,2])run(200023,side,'three-shape secondary filters',g=>{
 const row=[add(g,132209,3-side,1,0,30),add(g,132209,3-side,1,1,30,1,256),add(g,132209,3-side,1,2,30,2),add(g,142307,3-side,1,3,30),add(g,132209,3-side,1,4,30)];begin(g,200023,side);choose(g,row[2]);check(snap(row[1]).power.currentPower===27&&snap(row[2]).power.currentPower===28,'immune secondary and pivot damage4');check([row[0],row[3],row[4]].every(c=>snap(c).power.currentPower===30),'outside shape/hidden excluded');
});
for(const side of [1,2])for(const seat of [side,3-side])run(200105,side,'four actions/'+seat,g=>{
 const target=add(g,132209,seat,1,0,30,2),events=[];const old=g.NilfPowerChanged.bind(g);g.NilfPowerChanged=(...args)=>{if(id(args[1])===id(target))events.push(snap(target).power.currentPower);return old(...args);};begin(g,200105,side);choose(g,target);
 check(snap(target).power.currentPower===28&&snap(target).power.armor===0,'four damage1 armor-aware');check(events.length===4,'four separate power actions, not one damage4',{events});
});
for(const side of [1,2])for(const power of [9,17,31])run(200535,side,'current-source/'+power,g=>{
 const target=add(g,132209,3-side,1,0,60,4);begin(g,200535,side,2,power);choose(g,target);check(snap(target).power.currentPower===60-Math.max(0,power-4),'damage owner mutable CURRENT');
});
for(const side of [1,2])for(const from of [8,16,32])run(201622,side,'From/unused armor/'+from,g=>{
 const source=begin(g,201622,side,2,30,0,from);check(snap(source).power.currentPower===30+(from===16?5:0),'only Deck origin CURRENT5');check(snap(source).power.armor===0,'unused graph Armor2 grants nothing');
});
for(const side of [1,2])for(const initial of [[],[132303,132303],[132303],[132303,132303,132303],[132303,132303,132302,132302],[112101,132209]])run(201626,side,'initial census/'+initial.join(','),g=>{
 if(side===1)g.nilfInitialOne=initial;else g.nilfInitialTwo=initial;add(g,132303,side,16,0);const base=rt.definition(201626).header.power,valid=initial.length>0&&initial.some(x=>x===132303)&&[...new Set(initial)].filter(x=>x!==112101&&x!==132209).every(x=>initial.filter(y=>x===y).length===2),source=begin(g,201626,side,2,30,4);
 check(snap(source).power.basePower===(valid?22:base),'each initial Bronze definition exactly2; empty filtered false');check(snap(source).power.currentPower===30+(valid?22-base:0),'SET BASE22 retains current offset');check(snap(source).power.armor===4,'no armor modification');
});
finish(process.argv[3],'First20 of source-reviewed80: explicit numeric/filters/formulas/order and original From branches. Internal PlayFromPile fixture exercises common nested entry, not a full tutor ability proof.');
