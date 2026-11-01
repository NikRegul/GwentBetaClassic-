'use strict';
// Оззрелл (201698) consumes a Bronze/Silver unit from either graveyard and takes over its
// current power. The logged game (profile 23, round 3, ownHand 1, score 17:27) had an
// 11-power Cyclops in the AI's own graveyard and a 4-power Detmold in the enemy's. The AI
// ate the 4-power tutor because the candidate score added the card's own deploy value
// (a tutor is worth far more *played*) plus an unbounded spy-style denial bonus, and lost
// the round by one point. Neither side ever plays the eaten card again.
const fs = require('fs'), path = require('path');
const rt = require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const { add } = require('./audit_fixture095.cjs')(rt);
let checks = 0; const failures = [], cases = [];
const check = (v, s, detail) => { checks++; if (!v) failures.push({ assertion: s, ...(detail ? { detail } : {}) }); };
const snap = c => c.Snapshot(), cid = c => snap(c).instanceId;
function run(title, body) { try { body(); } catch (e) { failures.push({ case: title, fixtureError: e.stack }); } cases.push(title); }
function table() {
  const g = rt.newSession();
  if (!g.InitializeWithPresets(58, 74)) throw new Error('presets 58/74 are required for this position');
  for (const c of g.live) c.Move(c.Snapshot().positionPlayerId, 512, 0);
  g.mulligan = false; g.waiting = false; g.pendingCard = null; g.pendingLeader = null;
  g.recordVisuals = false; g.externalPolicyMask = 0; g.random.Initialize(2204500);
  g.match.currentPlayerId = 2; g.match.roundActive = g.match.turnActive = true; g.match.roundNumber = 3;
  g.match.playerOne.crowns = 1; g.match.playerTwo.crowns = 1;
  g.match.playerOne.hasPassed = g.match.playerTwo.hasPassed = false;
  return g;
}

// The round-deciding position from the log.
run('biggest captured body wins over the enemy tutor', () => {
  const g = table();
  const wall = add(g, 112101, 1, 1, 0, 27);
  const ownA = add(g, 112101, 2, 2, 0, 8), ownB = add(g, 112101, 2, 2, 1, 9);
  const cyclops = add(g, 200037, 2, 32, 0, 11);
  const tutor = add(g, 122207, 1, 32, 0, 4);
  const ozzrel = add(g, 201698, 2, 8, 0);
  check(g.archetypeAI.ProfileId() === 23, 'the logged archetype profile is in use', { profile: g.archetypeAI.ProfileId() });
  check(g.Score(1) === 27 && g.Score(2) === 17, 'the AI trails by ten in the last round', { one: g.Score(1), two: g.Score(2) });
  const small = g.AiAbilityChoiceValue(ozzrel, tutor, 2), big = g.AiAbilityChoiceValue(ozzrel, cyclops, 2);
  check(big > small, 'the eleven point body outscores the four point tutor', { big, small, deployValue: g.AiManagedDeployValue(rt.definition(122207), 2) });
  check(g.Play(2, cid(ozzrel), 2), 'Ozzrel is played as the last card');
  g.FlushEffects(); g.FlushDeaths();
  check(snap(ozzrel).power.currentPower === 16, 'Ozzrel took the eleven points', { power: snap(ozzrel).power.currentPower });
  check(snap(cyclops).locationMask === 512 && snap(tutor).locationMask === 32, 'the Cyclops was banished and the tutor stays in the enemy grave', { cyclops: snap(cyclops).locationMask, tutor: snap(tutor).locationMask });
  check(g.Score(2) > g.Score(1), 'and the round is now won instead of lost by one', { one: g.Score(1), two: g.Score(2) });
  check(!g.IsPending() && !g.IsFatal(), 'request resolved', { pending: !!g.IsPending(), fatal: g.IsFatal() });
  void wall; void ownA; void ownB;
});

