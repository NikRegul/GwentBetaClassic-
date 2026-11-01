'use strict';
// The received card, not either played deck, owns reward art and collection progress.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
process.env.ROOT=path.resolve(__dirname,'../..');
const H=require('./preview_screens096/harness.cjs');
const menuFile=path.join(process.env.ROOT,'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws');
const menu=fs.readFileSync(menuFile,'utf8');
function extractWs(name){const start=menu.indexOf('function '+name+'('),open=menu.indexOf('{',start);let end=open+1,depth=1;while(depth){depth+=(menu[end]==='{')-(menu[end]==='}');end++;}
 return menu.slice(start,end).replace(/:\s*(?:W3PlayerWitcher|SBetaGwentDuelDefinition|int)\b/g,'').replace(/var faction\s*;/,'var faction=0;');}
let checks=0;const failures=[];const check=(v,n)=>{checks++;if(!v)failures.push(n);};
const factions={1:'Нейтральные',2:'Чудовища',4:'Нильфгаард',8:'Королевства Севера',16:"Скоя'таэли",32:'Скеллиге'};
const ws=vm.createContext({FlashArgInt:n=>n,BetaGwentCollectionTotal:f=>f?100:479,BetaGwentDuelDefinition:id=>({header:{factionMask:H.byId[id].faction}})});
vm.runInContext(extractWs('PublishOutcomeProgress'),ws);
const records=[];
for(const relative of ['BetaGwent/ui/src/BetaGwentBoard.as','tools/features091/BetaGwentBoard_classic093.as']){
 const source=fs.readFileSync(path.join(process.env.ROOT,relative),'utf8'),c=H.ctx;
 vm.runInContext(['setOutcomeProgress','drawOutcomeProgress097','drawRewardPanel096','paintBetaFace'].map(n=>H.extract(n,source)).join('\n'),c);
 Object.assign(c,{rewardMessage:'',animations:[],reducedMotion:true,playing:false});
 for(const faction of [1,2,4,8,16,32]){
  const card=H.all.find(x=>x.faction===faction&&x.typeMask===4&&x.tier!==1);check(!!card,'reward fixture exists '+faction);if(!card)continue;
  let sent=null;ws.setOutcomeProgress={InvokeSelfSixArgs:(...args)=>{sent=args;}};
  ws.PublishOutcomeProgress({BetaGwentCollectionCount:f=>f?17:137},136,card.templateId);
  check(sent[3]===faction&&sent[4]===17&&sent[5]===100,'WS reports the received faction '+faction);
  c.setOutcomeProgress(...sent);const rows=[];c.outcomeBar097=(p,label,before,after,total)=>rows.push({label,before,after,total});
  c.rewardCard096={templateId:card.templateId,gained:0,total:500};c.drawOutcomeProgress097(new c.Sprite());
  check(rows[0].label==='Коллекция'&&rows[0].before===136&&rows[0].after===137,'collection progress '+faction);
  check(rows[1].label===factions[faction]&&rows[1].before===16&&rows[1].after===17,'correct faction progress and delta '+faction);
  // Deliberately use a leader from a different faction. A neutral reward must
  // keep its neutral banner; the in-battle owner tint does not apply here.
  c.leaderIds=[faction===8?131101:200168,200162];
  const host=new c.Sprite();c.drawRewardPanel096(true,host);
  const expected=-1610-[2,4,8,16,32,1].indexOf(faction);
  check(H.dump(host).some(o=>o.art?.id===expected),'reward card keeps its own banner '+faction);
 }
 let sent=null;ws.setOutcomeProgress={InvokeSelfSixArgs:(...args)=>{sent=args;}};
 ws.PublishOutcomeProgress({BetaGwentCollectionCount:f=>f?17:137},137,0);
 c.setOutcomeProgress(...sent);c.rewardCard096={templateId:0,gained:5,total:505};const rows=[];c.outcomeBar097=(p,label)=>rows.push(label);c.drawOutcomeProgress097(new c.Sprite());
 check(sent[3]===0&&rows.length===1&&rows[0]==='Коллекция','scraps-only reward does not invent a faction');
 records.push({source:relative,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(process.env.ROOT,relative))).digest('hex')});
}
const report={checks,failures,records,actualActionScript:true,actualWitcherScript:true,menuSourceSha256:crypto.createHash('sha256').update(fs.readFileSync(menuFile)).digest('hex'),nativeGameTested:false};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
