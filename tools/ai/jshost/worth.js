// Card worth table from self-play: immediate swing + own later growth until round end.
// node worth.js rules.js games strength out.json [shard] [shards]
const vm = require('vm'), fs = require('fs'), path = require('path');
const [rules, games, strength, out, shard, shards] = process.argv.slice(2);
const src = fs.readFileSync(path.join(__dirname, 'runtime.js'), 'utf8') + '\n' + fs.readFileSync(rules, 'utf8') + '\n' + fs.readFileSync(path.join(__dirname, 'harness.js'), 'utf8') + `
var __W={};var __track=[];
function __rec(g,card,fn){if(g.aiSimulating)return fn();const s0=card.Snapshot();const d=card.Definition();const side2=true;
 const before=g.Score(2)-g.Score(1);const r=fn();if(!r)return r;const after=g.Score(2)-g.Score(1);
 const s1=card.Snapshot();const t=d.header.templateId;const w=__W[t]=__W[t]||{n:0,imm:0,grow:0,growN:0};w.n++;w.imm+=after-before;
 if((s1.locationMask&7)!==0&&!__reversedX(g))__track.push({g,card,p:s1.power.currentPower,t,rev:__reversed(g)});
 else if((s1.locationMask&7)!==0)__track.push({g,card,p:s1.power.currentPower,t,rev:__reversed(g)});
 return r;}
function __reversedX(g){return false;}
function __flush(g){for(const x of __track){if(x.g!==g)continue;const s=x.card.Snapshot();const w=__W[x.t];w.growN++;
  if((s.locationMask&7)!==0)w.grow+=s.power.currentPower-x.p;else w.grow+=-x.p;}
 __track=__track.filter(x=>x.g!==g);}
const __P=CBetaGwentDuelSession.prototype;const __oPlay=__P.Play,__oBefore=__P.PlayBefore,__oLeader=__P.UseLeader,__oNext=__P.BeginNextRound;
__P.Play=function(side,id,row){if(side!==2)return __oPlay.call(this,side,id,row);return __rec(this,this.FindCard(id),()=>__oPlay.call(this,side,id,row));};
__P.PlayBefore=function(side,id,a){if(side!==2)return __oBefore.call(this,side,id,a);return __rec(this,this.FindCard(id),()=>__oBefore.call(this,side,id,a));};
__P.UseLeader=function(side){if(side!==2)return __oLeader.call(this,side);return __rec(this,this.Leader(2),()=>__oLeader.call(this,side));};
__P.BeginNextRound=function(){__flush(this);return __oNext.call(this);};
globalThis.__W=__W;globalThis.__flush=__flush;`;
const ctx = { console }; vm.createContext(ctx); vm.runInContext(src, ctx);
const h = ctx.__harness; const N = +games, sh = +(shard || 0), shs = +(shards || 1);
for (let i = sh; i < N; i += shs) {
  const a = 54 + (i % 40), b = 54 + ((i * 13 + 5 + Math.floor(i / 40)) % 40);
  const r = h.play(a, b, 31337 + i * 7, +strength, +strength);
}
fs.writeFileSync(out, JSON.stringify(ctx.__W));
