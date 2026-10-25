"""Execute current saved-profile WS with real catalog/library and faulted facts.

Models serialization loss/interruption; never claims retail save serialization.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys
import ws2js

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--source', type=Path, help='Alternative frozen WS sources for negative controls')
    parser.add_argument('--negative-control', action='store_true')
    parser.add_argument('--release', action='store_true', help='Require profile code to be identical to frozen release sources')
    args = parser.parse_args()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    source = args.source.resolve() if args.source else ROOT/'BetaGwent/development/scripts/game/betagwent'
    names = ['deckProfile.ws','profileBackup.ws','collectionProfile.ws','deckBuilder.ws','profileCleanup090.ws']
    frozen = args.snapshot/'sources/BetaGwent/development/scripts/game/betagwent'
    profile_frozen = all((source/n).read_bytes() == (frozen/n).read_bytes() for n in names)
    if args.release:
        assert profile_frozen, 'Storage checks must use the exact frozen release profile sources'
    collection = (source/'collectionProfile.ws').read_text('utf-8-sig')
    cap = re.search(r'function BetaGwentCollectionCap\(.*?\n}\n', collection, re.S).group()
    collection = collection.replace(cap, '')
    backup = (source/'profileBackup.ws').read_text('utf-8-sig')
    first_field = re.search(r'^@addField', backup, re.M).start()
    structs, backup = backup[:first_field], backup[first_field:]
    profile = collection+(source/'deckProfile.ws').read_text('utf-8-sig')+backup
    profile = re.sub(r'@add(?:Field|Method)\(W3PlayerWitcher\)\s*', '', profile).replace('private saved var', 'private var')
    wrapper = out/'profile.ws'
    wrapper.write_text('struct EntityHandle { var stableId : string; }\n'+structs+'\n'+cap+'\nclass W3PlayerWitcher extends IScriptable {\n'+profile+'''
 private var betaGwentScraps, betaGwentKegsUnopened : int;
 private var betaGwentKegAutomatic, betaGwentKegOffers, betaGwentKegAutomaticScraps : array<int>;
 private var betaGwentOpponentBag, betaGwentOpponentRecent : array<int>;
 public function BetaGwentCleanupPending() : bool { return false; }
 public function BetaGwentUpdateCollectionProgress() {}
 public function BetaGwentSyncTournamentAccess() {}
 public function BetaGwentKegPending() : bool { return false; }
 public function BetaGwentAddScraps(value : int) {}
 public function BetaGwentScraps() : int { return 0; }
 public function BetaGwentReceive(id : int) : int { return 0; }
}''', 'utf8')
    library = out/'library.ws'
    library.write_text((source/'deckBuilder.ws').read_text('utf-8-sig').split('// Saved AI difficulty',1)[0], 'utf8')
    extra = list(source.glob('*.ws'))+list((ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws'))
    translated, _ = ws2js.build([wrapper,library,source/'duelCatalog.ws',source/'progressionCatalog.ws'], extra)
    host = '\n'.join((args.snapshot/n).read_text('utf8') for n in ['runtime.js','rules.js','harness.js'])
    checks = Path(__file__).with_suffix('.cjs').read_text('utf8')
    if args.negative_control:
        checks = checks.split('let p=player();',1)[0]+'''
let p=player();const fresh=load(p,1);p=rich();const original=load(p,1).cards.slice();
const cur=facts.get('bg_b2_cur'),prefix='bg_b2_'+cur+'_d1_',alternate=deck(17);
facts.set(prefix+'n',alternate.cards.length);facts.set(prefix+'f',alternate.faction);facts.set(prefix+'l',alternate.leader);
alternate.cards.forEach((id,i)=>facts.set(prefix+i,id));facts.set('bg_b2_'+cur+'_sa',-1);
p.betaGwentDeckCards=[];const poisoned=load(p,1);
check(fresh.ok,'old empty profile incorrectly claims a valid deck');
check(S(poisoned.cards)!==S(original),'old repair trusts a modified bank with bad checksum');
console.log('REPORT198 '+S({complete:true,checks,negativeControl:true,observedEmptyLoadBug:fresh.ok,observedUncheckedBankBug:true,nativeSerializationTested:false}));
'''
    script = out/'checks.js';script.write_text(host+'\n(function(){\n'+translated+'\n'+checks+'\n})();\n','utf8')
    result = subprocess.run(['node',str(script)],cwd=ROOT,capture_output=True,text=True,encoding='utf8',timeout=180)
    (out/'result.log').write_text(result.stdout+result.stderr,'utf8')
    print((result.stdout+result.stderr)[-5000:])
    if result.returncode:raise SystemExit(result.returncode)
    report = json.loads(result.stdout.split('REPORT198 ',1)[1])
    report['profileSourcesFrozen'] = profile_frozen
    report['fingerprint'] = json.loads((args.snapshot/'manifest.json').read_text('utf8'))['fingerprint']
    cleanup=(source/'profileCleanup090.ws').read_text('utf-8-sig')
    recovery_fields=re.findall(r'private saved var (betaGwentDeckRecovery\w*)\s*:',(source/'deckProfile.ws').read_text('utf-8-sig'))
    for field in recovery_fields:assert re.search(r'\b'+field+r'\s*(?:=\s*0|\.Clear\(\))',cleanup),field
    report['explicitUninstallClearsRecoveryFields']=len(recovery_fields)
    report['sources']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [source/n for n in names]+[Path(__file__).resolve(),Path(__file__).with_suffix('.cjs').resolve()]}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n','utf8')

if __name__ == '__main__':main()
