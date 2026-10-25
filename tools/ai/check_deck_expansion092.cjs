'use strict';
// Runtime acceptance of the actual generated catalog, pool and quest lists.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime}=require('./beta_js092/session.cjs');
const {playMatch}=require('./beta_js092/matches.cjs');
const root=path.resolve(__dirname,'../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const rules=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);assert(!fs.existsSync(out),'Fresh output required');fs.mkdirSync(out,{recursive:true});
const presets=read('data/beta924/duel/presets.json').presets,byId=new Map(presets.map(p=>[p.id,p]));
const imported=read('data/beta924/design/beta_deck_import092.json'),npcs=read('data/beta924/design/npc_rewards.json').assignments;
const previous=read('data/beta924/ai/validation093/final092-rosters.json').decks;
const source=read('BetaGwent/drafts/day-iteration-20261023/beta-deck-import-review.json').decks;
const runtime=createRuntime(rules,924040001);let checks=0;
const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;};
const context=vm.createContext({});vm.runInContext(['runtime.js','rules.js'].map(f=>fs.readFileSync(path.join(rules,f),'utf8')).join('\n'),context);
const call=code=>vm.runInContext(code,context);
eq(imported.decks.length,30,'Only approved30');eq(imported.heldAssets.length,15,'Hold15');eq(presets.length,129,'Stable original identities plus30');
const pool=JSON.parse(call('(()=>{let ids={v:[]};BetaGwentAIOrdinaryPresets(ids);return JSON.stringify(ids.v);})()'));
eq(pool.length,76,'46 previous plus30');eq(new Set(pool).size,76,'No duplicate pool slots');
for(const d of previous){const p=byId.get(d.presetId);eq(p.templateIds,d.templateIds,'Retain original46 lists');eq(p.leader,d.leader,'Retain original46 leaders');}
for(let i=0;i<30;i++){
 const expected=imported.decks[i],p=byId.get(100+i),original=source.find(d=>d.asset===expected.asset);
 eq(p.templateIds,original.templateIds,'Exact original order/copies '+p.id);eq(p.leader,original.leader,'Exact original leader');eq(p.title,expected.asset,'Original asset title');
 eq(call('BetaGwentAIArchetypeName('+p.id+')'),expected.asset,'Actual HUD original name');assert(pool.includes(p.id));checks++;
 const validation=runtime.validateDeck(p.templateIds,p.faction,p.leader);eq(validation.valid,true,'Common legal deck '+p.id);
}
for(const name of imported.heldAssets){eq(presets.some(p=>p.originalBetaAsset===name),false,'Held source not activated '+name);}
for(const n of npcs){
 const p=byId.get(n.preset),base=byId.get(n.basePreset);eq(p.npcDeck,n.deckName,'Actual named NPC');eq(p.npcRulesProfile,base.aiRulesProfile,'Use corresponding archetype policy');
 eq(call('BetaGwentAIPresetProfile('+p.id+')'),base.aiRulesProfile,'Executable NPC policy alias');eq(runtime.validateDeck(p.templateIds,p.faction,p.leader).valid,true,'Legal NPC '+n.deckName);
}
// Quest reward/preset contracts remain byte-for-byte identical to the tournament rules.
const frozen=path.join(root,'BetaGwent/build/day092-beta-external-controls-20261024-v11/sources/BetaGwent/development/scripts/game/betagwent/progressionCatalog.ws');
eq(fs.readFileSync(frozen,'utf8').replace(/^\uFEFF/,'').replace(/\r/g,''),fs.readFileSync(path.join(root,'BetaGwent/development/scripts/game/betagwent/progressionCatalog.ws'),'utf8').replace(/^\uFEFF/,'').replace(/\r/g,''),'Unchanged quest/reward mappings');
const targets=[...presets.filter(p=>p.originalBetaAsset),...npcs.map(n=>byId.get(n.preset))];
eq(new Set(targets.map(p=>JSON.stringify([p.leader,[...p.templateIds].sort((a,b)=>a-b)]))).size,targets.length,'Distinct imported and named lists');
const report={scope:'New30 exact Beta rosters and33 thematic NPC variants under current ordinary AI; no Unfair WS mode yet',fingerprint:runtime.fingerprint,checks,ratingPermitted:false,total:targets.length*2,records:[]};
const save=()=>fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');save();
const entry=p=>({key:'092:'+p.id,policy:'092',presetId:p.id,leader:p.leader,faction:p.faction,templateIds:p.templateIds});
for(let i=0;i<targets.length;i++)for(let seat=1;seat<=2;seat++){
 const p=targets[i],opponent=previous[(i*11)%previous.length],q=byId.get(opponent.presetId),seed=924040001+i;
 const r=playMatch({current:rules},entry(seat===1?p:q),entry(seat===1?q:p),seed);
 report.records.push({...r,target:p.id,targetSide:seat});save();console.log(JSON.stringify({completed:report.records.length,total:report.total,target:p.id,seat,status:r.status,ms:r.ms,error:r.error}));
 assert.equal(r.status,'complete',r.error);
}
report.complete=true;save();
