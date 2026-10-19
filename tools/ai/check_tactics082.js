'use strict';
// Behavioural scenarios on the immutable 0.8.2 release; no gameplay patches.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..');
const args=process.argv.slice(2),opt=(n,d)=>args.includes(n)?args[args.indexOf(n)+1]:d;
const snapshot=path.resolve(opt('--snapshot','BetaGwent/build/audit082-20261018/rules'));
const out=path.resolve(opt('--output','BetaGwent/build/audit082-20261018/tactics'));
const strength=+opt('--strength','4'),damp=+opt('--damp','40');
if(![2,3,4].includes(strength)||!Number.isFinite(damp)||damp<0||damp>100)throw Error('strength must be 2/3/4 and damp must be 0..100');
const filter=opt('--cases','').split(',').filter(Boolean),presetFilter=opt('--presets','').split(',').filter(Boolean).map(Number);
fs.mkdirSync(out,{recursive:true});
fs.copyFileSync(__filename,path.join(out,'runner.js'));
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
if(!/\/release(?:082|090)-[^/]+$/.test(manifest.source?.replaceAll('\\','/')))throw Error('Use a frozen 0.8.2/0.9.0 release audit snapshot');
const ctx=vm.createContext({console:{log(){}},settings:{strength,damp}});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+String.raw`
Host.strength=settings.strength;Host.matchStrength=[settings.strength,settings.strength];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let stamp=100000,lastGame=null,lastDecision=null;
function add(g,id,zone,index=0,side=2,power){
 const key={v:0};if(!g.registry.Allocate(key))throw Error('registry allocation');
 const c=new CBetaGwentDuelCard();c.Setup(g,key.v,id,side,zone,index);
 if(power!==undefined)c.power.SetCurrentPair(power,0);g.registry.Put(key.v,c);g.live.push(c);return c;
}
function blank(preset,{round=3,enemyCrowns=1,ownCrowns=1,passed=false,enemyHand=3}={}){
 Host.strength=settings.strength;Host.seatIndex=1;Host.random=()=>.37;
 const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,preset))throw Error('preset '+preset);
 for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.pendingChoice=false;g.pendingPileChoice=false;g.pendingRow=false;g.pendingIds=[];
 g.waiting=false;g.recordVisuals=false;g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;
 g.match.roundNumber=round;g.match.playerOne.crowns=enemyCrowns;g.match.playerTwo.crowns=ownCrowns;
 g.match.playerOne.hasPassed=passed;g.match.playerTwo.hasPassed=false;g.aiSimDamp=settings.damp;
 for(let i=0;i<enemyHand;i++)add(g,112405,8,i,1);
 lastGame=g;lastDecision=null;return g;
}
function hand(g,ids){return ids.map((id,i)=>add(g,id,8,i));}
function live(c){const s=c.Snapshot();return (s.locationMask&7)!==0&&!s.isWaitingToDie&&s.power.currentPower>0;}
function clone(g){const h=new CBetaGwentCloner().CloneSession(g,++stamp);h.aiSimulating=true;h.recordVisuals=false;return h;}
function finish(g){const s=g.match.Snapshot();if(!s.matchWinnerMask&&s.currentPlayerId===2&&s.turnActive&&!g.IsPending())g.Pass(2);return g.match.Snapshot().matchWinnerMask;}
function outcome(g,id){const h=clone(g),value=h.AiSimPlay(id);if(value===-2147483647)return {valid:false};return {valid:true,winner:finish(h),lead:h.Score(2)-h.Score(1)};}
function view(g){return {round:g.match.roundNumber,current:g.match.currentPlayerId,turnActive:g.match.turnActive,crowns:[g.match.playerOne.crowns,g.match.playerTwo.crowns],scores:[g.Score(1),g.Score(2)],passed:[g.match.playerOne.hasPassed,g.match.playerTwo.hasPassed],
 cards:g.live.map(c=>c.Snapshot()).filter(s=>s.locationMask!==512).map(s=>({id:s.instanceId,t:s.runtimeTemplate.templateId,side:s.positionPlayerId,zone:s.locationMask,index:s.locationIndex,power:s.power.currentPower,armor:s.power.armor,tokens:s.tokenMask,timer:s.timerValue})),winner:g.match.Snapshot().matchWinnerMask};}
function act(g){const lines=[];Host.log=s=>lines.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 return {ok,fatal:g.IsFatal(),pending:g.IsPending(),message:g.GetMessage(),logs:lines.filter(s=>/event=(SELECT|PASS|CHASE|TARGET_SELECT|TARGET_FINISH)|DUEL_PLAY |DUEL_LEADER_USE/.test(s)),after:view(g)};}
function need(condition,message){if(!condition)throw Error(message);}
function decision(g){const a=act(g);lastDecision=a;need(a.ok&&!a.fatal&&!a.pending,'decision rejected/fatal/pending: '+a.message);return a;}
function deck(preset){const a={v:[]};need(BetaGwentDuelPresetDeck(preset,a),'missing deck');return [...new Set(a.v)];}
const winnerCache=new Map();
function actualWinner(preset,tier){
 const key=preset+':'+tier;if(winnerCache.has(key))return winnerCache.get(key);
 for(const id of deck(preset)){
  const d=BetaGwentDuelDefinition(id);if(d.header.typeMask!==4||tier&&d.header.tierMask!==tier||BetaGwentDuelSpying(id))continue;
  const g=blank(preset,{passed:true});add(g,112405,1,0,1,3);add(g,112405,1,0,2,1);const c=hand(g,[id])[0];
  if(outcome(g,c.Snapshot().instanceId).winner===2){winnerCache.set(key,id);return id;}
 }
 winnerCache.set(key,0);return 0;
}
const cases=[];
function scenario(id,title,scope,expected,run,level='required'){cases.push({id,title,scope,expected,run,level});}
scenario('P01','Пас при уже выигранной партии','actual-deck','Пас, ни одной потраченной карты и лидера',(p)=>{
 const g=blank(p,{passed:true});add(g,112405,1,0,1,5);add(g,112405,1,0,2,30);
 const cards=hand(g,deck(p).slice(0,8));const leader=add(g,g.leaderTemplateTwo,64);
 const a=decision(g);need(g.match.playerTwo.hasPassed&&g.match.Snapshot().matchWinnerMask===2,'does not take guaranteed winning pass');
 need(cards.every(c=>c.Snapshot().locationMask===8)&&leader.Snapshot().locationMask===64,'spends resources after victory is secured');return a;
});
scenario('P02','Последний реальный отряд выигрывает финал','actual-deck','Использовать имеющийся выигрышный ответ',(p)=>{
 const id=actualWinner(p,2)||actualWinner(p);need(id,'fixture: no winning unit in deck');
 const g=blank(p,{passed:true});add(g,112405,1,0,1,3);add(g,112405,1,0,2,1);const c=hand(g,[id])[0];
 const a=decision(g);need(c.Snapshot().locationMask!==8&&!g.match.playerTwo.hasPassed,'concedes holding guaranteed final-round win');need(finish(g)===2,'fails to convert one-card win');return a;
});
scenario('P03','Бронзовый догон сохраняет настоящее золото','actual-deck','Выиграть одной бронзой и сохранить золото на следующий раунд',(p)=>{
 const bronze=actualWinner(p,2),gold=actualWinner(p,8);if(!bronze||!gold)return {skip:'нет пары подходящих реальных карт'};
 const g=blank(p,{round:1,enemyCrowns:0,ownCrowns:0,passed:true});add(g,112405,1,0,1,3);add(g,112405,1,0,2,1);
 const [b,z]=hand(g,[bronze,gold]),a=decision(g);need(b.Snapshot().locationMask!==8&&z.Snapshot().locationMask===8,'spends gold instead of sufficient real bronze');need(finish(g)===0&&g.match.playerTwo.crowns===1,'does not secure the round');return a;
});
scenario('P04','Золото разрешено ради спасения партии','actual-deck','Потратить золото, если это единственный выигрыш',(p)=>{
 const id=actualWinner(p,8);if(!id)return {skip:'нет подходящего золотого отряда'};
 const g=blank(p,{passed:true});add(g,112405,1,0,1,3);add(g,112405,1,0,2,1);const c=hand(g,[id])[0],a=decision(g);
 need(c.Snapshot().locationMask!==8&&finish(g)===2,'reserves gold while losing the match');return a;
});
scenario('P05','Переполненный ряд не блокирует догон','actual-deck','Выбрать свободный ряд и довести выигрыш до паса',(p)=>{
 const id=actualWinner(p,2)||actualWinner(p),g=blank(p,{passed:true});
 for(let i=0;i<9;i++)add(g,112405,1,i,2,1);add(g,112405,1,0,1,10);const c=hand(g,[id])[0];
 const proof=outcome(g,c.Snapshot().instanceId);if(proof.winner!==2)return {skip:'этот реальный отряд не выигрывает конкретную заполненную позицию'};
 const a=decision(g);need([1,2,4].every(row=>g.CountLocation(2,row)<=9),'overfills row');need(c.Snapshot().locationMask!==8&&finish(g)===2,'misses winning placement in a free row');return a;
});
scenario('P06','Безнадёжный догон не сжигает руку','profile-probe','Пас в необязательном раунде при недостижимых очках',(p)=>{
 const g=blank(p,{round:1,enemyCrowns:0,ownCrowns:0,passed:true});add(g,112405,1,0,1,300);const cards=hand(g,[112405,112405]);
 const a=decision(g);need(g.match.playerTwo.hasPassed&&cards.every(c=>c.Snapshot().locationMask===8),'spends plain bodies into an impossible optional-round catch');return a;
});
scenario('C01','Казнь обеспечивает единственную победу','profile-probe','Сыграть Казнь и уничтожить высокий вражеский отряд',(p)=>{
 const g=blank(p,{passed:true});add(g,112405,2,0,2,5);const tall=add(g,112405,1,0,1,30);const scorch=hand(g,[113309])[0];
 const a=decision(g);need(scorch.Snapshot().locationMask!==8&&!live(tall)&&finish(g)===2,'holds winning Scorch while conceding');return a;
});
scenario('C02','Казнь уничтожает все чужие максимумы','profile-probe','Учесть обе цели одинаковой силы',(p)=>{
 const g=blank(p,{passed:true});add(g,112405,4,0,2,5);const x=add(g,112405,1,0,1,20),y=add(g,112405,2,0,1,20);hand(g,[113309]);
 const a=decision(g);need(!live(x)&&!live(y)&&finish(g)===2,'misses tied enemy Scorch payoff');return a;
});
scenario('C03','Не сжигать собственный максимум','profile-probe','Сохранить свою сильнейшую карту; Казнь не улучшает эту позицию',(p)=>{
 const g=blank(p,{passed:true});const own=add(g,112405,1,0,2,30);add(g,112405,1,0,1,20);const [scorch]=hand(g,[113309,112405]);
 const a=decision(g);need(live(own)&&scorch.Snapshot().locationMask===8&&g.match.Snapshot().matchWinnerMask===2,'destroys own maximum rather than take winning pass');return a;
});
scenario('C04','Игни: единственное окно победы','profile-probe','Учесть порог ряда и выиграть с помощью Игни',(p)=>{
 const g=blank(p,{passed:true});add(g,112405,2,0,2,6);const tall=add(g,112405,1,0,1,20);add(g,112405,1,1,1,5);const igni=hand(g,[112102])[0];
 const proof=outcome(g,igni.Snapshot().instanceId);need(proof.winner===2,'fixture: Igni must win');const a=decision(g);
 need(!live(tall)&&finish(g)===2,'misses winning Igni threshold');return a;
});
scenario('C05','Игни: несколько равных целей в ряду','profile-probe','Сжечь оба максимума в подходящем ряду',(p)=>{
 const g=blank(p,{passed:true});add(g,112405,2,0,2,5);const x=add(g,112405,1,0,1,12),y=add(g,112405,1,1,1,12);add(g,112405,1,2,1,1);hand(g,[112102]);
 const a=decision(g);need(!live(x)&&!live(y)&&finish(g)===2,'does not count tied Igni targets');return a;
});
scenario('C06','Игни: ниже порога нет выдуманного сжигания','profile-probe','Ряд на 24 очка сохраняет отряды после способности',(p)=>{
 const g=blank(p),targets=[];for(let i=0;i<4;i++)targets.push(add(g,112405,1,i,1,6));const c=hand(g,[112102])[0];
 need(g.Play(2,c.Snapshot().instanceId,2),'Igni play rejected');need(targets.every(live),'Igni incorrectly burns a row below 25');return {after:view(g)};
});
scenario('C07','Игни выбирает самый выгодный допустимый ряд','profile-probe','Из двух рядов уничтожить более ценный максимум',(p)=>{
 const g=blank(p);const low=add(g,112405,1,0,1,20);add(g,112405,1,1,1,5);const high=add(g,112405,2,0,1,30);add(g,112405,2,1,1,1);const c=hand(g,[112102])[0];
 need(g.Play(2,c.Snapshot().instanceId,4),'Igni play rejected');need(live(low)&&!live(high),'chooses inferior eligible Igni row');return {after:view(g)};
});
scenario('C08','Броня не спасает от уничтожения','profile-probe','Казнь оценивает силу; уничтожение обходит броню',(p)=>{
 const g=blank(p,{passed:true});add(g,112405,2,0,2,5);const tall=add(g,112405,1,0,1,30);tall.power.SetCurrentPair(30,100);hand(g,[113309]);
 const a=decision(g);need(!live(tall)&&finish(g)===2,'mistakes armour for immunity to Scorch');return a;
});
scenario('E01','Опасный движок важнее урона по большому телу','profile-probe','Убить Мируна, готовящую захват ценного союзника',(p)=>{
 const g=blank(p),vran=add(g,132305,1,0,1,27),miruna=add(g,132108,2,0,1,4);miruna.cardState.timerValue=2;
 add(g,142205,2,0,2,10);const sword=hand(g,[200535,112405,112405,112405])[0];sword.power.SetCurrentPair(9,0);
 need(g.Play(2,sword.Snapshot().instanceId,4),'damage card rejected');need(!live(miruna)&&vran.Snapshot().power.currentPower===27,'hits harmless tall body instead of preventable charm');return {after:view(g)};
});
scenario('E02','Заблокированный движок не имеет прежней угрозы','profile-probe','Отсутствующая способность не перевешивает больший полезный урон',(p)=>{
 const g=blank(p),big=add(g,112405,1,0,1,27),miruna=add(g,132108,2,0,1,4);miruna.cardState.timerValue=2;miruna.AddTokens(4);add(g,142205,2,0,2,10);
 const c=hand(g,[200535])[0];c.power.SetCurrentPair(9,0);need(g.Play(2,c.Snapshot().instanceId,4),'damage card rejected');
 need(big.Snapshot().power.currentPower===18,'overvalues locked charm and misses larger useful damage');return {after:view(g)};
});
scenario('E03','Пас владельца выключает будущие срабатывания','profile-probe','Не приписывать Мируна будущий ход после паса её владельца',(p)=>{
 const g=blank(p,{passed:true}),big=add(g,112405,1,0,1,27),miruna=add(g,132108,2,0,1,4);miruna.cardState.timerValue=2;add(g,142205,2,0,2,10);
 const c=hand(g,[200535])[0];c.power.SetCurrentPair(9,0);need(g.Play(2,c.Snapshot().instanceId,4),'damage card rejected');need(big.Snapshot().power.currentPower===18,'counters an engine that has no future activation');return {after:view(g)};
});
scenario('E04','Не тратить погоду вместо немедленного выигрыша','profile-probe','После паса противника сыграть очки, которые уже выигрывают',(p)=>{
 const g=blank(p,{passed:true});add(g,112405,1,0,1,5);const [weather,body]=hand(g,[113302,112405]);body.power.SetCurrentPair(6,0);
 const a=decision(g);need(weather.Snapshot().locationMask===8&&body.Snapshot().locationMask!==8&&finish(g)===2,'spends non-ticking weather instead of guaranteed winning body');return a;
});
scenario('E05','В решающем раунде срывать неизбежный захват','profile-probe','Прервать Мируна или выбрать линию, сохраняющую жертву',(p)=>{
 const g=blank(p),m=add(g,132108,2,0,1,4);m.cardState.timerValue=1;const victim=add(g,112405,2,0,2,20);
 const [sword]=hand(g,[200535,132305]);sword.power.SetCurrentPair(9,0);const a=decision(g);
 need(victim.Snapshot().positionPlayerId===2||!live(victim)||!live(m)||(m.Snapshot().tokenMask&4)!==0,'develops own engine while preventable charm steals twenty points');return a;
});
// An authored opponent uses only safe bodies and a public pass rule. No free
// turns are inserted: every action is applied by Play/Pass on the real FSM.
function opponent(g,steps){
 const m=g.match.Snapshot();if(m.currentPlayerId!==1||!m.turnActive)return {action:'inactive'};
 const cards=g.live.filter(c=>{const s=c.Snapshot();return s.positionPlayerId===1&&s.locationMask===8;});
 const lead=g.Score(1)-g.Score(2);
 if(!cards.length||lead>0&&(steps>=2||g.match.playerTwo.hasPassed))return {action:'pass',ok:g.Pass(1)};
 const c=cards.sort((a,b)=>a.Snapshot().power.currentPower-b.Snapshot().power.currentPower)[0];
 const row=[1,2,4].find(r=>g.CountLocation(1,r)<9);if(!row)return {action:'pass',ok:g.Pass(1)};
 return {action:'safe-body',template:c.TemplateId(),ok:g.Play(1,c.Snapshot().instanceId,row)};
}
for(const counter of [113309,112102])for(const advantage of [-1,1])for(const round of [1,2]){
 scenario('B'+(counter===113309?'S':'I')+(advantage<0?'minus':'plus')+'R'+round,(counter===113309?'Казнь':'Игни')+': раунд '+round+', давление, карт '+(advantage>0?'+1':'−1'),'profile-probe',
 'Блеф разрешён; нельзя спасовать с доказанным однокарточным выигрышем',p=>{
  const g=blank(p,{round,enemyCrowns:round===2?1:0,ownCrowns:0,enemyHand:0});
  add(g,112405,1,0,1,24);add(g,112405,1,1,1,5);add(g,112405,2,0,2,15);
  const mine=hand(g,[counter,112405,112405]);mine[1].power.SetCurrentPair(6,0);mine[2].power.SetCurrentPair(7,0);
  const enemyCount=mine.length-advantage;
  for(let i=0;i<enemyCount;i++)add(g,112405,8,i,1,5+i);
  const transcript=[];let counterAt=-1,opponentSteps=0;
  for(let turn=0;turn<16&&!g.match.Snapshot().matchWinnerMask&&!g.waiting;turn++){
   if(g.match.currentPlayerId===1){const reply=opponent(g,opponentSteps++);need(reply.ok,'scripted opponent action rejected: '+JSON.stringify(reply)+' '+g.GetMessage());transcript.push({actor:1,...reply,state:view(g)});continue;}
   const before=view(g),cards=g.live.filter(c=>{const s=c.Snapshot();return s.positionPlayerId===2&&s.locationMask===8;});
   let winning=[];
   if(g.match.playerOne.hasPassed)winning=cards.filter(c=>outcome(g,c.Snapshot().instanceId).winner===2).map(c=>c.TemplateId());
   const a=decision(g);transcript.push({actor:2,before,winning,...a});
   if(counterAt<0&&mine[0].Snapshot().locationMask!==8)counterAt=turn;
   need(!(round===2&&winning.length&&g.match.playerTwo.hasPassed),'passes with a guaranteed answer while facing elimination');
   if(g.match.playerOne.hasPassed&&!g.match.playerTwo.hasPassed&&g.match.currentPlayerId===2&&g.Score(2)>g.Score(1)){
    const a=decision(g);transcript.push({actor:2,...a});
   }
  }
  need(g.waiting||g.match.Snapshot().matchWinnerMask!==0,'scripted episode did not reach a round result');
  return {counterAt,advantage,transcript,result:view(g),observational:true};
 });
}
scenario('R01','Первый раунд: выигрыш ценой одной карты','profile-probe','Допускается потратить одну карту ради первого раунда',p=>{
 const g=blank(p,{round:1,enemyCrowns:0,ownCrowns:0,passed:true,enemyHand:4});add(g,112405,1,0,1,6);
 const cards=hand(g,[112405,112405,112405,112405]);cards[0].power.SetCurrentPair(7,0);
 const a=decision(g);need(!g.match.playerTwo.hasPassed&&g.Score(2)>g.Score(1),'refuses a clean first-round win at minus one card');
 need(finish(g)===0&&g.match.playerTwo.crowns===1,'fails to secure first round');return {...a,handBalance:g.CountLocation(2,8)-g.CountLocation(1,8)};
});
scenario('R02','Первый раунд: цена минус две карты','profile-probe','Зафиксировать цену, запас финишеров и мотив решения; выбор требует оценки',p=>{
 const g=blank(p,{round:1,enemyCrowns:0,ownCrowns:0,passed:true,enemyHand:4});add(g,112405,1,0,1,6);
 const cards=hand(g,[112405,112405,112405]);cards[0].power.SetCurrentPair(7,0);const a=decision(g);
 return {...a,projectedHandBalance:g.CountLocation(2,8)-g.CountLocation(1,8),observational:true};
});
scenario('R03','Первый раунд: не покупать победу ценой минус три','profile-probe','На обычных телах без переноса и комбинаций сохранить руку',p=>{
 const g=blank(p,{round:1,enemyCrowns:0,ownCrowns:0,passed:true,enemyHand:4});add(g,112405,1,0,1,6);
 const cards=hand(g,[112405,112405]);cards[0].power.SetCurrentPair(7,0);const a=decision(g);
 need(g.match.playerTwo.hasPassed&&cards.every(c=>c.Snapshot().locationMask===8),'buys optional round one at minus three without compensation');return a;
});
scenario('R04','Второй раунд после поражения: терпеть минус три ради спасения','profile-probe','Выиграть второй раунд, если уступка немедленно проигрывает матч',p=>{
 const g=blank(p,{round:2,enemyCrowns:1,ownCrowns:0,passed:true,enemyHand:4});add(g,112405,1,0,1,6);
 const cards=hand(g,[112405,112405]);cards[0].power.SetCurrentPair(7,0);const a=decision(g);
 need(!g.match.playerTwo.hasPassed&&g.Score(2)>g.Score(1),'applies optional-round economy while facing elimination');need(finish(g)===0&&g.match.playerTwo.crowns===1,'does not equalize the match');return a;
});
globalThis.tactical={cases,run(p,id){lastGame=null;lastDecision=null;const spec=cases.find(c=>c.id===id);return spec.run(p);},preset:p=>BetaGwentDuelPreset(p),view,diagnostic(){return {lastDecision,state:lastGame?view(lastGame):null};}};
`,ctx,{timeout:30000});
const specifications=ctx.tactical.cases.map(({id,title,scope,expected,level})=>({id,title,scope,expected,level}));
fs.writeFileSync(path.join(out,'cases.json'),JSON.stringify(specifications,null,2));
const report={version:'0.8.2',source:manifest.source,fingerprint:manifest.fingerprint,runnerSha256:crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),strength,damp,nativeGameTested:false,
 notes:['actual-deck uses cards from that exact preset','profile-probe supplies an authored tactical hand to every unchanged archetype; it does not claim that hand belongs to the shipping deck','bluff timing is observational; proven missed wins are required failures'],results:[]};
