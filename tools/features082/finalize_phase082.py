"""Correct the own-row first-tick phase before freezing the final candidate."""
from pathlib import Path
import sys,shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release082-polish2'
def main():
    for folder in [BUILD/'scripts/game/betagwent',ROOT/'BetaGwent/development/scripts/game/betagwent']:
        p=folder/'duelWeather.ws';s=p.read_text('utf-8-sig')
        assert s.count('            if(k>0)ForecastTurnEnd(cards);')==1
        s=s.replace('var s : SBetaGwentCardSnapshot;\n        game.GetZoneCards(side,row,live);','var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;\n        game.GetZoneCards(side,row,live);')
        s=s.replace('        previous=ForecastScore(cards);total=previous*10;','        m=game.Snapshot();previous=ForecastScore(cards);total=previous*10;')
        s=s.replace('            if(k>0)ForecastTurnEnd(cards);','            if(k>0 || (m.currentPlayerId==side && m.turnActive))ForecastTurnEnd(cards);')
        p.write_bytes(b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8'))
    sys.path.insert(0,str(ROOT/'tools/classic132'));from prepare_scripts import prepare
    adir=BUILD/'classic-phase-audit';old=BUILD/'classic-audit';audit=json.loads((old/'audit.json').read_text('utf8'))
    shutil.copytree(old/'baseline/vanilla-targets',adir/'baseline/vanilla-targets');shutil.copytree(BUILD/'scripts',adir/'baseline/scripts')
    audit['sourceScripts']={p.relative_to(BUILD/'scripts').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (BUILD/'scripts').rglob('*.ws')}
    (adir/'audit.json').write_text(json.dumps(audit,indent=2),'utf8');prepare(adir,BUILD/'classic-phase-prepared')
    print('Own-row forecast phase corrected; fresh native compilation required')
if __name__=='__main__':main()
