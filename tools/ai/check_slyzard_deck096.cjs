'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),assert=require('assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs');
const snapshot=path.resolve(process.argv[2]),rt=createRuntime(snapshot),failures=[],records=[];let checks=0,peakActions=0;
const observe=process.argv.includes('--observe');
function check(value,label){checks++;if(!value){failures.push(label);if(!observe)throw Error(label);}}
const capture=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/slyzard-deck096/decision-15.json.gz'))));
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,pending:g.IsPending()});}
function add(g,id,side,zone,power){const ref={v:0};assert(g.registry.Allocate(ref));const c=rt.newCard();c.Setup(g,ref.v,id,side,zone,g.CountLocation(side,zone));
 if(power!==undefined)c.power.ResetTemplatePower(power,0);g.registry.Put(ref.v,c);g.live.push(c);return c;}
function blank(){rt.host.strength=4;rt.host.matchStrength=[4,4];const g=rt.newSession();assert(g.InitializeWithPresets(61,61));
 for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;
 g.recordVisuals=false;g.externalPolicyMask=0;g.match.currentPlayerId=2;g.match.turnActive=g.match.roundActive=true;g.match.roundNumber=2;
 g.match.playerOne.hasPassed=true;g.match.playerTwo.hasPassed=false;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=0;
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.archetypeAI.Refresh();return g;}
function runPlay(g,id=30){const logs=[];rt.host.log=s=>logs.push(s);let ok;try{ok=g.Play(2,id,1);}finally{rt.host.log=null;}
 check(ok&&!g.IsPending()&&!g.IsFatal(),'real nested play resolves');return logs;}
// Ordinary bodies provide an independent expectation: Nekker gains one from
// the preceding consume; compare the MEAN of every eligible copy to thirteen.
// Neither the maximum, deck order, grave body nor current random seed chooses it.
for(const powers of [[1,21],[10,20]])for(const reverse of [false,true])for(const gravePower of [1,90])for(const seed of [1,109,9921]){
 const g=blank(),source=add(g,200539,2,8),grave=add(g,132305,2,32,gravePower),other=add(g,112405,2,32,2);
 const xs=reverse?powers.slice().reverse():powers;for(const power of xs)add(g,132305,2,16,power);add(g,112405,2,16,13);g.random.Initialize(seed);g.archetypeAI.Refresh();
 const logs=runPlay(g,source.Snapshot().instanceId),mean=(powers[0]+powers[1]+2)/2,expect=mean>13?grave:other;
 check(expect.Snapshot().locationMask===512,'choose average copy result instead of grave/highest/first power');
 const pool=logs.find(s=>s.includes('event=COPY_POOL')&&s.includes('template=132305'));
 check(Boolean(pool)&&pool.includes('copies=2')&&pool.includes('mean='+mean),'diagnostic exposes complete unordered pool');
}
// A pool absent from our deck is not a legal promise, even with huge grave power.
{const g=blank(),source=add(g,200539,2,8),missing=add(g,132305,2,32,99),other=add(g,112405,2,32,2);add(g,112405,2,16,7);g.archetypeAI.Refresh();runPlay(g,source.Snapshot().instanceId);
 check(missing.Snapshot().locationMask===32&&other.Snapshot().locationMask===512,'missing deck copies cannot be selected');}
// Every actual possible Nekker draw in the recorded final position must win,
// including the weakest copies. Force only the random-copy index, not combat.
const ids=capture.state;let base=rt.deserialize(ids);const pool=base.live.filter(c=>{const s=c.Snapshot();return s.positionPlayerId===2&&s.locationMask===16&&c.TemplateId()===132305;}).map(c=>c.Snapshot().instanceId);
check(pool.length===6,'retail position has all six logged matching deck instances');
for(const chosen of pool){const g=rt.deserialize(capture.state),copy=g.monsters.PlayDeckCopy,random=g.RandomIndex;let forced=false;
 g.monsters.PlayDeckCopy=function(source,template){
  if(source.TemplateId()!==200539||template!==132305)return copy.call(this,source,template);
  const ref={v:[]},s=source.Snapshot();this.Query(s.positionPlayerId,16,14,0,0,ref,14);
  const valid=ref.v.filter(id=>g.FindCard(id).TemplateId()===template),index=valid.indexOf(chosen);check(index>=0,'forced copy is in actual random pool');
  let first=true;g.RandomIndex=function(n){if(first){first=false;check(n===valid.length,'force exactly random deck-copy draw');random.call(g,n);forced=true;return index;}return random.call(g,n);};
  try{return copy.call(this,source,template);}finally{g.RandomIndex=random;}
 };
 const logs=runPlay(g),score=[g.Score(2),g.Score(1)];check(forced,'policy selects Nekker pool without forcing its grave choice');
 check(score[0]>score[1]&&score[1]===110,'every real Nekker draw wins the recorded round');
 check(g.Pass(2)&&g.Snapshot().playerOne.crowns===1&&g.Snapshot().playerTwo.crowns===1&&!g.Snapshot().matchWinnerMask,'answering pass really reaches deciding round');records.push({chosen,score,pools:logs.filter(s=>s.includes('event=COPY_POOL'))});
}
// Full policy, cooperative timing and privacy, not only a direct card play.
const proto=Object.getPrototypeOf(base),sim=proto.AiSimPlay;let calls=0;proto.AiSimPlay=function(id){calls++;return sim.call(this,id);};
for(const damp of [0,40,70])for(const staged of [false,true])for(const hidden of [false,true]){
 const g=rt.deserialize(capture.state);g.aiSimDamp=damp;
 if(hidden)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&s.locationMask===16){c.definition=rt.definition(112405);c.cardState.runtimeTemplate=c.definition.header;c.power.ResetTemplatePower(40,9);c.cardState.locationIndex=99-s.locationIndex;}}
 if(staged){const before=state(g);let ticks=0;while(true){calls=0;const done=g.AiPreparationStep();peakActions=Math.max(peakActions,calls);check(calls<=1,'copy pool adds no extra simulation play per callback');check(state(g)===before,'copy forecast preserves live match and RNG');if(done)break;if(++ticks>3000)throw Error('stalled');}}
 const logs=[];rt.host.log=s=>logs.push(s);let ok;try{for(let i=0;i<3;i++){ok=g.OpponentStep();if(ok)break;while(!g.AiPreparationStep()){} }}finally{rt.host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'whole final-card decision resolves');
 check(g.Score(2)>110&&g.Score(1)===110&&g.CountLocation(2,8)===0,'whole policy takes winning Nekker line at every budget/privacy variant');
}
proto.AiSimPlay=sim;
const report={checks,failures,records,peakActions,fingerprint:rt.fingerprint,actualWitcherScript:true,allRandomCopyOutcomesChecked:true,nativeGameplayVerified:false,notStrengthResult:true};
if(process.argv[3]&&!process.argv[3].startsWith('--'))fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks,failures,peakActions,allRandomCopyOutcomesChecked:true}));if(failures.length)process.exitCode=1;
