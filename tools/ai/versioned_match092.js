// Two historical policies and rosters, one authoritative set of card mechanics.
'use strict';
const fs=require('fs'),path=require('path');
const bridge=require('./comparison_bridge119.js'),variants=require('./variant_decks092.js');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
function extract(snapshot){
 const manifest=read(path.join(snapshot,'manifest.json'));
 const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n');
 return new Function('ids',code+String.raw`
 return ids.map(id=>{const p=BetaGwentDuelPreset(id),leader=BetaGwentDuelDefinition(p.leaderTemplateId),cards={v:[]};BetaGwentDuelPresetDeck(id,cards);
 const legal=BetaGwentValidateDeck(cards.v,leader.header.factionMask,p.leaderTemplateId);if(!legal.valid)throw Error(legal.message);
 return {presetId:id,basePreset:id,title:BetaGwentAIProfileTitle(BetaGwentAIPresetProfile(id)),leader:p.leaderTemplateId,faction:leader.header.factionMask,templateIds:cards.v};});`)(manifest.presets);
}
function metadata(current,original){
 const fresh=extract(current).map(d=>({...d,version:'0.9.2',title:'0.9.2 — '+d.title}));
 const old=extract(original).map(d=>({...d,presetId:d.presetId+100,version:'0.9.1',title:'0.9.1 — '+d.title}));
 return {fingerprint:read(path.join(current,'manifest.json')).fingerprint,originalFingerprint:read(path.join(original,'manifest.json')).fingerprint,decks:[...fresh,...old]};
}
function load(config,mode='function'){
 const meta=read(path.join(config.out,'deck-metadata.json')),byId=new Map(meta.decks.map(d=>[d.presetId,d]));
 const extras=meta.decks.filter(d=>d.version==='0.9.1');
 function host(dir){const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n')+'\n'+variants.adapter(extras)+String.raw`
const __originalTraining=BetaGwentAITrainingWeight;
BetaGwentAITrainingWeight=function(preset,index){const d=__extraById.get(preset);return __originalTraining(d?d.basePreset:preset,index);};
`+'\n'+bridge;
  let h;if(mode==='vm'){const c=require('vm').createContext({console});require('vm').runInContext(code,c);h=c.bridge;}
  else h=new Function(code+'\nreturn globalThis.bridge;')();
  h.setTunes(read(path.join(dir,'tunes.json')));h.setStrength(config.strength);h.setSimDamp(config.simDamp);return h;
 }
 const hosts={'0.9.2':host(config.snapshot),'0.9.1':host(config.oldPolicy)};
 function transfer(from,to){if(config.nativeTransfer!==false)to.loadNative(from.dumpNative());else to.load(from.dump());}
 function play(left,right,seed){
  let h=hosts['0.9.2'],steps=0;const policies=[byId.get(left)?.version,byId.get(right)?.version];
  if(policies.some(p=>!hosts[p]))throw Error('Unknown versioned entrant');
  try{
   const initial=h.initialize(left,right,seed),first=hosts[policies[1]];
   if(first!==h){first.load(initial);h=first;}h.initialMulligan();
   for(;steps<500;steps++){
    let s=h.view();if(s.fatal)throw Error(s.message);
    if(s.winner){const winner=s.reversed?((s.winner&1)<<1)|((s.winner&2)>>1):s.winner,result={left,right,seed,winner,steps};
     if(config.validationDigest)result.stateSha256=require('crypto').createHash('sha256').update(h.dump()).digest('hex');return result;}
    if(!s.mulligan&&!s.pending&&!s.waiting&&s.current===1){h.swap();s=h.view();}
    const chooser=s.mulligan?1-s.actor:s.actor,target=hosts[policies[chooser]];
    if(target!==h){transfer(h,target);h=target;}h.step();
   }
   throw Error('decision limit');
  }catch(e){return {left,right,seed,winner:0,steps,error:String(e.stack||e)};}
 }
 return {play,hosts,meta};
}
module.exports={metadata,extract,load};
