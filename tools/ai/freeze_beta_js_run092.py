"""Freeze direct JS policy code and a technical cross-policy coverage schedule."""
from pathlib import Path
import argparse, hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[2]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('config',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--kind',choices=['technical','paired'],default='technical');a=ap.parse_args()
    out=a.out.resolve()
    if out.exists():raise ValueError('Use a new experiment folder')
    config=json.loads(a.config.read_text('utf8'))
    for k in ('current','original091','policy091','originalRosters'):config[k]=str((ROOT/config[k]).resolve())
    out.mkdir(parents=True);frozen=out/'frozen';files={}
    sources=list((ROOT/'tools/ai/beta_js092').rglob('*'))
    sources += [ROOT/'tools/ai'/n for n in ('comparison_bridge119.js','versioned_match092.js','variant_decks092.js','run_beta_js_schedule092.cjs')]
    for src in sources:
        if not src.is_file() or '__pycache__' in src.parts:continue
        rel=src.relative_to(ROOT);target=frozen/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target);files[rel.as_posix()]=sha(target)
    # The source asset audit is copied as an input, never regenerated in a run.
    shutil.copy2(config['originalRosters'],out/'original-rosters.json');config['originalRosters']=str(out/'original-rosters.json')
    original=json.loads((out/'original-rosters.json').read_text('utf8'))['eligible']
    manifest=json.loads((Path(config['current'])/'manifest.json').read_text('utf8'))
    presets=manifest['presets'];beta=['beta092:'+str(i) for i in presets]+['betaOriginal:'+d['asset'] for d in original]
    schedule=[]
    for i,key in enumerate(beta):
        opponent=('091' if i%2 else '092')+':'+str(presets[(i*17+7)%len(presets)])
        for mirror in (0,1):
            left,right=(key,opponent) if not mirror else (opponent,key)
            schedule.append(dict(id=f'technical-{i:03d}-{mirror}',left=left,right=right,seed=924025001+i))
    if a.kind=='paired':
        groups={'091':['091:'+str(i) for i in presets],'092':['092:'+str(i) for i in presets],
                'beta092':['beta092:'+str(i) for i in presets],'betaOriginal':['betaOriginal:'+d['asset'] for d in original]}
        names=list(groups);schedule=[]
        # Two independently rotated fixed grids, each with mirrored seats and
        # identical pair seeds.45-vs46 includes one repeated original asset per
        # grid; record per-entrant exposure and report deck-weighted summaries.
        for grid in (0,1):
            for ai in range(len(names)):
                for bi in range(ai+1,len(names)):
                    lefts,rights=groups[names[ai]],groups[names[bi]]
                    for i in range(max(len(lefts),len(rights))):
                        left=lefts[i%len(lefts)];right=rights[(i+grid*13+ai*3+bi*7)%len(rights)]
                        seed=924030001+grid*10000+ai*1000+bi*100+i
                        for mirror in (0,1):
                            x,y=(left,right) if not mirror else (right,left)
                            schedule.append(dict(id=f'grid{grid}-{names[ai]}-{names[bi]}-{i:02d}-{mirror}',left=x,right=y,seed=seed,grid=grid,pair=f'{names[ai]}-{names[bi]}-{i:02d}'))
    plan=dict(schema=1,kind='paired-four-group-tournament' if a.kind=='paired' else 'technical-cross-policy-coverage',ratingPermitted=a.kind=='paired',config=config,schedule=schedule,
              groups={'091':46,'092':46,'beta092':46,'betaOriginal':len(original)},codeFiles=files,
              commonFingerprint=manifest['fingerprint'],commonManifestSha256=sha(Path(config['current'])/'manifest.json'),
              policyProofSha256=sha(Path(config['policy091'])/'comparison.json'),originalRostersSha256=sha(out/'original-rosters.json'),
              informationAsymmetry='Beta sees full hands/decks;091/092 preserve original information restrictions',
              sourceSearchBudget='Original Practice depth1/maxTime3 plus module force-fetch grace1s; host wall clock',
              mutationLimitPerBetaCallback=1,stopOnTechnicalError=True)
    (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (out/'games').mkdir();print(json.dumps({'out':str(out),'games':len(schedule),'planSha256':sha(out/'plan.json')}))

if __name__=='__main__':main()
