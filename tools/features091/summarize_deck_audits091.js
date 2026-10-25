'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const runs=process.argv.slice(2).map(p=>path.resolve(p)),reports=runs.map(dir=>JSON.parse(fs.readFileSync(path.join(dir,'report.json'),'utf8')));
if(!reports.length||new Set(runs).size!==runs.length||reports.some(r=>!r.complete||r.errors)||new Set(reports.map(r=>r.identity.fingerprint)).size!==1)throw Error('Use distinct complete error-free runs of the same snapshot');
const config=JSON.parse(fs.readFileSync(path.join(runs[0],'config.json'),'utf8'));
const source=fs.readFileSync(path.join(config.snapshot,'sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'),'utf8'),titles={};
for(const m of source.matchAll(/value\.id = (\d+);[^\r\n]*[\r\n]+\s*value\.title = "([^"]+)"/g))titles[m[1]]=m[2];
const decks=new Map(),passReasons={},losingPasses=[],suspects=[];let decisions=0,mulliganOptions=0,checked=0;
for(let index=0;index<reports.length;index++)for(const game of reports[index].games){
 const trace=JSON.parse(zlib.gunzipSync(fs.readFileSync(game.trace)));decisions+=trace.decisions.length;if(game.deterministic&&game.probesDidNotChangePlay)checked++;
 mulliganOptions+=trace.logs.filter(l=>/event=MULLIGAN_OPTION\b/.test(l.text)).length;
 for(const d of trace.decisions)if(d.pass){const key=/\breason=([^ ]+)/.exec(d.pass)?.[1];passReasons[key]=(passReasons[key]||0)+1;
  if(d.after.winner&&game.winner!==3&&game.winner!==d.before.actor+1&&d.before.hand.some(c=>c.canPlay))losingPasses.push({run:runs[index],game:game.id,step:d.step,preset:d.before.preset,score:d.before.score,pass:d.pass,hand:d.before.hand});}
 for(const s of trace.suspects)suspects.push({run:runs[index],game:game.id,kind:s.kind,step:s.step,preset:s.before.preset,picked:s.picked,alternatives:s.alternatives});
 for(const [seat,id,enemy] of [[1,game.left,game.right],[2,game.right,game.left]]){
  if(!decks.has(id))decks.set(id,{id,title:titles[id],games:0,wins:0,losses:0,draws:0,opponents:[]});const d=decks.get(id);d.games++;
  d[game.winner===seat?'wins':game.winner===3?'draws':'losses']++;if(!d.opponents.includes(enemy))d.opponents.push(enemy);
 }
}
const result={snapshot:reports[0].identity.fingerprint,runs,games:reports.reduce((n,r)=>n+r.completedGames,0),decisions,mulliganOptions,deterministicAndNoninterferingMatches:checked,passReasons,losingPassesWithCards:losingPasses,suspectsNeedingReview:suspects,decks:[...decks.values()].sort((a,b)=>a.id-b.id)};
fs.writeFileSync(path.join(runs[0],'combined-summary.json'),JSON.stringify(result,null,2));
const lines=['# Диагностика колод ИИ 0.9.1d','',`Завершено ${result.games} партий, ${decisions} решений. Ошибок исполнения: 0. Повторяемость и отсутствие влияния диагностических симуляций подтверждены для ${checked} партий.`,
 '', 'Максимальная сложность с обеих сторон. Seeds и расписания сохранены. В систематических сериях колоды меняются местами; одинаковый seed при перестановке разных колод не означает одинаковые стартовые руки. В случайной серии перемешиваются соперники и стороны, каждой партии назначается отдельный seed. Это диагностическая выборка, её результаты зависят от конкретных соперников и не являются рейтингом колод или оценкой игры против человека.',
 '', ...reports.flatMap((r,i)=>[`Серия ${i+1}: ${r.completedGames} партий; ${r.protocol}.`, `Данные: ${runs[i]}`, '']),
 '', '| ID | Колода | Партий | Победы / поражения / ничьи | Разных соперников |', '|---|---|---:|---:|---:|',
 ...result.decks.map(d=>`| ${d.id} | ${d.title} | ${d.games} | ${d.wins} / ${d.losses} / ${d.draws} | ${d.opponents.length} |`),
 '', `Автоматические сигналы для ручной проверки: ${suspects.length}. Они не считаются подтверждёнными ошибками: прирост корон после ничьей может сопровождаться проигрышем матча, а розыгрыш дорогого добора может улучшать будущую руку.`,
 '', 'Журналы всех партий и исходные состояния сохранены в подпапках matches. Для проверки конкретного решения:', '', '```powershell', 'node tools/features091/replay_deck_audit091.js <полный путь к game-N.json.gz> <номер шага> <путь к результату.json>', '```',
 '', 'Переигрывание проверяет совпадение исходной линии целиком, затем меняет один ход и заканчивает матч тем же ИИ. Улучшение на одной раздаче — повод проверить правило на других состояниях, а не основание сразу менять веса.', ''];
fs.writeFileSync(path.join(runs[0],'SUMMARY_RU.md'),lines.join('\n'));
console.log(JSON.stringify({games:result.games,decisions,checked,decks:decks.size,suspects:suspects.length,losingPassesWithCards:losingPasses.length,summary:path.join(runs[0],'SUMMARY_RU.md')}));