for(const preset of manifest.presets.filter(p=>!presetFilter.length||presetFilter.includes(p))){
 const summary={preset,pass:0,fail:0,skip:0};
 for(const spec of specifications.filter(c=>!filter.length||filter.includes(c.id))){
  ctx.job={preset,id:spec.id};const started=Date.now();let result;
  try{const detail=vm.runInContext('tactical.run(job.preset,job.id)',ctx,{timeout:30000});result={preset,case:spec.id,status:detail?.skip?'skip':'pass',...detail};}
  catch(e){result={preset,case:spec.id,status:'fail',error:String(e.stack||e),diagnostic:ctx.tactical.diagnostic()};}
  result.seconds=(Date.now()-started)/1000;report.results.push(result);summary[result.status]++;
  if(result.status==='fail')console.log('FAIL',preset,spec.id,result.error.match(/(?:Error|TypeError): [^\n]+/)?.[0]||result.error.split('\n')[0]);
 }
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(summary));
}
report.total=report.results.length;report.passed=report.results.filter(r=>r.status==='pass').length;report.failed=report.results.filter(r=>r.status==='fail').length;report.skipped=report.results.filter(r=>r.status==='skip').length;
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({total:report.total,passed:report.passed,failed:report.failed,skipped:report.skipped}));
process.exitCode=report.failed?1:0;
