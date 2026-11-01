// Concrete consumers of the pinned Northern graphs; shared managed effects and requests.
class CBetaGwentDuelNorth extends IScriptable
{
    private function DeckBoostRequest(source : CBetaGwentDuelCard)
    {var ids : array<int>;var i,maximum : int;for(i=0;i<source.choiceDeck.Size();i+=1)if(!source.monsterIds.Contains(source.choiceDeck[i]))ids.PushBack(source.choiceDeck[i]);maximum=Min(source.monsterRemaining,ids.Size());game.MonsterRequest(source,ids,2,0,maximum);}
    private function CommitDeckBoost(source : CBetaGwentDuelCard)
    {var i : int;var d : SBetaGwentDuelDefinition;d=source.Definition();for(i=0;i<source.monsterIds.Size();i+=1)game.MonsterOperation(source,game.FindCard(source.monsterIds[i]),1,d.amount,31);game.MonsterComplete(source);}
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public function Initialize(owner : CBetaGwentDuelSession) { game = owner; }
    private function Side(source : CBetaGwentDuelCard) : int
    { var s : SBetaGwentCardSnapshot; s = source.Snapshot(); if (BetaGwentDuelSpying(source.TemplateId())) return BetaGwentOpponentId(s.positionPlayerId); return s.positionPlayerId; }
    private function Query(side : int, zone : int, tier : int, category : int, ignore : int, out ids : array<int>, optional types : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>; var s : SBetaGwentCardSnapshot; var i : int;
        ids.Clear(); if (types == 0) types = 4; game.GetCards(cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].card;
            if ((side != 0 && s.positionPlayerId != side) || (s.locationMask & zone) == 0 || (s.runtimeTierMask & tier) == 0
                || (s.runtimeTemplate.typeMask & types) == 0 || s.isWaitingToDie || (s.tokenMask & ignore) != 0
                || (category != 0 && !BetaGwentNorthernCategory(s.runtimeTemplate.templateId, category) && !(category == 3 && game.FindCard(s.instanceId).northernCrew))) continue;
            ids.PushBack(s.instanceId);
        }
    game.PhysicalOrder096(ids);}
    private function Remove(out ids : array<int>, id : int)
    { var i : int; for (i = ids.Size() - 1; i >= 0; i -= 1) if (ids[i] == id) ids.Erase(i); }
    // Original Black Blood FilterCardCategory: any category16 (Vampire) or40
    // (Necrophage), mask1099511693312. unitTraits uses a different namespace
    // and must not select Witchers/Elves instead of these source categories.
    public function BlackBloodCategory(id : int) : bool
    { return id==112104 || id==112105 || id==132202 || id==132203 || id==132220 || id==132301 || id==132302 || id==132306 || id==132313 || id==132314 || id==200055 || id==200088 || id==200295 || id==201698; }
    private function Crew(source : CBetaGwentDuelCard) : int
    {
        var ids : array<int>; var s, t : SBetaGwentCardSnapshot; var i, count : int;
        s = source.Snapshot(); Query(s.positionPlayerId, s.locationMask, 15, 3, 8, ids);
        for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (Abs(t.locationIndex - s.locationIndex) == 1) count += 1; }
        return count;
    }
    private function Request(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, category : int, ignore : int, optional minimum : int, optional types : int)
    {
        var ids, deck, valid : array<int>; var i, j, mode, kind : int; var s, t, u : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition;
        s = source.Snapshot(); d = source.Definition(); mode = d.specialMode; Query(side, zone, tier, category, ignore, ids, types);
        kind = 0; if ((zone & 7) == 0) kind = 2;
        if (mode == 122 || mode == 135) Query(Side(source), 16, 2, 0, 0, deck);
        for (i = 0; i < ids.Size(); i += 1)
        {
            t = game.FindCard(ids[i]).Snapshot();
            if (source.monsterIds.Contains(ids[i])) continue;
            if(mode==134 && game.IsExecutingCard(game.FindCard(ids[i])))continue;
            if ((mode == 122 || mode == 135 || mode == 141 || mode == 126) && t.instanceId == s.instanceId) continue;
            if (mode == 122 || mode == 135)
            {
                for (j = 0; j < deck.Size(); j += 1) { u = game.FindCard(deck[j]).Snapshot(); if (u.runtimeTemplate.templateId == t.runtimeTemplate.templateId) break; }
                if (j == deck.Size()) continue;
            }
            if (mode == 125 && t.power.armor <= 0) continue;
            if (mode == 145 && (t.tokenMask & 8) == 0) continue;
            if (mode == 149 && !BlackBloodCategory(t.runtimeTemplate.templateId)) continue;
            valid.PushBack(ids[i]);
        }
        game.MonsterRequest(source, valid, kind, minimum, 1);
    }
    private function CreateChoice(source : CBetaGwentDuelCard, pool : int, randomThree : bool)
    { var ids : array<int>; BetaGwentNorthernPool(pool, ids); if (randomThree) { game.ShuffleIds(ids); while (ids.Size() > 3) ids.Erase(ids.Size()-1); } game.MonsterRequest(source, ids, 1, 1, 1); }
    public function Played(source : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var s : SBetaGwentCardSnapshot;
        d = source.Definition(); s = source.Snapshot(); source.monsterStage = 0; source.monsterIds.Clear(); source.monsterRemaining = Max(1, d.specialCount);
        BetaGwentLog("DUEL_NORTH_PLAY template=" + source.TemplateId() + " mode=" + d.specialMode);
        if (d.specialMode <= 124) PlayedLow(source); else PlayedHigh(source);
    }
    private function PlayedLow(source : CBetaGwentDuelCard)
    {
        var d, td : SBetaGwentDuelDefinition; var s, t : SBetaGwentCardSnapshot; var ids, hand, rowIds : array<int>; var i, side, mode, row : int;
        d = source.Definition(); s = source.Snapshot(); side = Side(source); mode = d.specialMode;
        if (mode == 101 || mode == 111) { if (source.TemplateId() == 201624) game.QueueTimer(source, 2, 1); game.MonsterComplete(source); return; }
        if (mode == 102) { Request(source, BetaGwentOpponentId(side), 7, 15, 0, 264, d.targetMinimum); return; }
        if (mode == 103)
        {
            i = 8; if (source.TemplateId() == 200033) i = 10;
            if (i == 10)
            { Query(side,16,2,i,0,ids,2); if (ids.Size() == 0) { game.MonsterComplete(source); return; } game.MonsterPlayExisting(source,game.FindCard(ids[game.RandomIndex(ids.Size())])); return; }
            Query(side,16,6,i,0,ids,14);game.ShuffleIds(ids);game.MonsterRequest(source,ids,2,0,1);return;
        }
        if (mode == 104 || mode == 112)
        {
            game.NorthPile(side, 16, ids);
            for (i = 0; i < ids.Size(); i += 1)
            {
                t = game.FindCard(ids[i]).Snapshot();
                if (mode == 112 && (t.runtimeTemplate.typeMask != 4 || (t.runtimeTierMask & 6) == 0 || BetaGwentDuelSpying(t.runtimeTemplate.templateId))) continue;
                source.monsterIds.PushBack(ids[i]); if (source.monsterIds.Size() >= (BetaGwentNorthPick(mode == 104,2,1))) break;
            }
            PlayNext(source); return;
        }
        if (mode == 105) { CreateChoice(source, source.TemplateId(), source.TemplateId() == 201582 || source.TemplateId() == 201595); return; }
        if (mode == 106) { source.monsterRemaining = 3;game.monsters.nilf.SourceCards(side,16,14,4,0,0,source,ids);source.choiceDeck=ids;game.ShuffleIds(source.choiceDeck);DeckBoostRequest(source);return; }
        if (mode == 107)
        {
            // Location.GetCards excludes the execution-stack owner and walks
            // row/index order before ListExt.Shuffle.
            for(row=1;row<=4;row*=2){game.VisibleRowEffectIds(side,row,rowIds);for(i=0;i<rowIds.Size();i+=1){t=game.FindCard(rowIds[i]).Snapshot();if((t.runtimeTemplate.typeMask&4)!=0 && (t.runtimeTierMask&15)!=0)ids.PushBack(rowIds[i]);}}
            game.ShuffleIds(ids);
            for (i = 0; i < ids.Size() && i < 5; i += 1) game.MonsterPower(source, game.FindCard(ids[i]), d.amount);
            game.MonsterComplete(source); return;
        }
        if (mode == 108)
        {
            if (s.timerValue != 1) { game.MonsterComplete(source); return; }
            Query(side,16,14,0,8,ids,14); source.choiceDeck=ids; game.ShuffleIds(ids); while (ids.Size() > 2) ids.Erase(ids.Size()-1); source.monsterIds = ids;
            if(ids.Size()>0)game.MonsterRequest(source, ids, 2, 1, 1);else{game.QueueTimer(source,0,1);game.MonsterComplete(source);}return;
        }
        if (mode == 109)
        {
            Query(side,16,14,0,0,ids,14); Query(side,8,15,0,0,hand,14);
            if(ids.Size()==0 || hand.Size()==0){game.MonsterComplete(source);return;}
            source.choiceDeck=ids; source.monsterRemaining=Min(2,Min(ids.Size(),hand.Size()));
            Request(source,side,8,15,0,0,0,14); return;
        }
        if (mode == 110) { Request(source, side, 8, 6, 0, 0, 0, 2); return; }
        if (mode == 113) { ReturnWeakest(source, side); ReturnWeakest(source, BetaGwentOpponentId(side)); game.MonsterComplete(source); return; }
        if (mode == 114) { Request(source, 0, 7, 15, 0, 256, d.targetMinimum); return; }
        if (mode == 115) { source.monsterRemaining = 3; Request(source, side, 32, 6, 0, 0, 0); return; }
        if (mode == 116) { game.NorthClearHazard(side, s.locationMask); game.MonsterComplete(source); return; }
        if (mode == 117 || mode == 118 || mode == 144)
        { source.monsterRemaining = Crew(source) + 1; Request(source, BetaGwentOpponentId(side), 7, 15, 0, 264, d.targetMinimum); return; }
        if (mode == 119) { source.monsterStored = d.amount + Crew(source); Request(source, BetaGwentOpponentId(side), 7, 15, 0, 264, 0); return; }
        if (mode == 120) { game.MonsterPower(source, source, d.amount * (Crew(source) + 1)); game.MonsterComplete(source); return; }
        if (mode == 121) { HunterBoost(source); game.MonsterComplete(source); return; }
        if (mode == 122) { Request(source, side, 7, 2, 0, 264, 0); return; }
        if (mode == 123 || mode == 124)
        {
            Query(side, BetaGwentNorthPick(mode == 123,31,7), 15, BetaGwentNorthPick(mode == 123,4,2), 8, ids);
            for (i = 0; i < ids.Size(); i += 1)
            {
                t = game.FindCard(ids[i]).Snapshot(); if (t.instanceId == s.instanceId) continue;
                if (mode == 123 && (t.power.currentPower != s.power.currentPower || !BetaGwentNorthernCategory(t.runtimeTemplate.templateId,4))) continue;
                game.MonsterOperation(source, game.FindCard(ids[i]), 1, d.amount, BetaGwentNorthPick(mode == 123,31,7));
            }
            if(mode==123)game.MonsterPower(source,source,d.amount);
            game.MonsterComplete(source); return;
        }
        game.FailAbility("Неизвестная способность Севера.");
    }
    private function PlayedHigh(source : CBetaGwentDuelCard)
    {
        var ids, rowIds, hand : array<int>; var d : SBetaGwentDuelDefinition; var s, t : SBetaGwentCardSnapshot; var i, side, mode, sum : int;
        d = source.Definition(); s = source.Snapshot(); side = Side(source); mode = d.specialMode;
        if (mode == 125) { Request(source, 0, 7, 15, 0, 264, 0); return; }
        if (mode == 126) { Request(source, side, 7, 6, 1, 0, 0); return; }
        if (mode == 127)
        {
            i = source.TemplateId(); if (i == 122401) i = 122402; else if (i == 122402) i = 122401;
            game.NorthSummonCopies(source, i); game.MonsterComplete(source); return;
        }
        if (mode == 128)
        {
            Query(side,16,2,0,0,ids,2); Query(side,8,14,0,0,hand,14);
            if(ids.Size()==0 || hand.Size()==0){game.MonsterComplete(source);return;}
            source.monsterRemaining=ids.Size()+1; Request(source,side,8,14,0,0,0,14); return;
        }
        if (mode == 129) { source.monsterStored = d.amount + Crew(source); Request(source, BetaGwentOpponentId(side), 7, 15, 0, 264, 0); return; }
        if (mode == 130)
        {
            Query(side, 16, 14, 0, 0, ids);
            for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if(t.power.currentPower<=t.power.basePower+t.power.permanentPower)continue; sum += t.power.currentPower-t.power.basePower; game.MonsterOperation(source, game.FindCard(ids[i]), 18, 0, 16); }
            game.MonsterPower(source, source, sum); game.MonsterComplete(source); return;
        }
        if (mode == 131)
        {
            Query(0, 7, 15, 0, 8, ids);
            for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (t.instanceId == s.instanceId) continue; sum += t.power.armor; game.MonsterOperation(source, game.FindCard(ids[i]), 16, 0, 7); }
            game.MonsterPower(source, source, (sum + 1) / 2); game.MonsterComplete(source); return;
        }
        if (mode == 132) { Request(source, 0, 7, 15, 0, 264, 0); return; }
        if (mode == 133)
        {
            Query(side, 31, 14, 0, 8, ids);
            for (i = 0; i < ids.Size(); i += 1)
            { t = game.FindCard(ids[i]).Snapshot(); if (t.instanceId != s.instanceId && !BetaGwentDuelSpying(t.runtimeTemplate.templateId)) game.MonsterOperation(source, game.FindCard(ids[i]), 1, d.amount, 31); }
            game.MonsterComplete(source); return;
        }
        if (mode == 134) { source.monsterRemaining = 2; Request(source, 0, 7, 15, 0, 256, 0); return; }
        if (mode == 135) { Request(source, side, 7, 2, 5, 256, 1); return; }
        if (mode == 136) { Request(source, side, 32, 2, 7, 0, 1); return; }
        if (mode == 137) { Request(source, BetaGwentOpponentId(side), 7, 15, 0, 264, 1); return; }
        if (mode == 138)
        {
            Query(BetaGwentOpponentId(side), 7, 15, 0, 8, ids);
            for (i = 0; i < ids.Size(); i += 1) game.MonsterPower(source, game.FindCard(ids[i]), -d.amount);
            game.FlushDeaths();
            for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (game.UnitDied(t)) { sum = game.NorthDeathRow(ids[i]); if ((t.locationMask & 7) != 0) sum = t.locationMask; if (sum > 0 && !rowIds.Contains(sum)) rowIds.PushBack(sum); } }
            for (i = 0; i < rowIds.Size(); i += 1) game.MonsterWeather(BetaGwentOpponentId(side), rowIds[i], 32);
            game.MonsterComplete(source); return;
        }
        if (mode == 139 || mode == 149)
        { ids.PushBack(BetaGwentNorthPick(mode == 139,201719,201721)); ids.PushBack(BetaGwentNorthPick(mode == 139,201720,201722)); game.MonsterRequest(source, ids, 1, 1, 1); return; }
        if (mode == 140) { if (source.playFromLocation == 16) game.MonsterPower(source, source, d.amount); game.MonsterComplete(source); return; }
        if (mode == 141) { Request(source, side, 7, 15, 7, 264, 1); return; }
        if (mode == 142)
        { game.NorthPile(side, 16, ids); for (i = 0; i < ids.Size(); i += 1) { t = game.FindCard(ids[i]).Snapshot(); if (t.runtimeTemplate.typeMask == 2 && t.runtimeTierMask == 2 && BetaGwentNorthernCategory(t.runtimeTemplate.templateId,9)) rowIds.PushBack(ids[i]); }
          // Beta SetVar -> CardListShuffle -> GetRange(0,2): two random candidates, not the top two.
          if (rowIds.Size() > 0) game.ShuffleIds(rowIds);
          for (i = 0; i < rowIds.Size() && i < 2; i += 1) source.monsterIds.PushBack(rowIds[i]);
          while (source.monsterIds.Size() > 2) source.monsterIds.Erase(source.monsterIds.Size()-1); game.MonsterRequest(source, source.monsterIds, 2, 1, 1); return; }
        if (mode == 143)
        { Query(side, s.locationMask, 15, 7, 8, ids); Remove(ids, s.instanceId); if (ids.Size() == 0) { game.MonsterComplete(source); return; } Request(source, 0, 7, 15, 0, 264, 0); return; }
        if (mode == 144) { source.monsterRemaining = Crew(source) + 1; Request(source, BetaGwentOpponentId(side), 7, 15, 0, 264, 1); return; }
        if (mode == 145) { Request(source, BetaGwentOpponentId(side), 7, 15, 0, 0, 1); return; }
        if (mode == 146 || mode == 147) { game.MonsterComplete(source); return; }
        if (mode == 148) { ids.PushBack(1); ids.PushBack(2); ids.PushBack(4); game.MonsterRequest(source, ids, 3, 1, 1); return; }
        game.FailAbility("Неизвестная способность Севера.");
    }
    public function Select(source : CBetaGwentDuelCard, id : int)
    {
        var target : CBetaGwentDuelCard; var d : SBetaGwentDuelDefinition; var s, t : SBetaGwentCardSnapshot; var mode : int;
        d = source.Definition(); mode = d.specialMode; s = source.Snapshot(); target = game.FindCard(id);
        if(mode==106){if(id>0){source.monsterIds.PushBack(id);source.monsterRemaining-=1;if(source.monsterRemaining>0){DeckBoostRequest(source);return;}}CommitDeckBoost(source);return;}
        if (mode == 105) { if (id != 0) game.MonsterCreate(source,id); else game.MonsterComplete(source); return; }
        if(mode==109 && id==0){FinishBianca(source,Side(source));return;}
        if(mode==128 && source.monsterStage==0 && id==0){game.MonsterComplete(source);return;}
        if (mode == 139 || mode == 149)
        {
            if (source.monsterStage == 0)
            {
                source.monsterStage = 1;
                if (id == 201719 || id == 201721) { CreateChoice(source, source.TemplateId(), true); return; }
                if (mode == 139) { source.monsterStage = 2; Request(source,Side(source),16,6,12,0,0,2); }
                else { source.monsterStage = 2; Request(source,0,7,6,0,264,0); } return;
            }
            if (source.monsterStage == 1) { if (id > 0) game.MonsterCreate(source,id); else game.MonsterComplete(source); return; }
        }
        if (!target) { game.MonsterComplete(source); return; }
        t = target.Snapshot();
        if (SelectPile(source,target)) return;
        SelectBoard(source,target);
    }
    private function FinishBianca(source : CBetaGwentDuelCard, side : int)
    {
        var i, index : int;var ids : array<int>;var card : CBetaGwentDuelCard;
        for(i=0;i<source.monsterIds.Size();i+=1)
        {
            card=game.FindCard(source.monsterIds[i]);if(!card)continue;
            Query(side,16,14,0,0,ids,14);index=game.RandomIndex(ids.Size()+1);
            game.MoveInactiveToIndex(card,side,16,index);
        }
        game.DrawCaptured(side,source.choiceDeck,source.monsterIds.Size(),false);game.MonsterComplete(source);
    }
    private function SelectPile(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    {
        var d : SBetaGwentDuelDefinition; var s, t : SBetaGwentCardSnapshot; var ids : array<int>; var i, mode, side : int;
        d = source.Definition(); mode = d.specialMode; s = source.Snapshot(); t = target.Snapshot(); side = Side(source);
        if (mode == 103 || mode == 110 || mode == 136 || mode == 142 || (mode == 139 && source.monsterStage == 2))
        { game.MonsterPlayExisting(source,target); return true; }
        if (mode == 106 || mode == 115)
        {
            source.monsterIds.PushBack(t.instanceId); source.monsterRemaining -= 1;
            if (mode == 106) game.MonsterOperation(source,target,1,d.amount,31); else game.NorthMoveInactive(target,side,16,true,game.DeckInsertionSlots(side,14,0));
            if (source.monsterRemaining > 0) { Request(source,side,BetaGwentNorthPick(mode == 106,16,32),BetaGwentNorthPick(mode == 106,14,6),0,0,0); return true; }
            game.MonsterComplete(source); return true;
        }
        if (mode == 108)
        {
            game.MoveInactiveToIndex(target,side,8,0); game.QueueTimer(source,0,1); game.MonsterComplete(source); return true;
        }
        if (mode == 109)
        {
            source.monsterIds.PushBack(t.instanceId);
            if(source.monsterIds.Size()>=source.monsterRemaining){FinishBianca(source,side);return true;}
            Request(source,side,8,15,0,0,0,14);return true;
        }
        if (mode == 128)
        {
            if(source.monsterStage==0)
            {
                source.monsterStage=1;game.MoveInactiveToIndex(target,side,16,game.RandomIndex(source.monsterRemaining));
                Query(side,16,2,0,0,ids,2);game.MonsterRequest(source,ids,2,1,1);return true;
            }
            game.MoveInactiveToIndex(target,side,8,0);game.MonsterComplete(source);return true;
        }
        return false;
    }
    private function SelectBoard(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var ids, chosen : array<int>; var d, td : SBetaGwentDuelDefinition; var s, t, u : SBetaGwentCardSnapshot; var i, mode, damage, cached, nextRow : int;
        d = source.Definition(); td = target.Definition(); mode = d.specialMode; s = source.Snapshot(); t = target.Snapshot();
        if (mode == 102 || mode == 143)
        {
            game.MonsterPower(source,target,-d.amount);
            if (source.TemplateId() == 122104)
            {
                cached = t.instanceId;
                for (damage = 4; damage >= 1; damage -= 1)
                { game.FlushDeaths(); Query(BetaGwentOpponentId(Side(source)),7,15,0,8,ids); Remove(ids,cached);
                  if (ids.Size() > 0) { cached = ids[game.RandomIndex(ids.Size())]; game.MonsterPower(source,game.FindCard(cached),-damage); } }
            }
        }
        else if (mode == 114) { game.QueueResetPower(source,target); game.MonsterOperation(source,target,6,0,7); }
        else if (mode == 117)
        {
            Query(t.positionPlayerId,7,15,0,8,ids);
            for (i = 0; i < ids.Size(); i += 1) { u = game.FindCard(ids[i]).Snapshot(); if (u.instanceId != t.instanceId && u.power.currentPower == t.power.currentPower) chosen.PushBack(u.instanceId); }
            game.ShuffleIds(chosen); while (chosen.Size() > 4) chosen.Erase(chosen.Size()-1); chosen.Insert(0,t.instanceId);
            for (i = 0; i < chosen.Size(); i += 1) game.MonsterPower(source,game.FindCard(chosen[i]),-d.amount);
            game.FlushDeaths(); source.monsterRemaining -= 1;
            if (source.monsterRemaining > 0) { Request(source,t.positionPlayerId,7,15,0,264,d.targetMinimum); return; }
        }
        else if (mode == 118 || mode == 144)
        {
            game.MonsterPower(source,target,-d.amount); game.FlushDeaths();
            if (mode == 144 && (t.locationMask & 3) != 0) game.QueueRelocation(target,t.positionPlayerId,t.locationMask*2,false);
            source.monsterRemaining -= 1;
            if (source.monsterRemaining > 0) { Request(source,BetaGwentOpponentId(Side(source)),7,15,0,264,d.targetMinimum); return; }
        }
        else if (mode == 119)
        {
            Query(t.positionPlayerId,t.locationMask,15,0,8,ids);
            for (i = 0; i < ids.Size(); i += 1) { u = game.FindCard(ids[i]).Snapshot(); if (Abs(u.locationIndex-t.locationIndex)<=1) game.MonsterPower(source,game.FindCard(ids[i]),-source.monsterStored); }
        }
        else if (mode == 122 || mode == 135 || mode == 132)
        {
            if (mode == 132) { game.QueueResetPower(source,target); if (!BetaGwentNorthernCategory(t.runtimeTemplate.templateId,6)) { game.MonsterComplete(source); return; } }
            Query(Side(source),16,BetaGwentNorthPick(mode == 132,14,2),0,0,ids);
            for (i = 0; i < ids.Size(); i += 1) { u = game.FindCard(ids[i]).Snapshot(); if (u.runtimeTemplate.templateId == t.runtimeTemplate.templateId) source.monsterIds.PushBack(ids[i]); }
            if (mode == 122) { if (source.monsterIds.Size() > 0) { i = source.monsterIds[game.RandomIndex(source.monsterIds.Size())]; source.monsterIds.Clear(); source.monsterIds.PushBack(i); } }
            else if (mode == 132) { game.ShuffleIds(source.monsterIds); while (source.monsterIds.Size()>1) source.monsterIds.Erase(source.monsterIds.Size()-1); }
            PlayNext(source); return;
        }
        else if (mode == 125) { game.MonsterOperation(source,target,16,0,7); game.MonsterPower(source,source,t.power.armor); }
        else if (mode == 126) { game.MonsterOperation(source,target,13,999,7); game.FlushDeaths(); game.NorthRepeatPlay(source,target); return; }
        else if (mode == 129)
        {
            cached = t.power.currentPower; game.MonsterPower(source,target,-source.monsterStored); game.FlushDeaths(); u = target.Snapshot();
            if (source.monsterStage == 0 && game.UnitDied(u))
            { source.monsterStage = 1; source.monsterStored = 3; Request(source,BetaGwentOpponentId(Side(source)),7,15,0,264,0); return; }
        }
        else if (mode == 134)
        { source.monsterIds.PushBack(t.instanceId);
          source.monsterRemaining -= 1; if (source.monsterRemaining > 0) { Request(source,0,7,15,0,256,0); return; }
          for(i=0;i<source.monsterIds.Size();i+=1)game.MonsterOperation(source,game.FindCard(source.monsterIds[i]),6,0,7);
          for(i=0;i<source.monsterIds.Size();i+=1){target=game.FindCard(source.monsterIds[i]);t=target.Snapshot();if(t.positionPlayerId!=Side(source))game.MonsterPower(source,target,-d.amount);} }
        else if (mode == 137) game.MonsterDuel(source,target,0,0);
        else if (mode == 141) { if (target.TemplateId() == 201625) game.MonsterOperation(source,target,20,0,7); else game.QueueTransform(source,target,201625); }
        else if (mode == 145 || (mode == 149 && source.monsterStage == 2)) game.QueueDestroy(target);
        game.MonsterComplete(source);
    }
    private function PlayNext(source : CBetaGwentDuelCard)
    {
        var id : int; var target : CBetaGwentDuelCard;
        if (source.monsterIds.Size()==0) { game.MonsterComplete(source); return; }
        id=source.monsterIds[0];source.monsterIds.Erase(0);target=game.FindCard(id);
        if (source.MonsterMode()==112) { game.MonsterOperation(source,target,15,5,16); game.FlushDeaths(); }
        game.MonsterPlayExisting(source,target);
    }
    public function ChildReturned(source : CBetaGwentDuelCard) : bool
    {
        var child : CBetaGwentDuelCard; var d : SBetaGwentDuelDefinition;
        d=source.Definition();child=source.TakePlayedChild();
        if (d.specialMode==110 && child) game.MonsterDraw(Side(source),false);
        if (d.specialMode==149 && source.monsterStage==1 && child) game.MonsterPower(source,child,2);
        if ((d.specialMode==104 || d.specialMode==135) && source.monsterIds.Size()>0) { PlayNext(source);return true; }
        return false;
    }
    private function ReturnWeakest(source : CBetaGwentDuelCard, side : int)
    {
        var ids, valid : array<int>;var i, least : int;var t : SBetaGwentCardSnapshot;
        Query(side,7,6,0,8,ids);least=2147483647;
        for(i=ids.Size()-1;i>=0;i-=1)if(game.IsExecutingCard(game.FindCard(ids[i])))ids.Erase(i);
        for (i=0;i<ids.Size();i+=1) { t=game.FindCard(ids[i]).Snapshot();least=Min(least,t.power.currentPower); }
        for (i=0;i<ids.Size();i+=1) { t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower==least) valid.PushBack(ids[i]); }
        if(valid.Size()>0) game.NorthMoveInactive(game.FindCard(valid[game.RandomIndex(valid.Size())]),side,16,true,game.DeckInsertionSlots(side,14,BetaGwentNorthPick(side==Side(source),0,8)));
    }
    private function HunterBoost(source : CBetaGwentDuelCard)
    {
        var ids : array<int>;var i : int;var t : SBetaGwentCardSnapshot;
        Query(Side(source),31,14,0,8,ids);
        for(i=0;i<ids.Size();i+=1) { t=game.FindCard(ids[i]).Snapshot();if(t.runtimeTemplate.templateId==122306) game.MonsterOperation(source,game.FindCard(ids[i]),1,1,31); }
    }
    public function Row(source : CBetaGwentDuelCard, side : int, row : int)
    {
        var ids, rows : array<int>;var i, j : int;var t : SBetaGwentCardSnapshot;
        game.VisibleRowEffectIds(side,row,ids);
        for(i=0;i<ids.Size();i+=1)
        { rows.Clear();for(j=1;j<=4;j*=2) if(j!=row && game.CountLocation(side,j)<9) rows.PushBack(j);
          if(rows.Size()>0) { game.QueueRelocation(game.FindCard(ids[i]),side,rows[game.RandomIndex(rows.Size())],false);game.FlushDeaths(); } }
        game.MonsterComplete(source);
    }
    public function Event(item : CBetaGwentDuelEvent)
    {
        var source, target : CBetaGwentDuelCard;var s, t, u : SBetaGwentCardSnapshot;var ids, valid, deck : array<int>;var i, j, id, row, kind, least : int;
        var d : SBetaGwentDuelDefinition;var m : SBetaGwentMatchSnapshot;
        source=game.FindCard(item.source.instanceId);if(!source)return;s=source.Snapshot();id=source.TemplateId();kind=item.rowToken;
        if((s.tokenMask&12)!=0 || s.isWaitingToDie)return; d=source.Definition();
        if(kind==1)
        {
            if(id==122213)
            { for(row=1;row<=4;row*=2) if(row!=s.locationMask && game.CountLocation(s.positionPlayerId,row)<9) ids.PushBack(row);
              row=s.locationMask;if(ids.Size()>0) { row=ids[game.RandomIndex(ids.Size())];game.QueueRelocation(source,s.positionPlayerId,row,false); }
              Query(s.positionPlayerId,row,15,0,8,ids);Remove(ids,s.instanceId);for(i=0;i<ids.Size();i+=1)game.MonsterPower(source,game.FindCard(ids[i]),1); }
            if(id==122313 && s.locationMask==16 && game.Score(BetaGwentOpponentId(s.positionPlayerId))-game.Score(s.positionPlayerId)>25)
            {
                Query(s.positionPlayerId,16,2,0,0,ids,4);game.NorthPile(s.positionPlayerId,16,deck);
                for(i=0;i<deck.Size();i+=1)if(ids.Contains(deck[i])){target=game.FindCard(deck[i]);u=target.Snapshot();if(u.runtimeTemplate.templateId==s.runtimeTemplate.templateId)game.RandomPositionMove(target,s.positionPlayerId,false);}
            }
        }
        else if(kind==2)
        {
            if(id==122308 && s.power.armor==0) { game.MonsterPower(source,source,2);game.MonsterOperation(source,source,15,2,7); }
            if(id==122315) { Query(BetaGwentOpponentId(s.positionPlayerId),7,15,0,8,ids);if(ids.Size()>0)game.MonsterPower(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),-1); }
            if(id==123301 && s.power.armor>0)
            { Query(s.positionPlayerId,s.locationMask,15,0,8,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(Abs(t.locationIndex-s.locationIndex)==1)game.MonsterPower(source,game.FindCard(ids[i]),1);} }
            if(id==200529){source.Power().SetBasePower(1);u=source.Snapshot();game.NilfPowerChanged(source,source,s,u,19);source.SetWaiting(false);game.RandomPositionMove(source,s.positionPlayerId,false);}
            if(id==112207 && source.monsterOnce>0) { source.monsterOnce=0;game.NorthResurrect(source,s.power.currentPower,source.monsterStored,source.monsterStage,false); }
        }
        else if(kind==3)
        {
            if(id==112207) { source.monsterStored=item.source.locationMask;source.monsterStage=item.source.locationIndex;source.monsterOnce=1; }
            if(id==112215) { Query(BetaGwentOpponentId(item.source.positionPlayerId),7,15,0,8,ids);game.ShuffleIds(ids);for(i=0;i<ids.Size() && i<5;i+=1)game.MonsterPower(source,game.FindCard(ids[i]),5); }
            if(id==122206)
            { Query(item.source.positionPlayerId,item.source.locationMask,15,0,8,ids);least=2147483647;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();least=Min(least,t.power.currentPower);}
              if(ids.Size()>0)for(i=0;i<ids.Size();i+=1)game.MonsterOperation(source,game.FindCard(ids[i]),11,least,7); }
        }
        else if(kind==4)
        {
            target=game.FindCard(item.cause.instanceId);if(!target)return;t=target.Snapshot();
            if(id==122306 && t.runtimeTemplate.templateId==122306 && (item.cause.locationMask&248)!=0 && t.positionPlayerId==s.positionPlayerId && (t.locationMask&7)!=0)HunterBoost(source);
            if(id==122309 && t.instanceId!=s.instanceId && t.positionPlayerId==s.positionPlayerId && (t.locationMask&7)!=0)
            { game.MonsterPower(source,target,1);if(BetaGwentNorthernCategory(t.runtimeTemplate.templateId,1))game.MonsterOperation(source,target,15,1,7); }
        }
        else if(kind==5)
        {
            target=game.FindCard(item.cause.instanceId);if(!target)return;t=target.Snapshot();
            if(id==201624 && s.timerValue==1 && t.positionPlayerId==s.positionPlayerId && BetaGwentNorthernCategory(t.runtimeTemplate.templateId,9))
            { game.QueueTimer(source,0,1);game.NorthPhantom(source); }
            if(id==122311 && s.locationMask==16 && t.positionPlayerId==s.positionPlayerId && t.runtimeTemplate.templateId!=s.runtimeTemplate.templateId && BetaGwentNorthernCategory(t.runtimeTemplate.templateId,4))
            {
                Query(s.positionPlayerId,16,15,0,264,valid,4);game.NorthPile(s.positionPlayerId,16,deck);ids.Clear();
                for(i=0;i<deck.Size();i+=1)if(valid.Contains(deck[i])){target=game.FindCard(deck[i]);u=target.Snapshot();if(u.runtimeTemplate.templateId==s.runtimeTemplate.templateId && u.power.currentPower==t.power.currentPower)ids.PushBack(deck[i]);}
                if(ids.Size()>0){target=game.FindCard(ids[game.RandomIndex(ids.Size())]);game.RandomPositionMove(target,s.positionPlayerId,true);}
            }
        }
        else if(kind==6 && id==122317)game.MonsterPower(source,source,5);
        else if(kind==7 && id==122101 && item.cause.positionPlayerId!=s.positionPlayerId)game.MonsterOperation(source,source,1,1,31);
    }
}

function BetaGwentNorthPick(condition : bool, yes : int, no : int) : int
{ if (condition) return yes; return no; }
