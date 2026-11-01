'use strict';
// Whole-catalog source triage. Node motifs and test mentions are navigation
// evidence, never a claim that a card's complete semantics have been verified.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),out=path.resolve(process.argv[3]);
if(fs.existsSync(out))throw Error('Fresh output required');fs.mkdirSync(out,{recursive:true});
const file=path.join(root,'data/beta924/normalized/catalog.json'),raw=fs.readFileSync(file),catalog=JSON.parse(raw);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const {createRuntime}=require('./beta_js092/session.cjs'),rt=createRuntime(path.resolve(process.argv[2]));
const fields={power:'Power',armor:'Armor',typeMask:'Type',tierMask:'Tier',factionMask:'FactionId'};
const rulesDir=path.join(root,'BetaGwent/development/scripts/game/betagwent');
const handlers=fs.readdirSync(rulesDir).filter(n=>/^duel.*\.ws$/.test(n)&&!/^duel(?:Catalog|Audio|Clone)/.test(n)).map(n=>({file:'BetaGwent/development/scripts/game/betagwent/'+n,lines:fs.readFileSync(path.join(rulesDir,n),'utf8').split(/\r?\n/)}));
const testDir=path.join(root,'tools/ai'),tests=fs.readdirSync(testDir).filter(n=>/^check.*\.(?:cjs|js)$/.test(n)&&!['check_all_cards198.cjs'].includes(n)).map(n=>({file:'tools/ai/'+n,text:fs.readFileSync(path.join(testDir,n),'utf8')}));
const motifs={history:/Matching.*(?:Played|History)|History/,move:/MoveCards|SwapCards|CardPosition|AvailableLocations|RandomPosition|Return.*Card/,random:/Random|Shuffle/,identity:/FilterCardIdNode/,categories:/FilterCardCategoryNode/,round:/Round.*Trigger|RoundId/,timing:/Before|After|Trigger/,power:/ChangePower|PowerChanged|SetPower|Armor/,printedPower:/CardDefinitionGetPowerNode/,transform:/Transform|SetDefinition|ChangeTemplate/,hidden:/Ambush|Reveal|Visible|Visibility/,variables:/SetVarNode|GetVarNode/,creation:/Spawn|Create|Resurrect|Summon|PlayCards/};
const weights={history:9,move:5,random:2,identity:3,categories:2,round:5,timing:2,power:1,printedPower:7,transform:5,hidden:5,variables:1,creation:3};
const independentlyReviewed={200103:{test:'tools/ai/check_olaf095.cjs',status:'confirmed-discrepancy-fixed',note:'self instance / history category / turn player / clone reversal / armor'},200080:{test:'tools/ai/check_xavier095.cjs',status:'confirmed-discrepancy-fixed',note:'latest other Dwarf uses template power, not mutable base power'},152403:{test:'tools/ai/check_whale094a.cjs',status:'source-semantics-checked',note:'other non-full row; move then current-row damage; owner turn; lock; append'},122314:{test:'tools/ai/check_armor_conversion094a.cjs',status:'source-semantics-checked',note:'saved armor, set0, one-to-one boost'}};
const classHashes=new Map();
const branchEvidence=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/design/rules_audit095_branches.json'),'utf8'));
for(const e of branchEvidence.records){
 const previous=independentlyReviewed[e.templateId];
 independentlyReviewed[e.templateId]={test:e.test,status:e.discrepancyFixed||previous?.status==='confirmed-discrepancy-fixed'?'confirmed-discrepancy-fixed':'partial-independent-source-check',note:previous?.note?previous.note+'; '+e.testedBranches:e.testedBranches,branchEvidence:e};
}
independentlyReviewed[112110]={test:'tools/ai/check_ciri_dash_round095.cjs',status:'confirmed-discrepancy-fixed',note:'AfterRound returns to deck only without Resilient; real Adrenaline Rush regression'};
independentlyReviewed[152209]={test:'tools/ai/check_mork_order095.cjs',status:'confirmed-discrepancy-fixed',note:'halve in grave before checking positive current power and available placement; original CardPower banishes zero-base inactive cards'};
independentlyReviewed[201625]={test:'tools/ai/audit_transform095.cjs',status:'confirmed-discrepancy-fixed',note:'same-definition branch uses ResetCards(255), including template base, armor, tokens and timer'};
independentlyReviewed[200088]={test:'tools/ai/audit_base_strength095.cjs',status:'confirmed-discrepancy-fixed',note:'only Boosted deck units are drained/reset; wounded units remain wounded'};
independentlyReviewed[112207]={test:'tools/ai/audit_olgierd095.cjs',status:'confirmed-discrepancy-fixed',note:'persistent Killed starts false; discard does not arm resurrection; leaving grave clears the latch'};
for(const id of [112104,112105,112213,122318,133301,142303,152106,162303,200031,200534,201644,201656,201817])
 if(!independentlyReviewed[id])independentlyReviewed[id]={test:'tools/ai/audit_base_strength095.cjs',status:'partial-independent-source-check',note:'base-strength reader with strengthened/weakened base and wounded/normal/boosted current power; nested effects not fully proven'};
