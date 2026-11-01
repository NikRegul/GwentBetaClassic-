// Creation closure: abilities reached through leaders created by Usurper.
class CBetaGwentNilfDependencies extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var nilf : CBetaGwentDuelNilf;
    public function Initialize(owner : CBetaGwentDuelSession, router : CBetaGwentDuelNilf) {game=owner;nilf=router;}
    private function Query(side : int, zone : int, tier : int, types : int, flags : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {nilf.DepQuery(side,zone,tier,types,flags,source,ids);}
    private function Request(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, flags : int)
    {var ids : array<int>;var i,f : int;var s : SBetaGwentCardSnapshot;
     // Beta Ignore=256: board targets of these abilities never include the card itself.
     f=flags;if((zone&7)!=0)f=f|16;
     Query(side,zone,tier,types,f,source,ids);for(i=ids.Size()-1;i>=0;i-=1){s=game.FindCard(ids[i]).Snapshot();if((s.locationMask&7)!=0 && (s.tokenMask&256)!=0)ids.Erase(i);}if(source.TemplateId()==201676 && ids.Size()>0)game.ShuffleIds(ids);game.MonsterRequest(source,ids,BetaGwentNorthPick((zone&7)!=0,0,2),BetaGwentNilfMinimum(source.TemplateId()),1);}
    public function Played(source : CBetaGwentDuelCard)
    {
        var id,side,enemy,i,j,count : int;var s,t : SBetaGwentCardSnapshot;var ids,valid,rows : array<int>;
        id=source.TemplateId();side=game.NorthActingSide(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();
        source.monsterStage=0;source.monsterRemaining=1;source.monsterStored=0;source.monsterIds.Clear();
        if(id==142201){Query(side,31,15,4,8192+16,source,ids);for(i=0;i<ids.Size();i+=1)game.MonsterOperation(source,game.FindCard(ids[i]),12,1,31);}
        else if(id==142202){ids.PushBack(113301);ids.PushBack(113305);ids.PushBack(113401);game.MonsterRequest(source,ids,1,1,1);return;}
        else if(id==142204 || id==142208 || id==142205 || id==142211 || id==142213 || id==142214 || id==142306 || id==142313 || id==142315 || id==200039 || id==200042 || id==200136){game.MonsterComplete(source);return;}
        else if(id==142210 || id==142307){game.QueueTimer(source,2,2);}
        else if(id==142206 || id==142302 || id==142311){
            if(id==142302)game.NorthClearHazard(side,s.locationMask);
            nilf.DepMovementRequest(source,BetaGwentNorthPick(id==142206,256,264),BetaGwentNorthPick(id==142206,0,s.locationMask));return;
        }
        else if(id==142310){Request(source,0,7,15,4,0);return;}
        else if(id==142207){Query(side,16,6,4,8192,source,ids);if(ids.Size()>0)game.MonsterPlayExisting(source,game.FindCard(ids[game.RandomIndex(ids.Size())]));else game.MonsterComplete(source);return;}
        else if(id==142209 || id==142305 || id==142314 || id==200535){Request(source,enemy,7,15,4,0);return;}
        else if(id==142301){source.monsterRemaining=2;Request(source,side,7,15,4,0);return;}
        else if(id==142212)
        {game.VisibleRowEffectIds(side,s.locationMask,ids);for(i=0;i<ids.Size();i+=1){rows.Clear();for(j=1;j<=4;j*=2)if(j!=s.locationMask && game.CountLocation(side,j)<9)rows.PushBack(j);if(rows.Size()>0){game.QueueRelocation(game.FindCard(ids[i]),side,rows[game.RandomIndex(rows.Size())],false);game.FlushDeaths();count+=1;}}game.MonsterPower(source,source,count);}
        else if(id==142303 || id==201638){Query(side,16,14,14,0,NULL,ids);if(ids.Size()>0){if(id==201638)source.choiceDeck=ids;else source.choiceDeck.Clear();Request(source,side,8,15,14,0);return;}}
        else if(id==142304){game.MonsterCreate(source,143301);return;}
        else if(id==142308){nilf.DepTop(source,side,2,10,0,2,true);return;}
        else if(id==142309){Query(side,7,15,4,16384,source,ids);for(i=0;i<ids.Size();i+=1)game.MonsterPower(source,game.FindCard(ids[i]),1);}
        else if(id==142312){Request(source,side,8,14,4,0);return;}
        else if(id==142316 || id==201559){game.NorthSummonCopies(source,id);}
        else if(id==142401){nilf.SourceCards(side,8,14,4,0,0,source,ids);game.ShuffleIds(ids);for(i=0;i<ids.Size() && i<2;i+=1)game.MonsterOperation(source,game.FindCard(ids[i]),1,1,31);}
        else if(id==143301){game.QueueTimer(source,2,1);}
        else if(id==200030){ids.PushBack(1);ids.PushBack(2);ids.PushBack(4);game.MonsterRequest(source,ids,3,1,1);return;}
        else if(id==200135){for(j=1;j<=4;j*=2){nilf.SourceCards(enemy,j,15,14,8,0,source,ids);if(ids.Size()>0)valid.PushBack(ids[game.RandomIndex(ids.Size())]);}for(i=0;i<valid.Size();i+=1)game.MonsterPower(source,game.FindCard(valid[i]),-3);}
        else if(id==200138){Request(source,side,32,2,10,65536);return;}
        else if(id==200139){Query(enemy,7,15,4,0,source,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(game.CountLocation(enemy,t.locationMask)<4)valid.PushBack(ids[i]);}game.MonsterRequest(source,valid,0,0,1);return;}
        else if(id==200293){game.AgitatorPool(side,valid);if(valid.Size()>0){game.MonsterCreate(source,valid[game.RandomIndex(valid.Size())]);return;}}
        else if(id==200520 || id==201696){Query(side,32,BetaGwentNorthPick(id==200520,6,2),4,BetaGwentNorthPick(id==201696,8192,0),source,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if((id==200520 && t.runtimeTemplate.factionMask==16 && t.power.currentPower<=s.power.currentPower) || (id==201696 && !BetaGwentNilfSupport(t.runtimeTemplate.templateId)))valid.PushBack(ids[i]);}game.MonsterRequest(source,valid,2,0,1);return;}
        else if(id==201636){t=s;t.locationIndex+=1;game.QueueSpawn(t,id,1);}
        else if(id==201676){Request(source,side,16,6,14,1024);return;}
        else {game.FailAbility("Неизвестная зависимость Узурпатора.");return;}
        game.MonsterComplete(source);
    }
    public function Select(source : CBetaGwentDuelCard, selected : int)
    {
        var id,side,i,power : int;var target : CBetaGwentDuelCard;var s,t,u : SBetaGwentCardSnapshot;var ids : array<int>;var template : SBetaGwentDuelDefinition;
        id=source.TemplateId();side=game.NorthActingSide(source);s=source.Snapshot();target=game.FindCard(selected);
        if(id==142202){if(selected>0)game.MonsterCreate(source,selected);else game.MonsterComplete(source);return;}
        if(id==142301 && selected==0){CommitMedic(source);return;}
        if(!target){game.MonsterComplete(source);return;}t=target.Snapshot();
        if(id==142207 || id==142308 || id==200138 || id==200520 || id==201696 || id==201676){game.MonsterPlayExisting(source,target);return;}
        if(id==142206 || id==142302 || id==142311)
        {
            if(id==142206)game.MonsterOperation(source,target,6,0,7);
            if(t.locationMask!=s.locationMask)game.QueueRelocation(target,t.positionPlayerId,s.locationMask,false);
            // Graph756 filters the selected side and boosts AFTER MoveCards.
            if(id==142311 && t.positionPlayerId==side)game.MonsterPower(source,target,3);
        }
        else if(id==142209 || id==200535)
        {game.MonsterPower(source,target,-s.power.currentPower);game.FlushEffects();u=target.Snapshot();if(id==142209 && u.power.currentPower<=0){nilf.SourceCards(side,31,15,4,0,0,source,ids);for(i=0;i<ids.Size();i+=1){u=game.FindCard(ids[i]).Snapshot();template=game.FindCard(ids[i]).Definition();if((template.tokens&8)!=0 || BetaGwentNilfDryad(u.runtimeTemplate.templateId))game.MonsterOperation(source,game.FindCard(ids[i]),1,1,31);}}}
        else if(id==142305){game.MonsterPower(source,target,-3);game.FlushDeaths();u=target.Snapshot();if(!game.UnitDied(u))game.MonsterPower(source,source,3);}
        else if(id==142301){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){Request(source,side,7,15,4,0);return;}CommitMedic(source);return;}
        else if(id==201638)
        {
            Query(side,16,15,14,0,NULL,ids);i=game.RandomIndex(ids.Size()+1);
            game.MoveInactiveToIndex(target,side,16,i);game.DrawCaptured(side,source.choiceDeck,1,false);
        }
        else if(id==142303)
        {
            game.NorthPile(side,16,ids);
            for(i=0;i<ids.Size();i+=1){u=game.FindCard(ids[i]).Snapshot();if((u.runtimeTierMask&14)!=0 && (u.runtimeTemplate.typeMask&14)!=0)break;}
            if(i<ids.Size()){
                game.MonsterPower(source,source,t.power.basePower);
                game.NorthMoveInactive(target,side,16,true);
                game.NilfTake(game.FindCard(ids[i]),side);game.NilfSwapped(target);
                BetaGwentLog("DUEL_AUTOMATIC_SWAP source="+s.instanceId+" returned="+selected+" drawn="+ids[i]);
            }
        }
        else if(id==142310){game.MonsterPower(source,target,-BetaGwentNorthPick(source.monsterStage==0,3,1));if(source.monsterStage==0){game.FlushDeaths();source.monsterStage=1;Request(source,0,7,15,4,0);return;}}
        else if(id==142312)game.MonsterOperation(source,target,1,3,31);
        else if(id==142314)game.MonsterPower(source,target,-2);
        else if(id==200139)game.MonsterPower(source,target,-7);
        game.MonsterComplete(source);
    }
    private function CommitMedic(source : CBetaGwentDuelCard)
    {var i : int;for(i=0;i<source.monsterIds.Size();i+=1)game.MonsterPower(source,game.FindCard(source.monsterIds[i]),3);game.MonsterComplete(source);}
    public function ChildReturned(source : CBetaGwentDuelCard) : bool
    {var child : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;child=source.TakePlayedChild();if(child && source.TemplateId()==142207)game.MonsterOperation(source,child,12,3,7);if(child && source.TemplateId()==200138){s=child.Snapshot();if((s.locationMask&7)!=0)game.MonsterOperation(source,child,14,0,7);else game.NilfBanish(child);}return false;}
    public function Row(source : CBetaGwentDuelCard, side : int, row : int)
    {
        var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;var i,n : int;
        if(source.TemplateId()!=200030){s=source.Snapshot();s.positionPlayerId=side;s.locationMask=row;s.locationIndex=-3;game.QueueSpawn(s,143301,1);game.MonsterComplete(source);return;}
        game.GetZoneCards(side,row,cards);n=cards.Size();
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if((s.tokenMask&8)==0 && (s.locationIndex==0 || s.locationIndex==n-1))game.MonsterPower(source,cards[i],-6);}
        game.MonsterComplete(source);
    }
    public function TimerTriggered(source : CBetaGwentDuelCard)
    {var s : SBetaGwentCardSnapshot;s=source.Snapshot();if(source.TemplateId()==142307 && (s.tokenMask&4)==0)source.RevealAmbush();}
    public function PlayCompleted(card : CBetaGwentDuelCard)
    {
        var old : SBetaGwentCardSnapshot;old=card.Snapshot();
        if((old.locationMask&7)==0 || (card.playFromLocation&7)!=0)return;
        old.locationMask=card.playFromLocation;MorennArrival(old);
    }
    private function MorennArrival(cause : SBetaGwentCardSnapshot)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var source,target : CBetaGwentDuelCard;var s,t : SBetaGwentCardSnapshot;var i : int;
        target=game.FindCard(cause.instanceId);if(!target || (cause.locationMask&7)!=0)return;t=target.Snapshot();
        if((t.locationMask&7)==0 || (t.tokenMask&8)!=0)return;game.GetCards(cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].card;if(s.runtimeTemplate.templateId!=142208 || (s.locationMask&7)==0 || s.isWaitingToDie || s.power.currentPower<=0 || (s.tokenMask&12)!=8 || t.positionPlayerId==s.positionPlayerId)continue;
            source=game.FindCard(s.instanceId);if(source.ambushPlayedId!=t.instanceId)continue;
            source.RevealAmbush();game.MonsterPower(source,target,-7);source.ambushPlayedId=0;}
    }
    public function Trigger(kind : int, cause : SBetaGwentCardSnapshot)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var s,t : SBetaGwentCardSnapshot;var source,target : CBetaGwentDuelCard;var ids,valid : array<int>;var i,j,id,power : int;
        if(kind==3)MorennArrival(cause);
        game.GetCards(cards);target=game.FindCard(cause.instanceId);if(target)t=target.Snapshot();
        for(i=0;i<cards.Size();i+=1)
        {
            s=cards[i].card;source=game.FindCard(s.instanceId);id=s.runtimeTemplate.templateId;if(!source || s.isWaitingToDie || (s.tokenMask&4)!=0)continue;
            if(kind==4 && id==200039 && (s.locationMask&31)!=0 && target && t.runtimeTemplate.typeMask==2 && game.NorthActingSide(target)==s.positionPlayerId)game.MonsterOperation(source,source,1,1,31);
            if(kind==3 && id==142214 && s.instanceId==cause.instanceId && ((cause.locationMask==8 && s.locationMask==16) || (cause.locationMask==16 && s.locationMask==8)))game.MonsterOperation(source,source,1,2,31);
            if(kind==3 && cause.instanceId==s.instanceId && cause.positionPlayerId==s.positionPlayerId && cause.locationMask==8 && s.locationMask==16 && id==142309)game.NilfQueueReaction(source,5,s.positionPlayerId);
            if(kind==6 && id==142211 && s.locationMask==16){Query(s.positionPlayerId,7,15,4,16384,NULL,ids);if(ids.Size()>=5)game.NorthRandomSummon(source);}
            if((s.locationMask&7)==0)continue;
            if(kind==3 && target && t.instanceId!=s.instanceId && (t.locationMask&7)!=0 && ((cause.locationMask&7)==0 || t.positionPlayerId!=cause.positionPlayerId))
            {if(id==142213 && t.positionPlayerId==s.positionPlayerId && BetaGwentNilfDwarf(t.runtimeTemplate.templateId))game.MonsterPower(source,source,1);if(id==142315 && t.positionPlayerId!=s.positionPlayerId)game.MonsterPower(source,source,1);}
            if(kind==3 && target && (cause.locationMask&7)!=0 && (t.locationMask&7)!=0 && cause.positionPlayerId==t.positionPlayerId && cause.locationMask!=t.locationMask)
            {if(id==142316 && t.instanceId==s.instanceId)game.MonsterPower(source,source,2);if(id==142314){if(t.instanceId==s.instanceId)nilf.DepRandomDamage(source,BetaGwentOpponentId(s.positionPlayerId),7,2,1);else if(t.positionPlayerId!=s.positionPlayerId)game.MonsterPower(source,target,-2);}}
            // AfterPlayed remembers the original instance. Its MoveCards at
            // execution-stack pop, after deploy, is the separate firing event.
            if(kind==4 && id==142208 && (s.tokenMask&8)!=0 && target && t.runtimeTemplate.typeMask==4 && t.positionPlayerId!=s.positionPlayerId && (target.playFromLocation&7)==0)source.ambushPlayedId=t.instanceId;
            if(kind==7 && id==142204 && (s.tokenMask&8)!=0 && cause.positionPlayerId!=s.positionPlayerId)
            {source.RevealAmbush();Query(s.positionPlayerId,s.locationMask,15,4,16,source,ids);for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();if(Abs(t.locationIndex-s.locationIndex)<=2)game.MonsterPower(source,game.FindCard(ids[j]),2);}}
            if(kind==5 && id==200136 && (s.tokenMask&8)==0)source.nilfCounter=0;
            if(kind==5 && cause.positionPlayerId==s.positionPlayerId)
            {
                if((id==142210 || id==142307) && (s.tokenMask&8)!=0 && s.timerValue>0)
                {game.QueueTimer(source,0,1);if(s.timerValue==1 && id==142210){source.RevealAmbush();Query(BetaGwentOpponentId(s.positionPlayerId),7,6,4,0,source,ids);power=-1;for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();if(t.power.currentPower<=5)power=Max(power,t.power.currentPower);}for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();if(t.power.currentPower==power)valid.PushBack(ids[j]);}if(valid.Size()>0){target=game.FindCard(valid[game.RandomIndex(valid.Size())]);t=target.Snapshot();game.QueueRelocation(target,s.positionPlayerId,t.locationMask,false);}}}
            }
            if(kind==6 && cause.positionPlayerId==s.positionPlayerId)
            {if(id==142205){Query(s.positionPlayerId,8,14,4,8,NULL,ids);if(ids.Size()>0)game.MonsterOperation(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),1,1,31);}if(id==200136 && source.nilfCounter>0)game.MonsterPower(source,source,2);
             if(id==143301 && !game.NilfBothPassed096())game.QueueTimer(source,2,s.timerValue-1);}
        }
    }
}
