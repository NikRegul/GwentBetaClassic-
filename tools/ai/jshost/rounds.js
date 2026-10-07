// Round economy stats: node rounds.js rules.js games strengthA strengthB
const vm = require('vm'), fs = require('fs'), path = require('path');
const rules = process.argv[2], games = +process.argv[3] || 40, sa = +(process.argv[4] || 1), sb = +(process.argv[5] || 1);
const src = fs.readFileSync(path.join(__dirname, 'runtime.js'), 'utf8') + '\n' + fs.readFileSync(rules, 'utf8') + '\n' + fs.readFileSync(path.join(__dirname, 'harness.js'), 'utf8') + `
var __R=[];const __oB=CBetaGwentDuelSession.prototype.BeginNextRound;
CBetaGwentDuelSession.prototype.BeginNextRound=function(){const m=this.Snapshot();const rev=__reversed(this);
 const h1=this.CountLocation(1,8),h2=this.CountLocation(2,8);const s1=this.Score(1),s2=this.Score(2);
 __R.push({round:m.roundNumber,hand:rev?[h2,h1]:[h1,h2],score:rev?[s2,s1]:[s1,s2]});return __oB.call(this);};
globalThis.__R=__R;`;
const ctx = { console }; vm.createContext(ctx); vm.runInContext(src, ctx);
const h = ctx.__harness; const agg = { r1: { n: 0, winnerCA: 0, bigOver: 0 }, matches: 0 };
let lines = [];
for (let i = 0; i < games; i++) {
  const a = 54 + (i % 40), b = 54 + ((i * 7 + 3) % 40); ctx.__R.length = 0;
  const r = h.play(a, b, 5000 + i, sa, sb); if (r.error) { console.log('ERR', r.error.slice(0, 200)); continue; }
  const R1 = ctx.__R[0]; if (!R1) continue;
  const w = R1.score[0] > R1.score[1] ? 0 : R1.score[1] > R1.score[0] ? 1 : -1;
  if (w >= 0) { agg.r1.n++; const ca = R1.hand[w] - R1.hand[1 - w]; agg.r1.winnerCA += ca; if (ca <= -2) agg.r1.bigOver++; }
  if (i < 12) lines.push(`${a} vs ${b}: R1 score ${R1.score} hands ${R1.hand}` + (ctx.__R[1] ? ` | R2 score ${ctx.__R[1].score} hands ${ctx.__R[1].hand}` : '') + ` winner ${r.winner} crowns ${r.crowns}`);
}
console.log(lines.join('\n')); console.log(JSON.stringify(agg), 'avg CA of R1 winner', (agg.r1.winnerCA / agg.r1.n).toFixed(2));
