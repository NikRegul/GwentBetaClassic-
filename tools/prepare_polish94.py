"""Apply the stage94 source migration once; normal builds use these sources."""
from pathlib import Path
import json, shutil
ROOT=Path(__file__).resolve().parents[1]
def change(rel,old,new):
 p=ROOT/rel;t=p.read_text('utf-8-sig')
 if new in t:return
 assert old in t,(rel,old[:80])
 p.write_text(t.replace(old,new,1),'utf-8-sig' if p.suffix=='.ws' else 'utf8')
DEV='BetaGwent/development/scripts/game/betagwent/'
change(DEV+'duelAudio.ws','templateId == 113209','templateId == 113309')
change('tools/ui/prepare_audio_import.py',"cue_bindings = {3:add_effect(vfx['DestroyDestroyBlood'])","cue_bindings = {3:add_effect(vfx['PowerDirectPhysical'])")
change(DEV+'duelSession.ws','RecordVisual(12, t.instanceId, "Поглощение: " + d.title, 460);','RecordVisual(11, t.instanceId, "Поглощение: " + d.title, 460);')
# Consume already has a presentation beat. Keep lifecycle/deathwish events,
# but do not play a second removal sound/animation for the same consumed body.
change(DEV+'duelSession.ws','if (!suppressAbilities) RecordVisual(3, s.instanceId, d.title + ": исчез", 320);','if (!suppressAbilities && batch[i].ConsumeAttackerId() == 0) RecordVisual(3, s.instanceId, d.title + ": исчез", 320);')
change(DEV+'duelSession.ws','if (!suppressAbilities) RecordVisual(3, s.instanceId, d.title + ": в сброс", 320);','if (!suppressAbilities && batch[i].ConsumeAttackerId() == 0) RecordVisual(3, s.instanceId, d.title + ": в сброс", 320);')
change(DEV+'duelSession.ws','    private function AiManagedDeployValue(','''    private function AiDuelTarget(source : CBetaGwentDuelCard, target : SBetaGwentCardSnapshot, immediate : bool) : int
    {
        var own : SBetaGwentCardSnapshot; var value : int; own=source.Snapshot();
        value=BetaGwentAIDuelSwing(own.power.currentPower,own.power.armor,target.power.currentPower,target.power.armor);
        if(!immediate && own.power.currentPower>=target.power.currentPower+target.power.armor)
            value+=AiEngineValue(target,own.positionPlayerId);
        return value;
    }
    private function AiDuelGain(source : CBetaGwentDuelCard, immediate : bool) : int
    {
        var i,best : int;var own,t : SBetaGwentCardSnapshot;own=source.Snapshot();best=-2147483647;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(t.positionPlayerId==own.positionPlayerId || (t.locationMask&7)==0 || t.isWaitingToDie || (t.tokenMask&264)!=0 || t.runtimeTemplate.typeMask!=4)continue;
            best=Max(best,AiDuelTarget(source,t,immediate));}
        if(best==-2147483647)return 0;return Max(0,best);
    }
    private function AiTimingReserve(card : CBetaGwentDuelCard, gain : int) : int
    {
        var d : SBetaGwentDuelDefinition;var s : SBetaGwentCardSnapshot;var useful : int;
        d=card.Definition();s=card.Snapshot();useful=gain-s.power.currentPower;
        // A reactive gold's body alone is not a reason to spend its ability.
        if(d.effect==34 && (d.specialMode==137 || d.specialMode==114 || d.specialMode==125 || d.specialMode==132))
            return Max(0,8-useful)*2;
        if(d.header.tierMask==8 && d.effect==1)return Max(0,d.amount-useful);
        return 0;
    }
    private function AiManagedDeployValue(''')
change(DEV+'duelSession.ws','        if((t.locationMask&7)==0)return value;','''        if((t.locationMask&7)==0)return value;
        if(d.effect==34 && d.specialMode==137)return AiDuelTarget(source,t,false);''')
change(DEV+'duelSession.ws','        value+=AiManagedDeployValue(d,2,immediate);','''        value+=AiManagedDeployValue(d,2,immediate);
        if(d.effect==34 && d.specialMode==137)value+=AiDuelGain(card,immediate);''')
