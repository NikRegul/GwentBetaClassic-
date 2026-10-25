// Parameterized, independently seeded endgame positions with known outcomes.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),output=path.resolve(process.argv[3]);
const samples=Number(process.argv[4]||64),seed=Number(process.argv[5]||91020260);
const damp=Number(process.argv[6]||0);
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
const crypto=require('crypto');
for(const [name,digest] of Object.entries(manifest.snapshotFiles))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(snapshot,name))).digest('hex')!==digest)throw Error('Changed snapshot: '+name);
if(!Number.isInteger(samples)||samples<1||samples>10000)throw Error('Invalid sample count');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
const ctx=vm.createContext({console:{log(){}},samples,seed,damp,fingerprint:manifest.fingerprint});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
let state=seed>>>0;const results=[];
function rnd(n){state^=state<<13;state>>>=0;state^=state>>>17;state>>>=0;state^=state<<5;state>>>=0;return state%n;}
for(let sample=0;sample<samples;sample++){
 const a=12+rnd(14),c=3+rnd(6),d=a-c+1+rnd(3),b=a+8+rnd(18);
 const g=fixture();g.live.forEach(card=>card.Move(card.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=damp;
 const finisher=add(g,112405,8,0,1,b);finisher.AddTokens(64);
 add(g,112405,1,0,1,a);add(g,112405,1,0,2,c);
 const control=add(g,113309,8),body=add(g,112405,8,1,2,d);
 const first=g.OpponentStep(),order=control.Snapshot().locationMask===8?'body':'control';
 let response=false,last=false;
 if(first&&!g.IsFatal()&&!g.IsPending()&&!g.match.playerTwo.hasPassed){response=g.Play(1,finisher.Snapshot().instanceId,1);if(response)last=g.OpponentStep();}
 // Waiting is a forced win: c+d>a, c+d<b, and Scorch can remove b.
 // Playing Scorch first loses. A pass also loses against the known body.
 const pass=!!(first&&response&&last&&!g.IsFatal()&&!g.IsPending()&&g.Score(2)>g.Score(1));
 results.push({family:'last-say',sample,a,b,c,d,order,own:g.Score(2),enemy:g.Score(1),pass});
 // Independent families include the opposite tactical choice, not only
 // different numerical copies of the successful last-say position.
 function blank(round=1){const h=fixture();h.live.forEach(card=>card.Move(card.Snapshot().positionPlayerId,512,0));h.aiStartingDeckOne.Clear();h.aiStartingDeckTwo.Clear();h.aiSimDamp=damp;h.match.roundNumber=round;h.match.playerOne.crowns=h.match.playerTwo.crowns=round===3?1:0;return h;}
 function decision(h){return h.OpponentStep()&&!h.IsFatal()&&!h.IsPending();}
 for(const strength of [2,3,4]){
  Host.strength=strength;const h=blank(),gap=3+rnd(5),own=2+rnd(12);h.match.playerOne.hasPassed=true;
  add(h,112405,1,0,1,own+gap);add(h,112405,1,0,2,own);
  const cheap=add(h,112405,8,0,2,gap+1),gold=add(h,112102,8);
  const ok=decision(h);results.push({family:'minimum-catch',sample,strength,gap,pass:ok&&cheap.Snapshot().locationMask!==8&&gold.Snapshot().locationMask===8});
 }
 Host.strength=4;
 {
  const h=blank(3);h.match.playerOne.hasPassed=true;
  add(h,112405,1,0,1,a);add(h,112405,1,0,2,c);
  const control=add(h,113309,8),smallBody=add(h,112405,8,1,2,1+rnd(2));
  const ok=decision(h);results.push({family:'control-now-after-pass',sample,a,c,pass:ok&&control.Snapshot().locationMask===32&&smallBody.Snapshot().locationMask===8});
 }
 for(const round of [1,3]){
  const h=blank(round);for(let i=0;i<4;i++)add(h,112405,8,i,1,5+rnd(5));
  // This family proves the multi-card reply tax against an announced plain
  // list. An unknown list could contain a one-card reset of the large unit;
  // that different case is covered explicitly by check_tactics091.
  h.aiStartingDeckOne=[112405,112405,112405,112405,112405];
  add(h,112405,1,0,2,60+rnd(20));add(h,112405,1,0,1,8+rnd(5));
  for(let i=0;i<4;i++)add(h,112405,8,i,2,7+rnd(3));
  const ok=decision(h);results.push({family:round===1?'expensive-reply-pass':'decisive-round',sample,pass:ok&&h.match.playerTwo.hasPassed===(round===1)});
 }
 for(const locked of [false,true]){
  const h=blank(3);for(let i=0;i<4;i++)add(h,112101,8,i,1,8+rnd(5));
  const largePower=9+rnd(2),engine=add(h,201624,1,0,1),large=add(h,112101,1,1,1,largePower);large.power.basePower=largePower;
  if(locked)engine.AddTokens(4);const removal=add(h,113301,8);for(let i=0;i<3;i++)add(h,112101,8,i+1,2,1+rnd(3));
  const ok=decision(h);results.push({family:locked?'locked-threat':'growing-threat',sample,removal:removal.Snapshot().locationMask,engine:engine.Snapshot().locationMask,large:large.Snapshot().locationMask,pass:ok&&removal.Snapshot().locationMask===32&&(locked?(large.Snapshot().locationMask===32||large.Snapshot().power.currentPower<largePower):engine.Snapshot().locationMask===32)});
 }
 // Exact proof must be disabled when the last card is hidden or the player
 // can still use a leader. No access to its hidden identity is justified.
 for(const unknown of [true,false]){
  const h=blank(3),last=add(h,112405,8,0,1,b);if(!unknown)last.AddTokens(64);
  add(h,112405,1,0,1,a);add(h,112405,1,0,2,c);add(h,113309,8);add(h,112405,8,1,2,d);
  if(!unknown)add(h,131101,64,0,1);
  results.push({family:unknown?'unknown-reply-no-proof':'available-leader-no-proof',sample,a,b,c,d,pass:(unknown||h.LeaderAvailable(1))&&!h.AiPlainLastReply()});
 }
}
globalThis.report={fingerprint,seed,samples,damp,results,failed:results.filter(r=>!r.pass).length,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:600000});
fs.writeFileSync(output,JSON.stringify(ctx.report,null,2));
console.log(JSON.stringify({samples,cases:ctx.report.results.length,damp,failed:ctx.report.failed,examples:ctx.report.results.filter(r=>!r.pass).slice(0,5)}));
process.exitCode=ctx.report.failed?1:0;
