// Real old/new decision logic in separate VMs, with one shared battle state.
// Only the transport differs from retail: all card effects remain actual WS.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const candidate=path.resolve(process.argv[2]),baseline=path.resolve(process.argv[3]);
const pairs=+(process.argv[4]||46),seed0=+(process.argv[5]||115),output=path.resolve(process.argv[6]||'comparison115.json');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const proof=JSON.parse(fs.readFileSync(path.join(baseline,'comparison.json'),'utf8'));
if(sha(path.join(candidate,'sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'))!==proof.sameDeckCatalogue)
 throw Error('Deck/card catalogue differs: regenerate the comparison baseline');
if(sha(path.join(baseline,'rules.js'))!==proof.baselineRules)throw Error('Baseline rules changed');
for(const name of ['runtime.js','harness.js'])if(sha(path.join(candidate,name))!==sha(path.join(baseline,name)))throw Error('Host adapters differ');
const bridge=String.raw`
function pack(g){
 const nodes=[],seen=new Map();
 function visit(v){if(v===undefined)return {u:1};if(v===null||typeof v!=='object')return v;
  if(seen.has(v))return {r:seen.get(v)};const i=nodes.length;seen.set(v,i);
  const node={type:Array.isArray(v)?'Array':v.constructor.name,fields:{}};nodes.push(node);
  for(const k of Object.keys(v)){
   if(k==='bgCloneEpoch'||k==='bgCloneRef'||k==='aiSimCloner'||k==='visualFrames')continue;
   node.fields[k]=visit(v[k]);}
  return {r:i};}
 const root=visit(g);return JSON.stringify({root,nodes,mem:__mem.get(g),engineRandom:randomState});
}
function unpack(text){const data=JSON.parse(text),objects=data.nodes.map(n=>{
 if(n.type==='Array')return [];if(n.type==='Object')return {};
 if(!/^[SC]BetaGwent\w+$/.test(n.type))throw Error('Unexpected state type '+n.type);
 const Kind=eval(n.type);return new Kind();});
 function value(v){if(v&&typeof v==='object'){if(v.u)return undefined;if('r' in v)return objects[v.r];}return v;}
 for(let i=0;i<objects.length;i++)for(const [k,v] of Object.entries(data.nodes[i].fields))objects[i][k]=value(v);
 const g=value(data.root);if(data.mem)__mem.set(g,data.mem);randomState=data.engineRandom;g.recordVisuals=false;__context(g);return g;
}
let active=null,randomState=1;
Host.tunes=[{},{}];Host.matchStrength=[4,4];Host.strength=4;Host.log=null;
Host.random=()=>{randomState^=randomState<<13;randomState>>>=0;randomState^=randomState>>>17;randomState>>>=0;randomState^=randomState<<5;randomState>>>=0;return randomState/4294967296;};
globalThis.bridge={
 initialize(left,right,seed){randomState=seed>>>0||1;Host.seatIndex=1;__simDepthHost=0;
  active=new CBetaGwentDuelSession();active.AiMulligan=()=>{};
  if(!active.InitializeWithPresets(left,right))throw Error('invalid preset');delete active.AiMulligan;
  active.recordVisuals=false;active.aiSimDamp=40;return pack(active);},
 load(text){active=unpack(text);},dump(){return pack(active);},
 view(){const s=active.Snapshot();return {winner:s.matchWinnerMask,actor:__reversed(active)?0:1,
   mulligan:active.IsMulligan(),pending:active.IsPending(),waiting:active.IsWaitingRound(),current:s.currentPlayerId,fatal:active.IsFatal(),message:active.GetMessage(),reversed:__reversed(active)};},
 initialMulligan(){__context(active);active.AiMulligan(active.mulliganBudget);active.RefreshMulligan();},
 mirror(){__swap(active);const m=__mem.get(active);m.rev=false;m.slots.reverse();__context(active);},
 step(){if(active.IsFatal())throw Error(active.GetMessage());
  if(active.IsMulligan()){__mulligan(active);return;}
  if(active.IsPending()){if(!__pending(active))throw Error('unresolved choice '+active.GetMessage());return;}
  if(active.IsWaitingRound()){if(!active.BeginNextRound())throw Error('round transition');return;}
  if(active.Snapshot().currentPlayerId===1)__swap(active);
  __context(active);if(!active.OpponentStep())throw Error('decision rejected '+active.GetMessage());
 },swap(){__swap(active);}
};`;
function host(folder){const c=vm.createContext({console});
 const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(folder,n),'utf8')).join('\n');
 vm.runInContext(code+'\n'+bridge,c,{filename:'comparison.bundle.js'});return c.bridge;}