// Denial must survive the correction: equal six point Bronze units, only the enemy one is
// an engine. Both are legal Ozzrel victims (Bronze/Silver units), unlike an event card.
run('equal bodies still prefer denying a live enemy engine', () => {
  const g = table();
  add(g, 112101, 1, 1, 0, 20);
  const ownBody = add(g, 132209, 2, 32, 0, 6);
  const enemyEngine = add(g, 132201, 1, 32, 0, 6);
  const ozzrel = add(g, 201698, 2, 8, 0);
  add(g, 112101, 1, 8, 0, 5);
  check(g.AiEngineValue(snap(enemyEngine), 2) >= 2, 'the enemy unit really counts as an engine', { engine: g.AiEngineValue(snap(enemyEngine), 2) });
  const ownValue = g.AiAbilityChoiceValue(ozzrel, ownBody, 2), enemyValue = g.AiAbilityChoiceValue(ozzrel, enemyEngine, 2);
  check(enemyValue > ownValue, 'while the enemy can still act, eating its engine beats eating an equal own body', { ownValue, enemyValue, ticks: g.AiWeatherTicks(2) });
  check(g.Play(2, cid(ozzrel), 2), 'Ozzrel played'); g.FlushEffects(); g.FlushDeaths();
  check(snap(ozzrel).power.currentPower === 11, 'the enemy engine was consumed and paid its six points', { power: snap(ozzrel).power.currentPower });
  check(snap(enemyEngine).locationMask === 512 && snap(ownBody).locationMask === 32, 'chosen enemy instance banished, own body untouched', { enemy: snap(enemyEngine).locationMask, own: snap(ownBody).locationMask });
});

// The denial bonus must stay bounded: a five point bigger own body is not outbid by it.
run('the denial bonus cannot outbid real points', () => {
  const g = table();
  add(g, 112101, 1, 1, 0, 20);
  const bigOwn = add(g, 200037, 2, 32, 0, 11);
  const enemyEngine = add(g, 132201, 1, 32, 0, 6);
  const ozzrel = add(g, 201698, 2, 8, 0);
  add(g, 112101, 1, 8, 0, 5);
  check(g.AiAbilityChoiceValue(ozzrel, bigOwn, 2) > g.AiAbilityChoiceValue(ozzrel, enemyEngine, 2), 'the eleven point own body still wins against the engine denial',
    { own: g.AiAbilityChoiceValue(ozzrel, bigOwn, 2), enemy: g.AiAbilityChoiceValue(ozzrel, enemyEngine, 2) });
  check(g.Play(2, cid(ozzrel), 2), 'Ozzrel played'); g.FlushEffects(); g.FlushDeaths();
  check(snap(bigOwn).locationMask === 512 && snap(enemyEngine).locationMask === 32, 'the bigger body was taken and the engine stays buried', { own: snap(bigOwn).locationMask, enemy: snap(enemyEngine).locationMask });
});

// A passed enemy closes the round: no future denial value may flip the choice.
run('a passed enemy keeps only the points', () => {
  const g = table();
  g.match.playerOne.hasPassed = true;
  add(g, 112101, 1, 1, 0, 20);
  const bigOwn = add(g, 200037, 2, 32, 0, 11);
  const smallEnemy = add(g, 122207, 1, 32, 0, 4);
  const ozzrel = add(g, 201698, 2, 8, 0);
  check(g.AiWeatherTicks(2) === 0, 'no weather turns are forecast once the enemy passed', { ticks: g.AiWeatherTicks(2) });
  check(g.AiAbilityChoiceValue(ozzrel, bigOwn, 2) > g.AiAbilityChoiceValue(ozzrel, smallEnemy, 2), 'the ten point gap decides it on points alone',
    { own: g.AiAbilityChoiceValue(ozzrel, bigOwn, 2), enemy: g.AiAbilityChoiceValue(ozzrel, smallEnemy, 2) });
  void bigOwn; void smallEnemy;
});

const report = { schema: 1, fingerprint: rt.fingerprint, checks, failures, cases, note: 'Positions rebuilt from log/ozzrel-vmito-ciklopa; only translated common WS executes.' };
if (process.argv[3]) { if (fs.existsSync(process.argv[3])) throw new Error('fresh report required'); fs.writeFileSync(process.argv[3], JSON.stringify(report, null, 2) + '\n'); }
console.log(JSON.stringify({ checks, cases: cases.length, failures: failures.length, firstFailures: failures.slice(0, 6), fingerprint: rt.fingerprint }));
if (failures.length) process.exitCode = 1;
