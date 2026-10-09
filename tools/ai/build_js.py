from pathlib import Path
import sys, re
sys.path.insert(0, str(Path(__file__).parent))
import ws2js
ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT/'BetaGwent/scripts/game/betagwent'
DEV = ROOT/'BetaGwent/development/scripts/game/betagwent'
NAMES = ['duelClone','duelPublicResponseAI','duelAIWorth','duelAICatalog','duelAIResearch','duelAIPass','duelAITuning','duelArchetypeAI','duelCatalog','duelEffectRuntime','duelEvents','duelLiveCard','duelMonsterDuel','duelMonsters','duelNeutral','duelNilf','duelNilfDependencies','duelNorth','duelScoia','duelSession','duelSkellige','duelSpecials','duelVisualFrame','duelWeather','duelWeatherAI','developmentRequestFlow','duelAITraining']
def main(out):
    files = sorted(CORE.glob('*.ws')) + [DEV/(n+'.ws') for n in NAMES if (DEV/(n+'.ws')).exists()]
    # deckBuilder: first two blocks only (as the C# host does)
    db = (DEV/'deckBuilder.ws').read_text(encoding='utf-8-sig'); blocks = ws2js.split_blocks(db)[:2]
    tmp = Path(out).parent/'_deckBuilder_head.ws'
    src = db
    # rebuild text of first two blocks
    end = blocks[1][-1].pos + 1
    tmp.write_text(db[:end], encoding='utf-8')
    files.append(tmp)
    extra = sorted(DEV.glob('*.ws')) + sorted(CORE.glob('*.ws'))
    js, prog = ws2js.build(files, extra, excluded_functions={'BetaGwentAITune','BetaGwentAIStrength','BetaGwentAIChooseOrdinaryPreset','BetaGwentAIRandomPreset'})
    # Keep the real exported weights as the default. Training can still supply
    # Host.policy explicitly; acceptance comparisons must not silently use zero.
    js=js.replace('function BetaGwentAITrainingWeight(', 'function __snapshotTrainingWeight(')
    Path(out).write_text(js, encoding='utf-8'); tmp.unlink()
    print('ok', len(js)//1024, 'KB', len(prog.classes), 'classes', len(prog.functions), 'functions')
if __name__ == '__main__': main(sys.argv[1])
