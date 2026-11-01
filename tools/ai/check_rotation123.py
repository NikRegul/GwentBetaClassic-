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
# This isolated rotation test does not load the complete profile-store subsystem.
# Model its contract explicitly: readiness gates mutation, commit captures only
# the persisted rotation; the roundtrip below restores that committed snapshot.
store_contract='''
private var rotationTestReady : bool;
private var rotationTestCommits : int;
private var rotationTestSavedBag : array<int>;
private var rotationTestSavedRecent : array<int>;
private var rotationTestSavedPoolSize : int;
public function BetaGwentStoreReady() : bool { return rotationTestReady; }
public function BetaGwentStoreCommit() : bool
{
    if (!rotationTestReady) return false;
    rotationTestSavedBag = betaGwentOpponentBag;
    rotationTestSavedRecent = betaGwentOpponentRecent;
    rotationTestSavedPoolSize = betaGwentOpponentPoolSize;
    rotationTestCommits += 1;
    return true;
}
'''
wrapper=out/'rotation.ws';wrapper.write_text('class W3PlayerWitcher extends IScriptable {\n'+store_contract+text+'\n}',encoding='utf8')
translated,_=ws2js.build([wrapper,source/'duelAITuning.ws',source/'duelAICatalog.ws',source/'duelCatalog.ws'],list(source.glob('*.ws'))+list((ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws')))
host='\n'.join((snapshot/f).read_text('utf8') for f in ('runtime.js','rules.js','harness.js'))
checks=r'''
function BetaGwentPresetFaction(id){return BetaGwentDuelDefinition(BetaGwentDuelPreset(id).leaderTemplateId).header.factionMask;}
function RandRange(n){return Math.floor(Host.random()*n);}
Host.random=()=>.37;
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
let p=new W3PlayerWitcher(),previous=0;
p.rotationTestReady=true;
let commits=0,roundtrips=0;
function savedRotation(p){return JSON.stringify({bag:p.rotationTestSavedBag,recent:p.rotationTestSavedRecent,pool:p.rotationTestSavedPoolSize});}
function workingRotation(p){return JSON.stringify({bag:p.betaGwentOpponentBag,recent:p.betaGwentOpponentRecent,pool:p.betaGwentOpponentPoolSize});}
function roundtrip(p){
 const saved=JSON.parse(savedRotation(p));const q=new W3PlayerWitcher();q.rotationTestReady=true;
 q.betaGwentOpponentBag=saved.bag;q.betaGwentOpponentRecent=saved.recent;q.betaGwentOpponentPoolSize=saved.pool;
 check(workingRotation(q)===workingRotation(p),'roundtrip restores committed rotation');roundtrips++;return q;
}
let activeOut={v:[]};BetaGwentAIOrdinaryPresets(activeOut);let active=activeOut.v;
check(active.length===new Set(active).size,'unique active pool');
for(let cycle=0;cycle<4;cycle++){
 let played=[];
 for(let i=0;i<active.length;i++){
  const before=p.rotationTestCommits;
  const next=p.BetaGwentNextOpponent();
  check(p.rotationTestCommits===before+1,'allowed selection commits exactly once');commits++;
  check(savedRotation(p)===workingRotation(p),'commit preserves bag recent and pool size');
  check(active.includes(next),'active pool');check(!played.includes(next),'no repeat before full cycle');
  check(previous!==next,'no cycle-boundary repeat');played.push(next);previous=next;
  if(i===16)p=roundtrip(p);
 }
 check(new Set(played).size===active.length,'all active decks per cycle after save/load');
}
// A rejected/unknown store must not consume the bag or record a recent choice.
p.rotationTestReady=false;
const blockedWorking=workingRotation(p),blockedSaved=savedRotation(p),blockedCommits=p.rotationTestCommits;
check(p.BetaGwentNextOpponent()===54,'blocked profile returns fallback');
check(workingRotation(p)===blockedWorking,'blocked profile preserves bag recent and pool size');
check(p.rotationTestCommits===blockedCommits,'blocked profile never commits');
check(savedRotation(p)===blockedSaved,'blocked profile preserves committed rotation');
p.rotationTestReady=true;
// Corrupt or obsolete bags recover to the current pool, never an invalid preset.
p.betaGwentOpponentBag=[1,1];check(p.BetaGwentNextOpponent()>=54,'obsolete bag recovers');
p.betaGwentOpponentBag=[54,55];p.betaGwentOpponentPoolSize=46;
if(active.length!=46){p.BetaGwentNextOpponent();check(p.betaGwentOpponentBag.length===active.length-1,'expanded pool migrates old valid partial bag');}
console.log(JSON.stringify({stage:123,checks,pool:active.length,cycles:4,mockedSaveRoundtrip:true,mockedRoundtrips:roundtrips,allowedCycleCommits:commits,storeContractMocked:true,blockedStorePreserved:true,nativeSaveTested:false}));
'''
bundle=out/'rotation.js';bundle.write_text(host+'\n(function(){\n'+translated+'\n'+checks+'\n})();',encoding='utf8')
result=subprocess.run(['node',str(bundle)],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
if result.returncode:raise SystemExit(result.returncode)
(ROOT/'docs/evidence/rotation123.json').write_text(result.stdout,encoding='utf8')
