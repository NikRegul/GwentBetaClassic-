"""Translate each actual native-prepared ruleset for platform smoke coverage.

This remains a JS stand. It does not execute cards inside either retail game.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, shutil

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared',type=Path);parser.add_argument('snapshot',type=Path);parser.add_argument('out',type=Path)
    args=parser.parse_args();out=args.out.resolve();assert not out.exists(),'Fresh output required'
    sources={'nextgen':args.prepared/'scripts/game/betagwent','classic':args.prepared/'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts/game/betagwent'}
    records=[]
    for platform,origin in sources.items():
        target=out/platform;core=target/'sources/core';dev=target/'sources/development';core.mkdir(parents=True);dev.mkdir()
        entries={}
        for p in sorted(origin.glob('*.ws')):
            raw=p.read_bytes();text=raw.decode('utf16' if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8-sig')
            (dev/p.name).write_text(text,'utf8');entries[str(p.resolve())]=sha(p)
        for p in (ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws'):
            shutil.copyfile(dev/p.name,core/p.name)
        spec=importlib.util.spec_from_file_location('platform198_'+platform,ROOT/'tools/ai/build_js.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.CORE=core;module.DEV=dev;module.main(target/'rules.js')
        for name in ['runtime.js','harness.js','tunes.json']:shutil.copyfile(args.snapshot/name,target/name)
        identity=hashlib.sha256(json.dumps(entries,sort_keys=True).encode()).hexdigest()
        payload={p.relative_to(target).as_posix():sha(p) for p in target.rglob('*') if p.is_file()}
        manifest=dict(schema=2,fingerprint=identity,snapshotFiles=payload,platform=platform,sourceInputs=entries,nativeGameplayExecuted=False,scope='JS translation of actual native-prepared rules, not in-game execution')
        (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8');records.append(dict(platform=platform,fingerprint=identity,files=len(entries)))
    (out/'preparation.json').write_text(json.dumps(records,indent=2)+'\n','utf8');print(json.dumps(records))

if __name__=='__main__':main()
