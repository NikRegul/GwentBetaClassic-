// Concrete consumers of strict Beta 0.9.24 graphs. Revealed is original token64.
class CBetaGwentNilfReaction extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable; public var source : CBetaGwentDuelCard; public var kind, side : int; }

class CBetaGwentDuelNilf extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var dependencies : CBetaGwentNilfDependencies;
    public function Initialize(owner : CBetaGwentDuelSession) { game = owner;dependencies=new CBetaGwentNilfDependencies in this;dependencies.Initialize(owner,this); }
    private function Side(source : CBetaGwentDuelCard) : int { return game.NorthActingSide(source); }
    private function Query(side : int, zone : int, tier : int, types : int, ignore : int, flags : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var s : SBetaGwentCardSnapshot;var i : int;var spy : bool;
        ids.Clear();game.GetCards(cards);
        for(i=0;i<cards.Size();i+=1)
        {
            s=cards[i].card;if((side!=0 && s.positionPlayerId!=side) || (s.locationMask&zone)==0 || (s.runtimeTierMask&tier)==0 || (s.runtimeTemplate.typeMask&types)==0 || (s.tokenMask&ignore)!=0 || s.isWaitingToDie)continue;
            spy=(s.tokenMask&128)!=0;if((s.locationMask&7)==0)spy=BetaGwentDuelSpying(s.runtimeTemplate.templateId);
            if((flags&1)!=0 && (s.tokenMask&64)==0)continue;
            if((flags&2)!=0 && (s.tokenMask&64)!=0)continue;
            if((flags&4)!=0 && !spy)continue;if((flags&8)!=0 && spy)continue;
            if((flags&16)!=0 && source && game.FindCard(s.instanceId)==source)continue;
            if((flags&32)!=0 && s.runtimeTemplate.factionMask!=1)continue;
            if((flags&64)!=0 && s.power.currentPower>3)continue;
            if((flags&128)!=0 && !BetaGwentNorthernCategory(s.runtimeTemplate.templateId,2))continue;
            if((flags&256)!=0 && !BetaGwentNorthernCategory(s.runtimeTemplate.templateId,1))continue;
            if((flags&512)!=0 && !BetaGwentNorthernCategory(s.runtimeTemplate.templateId,11))continue;
            if((flags&1024)!=0 && !BetaGwentNorthernCategory(s.runtimeTemplate.templateId,12))continue;
            if((flags&2048)!=0 && !BetaGwentNorthernCategory(s.runtimeTemplate.templateId,8))continue;
            if((flags&4096)!=0 && s.runtimeTemplate.templateId==201617)continue;
            if((flags&8192)!=0 && !BetaGwentNilfDwarf(s.runtimeTemplate.templateId))continue;
            if((flags&16384)!=0 && !BetaGwentNilfElf(s.runtimeTemplate.templateId))continue;
            if((flags&65536)!=0 && !BetaGwentNilfSpell(s.runtimeTemplate.templateId) && !BetaGwentNorthernCategory(s.runtimeTemplate.templateId,11))continue;
            if((flags&131072)!=0 && BetaGwentNorthernCategory(s.runtimeTemplate.templateId,7))continue;
            if((flags&262144)!=0 && !BetaGwentDuelHasKilledAbility(s.runtimeTemplate.templateId))continue;
            if(source && source.monsterIds.Contains(s.instanceId))continue;
            ids.PushBack(s.instanceId);
        }
    }
    private function Request(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, ignore : int, flags : int, optional minimum : int)
    { var ids : array<int>;Query(side,zone,tier,types,ignore,flags,source,ids);minimum=BetaGwentNilfMinimum(source.TemplateId());game.MonsterRequest(source,ids,BetaGwentNorthPick((zone&7)!=0,0,2),minimum,1); }
    private function Choose(source : CBetaGwentDuelCard, pool : int, randomThree : bool)
    { var ids : array<int>;BetaGwentNilfPool(pool,ids);if(randomThree){game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);}game.MonsterRequest(source,ids,1,1,1); }
    private function Top(source : CBetaGwentDuelCard, side : int, tier : int, types : int, flags : int, count : int, randomOrder : bool)
    {
        var ids, ordered, valid : array<int>;var i : int;
        Query(side,16,tier,types,0,flags,source,valid);game.NorthPile(side,16,ordered);
        for(i=0;i<ordered.Size();i+=1)if(valid.Contains(ordered[i]))ids.PushBack(ordered[i]);
        if(randomOrder)game.ShuffleIds(ids);while(ids.Size()>count)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,2,1,1);
    }
    private function Enemy(source : CBetaGwentDuelCard) { Request(source,BetaGwentOpponentId(Side(source)),7,15,4,264,0); }
    private function RainfarnCandidate(source : CBetaGwentDuelCard, card : CBetaGwentDuelCard) : bool
    {
        var s : SBetaGwentCardSnapshot; if (!card) return false; s=card.Snapshot();
        return s.positionPlayerId==Side(source) && s.locationMask==16 && !s.isWaitingToDie
            && (s.runtimeTierMask&6)!=0 && s.runtimeTemplate.typeMask==4 && BetaGwentDuelSpying(s.runtimeTemplate.templateId);
    }
    private function RainfarnRequest(source : CBetaGwentDuelCard)
    {
        var deck,valid : array<int>; var i : int;
        game.NorthPile(Side(source),16,deck);
        for(i=0;i<deck.Size();i+=1)if(RainfarnCandidate(source,game.FindCard(deck[i])))valid.PushBack(deck[i]);
        BetaGwentLog("DUEL_RAINFARN_POOL deck="+deck.Size()+" candidates="+valid.Size());
        game.MonsterRequest(source,valid,2,0,1);
    }
    private function Friendly(source : CBetaGwentDuelCard, flags : int) { Request(source,Side(source),7,15,4,264,flags); }
    public function Played(source : CBetaGwentDuelCard)
    {
        var id, side, enemy, i, j, maxPower : int;var s,t : SBetaGwentCardSnapshot;var ids,valid,rows : array<int>;var d : SBetaGwentDuelDefinition;
        if(source.MonsterMode()>=400){dependencies.Played(source);return;}
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();d=source.Definition();
        source.monsterStage=0;source.monsterStored=0;source.monsterIds.Clear();source.monsterRemaining=Max(1,d.specialCount);
        BetaGwentLog("DUEL_NILF_PLAY template="+id+" side="+side);
        if(id==162104){Request(source,side,32,1,4,0,0);return;}
        if(id==122106){Request(source,side,32,6,4,0,131072);return;}
        if(id==132106){Request(source,enemy,32,6,4,0,0);return;}
        if(id==200221){source.monsterRemaining=2;Request(source,side,32,2,4,0,262144);return;}
        if(id==122403){Top(source,side,2,14,512,2,true);return;}
        if(id==132407 || id==162301 || id==162312 || id==162212 || id==200294 || id==200296 || id==152312 || id==200219){game.MonsterComplete(source);return;}
        if(id==162101){source.monsterRemaining=2;Request(source,s.positionPlayerId,s.locationMask,15,4,256,16);return;}
        if(id==162102 || id==162305 || id==162306 || id==162308 || id==200124 || id==152304){Enemy(source);return;}
        if(id==162103){source.monsterRemaining=2;Request(source,side,8,14,14,64,0);return;}
        if(id==162105){Request(source,BetaGwentNorthPick(game.NilfTruce(),0,side),7,15,4,264,16);return;}
        if(id==162106){Request(source,side,16,14,14,0,0);return;}
        if(id==162107){if(game.NilfTruce()){game.MonsterPower(source,source,15);game.NilfDraw(enemy,2,true);}game.MonsterComplete(source);return;}
        if(id==162108){Request(source,enemy,16,14,14,0,0);return;}
        if(id==162201){if(game.NilfTruce()){game.NilfDraw(side,14,false);game.NilfDraw(enemy,14,true);}game.MonsterComplete(source);return;}
        if(id==162202){source.monsterRemaining=2;Request(source,0,32,6,14,0,0);return;}
        if(id==162203)
        {Query(enemy,8,14,12,64,0,source,ids);maxPower=-1;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();maxPower=Max(maxPower,t.power.currentPower);}for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower==maxPower)valid.PushBack(ids[i]);}if(valid.Size()>0){game.NilfReveal(game.FindCard(valid[game.RandomIndex(valid.Size())]),true);game.MonsterPower(source,source,maxPower);}game.MonsterComplete(source);return;}
        if(id==162204 || id==162208){source.monsterRemaining=BetaGwentNorthPick(id==162208,2,1);Request(source,0,7,15,4,BetaGwentNorthPick(id==162208,256,264),0);return;}
        if(id==162205 || id==200115)
        {Query(s.positionPlayerId,s.locationMask,15,4,0,16,source,ids);maxPower=-1;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationIndex==s.locationIndex-1){if(id==200115)game.MonsterPower(source,game.FindCard(ids[i]),-10);else maxPower=t.power.currentPower;}}if(id==162205 && maxPower>=0)for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationIndex==s.locationIndex+1)game.MonsterOperation(source,game.FindCard(ids[i]),11,maxPower,7);}game.MonsterComplete(source);return;}
        if(id==162206 || id==162209)
        {Query(enemy,7,15,4,264,0,source,ids);Query(enemy,8,14,4,0,1,source,valid);for(i=0;i<valid.Size();i+=1)ids.PushBack(valid[i]);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==162207 || id==162213 || id==201597){Choose(source,id,false);return;}
        if(id==162210)
        {if(s.timerValue==0){game.MonsterComplete(source);return;}game.NorthPile(side,16,ids);while(ids.Size()>2)ids.Erase(ids.Size()-1);source.monsterIds=ids;game.QueueTimer(source,0,1);for(i=0;i<ids.Size();i+=1)game.NilfTake(game.FindCard(ids[i]),side);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==162211){Top(source,side,6,4,8,1,false);return;}
        if(id==162302){ids.PushBack(1);ids.PushBack(2);ids.PushBack(4);game.MonsterRequest(source,ids,3,0,1);return;}
        if(id==162303){Request(source,0,8,6,12,0,1);return;}
        if(id==162304 || id==201780){Request(source,enemy,32,BetaGwentNorthPick(id==162304,2,6),4,BetaGwentNorthPick(id==162304,0,264),BetaGwentNorthPick(id==162304,0,128));return;}
        if(id==162307){Query(enemy,7,15,4,8,4,source,ids);game.MonsterPower(source,source,2*ids.Size());game.MonsterComplete(source);return;}
        if(id==162309){game.NorthClearHazard(side,s.locationMask);Query(side,7,15,4,264,0,source,ids);Query(side,8,14,12,0,1,source,valid);for(i=0;i<valid.Size();i+=1)ids.PushBack(valid[i]);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==162310){Request(source,0,7,15,4,264,4);return;}
        if(id==162311){game.NorthSummonCopies(source,id);game.MonsterComplete(source);return;}
        if(id==162313 || id==162315){Friendly(source,0);return;}
        if(id==162314){Top(source,side,2,4,0,2,true);return;}
        if(id==162316 || id==200163){source.monsterRemaining=BetaGwentNorthPick(id==200163,4,2);Request(source,0,8,15,14,64,0);return;}
        if(id==162317){RandomDamage(source,enemy,7,2,1);game.MonsterComplete(source);return;}
        if(id==162318)
        {Query(side,8,14,14,64,0,source,ids);maxPower=16;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();maxPower=Min(maxPower,t.runtimeTierMask);}for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.runtimeTierMask==maxPower)valid.PushBack(ids[i]);}if(valid.Size()>0)game.NilfReveal(game.FindCard(valid[game.RandomIndex(valid.Size())]),true);game.MonsterComplete(source);return;}
        if(id==162401){game.MonsterDeckCopies(enemy,200219,1);game.NorthPile(enemy,16,ids);for(i=ids.Size()-1;i>=0;i-=1)if(game.FindCard(ids[i]).TemplateId()==200219){game.MonsterTopDeck(game.FindCard(ids[i]));break;}game.MonsterComplete(source);return;}
        if(id==162402){game.QueueTimer(source,2,2);game.MonsterComplete(source);return;}
        if(id==163201){Request(source,enemy,7,15,4,264,0);return;}
        if(id==200031){Request(source,side,8,15,4,0,0);return;}
        if(id==200032){RainfarnRequest(source);return;}
        if(id==200041){Query(enemy,7,15,4,8,0,source,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationMask!=s.locationMask || (s.tokenMask&64)!=0)game.MonsterPower(source,game.FindCard(ids[i]),-1);}game.MonsterComplete(source);return;}
        if(id==200044 || id==201617)
        {Query(side,16,2,BetaGwentNorthPick(id==200044,14,12),0,BetaGwentNorthPick(id==200044,1024,4224),source,ids);if(ids.Size()>0)game.MonsterPlayExisting(source,game.FindCard(ids[game.RandomIndex(ids.Size())]));else game.MonsterComplete(source);return;}
        if(id==200050 || id==201580 || id==201583 || id==201589 || id==201585){Choose(source,id,true);return;}
        if(id==200071)
        {if(!game.NilfTruce()){game.MonsterComplete(source);return;}game.NorthPile(side,16,ids);game.NorthPile(enemy,16,valid);if(ids.Size()>0)source.monsterIds.PushBack(ids[0]);if(valid.Size()>0)source.monsterIds.PushBack(valid[0]);for(i=0;i<source.monsterIds.Size();i+=1)game.NilfTake(game.FindCard(source.monsterIds[i]),side);game.MonsterRequest(source,source.monsterIds,2,0,1);return;}
        if(id==200118){Request(source,0,7,15,4,264,0);return;}
        if(id==200162){Request(source,side,8,14,14,8,0);return;}
        if(id==200164){Top(source,side,15,14,0,3,false);return;}
        if(id==200227 || id==201616){source.monsterRemaining=BetaGwentNorthPick(id==200227,99,2);Request(source,0,8,14,BetaGwentNorthPick(id==200227,12,14),0,1);return;}
        if(id==200518){Request(source,0,8,14,12,256,1);return;}
        if(id==201601){i=game.NilfLastSpell(side);if(i>0)game.MonsterCreate(source,i);else game.MonsterComplete(source);return;}
        if(id==201603 || id==201662 || id==201653)
        {if(id==201603){ids.PushBack(201694);ids.PushBack(201695);}if(id==201662){ids.PushBack(201713);ids.PushBack(201714);}if(id==201653){ids.PushBack(201672);ids.PushBack(201673);}game.MonsterRequest(source,ids,1,1,1);return;}
        if(id==201609){Request(source,enemy,7,2,4,264,64);return;}
        if(id==201610){for(i=1;i<=4;i*=2)if(i!=s.locationMask){t=s;t.locationMask=i;t.locationIndex=-3;game.QueueSpawn(t,id,1);}game.MonsterComplete(source);return;}
        if(id==201612){Friendly(source,16);return;}
        if(id==201661){Friendly(source,128);return;}
        if(id==201664){Request(source,side,16,2,4,0,256);return;}
        if(id==200159){source.monsterRemaining=3;Request(source,side,16,14,14,0,0);return;}
        if(id==200160){Query(side,16,6,4,0,8,source,ids);maxPower=-1;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();maxPower=Max(maxPower,t.power.currentPower);}for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower==maxPower)valid.PushBack(ids[i]);}if(valid.Size()>0){i=valid[game.RandomIndex(valid.Size())];game.MonsterOperation(source,game.FindCard(i),12,2,31);game.FlushDeaths();game.MonsterPlayExisting(source,game.FindCard(i));}else game.MonsterComplete(source);return;}
        if(id==200161){RandomDamage(source,enemy,s.locationMask,1,9);game.MonsterComplete(source);return;}
        if(id==200165){Request(source,side,8,15,14,0,0);return;}
        if(id==200166){Request(source,side,32,6,2,0,0);return;}
        if(id==200167){Query(side,16,4,12,0,8,source,ids);Query(side,16,2,12,0,8192,source,valid);for(i=0;i<valid.Size();i+=1)ids.PushBack(valid[i]);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==152313){if(source.playFromLocation==32)game.MonsterOperation(source,source,12,3,7);game.MonsterComplete(source);return;}
        if(id==152315){source.monsterRemaining=3;Request(source,0,7,15,4,264,0);return;}
        if(id==200144){game.MonsterCreate(source,152406);return;}
        if(id==200020){Request(source,0,32,6,4,0,0);return;}
        if(id==200022){i=game.NilfLastUnit();if(i>0)game.MonsterCreate(source,i);else game.MonsterComplete(source);return;}
        if(id==201639){game.NilfInitialPool(enemy,ids);game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,1,1,1);return;}
        game.FailAbility("Способность не подключена: "+d.title);
    }
    private function RandomDamage(source : CBetaGwentDuelCard, side : int, zone : int, damage : int, count : int)
    {var ids : array<int>;var i : int;for(i=0;i<count;i+=1){Query(side,zone,15,4,8,0,NULL,ids);if(ids.Size()==0)return;game.MonsterPower(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),-damage);game.FlushDeaths();}}
    private function More(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, ignore : int, flags : int) : bool
    {source.monsterRemaining-=1;if(source.monsterRemaining<=0)return false;Request(source,side,zone,tier,types,ignore,flags);return true;}
    public function Select(source : CBetaGwentDuelCard, selected : int)
    {
        var target : CBetaGwentDuelCard;var s,t,u : SBetaGwentCardSnapshot;var id,side,enemy,i,j,amount : int;var ids,valid : array<int>;
        if(source.MonsterMode()>=400){dependencies.Select(source,selected);return;}
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();target=game.FindCard(selected);
        if(id==200032 && selected>0 && !RainfarnCandidate(source,target))
        {BetaGwentLog("DUEL_RAINFARN_REJECT_STALE card="+selected);RainfarnRequest(source);return;}
        if(id==162207 || id==162213 || id==201597 || id==200050 || id==201580 || id==201583 || id==201589 || id==201585 || id==201639 || id==200022)
        {if(selected>0)game.MonsterCreate(source,selected);else game.MonsterComplete(source);return;}
        if((id==201603 || id==201662 || id==201653) && source.monsterStage==0)
        {source.monsterStage=1;source.monsterStored=selected;
          if(id==201603){if(selected==201694)Request(source,enemy,7,1,4,264,0);else Request(source,side,16,6,10,0,2048);}
          if(id==201662){if(selected==201713)Enemy(source);else Request(source,0,7,6,4,264,32);}
          if(id==201653){if(selected==201672)Choose(source,201653,true);else Request(source,0,7,15,4,264,0);}return;}
        if(id==201653 && source.monsterStored==201672){if(selected>0)game.MonsterCreate(source,selected);else game.MonsterComplete(source);return;}
        if(id==162103 && selected==0){FinishVattier(source);return;}
        if((id==162210 || id==200071) && !target && source.monsterIds.Size()>0)target=game.FindCard(source.monsterIds[0]);
        if(id==200221 && selected==0){source.monsterStage=1;source.monsterStored=0;PlayRitualNext(source);return;}
        if(id==162101 && selected==0){LethoDrain(source);return;}if(!target){game.MonsterComplete(source);return;}t=target.Snapshot();if(selected==0)selected=t.instanceId;
        if(id==122403 || id==162314 || id==162211 || id==200032 || id==200164 || id==201664 || id==200166 || id==200167 || (id==201603 && source.monsterStored==201695))
        {game.MonsterPlayExisting(source,target);return;}
        if(id==162104){game.MonsterPlayExisting(source,target);return;}
        if(id==122106){game.MonsterOperation(source,target,2,2,32);if(!game.FlushEffects())return;game.MonsterPlayExisting(source,target);return;}
        if(id==200221){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){Request(source,side,32,2,4,0,262144);return;}source.monsterStage=1;source.monsterStored=0;PlayRitualNext(source);return;}
        if(id==162304 || id==201780 || id==132106){game.NorthMoveInactive(target,side,32,false);game.MonsterPlayExisting(source,target);return;}
        if(id==162101)
        {source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){Request(source,s.positionPlayerId,s.locationMask,15,4,256,16);return;}LethoDrain(source);return;}
        if(id==162102){if((t.tokenMask&128)!=0)game.QueueDestroy(target);else game.MonsterPower(source,target,-4);}
        else if(id==162103){source.monsterIds.PushBack(selected);game.NilfReveal(target,true);source.monsterRemaining-=1;if(source.monsterRemaining>0){Request(source,side,8,14,14,64,0);return;}FinishVattier(source);return;}
        else if(id==162105)
        {if(source.monsterStage==1){game.MonsterPlayExisting(source,target);return;}game.QueueDestroy(target);game.FlushDeaths();if(t.positionPlayerId==side){source.monsterStage=1;Top(source,side,14,14,0,1,false);return;}game.NilfDraw(enemy,2,true);}
        else if(id==162106){game.MonsterTopDeck(target);if(!BetaGwentDuelSpying(t.runtimeTemplate.templateId))game.MonsterOperation(source,target,1,5,31);}
        else if(id==162108)game.NilfBottom(target);
        else if(id==162202){source.monsterIds.PushBack(selected);game.NorthMoveInactive(target,t.positionPlayerId,16,false);if(More(source,0,32,6,14,0,0))return;}
        else if(id==162204){game.QueueResetPower(source,target);game.MonsterOperation(source,target,12,BetaGwentNorthPick(t.positionPlayerId==side,3,-3),7);}
        else if(id==162208){source.monsterIds.PushBack(selected);game.MonsterOperation(source,target,6,0,7);if(More(source,0,7,15,4,256,0))return;}
        else if(id==162206){Query(enemy,16,14,4,8,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==t.runtimeTemplate.templateId)game.NorthMoveInactive(game.FindCard(ids[i]),enemy,32,false);}
        else if(id==162209){if(t.locationMask==8)game.MonsterOperation(source,target,11,1,8);else game.MonsterPower(source,target,-7);}
        else if(id==162210 || id==200071)
        {for(i=0;i<source.monsterIds.Size();i+=1){target=game.FindCard(source.monsterIds[i]);if(source.monsterIds[i]==selected)continue;if(id==162210)game.NilfBottom(target);else game.NorthMoveInactive(target,enemy,8,false);}game.MonsterComplete(source);return;}
        else if(id==162303)game.MonsterPower(source,source,t.power.basePower);
        else if(id==162305)game.MonsterPower(source,target,-BetaGwentNorthPick((t.tokenMask&128)!=0,6,3));
        else if(id==162306 || id==162308 || id==152304)game.MonsterPower(source,target,-BetaGwentNorthPick(id==162306,5,BetaGwentNorthPick(id==162308,2,3)));
        else if(id==162309)game.MonsterOperation(source,target,1,3,15);
        else if(id==162310){game.MonsterPower(source,target,-7);game.FlushDeaths();u=target.Snapshot();if((u.locationMask&7)==0)game.MonsterOperation(source,source,12,4,7);}
        else if(id==162313 || id==162315)game.MonsterPower(source,target,BetaGwentNorthPick(id==162313,5,12));
        else if(id==162316 || id==200163){source.monsterIds.PushBack(selected);game.NilfReveal(target,true);if(More(source,0,8,15,14,64,0))return;}
        else if(id==163201)
        {if(source.monsterStage==0){source.monsterStored=selected;source.monsterStage=1;Query(t.positionPlayerId,t.locationMask,15,4,264,0,source,ids);for(i=0;i<ids.Size();i+=1){u=game.FindCard(ids[i]).Snapshot();if(Abs(u.locationIndex-t.locationIndex)==1)valid.PushBack(ids[i]);}game.MonsterRequest(source,valid,0,0,1);return;}game.MonsterDuel(game.FindCard(source.monsterStored),target,0,0);}
        else if(id==200031)
        {if(source.monsterStage==0){source.monsterStored=t.power.basePower;source.monsterStage=1;game.NilfReveal(target,true);Enemy(source);return;}game.MonsterPower(source,target,-source.monsterStored);}
        else if(id==200118){target.ToggleSpying();u=target.Snapshot();if((u.tokenMask&128)!=0)game.NilfSpyingAdded(u);}
        else if(id==200124)game.MonsterPower(source,target,-game.NilfAlchemy(side));
        else if(id==200162){if(source.monsterStage==0){source.monsterStage=1;game.MonsterPlayExisting(source,target);return;}game.NorthMoveInactive(target,side,8,true);}
        else if(id==200227 || id==201616)
        {source.monsterIds.PushBack(selected);game.NilfReveal(target,false);if(id==200227)game.MonsterOperation(source,target,1,BetaGwentNorthPick(t.positionPlayerId==side,2,-Min(2,Max(0,t.power.currentPower-1))),8);if(More(source,0,8,14,BetaGwentNorthPick(id==200227,12,14),0,1))return;}
        else if(id==200518){game.MonsterOperation(source,source,11,t.power.currentPower,7);game.MonsterOperation(source,target,11,s.power.currentPower,8);}
        else if(id==201603){game.QueueDestroy(target);game.MonsterPower(source,source,5);}
        else if(id==201609)game.QueueRelocation(target,side,t.locationMask,false);
        else if(id==201612){if(source.monsterStage==0){source.monsterStored=Max(0,t.power.currentPower-1);source.monsterStage=1;game.MonsterOperation(source,target,11,1,7);Enemy(source);return;}game.MonsterPower(source,target,-source.monsterStored);}
        else if(id==201661){Query(side,7,15,4,8,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==t.runtimeTemplate.templateId)game.MonsterPower(source,game.FindCard(ids[i]),2);}
        else if(id==201662){if(source.monsterStored==201714)game.QueueDestroy(target);else {Query(enemy,7,15,4,8,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(ids[i]==selected || BetaGwentNilfSharedCategory(t.runtimeTemplate.templateId,game.FindCard(ids[i]).TemplateId()))game.MonsterPower(source,game.FindCard(ids[i]),-2);}}
        else if(id==200159){source.monsterIds.PushBack(selected);game.MonsterOperation(source,target,12,1,31);game.FlushDeaths();game.NilfDiscard(target);if(More(source,side,16,14,14,0,0))return;}
        else if(id==200165){if(source.monsterStage==0){source.monsterStored=selected;source.monsterStage=1;Request(source,side,16,15,14,0,0);return;}game.NorthExchange(game.FindCard(source.monsterStored),target);game.MonsterOperation(source,target,1,3,31);}
        else if(id==152315){source.monsterIds.PushBack(selected);game.MonsterPower(source,target,-1);if(More(source,0,7,15,4,264,0))return;}
        else if(id==200020){if(source.monsterStage==0){source.monsterStored=t.power.currentPower;source.monsterStage=1;game.NilfBanish(target);Friendly(source,0);return;}game.MonsterPower(source,target,source.monsterStored);}
        else if(id==201653)game.MonsterOperation(source,target,12,7,7);
        else if(game.NilfReactionKind()==1 || game.NilfReactionKind()==4)game.MonsterPower(source,target,-BetaGwentNorthPick(game.NilfReactionKind()==1,5,2));
        else if(game.NilfReactionKind()==3)game.MonsterPower(source,target,2);
        game.MonsterComplete(source);
    }
    private function LethoDrain(source : CBetaGwentDuelCard)
    {var i,amount : int;var target : CBetaGwentDuelCard;var t : SBetaGwentCardSnapshot;
     for(i=0;i<source.monsterIds.Size();i+=1)game.FindCard(source.monsterIds[i]).AddLock();
     for(i=0;i<source.monsterIds.Size();i+=1){target=game.FindCard(source.monsterIds[i]);t=target.Snapshot();amount=t.power.currentPower;target.ChangePower(-amount,true);game.NilfPowerChanged(source,target,t,target.Snapshot(),1);if(amount>0)game.MonsterDamaged(source,target);game.MonsterPower(source,source,amount);}game.MonsterComplete(source);}
    private function FinishVattier(source : CBetaGwentDuelCard)
    {var ids : array<int>;var i : int;Query(BetaGwentOpponentId(Side(source)),8,14,14,64,0,NULL,ids);game.ShuffleIds(ids);for(i=0;i<ids.Size() && i<source.monsterIds.Size();i+=1)game.NilfReveal(game.FindCard(ids[i]),true);game.MonsterComplete(source);}
    private function PlayRitualNext(source : CBetaGwentDuelCard)
    {
        var child : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;
        while(source.monsterStored<source.monsterIds.Size())
        {child=game.FindCard(source.monsterIds[source.monsterStored]);source.monsterStored+=1;if(!child)continue;s=child.Snapshot();
         if(s.locationMask!=32 || s.positionPlayerId!=Side(source) || s.isWaitingToDie)continue;game.MonsterPlayExisting(source,child);return;}
        game.MonsterComplete(source);
    }
    public function ChildReturned(source : CBetaGwentDuelCard) : bool
    {
        var child : CBetaGwentDuelCard;var id : int;if(source.MonsterMode()>=400)return dependencies.ChildReturned(source);child=source.TakePlayedChild();id=source.TemplateId();
        if(id==200221 && source.monsterStage==1){PlayRitualNext(source);return true;}
        if(child && (id==162211 || id==201580 || id==201639))game.MonsterPower(source,child,BetaGwentNorthPick(id==162211,10,2));
        if(id==200162 && source.monsterStage==1){source.monsterStage=2;Request(source,Side(source),7,6,4,1288,0);return true;}
        return false;
    }
    public function Row(source : CBetaGwentDuelCard, side : int, row : int)
    {var s : SBetaGwentCardSnapshot;if(source.MonsterMode()>=400){dependencies.Row(source,side,row);return;}s=source.Snapshot();s.positionPlayerId=side;s.locationMask=row;s.locationIndex=-3;game.QueueSpawn(s,162402,1);game.MonsterComplete(source);}
    public function Reaction(source : CBetaGwentDuelCard, kind : int)
    {source.monsterIds.Clear();source.monsterStage=0;if(kind==5){Played(source);return;}if(kind==3)Friendly(source,0);else Enemy(source);}
    public function DepQuery(side : int, zone : int, tier : int, types : int, flags : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {Query(side,zone,tier,types,BetaGwentNorthPick((zone&7)!=0,8,0),flags,source,ids);}
    public function DepTop(source : CBetaGwentDuelCard, side : int, tier : int, types : int, flags : int, count : int, randomOrder : bool)
    {Top(source,side,tier,types,flags,count,randomOrder);}
    public function DepRandomDamage(source : CBetaGwentDuelCard, side : int, zone : int, amount : int, count : int)
    {RandomDamage(source,side,zone,amount,count);}
    public function Trigger(kind : int, cause : SBetaGwentCardSnapshot)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var source,target : CBetaGwentDuelCard;var s,t : SBetaGwentCardSnapshot;var ids,valid : array<int>;var i,j,id,least : int;var m : SBetaGwentMatchSnapshot;
        dependencies.Trigger(kind,cause);game.GetCards(cards);target=game.FindCard(cause.instanceId);if(target)t=target.Snapshot();m=game.NilfMatch();
        if(kind==1)
        {Query(BetaGwentOpponentId(cause.positionPlayerId),16,15,4,264,0,NULL,ids);for(j=0;j<ids.Size();j+=1)if(game.FindCard(ids[j]).TemplateId()==132407)valid.PushBack(ids[j]);if(valid.Size()>0)game.NorthRandomSummon(game.FindCard(valid[game.RandomIndex(valid.Size())]));}
        for(i=0;i<cards.Size();i+=1)
        {
            s=cards[i].card;source=game.FindCard(s.instanceId);id=s.runtimeTemplate.templateId;if(!source || s.isWaitingToDie || (s.tokenMask&12)!=0)continue;
            if(kind==1)
            {
                if(s.instanceId==cause.instanceId && s.locationMask==8){if(id==162301)game.NilfQueueReaction(source,2,s.positionPlayerId);if(id==162306)game.NilfQueueReaction(source,1,s.positionPlayerId);}
                if((s.locationMask&7)!=0 && id==162317 && cause.positionPlayerId==s.positionPlayerId)RandomDamage(source,BetaGwentOpponentId(s.positionPlayerId),7,2,1);
            }
            if((s.locationMask&7)==0)continue;
            if(kind==2 && id==162312)game.MonsterPower(source,source,1);
            // Spawn (12) is also an arrival: Cow Carcass already has Spying here.
            // The preceding move notification uses its final position, so it
            // does not count as another arrival and cannot trigger twice.
            if((kind==3 || kind==11 || kind==12) && target && (t.locationMask&7)!=0 && t.instanceId!=s.instanceId && (kind==11 || kind==12 || (cause.locationMask&7)==0 || cause.positionPlayerId!=t.positionPlayerId))
            {
                if(id==200296 && t.positionPlayerId==s.positionPlayerId)game.MonsterPower(source,source,1);
                if((t.tokenMask&128)!=0 && t.positionPlayerId!=s.positionPlayerId){if(id==162307)game.MonsterPower(source,source,2);if(id==162308 && m.currentPlayerId==s.positionPlayerId)source.nilfCounter+=1;}
            }
            if(kind==4 && id==200294 && target && game.NorthActingSide(target)==s.positionPlayerId && BetaGwentNorthernCategory(t.runtimeTemplate.templateId,2))game.NilfQueueReaction(source,3,s.positionPlayerId);
            if(kind==5 && id==162212 && cause.positionPlayerId==s.positionPlayerId && (s.tokenMask&128)!=0)game.MonsterPower(source,source,1);
            if(kind==6 && (cause.positionPlayerId==s.positionPlayerId || (id==162402 && ((s.positionPlayerId==1 && m.playerOne.hasPassed) || (s.positionPlayerId==2 && m.playerTwo.hasPassed)))))
            {
                if(id==162308){for(j=0;j<source.nilfCounter;j+=1)game.NilfQueueReaction(source,4,s.positionPlayerId);source.nilfCounter=0;}
                if(id==162402 && s.timerValue>0){game.QueueTimer(source,0,1);if(s.timerValue==1){Query(s.positionPlayerId,s.locationMask,15,4,8,16,source,ids);least=2147483647;for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();least=Min(least,t.power.currentPower);}for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();if(t.power.currentPower==least)game.QueueDestroy(game.FindCard(ids[j]));}game.MonsterOperation(source,source,14,0,7);}}
            }
            if(kind==7 && id==162212 && cause.positionPlayerId==s.positionPlayerId && (s.tokenMask&128)!=0)game.QueueRelocation(source,BetaGwentOpponentId(s.positionPlayerId),s.locationMask,false);
            if(kind==8 && id==152312 && cause.positionPlayerId!=s.positionPlayerId && cause.locationMask==s.locationMask)game.MonsterPower(source,source,1);
        }
        if(kind==9 && cause.runtimeTemplate.templateId==162212 && (cause.tokenMask&4)==0)
        {Query(cause.positionPlayerId,cause.locationMask,15,4,8,0,NULL,ids);least=2147483647;for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();least=Min(least,t.power.currentPower);}for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();if(t.power.currentPower==least)game.QueueDestroy(game.FindCard(ids[j]));}}
    }
}
