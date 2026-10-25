'use strict';
// Candidate discovery uses authored asset bindings and actual deck overlap.
// No score modification, source-profile editing, or extra hidden information.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),rules=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
const genericGaps=process.argv.includes('--generic-gaps');
if(fs.existsSync(out))throw Error('Fresh experiment directory required');
const {personality}=require('./beta_js092/profiles.cjs'),raw=require('./beta_js092/data/personalities.json');
const practice={2:'p_Monster_Practice',4:'p_Nilfgaard_Practice',8:'p_NorthernRealms_Practice',16:"p_Scoia'tael_Practice",32:'p_Skellige_Practice'};
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sourcePath=path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js/original-rosters.json');
const original=read(sourcePath),approved=read(path.join(root,'data/beta924/design/beta_deck_import092.json'));
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const api=new Function(source+String.raw`
return {deck:id=>{let p=BetaGwentDuelPreset(id),cards={v:[]};if(!BetaGwentDuelPresetDeck(id,cards))throw Error('Deck');
 const faction=BetaGwentDuelDefinition(p.leaderTemplateId).header.factionMask,legal=BetaGwentValidateDeck(cards.v,faction,p.leaderTemplateId);if(!legal.valid)throw Error(id+': '+legal.message);
 return {presetId:id,basePreset:id,title:p.title,leader:p.leaderTemplateId,faction,templateIds:cards.v};},faction:id=>BetaGwentDuelDefinition(id).header.factionMask};`)();
