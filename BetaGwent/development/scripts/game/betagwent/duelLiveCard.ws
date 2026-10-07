// Closed preview lifecycle. Supported deathwish dispatch is owned by the session death batches.
class CBetaGwentDuelPower extends CBetaGwentPowerNumbers
{
    public var card : CBetaGwentDuelCard;
    public function Attach(value : CBetaGwentDuelCard) { card = value; }
    public function ResetTemplatePower(base : int, armor : int) : bool
    { WriteBasePower(base); WritePermanentPower(0); return SetPowerAndArmor(base, armor); }
    public function SetCurrentPair(power : int, armor : int) : bool { return SetPowerAndArmor(power, armor); }
    protected function SetPowerAndArmor(power : int, armor : int) : bool
    {
        var oldPower, oldArmor : int;
        if (!card) return false;
        oldPower = GetCurrentPower(); oldArmor = GetCurrentArmor();
        power = Max(0, power); armor = Max(0, armor);
        if (oldPower == power && oldArmor == armor) return true;
        WriteCurrentPower(power); WriteCurrentArmor(armor);
        card.OnPowerChanged(oldPower, oldArmor);
        return true;
    }
}

class CBetaGwentDuelCard extends CBetaGwentRegistryCardReference
{
    public var cardState : SBetaGwentCardSnapshot;
    public var definition : SBetaGwentDuelDefinition;
    public var power : CBetaGwentDuelPower;
    public var game : CBetaGwentDuelSession;
    public var consumeAttackerId : int;
    public var playedChild : CBetaGwentDuelCard;
    public var monsterStage, monsterRemaining, monsterStored, monsterOnce : int;
    public var playFromLocation, lastActiveRow : int;
    public var northernCrew : bool;
    public var nilfCounter,neutralChoice : int;
    public var createdCopy : bool;
        public function NeutralReset(){cardState.tokenMask=cardState.tokenMask&-134;nilfCounter=0;ResetCurrentPower();}

