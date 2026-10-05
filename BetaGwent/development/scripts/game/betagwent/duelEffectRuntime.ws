// Concrete closed-duel coordinator: managed ApplyAction and nested passive FIFOs.
// Original full controller/graph/request/network lifecycle remains separate.
struct SBetaGwentDuelCueContext
{ var id, templateId, side, row : int; }
class CBetaGwentDuelPassiveFrame extends IScriptable
{
    public var actions : CBetaGwentActionQueue;
    public var source : SBetaGwentCardSnapshot;
    public var batchSerial : int;
}
class CBetaGwentDuelActionServices extends CBetaGwentActionServices
{
    private var runtime : CBetaGwentDuelEffectRuntime;
    public function Initialize(value : CBetaGwentDuelEffectRuntime) { runtime = value; }
    public function EmitBeforeDiagnostic(action : CBetaGwentManagedAction)
    { LogChannel('BetaGwent', "DUEL_MANAGER_BEFORE_DIAGNOSTIC"); }
    public function LogAction(valid : bool, action : CBetaGwentManagedAction) : bool
    { if (!valid) runtime.RecordSkipped(); return true; }
    // All supported effects are local, not network/request/cache objects.
    public function DestroyAction(action : CBetaGwentManagedAction) : bool { return true; }
}
class CBetaGwentDuelEffectAction extends CBetaGwentManagedAction
{
    private var attacker : CBetaGwentDuelCard;
    private var target : CBetaGwentDuelCard;
    private var runtime : CBetaGwentDuelEffectRuntime;
    private var operation, amount, allowedLocations : int;
    private var ignoreArmor : bool;

    public function Setup(owner : CBetaGwentDuelEffectRuntime, card : CBetaGwentDuelCard,
        kind : int, value : int, bypassArmor : bool, context : CBetaGwentActionContext, optional source : CBetaGwentDuelCard, optional locations : int) : bool
    {
        allowedLocations = 7; if (locations == 31 && kind == 1 && value > 0) allowedLocations = 31;
        if (kind == 12 && value > 0 && (locations == 31 || locations == 32 || locations == 543)) allowedLocations = locations;
        if (kind == 8 && value == 200457) allowedLocations = 32;
        if (kind == 2 && locations == 32) allowedLocations = 32;
        if((kind==1 || kind==11) && (locations==8 || locations==15))allowedLocations=locations;
        if(kind==19 && (locations==7 || locations==8 || locations==32))allowedLocations=locations;
        if ((kind == 15 || kind == 18) && locations == 16) allowedLocations = 16;
        runtime = owner; attacker = source; target = card; operation = kind; amount = value; ignoreArmor = bypassArmor;
        SetStateChanging(true); return Prepare(context);
    }
    public function IsValid() : bool
    {
        var s : SBetaGwentCardSnapshot;
        if (!target || !runtime || operation < 1 || operation > 19) return false;
        if (operation == 4 || operation == 5)
        { if (!attacker) return false; s = attacker.Snapshot(); if ((s.locationMask & 7) == 0 || s.isWaitingToDie) return false; }
        s = target.Snapshot();
        if (operation == 5) return (s.locationMask == 32 || s.locationMask == 8) && !s.isWaitingToDie;
        if (operation == 14) return (s.locationMask & 7) != 0 && (bool)attacker;
        return (s.locationMask & allowedLocations) != 0 && !s.isWaitingToDie;
    }
    protected function BeforeApplyImpl()
    { runtime.RecordBefore(); if (operation == 4) runtime.BeforeConsume(attacker, target); }
    protected function ApplyImpl() : bool
    {
        var old, next : SBetaGwentCardSnapshot;
        old = target.Snapshot();
        if (operation == 1) target.ChangePower(amount, ignoreArmor);
        else if (operation == 2) target.Power().AddArmor(amount);
        else if (operation == 3) target.Kill();
        else if (operation == 4) { target.Kill(); runtime.RecordConsume(attacker, target); }
        else if (operation == 5) { if (!runtime.BanishConsumed(attacker, target)) return false; }
        else if (operation == 6) { if (!target.ToggleLock()) return false; }
        else if (operation == 7) { if (!target.MultiplyCurrentPower(amount)) return false; }
        else if (operation == 8) { if (!target.TransformFigurine(amount)) return false; }
        else if (operation == 9) { if (!target.ResetCurrentPower()) return false; }
        else if (operation == 10) { if (!target.ToggleResilience()) return false; }
        else if (operation == 11) { if (!target.Power().SetPower(amount)) return false; }
        else if (operation == 12) { if (!target.ChangeBasePower(amount, ignoreArmor)) return false; }
        else if (operation == 13) { if (!target.Power().RestorePower(amount)) return false; }
        else if (operation == 14) { if (!runtime.BanishOrdinary(attacker, target)) return false; }
        else if (operation == 15) target.Power().AddArmor(amount);
        else if (operation == 16) target.Power().SetCurrentPair(old.power.currentPower, 0);
        else if (operation == 18) target.ResetCurrentPower();
        else if(operation==19)target.Power().SetBasePower(amount);
        else return false;
        next = target.Snapshot();
        runtime.NilfPowerChanged(attacker,target,old,next,operation);
        if ((operation == 1 || operation == 12) && next.power.currentPower + next.power.basePower < old.power.currentPower + old.power.basePower)
            runtime.MonsterDamaged(attacker, target);
        runtime.RecordApplied(); return true;
    }
    protected function AfterApplyImpl() : bool
    {
        runtime.RecordAfter();
        if (operation == 4 || operation == 5) return runtime.AfterConsume(attacker, target, operation == 5);
        return true;
    }
}

