// Revealed copies with different runtime power are different legal replies.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
check=(v,n)=>{if(!v)throw Error(n);checks++;};
function state(g){return JSON.stringify({m:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()]});}
const play=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,peak=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...a){calls++;return play.apply(this,a);};
const examples=[];
for(const order of [[2,15],[15,2],[2,4,15],[15,4,2],[2,4,9,15],[15,9,4,2]]){
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.aiSimDamp=40;
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 const own=add(g,112405,8,0,2,3),ids=order.map((power,i)=>{const c=add(g,112405,8,i,1,power);c.AddTokens(64);return c.Snapshot().instanceId;});
 const source=state(g),model=new CBetaGwentPublicResponseAI();model.Initialize(g,g.AiReplyLimit097());model.keepBranches097=true;
 const root=g.AiSimClone();check(root.AiSimPlay(own.Snapshot().instanceId)!==-2147483647,'actual first move legal');
 const baseline=root.Score(1),expected=[];
 for(const id of ids){const h=root.AiReverseClone();check(h.AiSimPlay(id)!==-2147483647,'each exact revealed copy is a legal native response');expected.push(h.Score(2)-baseline);}
 model.BeginApply(root);const actual=[];let ticks=0;
 while(true){calls=0;const done=model.ApplyStep(root);peak=Math.max(peak,calls);check(calls<=1,'one simulated reply per callback');
  if(model.lastReply097)actual.push(model.lastReply097.Score(2)-baseline);
  if(done)break;if(++ticks>10)throw Error('unbounded reply model');}
 expected.sort((a,b)=>a-b);actual.sort((a,b)=>a-b);
 check(JSON.stringify(expected)===JSON.stringify([...order].sort((a,b)=>a-b)),'independent native continuations realize each distinct revealed runtime power');
 check(JSON.stringify(actual)===JSON.stringify(expected),'model must retain both actual revealed copies, regardless of template equality or storage order');
 check(state(g)===source,'response model leaves real cards and RNG unchanged');
 examples.push({order,expected,actual,evaluated:model.evaluated});
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;
globalThis.report={checks,examples,peakSearchPlays:peak,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
