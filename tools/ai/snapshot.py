"""Freeze the complete training input; never edit game scripts from a training run."""
import argparse, hashlib, json, re, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def inputs():
    paths = list((ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws'))
    paths += list((ROOT/'BetaGwent/development/scripts/game/betagwent').glob('*.ws'))
    paths += list((ROOT/'tools/ai/jshost').glob('*.js'))
    paths += [ROOT/'tools/ai'/n for n in ('snapshot.py','build_js.py','ws2js.py','gen_clone.py')]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

def fingerprint(files):
    return hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def verify(directory):
    m=json.loads((directory/'manifest.json').read_text('utf8'))
    if m['schema']!=2 or m['fingerprint']!=fingerprint(inputs()):
        raise ValueError('Training inputs changed; start a new output folder instead of Resume')
    for name,digest in m['snapshotFiles'].items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Snapshot was modified: '+name)
    return m

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--resume',action='store_true');a=p.parse_args()
    directory=a.directory.resolve()
    if a.resume:
        print('verified snapshot',verify(directory)['fingerprint']);return
    if directory.exists() and any(directory.iterdir()):raise ValueError('Snapshot folder must be empty')
    before=inputs();directory.mkdir(parents=True,exist_ok=True)
    for name in before:
        target=directory/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    for source in (ROOT/'tools/ai/jshost').glob('*.js'):shutil.copy2(source,directory/source.name)
    # Compile only the frozen copies, including the translator.
    import importlib.util
    spec=importlib.util.spec_from_file_location('frozen_build',directory/'sources/tools/ai/build_js.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.main(directory/'rules.js')
    ws=(directory/'sources/BetaGwent/development/scripts/game/betagwent/duelAIPass.ws').read_text('utf-8-sig')
    block=ws.split('function BetaGwentAITune(',1)[1].split('// Average public value',1)[0]
    defaults={k:int(v) for k,v in re.findall(r'case (\d+): return (-?\d+);',block)}
    runtime=directory/'runtime.js';code=runtime.read_text('utf8')
    code,n=re.subn(r'const __tuneDefaults = \{[^}]*\};','const __tuneDefaults = '+json.dumps(defaults)+';',code)
    if n!=1:raise ValueError('Runtime tune table missing')
    runtime.write_text(code,'utf8');(directory/'tunes.json').write_text(json.dumps(defaults,indent=2),'utf8')
    if before!=inputs():raise ValueError('Sources changed while freezing; discard this snapshot')
    frozen={p.relative_to(directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.rglob('*')) if p.is_file()}
    catalog=(directory/'sources/BetaGwent/development/scripts/game/betagwent/duelAICatalog.ws').read_text('utf-8-sig')
    mapping=catalog.split('function BetaGwentAIPresetProfile(',1)[1].split('\n}',1)[0]
    pool=sorted(int(i) for i in re.findall(r'case (\d+): return \d+;',mapping))
    if len(pool)!=46 or len(set(pool))!=46:raise ValueError('Frozen pool must contain all 46 researched profiles')
    manifest={'schema':2,'fingerprint':fingerprint(before),'files':before,'snapshotFiles':frozen,'presets':pool}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2),'utf8');print('snapshot',manifest['fingerprint'])

if __name__=='__main__':main()
