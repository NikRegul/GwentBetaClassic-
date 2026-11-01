'use strict';
// Мороз and Туман hit one body per turn, chosen by power order (the cheapest for Frost,
// the strongest for Fog). The AI used to price weather only as a row-versus-row penalty:
// it kept dropping fresh bodies into empty weathered rows, where those bodies then ate
// every hit and scored nothing. These checks pin the body-level risk model and both of
// its consumers (row ranking and the card forecast).
const fs = require('fs'), path = require('path');
const rt = require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const { fixture, add } = require('./audit_fixture095.cjs')(rt);
let checks = 0; const failures = [], cases = [];
const check = (v, s, detail) => { checks++; if (!v) failures.push({ assertion: s, ...(detail ? { detail } : {}) }); };
const snap = c => c.Snapshot();
function run(title, body) { try { body(); } catch (e) { failures.push({ case: title, fixtureError: e.stack }); } cases.push(title); }
function frost(g, token) { for (const row of [1, 2, 4]) g.weather.ApplyHazard(2, row, token); }

// Frost = token 1 (2 dmg/turn), Fog = token 2 (2), Rain = token 4 (1).
run('risk table', () => {
  const TABLE = [
    [1, [], 3, 0, 2, 3, 'a lone body on Frost eats both hits'],
    [1, [6], 11, 0, 2, 0, 'a cheaper neighbour absorbs Frost'],
    [1, [2], 3, 0, 2, 2, 'the cheaper neighbour dies on the first tick and cannot shelter the second'],
    [1, [3], 3, 0, 2, 3, 'an equal body does not absorb the hit (Frost randomises ties)'],
    [2, [6], 11, 0, 2, 4, 'Fog takes the strongest body, which is this one'],
    [2, [14], 11, 0, 2, 0, 'a stronger neighbour absorbs Fog'],
    [1, [], 11, 0, 2, 4, 'cumulative hits are hazard times turns'],
    [1, [], 3, 0, 5, 3, 'the risk never exceeds what the body is worth'],
    [1, [], 11, 1, 2, 3, 'one armour point is spent once across the two hits'],
    [1, [], 6, 2, 3, 4, 'armour equal to one hit shelters only that first hit'],
    [4, [6], 11, 0, 2, 2, 'random-target weather ignores the power order'],
  ];
  for (const [token, rowPowers, power, armor, ticks, want, why] of TABLE) {
    const g = fixture(2, 112233); frost(g, token);
    rowPowers.forEach((p, i) => add(g, 132209, 2, 1, i, p));
    const got = g.AiHazardBodyRisk(2, 1, power, armor, ticks);
    check(got === want, why, { token, rowPowers, power, armor, ticks, got, want });
  }
});

// Verify against actual weather resolution, rather than restating a forecast formula.
for(const [token,neighbour,power,armor,ticks] of [[1,0,11,1,2],[1,0,6,2,3],[1,2,11,0,3],[2,0,11,1,3],[2,14,11,0,4]]){
 run('forecast against real ticks '+[token,neighbour,power,armor,ticks].join('/'),()=>{
  const g=fixture(2,112233);frost(g,token);
  if(neighbour)add(g,132209,2,1,0,neighbour);
  const expected=g.AiHazardBodyRisk(2,1,power,armor,ticks);
  const body=add(g,132209,2,1,1,power,armor);
  for(let tick=0;tick<ticks;tick++){g.weather.BeforeTurn(2);g.FlushEffects();g.FlushDeaths();}
  const actual=power-snap(body).power.currentPower;
  check(actual===expected,'real ticks consume armour once and stop sheltering after a neighbour dies',{actual,expected,token,neighbour,power,armor,ticks});
 });
}

