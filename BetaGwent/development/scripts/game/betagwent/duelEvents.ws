// Concrete AfterTurn/Killed graph consumers for the closed duel.
// This is not the full original AbilityManager/ActionManager coordinator.
class CBetaGwentDuelEvent extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var kind, batchSerial : int;
    public var source, cause : SBetaGwentCardSnapshot;
    public var rowToken : int;
    public var rowTargets : array<int>;
    public var banishedConsume : bool;
}

class CBetaGwentDuelEvents extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var pending : array<CBetaGwentDuelEvent>;
    public var batchSerial : int;
    public function Count() : int { return pending.Size(); }
    public function NextBatchSerial() : int { if (pending.Size() == 0) return 0; return pending[0].batchSerial; }
    public function Pop() : CBetaGwentDuelEvent
    {
        var item : CBetaGwentDuelEvent;
        if (pending.Size() == 0) return NULL; item = pending[0]; pending.Erase(0); return item;
    }
    private function PrependBatch(batch : array<CBetaGwentDuelEvent>)
    {
        var i : int;
        if (batch.Size() == 0) return;
        if (pending.Size() + batch.Size() > 1024) { game.FailAbility("Превышен лимит пассивных событий."); return; }
        batchSerial += 1;
        // AbilityManager.Trigger inserts a sorted batch at the front, preserving its order.
        for (i = batch.Size() - 1; i >= 0; i -= 1)
        { batch[i].batchSerial = batchSerial; pending.Insert(0, batch[i]); }
    }
    public function Initialize(owner : CBetaGwentDuelSession) { game = owner; }
    public function RowAbility(kind : int, token : int, side : int, row : int, templateId : int, targets : array<int>)
    {
        var item : CBetaGwentDuelEvent; var batch : array<CBetaGwentDuelEvent>;
        item = new CBetaGwentDuelEvent in this; item.kind = kind; item.rowToken = token; item.rowTargets = targets;
        // Original row abilities have BoardManager as owner, no card instance.
        item.source.positionPlayerId = side; item.source.locationMask = row; item.source.runtimeTemplate.templateId = templateId;
        batch.PushBack(item); PrependBatch(batch);
    }
    public function AfterTurn(side : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>;
        var batch : array<CBetaGwentDuelEvent>;
        var tickets : array<SBetaGwentTriggerTicket>;
        var ticket : SBetaGwentTriggerTicket;
        var item : CBetaGwentDuelEvent;
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var i, index : int;
        game.GetCards(cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].card; d = BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
            // OwnerLocation=Active7, IsAmbushing=false, owner-player filter.
            if ((d.passiveBoost == 0 && d.header.templateId != 201781) || s.positionPlayerId != side || (s.locationMask & 7) == 0
                || s.isWaitingToDie || (s.tokenMask & 12) != 0) continue;
            ticket.instanceId = s.instanceId; ticket.ownerPresent = true;
            ticket.priority = d.passivePriority; ticket.locationMask = s.locationMask;
            ticket.ownerPlayerId = s.positionPlayerId; ticket.ownerIndex = s.locationIndex;
            index = BetaGwentTriggerInsertionIndex(tickets, ticket, side);
            if (index < 0) { game.FailAbility("Неизвестный порядок пассивных событий."); return; }
            item = new CBetaGwentDuelEvent in this; item.kind = 1; item.source = s;
            if (d.header.templateId == 201781) { item.kind = 10; item.rowToken = 2; }
            tickets.Insert(index, ticket); batch.Insert(index, item);
        }
        // Source Trigger reverses its sorted batch into front insertion; net order is this batch.
        PrependBatch(batch);
    }
    public function BeforeTurn(side : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>; var batch : array<CBetaGwentDuelEvent>;
        var tickets : array<SBetaGwentTriggerTicket>; var ticket : SBetaGwentTriggerTicket;
        var item : CBetaGwentDuelEvent; var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i, index : int;
        game.GetCards(cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].card; d = BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
            if ((d.timerPeriod == 0 && d.header.templateId != 200038) || s.positionPlayerId != side || (s.locationMask & 7) == 0
                || s.isWaitingToDie || s.power.currentPower <= 0 || (s.tokenMask & 12) != 0) continue;
            ticket.instanceId = s.instanceId; ticket.ownerPresent = true; ticket.priority = d.timerPriority;
            ticket.locationMask = s.locationMask; ticket.ownerPlayerId = s.positionPlayerId; ticket.ownerIndex = s.locationIndex;
            index = BetaGwentTriggerInsertionIndex(tickets, ticket, side);
            if (index < 0) { game.FailAbility("Неизвестный порядок событий начала хода."); return; }
            item = new CBetaGwentDuelEvent in this; item.kind = 6; item.source = s;
            if (d.header.templateId == 132108 || d.header.templateId == 200038) { item.kind = 10; item.rowToken = 1; }
            tickets.Insert(index, ticket); batch.Insert(index, item);
        }
        PrependBatch(batch);
    }
    public function TimerExpired(s : SBetaGwentCardSnapshot)
    {
        var d : SBetaGwentDuelDefinition; var item : CBetaGwentDuelEvent; var batch : array<CBetaGwentDuelEvent>;
        d = BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
        // AbilityManager.OnCardTimerTriggered checks presence of graph and Lock; no passive sort.
        if (d.timerPeriod == 0 || d.header.templateId == 132108 || (s.tokenMask & 4) != 0) return;
        item = new CBetaGwentDuelEvent in this; item.kind = 7; item.source = s;
        batch.PushBack(item); PrependBatch(batch);
    }
    public function BeforeConsume(attacker : SBetaGwentCardSnapshot, target : SBetaGwentCardSnapshot)
    {
        var d : SBetaGwentDuelDefinition; var item : CBetaGwentDuelEvent; var batch : array<CBetaGwentDuelEvent>;
        d = BetaGwentDuelDefinition(target.runtimeTemplate.templateId);
        // Closed BeforeDestroyed graph: Targets contains owner, RemovalType=Consume.
        if (d.beforeConsumeAttackerBoost == 0 || (target.locationMask & 63) == 0
            || target.isWaitingToDie || target.power.currentPower <= 0 || (target.tokenMask & 12) != 0) return;
        item = new CBetaGwentDuelEvent in this; item.kind = 4; item.source = target; item.cause = attacker;
        batch.PushBack(item); PrependBatch(batch);
    }
    public function BeforeTurnEnd(side : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>; var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i : int; var card : CBetaGwentDuelCard;
        game.GetCards(cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].card; d = BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
            if (d.beforeConsumeAttackerBoost == 0 || s.positionPlayerId != side || (s.locationMask & 7) == 0
                || s.isWaitingToDie || s.power.currentPower <= 0 || (s.tokenMask & 12) != 0) continue;
            card = game.FindCard(s.instanceId); if (card) card.StoreConsumeAttacker(0);
        }
    }
    public function AfterConsume(attacker : SBetaGwentCardSnapshot, target : SBetaGwentCardSnapshot, optional banished : bool)
    {
        var cards : array<SBetaGwentDevelopmentCard>; var batch : array<CBetaGwentDuelEvent>;
        var tickets : array<SBetaGwentTriggerTicket>; var ticket : SBetaGwentTriggerTicket;
        var item : CBetaGwentDuelEvent; var m : SBetaGwentMatchSnapshot;
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var i, index, eventMask : int; var eggBanish : bool;
        eventMask = 1; if (banished) eventMask = 2;
        if (target.instanceId == 0) return; game.GetCards(cards); m = game.Snapshot();
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].card; d = BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
            // APassiveTrigger: location, IsAlive, Lock and IsAmbushing; graph compares current players.
            eggBanish = banished && d.banishedConsumeAttackerBoost > 0 && s.locationMask == 512 && s.instanceId == target.instanceId;
            if (!eggBanish && (d.consumePassiveBoost == 0 || (d.consumePassiveEvents & eventMask) == 0
                || (s.locationMask & d.consumePassiveLocations) == 0 || s.positionPlayerId != attacker.positionPlayerId)) continue;
            if (s.isWaitingToDie || s.power.currentPower <= 0 || (s.tokenMask & 12) != 0) continue;
            ticket.instanceId = s.instanceId; ticket.ownerPresent = true; ticket.priority = d.consumePassivePriority;
            ticket.locationMask = s.locationMask; ticket.ownerPlayerId = s.positionPlayerId; ticket.ownerIndex = s.locationIndex;
            index = BetaGwentTriggerInsertionIndex(tickets, ticket, m.currentPlayerId);
            if (index < 0) { game.FailAbility("Неизвестный порядок реакции на поглощение."); return; }
            item = new CBetaGwentDuelEvent in this; item.kind = 3; if (eggBanish) item.kind = 5; item.source = s; item.cause = attacker; item.banishedConsume = banished;
            tickets.Insert(index, ticket); batch.Insert(index, item);
        }
        PrependBatch(batch);
    }
    public function Killed(cards : array<SBetaGwentCardSnapshot>)
    {
        var i : int; var d : SBetaGwentDuelDefinition; var item : CBetaGwentDuelEvent; var batch : array<CBetaGwentDuelEvent>;
        // KillCardsAction walks the list backwards, OnCardKilled adds at the front.
        // Net deathwish order retains the pending-death batch order, not passive sort order.
        for (i = 0; i < cards.Size(); i += 1)
        {
            d = BetaGwentDuelDefinition(cards[i].runtimeTemplate.templateId);
            if ((d.deathwishDamage == 0 && d.deathwishSpawnCount == 0 && d.deathwishSummonTemplate == 0 && d.header.templateId != 200038 && d.header.templateId != 122206 && d.header.templateId != 112207 && d.header.templateId != 112215) || (cards[i].locationMask & 7) == 0 || (cards[i].tokenMask & 4) != 0) continue;
            item = new CBetaGwentDuelEvent in this; item.kind = 2; item.source = cards[i];
            if (d.header.templateId == 122206 || d.header.templateId == 112207 || d.header.templateId == 112215) { item.kind = 11; item.rowToken = 3; }
            batch.PushBack(item);
        }
        PrependBatch(batch);
    }
    public function NorthTrigger(kind : int, cause : SBetaGwentCardSnapshot)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var batch : array<CBetaGwentDuelEvent>;
        var tickets : array<SBetaGwentTriggerTicket>;var ticket : SBetaGwentTriggerTicket;
        var item : CBetaGwentDuelEvent;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        var i, id, zone, index : int;var eligible : bool;var aborted : array<int>;
        game.GetCards(cards);m=game.Snapshot();
        for(i=0;i<cards.Size();i+=1)
        {
            s=cards[i].card;id=s.runtimeTemplate.templateId;eligible=false;zone=7;
            if(kind==1){eligible=id==122213 || id==122313;if(id==122313)zone=16;}
            else if(kind==2){eligible=id==122308 || id==122315 || id==123301 || id==200529 || id==112207;if(id==200529 || id==112207)zone=32;}
            else if(kind==4)eligible=id==122306 || id==122309;
            else if(kind==5){eligible=id==122311 || id==201624;if(id==122311)zone=16;}
            else if(kind==6)eligible=id==122317 && s.instanceId==cause.instanceId;
            else if(kind==7){eligible=id==122101;zone=31;}
            if(!eligible || (s.locationMask&zone)==0 || s.isWaitingToDie || (s.tokenMask&12)!=0 || s.power.currentPower<=0)continue;
            if((kind==1 || kind==2) && s.positionPlayerId!=cause.positionPlayerId)continue;
            if(kind==5 && id==122311){if(aborted.Contains(s.positionPlayerId))continue;aborted.PushBack(s.positionPlayerId);}
            ticket.instanceId=s.instanceId;ticket.ownerPresent=true;ticket.priority=0;ticket.locationMask=s.locationMask;
            ticket.ownerPlayerId=s.positionPlayerId;ticket.ownerIndex=s.locationIndex;index=BetaGwentTriggerInsertionIndex(tickets,ticket,m.currentPlayerId);
            if(index<0){game.FailAbility("Неизвестный порядок событий Севера.");return;}
            item=new CBetaGwentDuelEvent in this;item.kind=11;item.rowToken=kind;item.source=s;item.cause=cause;
            tickets.Insert(index,ticket);batch.Insert(index,item);
        }
        PrependBatch(batch);
    }
    public function Flush() : bool
    {
        return game.FlushEffects();
    }
    public function MonsterTrigger(kind : int, cause : SBetaGwentCardSnapshot)
    {
        var cards : array<SBetaGwentDevelopmentCard>; var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var batch : array<CBetaGwentDuelEvent>; var item : CBetaGwentDuelEvent;
        var tickets : array<SBetaGwentTriggerTicket>; var ticket : SBetaGwentTriggerTicket;
        var m : SBetaGwentMatchSnapshot; var i, id, index : int; var eligible : bool; var deckTriggers : array<int>;
        game.GetCards(cards); m = game.Snapshot();
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].card; d = BetaGwentDuelDefinition(s.runtimeTemplate.templateId); id = d.header.templateId; eligible = false;
            if (kind == 3) eligible = id == 132212 || id == 132301 || id == 201600 || id == 200114;
            else if (kind == 4) eligible = id == 200301 || id == 132212 || id == 132315 || id == 201600 || id == 200114 || id == 200174;
            else if (kind == 6) eligible = id == 132201;
            if (!eligible || s.isWaitingToDie || s.power.currentPower <= 0 || (s.tokenMask & 12) != 0) continue;
            if (id == 132301 || id == 132315)
            {
                if (s.locationMask != 16) continue;
                // AbortForAbility compares the shared StartTrigger and TriggerInfo references.
                // Foglet/Harpy copies share both; the first successful graph summons one copy.
                if (deckTriggers.Contains(id * 2 + s.positionPlayerId)) continue; deckTriggers.PushBack(id * 2 + s.positionPlayerId);
            }
            else if ((s.locationMask & 7) == 0) continue;
            ticket.instanceId = s.instanceId; ticket.ownerPresent = true; ticket.priority = 0; ticket.locationMask = s.locationMask;
            ticket.ownerPlayerId = s.positionPlayerId; ticket.ownerIndex = s.locationIndex;
            index = BetaGwentTriggerInsertionIndex(tickets, ticket, m.currentPlayerId);
            if (index < 0) { game.FailAbility("Неизвестный порядок пассивных способностей Чудовищ."); return; }
            item = new CBetaGwentDuelEvent in this; item.kind = 10; item.rowToken = kind; item.source = s; item.cause = cause;
            tickets.Insert(index, ticket); batch.Insert(index, item);
        }
        PrependBatch(batch);
    }
    public function MonsterSpawn(s : SBetaGwentCardSnapshot)
    {
        var item : CBetaGwentDuelEvent; var batch : array<CBetaGwentDuelEvent>;
        if (s.runtimeTemplate.templateId != 132404 && s.runtimeTemplate.templateId != 200174) return;
        item = new CBetaGwentDuelEvent in this; item.kind = 10; item.rowToken = 5; item.source = s; batch.PushBack(item); PrependBatch(batch);
    }
    public function MonsterDamaged(card : CBetaGwentDuelCard, cause : SBetaGwentCardSnapshot)
    {
        var item : CBetaGwentDuelEvent; var batch : array<CBetaGwentDuelEvent>; var s : SBetaGwentCardSnapshot;
        if (!card) return; s = card.Snapshot(); if (s.runtimeTemplate.templateId != 200052 || cause.instanceId == s.instanceId) return;
        item = new CBetaGwentDuelEvent in this; item.kind = 10; item.rowToken = 7; item.source = s; item.cause = cause;
        batch.PushBack(item); PrependBatch(batch);
    }

}
