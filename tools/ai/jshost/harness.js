// Appended to the transpiled rules inside one script scope.
const __Seats = new Set(['ownerId','controllerId','ownerPlayerId','positionPlayerId','playerId','targetPlayerId','startingPlayerId','currentPlayerId','roundStarter','visualSide','savedSourceSide','side','targetSide']);
const __Pairs = ['aiRoundHand','player','score','crownDelta','preset','leaderTemplate','nilfInitial','nilfSpell','grave','deck','leader','history','beasts'];
function __flip(n) { return n === 1 ? 2 : n === 2 ? 1 : n; }
function __visit(v, seen) {
  if (v === null || typeof v !== 'object') return v;
  if (v instanceof SBetaGwentDuelDefinition || v instanceof SBetaGwentTemplateHeader) return v;
  if (Array.isArray(v)) { for (let i = 0; i < v.length; i++) v[i] = __visit(v[i], seen); return v; }
  if (seen.has(v)) return v; seen.add(v);
  for (const p of __Pairs) { const a = p + 'One', b = p + 'Two'; if (a in v && b in v) { const t = v[a]; v[a] = v[b]; v[b] = t; } }
  for (const k of Object.keys(v)) {
    // Clone stamps/references are bookkeeping, not part of a player seat. Do
    // not walk into previous disposable simulations when swapping a real turn.
    if (k === 'bgCloneRef' || k === 'bgCloneEpoch' || k === 'aiSimCloner') continue;
    const old = v[k];
    if (typeof old === 'number' && __Seats.has(k)) v[k] = __flip(old);
    else if (k === 'winnerMask' || k === 'matchWinnerMask') v[k] = ((old & 1) << 1) | ((old & 2) >> 1);
    else v[k] = __visit(old, seen);
  }
  if (v instanceof CBetaGwentDuelWeather) {
    for (let i = 0; i < 3; i++) { const a = v.hazards[i]; v.hazards[i] = v.hazards[i + 3]; v.hazards[i + 3] = a; }
    for (let i = 0; i < v.dreamRows.length; i++) v.dreamRows[i] = (v.dreamRows[i] + 3) % 6;
  }
  return v;
}
const __mem = new WeakMap();
function __swap(g) {
  const m = __mem.get(g) || { rev: false, slots: [[0,0,0,0,0,0],[0,0,0,0,0,0]] }; __mem.set(g, m);
  let actor = m.rev ? 0 : 1;
  m.slots[actor] = [g.aiChaseRound, g.aiChaseInitialHand, g.aiObservedRound, g.aiObservedEnemyScore, g.aiPublicTempo, g.aiChaseSpent];
  __visit(g, new Set()); m.rev = !m.rev; actor = m.rev ? 0 : 1;
  const s = m.slots[actor]; g.aiChaseRound = s[0]; g.aiChaseInitialHand = s[1]; g.aiObservedRound = s[2]; g.aiObservedEnemyScore = s[3]; g.aiPublicTempo = Math.max(14, s[4]); g.aiChaseSpent = s[5];
  g.weatherAI.Initialize(g); g.weatherProfile = g.weatherAI.Matches(g.nilfInitialTwo);
  g.archetypeAI.Initialize(g, g.nilfInitialTwo, g.presetTwo, g.leaderTemplateTwo);
  __context(g);
}
function __reversed(g) { const m = __mem.get(g); return !!(m && m.rev); }
function __context(g) {
  Host.seatIndex = __reversed(g) ? 0 : 1;
  Host.strength = Host.matchStrength[Host.seatIndex];
}
function __mulligan(g) { __swap(g); g.AiMulligan(g.mulliganBudget); __swap(g); g.RefreshMulligan(); g.FinishMulligan(g.requestId); }
function __pending(g) {
  if (!g.IsPending()) return true;
  if (g.mulligan) { __mulligan(g); return !g.fatal; }
  if (g.NilfDecisionSide() === 1) __swap(g);
  if (g.pendingLeader) { const c = g.pendingLeader; g.pendingLeader = null; return g.PlaceLeader(c, 2, g.BestCardRow(2, c.Definition()), -3); }
  if (g.pendingRally) { const r = g.BestNestedRow(g.pendingRally); if (r === 0) return false; g.PlaceRally(2, r, -3); return !g.fatal; }
  if (!g.pendingCard) return false;
  const d = g.pendingCard.Definition();
  if (g.pendingCard.IsMonsterAbility()) {
    const k = g.pendingChoice ? 1 : g.pendingPileChoice ? 2 : g.pendingRow ? 3 : 0;
    g.MonsterRequest(g.pendingCard, g.pendingIds, k, g.monsterMinimum, g.monsterMaximum); return !g.fatal;
  }
  if (g.pendingChoice) {
    if (g.IsModeChoice()) g.ResolveModeChoice(g.BestModeChoice(d, 2));
    else if (g.IsDagonChoice()) g.ResolveDagonChoice(g.ChooseDagonWeather(2));
    else if (g.IsFirstLightChoice()) g.ResolveFirstLight(g.ChooseFirstLight(2));
    else return false;
  } else if (g.pendingPileChoice) {
    let best = 0, score = -Infinity;
    for (let i = 0; i < g.pendingIds.length; i++) { const c = g.FindCard(g.pendingIds[i]); if (!c) continue; const v = g.AiAbilityChoiceValue(g.pendingCard, c, 2); if (v > score) { best = g.pendingIds[i]; score = v; } }
    if (best === 0) return false; g.SelectPileCard(best);
  } else if (g.pendingRow) {
    if (d.effect === 28) { const s = { v: 0 }, r = { v: 0 }; g.specials.BestRow(d, 2, s, r); g.ApplyRowTarget(s.v, r.v); }
    else if (d.weatherToken !== 0) g.ApplyRowTarget(1, g.BestWeatherRow(2, d.weatherToken));
    else g.ApplyRowTarget(1, g.BestEnemyRow(2));
  } else g.ApplyCardTarget(g.BestTarget(2, d.effect, d.amount));
  return !g.fatal;
}
function __play(left, right, seed, strengthLeft, strengthRight, traceLimit) {
  Host.matchStrength = [strengthLeft, strengthRight];
  Host.seatIndex = 1; Host.strength = strengthRight; __simDepthHost = 0;
  let state = (seed >>> 0) || 1;
  Host.random = () => { state ^= state << 13; state >>>= 0; state ^= state >>> 17; state ^= state << 5; state >>>= 0; return state / 4294967296; };
  const trace = []; Host.log = (s) => { trace.push(s); if (trace.length > (traceLimit || 80)) trace.shift(); };
  const g = new CBetaGwentDuelSession(); let steps = 0;
  const seatStrength = () => __reversed(g) ? strengthLeft : strengthRight; // AI acts as side 2
  try {
    if (!g.InitializeWithPresets(left, right)) throw new Error('Invalid preset');
    g.recordVisuals = false; g.aiSimDamp = Host.simDamp === undefined ? 40 : Host.simDamp;
    for (; steps < 500; steps++) {
      if (g.IsFatal()) throw new Error(g.GetMessage());
      const m = g.Snapshot();
      if (m.matchWinnerMask !== 0) {
        let w = m.matchWinnerMask; if (__reversed(g)) w = ((w & 1) << 1) | ((w & 2) >> 1);
        const sc = [m.playerOne.crowns, m.playerTwo.crowns]; if (__reversed(g)) sc.reverse();
        return { left, right, seed, winner: w, steps, crowns: sc };
      }
      Host.strength = seatStrength(); Host.seatIndex = __reversed(g) ? 0 : 1;
      if (g.IsMulligan()) { __mulligan(g); continue; }
      if (g.IsPending()) { Host.strength = seatStrength(); Host.seatIndex = __reversed(g) ? 0 : 1; if (!__pending(g)) throw new Error('Unresolved choice: ' + g.GetMessage()); continue; }
      if (g.IsWaitingRound()) { if (!g.BeginNextRound()) throw new Error('Round transition failed'); g.recordVisuals = false; continue; }
      if (m.currentPlayerId === 1) __swap(g);
      Host.strength = seatStrength(); Host.seatIndex = __reversed(g) ? 0 : 1;
      if (!g.OpponentStep()) throw new Error('Decision rejected: ' + g.GetMessage());
    }
    throw new Error('Decision limit exceeded');
  } catch (e) { return { left, right, seed, winner: 0, steps, error: String(e && e.stack || e), trace }; }
  finally { Host.log = null; }
}
var __harness = { play: __play, Host };
globalThis.__harness = __harness;