const fresh=host(candidate),old=host(baseline),pool=JSON.parse(fs.readFileSync(path.join(candidate,'manifest.json'),'utf8')).presets;
if(pairs<pool.length)throw Error('Cover the whole deck pool');
const summary={schema:2,protocol:'identical raw deal and RNG, mirrored seats, independent version mulligans',candidate,baseline,
 candidateRulesSha256:sha(path.join(candidate,'rules.js')),baselineRulesSha256:proof.baselineRules,
 catalogueSha256:proof.sameDeckCatalogue,pairs,seed:seed0,wins:0,losses:0,draws:0,errors:[],blocks:[],perDeck:{}};
function play(initial,newSeat,mirrored){let h=fresh,steps=0;h.load(initial);if(mirrored)h.mirror();
 const right=newSeat===1?fresh:old;if(right!==h){right.load(h.dump());h=right;}h.initialMulligan();
 for(;steps<500;steps++){
  let s=h.view();if(s.fatal)throw Error(s.message);
  if(s.winner){let w=s.winner;if(s.reversed)w=((w&1)<<1)|((w&2)>>1);return w;}
  // Initial cards and RNG are identical per deck; each version performs its
  // own mulligan. During its UI phase the chooser is physical player one.
  if(!s.mulligan&&!s.pending&&!s.waiting&&s.current===1){h.swap();s=h.view();}
  const chooser=s.mulligan?1-s.actor:s.actor;
  const target=chooser===newSeat?fresh:old;
  if(target!==h){target.load(h.dump());h=target;}
  h.step();
 }throw Error('decision limit');}
let state=seed0>>>0||1;function rnd(){state^=state<<13;state>>>=0;state^=state>>>17;state>>>=0;state^=state<<5;state>>>=0;return state;}
const started=Date.now();
for(let i=0;i<pairs;i++){
 const a=pool[i%pool.length],b=pool[(i+1+rnd()%(pool.length-1))%pool.length],seed=rnd(),initial=fresh.initialize(a,b,seed);let score=0;
 for(const [left,right,newSeat,mirrored] of [[a,b,0,false],[b,a,1,true]]){
  try{const w=play(initial,newSeat,mirrored),d=summary.perDeck[a]||(summary.perDeck[a]={wins:0,losses:0,draws:0});
   if(w===3){summary.draws++;d.draws++;score+=.5;}
   else if(w===(newSeat+1)){summary.wins++;d.wins++;score++;}else{summary.losses++;d.losses++;}
  }catch(e){summary.errors.push({left,right,seed,newSeat,error:String(e.stack||e)});}}
 summary.blocks.push(score/2);summary.seconds=(Date.now()-started)/1000;
 fs.writeFileSync(output,JSON.stringify(summary,null,2));
 if((i+1)%10===0||i+1===pairs)console.log(`${i+1}/${pairs}: new ${summary.wins}, old ${summary.losses}, draw ${summary.draws}, errors ${summary.errors.length}`);
 if(summary.errors.length)break;
}
const n=summary.blocks.length;summary.mean=summary.blocks.reduce((a,b)=>a+b,0)/n;
summary.se=Math.sqrt(summary.blocks.reduce((a,b)=>a+(b-summary.mean)**2,0)/Math.max(1,n-1)/n);
summary.lower99=summary.mean-2.576*summary.se;summary.confirmedBetter=summary.errors.length===0&&summary.lower99>.5;
fs.writeFileSync(output,JSON.stringify(summary,null,2));console.log(JSON.stringify({wins:summary.wins,losses:summary.losses,draws:summary.draws,errors:summary.errors.length,mean:summary.mean,lower99:summary.lower99,confirmedBetter:summary.confirmedBetter,seconds:summary.seconds}));
if(summary.errors.length)process.exitCode=1;
