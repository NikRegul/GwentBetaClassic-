'use strict';
const fs=require('fs'),path=require('path'),{adapter}=require('./variant_decks092.js');
const snapshot=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json')));
const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n');
const base=new Function('ids',code+String.raw`
return ids.map(id=>{const p=BetaGwentDuelPreset(id),l=BetaGwentDuelDefinition(p.leaderTemplateId),cards={v:[]};BetaGwentDuelPresetDeck(id,cards);
return {presetId:id,title:BetaGwentAIProfileTitle(BetaGwentAIPresetProfile(id)),requestedLeader:l.title,leader:p.leaderTemplateId,faction:l.header.factionMask,templateIds:cards.v};});`)(manifest.presets);
function variant(id,baseId,title,changes){const b=base.find(d=>d.presetId===baseId),d={...b,presetId:id,basePreset:baseId,title,templateIds:b.templateIds.slice()};
 for(const [a,z,n=1]of changes)for(let i=0;i<n;i++){const at=d.templateIds.indexOf(a);if(at<0)throw Error('Missing replacement '+a);d.templateIds[at]=z;}return d;}
const extraDecks=[
 variant(100,96,'Крах: мечники — Игни',[[201776,112102]]),
 variant(101,94,'Аретуза — рыцари и Ласточка',[[200033,201622,2],[113302,113310,2]]),
 variant(102,95,'Узурпатор — Райнфарн и Кантарелла',[[200031,200032],[162401,162210]])
];
// Validate every entrant with the actual frozen WS deck validator before writing configuration.
new Function(code+'\n'+adapter(extraDecks))();
fs.mkdirSync(out,{recursive:true});
const config={snapshot,out,workers:16,seed:923001701,simDamp:40,blocksByStrength:{4:1},extraDecks};
fs.writeFileSync(path.join(out,'variants.json'),JSON.stringify(extraDecks,null,2));
fs.writeFileSync(path.join(out,'deck-metadata.json'),JSON.stringify({fingerprint:manifest.fingerprint,decks:base.concat(extraDecks)},null,2));
fs.writeFileSync(path.join(out,'config-proposal.json'),JSON.stringify(config,null,2));
console.log(JSON.stringify({fingerprint:manifest.fingerprint,entrants:base.length+extraDecks.length,variants:extraDecks.map(d=>({id:d.presetId,title:d.title}))}));
