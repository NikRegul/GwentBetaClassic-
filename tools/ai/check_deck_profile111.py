"""Execute the actual deck library/profile methods in the WS-to-JS host.

This checks storage and selection logic, not the engine's save serializer.
"""
from pathlib import Path
import argparse, re, subprocess, sys
import ws2js

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('snapshot', type=Path)
a = p.parse_args()
snapshot = a.snapshot.resolve()
source = snapshot/'sources/BetaGwent/development/scripts/game/betagwent'
out = ROOT/'BetaGwent/build/deck-profile111'
out.mkdir(parents=True, exist_ok=True)
profile = (source/'deckProfile.ws').read_text('utf-8-sig')
profile = re.sub(r'@add(?:Field|Method)\(W3PlayerWitcher\)\s*', '', profile)
profile = profile.replace('private saved var', 'private var')
(out/'profile.ws').write_text('class W3PlayerWitcher extends IScriptable {\n'+profile+'\n}', 'utf8')
library = (source/'deckBuilder.ws').read_text('utf-8-sig').split('class CBetaGwentDeckDraft', 1)[1]
(out/'library.ws').write_text('class CBetaGwentDeckDraft'+library, 'utf8')
extra = list(source.glob('*.ws')) + list((snapshot/'sources/BetaGwent/scripts/game/betagwent').glob('*.ws'))
translated, _ = ws2js.build([out/'profile.ws', out/'library.ws', source/'duelCatalog.ws', source/'progressionCatalog.ws'], extra)
host = '\n'.join((snapshot/f).read_text('utf8') for f in ('runtime.js', 'rules.js', 'harness.js'))
checks = r'''
function StrLen(value) { return value.length; }
function StrLeft(value, length) { return value.slice(0,length); }
let thePlayer = new W3PlayerWitcher();
thePlayer.BetaGwentEnsureCollection = () => {};
thePlayer.BetaGwentOwnsDeck = () => true;
function check(ok, label) { if (!ok) throw Error(label); console.log('PASS', label); }
function storeCustom(slot) {
    const cards = {v:[]}; BetaGwentDuelPresetDeck(16, cards);
    const leader = BetaGwentDuelPreset(16).leaderTemplateId;
    return thePlayer.BetaGwentStoreDeck(slot, cards.v, 'Original '+slot, BetaGwentDuelDefinition(leader).header.factionMask, leader);
}
for (let slot=1;slot<=8;slot++) check(storeCustom(slot), 'populate legacy custom slot '+slot);
const originalCustom = JSON.stringify(thePlayer.betaGwentDeckCards);
let library = new CBetaGwentDeckLibrary(); library.Initialize(false);
check(library.FirstEmpty()===0, 'all eight custom slots are occupied');
for (let id=16;id<=20;id++) {
    const draft = library.Edit(id);
    check(draft && draft.slot===id-7, 'starter '+id+' editable with no custom slot');
    const originalPresetTitle = BetaGwentDuelPreset(id).title;
    const name = 'Изменённая колода '+id;
    const gold = draft.cards.findIndex(card=>BetaGwentDuelDefinition(card).header.tierMask===8);
    check(gold>=0 && !draft.cards.includes(112101), 'starter has a gold slot available for replacement '+id);
    draft.cards[gold]=112101;
    check(library.Save(draft, name), 'save starter '+id+' directly');
    library = new CBetaGwentDeckLibrary(); library.Initialize(false);
    check(library.Get(id).title===name, 'reopen starter '+id+' with changed name');
    const own={v:[]}, ownLeader={v:0}, foe={v:[]}, foeLeader={v:0}, original={v:[]};
    check(library.Resolve(id, own, ownLeader), 'resolve edited starter '+id);
    check(own.v.includes(112101), 'reopened starter retains changed card composition '+id);
    check(library.ResolveOpponent(id, foe, foeLeader), 'opponent resolves its original preset '+id);
    BetaGwentDuelPresetDeck(id, original);
    check(JSON.stringify(foe.v)===JSON.stringify(original.v), 'opponent preset remains original '+id);
    check(BetaGwentDuelPreset(id).title===originalPresetTitle, 'global preset title is unchanged '+id);
}
check(JSON.stringify(thePlayer.betaGwentDeckCards)===originalCustom, 'starter edits preserve legacy custom cards');
check(library.Get(1001).title==='Original 1' && library.Get(1008).title==='Original 8', 'custom names and IDs preserved');
// Reject malformed/unknown starter schema without rewriting existing values.
thePlayer.betaGwentStarterDeckSchema=99;
const invalid=library.Edit(16);const before=JSON.stringify(thePlayer.betaGwentStarterDeckCards);
check(!library.Save(invalid, 'Rejected'), 'unknown starter schema is rejected');
check(JSON.stringify(thePlayer.betaGwentStarterDeckCards)===before, 'rejection does not overwrite saved starter cards');
'''
script = out/'checks.js'
script.write_text(host+'\n(function(){\n'+translated+'\n'+checks+'\n})();\n', 'utf8')
result = subprocess.run(['node', str(script)], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
(out/'result.txt').write_text(result.stdout+result.stderr, 'utf8')
print((result.stdout+result.stderr)[-6000:])
raise SystemExit(result.returncode)
