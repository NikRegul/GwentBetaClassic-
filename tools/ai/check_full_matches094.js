// Separate fixed technical smoke games. Never reads or writes a tournament.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const {load}=require('./diagnose_strategy096.js');
const snapshot=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
if(fs.existsSync(out))throw Error('Use a fresh smoke output directory');
const {context:ctx,manifest}=load(snapshot);
const mapping=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/beta924/design/beta_ai_profiles093.json'),'utf8'));
ctx.presetIds=mapping.assignments.map(d=>d.presetId);
const roster=vm.runInContext(`presetIds.map(id=>{const p=BetaGwentDuelPreset(id),d=BetaGwentDuelDefinition(p.leaderTemplateId);return {id,faction:d.header.factionMask};})`,ctx);
const games=[];
for(const faction of [2,4,8,16,32]){
 const pool=roster.filter(d=>d.faction===faction),imported=pool.find(d=>d.id>=100),npc=pool.find(d=>d.id<54);
 if(!imported||!npc)throw Error('Need an imported and NPC deck for faction '+faction);
 const seed=(0x09410240+faction*1009)>>>0;
 games.push({faction,left:imported.id,right:npc.id,seed},{faction,left:npc.id,right:imported.id,seed});
}
const plan={schema:1,kind:'technical-smoke-not-strength-trial',fingerprint:manifest.fingerprint,strength:4,simDamp:40,games};
const planText=JSON.stringify(plan,null,2)+'\n',planSha256=crypto.createHash('sha256').update(planText).digest('hex');
fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'plan.json'),planText);
const report={schema:1,kind:plan.kind,fingerprint:manifest.fingerprint,planSha256,planned:games.length,complete:false,errors:0,games:[]};
function save(){fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');}
save();
for(const game of games){const start=Date.now();
 const result=ctx.__harness.play(game.left,game.right,game.seed,4,4,30);
 report.games.push({...game,...result,ms:Date.now()-start});if(result.error)report.errors++;
 save();console.log(JSON.stringify({completed:report.games.length,planned:games.length,presets:[game.left,game.right],winner:result.winner,steps:result.steps,error:result.error||null}));
 if(result.error)throw Error('Technical smoke failed; no result awarded');
}
report.complete=true;save();console.log(JSON.stringify({complete:report.complete,games:report.games.length,errors:report.errors,planSha256}));
