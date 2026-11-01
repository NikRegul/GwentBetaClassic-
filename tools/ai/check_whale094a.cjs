// 0.9.4a: Dreamcave Whale (152403) moves at turn end to a random OTHER row
// with free space, never back into its current row. Confirmed from Beta graph
// 152403/228 and its C# nodes. Executes WS->JS; argv: rules [report].
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const graph=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8')).abilities.find(a=>a.templateId===152403);
assert.equal(graph.nid,228);
const node=id=>graph.nodes.find(n=>n.nodeId===id),value=(id,f)=>node(id).sourceTree.children.find(c=>c.tag===f).attributes.V;
const edge=(a,f,b,g)=>graph.connections.some(c=>c.sourcePort.nodeId===a&&c.sourcePort.field===f&&c.destinationPort.nodeId===b&&c.destinationPort.field===g);
assert.equal(node(12).type,'LocationIdNegateNode');assert.equal(value(12,'LocationMask'),'7');
assert(edge(16,'DV',12,'DS')&&edge(12,'DV',136,'Location')&&edge(136,'Out',142,'List'));
assert(edge(80,'FlowOut',172,'FlowIn')&&edge(120,'Out',122,'LocationId'));
assert.equal(value(182,'Tokens'),'8');assert.equal(value(182,'Negate'),'True');assert.equal(value(202,'Negate'),'True');
assert(edge(193,'DV',202,'CardId')&&edge(202,'Out',172,'e1'));
assert(edge(9,'Out',216,'PlayerIdFilter')&&edge(216,'FlowOut',142,'FlowIn'));
const {createRuntime}=require('./beta_js092/session.cjs');
const rt=createRuntime(path.resolve(process.argv[2]));let checks=0;const failures=[];
const check=(v,n)=>{checks++;if(!v)failures.push(n);};
const WHALE=152403,FILLER=152101,DECK=16,GRAVE=32,ROWS=[1,2,4];
function add(g,id,side,zone,index){const r={v:0};g.registry.Allocate(r);const c=rt.newCard();c.Setup(g,r.v,id,side,zone,index);g.registry.Put(r.v,c);g.live.push(c);return c;}
function session(row,fill){
 const g=rt.newSession();g.InitializeWithPresets(72,72);
 for(const c of g.live){const s=c.Snapshot();if(s.locationMask!==DECK&&s.locationMask!==GRAVE&&s.locationMask!==8)c.Move(s.positionPlayerId,GRAVE,0);}
 g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;g.recordVisuals=false;
 g.match.currentPlayerId=2;g.match.roundActive=g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=g.match.playerTwo.hasPassed=false;
 const whale=add(g,WHALE,2,row,0);const others={};
 for(const r of ROWS){others[r]=[];const n=fill[r]||0;for(let i=0;i<n;i++)others[r].push(add(g,FILLER,2,r,r===row?i+1:i));}
 return {g,whale,others};}
const power=s=>s.power.currentPower;
const snap=(g,c)=>{const id=c.Snapshot().instanceId;for(const x of g.live){const s=x.Snapshot();if(s.instanceId===id)return s;}return null;};
const records=[];
for(const row of ROWS){
 const seen={};let trials=0;
 for(let t=0;t<120;t++){
  const {g,whale,others}=session(row,{1:1,2:1,4:1});const before={};for(const r of ROWS)before[r]=others[r].map(c=>power(snap(g,c)));
  const ok=g.EndTurnWithEvents();check(ok!==false&&!g.IsFatal(),'turn end resolves from row '+row);
  const s=snap(g,whale);trials++;seen[s.locationMask]=(seen[s.locationMask]||0)+1;
  check(s.locationMask!==row,'whale leaves row '+row+' (trial '+t+')');
  check(s.positionPlayerId===2,'whale stays on its side');
  for(const r of ROWS)others[r].forEach((c,i)=>{const p=power(snap(g,c));check(r===s.locationMask?p===before[r][i]-1:p===before[r][i],'only units in the destination row take 1 damage');});
 }
 const other=ROWS.filter(r=>r!==row);
 check(other.every(r=>seen[r]>=20),'both other rows are reachable from row '+row+' '+JSON.stringify(seen));
 records.push({from:row,trials,destinations:seen});
}
// One other row full: the whale always takes the remaining free row.
for(const row of ROWS){const [full,free]=ROWS.filter(r=>r!==row);
 for(let t=0;t<20;t++){const {g,whale}=session(row,{[full]:9});g.EndTurnWithEvents();check(snap(g,whale).locationMask===free,'full row '+full+' skipped from '+row);}}
// Both other rows full: it stays and still damages the units beside it.
for(const row of ROWS){const fill={};for(const r of ROWS)if(r!==row)fill[r]=9;fill[row]=2;
 const {g,whale,others}=session(row,fill);const before=others[row].map(c=>power(snap(g,c)));g.EndTurnWithEvents();
 check(snap(g,whale).locationMask===row,'no free other row: whale stays in row '+row);
 others[row].forEach((c,i)=>check(power(snap(g,c))===before[i]-1,'no free other row: neighbours still take 1 damage'));
 check(power(snap(g,whale))===rt.definition(WHALE).header.power,'whale itself is not damaged');}
// The passive follows the current board side, never the creator/other turn;
// lock suppresses it, and a normal jump appends to the destination row.
for(const side of [1,2])for(const locked of [false,true]){
 const {g,whale,others}=session(1,{1:1,2:9,4:2});
 if(side===1){for(const c of [whale,...Object.values(others).flat()]){const s=c.Snapshot();c.Move(1,s.locationMask,s.locationIndex);}g.match.currentPlayerId=1;}
 if(locked)whale.AddTokens(4);
 g.EndTurnWithEvents();const s=snap(g,whale);
 check(s.locationMask===(locked?1:4),'lock / owner turn '+side+'/'+locked);
 if(!locked)check(s.locationIndex===2,'jump appends after existing cards '+side);
}
{const {g,whale}=session(1,{2:9});g.match.currentPlayerId=1;g.EndTurnWithEvents();check(snap(g,whale).locationMask===1,'other player turn does not trigger whale');}
const report={checks,failures,records,fingerprint:rt.fingerprint,sourceAbility:'152403/228',sourceGraphSha256:require('crypto').createHash('sha256').update(JSON.stringify(graph)).digest('hex'),actualWitcherScript:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
