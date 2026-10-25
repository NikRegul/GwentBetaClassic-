'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),build=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
const grids=Number(process.argv[4]||16),workers=Number(process.argv[5]||4),finalize=process.argv.includes('--finalize-plan');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(!Number.isInteger(grids)||grids<1||grids>64||!Number.isInteger(workers)||workers<1||workers>4)throw Error('Invalid grid/worker count');
if(fs.existsSync(path.join(out,'plan.json')))throw Error('Tournament plan already frozen');
if(finalize){
 const base=read(path.join(out,'preflight-config.json')),benchmark=read(path.join(out,'benchmark.json'));
 if(benchmark.sourceConfigSha256!==sha(path.join(out,'preflight-config.json')))throw Error('Benchmark settings changed');
 if(!benchmark.complete||benchmark.records.length!==8||benchmark.records.some(r=>r.result.status!=='complete'))throw Error('Complete benchmark required');
 if(base.grids!==grids||base.workers!==workers)throw Error('Prepared settings changed');
 for(const [name,digest]of Object.entries(base.codeFiles))if(sha(path.join(out,'frozen',name))!==digest)throw Error('Prepared code changed '+name);
 if(sha(path.join(out,'entrants.json'))!==base.rosterSha256||sha(path.join(base.current,'manifest.json'))!==base.commonManifestSha256)throw Error('Prepared data changed');
 const entrants=read(path.join(out,'entrants.json')),rosters=[];
 function random(seed){let counter=0;return n=>{const ceiling=Math.floor(4294967296/n)*n;for(;;){const x=crypto.createHash('sha256').update(seed+':'+counter++).digest().readUInt32LE(0);if(x<ceiling)return x%n;}};}
 function shuffle(a,next){for(let i=a.length-1;i>0;i--){const j=next(i+1);[a[i],a[j]]=[a[j],a[i]];}return a;}
 for(let g=0;g<grids;g++){
  const next=random(base.masterSeed+':bracket:'+g),players=shuffle(entrants.map(e=>e.key),next),pairs=[];
  for(let i=0;i<112;i+=2)pairs.push([players[i],players[i+1]]);
  for(const key of players.slice(112))pairs.push([key,null]);
  const slots=shuffle(pairs,next).flat();if(slots.length!==256||slots.filter(Boolean).length!==184||new Set(slots.filter(Boolean)).size!==184)throw Error('Invalid bracket');rosters.push(slots);
 }
 const series=grids*(entrants.length-1),plan={...base,kind:'classic093-seeded-knockout',format:{basePairs:4,maxExtraPairs:4,drawPoints:.5,tiedSeriesAfterAllPairs:'seeded-draw-separately-reported',bracketSlots:256,byesPerBracket:72},
  brackets:rosters,series,minimumGames:series*8,maximumGames:series*16,benchmarkSha256:sha(path.join(out,'benchmark.json')),estimatedHours:[series*8,series*16].map(n=>n*benchmark.elapsedMs/benchmark.records.length/3600000),
  information:'Classic may inspect actual hand/deck; Hard retains existing information restrictions. Technical errors stop the run and never become losses.',
  scheduleRule:'Freeze participants, random bracket slots, series lengths, seed function and tie rule before play; future opponents follow recorded winners. No mid-run format or volume changes.'};
 fs.writeFileSync(path.join(out,'plan.json'),JSON.stringify(plan,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({grids,entrants:entrants.length,series,minimumGames:plan.minimumGames,maximumGames:plan.maximumGames,estimatedHours:plan.estimatedHours,planSha256:sha(path.join(out,'plan.json'))}));process.exit(0);
}
if(fs.existsSync(path.join(out,'preflight-config.json')))throw Error('Already prepared');
const release=read(path.join(build,'release.json')),verification=read(path.join(build,'archive-verification.json'));
if(release.version!=='0.9.3'||verification.version!=='0.9.3'||!verification.classicCompilerPassed||!verification.nextgenCompilerPassed)throw Error('Verified final093 build required');
for(const archive of release.archives)if(sha(archive.path)!==archive.sha256)throw Error('Release archive changed');
const rules=path.join(build,'rules'),manifest=read(path.join(rules,'manifest.json')),mappingPath=path.join(build,'unfair-checks/profile-mapping.json'),mapping=read(mappingPath);
if(!mapping.validated||sha(mappingPath)!==release.originalBetaAI.mappingSha256)throw Error('Shipping mapping changed');
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const extract=new Function('ids',source+`return ids.map(id=>{const p=BetaGwentDuelPreset(id),cards={v:[]};if(!BetaGwentDuelPresetDeck(id,cards))throw Error('Deck');const faction=BetaGwentDuelDefinition(p.leaderTemplateId).header.factionMask,v=BetaGwentValidateDeck(cards.v,faction,p.leaderTemplateId);if(!v.valid)throw Error(id+': '+v.message);return {presetId:id,basePreset:id,title:p.title,leader:p.leaderTemplateId,faction,templateIds:cards.v,hardProfile:BetaGwentAIPresetProfile(id)};});`);
const groups=new Map();
for(const d of extract(Array.from({length:109},(_,i)=>21+i))){
 const k=d.leader+':'+d.templateIds.slice().sort((a,b)=>a-b).join(',');if(!groups.has(k))groups.set(k,[]);groups.get(k).push(d);
}
if(groups.size!==92)throw Error('Expected92 unique compositions');
const entrants=[];
for(const aliases of groups.values()){
 const deck=aliases.find(d=>d.presetId>=54)||aliases[0],profile=mapping.assignments.find(a=>a.presetId===deck.presetId).profile;
 if(aliases.some(d=>mapping.assignments.find(a=>a.presetId===d.presetId).profile!==profile))throw Error('Alias Classic profile mismatch');
 for(const group of ['hard','classic'])entrants.push({...deck,key:group+':'+deck.presetId,group,policy:group==='hard'?'092':'beta',profile,aliases:aliases.map(d=>({presetId:d.presetId,title:d.title,hardProfile:d.hardProfile}))});
}
fs.mkdirSync(out,{recursive:true});const codeFiles={};
function copy(p){const rel=path.relative(root,p).replaceAll('\\','/'),dest=path.join(out,'frozen',rel);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(p,dest);codeFiles[rel]=sha(dest);}
function walk(p){for(const e of fs.readdirSync(p,{withFileTypes:true})){const x=path.join(p,e.name);if(e.isDirectory())walk(x);else copy(x);}}
walk(path.join(root,'tools/ai/beta_js092'));
for(const n of ['comparison_bridge119.js','versioned_match092.js','variant_decks092.js','profile_trial_io093.cjs','run_classic093_knockout.cjs','prepare_classic093_knockout.cjs','launch_classic093_knockout.py','Start-Classic093Tournament.ps1'])copy(path.join(root,'tools/ai',n));
fs.copyFileSync(mappingPath,path.join(out,'profile-mapping.json'));
fs.writeFileSync(path.join(out,'entrants.json'),JSON.stringify(entrants,null,2)+'\n',{flag:'wx'});
const masterSeed=crypto.randomInt(1,4294967295-64*8*128*8),base={schema:1,build,current:rules,commonFingerprint:manifest.fingerprint,commonManifestSha256:sha(path.join(rules,'manifest.json')),codeFiles,rosterSha256:sha(path.join(out,'entrants.json')),mappingSha256:sha(mappingPath),grids,workers,masterSeed};
fs.writeFileSync(path.join(out,'preflight-config.json'),JSON.stringify(base,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({prepared:true,entrants:entrants.length,uniqueCompositions:groups.size,grids,workers,masterSeed}));
