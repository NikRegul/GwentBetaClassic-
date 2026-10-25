'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const [source,output]=process.argv.slice(2),root=path.resolve(source),out=path.resolve(output);
if(fs.existsSync(out))throw Error('Use a fresh analysis folder');fs.mkdirSync(out,{recursive:true});
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const plan=read(path.join(root,'plan.json')),entrants=read(path.join(root,'entrants.json')),byKey=new Map(entrants.map(e=>[e.key,e]));
if(sha(path.join(root,'plan.json'))!=='0b77e00347265b84915bb759253f4a15d1445b6510abadecb7dda6ae05945380')throw Error('Unexpected historical plan');
const series=fs.readdirSync(path.join(root,'series')).filter(n=>n.endsWith('.json')).sort().map(n=>read(path.join(root,'series',n))).filter(s=>s.grid<13);
if(series.length!==13*183)throw Error('Expected exactly13 completed brackets');
const stats=new Map(),losses=[];let games=0;
for(const s of series)for(const item of s.games){
 const file=path.join(root,'games',item.id+'.json');if(sha(file)!==item.sha256)throw Error('Historical game changed');const g=read(file);games++;
 for(const side of [1,2]){
  const key=side===1?g.left:g.right,e=byKey.get(key),enemy=byKey.get(side===1?g.right:g.left);if(e.group!=='hard')continue;
  if(!stats.has(key))stats.set(key,{key,title:e.title,faction:e.faction,games:0,points:0,losses:0,swept:0,opponents:{}});
  const row=stats.get(key),won=g.winner===side,draw=g.winner===3;row.games++;row.points+=draw?.5:Number(won);row.losses+=Number(!won&&!draw);row.swept+=Number(!won&&!draw&&g.crowns[side-1]===0);
  const mode=enemy.group;row.opponents[mode]??={games:0,points:0};row.opponents[mode].games++;row.opponents[mode].points+=draw?.5:Number(won);
  if(!won&&!draw&&enemy.group==='hard')losses.push({game:item.id,side,key,enemy:enemy.key,faction:e.faction,title:e.title,seed:g.seed,crowns:g.crowns,turns:g.trace.length,swept:g.crowns[side-1]===0});
 }
}
const decks=[...stats.values()].map(r=>({...r,pointRate:r.points/r.games})).sort((a,b)=>a.pointRate-b.pointRate);
// Development evidence spans factions and different losing/winning compositions.
// No outcome from this selection is later called an independent holdout.
const selected=[];
for(const faction of [2,4,8,16,32]){
 const seen=new Set();for(const row of losses.filter(r=>r.faction===faction).sort((a,b)=>Number(b.swept)-Number(a.swept)||a.turns-b.turns||a.game.localeCompare(b.game))){
  if(seen.has(row.key))continue;seen.add(row.key);selected.push(row);if(seen.size===3)break;
 }
}
const report={schema:1,kind:'development-evidence-not-strength-trial',source:root,planSha256:sha(path.join(root,'plan.json')),completedBrackets:13,completedSeries:series.length,games,decks,selected};
fs.writeFileSync(path.join(out,'sessions-analysis.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({games,series:series.length,decks:decks.length,lowest:decks.slice(0,12).map(r=>({title:r.title,faction:r.faction,games:r.games,rate:r.pointRate})),selected}));