for(const id of [152107,200053,152301])independentlyReviewed[id]={test:'tools/ai/audit_transform095.cjs',status:'partial-independent-source-check',note:'all-reset transform branch; damaged Berserker with lock/armor; complete external reactions not proven'};
independentlyReviewed[132101]={test:'tools/ai/audit_draug095.cjs',status:'partial-independent-source-check',note:'grave population, row capacity, identity and reset; exact RNG stream/external reactions remain open'};
for(const id of [132215,201601])independentlyReviewed[id]={test:'tools/ai/audit_history_gaunter095.cjs',status:'partial-independent-source-check',note:'printed-strength guesses or latest eligible own Spell history across rounds; nested copied abilities not fully proven'};
// Carry forward the completed reset/heal block. These are branch-level proofs:
// tutors, every Shupe option, exact RNG and outside reactions remain separate.
const resetEvidence={};
for(const id of [113320,113403,113404,200223,201562,201563,122211,162204,200233,200132,201523,113205,201644,201598,201703])
 resetEvidence[id]={test:'tools/ai/audit_reset_power095.cjs',scope:'Reset(Power)/Restore branch, wounds vs boosts, retained instance base and armor'};
resetEvidence[200040]={test:'tools/ai/audit_greatsword096.cjs',scope:'owner-turn timer, wounded-only reset and base strengthening'};
for(const id of [152317,201737,201740])resetEvidence[id]={test:'tools/ai/audit_armorsmith_shupe096.cjs',scope:'Armorsmith healing/armor or Shupe Knight reset branch'};
for(const [id,evidence]of Object.entries(resetEvidence)){
 if(!independentlyReviewed[id])independentlyReviewed[id]={test:evidence.test,status:'partial-independent-source-check',note:evidence.scope};
 independentlyReviewed[id].additionalSourceChecks=[evidence];
}
// Accepted primary checks for the final 100+198 cards. Keep the original
// expectation files intact: later edge amendments refine their stated limits.
for(const [name,test] of [
 ['batch100','audit_batch100{a,b,c,d,e}096'],['creators20','audit_creators20096'],
 ['templates21','audit_templates21096'],['lists','audit_lists096'],
 ['spawn','audit_spawn096'],['tchoice','audit_tchoice096'],['flow','audit_flow096'],['misc','audit_misc096']]){
 const file=`data/beta924/design/rules_audit096_${name}_sources.json`;
 const source=JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));
 const tests=(name==='batch100'?[...'abcde'].map(c=>`audit_batch100${c}096`):[test]).map(n=>`tools/ai/${n}.cjs`);
 const records=[...source.records,...(source.rallyIds||[]).map(id=>({id,expected:source.rallyExpected}))];
 for(const e of records){const prior=independentlyReviewed[e.id];
  independentlyReviewed[e.id]={...prior,test:prior?.test||(tests.length===1?tests[0]:undefined),tests,status:prior?.status||'partial-independent-source-check',
   note:[prior?.note,(e.expected||'Independent primary branch checked; full external reactions remain open.').replace('Exact native dictionary order and all child abilities deferred.','Exact source dictionary/shuffle order confirmed; child abilities remain separate.').replace('No target -> nothing (open: mod refuses to play Decoy without targets).','No target -> no effect; nested Decoy without targets completes to graveyard.')].filter(Boolean).join('; '),
   primaryEvidence:{file,sha256:sha(fs.readFileSync(path.join(root,file))),tests,allBranchesComplete:false}};
 }
}
for(const [id,note] of Object.entries({
 201633:'Empty request still spawns 201758 in a random available own row; full rows create none.',
 162212:'AfterPassed preserves/clamps the row index; destination capacity respected.',
 200162:'Chosen-card AfterMoved arms the persistent counter; own BeforeTurnEnd asks for bounce; lock and event-card completion checked.',
 133302:'Spawned child boosted while awaiting placement, before its Played graph.',
 200146:'Empty or skipped choice still consumes IntGetRandom bound1; nonempty uses filtered deck length+1.',
 201780:'Empty enemy Soldier grave resolves without an added pause.',
 131102:'Empty choice returns the captured pair with exact forward MoveCards insertion at index0.',
 201725:'All five Mage modes checked in every one of three offered slots, both seats.',
 201731:'All five Hunter modes checked in every slot; 15-damage target pool includes both seats, excludes executing owner/Ambush/NotTargetable.'
})){
 const prior=independentlyReviewed[id];independentlyReviewed[id]={...prior,status:id==201725?'partial-independent-source-check':'confirmed-discrepancy-fixed',
  note:note+' Other full-graph/external-reaction combinations remain open.',edgeEvidence:{test:'tools/ai/audit_edges096.cjs',allBranchesComplete:false}};
}
const cards=[],missingNodeClasses=new Set(),attributeDifferences=[];
for(const template of catalog.templates){
 const id=template.templateId;if(id<100000)continue;
 const d=rt.definition(id),active=d.header.templateId>0&&[2,4].includes(d.header.typeMask);
 const abilities=catalog.abilities.filter(a=>a.templateId===id),nodes=abilities.flatMap(a=>a.nodes),types=[...new Set(nodes.map(n=>n.type))].sort();
 if(!active)continue;
 const diff=[];for(const [key,source]of Object.entries(fields))if(d.header[key]!==Number(template.fields[source]))diff.push({field:key,source:Number(template.fields[source]),mod:d.header[key]});
 for(const [key,source]of [['initialTimer','InitialTimer'],['tokens','Tokens']])if(d[key]!==Number(template.fields[source]))diff.push({field:key,source:Number(template.fields[source]),mod:d[key]});
 if(diff.length)attributeDifferences.push({id,differences:diff});
 const risks=Object.keys(motifs).filter(k=>types.some(t=>motifs[k].test(t)));
 // Hidden/locked states are commonly encoded in token fields, not class names.
 const tokenNodes=nodes.filter(n=>n.type==='FilterCardTokensNode'||/Trigger$/.test(n.type));
 if(!risks.includes('hidden')&&tokenNodes.some(n=>n.sourceTree.children.some(x=>x.tag==='IsAmbushing'&&x.attributes.V==='True'||x.tag==='Tokens'&&(Number(x.attributes.V)&8)!==0)))risks.push('hidden');
 const references=[];for(const h of handlers)h.lines.forEach((line,i)=>{if(new RegExp('\\b'+id+'\\b').test(line))references.push({file:h.file,line:i+1});});
 const testMentions=tests.filter(t=>new RegExp('\\b'+id+'\\b').test(t.text)).map(t=>t.file);
 const cs=types.map(t=>{
  const file='BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay/'+t+'.cs';
  if(!classHashes.has(file))classHashes.set(file,fs.existsSync(path.join(root,file))?sha(fs.readFileSync(path.join(root,file))):null);
  return {type:t,file,sha256:classHashes.get(file)};
 });
 for(const item of cs)if(!fs.existsSync(path.join(root,item.file)))missingNodeClasses.add(item.type);
 const cardBranches=branchEvidence.records.filter(e=>e.templateId===id);
 const review={...(independentlyReviewed[id]||{status:'needs-independent-source-comparison'}),...(cardBranches.length?{branchEvidenceRecords:cardBranches}:{})};
 const sourceObligations=abilities.map(a=>({graph:a.nid,nodes:a.nodes.map(n=>({id:n.nodeId,type:n.type,fullSemanticsProven:false,referencedByBranchEvidence:cardBranches.some(e=>e.graph===a.nid&&e.nodeIds.includes(n.nodeId))}))}));
 const openQuestions=cardBranches.length?[...new Set(cardBranches.flatMap(e=>e.openQuestions))]:[abilities.length?'Остальные ветви графа, формулы, фильтры, порядок операций и внешних реакций требуют независимой сверки.':'Нет самостоятельного графа: проверить общие правила, исходные жетоны и скрытые состояния шаблона.'];
 cards.push({id,title:catalog.localization.ru_ru[id+'_name']||template.attributes.DebugName,kind:d.header.typeMask,tier:d.header.tierMask,sourceAbilities:abilities.map(a=>({nid:a.nid,nodes:a.nodes.length,sha256:sha(JSON.stringify(a))})),nodeTypes:types,sourceNodeClasses:cs,risks,priority:risks.reduce((n,k)=>n+weights[k],0),handlerReferences:references,testMentions,semanticReview:review,fullAbilityProven:false,sourceObligations,openQuestions,attributeDifferences:diff});
}
cards.sort((a,b)=>b.priority-a.priority||a.id-b.id);
const report={schema:1,fingerprint:rt.fingerprint,catalogSha256:sha(raw),betaTarget:catalog.target,scope:'All playable/supported engine unit and special templates, including leaders and created tokens. Source is extracted Beta client gameplay graphs and shared C#; a separate live server is not accessed.',cards:cards.length,sourceAbilities:cards.reduce((n,c)=>n+c.sourceAbilities.length,0),independentlyReviewed:cards.filter(c=>c.semanticReview.status!=='needs-independent-source-comparison').length,attributeDifferences,missingNodeClasses:[...missingNodeClasses].sort(),riskCounts:Object.fromEntries(Object.keys(motifs).map(k=>[k,cards.filter(c=>c.risks.includes(k)).length])),semanticCoverageComplete:false,nativeGameplayVerified:false,records:cards};
fs.writeFileSync(path.join(out,'catalog-audit.json'),JSON.stringify(report,null,2)+'\n');
const lines=['# Сверка правил с бетой — весь каталог','','Технический прогон не доказывает совпадение формулы карты. Упоминание ID и совпадение WS/JS не доказывают способность. Статус исправления относится к найденному расхождению; вся способность этим не закрывается.',
 '',`Всего ${report.cards} карт; ${report.independentlyReviewed} имеют хотя бы частичную независимую сверку. Полная сверка каталога открыта. Для каждого узла JSON-матрица сохраняет отдельное обязательство проверки, а наличие ссылки из проверки ветви не приравнивается к доказанному узлу.`,
 '', 'Ожидаемые результаты нового блока, ссылки на графы/узлы и воспроизведение: [размещение и перемещение](BETA_MOVEMENT_AUDIT_095_RU.md). Новые блоки: [переходы между зонами](BETA_ZONE_AUDIT_095_RU.md), [пакет 25 карт](BETA_BATCH25_095_RU.md), [жетоны и раскрытие](BETA_TOKENS_AUDIT_096_RU.md), [формулы силы](BETA_POWER_AUDIT_096_RU.md), [реакции и общие пулы](BETA_REACTIONS_AUDIT_096_RU.md), [блок80 карт](BETA_BATCH80_096_RU.md). Машиночитаемые утверждения: [rules_audit095_branches.json](../data/beta924/design/rules_audit095_branches.json).',
 '','| ID | Карта | Графы / узлы | Риски | Статус | Проверенные ветви | Открыто |','|---|---|---|---|---|---|---|'];
const cell=x=>String(x||'—').replace(/\|/g,'/').replace(/\r?\n/g,' ');
for(const c of cards)lines.push(`| ${c.id} | ${cell(c.title)} | ${c.sourceAbilities.map(a=>a.nid+' / '+a.nodes).join('; ')} | ${c.risks.join(', ')} | ${c.semanticReview.status} | ${cell(c.semanticReview.note)} | ${cell(c.openQuestions.join(' '))} |`);
fs.writeFileSync(path.join(out,'catalog-audit.md'),lines.join('\n')+'\n');
console.log(JSON.stringify({cards:report.cards,abilities:report.sourceAbilities,attributeDifferences,missingNodeClasses:report.missingNodeClasses,risks:report.riskCounts,semanticCoverageComplete:false}));
if(report.cards!==511)process.exitCode=1;
