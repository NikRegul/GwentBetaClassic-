"""Run actual saved-profile WS with faults at facts write boundaries.

The inventory/game save serializer is a host substitute; this is not retail
serialization acceptance. Output directories must be fresh.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

import ws2js

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/classic132'))
from prepare_scripts import extract_annotations, read_source

EXTRA_READ_FILES=['collectionQuest.ws','profileCleanup090.ws']
NAMES = ['aaProfileStore.ws', 'collectionProfile.ws', 'deckProfile.ws', 'profileBackup.ws',
         'scrapsProfile.ws', 'kegProfile.ws']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--source', type=Path, help='Frozen profile source directory for before/after controls')
    parser.add_argument('--release', action='store_true', help='Require the exact frozen profile sources')
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        parser.error('Use a fresh output directory')
    source = args.source.resolve() if args.source else ROOT/'BetaGwent/development/scripts/game/betagwent'
    snapshot = args.snapshot.resolve()
    frozen = snapshot/'sources/BetaGwent/development/scripts/game/betagwent'
    profile_frozen = all((frozen/n).exists() and (source/n).read_bytes() == (frozen/n).read_bytes() for n in NAMES+EXTRA_READ_FILES)
    if args.release and not profile_frozen:
        parser.error('Storage checks must use the exact frozen release profile sources')
    # 0.9.4: Next-Gen keeps only the first 45 saved @addField properties of
    # W3PlayerWitcher across all mods. Beta Gwent may declare exactly the store.
    import re
    saved_fields=[]
    for path in sorted(source.glob('*.ws')):
        for m in re.finditer(r'@addField\(W3PlayerWitcher\)\s*(?:public|private|protected)?\s*saved\s+var\s+(\w+)',read_source(path)):
            saved_fields.append((path.name,m[1]))
    expected_store=[('aaProfileStore.ws',n) for n in ['betaGwentStore','betaGwentStoreText','betaGwentRewardActors','betaGwentRewardedQuests']]
    if saved_fields!=expected_store:
        raise SystemExit('Saved W3PlayerWitcher fields must be exactly the store: '+repr(saved_fields))
    out.mkdir(parents=True)
    globals_, members = [], []
    for name in NAMES:
        remaining, blocks = extract_annotations(read_source(source/name), name)
        globals_.append(remaining)
        for block in blocks:
            if block['kind'] == 'wrapMethod':
                continue  # Native gameplay-start dispatch is covered by native acceptance.
            if block['target'] != 'W3PlayerWitcher' and block['kind'] != 'wrapMethod':
                raise ValueError('Unexpected storage target: '+block['target'])
            members.append(block['text'].replace('private saved var', 'private var'))
    # Execute the real count getter while leaving native quest/timer commands mocked.
    _,quest_blocks=extract_annotations(read_source(source/'collectionQuest.ws'),'collectionQuest.ws')
    members += [b['text'] for b in quest_blocks if b.get('member')=='BetaGwentCollectionCount']
    _,cleanup_blocks=extract_annotations(read_source(source/'profileCleanup090.ws'),'profileCleanup090.ws')
    members += [b['text'] for b in cleanup_blocks if b.get('member')=='BetaGwentCleanupPending']
    wrapper = out/'profile.ws'
    wrapper.write_text('struct EntityHandle { var stableId : string; }\n'
                       'struct SItemUniqueId { var id : int; }\n'+
                       '\n'.join(globals_)+'\nclass W3PlayerWitcher extends IScriptable {\n'+
                       '\n'.join(members)+'''
 private var inv : IScriptable;
 private var betaGwentOpponentBag, betaGwentOpponentRecent : array<int>;
 private var betaGwentOpponentPoolSize : int;
 private var betaGwentCleanupPending090 : bool;
 public function BetaGwentUpdateCollectionProgress() {}
 public function BetaGwentSyncTournamentAccess() {}
}''', 'utf8')
    extra = list(source.glob('*.ws'))+list((ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws'))
    translated, _ = ws2js.build([wrapper, source/'duelCatalog.ws', source/'progressionCatalog.ws'], extra)
    host = '\n'.join((snapshot/n).read_text('utf8') for n in ['runtime.js', 'rules.js', 'harness.js'])
    checks = Path(__file__).with_suffix('.cjs').read_text('utf8')
    script = out/'checks.js'
    script.write_text(host+'\n(function(){\n'+translated+'\n'+checks+'\n})();\n', 'utf8')
    result = subprocess.run(['node', str(script)], cwd=ROOT, capture_output=True,
                            text=True, encoding='utf8', timeout=240)
    (out/'result.log').write_text(result.stdout+result.stderr, 'utf8')
    print((result.stdout+result.stderr)[-6500:])
    marker = 'SAVE_SAFETY094 '
    if marker in result.stdout:
        report = json.loads(result.stdout.split(marker, 1)[1])
        files = [source/n for n in NAMES+EXTRA_READ_FILES]+[Path(__file__), Path(__file__).with_suffix('.cjs')]
        report['sources'] = {str(p.resolve().relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        report['snapshotFingerprint'] = json.loads((snapshot/'manifest.json').read_text('utf8'))['fingerprint']
        report['profileSourcesFrozen'] = profile_frozen
        report['nativeSerializationTested'] = False
        report['savedPlayerFields'] = [name for _, name in saved_fields]
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', 'utf8')
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
