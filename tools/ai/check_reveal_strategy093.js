// Reveal choices: information, actual golem summons and valid own-hand synergies.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
const helper=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+helper+String.raw`
const failures=[],cases=[];check=(ok,label)=>{checks++;if(!ok){failures.push(label);throw Error(label);}};
function setup(strength,damp){Host.strength=strength;Host.matchStrength=[strength,strength];const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.aiSimDamp=damp;g.aiStartingDeckOne=[112405];
 return g;
}
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 const g=setup(strength,damp),alchemist=add(g,162316,8,0,2),own=add(g,162301,8,1,2),ownOther=add(g,112405,8,2,2);
 const enemy=[add(g,112405,8,0,1),add(g,113310,8,1,1)];
 const golems=[add(g,132407,16,0,2),add(g,132407,16,1,2)];
 const logs=[];Host.log=s=>logs.push(s);const ok=g.Play(2,alchemist.Snapshot().instanceId,1);Host.log=null;
 check(ok&&!g.IsFatal()&&!g.IsPending(),'Alchemist resolves two valid reveals');
 if(!enemy.every(c=>(c.Snapshot().tokenMask&64)!==0))console.log(JSON.stringify({strength,damp,logs:logs.filter(s=>/TARGET_|DUEL_REVEAL|SUMMON/.test(s)),enemy:enemy.map(c=>c.Snapshot()),own:own.Snapshot()}));
 check(enemy.every(c=>(c.Snapshot().tokenMask&64)!==0),'Alchemist reveals opposing cards before exposing our own hand');
 check((own.Snapshot().tokenMask&64)===0&&(ownOther.Snapshot().tokenMask&64)===0,'unneeded own disclosure is avoided');
 if(!golems.every(c=>(c.Snapshot().locationMask&7)!==0))console.log(JSON.stringify({strength,damp,logs,golems:golems.map(c=>c.Snapshot())}));
 check(golems.every(c=>(c.Snapshot().locationMask&7)!==0),'both real golem reveal reactions summon our bodies');
 cases.push({strength,damp,enemyRevealed:enemy.length,golemsPlayed:golems.length});
}
// A mandatory own-hand-only reveal remains legal and can enable a source synergy.
{
 const g=setup(4,70),alchemist=add(g,162316,8,0,2),own=add(g,162301,8,1,2);
 check(g.Play(2,alchemist.Snapshot().instanceId,1)&&!g.IsFatal()&&!g.IsPending(),'own-only legal reveal completes');
 check((own.Snapshot().tokenMask&64)!==0,'own-only reveal is not prohibited');
}
// Opposing unrevealed identities and powers cannot choose which back to reveal.
{
 const choices=[];
 for(const swapped of [false,true]){
  const g=setup(4,70),alchemist=add(g,162316,8,0,2);add(g,112405,8,1,2);
  const a=add(g,swapped?113310:112405,8,0,1,swapped?0:20),b=add(g,swapped?112405:113310,8,1,1,swapped?20:0);
  add(g,132407,16,0,2);const logs=[];Host.log=s=>logs.push(s);g.Play(2,alchemist.Snapshot().instanceId,1);Host.log=null;
  choices.push(logs.filter(s=>s.includes('event=TARGET_SELECT source=162316')).map(s=>/target=(\d+)/.exec(s)[1]));
 }
 check(JSON.stringify(choices[0])===JSON.stringify(choices[1]),'reveal targeting never peeks at hidden identities or power');
}
// Queued arrivals reserve both their instance and their future row slot.
{
 const g=setup(4,70);
 for(const row of [1,2,4])for(let i=0;i<8;i++)add(g,112405,row,i,2);
 const source=add(g,162316,8,0,2),enemy=[add(g,112405,8,0,1),add(g,112405,8,1,1)];
 const golems=[add(g,132407,16,0,2),add(g,132407,16,1,2)];
 check(g.Play(2,source.Snapshot().instanceId,1)&&!g.IsFatal()&&!g.IsPending(),'near-capacity reveal resolves');
 check(golems.every(c=>(c.Snapshot().locationMask&7)!==0),'different golems use both remaining row slots');
 check([1,2,4].every(row=>g.CountLocation(2,row)===9),'queued capacity never exceeds nine per row');
}
{
 const g=setup(4,70),a=add(g,132407,16,0,2),b=add(g,132407,16,1,2);
 g.NorthRandomSummon(a);check(g.NorthSummonPending(a)&&!g.NorthSummonPending(b),'only the queued identity is reserved');
 const clone=g.AiSimClone();check(clone&&clone.NorthSummonPending(clone.FindCard(a.Snapshot().instanceId)),'reservation survives a real search clone');
 clone.FlushDeaths();check((clone.FindCard(a.Snapshot().instanceId).Snapshot().locationMask&7)!==0,'cloned pending summon applies');
 check(a.Snapshot().locationMask===16&&b.Snapshot().locationMask===16,'clone cannot move original deck cards');
 g.FlushDeaths();check((a.Snapshot().locationMask&7)!==0&&!g.NorthSummonPending(a),'applied summon releases its reservation');
}
{
 const g=setup(4,70);for(const row of [1,2,4])for(let i=0;i<9;i++)add(g,112405,row,i,2);
 const a=add(g,132407,16,0,2),enemy=add(g,112405,8,0,1);
 g.NilfReveal(enemy,true);g.FlushDeaths();
 check(a.Snapshot().locationMask===16&&!g.IsFatal(),'a completely full board leaves the golem in deck');
}
globalThis.report={checks,failures,cases,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
