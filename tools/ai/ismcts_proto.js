
// ===== IS-MCTS prototype (determinized flat Monte Carlo at key decisions) =====
// Appended to transpiled rules. Never reads the opponent's real hidden cards:
// hidden cards are placeholders after AiSimClone and are re-sampled from the
// opponent faction's known archetype rosters (public deck knowledge).
var __isNow = (typeof performance !== "undefined" && performance.now) ? () => performance.now() : () => Date.now();
var __IS = globalThis.__IS = {
  enabled: true, samples: 16, maxHand: 5, budgetMs: 8000, rolloutSteps: 160,
  stats: { decisions: 0, searched: 0, ms: 0, overridden: 0, rollouts: 0, rolloutMs: 0, errors: 0 }
};
var __isPools = {};
function __isFactionOf(templateId) { const d = BetaGwentDuelDefinition(templateId); return d.header.factionMask; }
function __isPool(faction) {
  if (__isPools[faction]) return __isPools[faction];
  const weights = new Map();
  for (let id = 1; id <= 99; id++) {
    const p = BetaGwentDuelPreset(id); if (!p || !p.leaderTemplateId) continue;
    if (__isFactionOf(p.leaderTemplateId) !== faction) continue;
    const o = { v: [] }; if (!BetaGwentDuelPresetDeck(id, o)) continue;
    for (const t of o.v) weights.set(t, (weights.get(t) || 0) + 1);
  }
  const ids = [], cum = []; let total = 0;
  for (const [t, w] of weights) { total += w; ids.push(t); cum.push(total); }
  return __isPools[faction] = { ids, cum, total };
}
function __isSample(pool, rnd, used) {
  for (let tries = 0; tries < 20; tries++) {
    const x = rnd() * pool.total; let lo = 0, hi = pool.cum.length - 1;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (pool.cum[mid] > x) hi = mid; else lo = mid + 1; }
    const id = pool.ids[lo], d = BetaGwentDuelDefinition(id);
    const cap = d.header.tierMask === 2 ? 3 : 1;
    if ((used.get(id) || 0) >= cap) continue;
    used.set(id, (used.get(id) || 0) + 1); return id;
  }
  return 0;
}
function __isAssign(card, id) {
  const d = BetaGwentDuelDefinition(id);
  card.definition = d;
  card.cardState.originTemplateId = id;
  card.cardState.runtimeTemplate = __cp(d.header);
  card.cardState.runtimeTierMask = d.header.tierMask;
  card.cardState.tokenMask = 0;
  card.cardState.timerValue = d.initialTimer;
  card.nilfCounter = 0; card.selectedModeId = 0;
  card.cardState.power.basePower = d.header.power;
  card.cardState.power.currentPower = d.header.power;
  card.cardState.power.armor = d.header.armor;
  card.power.initialized = false; card.power.InitFromFields(card.cardState.power);
}
function __isRng(seed) { let s = (seed >>> 0) || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
// Sample identities for the opponent's unknown hand and deck cards.
function __isDeterminize(g, rnd) {
  const leader = g.leaderTemplateOne, faction = leader ? __isFactionOf(leader) : 1;
  const pool = __isPool(faction); if (!pool.ids.length) return;
  const used = new Map();
  for (const c of g.live) { const s = c.Snapshot(); if (s.positionPlayerId === 1 && (s.locationMask & 7) !== 0 && (s.tokenMask & 8) === 0) used.set(s.templateId, (used.get(s.templateId) || 0) + 1); }
  for (const c of g.live) {
    const s = c.Snapshot();
    if (s.positionPlayerId !== 1 || (s.locationMask !== 8 && s.locationMask !== 16)) continue;
    if (c.cardState.originTemplateId !== 112101) continue; // only placeholders
    const id = __isSample(pool, rnd, used); if (id) __isAssign(c, id);
  }
}
function __isOutcome(g) {
  const m = g.Snapshot(); let w = m.matchWinnerMask;
  if (w === 0) return null;
  if (__reversed(g)) w = ((w & 1) << 1) | ((w & 2) >> 1);
  return w === 2 ? 1 : w === 1 ? 0 : 0.5;
}
function __isHeuristicEval(g) {
  // Unfinished rollout: crowns and card advantage dominate, then points.
  const m = g.Snapshot(); const rev = __reversed(g);
  const own = rev ? m.playerOne : m.playerTwo, opp = rev ? m.playerTwo : m.playerOne;
  const ownSide = rev ? 1 : 2, oppSide = rev ? 2 : 1;
  const v = (own.crowns - opp.crowns) * 2 + (g.CountLocation(ownSide, 8) - g.CountLocation(oppSide, 8)) * 0.4 + Math.sign(g.Score(ownSide) - g.Score(oppSide)) * 0.3;
  return 1 / (1 + Math.exp(-v));
}
function __isRollout(g, limit) {
  const t = __isNow();
  try {
    for (let step = 0; step < limit; step++) {
      if (g.IsFatal()) return null;
      const o = __isOutcome(g); if (o !== null) return o;
      if (g.IsMulligan()) return null;
      if (g.IsPending()) { if (!__pending(g)) return null; continue; }
      if (g.IsWaitingRound()) { if (!g.BeginNextRound()) return null; g.recordVisuals = false; continue; }
      if (g.Snapshot().currentPlayerId === 1) __swap(g);
      if (!g.OpponentStep()) return null;
    }
    return __isHeuristicEval(g);
  } catch (e) { __IS.stats.errors++; return null; }
  finally { __IS.stats.rollouts++; __IS.stats.rolloutMs += __isNow() - t; }
}
// Apply one root action to a clone (side 2 acts).
function __isApply(g, action) {
  if (action.kind === 'pass') return g.Pass(2);
  return g.AiSimPlay(action.id) !== -2147483647;
}
function __isActions(g) {
  const out = [];
  for (const c of g.live) {
    const s = c.Snapshot();
    if (s.positionPlayerId !== 2 || !s.canBePlayed) continue;
    if (s.locationMask === 8 || s.locationMask === 64) out.push({ kind: 'card', id: s.instanceId, template: s.templateId, leader: s.locationMask === 64 });
  }
  out.push({ kind: 'pass' });
  return out;
}
function __isKey(g) {
  const m = g.Snapshot();
  const hand = g.CountLocation(2, 8);
  if (hand === 0) return false;
  return hand <= __IS.maxHand || m.playerOne.hasPassed || m.roundNumber >= 3 || m.playerOne.crowns >= 1;
}
const __isOriginalStep = CBetaGwentDuelSession.prototype.OpponentStep;
CBetaGwentDuelSession.prototype.OpponentStep = function () {
  if (this.aiSimulating || !__IS.enabled || !this.CanAct(2)) return __isOriginalStep.apply(this, arguments);
  __IS.stats.decisions++;
  if (!__isKey(this)) return __isOriginalStep.apply(this, arguments);
  const t0 = __isNow();
  const actions = __isActions(this);
  if (actions.length < 2) return __isOriginalStep.apply(this, arguments);
  // What the heuristic would do: run it on a disposable full-information-free clone.
  let heuristic = null;
  { const h = this.AiSimClone(); if (h) {
      h.aiSimulating = false;
      const before = new Map(); for (const c of h.live) { const s = c.Snapshot(); before.set(s.instanceId, s.locationMask); }
      const passedBefore = h.Snapshot().playerTwo.hasPassed;
      const savedLog = Host.log; Host.log = null;
      try { __isOriginalStep.apply(h, []); } catch (e) {} finally { Host.log = savedLog; }
      if (h.Snapshot().playerTwo.hasPassed && !passedBefore) heuristic = 'pass';
      else for (const c of h.live) { const s = c.Snapshot(); const b = before.get(s.instanceId); if ((b === 8 || b === 64) && s.locationMask !== b) { heuristic = s.instanceId; break; } }
  } }
  const totals = actions.map(() => 0), counts = actions.map(() => 0);
  const seedBase = (this.random.InitialSeed() ^ Math.imul(this.random.DrawCount(), 2654435761)) >>> 0;
  for (let k = 0; k < __IS.samples; k++) {
    if (__isNow() - t0 > __IS.budgetMs) break;
    for (let a = 0; a < actions.length; a++) {
      const g = this.AiSimClone(); if (!g) continue;
      const rnd = __isRng(seedBase + k * 7919 + 1);
      __isDeterminize(g, rnd); g.AiSpyForecastDeck(k);
      g.random.Initialize(Max(1, (seedBase + k * 104729) % 2000000000));
      if (!__isApply(g, actions[a])) { totals[a] = -1e9; continue; }
      const r = __isRollout(g, __IS.rolloutSteps);
      if (r === null) continue;
      totals[a] += r; counts[a]++;
    }
  }
  let best = -1, bestMean = -Infinity, heurIndex = -1;
  for (let a = 0; a < actions.length; a++) {
    const key = actions[a].kind === 'pass' ? 'pass' : actions[a].id;
    if (key === heuristic) heurIndex = a;
    if (!counts[a]) continue;
    const mean = totals[a] / counts[a];
    if (mean > bestMean + 1e-9) { bestMean = mean; best = a; }
  }
  __IS.stats.searched++; __IS.stats.ms += __isNow() - t0;
  // Keep the heuristic unless the search finds a clearly better action.
  const margin = 0.08;
  if (best < 0 || best === heurIndex || (heurIndex >= 0 && counts[heurIndex] && bestMean - totals[heurIndex] / counts[heurIndex] < margin))
    return __isOriginalStep.apply(this, arguments);
  __IS.stats.overridden++;
  const act = actions[best];
  if (act.kind === 'pass') return this.AiExplainedPass('ismcts');
  if (act.leader) return this.UseLeader(2);
  const card = this.FindCard(act.id); if (!card) return __isOriginalStep.apply(this, arguments);
  const d = card.Definition(); let row = this.BestCardRow(2, d); if (row === 0) row = 1;
  let anchor = 0; if (d.effect === 23) anchor = this.BestVranAnchor(2); if (anchor === 0) anchor = this.AiPlacementAnchor(d);
  const ok = anchor !== 0 ? this.PlayBefore(2, act.id, anchor) : this.Play(2, act.id, row);
  return ok ? true : __isOriginalStep.apply(this, arguments);
};
