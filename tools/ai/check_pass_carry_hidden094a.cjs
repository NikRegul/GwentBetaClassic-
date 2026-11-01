'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),assert=require('node:assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs'),runtime=createRuntime(path.resolve(process.argv[2]));
let checks=0;const records=[];
for(const decision of [9,10,12])for(const damp of [0,70]){
 const input=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,`fixtures/pass-carry094a/decision-${decision}.json.gz`)))),choices=[];
 for(const hiddenTemplate of [null,112405,152209]){
  const g=runtime.deserialize(input.state);g.aiSimDamp=damp;
  if(hiddenTemplate)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId!==1||![8,16].includes(s.locationMask)||(s.tokenMask&64)!==0)continue;
   const d=runtime.definition(hiddenTemplate);c.definition=d;c.cardState.runtimeTemplate=d.header;c.cardState.runtimeTierMask=d.header.tierMask;
   c.power.ResetTemplatePower(d.header.power,d.header.armor);c.cardState.locationIndex=99-s.locationIndex;
  }
  let ticks=0;while(!g.AiPreparationStep())if(++ticks>10000)throw Error('stalled');
  const forecast=g.AiNextRound094a(),logs=[];runtime.host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{runtime.host.log=null;}
  assert(ok&&!g.IsFatal());checks++;
  choices.push({forecast,choice:logs.filter(s=>/event=(PASS|SELECT|ROUND_TRANSITION)/.test(s))});
 }
 assert.deepEqual(choices[0],choices[1]);checks++;assert.deepEqual(choices[0],choices[2]);checks++;
 records.push({decision,damp,choices});
}
const result={checks,failures:[],records,actualWitcherScript:true,hiddenEnemyIdentityAndOrderIndependent:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({checks,failures:[]}));
