"""Translate the actual RNG once, then check vectors, bounded arithmetic and fallback."""
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js
source=ROOT/'BetaGwent/scripts/game/betagwent/randomGenerator.ws'
js,_=ws2js.build([source],[source])
out=ROOT/'BetaGwent/drafts/day-iteration-20261023/classic132-rng-regression/portable-rng.js'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text((ROOT/'tools/ai/jshost/runtime.js').read_text()+'\n'+js+'\n'
               'module.exports={CBetaGwentRandomGenerator,BetaGwentLogicalShift,BetaGwentRngShiftLeft,BetaGwentRngSeedMultiply,Host};\n',encoding='utf-8')
subprocess.run(['node',str(ROOT/'tools/ai/check_portable_rng092.cjs')],cwd=ROOT,check=True)