change(DEV+'duelSession.ws','            reserve = AiReserveCost(d);','            reserve = AiReserveCost(d)+AiTimingReserve(live[i],value);')
change(DEV+'duelSession.ws','value = s.power.currentPower;\n            value+=AiManagedDeployValue(d,2);','value = AiCardTempo(leaderCard,false,vranAnchor,clearRisk);')
change(DEV+'duelSession.ws','            cost = 10; if (m.roundNumber >= 3) cost = 0;','''            cost = 10; if (m.roundNumber >= 3) cost = 0;
            // Preserve a once-per-match leader unless its actual ability has
            // useful targets, it sets up the deck, or no hand play is left.
            reserve=cost+AiTimingReserve(leaderCard,value);
            if(m.roundNumber<3 && value<=s.power.currentPower+2 && archetypeAI.LeaderPriority(d)<=0 && ownHand>0)reserve+=12;''')
change(DEV+'duelSession.ws','value * 10 - 20 + archetypeAI.LeaderPriority(d)*10 > maximum','value * 10 - reserve * 10 + archetypeAI.LeaderPriority(d)*10 > maximum')
change(DEV+'duelSession.ws','action.reserve=cost;actions.PushBack(action);','action.reserve=reserve;actions.PushBack(action);')
change(DEV+'duelSession.ws','if (best != 0 && (catchBest != 0 || (maximum > 0 && bestUtility > 0)))','''// A low ordering score is a reason to save a gold, not to pass away a
        // mandatory round. If every remaining card is reactive, still play
        // the least wasteful legal body rather than concede by score cutoff.
        if (best != 0)''')
change(DEV+'duelSession.ws','        if (!m.playerOne.hasPassed && LeaderAvailable(2) && BestOwnRow(2) != 0) return UseLeader(2);','''        // Only use the emergency leader when there is no legal hand play.
        if (!m.playerOne.hasPassed && best==0 && LeaderAvailable(2) && BestOwnRow(2) != 0) return UseLeader(2);
        LogChannel('BetaGwent',"DUEL_AI_PASS reason=no_legal_hand_or_useful_chase hand="+ownHand);''')
change(DEV+'duelSession.ws','planner=tempo90','planner=tempo94')
# Original banish is a disappearance, never a consume-to-source flight.
change('BetaGwent/ui/src/BetaGwentBoard.as','if(activeCue.kind==11||activeCue.kind==12)drawConsumeCue(fx,origin);','if(activeCue.kind==11)drawConsumeCue(fx,origin);')
# Extract source artwork at 384x540; keep board/UI at their original full size.
source=ROOT/'tools/ui/build_hd_art93.py';dest=ROOT/'tools/ui/build_hd_art94.py'
if not dest.exists():
 t=source.read_text('utf8').replace('hd93','hd94').replace('hd-art93','hd-art94').replace('stage=93','stage=94')
 t=t.replace('range(0,len(cards),160)','range(0,len(cards),70)').replace('cards[first:first+160]','cards[first:first+70]')
 t=t.replace('((len(group)+15)//16)*360','((len(group)+9)//10)*540').replace("Image.new('RGBA',(4096,height))","Image.new('RGBA',(3840,height))")
 t=t.replace('(256,360)','(384,540)').replace('i%16*256,i//16*360','i%10*384,i//10*540').replace('[page,x,y,256,360]','[page,x,y,384,540]').replace('str(first//160)','str(first//70)')
 dest.write_text(t,'utf8')
change('tools/ui/build_card_art.py','tools/ui/build_hd_art93.py','tools/ui/build_hd_art94.py')
plan=ROOT/'docs/plan.md';t=plan.read_text('utf8')
if 'Текущий шаг — 94:' not in t:
 i=t.index('## Текущий шаг');t=t[:i]+'''## Текущий шаг — 94: исправления ИИ, звука, погоды и контроллера

Запрос 2026-10-05: устранить преждевременный лидер/пас и розыгрыш Зельтрика,
разделить гибель и поглощение, убрать повтор Белого хлада, повысить качество
карт, доски и редактора, улучшить управление. Затем исходный коммит и RU/EN
0.2.1 для Nexus. Публикация Nexus вручную, управление UI не используется.
В установленной игре обнаружена preview.2, HD93 ещё не установлена.
Доступный editor.log подтверждает загрузку банка, не содержит последних AI-ходов.

'''+t[i:].replace('## Текущий шаг — 93:','## Завершённый этап — 93:')
 plan.write_text(t,'utf8')
print('Stage94 migration prepared. Build, native compile and runtime acceptance still pending.')
if __name__=='__main__':pass
