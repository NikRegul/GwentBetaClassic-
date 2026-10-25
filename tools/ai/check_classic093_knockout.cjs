/* Contract test for adaptive bracket persistence, explicit ties and errors. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'BetaGwent/build/classic093-knockout-contracts-20261024');
assert(!fs.existsSync(base),'Fresh contracts directory required');fs.mkdirSync(base,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');let checks=0;
function fixture(name,error=false){
 const out=path.join(base,name),frozen=path.join(out,'frozen/tools/ai');fs.mkdirSync(path.join(frozen,'beta_js092'),{recursive:true});
 const files={};for(const name of ['run_classic093_knockout.cjs','profile_trial_io093.cjs']){const dest=path.join(frozen,name);fs.copyFileSync(path.join(__dirname,name),dest);files['tools/ai/'+name]=sha(dest);}
 const fake=path.join(frozen,'beta_js092/matches.cjs');fs.writeFileSync(fake,error?`exports.playMatch=()=>({status:'technical-error',error:'injected-error'});`:`exports.playMatch=(config,left,right,seed)=>({status:'complete',left:left.key,right:right.key,seed,winner:3,ms:1,finalStateSha256:'fixture'});`);files['tools/ai/beta_js092/matches.cjs']=sha(fake);
 const entrants=['hard:1','hard:2','hard:3','classic:1','classic:2','classic:3'].map(key=>({key,title:key,group:key.split(':')[0]}));fs.writeFileSync(path.join(out,'entrants.json'),JSON.stringify(entrants));fs.writeFileSync(path.join(out,'profile-mapping.json'),'{}');fs.mkdirSync(path.join(out,'rules'));fs.writeFileSync(path.join(out,'rules/manifest.json'),'{}');
 const p={current:path.join(out,'rules'),commonManifestSha256:sha(path.join(out,'rules/manifest.json')),codeFiles:files,rosterSha256:sha(path.join(out,'entrants.json')),mappingSha256:sha(path.join(out,'profile-mapping.json')),workers:2,grids:2,masterSeed:123456,minimumGames:20,maximumGames:40,format:{basePairs:1,maxExtraPairs:1},brackets:[['hard:1','classic:1','hard:2',null,'classic:2',null,'hard:3','classic:3'],['classic:3','hard:1','hard:2',null,'classic:2',null,'hard:3','classic:1']]};
 fs.writeFileSync(path.join(out,'plan.json'),JSON.stringify(p));return out;
}
function run(out,args=[]){return cp.spawnSync(process.execPath,[path.join(out,'frozen/tools/ai/run_classic093_knockout.cjs'),out,...args],{encoding:'utf8'});}
const out=fixture('complete-and-resume'),first=run(out);assert.equal(first.status,0,first.stderr);checks++;
const report=JSON.parse(fs.readFileSync(path.join(out,'report.json')));assert.equal(report.games,40);assert.equal(report.series,10);assert.equal(report.seededDrawSeries.length,10);assert.equal(report.champions.reduce((n,c)=>n+c.wins,0),2);checks+=4;
const inputs={};for(const dir of ['games','series'])for(const f of fs.readdirSync(path.join(out,dir)))inputs[path.join(dir,f)]=sha(path.join(out,dir,f));
const resumed=run(out,['--resume']);assert.equal(resumed.status,0,resumed.stderr);checks++;
for(const [f,h]of Object.entries(inputs)){assert.equal(sha(path.join(out,f)),h);checks++;}
const occupied=path.join(out,'exclusive.lock');fs.writeFileSync(occupied,'{"pid":123}');const saved=sha(path.join(out,'progress.json')),duplicate=run(out,['--resume']);assert.notEqual(duplicate.status,0);assert.equal(sha(path.join(out,'progress.json')),saved);assert.equal(JSON.parse(fs.readFileSync(occupied)).pid,123);checks+=3;
const bad=fixture('technical-error',true),failed=run(bad);assert.notEqual(failed.status,0);assert(!fs.existsSync(path.join(bad,'report.json')));assert.equal(fs.readdirSync(path.join(bad,'games')).length,0);assert.equal(fs.readdirSync(path.join(bad,'series')).length,0);assert.equal(JSON.parse(fs.readFileSync(path.join(bad,'progress.json'))).status,'failed');checks+=5;
fs.writeFileSync(path.join(base,'report.json'),JSON.stringify({checks,scope:'Synthetic bracket orchestration only; no AI strength evidence',byesPreserved:true,seededTiesSeparateFromGameWins:true,resumePreservesAllGameAndSeriesHashes:true,activeLockRejectsDuplicateWithoutWritingProgress:true,technicalErrorsNeverBecomeLosses:true},null,2)+'\n');console.log(JSON.stringify({checks,passed:true}));