class CBetaGwentDuelEffectRuntime extends CBetaGwentActionSink
{
    private var game : CBetaGwentDuelSession;
    private var queue : CBetaGwentActionQueue;
    private var context : CBetaGwentManagerContext;
    private var manager : CBetaGwentActionManager;
    private var services : CBetaGwentDuelActionServices;
    private var frames : array<CBetaGwentDuelPassiveFrame>;
    private var buildingFrame : CBetaGwentDuelPassiveFrame;
    private var dispatchingFrame : CBetaGwentDuelPassiveFrame;
    private var passiveCount, maximumDepth : int;
    private var failed, running : bool;
    private var beforeCount, appliedCount, afterCount, skippedCount : int;

    public function Initialize(owner : CBetaGwentDuelSession)
    {
        game = owner; context = new CBetaGwentManagerContext in this; context.SetAuthority(true); context.SetVerbose(true);
        // Local managed effects: no fabricated network IDs, transport or pause service.
        context.SetMain(false); services = new CBetaGwentDuelActionServices in this; services.Initialize(this);
        manager = new CBetaGwentActionManager in this;
        if (!manager.Initialize(context, services)) failed = true;
        queue = new CBetaGwentActionQueue in this;
        if (!queue.Initialize(true, true, this) || !queue.BindAuthority(context)) failed = true;
    }
    public function Enqueue(card : CBetaGwentDuelCard, kind : int, value : int, bypassArmor : bool, optional source : CBetaGwentDuelCard, optional locations : int) : bool
    {
        var action : CBetaGwentDuelEffectAction;
        if (failed || !card || kind < 1 || kind > 19) return false;
        action = new CBetaGwentDuelEffectAction in this;
        if (!action.Setup(this, card, kind, value, bypassArmor, context, source, locations) || !PushPrepared(action))
        { failed = true; return false; }
        return true;
    }
    public function EnqueueRelocation(card : CBetaGwentDuelCard, side : int, row : int, resetHand : bool) : bool
    {
        var action : CBetaGwentDuelRelocateAction;
        if (failed || !card) return false;
        action = new CBetaGwentDuelRelocateAction in this;
        if (!action.Setup(this, game, card, side, row, resetHand, context) || !PushPrepared(action)) { failed = true; return false; }
        return true;
    }
    public function EnqueueSpawn(fromPosition : SBetaGwentCardSnapshot, templateId : int, ids : array<int>) : bool
    {
        var action : CBetaGwentDuelSpawnAction;
        if (failed) return false;
        action = new CBetaGwentDuelSpawnAction in this;
        if (!action.Setup(this, game, fromPosition, templateId, ids, context) || !PushPrepared(action))
        { failed = true; return false; }
        return true;
    }
    public function EnqueueTimer(card : CBetaGwentDuelCard, operation : int, value : int) : bool
    {
        var action : CBetaGwentDuelTimerAction;
        if (failed || !card || operation < 0 || operation > 2) return false;
        action = new CBetaGwentDuelTimerAction in this;
        if (!action.Setup(this, card, operation, value, context) || !PushPrepared(action)) { failed = true; return false; }
        return true;
    }
    public function EnqueueCreatedCard(source : CBetaGwentDuelCard, templateId : int, id : int) : bool
    {
        var action : CBetaGwentDuelCreatedCardAction;
        if (failed || !source || id == 0) return false;
        action = new CBetaGwentDuelCreatedCardAction in this;
        if (!action.Setup(this, game, source, templateId, id, context) || !PushPrepared(action)) { failed = true; return false; }
        return true;
    }
    public function EnqueueDeckMove(fromPosition : SBetaGwentCardSnapshot, card : CBetaGwentDuelCard) : bool
    {
        var action : CBetaGwentDuelMoveAction;
        if (failed || !card) return false;
        action = new CBetaGwentDuelMoveAction in this;
        if (!action.Setup(this, game, fromPosition, card, context) || !PushPrepared(action))
        { failed = true; return false; }
        return true;
    }
    public function BeforeConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { game.BeforeConsume(source, target); }
    public function BanishConsumed(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    { return game.BanishConsumed(source, target); }
    public function BanishOrdinary(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    { return game.BanishOrdinary(source, target); }
    public function AfterConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, optional banished : bool) : bool
    { return game.AfterConsume(source, target, banished); }
    public function RecordConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { game.RecordConsume(source, target); }
    private function PushPrepared(action : CBetaGwentManagedAction) : bool
    {
        if (buildingFrame) return buildingFrame.actions.Push(action, false);
        if (dispatchingFrame) return dispatchingFrame.actions.Push(action, false);
        return queue.Push(action, false);
    }
    public function MonsterDamaged(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) { game.MonsterDamaged(source, target); }
    public function NilfPowerChanged(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, old : SBetaGwentCardSnapshot, current : SBetaGwentCardSnapshot, operation : int)
    {game.NilfPowerChanged(source,target,old,current,operation);}
    public function EnqueueMonsterDuel(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, retaliation : bool, heal : int, armor : int) : bool
    {
        var action : CBetaGwentMonsterDuelAction;
        if (failed || !source || !target) return false;
        action = new CBetaGwentMonsterDuelAction in this;
        if (!action.Setup(this, game, source, target, retaliation, heal, armor, context) || !PushPrepared(action)) { failed = true; return false; }
        return true;
    }
    public function DispatchAction(action : CBetaGwentQueuedAction)
    {
        var managed : CBetaGwentManagedAction;
        managed = (CBetaGwentManagedAction)action;
        if (!managed || !manager.ApplyAction(managed)) failed = true;
    }
    private function HasWork() : bool
    { return queue.Count() > 0 || frames.Size() > 0 || game.PendingEventCount() > 0; }
    private function ResolveNextPassive()
    {
        var item : CBetaGwentDuelEvent; var frame : CBetaGwentDuelPassiveFrame;
        item = game.PopDuelEvent(); if (!item) { failed = true; return; }
        frame = new CBetaGwentDuelPassiveFrame in this; frame.source = item.source; frame.batchSerial = item.batchSerial;
        frame.actions = new CBetaGwentActionQueue in frame;
        if (!frame.actions.Initialize(true, true, this) || !frame.actions.BindAuthority(context)) { failed = true; return; }
        // Build just this graph's actions. Its own FIFO is completed before the
        // next sibling passive; a newly triggered batch can interrupt it.
        buildingFrame = frame; game.ResolveDuelEvent(item); buildingFrame = NULL; passiveCount += 1;
        if (game.IsFatal()) { failed = true; return; }
        if (frame.actions.Count() > 0)
        {
            if (frames.Size() >= 64) { failed = true; return; }
            frames.PushBack(frame); maximumDepth = Max(maximumDepth, frames.Size());
        }
    }
    private function StepCoordinated() : bool
    {
        var frame : CBetaGwentDuelPassiveFrame; var previous : SBetaGwentDuelCueContext;
        if (game.PendingEventCount() > 0)
        {
            if (frames.Size() == 0) { ResolveNextPassive(); return !failed; }
            frame = frames[frames.Size() - 1];
            if (game.NextEventBatchSerial() > frame.batchSerial) { ResolveNextPassive(); return !failed; }
        }
        if (frames.Size() > 0)
        {
            frame = frames[frames.Size() - 1];
            if (frame.actions.Count() == 0) { frames.Erase(frames.Size() - 1); return true; }
            previous = game.GetVisualSource();
            game.SetVisualSource(frame.source.instanceId, frame.source.runtimeTemplate.templateId, frame.source.positionPlayerId, frame.source.locationMask);
            dispatchingFrame = frame;
            if (!frame.actions.Step()) failed = true;
            dispatchingFrame = NULL;
            game.SetVisualSource(previous.id, previous.templateId, previous.side, previous.row);
            return !failed;
        }
        return queue.Step();
    }
    public function Flush() : bool
    {
        var steps : int;
        if (running) return !failed;
        running = true;
        while (!failed && !game.IsFatal() && HasWork() && steps < 4096)
        { if (!StepCoordinated()) failed = true; steps += 1; }
        if (HasWork() || manager.IsFaulted() || game.IsFatal()) failed = true;
        running = false;
        if (failed) game.FailAbility("Не удалось завершить очередь эффекта и пассивных реакций.");
        return !failed;
    }
    public function RecordSkipped() { skippedCount += 1; }
    public function RecordBefore() { beforeCount += 1; }
    public function RecordApplied() { appliedCount += 1; }
    public function RecordAfter() { afterCount += 1; }
    public function Report()
    {
        LogChannel('BetaGwent', "DUEL_EFFECT_SUMMARY before=" + beforeCount + " applied=" + appliedCount
            + " after=" + afterCount + " skipped=" + skippedCount + " pending=" + queue.Count()
            + " passivePending=" + game.PendingEventCount() + " passiveFrames=" + frames.Size() + " passiveDone=" + passiveCount
            + " maxPassiveDepth=" + maximumDepth + " managed=" + manager.GetDispatchCount() + " dirty=" + context.IsDirty());
    }
}

// One original SpawnCardsAction owns all preallocated requests.
class CBetaGwentDuelSpawnAction extends CBetaGwentManagedAction
{
    private var runtime : CBetaGwentDuelEffectRuntime;
    private var game : CBetaGwentDuelSession;
    private var fromPosition : SBetaGwentCardSnapshot;
    private var templateId : int; private var ids : array<int>;
    public function Setup(owner : CBetaGwentDuelEffectRuntime, session : CBetaGwentDuelSession,
        sourcePosition : SBetaGwentCardSnapshot, template : int, requests : array<int>, context : CBetaGwentActionContext) : bool
    {
        runtime = owner; game = session; fromPosition = sourcePosition; templateId = template; ids = requests;
        SetStateChanging(true); return Prepare(context);
    }
    public function IsValid() : bool
    { return (bool)runtime && (bool)game && ids.Size() > 0 && (fromPosition.locationMask & 7) != 0; }
    protected function BeforeApplyImpl() { runtime.RecordBefore(); }
    protected function ApplyImpl() : bool
    {
        var i : int;
        for (i = 0; i < ids.Size(); i += 1)
            if (!game.ApplySpawnRequest(fromPosition, templateId, ids[i])) return false;
        runtime.RecordApplied(); return true;
    }
    protected function AfterApplyImpl() : bool { runtime.RecordAfter(); return true; }
}

// Killed graph MoveCards: existing deck ID, no Played trigger or initial move.
class CBetaGwentDuelMoveAction extends CBetaGwentManagedAction
{
    private var runtime : CBetaGwentDuelEffectRuntime;
    private var game : CBetaGwentDuelSession;
    private var destination : SBetaGwentCardSnapshot;
    private var card : CBetaGwentDuelCard;
    public function Setup(owner : CBetaGwentDuelEffectRuntime, session : CBetaGwentDuelSession,
        fromPosition : SBetaGwentCardSnapshot, value : CBetaGwentDuelCard, context : CBetaGwentActionContext) : bool
    { runtime = owner; game = session; destination = fromPosition; card = value; SetStateChanging(true); return Prepare(context); }
    public function IsValid() : bool
    {
        var s : SBetaGwentCardSnapshot;
        if (!runtime || !game || !card) return false; s = card.Snapshot();
        return s.locationMask == 16 && !s.isWaitingToDie && s.positionPlayerId == destination.positionPlayerId;
    }
    protected function BeforeApplyImpl() { runtime.RecordBefore(); }
    protected function ApplyImpl() : bool
    { if (!game.ApplyDeckSummon(destination, card)) return false; runtime.RecordApplied(); return true; }
    protected function AfterApplyImpl() : bool { runtime.RecordAfter(); return true; }
}

// Concrete ChangeTimerAttack consumer; generic TimerChanged/Before-After hooks are not implemented.
class CBetaGwentDuelCreatedCardAction extends CBetaGwentManagedAction
{
    private var runtime : CBetaGwentDuelEffectRuntime;
    private var game : CBetaGwentDuelSession;
    private var source : CBetaGwentDuelCard;
    private var templateId, instanceId : int;
    public function Setup(owner : CBetaGwentDuelEffectRuntime, session : CBetaGwentDuelSession,
        creator : CBetaGwentDuelCard, requestedTemplate : int, id : int, context : CBetaGwentActionContext) : bool
    { runtime = owner; game = session; source = creator; templateId = requestedTemplate; instanceId = id; SetStateChanging(true); return Prepare(context); }
    public function IsValid() : bool
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!source || !game || !runtime || instanceId == 0 || game.FindCard(instanceId)) return false;
        s = source.Snapshot(); d = source.Definition();
        if (s.isWaitingToDie) return false;
        if (d.effect == 24) return (s.locationMask & 7) != 0 && (templateId == 113305 || templateId == 113312);
        if (d.effect == 28 && d.specialMode == 24) return s.locationMask == 256 && (templateId == d.playTemplateId || templateId == d.deploySpawnTemplate);
        if (d.effect == 28 && d.specialMode == 25) return s.locationMask == 256 && templateId == d.playTemplateId;
        if (d.effect == 34) return ((s.locationMask & 7) != 0 || s.locationMask == 256) && game.MonsterCreationAllowed(source, templateId);
        return false;
    }
    protected function BeforeApplyImpl() { runtime.RecordBefore(); }
    protected function ApplyImpl() : bool
    { if (!game.ApplyCreatedCard(source, templateId, instanceId)) return false; runtime.RecordApplied(); return true; }
    protected function AfterApplyImpl() : bool { runtime.RecordAfter(); return true; }
}
class CBetaGwentDuelTimerAction extends CBetaGwentManagedAction
{
    private var runtime : CBetaGwentDuelEffectRuntime;
    private var card : CBetaGwentDuelCard;
    private var operation, value : int;
    public function Setup(owner : CBetaGwentDuelEffectRuntime, target : CBetaGwentDuelCard,
        op : int, amount : int, context : CBetaGwentActionContext) : bool
    { runtime = owner; card = target; operation = op; value = amount; SetStateChanging(true); return Prepare(context); }
    public function IsValid() : bool
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!runtime || !card) return false; s = card.Snapshot(); d = card.Definition();
        // Swordsman's timer is driven by the Skellige graph, not the Vran scheduler.
        return (s.locationMask & 7) != 0 && !s.isWaitingToDie && s.power.currentPower > 0 && (d.timerPeriod > 0 || d.header.templateId == 200040);
    }
    protected function BeforeApplyImpl() { runtime.RecordBefore(); }
    protected function ApplyImpl() : bool
    { if (!card.ChangeTimer(value, operation)) return false; runtime.RecordApplied(); return true; }
    protected function AfterApplyImpl() : bool { runtime.RecordAfter(); return true; }
}

class CBetaGwentDuelRelocateAction extends CBetaGwentManagedAction
{
    private var runtime : CBetaGwentDuelEffectRuntime; private var game : CBetaGwentDuelSession;
    private var card : CBetaGwentDuelCard; private var side, row : int; private var resetHand : bool;
    public function Setup(owner : CBetaGwentDuelEffectRuntime, session : CBetaGwentDuelSession,
        target : CBetaGwentDuelCard, destinationSide : int, destinationRow : int, handReset : bool, context : CBetaGwentActionContext) : bool
    { runtime = owner; game = session; card = target; side = destinationSide; row = destinationRow; resetHand = handReset; SetStateChanging(true); return Prepare(context); }
    public function IsValid() : bool
    { return (bool)game && (bool)card && (side == 1 || side == 2) && (row == 1 || row == 2 || row == 4 || row == 8); }
    protected function BeforeApplyImpl() { runtime.RecordBefore(); }
    protected function ApplyImpl() : bool
    { if (!game.ApplyRelocation(card, side, row, resetHand)) return false; runtime.RecordApplied(); return true; }
    protected function AfterApplyImpl() : bool { runtime.RecordAfter(); return true; }
}
