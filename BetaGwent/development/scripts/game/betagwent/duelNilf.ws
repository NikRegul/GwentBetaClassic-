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
    public var turnPlayedIds, turnPlayedDestinations : array<int>;
    public var historyTurn, historyRound : int;
    public function Initialize(owner : CBetaGwentDuelSession) { game = owner;dependencies=new CBetaGwentNilfDependencies in this;dependencies.Initialize(owner,this); }
    private function Side(source : CBetaGwentDuelCard) : int { return game.NorthActingSide(source); }
    public function RecordPlayed(card : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;s=card.Snapshot();m=game.NilfMatch();
        if(historyRound!=m.roundNumber || historyTurn!=m.turnSequence){turnPlayedIds.Clear();turnPlayedDestinations.Clear();historyRound=m.roundNumber;historyTurn=m.turnSequence;}
        turnPlayedIds.PushBack(s.instanceId);turnPlayedDestinations.PushBack(s.positionPlayerId);
    }
    // Event cards are played to Graveyard in Beta, then a Doomed pop may
    // banish them. The compact runtime uses PlayStack/Void directly, so emit
    // the selected-event arrival latch at the equivalent completed pop.
    public function PlayCompleted(card : CBetaGwentDuelCard)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var c,s : SBetaGwentCardSnapshot;var source : CBetaGwentDuelCard;var i : int;
        c=card.Snapshot();if(c.runtimeTemplate.typeMask!=2 || (card.playFromLocation&248)==0 || (c.locationMask!=32 && c.locationMask!=512))return;
        game.GetCards(cards);for(i=0;i<cards.Size();i+=1){s=cards[i].card;if(s.runtimeTemplate.templateId!=200162 || s.positionPlayerId!=c.positionPlayerId || (s.locationMask&7)==0 || s.isWaitingToDie || (s.tokenMask&12)!=0)continue;
            source=game.FindCard(s.instanceId);if(source.nilfCounter==c.instanceId)source.nilfTurnArmed=true;}
    }
    public function WasPlayedThisTurn(card : CBetaGwentDuelCard) : bool
    {var m : SBetaGwentMatchSnapshot;var s : SBetaGwentCardSnapshot;if(!card)return false;m=game.NilfMatch();s=card.Snapshot();return historyRound==m.roundNumber && historyTurn==m.turnSequence && turnPlayedIds.Contains(s.instanceId);}
    public function BeforeTurnEnd(side : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var s,t : SBetaGwentCardSnapshot;var source,card : CBetaGwentDuelCard;
        var m : SBetaGwentMatchSnapshot;var i,j,count,played : int;m=game.NilfMatch();
        if(historyRound==m.roundNumber && historyTurn==m.turnSequence)for(j=0;j<turnPlayedIds.Size();j+=1)
        {card=game.FindCard(turnPlayedIds[j]);if(card && turnPlayedDestinations[j]!=m.currentPlayerId){t=card.Snapshot();if((t.tokenMask&8)==0)played+=1;}}
        game.GetCards(cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].card;
            if(s.runtimeTemplate.templateId==200162 && s.positionPlayerId==side && (s.locationMask&7)!=0 && !s.isWaitingToDie && s.power.currentPower>0 && (s.tokenMask&12)==0)
            {source=game.FindCard(s.instanceId);if(source.nilfTurnArmed){source.nilfTurnArmed=false;source.nilfCounter=0;game.NilfQueueReaction(source,9,side);}}
            if(s.runtimeTemplate.templateId!=162308 || s.positionPlayerId!=side || (s.locationMask&7)==0 || s.isWaitingToDie || s.power.currentPower<=0 || (s.tokenMask&12)!=0)continue;
            source=game.FindCard(s.instanceId);if(!source.nilfTurnArmed)continue;count=source.nilfCounter+played;
            for(j=0;j<count;j+=1)game.NilfQueueReaction(source,4,side);}
    }
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
    game.PhysicalOrder096(ids);}
    // Location.GetCards walks physical indexes, not registry allocation order.
    // Use this ordered helper for independently reviewed token and batch80 graphs.
    private function TokenQuery(side : int, zone : int, tier : int, types : int, ignore : int, flags : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {
        var raw : array<int>;var i,j,value : int;var s,t : SBetaGwentCardSnapshot;
        Query(side,zone,tier,types,ignore,flags,source,raw);ids.Clear();
        for(i=0;i<raw.Size();i+=1)
        {
            if(game.IsExecutingCard(game.FindCard(raw[i])))continue;
            s=game.FindCard(raw[i]).Snapshot();value=ids.Size();
            for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();
                if(s.positionPlayerId<t.positionPlayerId || s.positionPlayerId==t.positionPlayerId && (s.locationMask<t.locationMask || s.locationMask==t.locationMask && s.locationIndex<t.locationIndex)){value=j;break;}}
            ids.Insert(value,raw[i]);
        }
    }
    private function TokenRequest(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, ignore : int, flags : int)
    {
        var ids : array<int>;var minimum,maximum : int;
        TokenQuery(side,zone,tier,types,ignore,flags,source,ids);
        maximum=Max(0,source.monsterRemaining);minimum=0;
        // ARequestTargetsAction.ApplyImpl: MinTargets = clamped MaxTargets.
        if((zone&7)!=0)minimum=Min(maximum,ids.Size());
        game.MonsterRequest(source,ids,BetaGwentNorthPick((zone&7)!=0,0,2),minimum,maximum);
    }
    public function SourceCards(side : int, zone : int, tier : int, types : int, ignore : int, flags : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {TokenQuery(side,zone,tier,types,ignore,flags,source,ids);}
    private function ArcherRequest(source : CBetaGwentDuelCard)
    {var ids : array<int>;var maximum : int;TokenQuery(0,7,15,4,264,0,source,ids);maximum=Min(source.monsterRemaining,ids.Size());game.MonsterRequest(source,ids,0,maximum,maximum);}
    private function CommitArcher(source : CBetaGwentDuelCard)
    {var i : int;for(i=0;i<source.monsterIds.Size();i+=1)game.MonsterPower(source,game.FindCard(source.monsterIds[i]),-1);game.MonsterComplete(source);}
    private function Request(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, ignore : int, flags : int, optional minimum : int)
    { var ids : array<int>;Query(side,zone,tier,types,ignore,flags,source,ids);ShuffleOnce096(source,ids);minimum=BetaGwentNilfMinimum(source.TemplateId());game.MonsterRequest(source,ids,BetaGwentNorthPick((zone&7)!=0,0,2),minimum,1); }
    private function Choose(source : CBetaGwentDuelCard, pool : int, randomThree : bool)
    { var ids : array<int>;BetaGwentNilfPool(pool,ids);if(randomThree){game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);}game.MonsterRequest(source,ids,1,1,1); }
    private function Top(source : CBetaGwentDuelCard, side : int, tier : int, types : int, flags : int, count : int, randomOrder : bool)
    {
        var ids, ordered, valid : array<int>;var i : int;
        Query(side,16,tier,types,0,flags,source,valid);game.NorthPile(side,16,ordered);
        for(i=0;i<ordered.Size();i+=1)if(valid.Contains(ordered[i]))ids.PushBack(ordered[i]);
        if(randomOrder)game.ShuffleIds(ids);while(ids.Size()>count)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,2,1,1);
    }
    // Beta SetVar -> CardListShuffle -> one RequestCardChoice: shuffle once, keep that order for the UI's follow-up picks.
    private function ShuffleOnce096(source : CBetaGwentDuelCard, out ids : array<int>)
    {
        var i : int; var ordered : array<int>;
        if(source.TemplateId()!=162106 && source.TemplateId()!=200159)return;
        if(source.choiceDeck.Size()==0){if(ids.Size()>0){game.ShuffleIds(ids);for(i=0;i<ids.Size();i+=1)source.choiceDeck.PushBack(ids[i]);}return;}
        for(i=0;i<source.choiceDeck.Size();i+=1)if(ids.Contains(source.choiceDeck[i]))ordered.PushBack(source.choiceDeck[i]);
        ids=ordered;
    }
    private function TopPlay096(source : CBetaGwentDuelCard, side : int, tier : int, types : int, flags : int)
    {
        var ordered, valid : array<int>;var i : int;
        Query(side,16,tier,types,0,flags,source,valid);game.NorthPile(side,16,ordered);
        for(i=0;i<ordered.Size();i+=1)if(valid.Contains(ordered[i])){game.MonsterPlayExisting(source,game.FindCard(ordered[i]));return;}
        game.MonsterComplete(source);
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
        if(valid.Size()>0)game.ShuffleIds(valid);
        game.MonsterRequest(source,valid,2,0,1);
    }
    private function Friendly(source : CBetaGwentDuelCard, flags : int) { Request(source,Side(source),7,15,4,264,flags); }
    public function Played(source : CBetaGwentDuelCard)
    {
        var id, side, enemy, i, j, maxPower : int;var s,t : SBetaGwentCardSnapshot;var ids,valid,rows,deck : array<int>;var d : SBetaGwentDuelDefinition;var m : SBetaGwentMatchSnapshot;
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
        if(id==162101){source.monsterRemaining=2;TokenRequest(source,s.positionPlayerId,s.locationMask,15,4,256,16);return;}
        if(id==162102 || id==162305 || id==162306 || id==162308 || id==152304){Enemy(source);return;}
        if(id==200124){if(game.NilfAlchemy(side)>0)Request(source,0,7,15,4,264,0);else game.MonsterComplete(source);return;}
        if(id==162103){source.monsterRemaining=2;TokenRequest(source,side,8,14,14,64,0);return;}
        if(id==162105){Request(source,BetaGwentNorthPick(game.NilfTruce(),0,side),7,15,4,264,16);return;}
        if(id==162106){source.choiceDeck.Clear();Request(source,side,16,14,14,0,0);return;}
        if(id==162107){if(game.NilfTruce()){game.MonsterPower(source,source,15);game.FlushDeaths();game.NilfDraw(enemy,2,true);}game.MonsterComplete(source);return;}
        if(id==162108){Query(enemy,16,14,14,0,0,source,ids);game.ShuffleIds(ids);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==162201){if(game.NilfTruce()){game.NilfDraw(enemy,14,true);game.FlushDeaths();game.NilfDraw(side,14,false);}game.MonsterComplete(source);return;}
        if(id==162202){source.monsterRemaining=2;Request(source,0,32,6,14,0,0);return;}
        if(id==162203)
        {TokenQuery(enemy,8,14,12,64,0,source,ids);maxPower=-1;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();maxPower=Max(maxPower,t.power.currentPower);}for(i=ids.Size()-1;i>=0;i-=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower==maxPower)valid.PushBack(ids[i]);}if(valid.Size()>0){j=valid[game.RandomIndex(valid.Size())];game.NilfReveal(game.FindCard(j),true);game.FlushDeaths();t=game.FindCard(j).Snapshot();game.MonsterPower(game.FindCard(j),source,t.power.currentPower);}game.MonsterComplete(source);return;}
        if(id==162204){Request(source,0,7,15,4,264,0);return;}
        if(id==162208){source.monsterRemaining=2;TokenRequest(source,0,7,15,4,256,0);return;}
        if(id==162205 || id==200115)
        {Query(s.positionPlayerId,s.locationMask,15,4,BetaGwentNorthPick(id==200115,8,0),16,source,ids);maxPower=-1;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationIndex==s.locationIndex-1){if(id==200115)game.MonsterPower(source,game.FindCard(ids[i]),-10);else maxPower=t.power.currentPower;}}if(id==162205 && maxPower>=0)for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationIndex==s.locationIndex+1)game.MonsterOperation(source,game.FindCard(ids[i]),11,maxPower,7);}game.MonsterComplete(source);return;}
        if(id==162206 || id==162209)
        {Query(enemy,7,15,4,264,0,source,ids);Query(enemy,8,14,4,0,1,source,valid);for(i=0;i<valid.Size();i+=1)ids.PushBack(valid[i]);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==162207 || id==162213 || id==201597){Choose(source,id,false);return;}
        if(id==162210)
        {if(s.timerValue!=1){game.MonsterComplete(source);return;}Query(side,16,15,6,0,0,source,valid);game.NorthPile(side,16,deck);for(i=0;i<deck.Size() && ids.Size()<2;i+=1)if(valid.Contains(deck[i]))ids.PushBack(deck[i]);source.monsterIds=ids;source.choiceDeck.Clear();if(ids.Size()>0)game.MonsterRequest(source,ids,2,1,1);else{game.QueueTimer(source,0,1);game.MonsterComplete(source);}return;}
        if(id==162211){TopPlay096(source,side,6,4,8);return;}
        if(id==162302){game.MonsterCreate(source,162402);return;}
        if(id==162303){Request(source,0,8,6,12,0,1);return;}
        if(id==162304 || id==201780){Request(source,enemy,32,BetaGwentNorthPick(id==162304,2,6),4,BetaGwentNorthPick(id==162304,0,264),BetaGwentNorthPick(id==162304,0,128));return;}
        if(id==162307){Query(enemy,7,15,4,8,4,source,ids);game.MonsterPower(source,source,2*ids.Size());source.monsterIds=ids;game.MonsterComplete(source);return;}
        if(id==162309){game.NorthClearHazard(side,s.locationMask);TokenQuery(side,7,15,12,8,0,source,ids);TokenQuery(side,8,15,12,0,1,source,valid);for(i=0;i<valid.Size();i+=1)ids.PushBack(valid[i]);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==162310){Request(source,0,7,15,4,264,4);return;}
        if(id==162311){game.NorthSummonCopies(source,id);game.MonsterComplete(source);return;}
        if(id==162313 || id==162315){Friendly(source,0);return;}
        if(id==162314){Top(source,side,2,4,0,2,true);return;}
        if(id==162316 || id==200163){source.monsterRemaining=BetaGwentNorthPick(id==200163,4,2);TokenRequest(source,0,8,15,BetaGwentNorthPick(id==200163,6,14),BetaGwentNorthPick(id==200163,72,64),0);return;}
        if(id==162317){RandomDamage(source,enemy,7,2,1);game.MonsterComplete(source);return;}
        if(id==162318)
        {TokenQuery(side,8,14,14,64,0,source,ids);for(j=2;j<=8;j*=2){valid.Clear();for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if((t.runtimeTierMask&j)!=0)valid.PushBack(ids[i]);}if(valid.Size()>0){game.NilfReveal(game.FindCard(valid[game.RandomIndex(valid.Size())]),true);break;}}game.MonsterComplete(source);return;}
        if(id==162401){game.MonsterDeckCopies(enemy,200219,1);game.NorthPile(enemy,16,ids);for(i=ids.Size()-1;i>=0;i-=1)if(game.FindCard(ids[i]).TemplateId()==200219){game.MonsterTopDeck(game.FindCard(ids[i]));break;}game.MonsterComplete(source);return;}
        if(id==162402){game.QueueTimer(source,2,2);game.MonsterComplete(source);return;}
        if(id==163201){Request(source,enemy,7,15,4,264,0);return;}
        if(id==200031){source.monsterRemaining=1;TokenRequest(source,side,8,15,4,64,0);return;}
        if(id==200032){RainfarnRequest(source);return;}
        if(id==200041){Query(enemy,7,15,4,8,0,source,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationMask!=s.locationMask || ((s.tokenMask|source.playFromTokens)&64)!=0)game.MonsterPower(source,game.FindCard(ids[i]),-1);}game.MonsterComplete(source);return;}
        if(id==200044 || id==201617)
        {Query(side,16,2,BetaGwentNorthPick(id==200044,14,12),0,BetaGwentNorthPick(id==200044,1024,4224),source,ids);if(ids.Size()>0)game.MonsterPlayExisting(source,game.FindCard(ids[game.RandomIndex(ids.Size())]));else game.MonsterComplete(source);return;}
        if(id==200050 || id==201580 || id==201583 || id==201589 || id==201585){Choose(source,id,true);return;}
        if(id==200071)
        {m=game.NilfMatch();if((side==1 && m.playerTwo.hasPassed) || (side==2 && m.playerOne.hasPassed)){game.MonsterComplete(source);return;}Query(side,16,15,6,0,0,source,valid);game.NorthPile(side,16,deck);for(i=0;i<deck.Size();i+=1)if(valid.Contains(deck[i])){ids.PushBack(deck[i]);break;}Query(enemy,16,15,6,0,0,source,valid);game.NorthPile(enemy,16,deck);for(i=0;i<deck.Size();i+=1)if(valid.Contains(deck[i])){ids.PushBack(deck[i]);break;}if(ids.Size()!=2){game.MonsterComplete(source);return;}source.monsterIds=ids;source.choiceDeck.Clear();game.MonsterRequest(source,source.monsterIds,2,1,1);return;}
        if(id==200118){Request(source,0,7,15,4,264,0);return;}
        if(id==200162){Request(source,side,8,14,14,8,0);return;}
        if(id==200164){Top(source,side,15,14,0,3,false);return;}
        if(id==201616){source.monsterRemaining=2;TokenRequest(source,0,8,14,14,0,1);return;}
        if(id==200227){source.monsterRemaining=99;Request(source,0,8,14,12,0,1);return;}
        if(id==200518){Request(source,0,8,14,12,256,1);return;}
        if(id==201601){i=game.NilfLastSpell(side);if(i>0)game.MonsterCreate(source,i);else game.MonsterComplete(source);return;}
        if(id==201603 || id==201662 || id==201653)
        {if(id==201603){ids.PushBack(201694);ids.PushBack(201695);}if(id==201662){ids.PushBack(201713);ids.PushBack(201714);}if(id==201653){ids.PushBack(201672);ids.PushBack(201673);}game.MonsterRequest(source,ids,1,1,1);return;}
        if(id==201609){
            // Graph879 first collects enemy rows opposite available own rows.
            Query(enemy,7,2,4,264,64,source,ids);
            for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(game.CountLocation(side,t.locationMask)<9)valid.PushBack(ids[i]);}
            game.MonsterRequest(source,valid,0,1,1);return;
        }
        if(id==201610){for(i=1;i<=4;i*=2)if(i!=s.locationMask){t=s;t.locationMask=i;t.locationIndex=-3;game.QueueSpawn(t,id,1);}game.MonsterComplete(source);return;}
        if(id==201612){Query(enemy,7,15,4,264,0,source,ids);if(ids.Size()>0)Friendly(source,16);else game.MonsterComplete(source);return;}
        if(id==201661){Friendly(source,128);return;}
        if(id==201664){Request(source,side,16,2,4,0,256);return;}
        if(id==200159){source.monsterRemaining=3;source.choiceDeck.Clear();Request(source,side,16,14,14,0,0);return;}
        if(id==200160){Query(side,16,6,4,0,8,source,ids);maxPower=-1;for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();maxPower=Max(maxPower,t.power.currentPower);}for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower==maxPower)valid.PushBack(ids[i]);}if(valid.Size()>0){i=valid[game.RandomIndex(valid.Size())];game.MonsterOperation(source,game.FindCard(i),12,2,31);game.FlushDeaths();game.MonsterPlayExisting(source,game.FindCard(i));}else game.MonsterComplete(source);return;}
        if(id==200161){RandomDamage(source,enemy,s.locationMask,1,10);game.MonsterComplete(source);return;}
        if(id==200165){Query(side,16,15,14,0,0,source,ids);if(ids.Size()==0){game.MonsterComplete(source);return;}Request(source,side,8,15,14,0,0);return;}
        if(id==200166){Request(source,side,32,6,2,0,0);return;}
        if(id==200167){Query(side,16,4,12,0,8,source,ids);Query(side,16,2,12,0,8192,source,valid);for(i=0;i<valid.Size();i+=1)ids.PushBack(valid[i]);if(ids.Size()>0)game.ShuffleIds(ids);game.MonsterRequest(source,ids,2,0,1);return;}
        if(id==152313){if(source.playFromLocation==32)game.MonsterOperation(source,source,12,3,7);game.MonsterComplete(source);return;}
        if(id==152315){source.monsterRemaining=3;ArcherRequest(source);return;}
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
        var target : CBetaGwentDuelCard;var s,t,u : SBetaGwentCardSnapshot;var id,side,enemy,i,j,amount,destination : int;var ids,valid,selectedIds,deck : array<int>;
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
        if(id==152315){if(selected>0){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){ArcherRequest(source);return;}}CommitArcher(source);return;}
        if((id==162316 || id==200163 || id==201616) && selected==0){game.NilfRevealCards(source.monsterIds,id!=201616);game.MonsterComplete(source);return;}
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
        {source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){TokenRequest(source,s.positionPlayerId,s.locationMask,15,4,256,16);return;}LethoDrain(source);return;}
        if(id==162102){if((t.tokenMask&128)!=0)game.QueueDestroy(target);else game.MonsterPower(source,target,-4);}
        else if(id==162103){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){TokenRequest(source,side,8,14,14,64,0);return;}FinishVattier(source);return;}
        else if(id==162105)
        {if(source.monsterStage==1){game.MonsterPlayExisting(source,target);return;}game.QueueDestroy(target,source);game.KillWaitingToDieNow();if(t.positionPlayerId==side){source.monsterStage=1;TokenQuery(side,16,14,14,0,0,source,ids);if(ids.Size()>0)game.MonsterPlayExisting(source,game.FindCard(ids[0]));else game.MonsterComplete(source);return;}game.NilfDraw(enemy,2,true);}
        else if(id==162106){game.MonsterTopDeck(target);if(!BetaGwentDuelSpying(t.runtimeTemplate.templateId))game.MonsterOperation(source,target,1,5,31);}
        else if(id==162108)game.NilfBottom(target);
        else if(id==162202){source.monsterIds.PushBack(selected);game.NorthMoveInactive(target,t.positionPlayerId,16,false);if(More(source,0,32,6,14,0,0))return;}
        else if(id==162204){game.QueueResetPower(source,target);game.MonsterOperation(source,target,12,BetaGwentNorthPick(t.positionPlayerId==side,3,-3),7);}
        else if(id==162208){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){TokenRequest(source,0,7,15,4,256,0);return;}for(i=0;i<source.monsterIds.Size();i+=1)game.MonsterOperation(source,game.FindCard(source.monsterIds[i]),6,0,7);}
        else if(id==162206){Query(enemy,16,14,4,8,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==t.runtimeTemplate.templateId)game.NorthMoveInactive(game.FindCard(ids[i]),enemy,32,false);}
        else if(id==162209){if(t.locationMask==8)game.MonsterOperation(source,target,11,1,8);else game.MonsterPower(source,target,-7);}
        else if(id==162210)
        {selectedIds.PushBack(selected);game.DrawCaptured(side,selectedIds,1,false);for(i=0;i<source.monsterIds.Size();i+=1)if(source.monsterIds[i]!=selected){target=game.FindCard(source.monsterIds[i]);game.NorthPile(side,16,deck);game.MoveInactiveToIndex(target,side,16,deck.Size());}game.QueueTimer(source,0,1);game.MonsterComplete(source);return;}
        else if(id==200071)
        {game.MoveInactiveToIndex(target,side,8,game.CountLocation(side,8));for(i=0;i<source.monsterIds.Size();i+=1)if(source.monsterIds[i]!=selected){target=game.FindCard(source.monsterIds[i]);destination=enemy;game.MoveInactiveToIndex(target,destination,8,game.CountLocation(destination,8));}game.MonsterComplete(source);return;}
        else if(id==162303)game.MonsterPower(source,source,t.power.basePower);
        else if(id==162305)game.MonsterPower(source,target,-BetaGwentNorthPick((t.tokenMask&128)!=0,6,3));
        else if(id==162306 || id==162308 || id==152304)game.MonsterPower(source,target,-BetaGwentNorthPick(id==162306,5,BetaGwentNorthPick(id==162308,2,3)));
        else if(id==162309)game.MonsterOperation(source,target,1,3,15);
        else if(id==162310){game.MonsterPower(source,target,-7);game.FlushDeaths();u=target.Snapshot();if(game.UnitDied(u))game.MonsterOperation(source,source,12,4,7);}
        else if(id==162313 || id==162315)game.MonsterPower(source,target,BetaGwentNorthPick(id==162313,5,12));
        else if(id==162316 || id==200163){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){TokenRequest(source,0,8,15,BetaGwentNorthPick(id==200163,6,14),BetaGwentNorthPick(id==200163,72,64),0);return;}game.NilfRevealCards(source.monsterIds,true);}
        else if(id==163201)
        {if(source.monsterStage==0){source.monsterStored=selected;source.monsterStage=1;Query(t.positionPlayerId,t.locationMask,15,4,264,0,source,ids);for(i=0;i<ids.Size();i+=1){u=game.FindCard(ids[i]).Snapshot();if(Abs(u.locationIndex-t.locationIndex)==1)valid.PushBack(ids[i]);}game.MonsterRequest(source,valid,0,0,1);return;}game.MonsterDuel(game.FindCard(source.monsterStored),target,0,0);}
        else if(id==200031)
        {if(source.monsterStage==0){source.monsterStage=1;game.NilfReveal(target,true);game.FlushDeaths();t=target.Snapshot();source.monsterStored=t.power.basePower;Enemy(source);return;}game.MonsterPower(source,target,-source.monsterStored);}
        else if(id==200118){target.ToggleSpying();u=target.Snapshot();if((u.tokenMask&128)!=0)game.NilfSpyingAdded(u);}
        else if(id==200124)game.MonsterPower(source,target,-game.NilfAlchemy(side));
        else if(id==200162){if(source.monsterStage==0){source.monsterStage=1;source.nilfCounter=selected;source.nilfTurnArmed=false;game.MonsterPlayExisting(source,target);return;}game.NorthMoveInactive(target,side,8,true);}
        else if(id==201616){source.monsterIds.PushBack(selected);source.monsterRemaining-=1;if(source.monsterRemaining>0){TokenRequest(source,0,8,14,14,0,1);return;}game.NilfRevealCards(source.monsterIds,false);}
        else if(id==200227)
        {source.monsterIds.PushBack(selected);game.NilfReveal(target,false);game.MonsterOperation(source,target,1,BetaGwentNorthPick(t.positionPlayerId==side,2,-Min(2,Max(0,t.power.currentPower-1))),8);if(More(source,0,8,14,12,0,1))return;}
        else if(id==200518){game.MonsterOperation(source,source,11,t.power.currentPower,7);game.MonsterOperation(source,target,11,s.power.currentPower,8);}
        else if(id==201603){game.QueueDestroy(target);game.MonsterPower(source,source,5);}
        else if(id==201609)game.QueueRelocation(target,side,t.locationMask,false);
        else if(id==201612){if(source.monsterStage==0){source.monsterStored=Max(0,t.power.currentPower-1);source.monsterStage=1;game.MonsterOperation(source,target,11,1,7);Enemy(source);return;}game.MonsterPower(source,target,-source.monsterStored);}
        else if(id==201661){game.RandomIndex(1);TokenQuery(side,7,15,4,8,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==t.runtimeTemplate.templateId)game.MonsterPower(source,game.FindCard(ids[i]),2);}
        else if(id==201662){if(source.monsterStored==201714)game.QueueDestroy(target);else {Query(enemy,7,15,4,8,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(BetaGwentNilfSharedCategory(t.runtimeTemplate.templateId,game.FindCard(ids[i]).TemplateId()))game.MonsterPower(source,game.FindCard(ids[i]),-2);}}
        else if(id==200159){source.monsterIds.PushBack(selected);game.MonsterOperation(source,target,12,1,31);game.FlushDeaths();game.NilfDiscard(target);if(More(source,side,16,14,14,0,0))return;}
        else if(id==200165){if(source.monsterStage==0){Query(side,16,15,14,0,0,source,ids);game.MoveInactiveToIndex(target,side,16,game.RandomIndex(ids.Size()+1));source.monsterStage=1;Query(side,16,15,14,0,0,source,ids);if(ids.Size()>0)game.ShuffleIds(ids);game.MonsterRequest(source,ids,2,1,1);return;}game.NorthMoveInactive(target,side,8,false);if(t.runtimeTemplate.typeMask==4)game.MonsterOperation(source,target,1,3,31);}
        else if(id==152315){source.monsterIds.PushBack(selected);game.MonsterPower(source,target,-1);if(More(source,0,7,15,4,264,0))return;}
        else if(id==200020){if(source.monsterStage==0){source.monsterStored=t.power.currentPower;source.monsterStage=1;game.NilfBanish(target);Friendly(source,0);return;}game.MonsterPower(source,target,source.monsterStored);}
        else if(id==201653)game.MonsterOperation(source,target,12,7,7);
        else if(game.NilfReactionKind()==1 || game.NilfReactionKind()==4)game.MonsterPower(source,target,-BetaGwentNorthPick(game.NilfReactionKind()==1,5,2));
        else if(game.NilfReactionKind()==3)game.MonsterPower(source,target,2);
        game.MonsterComplete(source);
    }
    private function LethoDrain(source : CBetaGwentDuelCard)
    {var i,amount : int;var target : CBetaGwentDuelCard;var t : SBetaGwentCardSnapshot;
     for(i=0;i<source.monsterIds.Size();i+=1){target=game.FindCard(source.monsterIds[i]);t=target.Snapshot();amount+=t.power.currentPower;}
     for(i=0;i<source.monsterIds.Size();i+=1)game.FindCard(source.monsterIds[i]).AddLock();
     for(i=0;i<source.monsterIds.Size();i+=1)game.QueueDestroy(game.FindCard(source.monsterIds[i]),source);
     game.MonsterPower(source,source,amount);game.MonsterComplete(source);}
    private function FinishVattier(source : CBetaGwentDuelCard)
    {var ids : array<int>;var i : int;game.NilfRevealCards(source.monsterIds,true);game.FlushDeaths();for(i=0;i<source.monsterIds.Size();i+=1){TokenQuery(BetaGwentOpponentId(Side(source)),8,14,14,64,0,NULL,ids);if(ids.Size()>0){game.NilfReveal(game.FindCard(ids[game.RandomIndex(ids.Size())]),true);game.FlushDeaths();}}game.MonsterComplete(source);}
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
        return false;
    }
    public function Row(source : CBetaGwentDuelCard, side : int, row : int)
    {var s : SBetaGwentCardSnapshot;if(source.MonsterMode()>=400){dependencies.Row(source,side,row);return;}s=source.Snapshot();s.positionPlayerId=side;s.locationMask=row;s.locationIndex=-3;game.QueueSpawn(s,162402,1);game.MonsterComplete(source);}
    public function Reaction(source : CBetaGwentDuelCard, kind : int)
    {source.monsterIds.Clear();source.monsterStage=0;if(kind==9){source.monsterStage=2;Request(source,Side(source),7,6,4,1288,0);return;}if(kind==5){Played(source);return;}if(kind==3)Friendly(source,0);else Enemy(source);}
    public function DepQuery(side : int, zone : int, tier : int, types : int, flags : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {Query(side,zone,tier,types,BetaGwentNorthPick((zone&7)!=0,8,0),flags,source,ids);}
    // Movement graphs choose their explicit Ignore mask and other-row mask;
    // DepQuery's default Ambush exclusion does not apply to Kiaran (Ignore256).
    public function DepMovementRequest(source : CBetaGwentDuelCard, ignore : int, excludedRow : int)
    {var ids : array<int>;Query(0,7-excludedRow,15,4,ignore,16,source,ids);game.MonsterRequest(source,ids,0,0,1);}
    public function DepTop(source : CBetaGwentDuelCard, side : int, tier : int, types : int, flags : int, count : int, randomOrder : bool)
    {Top(source,side,tier,types,flags,count,randomOrder);}
    public function DepRandomDamage(source : CBetaGwentDuelCard, side : int, zone : int, amount : int, count : int)
    {RandomDamage(source,side,zone,amount,count);}
    public function TokenEvent(item : CBetaGwentDuelEvent)
    {
        var source : CBetaGwentDuelCard;var s,t : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;var ids : array<int>;var id,i : int;var addedAction : bool;
        source=game.FindCard(item.source.instanceId);if(!source)return;s=source.Snapshot();id=s.runtimeTemplate.templateId;m=game.NilfMatch();
        if(item.rowToken==64)
        {
            if(s.positionPlayerId!=m.currentPlayerId)return;
            if(id==132407)
            {
                for(i=0;i<item.rowTargets.Size();i+=1){TokenQuery(s.positionPlayerId,16,15,4,264,0,NULL,ids);
                    for(id=ids.Size()-1;id>=0;id-=1)if(game.FindCard(ids[id]).TemplateId()!=132407)ids.Erase(id);
                    if(ids.Size()>0 && game.RandomPositionMove(game.FindCard(ids[game.RandomIndex(ids.Size())]),s.positionPlayerId,true))addedAction=true;}
                if(addedAction)game.events.AbortTokenSiblings(item);
                return;
            }
            if(id==162301 || id==162306){game.NilfQueueReaction(source,BetaGwentNorthPick(id==162301,2,1),s.positionPlayerId);return;}
            if(id==162317)for(i=0;i<item.rowTargets.Size();i+=1)RandomDamage(source,BetaGwentOpponentId(s.positionPlayerId),7,2,1);
        }
        if(item.rowToken==128)
        {if(id==162307)game.MonsterPower(source,source,2);if(id==162308 && m.currentPlayerId==s.positionPlayerId)source.nilfCounter+=item.rowTargets.Size();}
    }
    public function Trigger(kind : int, cause : SBetaGwentCardSnapshot, optional playedArrival : bool)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var source,target : CBetaGwentDuelCard;var s,t : SBetaGwentCardSnapshot;var ids,valid : array<int>;var i,j,id,least : int;var m : SBetaGwentMatchSnapshot;var golemHandled : bool;
        dependencies.Trigger(kind,cause);game.GetCards(cards);target=game.FindCard(cause.instanceId);if(target)t=target.Snapshot();m=game.NilfMatch();golemHandled=false;
        // Golem priority5 runs before the priority0 self-reveal reactions.
        // AfterChangedToken dispatch already establishes Add(Revealed64).
        if(kind==1 && cause.positionPlayerId!=m.currentPlayerId)
        {
            Query(m.currentPlayerId,16,15,4,0,0,NULL,ids);valid.Clear();
            for(j=0;j<ids.Size();j+=1){source=game.FindCard(ids[j]);s=source.Snapshot();if(s.runtimeTemplate.templateId!=132407)continue;
                if((s.tokenMask&12)==0 && s.power.currentPower>0)golemHandled=true;
                if((s.tokenMask&264)==0 && !game.IsExecutingCard(source))valid.PushBack(s.instanceId);}
            if(golemHandled && valid.Size()>0)game.RandomPositionMove(game.FindCard(valid[game.RandomIndex(valid.Size())]),m.currentPlayerId,true);
            valid.Clear();
        }
        target=game.FindCard(cause.instanceId);if(target)t=target.Snapshot();
        for(i=0;i<cards.Size();i+=1)
        {
            s=cards[i].card;source=game.FindCard(s.instanceId);if(!source)continue;s=source.Snapshot();id=s.runtimeTemplate.templateId;if(s.isWaitingToDie || (s.tokenMask&12)!=0)continue;
            if(kind==1)
            {
                if(s.instanceId==cause.instanceId && id==162301 && s.locationMask==8 && m.currentPlayerId==s.positionPlayerId)game.NilfQueueReaction(source,2,s.positionPlayerId);
                if(s.instanceId==cause.instanceId && s.locationMask==8 && m.currentPlayerId==s.positionPlayerId && id==162306)game.NilfQueueReaction(source,1,s.positionPlayerId);
                if((s.locationMask&7)!=0 && id==162317 && m.currentPlayerId==s.positionPlayerId)RandomDamage(source,BetaGwentOpponentId(s.positionPlayerId),7,2,1);
            }
            if((s.locationMask&7)==0)continue;
            // Graph334 arms only after the chosen card actually moves from
            // this player's inactive zone to Active/Graveyard. Bounce is a later
            // BeforeTurnEnd graph, independent of child completion.
            if(id==200162 && kind==3 && cause.instanceId==source.nilfCounter && cause.positionPlayerId==s.positionPlayerId && (cause.locationMask&248)!=0 && target && (t.locationMask&39)!=0)source.nilfTurnArmed=true;
            if(id==162312 && kind==3 && cause.locationMask==16 && target && t.locationMask==8 && t.instanceId!=s.instanceId)game.MonsterPower(source,source,1);
            // Spawn (12) is also an arrival: Cow Carcass already has Spying here.
            // The preceding move notification uses its final position, so it
            // does not count as another arrival and cannot trigger twice.
            if((kind==3 || kind==11 || kind==12) && target && (t.locationMask&7)!=0 && t.instanceId!=s.instanceId && (kind==11 || kind==12 || (cause.locationMask&7)==0 || cause.positionPlayerId!=t.positionPlayerId))
            {
                if(id==200296 && t.positionPlayerId==s.positionPlayerId)game.MonsterPower(source,source,1);
                if((t.tokenMask&128)!=0 && t.positionPlayerId!=s.positionPlayerId)
                {
                    // Beta ExecutionStack pops the played spy's AfterMoved after the ability
                    // that already brought this Brigade into play, so a spy counted by the
                    // deploy clause would feed the "appears" trigger a second time. Each
                    // counted spy gives up exactly that one deferred notification; a spy that
                    // appears later in the round still boosts.
                    if(id==162307){j=source.monsterIds.FindFirst(t.instanceId);if(j>=0)source.monsterIds.Erase(j);else game.MonsterPower(source,source,2);}
                    if(id==162308 && kind==11 && m.currentPlayerId==s.positionPlayerId)source.nilfCounter+=1;
                }
            }
            if(kind==4 && id==200294 && target && game.NorthActingSide(target)==s.positionPlayerId && BetaGwentNorthernCategory(t.runtimeTemplate.templateId,2)){
                // Beta ExecutionStack: AfterPlayed on push, AfterMoved(From=hand) on pop of the
                // SAME play. Our soldier has already landed, so the pop reaction is due now,
                // always on the owner's own play ("каждый раз, когда играете солдата").
                source.nilfCounter=t.instanceId;}
            if(kind==3 && id==200294 && target && t.instanceId!=s.instanceId && ((cause.locationMask&767)!=0 || playedArrival) && (t.locationMask&7)!=0 && source.nilfCounter==t.instanceId){source.nilfCounter=0;game.NilfQueueReaction(source,3,s.positionPlayerId);}
            if(kind==5 && id==162212 && cause.positionPlayerId==s.positionPlayerId && (s.tokenMask&128)!=0)game.MonsterPower(source,source,1);
            if(kind==6 && (cause.positionPlayerId==s.positionPlayerId || (id==162402 && ((s.positionPlayerId==1 && m.playerOne.hasPassed) || (s.positionPlayerId==2 && m.playerTwo.hasPassed)))))
            {
                if(id==162308){source.nilfTurnArmed=true;source.nilfCounter=0;}
                if(id==162402 && s.timerValue>0 && !(m.playerOne.hasPassed && m.playerTwo.hasPassed))game.QueueTimer(source,0,1);
            }
            if(kind==7 && id==162212 && cause.positionPlayerId==s.positionPlayerId && (s.tokenMask&128)!=0)game.QueueRelocationAt(source,BetaGwentOpponentId(s.positionPlayerId),s.locationMask,s.locationIndex);
            if(kind==8 && id==152312 && cause.positionPlayerId!=s.positionPlayerId && cause.locationMask==s.locationMask)game.MonsterPower(source,source,1);
        }
        if(kind==9 && cause.runtimeTemplate.templateId==162212 && (cause.tokenMask&4)==0)
        {Query(cause.positionPlayerId,cause.locationMask,15,4,8,0,NULL,ids);least=2147483647;for(j=0;j<ids.Size();j+=1){t=game.FindCard(ids[j]).Snapshot();least=Min(least,t.power.currentPower);}for(j=ids.Size()-1;j>=0;j-=1){t=game.FindCard(ids[j]).Snapshot();if(t.power.currentPower!=least)ids.Erase(j);}if(ids.Size()>0)game.QueueDestroy(game.FindCard(ids[game.RandomIndex(ids.Size())]));}
    }
}
