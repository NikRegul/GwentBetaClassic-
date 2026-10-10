"""Execute the saved opponent rotation after a mocked save/load roundtrip."""
from pathlib import Path
import re,sys,subprocess
import ws2js
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'BetaGwent/development/scripts/game/betagwent'
snapshot=Path(sys.argv[1]).resolve()
out=ROOT/'BetaGwent/build/rotation123';out.mkdir(parents=True,exist_ok=True)
text=(source/'opponentRotation.ws').read_text('utf-8-sig').split('function BetaGwentChooseDiversePreset()')[0]
text=re.sub(r'@add(?:Field|Method)\(W3PlayerWitcher\)\s*','',text).replace('private saved var','private var')
wrapper=out/'rotation.ws';wrapper.write_text('class W3PlayerWitcher extends IScriptable {\n'+text+'\n}',encoding='utf8')
translated,_=ws2js.build([wrapper,source/'duelAITuning.ws',source/'duelAICatalog.ws',source/'duelCatalog.ws'],list(source.glob('*.ws'))+list((ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws')))
host='\n'.join((snapshot/f).read_text('utf8') for f in ('runtime.js','rules.js','harness.js'))
checks=r'''
function BetaGwentPresetFaction(id){return BetaGwentDuelDefinition(BetaGwentDuelPreset(id).leaderTemplateId).header.factionMask;}
function RandRange(n){return Math.floor(Host.random()*n);}
Host.random=()=>.37;
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
let p=new W3PlayerWitcher(),previous=0;
for(let cycle=0;cycle<4;cycle++){
 let played=[];
 for(let i=0;i<46;i++){
  const next=p.BetaGwentNextOpponent();
  check(next>=54&&next<=99,'active pool');check(!played.includes(next),'no repeat before full cycle');
  check(previous!==next,'no cycle-boundary repeat');played.push(next);previous=next;
  if(i===16){const saved=JSON.parse(JSON.stringify(p));p=new W3PlayerWitcher();Object.assign(p,saved);}
 }
 check(new Set(played).size===46,'all 46 per cycle after save/load');
}
// Corrupt or obsolete bags recover to the current pool, never an invalid preset.
p.betaGwentOpponentBag=[1,1];check(p.BetaGwentNextOpponent()>=54,'obsolete bag recovers');
console.log(JSON.stringify({stage:123,checks,cycles:4,mockedSaveRoundtrip:true,nativeSaveTested:false}));
'''
bundle=out/'rotation.js';bundle.write_text(host+'\n(function(){\n'+translated+'\n'+checks+'\n})();',encoding='utf8')
result=subprocess.run(['node',str(bundle)],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
if result.returncode:raise SystemExit(result.returncode)
(ROOT/'docs/evidence/rotation123.json').write_text(result.stdout,encoding='utf8')
