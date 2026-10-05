// Remaining Scoiatael graphs; the other fifty consumers are existing concrete dependencies.
class CBetaGwentDuelScoia extends IScriptable
{
    private var game : CBetaGwentDuelSession;
    private var historyOne, historyTwo : array<int>;
    public function Initialize(owner : CBetaGwentDuelSession) {game=owner;historyOne.Clear();historyTwo.Clear();}
    private function Side(source : CBetaGwentDuelCard) : int {return game.NorthActingSide(source);}
    private function Query(side : int, zone : int, tier : int, types : int, ignore : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var s : SBetaGwentCardSnapshot;var i : int;
        ids.Clear();game.GetCards(cards);
        for(i=0;i<cards.Size();i+=1)
        {s=cards[i].card;if((side!=0 && s.positionPlayerId!=side) || (s.locationMask&zone)==0 || (s.runtimeTierMask&tier)==0 || (s.runtimeTemplate.typeMask&types)==0 || (s.tokenMask&ignore)!=0 || s.isWaitingToDie)continue;
         if(source && source.monsterIds.Contains(s.instanceId))continue;ids.PushBack(s.instanceId);}
    }
    private function Request(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, minimum : int)
    {var ids : array<int>;Query(side,zone,tier,types,BetaGwentNorthPick((zone&7)!=0,264,0),source,ids);game.MonsterRequest(source,ids,BetaGwentNorthPick((zone&7)!=0,0,2),minimum,1);}
    public function History(card : CBetaGwentDuelCard)
    {var s : SBetaGwentCardSnapshot;var side : int;s=card.Snapshot();if(s.runtimeTemplate.typeMask!=4 || !BetaGwentNilfDwarf(s.runtimeTemplate.templateId))return;side=Side(card);if(side==1)historyOne.PushBack(s.instanceId);else historyTwo.PushBack(s.instanceId);}
    public function BeforePlayed(card : CBetaGwentDuelCard) : bool
    {
        var cards : array<SBetaGwentDevelopmentCard>;var s,t : SBetaGwentCardSnapshot;var ambush : CBetaGwentDuelCard;var i,side : int;var cancelled : bool;
        t=card.Snapshot();if(t.runtimeTemplate.typeMask!=2 || (t.runtimeTierMask&6)==0)return false;side=Side(card);game.GetCards(cards);
        for(i=0;i<cards.Size();i+=1)
        {s=cards[i].card;if(s.runtimeTemplate.templateId!=201779 || (s.locationMask&7)==0 || s.positionPlayerId==side || s.isWaitingToDie || (s.tokenMask&4)!=0 || (s.tokenMask&8)==0)continue;
         ambush=game.FindCard(s.instanceId);ambush.RevealAmbush();game.RecordVisual(8,s.instanceId,"Моренн: особая способность отменена",650);cancelled=true;
         LogChannel('BetaGwent',"DUEL_SCOIA_CANCEL source="+s.instanceId+" special="+t.instanceId);}
        return cancelled;
    }
    private function Milva(source : CBetaGwentDuelCard, side : int)
    {var ids,valid : array<int>;var i,power : int;var t : SBetaGwentCardSnapshot;Query(side,7,6,4,1032,NULL,ids);power=-1;
     for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();power=Max(power,t.power.currentPower);}
     for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower==power)valid.PushBack(ids[i]);}
     if(valid.Size()>0)game.NorthMoveInactive(game.FindCard(valid[game.RandomIndex(valid.Size())]),side,16,false);}
    private function DuelTargets(source : CBetaGwentDuelCard)
    {var ids,valid : array<int>;var counts : array<int>;var i,row : int;var t : SBetaGwentCardSnapshot;
     Query(BetaGwentOpponentId(Side(source)),7,15,4,264,source,ids);counts.PushBack(0);counts.PushBack(0);counts.PushBack(0);counts.PushBack(0);counts.PushBack(0);
     for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();counts[t.locationMask]+=1;}
     for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(counts[t.locationMask]>=2)valid.PushBack(ids[i]);}
     game.MonsterRequest(source,valid,0,1,1);}
    public function Played(source : CBetaGwentDuelCard)
    {
        var id,side,enemy,i,damage,power : int;var s,t : SBetaGwentCardSnapshot;var ids,valid,history : array<int>;
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();source.monsterStage=0;source.monsterIds.Clear();source.monsterRemaining=1;
        LogChannel('BetaGwent',"DUEL_SCOIA_PLAY template="+id+" side="+side);
        if(id==142101)
        {Query(side,7,15,12,8,NULL,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(BetaGwentNilfDwarf(t.runtimeTemplate.templateId))power+=1;if(BetaGwentNilfElf(t.runtimeTemplate.templateId))damage+=1;}
         if(power>0)game.MonsterPower(source,source,power);source.monsterStored=damage;if(damage>0){Request(source,enemy,7,15,4,1);return;}}
        else if(id==142102)
        {Query(side,16,6,12,0,NULL,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if((t.tokenMask&8)!=0)valid.PushBack(ids[i]);}game.MonsterRequest(source,valid,2,0,1);return;}
        else if(id==142103){Request(source,enemy,7,15,4,1);return;}
        else if(id==142104){Milva(source,enemy);Milva(source,side);}
        else if(id==142105){source.monsterRemaining=3;ZoltanTargets(source);return;}
        else if(id==142106){Request(source,enemy,32,6,2,0);return;}
        else if(id==142107)
        {Query(side,16,2,2,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(BetaGwentScoiaIthlinne(game.FindCard(ids[i]).TemplateId()))valid.PushBack(ids[i]);game.MonsterRequest(source,valid,2,0,1);return;}
        else if(id==142108){BetaGwentScoiaPool(id,ids);game.MonsterRequest(source,ids,1,1,1);return;}
        else if(id==142203)
        {if(s.timerValue!=1){game.MonsterComplete(source);return;}Query(side,16,14,4,0,NULL,ids);if(ids.Size()>0)valid.PushBack(ids[game.RandomIndex(ids.Size())]);Query(side,16,14,2,0,NULL,ids);if(ids.Size()>0)valid.PushBack(ids[game.RandomIndex(ids.Size())]);game.MonsterRequest(source,valid,2,0,1);return;}
        else if(id==200080)
        {if(side==1)history=historyOne;else history=historyTwo;for(i=history.Size()-1;i>=0;i-=1)if(history[i]!=s.instanceId){t=game.FindCard(history[i]).Snapshot();if(BetaGwentNilfDwarf(t.runtimeTemplate.templateId)){game.MonsterPower(source,source,t.power.basePower);break;}}}
        else if(id==200209)
        {Query(side,16,2,14,0,NULL,ids);source.monsterRemaining=Min(2,ids.Size());if(source.monsterRemaining>0){Request(source,side,8,15,14,0);return;}}
        else if(id==201611){DuelTargets(source);return;}
        else if(id==201615){ids.PushBack(201715);ids.PushBack(201716);game.MonsterRequest(source,ids,1,1,1);return;}
        else if(id!=201779){game.FailAbility("Неизвестная карта Скоя’таэлей.");return;}
        game.MonsterComplete(source);
    }
    private function ZoltanTargets(source : CBetaGwentDuelCard)
    {var s,t : SBetaGwentCardSnapshot;var ids,valid : array<int>;var i : int;s=source.Snapshot();Query(0,7,15,4,264,source,ids);
     for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationMask!=s.locationMask)valid.PushBack(ids[i]);}game.MonsterRequest(source,valid,0,0,1);}
    private function FinishZoltan(source : CBetaGwentDuelCard)
    {var s,t : SBetaGwentCardSnapshot;var target : CBetaGwentDuelCard;var i : int;s=source.Snapshot();
     for(i=0;i<source.monsterIds.Size();i+=1){target=game.FindCard(source.monsterIds[i]);t=target.Snapshot();if(t.positionPlayerId!=s.positionPlayerId)continue;game.QueueRelocation(target,t.positionPlayerId,s.locationMask,false);game.MonsterOperation(source,target,12,2,7);}
     for(i=0;i<source.monsterIds.Size();i+=1){target=game.FindCard(source.monsterIds[i]);t=target.Snapshot();if(t.positionPlayerId==s.positionPlayerId)continue;game.QueueRelocation(target,t.positionPlayerId,s.locationMask,false);game.MonsterPower(source,target,-2);}game.MonsterComplete(source);}
    private function BeginSwapDraw(source : CBetaGwentDuelCard)
    {var ids : array<int>;var side,i : int;side=Side(source);source.monsterRemaining=source.monsterIds.Size();
     if(source.monsterRemaining==0){game.MonsterComplete(source);return;}
     for(i=0;i<source.monsterIds.Size();i+=1){game.NorthMoveInactive(game.FindCard(source.monsterIds[i]),side,16,false);game.NilfSwapped(game.FindCard(source.monsterIds[i]));}
     source.monsterStage=1;source.monsterIds.Clear();Query(side,16,2,14,0,NULL,ids);game.ShuffleIds(ids);game.MonsterRequest(source,ids,2,1,1);}
    public function Select(source : CBetaGwentDuelCard, selected : int)
    {
        var id,side,enemy,i,row : int;var target : CBetaGwentDuelCard;var s,t,u : SBetaGwentCardSnapshot;var ids,valid : array<int>;
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();target=game.FindCard(selected);
        if(id==142108){if(selected>0)game.MonsterCreate(source,selected);else game.MonsterComplete(source);return;}
        if(id==201615)
        {if(source.monsterStage==0){source.monsterStage=1;source.monsterStored=selected;if(selected==201715){Request(source,side,16,6,2,1);return;}BetaGwentScoiaPool(id,ids);game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,1,1,1);return;}
         if(source.monsterStored==201716){if(selected>0)game.MonsterCreate(source,selected);else game.MonsterComplete(source);return;}}
        if(id==142105 && selected==0){FinishZoltan(source);return;}
        if(id==200209 && selected==0 && source.monsterStage==0){BeginSwapDraw(source);return;}
        if(!target){if(id==142203)game.QueueTimer(source,0,1);game.MonsterComplete(source);return;}t=target.Snapshot();
        if(id==142102 || (id==201615 && source.monsterStored==201715))
        {
            // Created Toruviel and original deck Toruviel are distinct instances.
            if(t.locationMask!=16 || t.positionPlayerId!=side || t.isWaitingToDie || (t.runtimeTierMask&6)==0
                || (id==142102 && ((t.tokenMask&8)==0 || (t.runtimeTemplate.typeMask&12)==0))
                || (id==201615 && t.runtimeTemplate.typeMask!=2))
            {LogChannel('BetaGwent',"DUEL_DECK_PICK_REJECTED source="+s.instanceId+" target="+selected+" location="+t.locationMask);Played(source);return;}
            LogChannel('BetaGwent',"DUEL_DECK_PICK source="+s.instanceId+" target="+selected+" template="+t.runtimeTemplate.templateId+" location=16 created="+target.createdCopy);
            game.MonsterPlayExisting(source,target);return;
        }
        if(id==142106){
            if(t.locationMask!=32 || t.positionPlayerId!=enemy || t.runtimeTemplate.typeMask!=2
                || (t.runtimeTierMask&6)==0 || t.isWaitingToDie || (t.tokenMask&512)!=0)
            {LogChannel('BetaGwent',"DUEL_AGLAIS_PICK_REJECTED target="+selected+" zone="+t.locationMask);Played(source);return;}
            // Transfer the grave card before adding Doomed. Move(to Graveyard)
            // removes a Doomed card immediately, before its nested play begins.
            game.NorthMoveInactive(target,side,32,false);target.AddTokens(512);
            LogChannel('BetaGwent',"DUEL_AGLAIS_REPLAY target="+selected+" side="+side+" banishAfterPlay=true");
            game.MonsterPlayExisting(source,target);return;
        }
        if(id==142107){source.monsterStored=t.runtimeTemplate.templateId;source.monsterStage=1;game.MonsterPlayExisting(source,target);return;}
        if(id==142101)game.MonsterPower(source,target,-source.monsterStored);
        else if(id==142103)
        {game.MonsterPower(source,target,-8);game.FlushDeaths();u=target.Snapshot();if((u.locationMask&7)==0){Query(side,8,14,4,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(BetaGwentNilfElf(game.FindCard(ids[i]).TemplateId()))game.MonsterOperation(source,game.FindCard(ids[i]),1,1,8);}}
        else if(id==142105){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){ZoltanTargets(source);return;}FinishZoltan(source);return;}
        else if(id==142203){game.NilfTake(target,side);game.QueueTimer(source,0,1);}
        else if(id==200209)
        {if(source.monsterStage==0){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){Request(source,side,8,15,14,0);return;}BeginSwapDraw(source);return;}
         game.NilfTake(target,side);source.monsterRemaining-=1;if(source.monsterRemaining>0){Query(side,16,2,14,0,NULL,ids);game.ShuffleIds(ids);game.MonsterRequest(source,ids,2,1,1);return;}}
        else if(id==201611)
        {if(source.monsterStage==0){source.monsterStored=selected;source.monsterStage=1;source.monsterIds.PushBack(selected);Query(enemy,t.locationMask,15,4,264,source,ids);game.MonsterRequest(source,ids,0,1,1);return;}game.MonsterDuel(game.FindCard(source.monsterStored),target,0,0);}
        game.MonsterComplete(source);
    }
    public function ChildReturned(source : CBetaGwentDuelCard) : bool
    {var child : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;child=source.TakePlayedChild();
     if(source.TemplateId()==142107 && source.monsterStage==1){source.monsterStage=2;game.MonsterCreate(source,source.monsterStored);return true;}
     if(child && source.TemplateId()==142106){s=child.Snapshot();if((s.locationMask&7)!=0)game.MonsterOperation(source,child,14,0,7);else game.NilfBanish(child);}return false;}
}
