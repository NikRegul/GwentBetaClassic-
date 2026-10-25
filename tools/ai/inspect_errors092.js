// Replay selected completed error-audit games without changing the frozen tournament.
// Usage: node tools/ai/inspect_errors092.js <audit-root> <output-directory>
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const root=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
const config=JSON.parse(fs.readFileSync(path.join(root,'config.json'),'utf8'));
const records=fs.readFileSync(path.join(root,'results/records.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const dir=config.versions.new;
let code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n');
const marker='return { left, right, seed, winner: w, steps, crowns: sc };';
if(!code.includes(marker))throw Error('Unsupported frozen harness');
code=code.replace(marker,'return { left, right, seed, winner: w, steps, crowns: sc, trace };');
const h=new Function(code+'\nreturn __harness;')();h.Host.simDamp=config.simDamp;
fs.mkdirSync(out,{recursive:true});
// One actual flagged game from each class. Subsequent runs reuse the same seeds.
let wanted=[['conceding_pass','s4-174'],['spy_boost','s4-65'],['empty_slyzard','s4-15'],['nekker_deck_emptied','s3-23']];
if(process.argv.includes('--all'))wanted=records.flatMap(r=>Object.keys(r.results.new[0].counts||{}).filter(k=>r.results.new.some(g=>g.counts&&g.counts[k]>0)).map(k=>[k,r.id]));
const reports=[];
for(const [detector,id]of wanted){
 const task=records.find(r=>r.id===id);if(!task)throw Error('Missing task '+id);
 const reverse=task.results.new.findIndex(g=>g.counts&&g.counts[detector]>0);
 if(reverse<0)throw Error('Missing flag '+id);
 const left=reverse?task.b:task.a,right=reverse?task.a:task.b;
 const file=id+'-'+reverse+'.json.gz';
 const result=fs.existsSync(path.join(out,file))?JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(out,file)))).result:h.play(left,right,task.seed,task.strength,task.strength,1000000);
 const expected=task.results.new[reverse];
 if(result.winner!==expected.winner||result.steps!==expected.steps)throw Error('Replay mismatch '+id);
 fs.writeFileSync(path.join(out,file),zlib.gzipSync(JSON.stringify({task,detector,reverse,result})));
 const matches=[];
 for(let i=0;i<result.trace.length;i++){
  const line=result.trace[i];
  if(detector==='conceding_pass'&&/event=PASS /.test(line)
   ||detector==='spy_boost'&&/TARGET_SELECT .*effect=2 /.test(line)
   ||detector==='empty_slyzard'&&/event=SELECT .*template=200539 /.test(line)
   ||detector==='nekker_deck_emptied'&&/DUEL_DEATHWISH .*summon=132305/.test(line)){
   matches.push({line:i,context:result.trace.slice(Math.max(0,i-6),i+8)});
  }
 }
 reports.push({id,detector,reverse,left,right,seed:task.seed,strength:task.strength,winner:result.winner,steps:result.steps,exactReplay:true,file,matches});
 fs.writeFileSync(path.join(out,'replays.json'),JSON.stringify(reports,null,2)+'\n');
 console.log(JSON.stringify({id,detector,winner:result.winner,steps:result.steps,exactReplay:true,matches:matches.length}));
}
