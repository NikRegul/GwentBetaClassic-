"""Apply the stage90 valuation split once, keeping rule execution unchanged."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'BetaGwent/development/scripts/game/betagwent/duelSession.ws'
s=p.read_text('utf-8-sig')
assert 'private function AiCardTempo(' not in s
start=s.index('            d = live[i].Definition(); value = s.power.currentPower;',s.index('public function OpponentStep()'))
end=s.index('            reserve = AiReserveCost(d);',start)
body=s[start:end].replace('live[i]','card')
body=body.replace('            if (d.header.typeMask == 4 && BestCardRow(2,d) == 0) continue;\n','')
body=body.replace('AiManagedDeployValue(d,2)','AiManagedDeployValue(d,2,immediate)')
body=body.replace('archetypeAI.PileGain(d)','archetypeAI.PileGain(d,immediate)')
body=body.replace('d.targetSide, d.header.templateId);','d.targetSide, d.header.templateId, immediate);')
body=body.replace('if (d.weatherToken != 0)','if (!immediate && d.weatherToken != 0)')
body=body.replace('weather.ClearValue(2, d.amount), RallyValue(2)','weather.ClearValue(2, d.amount, immediate), RallyValue(2,immediate)')
body=body.replace('if (d.effect == 14 &&','if (!immediate && d.effect == 14 &&')
body=body.replace('if (d.effect == 15)','if (!immediate && d.effect == 15)')
body=body.replace('if (d.timerPeriod > 0 &&','if (!immediate && d.timerPeriod > 0 &&')
body=body.replace('if (d.passiveBoost != 0 &&','if (!immediate && d.passiveBoost != 0 &&')
body=body.replace('if (d.deathwishDamage != 0 &&','if (!immediate && d.deathwishDamage != 0 &&')
body=body.replace('if (d.deathwishSummonTemplate > 0 &&','if (!immediate && d.deathwishSummonTemplate > 0 &&')
body=body.replace('weatherAI.Gain(d,s.power.currentPower,false,true)','weatherAI.Gain(d,s.power.currentPower,false,s.locationMask==8,immediate)')
helper='''    // Tempo is the immediate score swing; forecasts only rank normal turns.
    // This reads snapshots and own/public zones, never executes a play or RNG.
    private function AiCardTempo(card : CBetaGwentDuelCard, immediate : bool, vranAnchor : int, clearRisk : int) : int
    {
        var s,vranTarget : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        var d : SBetaGwentDuelDefinition;var value,effectValue,row : int;
        s=card.Snapshot();m=match.Snapshot();
'''+''.join(line[4:]+'\n' for line in body.splitlines())+'''        return value;
    }
'''
s=s[:start]+'''            d=live[i].Definition();
            if(d.header.typeMask==4 && BestCardRow(2,d)==0)continue;
            value=AiCardTempo(live[i],false,vranAnchor,clearRisk);
            tempo=AiCardTempo(live[i],true,vranAnchor,clearRisk);
'''+s[end:]
pos=s.index('    public function OpponentStep()');s=s[:pos]+helper+s[pos:]
s=s.replace('catchCost, cost, bestGain, clearRisk : int;','catchCost, cost, bestGain, bestUtility, tempo, clearRisk : int;')
s=s.replace('action.gain=value;action.cards=1;','action.gain=tempo;action.cards=1;')
s=s.replace('m.playerOne.hasPassed && value >= deficit','m.playerOne.hasPassed && tempo >= deficit')
s=s.replace('Max(0, value - deficit)','Max(0, tempo - deficit)')
s=s.replace('bestGain = value+AiDrawUtility(d,2); best = s.instanceId;','bestGain = tempo; bestUtility=value+AiDrawUtility(d,2); best = s.instanceId;')
s=s.replace('action.id=-1;action.gain=value;', 'tempo=AiCardTempo(leaderCard,true,vranAnchor,clearRisk)+archetypeAI.LeaderGain(d);\n            action.id=-1;action.gain=tempo;')
s=s.replace('(maximum > 0 && bestGain > 0)','(maximum > 0 && bestUtility > 0)')
s=s.replace('planner=rules88','planner=tempo90')
# Rally is random: use the weakest supported result for a guaranteed chase.
s=s.replace('private function RallyValue(side : int) : int','private function RallyValue(side : int, optional immediate : bool) : int')
s=s.replace('var i, total, count, value : int; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;\n        if (BestOwnRow(side) == 0)',
    'var i, total, count, value, lowest : int; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;\n        lowest=2147483647;\n        if (BestOwnRow(side) == 0)',1)
lo=s.index('    private function RallyValue(');hi=s.index('    private function DeckCopiesValue(',lo)
r=s[lo:hi]
r=r.replace('d = cards[i].Definition(); value = s.power.currentPower;','d = cards[i].Definition(); value = s.power.currentPower;\n                if(BetaGwentDuelSpying(d.header.templateId))value=-value;')
r=r.replace('d.targetSide, d.header.templateId));','d.targetSide, d.header.templateId, immediate));')
for clause in ('d.effect == 14 &&','d.effect == 15','d.timerPeriod > 0','d.passiveBoost != 0 &&','d.deathwishDamage != 0','d.deathwishSummonTemplate > 0'):
    r=r.replace('if ('+clause,'if (!immediate && '+clause)
r=r.replace('total += value; count += 1;','lowest=Min(lowest,value);total += value; count += 1;')
r=r.replace('if (count == 0) return 0; return total / count;','if (count == 0) return 0; if(immediate)return lowest; return total / count;')
s=s[:lo]+r+s[hi:]
p.write_text(s,'utf-8-sig')
print('Separated immediate tempo from setup, engines, drawing and weather forecasts.')
