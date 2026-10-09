"""Compile Stage113 drafts to JS without altering the active REDkit sources."""
from pathlib import Path
import shutil,sys
sys.path.insert(0,str(Path(__file__).parent))
import build_js,gen_clone
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/stage113/preview'
for kind,source in [('core',build_js.CORE),('dev',build_js.DEV)]:
    dest=BASE/kind;dest.mkdir(parents=True,exist_ok=True)
    for p in source.glob('*.ws'):shutil.copy2(p,dest/p.name)
if 'public function AiReverseClone()' not in (build_js.DEV/'duelSession.ws').read_text('utf-8-sig'):
    for name in ('duelSession.ws','duelPublicResponseAI.ws'):
        shutil.copy2(ROOT/'BetaGwent/build/stage113/draft'/name,BASE/'dev'/name)
build_js.CORE=BASE/'core';build_js.DEV=BASE/'dev';build_js.NAMES+=[] if 'duelPublicResponseAI' in build_js.NAMES else ['duelPublicResponseAI']
gen_clone.CORE=build_js.CORE;gen_clone.DEV=build_js.DEV;gen_clone.OUT=build_js.DEV/'duelClone.ws'
p=gen_clone.program();gen_clone.patch_sources(p);gen_clone.gen(gen_clone.program())
build_js.main(BASE/'rules.js')
for name in ('runtime.js','harness.js'):shutil.copy2(ROOT/'tools/ai/jshost'/name,BASE/name)
print(BASE)