function key(d){return d.leader+':'+d.templateIds.slice().sort((a,b)=>a-b).join(',');}
function overlap(a,b){const counts=new Map();for(const id of b)counts.set(id,(counts.get(id)||0)+1);let total=0;for(const id of a)if(counts.get(id)>0){total++;counts.set(id,counts.get(id)-1);}return total/Math.max(a.length,b.length);}
function supported(n){if(!raw[n])return false;const p=personality(n);return p.TreeSearchType==='AlphaBeta'&&p.EvaluatorType==='MiniMax'&&p.CardPickerType==='BestCardForPersonality';}
function signature(n){const p=personality(n);delete p.name;return JSON.stringify(p);}
const references=[];
for(const d of original.decks)for(const player of d.players||[]){if(!player.personality)continue;references.push({asset:d.asset,profile:player.personality,faction:d.faction,leader:d.leader.templateId,cards:d.cards,provenance:'Serialized PlayerDefinition -> DeckDefinition'});}
for(const [name,p]of Object.entries(raw))if(p.values.Deck){
 const entries=p.values.Deck.trim().split(/\r?\n/).map(s=>s.split(';')),cards=[],leader=Number(entries[0][0]);
 for(const e of entries.slice(1))for(let i=0;i<Number(e[3]||1);i++)cards.push(Number(e[0]));
 const tally={};for(const t of cards){const f=api.faction(t);if(f>1)tally[f]=(tally[f]||0)+1;}
 const faction=api.faction(leader)||Number(Object.keys(tally).sort((a,b)=>tally[b]-tally[a])[0]||0);
 references.push({asset:name,profile:name,faction,leader,cards,provenance:'Original AIPersonality.Deck property'});
}
const bySource=new Map(original.decks.map(d=>[d.asset,d]));
const importAssets=new Map(approved.decks.map((d,i)=>[100+i,d.asset]));
const units=new Map(),bindings=[];
for(let id=21;id<=129;id++){
 const d=api.deck(id),k=key(d),asset=importAssets.get(id),direct=asset?(bySource.get(asset)?.players||[]).map(p=>p.personality).filter(Boolean):[];
 if(asset){const src=bySource.get(asset);if(!src||src.leader.templateId!==d.leader||overlap(src.cards,d.templateIds)!==1)throw Error('Imported preset/source mismatch '+id+'/'+asset);}
 const binding={presetId:id,title:asset||d.title,asset:asset||null,directSerializedProfiles:direct};bindings.push(binding);
 if(!units.has(k))units.set(k,{...d,key:'deck'+id,aliases:[],direct:new Set()});
 const unit=units.get(k);unit.aliases.push(binding);for(const n of direct)unit.direct.add(n);
}
const decks=[];
for(const d of units.values()){
 const baseline=practice[d.faction];if(!baseline)throw Error('Unknown faction '+d.faction);
 const scores=new Map(),proof=new Map();
 for(const ref of references){if(ref.faction!==d.faction||!supported(ref.profile))continue;
  const value=overlap(d.templateIds,ref.cards)+(ref.leader===d.leader ? 0.08 : 0);
  if(value>(scores.get(ref.profile)??-1)){scores.set(ref.profile,value);proof.set(ref.profile,{...ref,overlap:value,cards:undefined});}}
 const names=[...d.direct,...[...scores].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).map(x=>x[0])];
 const candidates=[],seen=new Set([signature(baseline)]);
 for(const n of names){if(!supported(n))continue;const sig=signature(n);if(seen.has(sig))continue;
  if(!d.direct.has(n)&&(scores.get(n)||0)<.30)continue;seen.add(sig);
  candidates.push({profile:n,direct:d.direct.has(n),affinity:scores.get(n)||null,evidence:proof.get(n)||{provenance:'Serialized source binding'}});
  if(candidates.length===2)break;}
 if(genericGaps){
  if(candidates.length)continue;
  for(const name of ['Base','Base_Challenges'])if(!seen.has(signature(name))){seen.add(signature(name));candidates.push({profile:name,direct:false,affinity:null,evidence:{provenance:'Original generic source control for a composition without a distinct matched profile'}});}
 }
 decks.push({...d,direct:[...d.direct],baseline,candidates});
}
const schedule=[];
// Compare each actual source candidate against its incumbent on the SAME deck.
// Keep both mirror seats together. This screens profile suitability; a later
// varied-opponent holdout is required before selecting shipping bindings.
for(const d of decks)for(let c=0;c<d.candidates.length;c++)for(let block=0;block<2;block++)for(let mirror=0;mirror<2;mirror++){
 const candidate={...d,key:d.key+':'+d.candidates[c].profile,policy:'beta',profile:d.candidates[c].profile};
 const incumbent={...d,key:d.key+':'+d.baseline,policy:'beta',profile:d.baseline};
 schedule.push({id:`${d.key}-c${c}-b${block}-m${mirror}`,deck:d.key,candidate:d.candidates[c].profile,baseline:d.baseline,block,mirror,seed:924110001+d.presetId*101+block*10007,left:mirror?incumbent:candidate,right:mirror?candidate:incumbent});
}
fs.mkdirSync(out,{recursive:true});fs.mkdirSync(path.join(out,'games'));
const files={};function copy(src){const rel=path.relative(root,src),dest=path.join(out,'frozen',rel);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(src,dest);files[rel.replaceAll('\\','/')]=sha(dest);}
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else copy(p);}}
walk(path.join(root,'tools/ai/beta_js092'));
for(const n of ['comparison_bridge119.js','versioned_match092.js','variant_decks092.js','run_beta_profile_trials093.cjs'])copy(path.join(root,'tools/ai',n));
const manifest=read(path.join(rules,'manifest.json'));
const plan={schema:1,kind:genericGaps?'beta-profile-generic-gap-screening':'beta-profile-deck-screening',ratingPermitted:false,current:rules,commonFingerprint:manifest.fingerprint,commonManifestSha256:sha(path.join(rules,'manifest.json')),codeFiles:files,sourceRosterSha256:sha(sourcePath),bindings,decks,schedule,
 selectionRule:'Screen candidates on two mirrored self-deck pairs; then freeze separate varied-opponent holdout before shipping. Do not select by profile name or change original profile settings.',stopOnError:true};
fs.writeFileSync(path.join(out,'plan.json'),JSON.stringify(plan,null,2)+'\n');
console.log(JSON.stringify({out,uniqueDecks:decks.length,presets:bindings.length,candidates:decks.reduce((n,d)=>n+d.candidates.length,0),games:schedule.length,planSha256:sha(path.join(out,'plan.json'))}));
