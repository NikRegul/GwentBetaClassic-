// Tournament entrants may share a policy profile while using explicit legal rosters.
// The adapter changes only preset lookup; battle/AI methods remain frozen WS code.
'use strict';
const fs=require('fs'),path=require('path');
function adapter(extras=[]){return `
const __extraDecks=${JSON.stringify(extras)};
const __extraById=new Map(__extraDecks.map(d=>[d.presetId,d]));
const __originalPreset=BetaGwentDuelPreset,__originalCards=BetaGwentDuelPresetDeck,__originalProfile=BetaGwentAIPresetProfile;
for(const d of __extraDecks){
 if(!Number.isInteger(d.presetId)||d.presetId<100||__originalPreset(d.basePreset).id===0)throw Error('Invalid extra entrant');
 const leader=BetaGwentDuelDefinition(d.leader),v=BetaGwentValidateDeck(d.templateIds,leader.header.factionMask,d.leader);
 if(!v.valid)throw Error('Invalid variant '+d.presetId+': '+v.message);
}
BetaGwentDuelPreset=function(id){const d=__extraById.get(id);if(!d)return __originalPreset(id);
 const p=__originalPreset(d.basePreset),v=BetaGwentValidateDeck(d.templateIds,BetaGwentDuelDefinition(d.leader).header.factionMask,d.leader);
 p.id=id;p.leaderTemplateId=d.leader;p.title=d.title;p.unitCount=v.units;p.specialCount=v.specials;p.goldCount=v.gold;p.silverCount=v.silver;return p;};
BetaGwentDuelPresetDeck=function(id,out){const d=__extraById.get(id);if(!d)return __originalCards(id,out);out.v=d.templateIds.slice();return true;};
BetaGwentAIPresetProfile=function(id){const d=__extraById.get(id);return __originalProfile(d?d.basePreset:id);};
`;}
function load(snapshot,extras=[],suffix='',mode='function'){
 const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\n'+adapter(extras)+'\n'+suffix;
 if(mode==='vm'){const ctx=require('vm').createContext({console});require('vm').runInContext(code,ctx);return ctx.__harness;}
 return new Function(code+'\nreturn __harness;')();
}
module.exports={adapter,load};
