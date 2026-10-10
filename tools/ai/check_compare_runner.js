// Contract checks: all-deck schedule, checkpoint/resume, statistics and tamper rejection.
// A tiny deterministic host keeps these tests independent of card balance.
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process'),assert=require('assert'),zlib=require('zlib');
const root=path.resolve(__dirname,'../../BetaGwent/build/comparison-tests');fs.mkdirSync(root,{recursive:true});
const out=fs.mkdtempSync(path.join(root,'runner-'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(p,value)=>{p=path.join(out,p);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof value==='string'?value:JSON.stringify(value));};
const pool=Array.from({length:46},(_,i)=>54+i);
for(const folder of ['candidate','baseline'])for(const file of ['rules.js','runtime.js','harness.js'])write(folder+'/'+file,'// fixture');
for(const folder of ['candidate','baseline'])write(folder+'/tunes.json',{});
write('candidate/sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws','catalogue');
write('candidate/manifest.json',{presets:pool});
write('baseline/comparison.json',{sameDeckCatalogue:sha(path.join(out,'candidate/sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws')),baselineRules:sha(path.join(out,'baseline/rules.js')),sharedBattleMechanics:true,sessionPolicyMethods:['OpponentStep']});
write('profiles.json',{profiles:pool.map(id=>({presetId:id,id,title:'Deck '+id}))});
write('run.json',{cycles:2,seed:422,candidateLabel:'fixture-new',baselineLabel:'fixture-old'});
write('comparison_bridge119.js',`module.exports=String.raw\`
let state,log;
globalThis.bridge={setTunes(){},setLog(callback){log=callback},initialize(a,b,seed){return JSON.stringify({a,b,seed,winner:0,reversed:false})},
 load(s){state=JSON.parse(s)},dump(){return JSON.stringify(state)},mirror(){},initialMulligan(){},swap(){},
 view(){return {...state,actor:1,current:2,mulligan:false,pending:false,waiting:false,fatal:false}},
 step(){state.winner=1;log('fixture decision')}
};\`;`);
for(const name of ['compare_ai.js','replay119.js'])fs.copyFileSync(path.join(__dirname,name),path.join(out,name));
const run=args=>cp.spawnSync(process.execPath,[path.join(out,'compare_ai.js'),out,...args],{encoding:'utf8'});
let result=run(['--max-games','3']);assert.strictEqual(result.status,0,result.stderr);
const first=sha(path.join(out,'matches/game-000001.json.gz'));
result=run(['--resume','--max-games','5']);assert.strictEqual(result.status,0,result.stderr);
let report=JSON.parse(fs.readFileSync(path.join(out,'report.json')));assert.strictEqual(report.completedGames,8);
result=run(['--resume']);assert.strictEqual(result.status,0,result.stderr);
report=JSON.parse(fs.readFileSync(path.join(out,'report.json')));
assert.strictEqual(report.completedGames,368);assert.strictEqual(report.wins,184);assert.strictEqual(report.losses,184);
assert.strictEqual(report.errors,0);assert.strictEqual(report.mean,.5);assert.strictEqual(report.confirmedBetter,false);
assert.strictEqual(report.blocks.length,92);assert.strictEqual(Object.keys(report.perDeck).length,46);
assert.strictEqual(new Set(report.games.map(g=>g.id)).size,368);
assert.strictEqual(sha(path.join(out,'matches/game-000001.json.gz')),first);
for(const deck of Object.values(report.perDeck)){assert.strictEqual(deck.wins,4);assert.strictEqual(deck.losses,4);assert.strictEqual(deck.scoreRate,.5);}
for(let i=0;i<368;i+=4){const initials=report.games.slice(i,i+4).map(g=>JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(out,'matches',g.id+'.json.gz')))).initial);assert.strictEqual(new Set(initials).size,1);}
assert.strictEqual(fs.readFileSync(path.join(out,'archetypes.csv'),'utf8').split('\r\n').length,47);
const before=sha(path.join(out,'report.json'));
fs.writeFileSync(path.join(out,'candidate/tunes.json'),'{"1":999}');result=run(['--resume']);
assert.notStrictEqual(result.status,0);assert.match(result.stderr,/changed; resume refused/);
assert.strictEqual(sha(path.join(out,'report.json')),before);
console.log('PASS: 368 scheduled games; resume inside a block; 46 deck rows; shared deals; frozen matches; tamper rejection. Fixture: '+out);
