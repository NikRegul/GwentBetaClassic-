// A real development-game divergence; both continuations use unchanged 0.9.3b.
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const {createRuntime}=require('./beta_js092/session.cjs');
const [candidate,baseline,output]=process.argv.slice(2);
const input=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/four-card-tutor093c.json.gz'))));
const old=createRuntime(path.resolve(baseline)),fresh=createRuntime(path.resolve(candidate)),records=[];
function check(ok,message){if(!ok)throw Error(message);}
function finish(g){
 for(let turn=0;!g.Snapshot().matchWinnerMask;turn++){
  check(turn<50&&!g.IsFatal()&&!g.IsPending()&&!g.mulligan&&!g.waiting,'ordinary final-round continuation');
  const side=g.Snapshot().currentPlayerId;if(side===1)old.swap(g);
  check(g.OpponentStep(),'baseline continuation resolves');if(side===1)old.swap(g);
 }
 return {winner:g.Snapshot().matchWinnerMask,score:[g.Score(1),g.Score(2)]};
}
for(const [name,runtime] of [['baseline',old],['candidate',fresh]]){
 const g=runtime.deserialize(input),logs=[];runtime.host.log=s=>logs.push(s);
 check(g.Snapshot().roundNumber===3&&g.CountLocation(2,8)===4&&g.CountLocation(1,8)===3,'real four-versus-three final');
 check(g.OpponentStep()&&!g.IsFatal()&&!g.IsPending(),'first actual policy play resolves');runtime.host.log=null;
 const selected=logs.find(s=>s.includes('event=SELECT action=card'));
 const after={score:[g.Score(1),g.Score(2)],hand:[g.CountLocation(1,8),g.CountLocation(2,8)]};
 const tail=old.deserialize(runtime.serialize(g));records.push({policy:name,selected,after,result:finish(tail)});
}
const report={candidateFingerprint:fresh.fingerprint,baselineFingerprint:old.fingerprint,kind:'real-development-witness-not-strength-trial',records};
if(output)fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
check(records[0].result.winner===1&&records[1].result.winner===2,'new first move wins under the same baseline continuation that loses after the old move');
check(records[0].selected.includes('template=200048')&&records[1].selected.includes('template=113310'),'tutor before boost is replaced by the winning boost-first order');
console.log(JSON.stringify(report));
