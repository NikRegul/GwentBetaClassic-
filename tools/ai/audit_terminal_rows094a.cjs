'use strict';
// Development audit only: enumerate actual legal plays on a synthetic final
// turn. No hidden hand, no future deck, no random-roll hindsight acceptance.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
if(fs.existsSync(out))throw Error('Use a fresh audit directory');fs.mkdirSync(out,{recursive:true});
fs.copyFileSync(__filename,path.join(out,'runner.cjs'));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(snapshot);
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
c.ids=catalog.templates.filter(t=>[2,4,8].includes(t.fields.Tier)&&t.fields.Type===4&&Number(t.placement.PlayerSide)===7&&Number(t.placement.OpponentSide)===0&&Number(t.attributes.Availability)===1).map(t=>Number(t.attributes.Id));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
Host.matchStrength=[4,4];let serial=-1680000000;
function terminalPosition(id,counts){
 const g=fixture();for(const card of g.live)card.Move(card.Snapshot().positionPlayerId,512,0);
 g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=true;
 g.random.Initialize(3129701);
 for(const [row,n]of [[1,counts[0]],[2,counts[1]],[4,counts[2]]])for(let i=0;i<n;i++)add(g,112101,row,i,2,5);
 for(const row of [1,2,4])add(g,112101,row,0,1,7);
 const card=add(g,id,8,0);g.archetypeAI.Refresh();return {g,card};
}
function terminalAudit(id,counts){
 const {g,card}=terminalPosition(id,counts),anchor=g.AiPlacementAnchor(card.Definition());
 const chosen=anchor?g.FindCard(anchor).Snapshot().locationMask:g.BestCardRow(2,card.Definition()),options=[];
 const chosenIndex=anchor?g.FindCard(anchor).Snapshot().locationIndex:g.AiAdjacencyIndex(card,chosen);
 const actualIndex=chosenIndex<0?g.CountLocation(2,chosen):chosenIndex;
 for(const row of [1,2,4]){
  if(g.CountLocation(2,row)>=9)continue;
  for(let index=0;index<=g.CountLocation(2,row);index++){
  const h=new CBetaGwentCloner().CloneSession(g,--serial),draws=h.random.DrawCount();
  try{
   if(!h.PlayAtIndex(2,card.Snapshot().instanceId,row,index)||h.IsPending()||h.IsFatal()){options.push({row,index,complete:false});continue;}
   if(!h.Snapshot().matchWinnerMask&&!h.Pass(2)){options.push({row,index,complete:false});continue;}
   const m=h.Snapshot();options.push({row,index,complete:!!m.matchWinnerMask&&!h.IsPending()&&!h.IsFatal(),
    lead:h.Score(2)-h.Score(1),winner:m.matchWinnerMask,draws:h.random.DrawCount()-draws});
  }catch(e){options.push({row,index,complete:false,error:String(e.message)});}
  }
 }
 const eligible=options.length>0&&options.every(x=>x.complete&&x.draws===0),actual=options.find(x=>x.row===chosen&&x.index===actualIndex);
 return {id,counts,chosen,chosenIndex:actualIndex,anchor,options,eligible,dominated:eligible&&!!actual&&actual.lead<Math.max(...options.map(x=>x.lead))};
}
`,c);
const report={complete:false,fingerprint:manifest.fingerprint,scope:'Synthetic final-turn development positions, ordinary public board, no enemy hand or leaders; differences are review priorities, not automatic fixes or strength results.',records:[],notHistoricalReplay:true,nativeGameplayVerified:false};
for(const counts of [[4,1,0],[0,4,1],[2,2,1]])for(const id of c.ids){
 c.job={id,counts};report.records.push(vm.runInContext('terminalAudit(job.id,job.counts)',c,{timeout:15000}));
 if(report.records.length%50===0)fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
}
report.complete=true;report.eligible=report.records.filter(x=>x.eligible).length;report.dominated=report.records.filter(x=>x.dominated).length;
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({positions:report.records.length,eligible:report.eligible,dominated:report.dominated,ids:[...new Set(report.records.filter(x=>x.dominated).map(x=>x.id))]}));
