"""Prepare a new 0.8.2 AI candidate without changing the accepted release."""
from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/release082-final'
BUILD=ROOT/'BetaGwent/build/release082-ai1'
DEV=ROOT/'BetaGwent/development/scripts/game/betagwent'
def read(p):return p.read_text('utf-8-sig')
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
def replace(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b)
def patch(name,s):
    if name=='duelWeather.ws':
        fragment=read(ROOT/'tools/features082/ai_row_forecast.ws')
        s=replace(s,'    public function ClearRowForecast(side : int, row : int) : int',fragment+'\n    public function ClearRowForecast(side : int, row : int) : int')
        s=replace(s,'        if(ticks==0 || token==0 || (token&384)!=0 || token==512 || token==2048)return 0;',
            '        if(ticks==0 || token==0 || (token&384)!=0 || token==512 || token==2048)return 0;\n        if(token==64)return ForecastTokenLoss(side,row,token,ticks);')
    if name=='duelSession.ws':
        fragment=read(ROOT/'tools/features082/ai_row_choice.ws')
        s=replace(s,'    public function MonsterRequest(source : CBetaGwentDuelCard, ids : array<int>, kind : int, minimum : int, maximum : int)',fragment+'\n    public function MonsterRequest(source : CBetaGwentDuelCard, ids : array<int>, kind : int, minimum : int, maximum : int)')
        s=replace(s,'var m : SBetaGwentMatchSnapshot; var i, best, value, score, rowSide : int; var card : CBetaGwentDuelCard;',
            'var m : SBetaGwentMatchSnapshot; var i, best, value, score, rowSide, bestSide, candidateSide : int; var card : CBetaGwentDuelCard;')
        s=replace(s,'        score = -2147483647; best = ids[0];','        score = -2147483647; best = ids[0]; bestSide=rowSide;')
        s=replace(s,'            else if (kind == 3) value = CountLocation(rowSide, ids[i]);',
            '''            else if (kind == 3) {
                for(candidateSide=1;candidateSide<=2;candidateSide+=1){
                    if(SpecialRowMode()!=1 && candidateSide!=rowSide)continue;
                    value=AiRowAbilityValue(source,candidateSide,ids[i]);
                    AiExplain("ROW_OPTION","source="+source.TemplateId()+" side="+candidateSide+" row="+ids[i]+" value="+value);
                    if(value>score){score=value;best=ids[i];bestSide=candidateSide;}
                }
                continue;
            }''')
        s=replace(s,'        if (kind == 3) monsters.Row(source, rowSide, best); else monsters.Select(source, best);',
            '        if (kind == 3) monsters.Row(source, bestSide, best); else monsters.Select(source, best);')
        s=replace(s,'        if(d.effect!=34)return 0;\n        if(id==162205)',
            '''        if(d.effect!=34)return 0;
        if(id==152105){
            if(immediate)return 0;
            for(i=1;i<=4;i*=2)value=Max(value,weather.ForecastTokenLoss(enemy,i,64,AiWeatherTicks(side))-weather.ForecastTokenLoss(enemy,i,weather.Token(enemy,i),AiWeatherTicks(side)));
            return value;
        }
        if(id==162205)''')
        s=replace(s,'        count = CountLocation(enemy, row);\n        for (i = 0; i < live.Size(); i += 1)',
            '''        count = CountLocation(enemy, row);
        if(token==64 && count>0)return (weather.ForecastTokenLoss(enemy,row,token,ticks)-weather.ForecastTokenLoss(enemy,row,weather.Token(enemy,row),ticks))*BetaGwentAITune(11)/10;
        for (i = 0; i < live.Size(); i += 1)''')
        s=replace(s,'        if(s.positionPlayerId==side || s.power.currentPower>Max(0,amount-s.power.armor))return value;',
            '''        if(s.positionPlayerId!=side && (s.tokenMask&4)==0 && s.power.armor>0 && amount>=s.power.armor && s.power.currentPower>Max(0,amount-s.power.armor)){
            if(s.runtimeTemplate.templateId==122317)value-=5;
            if(!immediate && s.runtimeTemplate.templateId==122308)value-=2;
        }
        if(s.positionPlayerId==side || s.power.currentPower>Max(0,amount-s.power.armor))return value;''')
    if name=='duelAIPass.ws':
        s=replace(s,'    if (cards == 0) return 0;\n    if (spent + cards <= 1) return 0;',
            '    if (cards == 0) return 0;\n    // Net hand balance matters even when this is the first chase card.\n    if (ownHand - cards - enemyHand < -2) return 3;\n    if (spent + cards <= 1) return 0;')
    return s
def main():
    assert not BUILD.exists(),'Use a new revision directory'
    shutil.copytree(SOURCE/'scripts',BUILD/'scripts')
    shutil.copytree(SOURCE/'redux',BUILD/'redux')
    for platform in ['classic','nextgen']:
        part=BUILD/platform;part.mkdir()
        for name in ['ui','extra-resources']:shutil.copytree(SOURCE/platform/name,part/name)
        for name in ['ui-inputs.json','subimages.json']:
            if (SOURCE/platform/name).exists():shutil.copy2(SOURCE/platform/name,part/name)
        (part/'menus').mkdir();shutil.copy2(SOURCE/platform/'menus/menus.json',part/'menus/menus.json')
    names=['duelSession.ws','duelWeather.ws','duelAIPass.ws']
    changes={}
    for name in names:
        old=SOURCE/'scripts/game/betagwent'/name
        assert read(DEV/name)==read(old),'Working source differs from 0.8.2: '+name
        updated=patch(name,read(old));write(BUILD/'scripts/game/betagwent'/name,updated);write(DEV/name,updated)
        changes[name]=dict(before=hashlib.sha256(old.read_bytes()).hexdigest(),after=hashlib.sha256((DEV/name).read_bytes()).hexdigest())
    for p in (BUILD/'scripts/game/betagwent').glob('*.ws'):
        other=SOURCE/'scripts/game/betagwent'/p.name
        if p.name not in names:assert p.read_bytes()==other.read_bytes()
    (BUILD/'ai-changes.json').write_text(json.dumps(dict(version='0.8.2',source=str(SOURCE),changes=changes,gameInstalled=False),indent=2),'utf8')
    print(json.dumps(changes))
if __name__=='__main__':main()
