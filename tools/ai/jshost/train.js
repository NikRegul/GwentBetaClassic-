// Self-play tuning of the WS battle AI (BetaGwentAITune) with full logs.
// node train.js --rules build/rules.js --out <dir> [--generations 20] [--pairs 120] [--shards N] [--strength 4] [--resume]
// Each generation mutates the current best tune vector, plays candidate vs best on
// every one of the 40 archetypes (both seats, same deals) and keeps the candidate only
// when it wins clearly. Everything is written to <dir>: generation logs, best.json, summary.csv.
const fs = require('fs'), path = require('path'), os = require('os');
const { fork } = require('child_process');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const has = (k) => process.argv.includes('--' + k);
// Tunable parameters: index -> [min, max, step]. Defaults live in duelAIPass.ws.
const SPACE = { 0: [0, 14, 2], 1: [0, 12, 4], 2: [0, 1, 1], 3: [0, 1, 1], 4: [0, 1, 1], 6: [1, 6, 1], 7: [3, 9, 1], 8: [0, 10, 1], 9: [2, 6, 1] };
const DEFAULTS = { 0: 6, 1: 0, 2: 0, 3: 0, 4: 1, 6: 3, 7: 6, 8: 5, 9: 4 };

if (process.argv[2] === '--child') {
  const [, , , rules, from, to, strength, seed, ta, tb] = process.argv;
  const h = require('./selfplay.js').load(rules);
  const A = JSON.parse(ta), B = JSON.parse(tb);
  const out = { A: 0, B: 0, D: 0, E: 0, errors: [], perDeck: {}, crowns: 0 };
  for (let i = +from; i < +to; i++) {
    const a = 54 + (i % 40), b = 54 + ((i * 17 + 1 + Math.floor(i / 40) + +seed) % 40), deal = (+seed * 7919 + i * 104729) >>> 0;
    if (a === b) continue;
    for (const swap of [false, true]) {
      h.Host.tunes = swap ? [B, A] : [A, B];
      const r = swap ? h.play(b, a, deal, +strength, +strength) : h.play(a, b, deal, +strength, +strength);
      if (r.error) { out.E++; if (out.errors.length < 5) out.errors.push({ a, b, deal, error: r.error.split('\n').slice(0, 4).join(' | ') }); continue; }
      const aWon = swap ? r.winner === 2 : r.winner === 1, bWon = swap ? r.winner === 1 : r.winner === 2;
      const d = out.perDeck[a] = out.perDeck[a] || [0, 0];
      if (aWon) { out.A++; d[0]++; } else if (bWon) { out.B++; d[1]++; } else out.D++;
    }
  }
  process.send(out); process.exit(0);
}

function match(rules, pairs, shards, strength, seed, A, B) {
  return new Promise((resolve) => {
    const total = { A: 0, B: 0, D: 0, E: 0, errors: [], perDeck: {} }; let done = 0;
    for (let s = 0; s < shards; s++) {
      const from = Math.floor(pairs * s / shards), to = Math.floor(pairs * (s + 1) / shards);
      const c = fork(__filename, ['--child', rules, from, to, strength, seed, JSON.stringify(A), JSON.stringify(B)]);
      c.on('message', (o) => {
        for (const k of ['A', 'B', 'D', 'E']) total[k] += o[k]; total.errors.push(...o.errors);
        for (const [d, v] of Object.entries(o.perDeck)) { const t = total.perDeck[d] = total.perDeck[d] || [0, 0]; t[0] += v[0]; t[1] += v[1]; }
        if (++done === shards) resolve(total);
      });
    }
  });
}

function mutate(best, rng) {
  const c = { ...best }; const keys = Object.keys(SPACE); const n = 1 + Math.floor(rng() * 2);
  for (let k = 0; k < n; k++) {
    const i = keys[Math.floor(rng() * keys.length)]; const [lo, hi, step] = SPACE[i];
    const dir = rng() < 0.5 ? -1 : 1; c[i] = Math.max(lo, Math.min(hi, (c[i] ?? DEFAULTS[i]) + dir * step));
  }
  return c;
}

(async () => {
  const rules = arg('rules', 'build/rules.js'), out = arg('out', 'BetaGwent/training/js-' + new Date().toISOString().slice(0, 10));
  const generations = +arg('generations', 20), pairs = +arg('pairs', 200), strength = +arg('strength', 4);
  const shards = +arg('shards', Math.max(1, os.cpus().length - 1));
  fs.mkdirSync(out, { recursive: true });
  const stateFile = path.join(out, 'best.json');
  let state = has('resume') && fs.existsSync(stateFile) ? JSON.parse(fs.readFileSync(stateFile, 'utf8')) : { generation: 0, best: { ...DEFAULTS }, history: [] };
  let seed = 1000 + state.generation * 31; let rs = (seed * 2654435761) >>> 0;
  const rng = () => { rs ^= rs << 13; rs >>>= 0; rs ^= rs >>> 17; rs ^= rs << 5; rs >>>= 0; return rs / 4294967296; };
  const csv = path.join(out, 'summary.csv');
  if (!fs.existsSync(csv)) fs.writeFileSync(csv, 'generation,candidate,wins,losses,draws,errors,winrate,accepted,seconds\n');
  console.log(`training: ${generations} generations x ${pairs * 2} games, ${shards} processes, strength ${strength}, output ${out}`);
  const first = state.generation, last = first + generations;
  for (let g = first; g < last; g++) {
    const cand = mutate(state.best, rng); const t0 = Date.now();
    const r = await match(rules, pairs, shards, strength, 5000 + g * 97, cand, state.best);
    const n = r.A + r.B, p = r.A / Math.max(1, n), se = Math.sqrt(p * (1 - p) / Math.max(1, n));
    const accepted = r.E === 0 && p - 1.5 * se > 0.5;   // clearly better than the current best
    const entry = { generation: g, candidate: cand, best: state.best, result: { wins: r.A, losses: r.B, draws: r.D, errors: r.E, winrate: +p.toFixed(4) }, accepted, perDeck: r.perDeck, errors: r.errors, seconds: Math.round((Date.now() - t0) / 1000) };
    fs.writeFileSync(path.join(out, `gen-${String(g).padStart(4, '0')}.json`), JSON.stringify(entry, null, 1));
    fs.appendFileSync(csv, `${g},"${JSON.stringify(cand).replace(/"/g, "'")}",${r.A},${r.B},${r.D},${r.E},${p.toFixed(4)},${accepted},${entry.seconds}\n`);
    console.log(`gen ${g}: ${JSON.stringify(cand)} -> ${(100 * p).toFixed(1)}% (${r.A}:${r.B}, err ${r.E}) ${accepted ? 'ACCEPTED' : 'rejected'} ${entry.seconds}s`);
    if (accepted) state.best = cand;
    state.history.push({ generation: g, winrate: p, accepted }); state.generation = g + 1;
    fs.writeFileSync(stateFile, JSON.stringify(state, null, 1));
  }
  console.log('best tunes:', JSON.stringify(state.best), '->', stateFile);
})();