run('no risk once the round is over', () => {
  const g = fixture(2, 112233); frost(g, 1);
  add(g, 112101, 2, 8, 0, 11); add(g, 112101, 2, 8, 1, 11); add(g, 112101, 2, 8, 2, 11);
  add(g, 112101, 1, 1, 0, 3); add(g, 112101, 1, 8, 0, 6); add(g, 112101, 1, 8, 1, 6);
  const live = Math.floor(g.AiWeatherTicks(2) / 10);
  check(live > 0, 'while the enemy can act the weather still costs points', { live });
  check(g.AiHazardBodyRisk(2, 1, 11, 0, live) > 0, 'the body on a frosted row pays');
  g.match.playerOne.hasPassed = true;
  check(g.AiWeatherTicks(2) === 0, 'a passed enemy ends the tick forecast');
  check(g.AiHazardBodyRisk(2, 1, 11, 0, Math.floor(g.AiWeatherTicks(2) / 10)) === 0, 'the round closing now costs this body nothing');
});

run('row ranking prefers a row that already shelters a cheaper body', () => {
  const g = fixture(2, 112233); frost(g, 1);
  add(g, 132209, 2, 1, 0, 4);                                   // row 1: frost plus a 4-power chaff
  add(g, 132209, 2, 8, 0, 13); add(g, 132209, 2, 8, 1, 13); add(g, 132209, 2, 8, 2, 13);
  add(g, 132209, 1, 8, 0, 6); add(g, 132209, 1, 8, 1, 6);
  const d = rt.definition(132209);
  check(d.header.armor === 0, 'the test body has no armour to mask the hazard', { armor: d.header.armor });
  const chaffed = g.AiRowPlacementCost(2, 1, d), emptyA = g.AiRowPlacementCost(2, 2, d), emptyB = g.AiRowPlacementCost(2, 4, d);
  check(chaffed < emptyA && chaffed < emptyB, 'a 13-power body is placed where a cheaper body already eats the frost', { chaffed, emptyA, emptyB });
  check(g.BestCardRow(2, d) === 1, 'and the chosen row is that chaffed one', { chosen: g.BestCardRow(2, d) });
});

run('card forecast pays for the weather the body will actually eat', () => {
  const weathered = fixture(2, 112233), clean = fixture(2, 112233);
  frost(weathered, 1);
  for (const g of [weathered, clean]) { add(g, 132209, 2, 8, 0, 13); add(g, 132209, 2, 8, 1, 13); add(g, 132209, 2, 8, 2, 13); add(g, 132209, 1, 8, 0, 6); add(g, 132209, 1, 8, 1, 6); }
  const body = weathered.live.find(c => c.TemplateId() === 132209 && c.Snapshot().locationMask === 8 && c.Snapshot().positionPlayerId === 2);
  const twin = clean.live.find(c => c.TemplateId() === 132209 && c.Snapshot().locationMask === 8 && c.Snapshot().positionPlayerId === 2);
  const d = rt.definition(132209), ticks = Math.floor(weathered.AiWeatherTicks(2) / 10), row = weathered.BestCardRow(2, d);
  check(row > 0 && ticks > 0 && weathered.weather.Hazard(2, row) > 0, 'the round stays alive and the chosen row is weathered', { row, ticks });
  const forecast = weathered.AiCardTempo(body, false, 0, 0), cleanForecast = clean.AiCardTempo(twin, false, 0, 0);
  const expectedRisk = Math.min(13, weathered.weather.Hazard(2, row) * ticks);
  check(forecast === cleanForecast - expectedRisk, 'forecast drops by exactly the points the frost will take from this body',
    { forecast, cleanForecast, expectedRisk, ticks, row, hazard: weathered.weather.Hazard(2, row) });
  check(forecast < cleanForecast, 'a body dropped on weather is worth less than its printed points');
  check(weathered.AiCardTempo(body, true, 0, 0) === clean.AiCardTempo(twin, true, 0, 0), 'the immediate tempo of this turn is not punished');
});

const report = { schema: 1, fingerprint: rt.fingerprint, checks, failures, cases };
if (process.argv[3]) { if (fs.existsSync(process.argv[3])) throw new Error('fresh report required'); fs.writeFileSync(process.argv[3], JSON.stringify(report, null, 2) + '\n'); }
console.log(JSON.stringify({ checks, cases: cases.length, failures: failures.length, firstFailures: failures.slice(0, 6), fingerprint: rt.fingerprint }));
if (failures.length) process.exitCode = 1;
