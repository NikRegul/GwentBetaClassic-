"""Freeze old decision logic with the same researched decks/card effects as new AI."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
import build_js,gen_clone
from comparison_inputs import validate_snapshot, graft_policy
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('old',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--original091',action='store_true',help='Allow support classes introduced after original0.9.1, unreachable from its original decision/preparation entry points')
    a=p.parse_args()
    candidate=a.candidate.resolve();old=a.old.resolve();out=a.output.resolve()
    validate_snapshot(candidate);validate_snapshot(old)
    if out.exists() and any(out.iterdir()):raise ValueError('Use an empty comparison output directory')
    out.mkdir(parents=True,exist_ok=True)
    proof={};retained=[]
    for folder in ('core','dev'):
        src=candidate/'sources/BetaGwent'/('scripts' if folder=='core' else 'development/scripts')/'game/betagwent'
        shutil.copytree(src,out/folder)
    # Card rules, catalogue and all 46 compositions remain identical. Compare
    # the old decision procedure, archetype priorities and round economy.
    for name in ('duelSession.ws','duelArchetypeAI.ws','duelAIPass.ws','duelAICatalog.ws','duelAIResearch.ws','duelWeatherAI.ws','duelAIWorth.ws','duelAITuning.ws','duelPublicResponseAI.ws','duelAITraining.ws','duelReplyTreeAI.ws','duelStrategyAI.ws','duelEndgameAI.ws'):
        src=old/'sources/BetaGwent/development/scripts/game/betagwent'/name
        if not src.exists() and a.original091 and name in ('duelReplyTreeAI.ws','duelStrategyAI.ws','duelEndgameAI.ws'):
            retained.append(name);continue
        if name=='duelSession.ws':
            target=out/'dev'/name
            merged,methods=graft_policy(target.read_text('utf-8-sig'),src.read_text('utf-8-sig'))
            target.write_text(merged,'utf-8')
        else:shutil.copy2(src,out/'dev'/name)
        proof[name]=hashlib.sha256(src.read_bytes()).hexdigest()
    build_js.CORE=gen_clone.CORE=out/'core';build_js.DEV=gen_clone.DEV=out/'dev';gen_clone.OUT=out/'dev/duelClone.ws'
    gen_clone.patch_sources(gen_clone.program());gen_clone.gen(gen_clone.program());build_js.main(out/'rules.js')
    # Use exactly the same host, deal and seat adapter in both arms.
    for name in ('runtime.js','harness.js','manifest.json'):
        shutil.copy2(candidate/name,out/name)
    shutil.copy2(old/'tunes.json',out/'tunes.json')
    record={'schema':1,'candidate':str(candidate),'oldSnapshot':str(old),'baselineAI':proof,
            'sameDeckCatalogue':hashlib.sha256((out/'dev/duelCatalog.ws').read_bytes()).hexdigest(),
            'baselineRules':hashlib.sha256((out/'rules.js').read_bytes()).hexdigest(),
            'sessionPolicyMethods':methods,'sharedBattleMechanics':True,'retainedCompatibilitySupport':retained,'original091':a.original091}
    (out/'comparison.json').write_text(json.dumps(record,indent=2),'utf-8')
    print('Prepared baseline with identical researched decks:',out)
if __name__=='__main__':main()
