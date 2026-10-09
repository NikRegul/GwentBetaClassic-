// Placement regressions against actual frozen WS rules, not a second AI implementation.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const code=['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n');
vm.runInContext(code+`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
function fixture(){const g=new CBetaGwentDuelSession();g.InitializeWithPresets(54,88);
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.waiting=false;
 g.weatherProfile=false;g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;
 g.match.roundNumber=2;g.match.playerOne.hasPassed=false;g.recordVisuals=false;return g;}
function add(g,template,zone,index){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,template,2,zone,index);g.registry.Put(id.v,c);g.live.push(c);return c;}
function check(ok,label){if(!ok)throw Error(label);console.log('PASS',label);}
for(const template of [112101,132310,142308,201600,122106]){
 const g=fixture();g.weather.hazards[3]=1;g.weather.hazards[4]=1;
 const d=BetaGwentDuelDefinition(template);
 check(g.BestCardRow(2,d)===4,'only safe row selected for '+template);
 for(let i=0;i<9;i++)add(g,112101,4,i);
 check(g.BestCardRow(2,d)!==4,'full safe row is excluded for '+template);
}
{
 const g=fixture();add(g,123301,1,0);add(g,122104,1,1);g.weather.hazards[3]=1;
 const d=BetaGwentDuelDefinition(122106);
 check(g.BestCardRow(2,d)!==1,'support engine does not force unit into frost');
}
{
 const g=fixture();g.weather.hazards[3]=1;g.weather.hazards[4]=1;g.weather.hazards[5]=1;
 check([1,2,4].includes(g.BestCardRow(2,BetaGwentDuelDefinition(112101))),'all rows frozen still permit a legal play');
}
`,context,{filename:'scenarios112.bundle.js',timeout:120000});
