'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {createRuntime}=require('./beta_js092/session.cjs'),{personality}=require('./beta_js092/profiles.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]),924022200),out=path.resolve(process.argv[3]);if(fs.existsSync(out))throw Error('Fresh output required');
const source=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/beta-original-js/original-rosters.json'),raw=fs.readFileSync(source),original=JSON.parse(raw);
const practice={2:'p_Monster_Practice',4:'p_Nilfgaard_Practice',8:'p_NorthernRealms_Practice',16:"p_Scoia'tael_Practice",32:'p_Skellige_Practice'};
const report={schema:1,sourceSha256:crypto.createHash('sha256').update(raw).digest('hex'),fingerprint:runtime.fingerprint,
 scope:'Exact original card lists checked by common final deck legality. Invalid challenge/tutorial decks preserved and excluded; no card replacement or repair.',records:[],eligible:[]};
for(let i=0;i<original.decks.length;i++){
 const d=original.decks[i],leader=d.leader.templateId,definition=runtime.definition(leader),faction=definition?.header.factionMask||0,valid=runtime.validateDeck(d.cards,faction,leader);
 const r={asset:d.asset,leader,faction,cards:d.cards.length,legal:valid.valid,message:valid.message,serializedProfiles:d.players.map(p=>p.personality).filter(Boolean)};
 if(valid.valid){
  const profile=practice[faction];if(!profile)throw Error('Missing standard Beta faction profile');const p=personality(profile);
  if(p.TreeSearchType!=='AlphaBeta'||p.EvaluatorType!=='MiniMax')throw Error('Standard Beta path missing');
  const deck={presetId:1000+i,asset:d.asset,title:d.asset,leader,faction,templateIds:d.cards,profile,serializedProfiles:r.serializedProfiles};
  // The practice policy is selected before results, uniformly by faction.
  // Original challenge personalities are retained in provenance, not silently
  // presented as the standard high-difficulty practice opponent.
  report.eligible.push(deck);r.selectedProfile=profile;
 }
 report.records.push(r);
}
report.originalDecks=original.decks.length;report.legalDecks=report.eligible.length;report.excludedDecks=report.originalDecks-report.legalDecks;
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({original:report.originalDecks,legal:report.legalDecks,excluded:report.excludedDecks}));
