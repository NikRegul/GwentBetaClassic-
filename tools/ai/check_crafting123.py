"""Run the real menu craft event and save-profile WS with mocked engine/UI handles."""
from pathlib import Path
import json
import re
import subprocess
import sys

import ws2js

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'BetaGwent/development/scripts/game/betagwent'
snapshot = Path(sys.argv[1]).resolve()
out = ROOT / 'BetaGwent/build/crafting123'
out.mkdir(parents=True, exist_ok=True)


def function(text, name):
    match = re.search(r'(?:(?:private|public)\s+)?(?:function|event)\s+' + name + r'\(', text)
    if not match:
        raise ValueError(name)
    start = text.index('{', match.start())
    depth, end = 1, start + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end]


collection = (source / 'collectionProfile.ws').read_text('utf-8-sig')
scraps = (source / 'scrapsProfile.ws').read_text('utf-8-sig')
cap = function(collection, 'BetaGwentCollectionCap')
collection = collection.replace(cap, '')
globals_ = [function(scraps, name) for name in
            ('BetaGwentRareBronze', 'BetaGwentCardRarity', 'BetaGwentCraftCost', 'BetaGwentMillValue')]
for item in globals_:
    scraps = scraps.replace(item, '')
profile = collection + (source / 'deckProfile.ws').read_text('utf-8-sig') + scraps
profile = re.sub(r'@add(?:Field|Method)\(W3PlayerWitcher\)\s*', '', profile)
profile = profile.replace('private saved var', 'private var')
menu = (source / 'developmentBoardMenu.ws').read_text('utf-8-sig')
event = function(menu, 'OnBetaGwentCollectionCraft').replace('event ', 'public function ', 1)
event = event.replace('(id : int)', '(id : int) : bool', 1)
wrapper = out / 'crafting.ws'
wrapper.write_text('struct EntityHandle { var stableId : string; }\n' + cap + '\n' +
                   '\n'.join(globals_) + '\nclass W3PlayerWitcher extends IScriptable {\n' + profile + '''
 public function BetaGwentUpdateCollectionProgress() {}
 public function BetaGwentSyncTournamentAccess() {}
 public function BetaGwentKegPending() : bool { return false; }
}
class CraftMenu extends IScriptable {
 var configured, npcMatch, selectingDecks, deckDraft : bool;
 var refreshes, editorRefreshes : int;
 var status : string;
 private function PublishCollection() { refreshes += 1; }
 private function Publish(value : string) { editorRefreshes += 1; status = value; }
''' + event + '\n' + function(menu, 'CollectionStatus') + '\n}', 'utf8')
extra = list(source.glob('*.ws')) + list((ROOT / 'BetaGwent/scripts/game/betagwent').glob('*.ws'))
translated, _ = ws2js.build([wrapper, source / 'duelCatalog.ws', source / 'progressionCatalog.ws'], extra)
host = '\n'.join((snapshot / f).read_text('utf8') for f in ('runtime.js', 'rules.js', 'harness.js'))
checks = r'''
let thePlayer;
function player(){const p=new W3PlayerWitcher();
 p.BetaGwentKegPending=()=>false;p.BetaGwentUpdateCollectionProgress=()=>{};p.BetaGwentSyncTournamentAccess=()=>{};
 p.betaGwentCollectionSchema=1;p.betaGwentStarterSetRevision=BetaGwentStarterRevision();
 p.BetaGwentAddScraps(1160);return p;}
function menu(npc,editor){const m=new CraftMenu();m.configured=true;m.npcMatch=npc;m.selectingDecks=true;m.deckDraft=editor;return m;}
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
const leader=201743,bronze=132303;
check(BetaGwentDuelIsLeader(leader)&&BetaGwentCraftCost(leader)===800,'real leader definition and cost');
check(BetaGwentCollectionCap(bronze)===3&&BetaGwentCraftCost(bronze)===30,'real common bronze definition and cost');
for(const npc of [true,false])for(const editor of [false,true]){
 thePlayer=player();const m=menu(npc,editor),name=`${npc?'NPC pre-battle':'standalone'} ${editor?'editor':'collection'}`;
 check(m.OnBetaGwentCollectionCraft(leader)===true,name+' accepts leader craft event');
 check(thePlayer.BetaGwentOwned(leader)===1&&thePlayer.BetaGwentScraps()===360,name+' grants leader and charges exactly once');
 check(m.refreshes===1&&m.editorRefreshes===(editor?1:0),name+' refreshes ownership and preserves screen');
 check(!m.OnBetaGwentCollectionCraft(leader)&&thePlayer.BetaGwentScraps()===360,name+' duplicate leader does not charge');
 for(let i=0;i<3;i++)check(m.OnBetaGwentCollectionCraft(bronze),name+' crafts bronze copy '+(i+1));
 check(thePlayer.BetaGwentOwned(bronze)===3&&thePlayer.BetaGwentScraps()===270,name+' bronze copies and balance');
 check(!m.OnBetaGwentCollectionCraft(bronze)&&thePlayer.BetaGwentScraps()===270,name+' bronze cap does not charge');
}
thePlayer=player();thePlayer.betaGwentScraps=799;let m=menu(true,true);
check(!m.OnBetaGwentCollectionCraft(leader)&&thePlayer.BetaGwentOwned(leader)===0&&thePlayer.BetaGwentScraps()===799,'insufficient scraps do not grant or charge');
check(m.editorRefreshes===1&&m.status.length>0,'editor receives rejection status');
for(const npc of [true,false]){
 thePlayer=player();m=menu(npc,false);m.selectingDecks=false;
 check(!m.OnBetaGwentCollectionCraft(leader)&&thePlayer.BetaGwentScraps()===1160&&m.refreshes===0,'active battle rejects out-of-screen craft request');
}
thePlayer=player();m=menu(true,false);m.configured=false;
check(!m.OnBetaGwentCollectionCraft(leader)&&thePlayer.BetaGwentScraps()===1160,'unconfigured menu rejects craft');
thePlayer=player();m=menu(true,true);
check(!m.OnBetaGwentCollectionCraft(-1)&&thePlayer.BetaGwentScraps()===1160,'invalid card does not grant or charge');
console.log(JSON.stringify({stage:123,checks,actualMenuAndProfileWS:true,nativeMouseTested:false}));
'''
script = out / 'checks.js'
script.write_text(host + '\n(function(){\n' + translated + '\n' + checks + '\n})();\n', 'utf8')
result = subprocess.run(['node', str(script)], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
(out / 'result.txt').write_text(result.stdout + result.stderr, 'utf8')
print((result.stdout + result.stderr)[-6000:])
if result.returncode == 0:
    report = json.loads(result.stdout.strip().splitlines()[-1])
    (ROOT / 'docs/evidence/crafting123.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
raise SystemExit(result.returncode)
