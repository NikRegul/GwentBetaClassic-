// Sweers ranks public unseen-copy estimates, never hidden deck identities or target power.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const cases=[];
for(const strength of [2,3,4]){
 Host.strength=strength;const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const gold=add(g,112101,1,0,1,15),nekker=add(g,132305,2,0,1,4);
 add(g,112101,8,0,1);add(g,132305,16,0,1);add(g,132305,16,1,1);for(let i=2;i<8;i++)add(g,142305,16,i,1);
 g.aiStartingDeckOne.Clear();for(const t of [112101,132305,132305,132305,142305,142305,142305])g.aiStartingDeckOne.PushBack(t);
 const sweers=add(g,162206,1,0,2);g.playStack.PushBack(sweers);check(g.match.ClaimInitialMove(2)===0,'start Sweers real turn');
 const goldValue=g.AiSweersTargetValue(gold),nekkerValue=g.AiSweersTargetValue(nekker);
 check(goldValue===0&&nekkerValue>0,'remaining bronze copies outrank an already played singleton '+strength);
 const before=g.live.map(c=>c.Snapshot()).filter(s=>s.positionPlayerId===1&&s.locationMask===16).map(s=>s.instanceId);
 g.MonsterRequest(sweers,[gold.cardState.instanceId,nekker.cardState.instanceId],2,1,1);
 check(!g.IsFatal()&&!g.IsPending(),'Sweers selection finishes '+strength);
 const milled=before.map(id=>g.FindCard(id)).filter(c=>c.TemplateId()===132305&&c.Snapshot().locationMask===32);
 check(milled.length===2,'Sweers really mills the two bronze copies '+strength);
 check(gold.Snapshot().locationMask===1&&nekker.Snapshot().locationMask===2,'selected visible units are not destroyed');
 cases.push({strength,goldValue,nekkerValue});
}
{
 Host.strength=4;const g=fixture(),target=add(g,132305,1,0,1);
 g.aiStartingDeckOne.Clear();g.aiStartingDeckOne.PushBack(132305);
 for(let i=0;i<5;i++)add(g,142305,16,i,1);
 check(g.AiSweersTargetValue(target)===0,'known starting singleton has no unseen original copy');
 g.aiStartingDeckOne.PushBack(132305);g.aiStartingDeckOne.PushBack(132305);
 const a=g.AiSweersTargetValue(target);
 for(const c of g.live)if(c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===16){const s=c.Snapshot();c.Setup(g,s.instanceId,112101,1,16,s.locationIndex);}
 check(g.AiSweersTargetValue(target)===a,'changing real hidden deck identities cannot change the estimate');
 for(const c of g.live)if(c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===16)c.Move(1,512,0);
 check(g.AiSweersTargetValue(target)===0,'empty opponent deck gives zero milling value');
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'sweers-copies.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
