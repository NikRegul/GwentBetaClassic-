'use strict';
const fs=require('fs'),crypto=require('crypto'),assert=require('assert/strict'),{catalog}=require('./source_graph095.cjs');
const file='data/beta924/design/rules_audit096_templates21_sources.json',raw=fs.readFileSync(file),source=JSON.parse(raw),sha=x=>crypto.createHash('sha256').update(x).digest('hex'),evidence={file,sha256:sha(raw),records:source.records};
assert(source.independentExpectationsBeforeHandlers&&source.records.length===19);
for(const r of source.records){assert.deepEqual(catalog.templates.find(t=>t.templateId===r.id),r.template);assert(catalog.abilities.filter(g=>g.templateId===r.id).every(g=>g.nodes.length===0));}
const {rt,add,snap,id,check,flush,run,begin,trace,finish}=require('./fixture_batch100096.cjs')(process.argv[2],evidence);
for(const r of source.records)for(const side of [1,2])run(r.id,side,'native template and real deploy',g=>{
 const f=r.template.fields,d=rt.definition(r.id),owner=begin(g,r.id,side,2,f.Power,f.Armor),s=snap(owner);
 check(d.header.power===f.Power&&d.header.armor===f.Armor,'printed power/armor exact source');check(d.header.typeMask===f.Type&&d.header.factionMask===f.FactionId,'template type/faction exact');
 check(s.runtimeTierMask===f.Tier,'source tier');check(s.timerValue===f.InitialTimer,'template timer without invented action');check(s.power.currentPower===f.Power&&s.power.basePower===f.Power&&s.power.permanentPower===0&&s.power.armor===f.Armor,'empty deploy preserves template power/armor');
 check(s.tokenMask===f.Tokens,'source innate tokens');check(s.positionPlayerId===side&&s.locationMask===2,'normal own-row deployment');check(!g.IsPending()&&g.random.DrawCount()===0,'no invented ability request/RNG');
});
for(const tid of source.rallyIds)for(const side of [1,2])for(const empty of [false,true])run(tid,side,'source FirstLight/Rally/'+empty,g=>{
 const unit=empty?null:add(g,132403,side,16,0),silver=add(g,132209,side,16,1),special=add(g,113301,side,16,2),before=g.live.length,rng=trace(g),owner=begin(g,113303,side);
 check(g.IsFirstLightChoice()&&g.SelectFirstLight(g.requestId,113402),'real FirstLight mode Rally');flush(g);
 if(unit){check(g.IsRallyRowRequest()&&g.CanSelectRow(g.requestId,side,2),'PlayCards hands placement of the played deck unit to its owner (PushCardsPlayStackAction)');g.SelectRow(g.requestId,side,2);flush(g);}
 if(unit)check(snap(unit).locationMask===2||snap(unit).locationMask===1||snap(unit).locationMask===4,'existing Bronze Unit played from deck');
 check(snap(silver).locationMask===16&&snap(special).locationMask===16,'Silver and Special excluded');check(rng.length===(empty?0:1),'singleton RNG1, empty0');check(g.live.length===before+1,'mode does not spawn extra card');check(!g.IsPending(),'branch completes');
});
finish(process.argv[3],'21 new cards:19 templates without executable card nodes, plus FirstLight and linked Rally primary mode. Global/shared token/row consumers and all branches deferred.');