    public function SetNilfCounter(value : int) {nilfCounter=value;}
    public var monsterIds : array<int>;
    public var selectedModeId : int;
    public function ResetModeChoice() { selectedModeId = 0; }
    public function SelectMode(choice : int) : bool
    { var ids : array<int>; BetaGwentDuelModeChoices(definition.header.templateId, ids); if (!ids.Contains(choice)) return false; selectedModeId = choice; return true; }
    public function StorePlayedChild(value : CBetaGwentDuelCard) { playedChild = value; }
    public function TakePlayedChild() : CBetaGwentDuelCard
    { var value : CBetaGwentDuelCard; value = playedChild; playedChild = NULL; return value; }
    public function StoreConsumeAttacker(id : int) { consumeAttackerId = id; }
    public function ConsumeAttackerId() : int { return consumeAttackerId; }
    public function Setup(owner : CBetaGwentDuelSession, id : int, templateId : int, side : int, zone : int, index : int)
    {
        definition = BetaGwentDuelDefinition(templateId); game = owner; monsterOnce = 1;
        cardState.instanceId = id; cardState.originTemplateId = templateId; cardState.runtimeTemplate = definition.header;
        cardState.runtimeTierMask = definition.header.tierMask;
        cardState.tokenMask = definition.tokens; cardState.timerValue = definition.initialTimer;
        cardState.ownerId = side; cardState.controllerId = side; cardState.positionPlayerId = side;
        cardState.locationMask = zone; cardState.locationIndex = index; cardState.canBePlayed = true;
        cardState.power.basePower = definition.header.power; cardState.power.currentPower = definition.header.power;
        cardState.power.armor = definition.header.armor;
        power = new CBetaGwentDuelPower in this; power.Attach(this); power.InitFromFields(cardState.power);
    }
    public function Snapshot() : SBetaGwentCardSnapshot { cardState.power = power.Snapshot(); return cardState; }
    public function Definition() : SBetaGwentDuelDefinition { if (selectedModeId == 0) return definition; return BetaGwentDuelModeDefinition(definition, selectedModeId); }
    public function IsMonsterAbility() : bool { return definition.effect == 34; }
    public function MonsterMode() : int { return definition.specialMode; }
    public function TemplateId() : int { return definition.header.templateId; }
    public function Power() : CBetaGwentDuelPower { return power; }
    public function RevealAmbush()
    {
        var previous : SBetaGwentDuelCueContext;
        if((cardState.tokenMask&8)==0)return;
        cardState.tokenMask-=8;
        previous=game.GetVisualSource();
        game.SetVisualSource(cardState.instanceId,definition.header.templateId,cardState.positionPlayerId,cardState.locationMask);
        game.RecordVisual(8,cardState.instanceId,"Засада раскрылась: "+definition.title,650,24);
        game.SetVisualSource(previous.id,previous.templateId,previous.side,previous.row);
        BetaGwentLog("DUEL_AMBUSH_REVEALED card="+cardState.instanceId+" template="+definition.header.templateId);
    }
    public function SetRevealed(value : bool)
    {if(value)cardState.tokenMask=cardState.tokenMask|64;else if((cardState.tokenMask&64)!=0)cardState.tokenMask-=64;}
    public function AddLock() {var old : int;old=cardState.tokenMask;cardState.tokenMask=(cardState.tokenMask|4)&-138;nilfCounter=0;game.RecordLockVisual(this,old);}
    public function ToggleSpying() {if((cardState.tokenMask&128)!=0)cardState.tokenMask-=128;else cardState.tokenMask+=128;}
    public function AddTokens(tokens : int) { cardState.tokenMask = cardState.tokenMask | tokens; }
    public function Move(side : int, zone : int, index : int)
    {
        // Original CardData.HandleDoomedTag: every move to Graveyard removes
        // a Doomed card. Death processing is not the only way to enter a grave.
        if (zone == 32 && (cardState.tokenMask & 512) != 0)
        {
            zone = 512; index = 0; cardState.canBePlayed = false; cardState.isWaitingToDie = false;
            BetaGwentLog("DUEL_DOOMED_REMOVED card=" + cardState.instanceId + " grave=false");
        }
        // CardData.OnCardMoved removes Lock when leaving the graveyard.
        if (cardState.locationMask == 32 && zone != 32 && (cardState.tokenMask & 4) != 0) cardState.tokenMask -= 4;
        if ((cardState.locationMask & 7) != 0 && (zone & 7) != 0 && side != cardState.positionPlayerId)
        { if ((cardState.tokenMask & 128) != 0) cardState.tokenMask -= 128; else cardState.tokenMask += 128; }
        cardState.controllerId = side;
        cardState.positionPlayerId = side; cardState.locationMask = zone; cardState.locationIndex = index;
    }
    // CardTokens.Toggle is XOR only: unlike Add, it does not call HandleLockAdded.
    public function ToggleLock() : bool
    {
        var old : int;
        old = cardState.tokenMask;
        if ((old & 4) != 0) cardState.tokenMask = old - 4;
        else cardState.tokenMask = old + 4;
        game.RecordLockVisual(this, old); return true;
    }
    public function ResetCurrentPower() : bool
    { return power.SetPower(power.GetBasePower() + power.GetPermanentPower()); }
    public function ToggleResilience() : bool
    {
        if ((cardState.tokenMask & 1) != 0) cardState.tokenMask -= 1; else cardState.tokenMask += 1;
        game.RecordResilienceVisual(this); return true;
    }
    public function MultiplyCurrentPower(multiplier : int) : bool
    {
        var result : int;
        if (!power.MultiplyValue(power.GetCurrentPower(), multiplier, result)) return false;
        // Morvudd ignores armor and keeps the current armor pair.
        return power.SetPower(result);
    }
    public function TransformFigurine(templateId : int) : bool
    {
        var next : SBetaGwentDuelDefinition; var old, oldTokens : int;
        if ((templateId != 200307 && templateId != 200457 && templateId != 201625 && templateId != 152405) || cardState.isWaitingToDie || ((cardState.locationMask & 7) == 0 && !(templateId == 200457 && cardState.locationMask == 32))) return false;
        // Original SetDefinition returns without reset when the definition is unchanged.
        if (definition.header.templateId == templateId) return true;
        next = BetaGwentDuelDefinition(templateId); if (next.header.templateId == 0) return false;
        old = definition.header.templateId; oldTokens = cardState.tokenMask; definition = next; consumeAttackerId = 0;
        cardState.runtimeTemplate = next.header; cardState.runtimeTierMask = next.header.tierMask; cardState.timerValue = next.initialTimer;
        // All reset: template base/armor, zero permanent, template-persistent tokens.
        // Owner, controller, position, existing instance ID and playability remain.
        if (!power.ResetTemplatePower(next.header.power, next.header.armor)) return false;
        cardState.tokenMask = next.tokens & 1792;
        game.TokensRemoved(this, oldTokens & 8);
        game.RecordTransformVisual(this, old); return true;
    }
    public function ChangeTimer(value : int, operation : int) : bool
    {
        var old, next : int;
        if (operation < 0 || operation > 2) return false;
        old = cardState.timerValue; next = value;
        if (operation == 0) { if (old <= 0) return true; next = Max(0, old - value); }
        else if (operation == 1) { if (old < 0) return true; next = old + value; }
        if (old == next) return true;
        cardState.timerValue = next; game.RecordTimerVisual(this, old, operation);
        // Original Set emits TimerTriggered only on the positive -> zero transition.
        if (old > 0 && next == 0) game.TimerExpired(this);
        return true;
    }
    public function SetPlayable(value : bool) { cardState.canBePlayed = value; }
    public function SetWaiting(value : bool) { cardState.isWaitingToDie = value; }
    public function CanDie() : bool
    { return definition.header.typeMask == 4 && ((cardState.locationMask & 7) != 0 || cardState.isInExecutionStack); }
    public function Kill()
    {
        if (cardState.isWaitingToDie) return;
        if (definition.header.typeMask == 4 && power.GetCurrentPower() > 0) power.SetPower(0);
        game.MarkDeath(this);
    }
    public function OnPowerChanged(oldPower : int, oldArmor : int)
    {
        BetaGwentLog("DUEL_POWER card=" + cardState.instanceId + " old=" + oldPower + "/" + oldArmor
            + " current=" + power.GetCurrentPower() + "/" + power.GetCurrentArmor());
        game.RecordPowerVisual(this, oldPower, oldArmor);
        if (oldArmor > 0 && power.GetCurrentArmor() == 0 && power.GetCurrentPower() > 0 && (cardState.locationMask & 7) != 0) game.NorthArmorBroken(this);
        if (power.GetCurrentPower() <= 0 && CanDie()) Kill();
    }
    public function ChangePower(delta : int, ignoreArmor : bool) : bool
    {
        var damage, armor : int;
        damage = delta; armor = power.GetCurrentArmor();
        // Original TryUseArmor: only negative current-power delta on active cards.
        if (!ignoreArmor && (cardState.locationMask & 7) != 0 && delta < 0)
        { armor = Max(0, power.GetCurrentArmor() + delta); damage = delta + power.GetCurrentArmor() - armor; }
        return power.SetCurrentPair(power.GetCurrentPower() + damage, armor);
    }
    public function ResetInHand()
    {
        // Active->Hand resets temporary power/tokens without a Killed event.
        cardState.tokenMask = cardState.tokenMask & 1792;
        if (BetaGwentDuelResetInInactive(cardState.runtimeTemplate.templateId)) cardState.timerValue = definition.initialTimer;
        power.SetCurrentPair(power.GetBasePower() + power.GetPermanentPower(), definition.header.armor);
    }
    public function ChangeBasePower(delta : int, ignoreArmor : bool) : bool
    {
        var armor, changed : int; armor = power.GetCurrentArmor(); changed = delta;
        if (!ignoreArmor && (cardState.locationMask & 7) != 0 && delta < 0)
        { armor = Max(0, power.GetCurrentArmor() + delta); changed = delta + power.GetCurrentArmor() - armor; }
        return power.SetBasePowerAndArmor(power.GetBasePower() + changed, armor);
    }
    public function ResetInGraveyard()
    {
        // Restore numbers after leaving the row; deathwish retains a separate FromPosition snapshot.
        // Inactive grave reset preserves Lock and template-persistent bits1792.
        cardState.tokenMask = cardState.tokenMask & 1796;
        if (BetaGwentDuelResetInInactive(cardState.runtimeTemplate.templateId)) cardState.timerValue = definition.initialTimer;
        power.SetCurrentPair(power.GetBasePower() + power.GetPermanentPower(), definition.header.armor); SetWaiting(false);
    }
}

class CBetaGwentDuelRegistry extends CBetaGwentRegistryIdStore
{
    public function Put(id : int, card : CBetaGwentDuelCard) : bool { return WriteSlot(id, card); }
    public function Find(id : int) : CBetaGwentDuelCard { return (CBetaGwentDuelCard)GetCard(id); }
}
