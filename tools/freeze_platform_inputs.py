"""Freeze final release UI sources/assets for subsequent platform builds."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


# Compiler support classes that live in subpackages of ui/src (not stage
# sources): the mx.core.BitmapAsset embed carrier. Without it Classic menus
# fail with "The definition of base class BitmapAsset was not found".
SUPPORT=('mx',)


def support_files(src):
    return {p.relative_to(src).as_posix():sha(p) for d in SUPPORT for p in sorted((src/d).rglob('*')) if p.is_file()}


def pin_support(out,saved=None):
    live=ROOT/'BetaGwent/ui/src';expected=support_files(live)
    if not expected:raise RuntimeError('UI support classes are missing from BetaGwent/ui/src')
    if saved is not None and 'support' in saved:expected=saved['support']
    for name,digest in expected.items():
        target=out/'src'/name
        if not target.is_file():
            source=live/name
            if not source.is_file() or sha(source)!=digest:raise RuntimeError('Pinned UI support class unavailable: '+name)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        if sha(target)!=digest:raise RuntimeError('Pinned UI support class changed: '+name)
    return expected


def freeze(stage):
    record=json.loads((ROOT/f'docs/evidence/stage{stage}-completion.json').read_text('utf8'))
    out=ROOT/f'BetaGwent/build/stage{stage}/common/ui'
    if out.exists():
        saved=json.loads((out/'inputs.json').read_text('utf8'))
        if saved['sources']!=record['sources']:raise RuntimeError('Pinned UI stage mismatch')
        for name,digest in saved['sources'].items():
            if sha(out/'src'/name)!=digest:raise RuntimeError('Pinned UI source changed: '+name)
        for name,digest in saved['assets'].items():
            if sha(out/'assets'/name)!=digest:raise RuntimeError('Pinned UI asset changed: '+name)
        if 'support' not in saved:
            # Snapshots made before support pinning: add the classes once.
            saved['support']=pin_support(out)
            (out/'inputs.json').write_text(json.dumps(saved,indent=2)+'\n','utf8')
        else:pin_support(out,saved)
        return out
    candidates=[ROOT/'BetaGwent/ui/src',*sorted((ROOT/'tmp').glob('backup*/BetaGwent/ui/src'),reverse=True)]
    selected={}
    for name,digest in record['sources'].items():
        source=next((p/name for p in candidates if (p/name).is_file() and sha(p/name)==digest),None)
        if source is None:raise RuntimeError('Frozen UI source unavailable: '+name)
        selected[name]=source
    assets=ROOT/'BetaGwent/ui/assets'
    before={p.relative_to(assets).as_posix():sha(p) for p in sorted(assets.rglob('*')) if p.is_file()}
    (out/'src').mkdir(parents=True)
    for name,source in selected.items():shutil.copy2(source,out/'src'/name)
    shutil.copytree(assets,out/'assets')
    after={p.relative_to(out/'assets').as_posix():sha(p) for p in sorted((out/'assets').rglob('*')) if p.is_file()}
    if before!=after or before!={p.relative_to(assets).as_posix():sha(p) for p in sorted(assets.rglob('*')) if p.is_file()}:raise RuntimeError('Assets changed during snapshot')
    if {p.name:sha(p) for p in (out/'src').glob('*.as')}!=record['sources']:raise RuntimeError('UI copy changed')
    support=pin_support(out)
    (out/'inputs.json').write_text(json.dumps(dict(stage=stage,sources=record['sources'],assets=after,support=support,sourceOrigins={n:str(p) for n,p in selected.items()},
        pixelAuthority='Frozen release resources; compilation assets provide embed linkage only'),indent=2)+'\n','utf8')
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',type=int,required=True)
    print(freeze(parser.parse_args().stage))
