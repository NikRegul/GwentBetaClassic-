// A/B: node ab.js rules.js pairs strengthA strengthB [shards] [seed]
// Every pairing is played twice with the same deal and seats swapped.
const { fork } = require('child_process');
if (process.argv[2] === '--child') {
  const [, , , rules, from, to, sa, sb, seed0] = process.argv;
  const h = require('./selfplay.js').load(rules);
  const out = { A: 0, B: 0, D: 0, E: 0, errors: [], perDeck: {} };
  for (let i = +from; i < +to; i++) {
    const a = 54 + (i % 40), b = 54 + ((i * 17 + 1 + Math.floor(i / 40)) % 40), seed = (+seed0 * 7919 + i * 104729) >>> 0;
    if (a === b) continue;
    for (const mode of [0,1,2,3]) {
      const swap=!!(mode&1), flipped=!!(mode&2), candidateLeft=swap===flipped;
      const L = swap ? b : a, R = swap ? a : b;            // A always drives deck `a`
      const TA = JSON.parse(process.env.TUNE_A || '{}'), TB = JSON.parse(process.env.TUNE_B || '{}');
      h.Host.tunes = candidateLeft ? [TA, TB] : [TB, TA];
      const r = candidateLeft ? h.play(L,R,seed,+sa,+sb) : h.play(L,R,seed,+sb,+sa);
      if (r.error) { out.E++; if (out.errors.length < 5) out.errors.push([L, R, seed, r.error.split('\n').slice(0, 4).join(' | '), (r.trace || []).slice(-5).join(' || ')]); continue; }
      const aWon = r.winner === (candidateLeft?1:2), bWon = r.winner === (candidateLeft?2:1);
      const deck = candidateLeft?L:R; out.perDeck[deck] = out.perDeck[deck] || [0, 0];
      if (aWon) { out.A++; out.perDeck[deck][0]++; } else if (bWon) { out.B++; out.perDeck[deck][1]++; } else out.D++;
    }
  }
  process.send(out); process.exit(0);
} else {
  const rules = process.argv[2], pairs = +process.argv[3] || 200, sa = process.argv[4] || '2', sb = process.argv[5] || '1';
  const shards = +process.argv[6] || 2, seed = process.argv[7] || '1'; const t0 = Date.now();
  let done = 0; const total = { A: 0, B: 0, D: 0, E: 0, errors: [], perDeck: {} };
  for (let s = 0; s < shards; s++) {
    const from = Math.floor(pairs * s / shards), to = Math.floor(pairs * (s + 1) / shards);
    const c = fork(__filename, ['--child', rules, from, to, sa, sb, seed]);
    c.on('message', (o) => {
      for (const k of ['A', 'B', 'D', 'E']) total[k] += o[k]; total.errors.push(...o.errors);
      for (const [d, v] of Object.entries(o.perDeck)) { total.perDeck[d] = total.perDeck[d] || [0, 0]; total.perDeck[d][0] += v[0]; total.perDeck[d][1] += v[1]; }
      if (++done === shards) {
        const n = total.A + total.B; const p = total.A / Math.max(1, n);
        const se = Math.sqrt(p * (1 - p) / Math.max(1, n));
        console.log(`A(strength ${sa}) ${total.A} : B(strength ${sb}) ${total.B}  draws ${total.D} errors ${total.E}  winrate ${(100 * p).toFixed(1)}% ±${(196 * se).toFixed(1)}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
        for (const e of total.errors) console.log('ERR', JSON.stringify(e).slice(0, 600));
        if (process.env.PERDECK) console.log(JSON.stringify(total.perDeck));
      }
    });
  }
}
