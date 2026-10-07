// node run.js rules.js mode games seed [strengthLeft strengthRight]
const h = require('./selfplay.js').load(process.argv[2]);
const pool = []; for (let p = 54; p <= 93; p++) pool.push(p);
const games = +process.argv[4] || 80, seed0 = +process.argv[5] || 1;
const sl = +(process.argv[6] ?? 1), sr = +(process.argv[7] ?? 1);
let res = { L: 0, R: 0, D: 0, E: 0 }, errs = {}, perDeck = {}, t0 = Date.now();
let rng = seed0 >>> 0 || 1; const rnd = () => { rng ^= rng << 13; rng >>>= 0; rng ^= rng >>> 17; rng ^= rng << 5; rng >>>= 0; return rng; };
for (let i = 0; i < games; i++) {
  const a = pool[i % 40], b = pool[(i + 1 + (rnd() % 39)) % 40], seed = rnd();
  for (const [x, y, flip] of [[a, b, false], [b, a, true]]) {
    // flip: same deal, strengths swapped seats so each strength plays both decks
    const r = h.play(x, y, seed, flip ? sr : sl, flip ? sl : sr);
    if (r.error) { res.E++; const k = r.error.split('\n')[0]; errs[k] = (errs[k] || 0) + 1; if (errs[k] === 1) { console.error('ERR', x, y, seed, r.error.split('\n').slice(0, 6).join(' | ')); console.error(' trace:', r.trace.slice(-6).join(' || ')); } continue; }
    const strongWon = flip ? r.winner === 2 : r.winner === 1;   // "Left strength" won
    const strongLost = flip ? r.winner === 1 : r.winner === 2;
    if (r.winner === 3) res.D++; else if (strongWon) res.L++; else if (strongLost) res.R++;
  }
}
console.log(JSON.stringify(res), 'games', games * 2, 'sec', ((Date.now() - t0) / 1000).toFixed(1));
console.log(JSON.stringify(errs, null, 1));
