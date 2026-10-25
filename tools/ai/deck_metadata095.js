// Export names, leaders and actual rosters from the SAME frozen rules as play.
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const dir=path.resolve(process.argv[2]),manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));
for(const [name,hash]of Object.entries(manifest.snapshotFiles))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,name))).digest('hex')!==hash)throw Error('Changed snapshot: '+name);
const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n');
const decks=new Function('ids',code+String.raw`
return ids.map(id=>{const preset=BetaGwentDuelPreset(id),leader=BetaGwentDuelDefinition(preset.leaderTemplateId),cards={v:[]};
 if(!BetaGwentDuelPresetDeck(id,cards))throw Error('Missing deck '+id);
 return {presetId:id,title:BetaGwentAIProfileTitle(BetaGwentAIPresetProfile(id)),requestedLeader:leader.title,leader:preset.leaderTemplateId,faction:leader.header.factionMask,templateIds:cards.v};
});`)(manifest.presets);
fs.writeFileSync(process.argv[3],JSON.stringify({fingerprint:manifest.fingerprint,decks},null,2));
console.log(JSON.stringify({decks:decks.length,fingerprint:manifest.fingerprint,minimumCards:Math.min(...decks.map(d=>d.templateIds.length)),maximumCards:Math.max(...decks.map(d=>d.templateIds.length))}));
