// Original ApplyAction control flow, with explicit services and bool failures.
// No serialization/network/time/cache implementation is hidden in this layer.
struct SBetaGwentDelay64
{
    var highWord : int; // signed high 32 bits
    var lowWord : int;  // raw low 32 bits, represented by signed int
}
function BetaGwentDelay64FromInt(value : int) : SBetaGwentDelay64
{
    var delay : SBetaGwentDelay64;
    delay.lowWord = value;
    if (value < 0) delay.highWord = -1;
    return delay;
}
function BetaGwentDelay64Positive(value : SBetaGwentDelay64) : bool
{ return value.highWord > 0 || (value.highWord == 0 && value.lowWord != 0); }

class CBetaGwentManagerContext extends CBetaGwentActionContext
{
    private var mainController : bool;
    private var verbose : bool;
    private var dirty : bool;
    public function SetMain(value : bool) { mainController = value; }
    public function IsMain() : bool { return mainController; }
    public function SetVerbose(value : bool) { verbose = value; }
    public function IsVerbose() : bool { return verbose; }
    public function MarkDirty() { dirty = true; }
    public function IsDirty() : bool { return dirty; }
}

abstract class CBetaGwentManagedAction extends CBetaGwentApplicableAction
{
    private var networkId : int;
    private var delay : SBetaGwentDelay64;
    private var stateChanging : bool;
    public function SetNetworkId(value : int) { networkId = value; }
    public function GetNetworkId() : int { return networkId; }
    public function SetDelay(value : SBetaGwentDelay64) { delay = value; }
    public function GetDelay() : SBetaGwentDelay64 { return delay; }
    public function SetStateChanging(value : bool) { stateChanging = value; }
    public function IsStateChanging() : bool { return stateChanging; }
    // A concrete managed effect must override this. Missing handlers may not
    // inherit the direct-boundary no-op and silently consume an action.
    protected function ApplyImpl() : bool { return false; }
}

abstract class CBetaGwentManagedRequest extends CBetaGwentManagedAction
{
    public function CanProcess() : bool { return false; }
    public function GetPlayerId() : int { return 0; }
}

abstract class CBetaGwentActionServices extends IScriptable
{
    // Defaults fail closed: a missing implementation must not report success.
    // EmitBeforeDiagnostic models ExceptionHelper.Create+pop, not a thrown error.
    public function EmitBeforeDiagnostic(action : CBetaGwentManagedAction) {}
    public function LogOutOfOrder(previousId : int, currentId : int, action : CBetaGwentManagedAction) : bool { return false; }
    public function LogAction(valid : bool, action : CBetaGwentManagedAction) : bool { return false; }
    public function AddRequest(request : CBetaGwentManagedRequest) : bool { return false; }
    public function MarkDirty(context : CBetaGwentManagerContext) : bool { context.MarkDirty(); return true; }
    public function DeliverRequest(playerId : int, request : CBetaGwentManagedRequest) : bool { return false; }
    // handled=false models a service failure; sent=false is a normal TrySend
    // result that the original ignores before checking Delay.
    public function TrySend(action : CBetaGwentManagedAction, out sent : bool) : bool { sent = false; return false; }
    public function PushPause(delay : SBetaGwentDelay64) : bool { return false; }
    public function DestroyAction(action : CBetaGwentManagedAction) : bool { return false; }
}

enum EBetaGwentManagerFault
{
    BG_ManagerNoFault,
    BG_ManagerNotInitialized,
    BG_ManagerUnsupportedAction,
    BG_ManagerServiceFailed,
    BG_ManagerApplyFailed
}

class CBetaGwentActionManager extends CBetaGwentActionSink
{
    private var context : CBetaGwentManagerContext;
    private var services : CBetaGwentActionServices;
    private var initialized : bool;
    private var lastKnownNetworkId : int;
    private var fault : EBetaGwentManagerFault;
    private var dispatches : int;
    public function Initialize(ownerContext : CBetaGwentManagerContext, ownerServices : CBetaGwentActionServices) : bool
    {
        if (initialized || !ownerContext || !ownerServices) return false;
        context = ownerContext; services = ownerServices; initialized = true; return true;
    }
    public function GetLastKnownNetworkId() : int { return lastKnownNetworkId; }
    public function IsInitialized() : bool { return initialized; }
    public function SetLastKnownNetworkId(value : int) { lastKnownNetworkId = value; }
    public function GetFault() : EBetaGwentManagerFault { return fault; }
    public function IsFaulted() : bool { return fault != BG_ManagerNoFault; }
    public function GetDispatchCount() : int { return dispatches; }
    private function Fail(value : EBetaGwentManagerFault) : bool { fault = value; return false; }
    public function DispatchAction(action : CBetaGwentQueuedAction)
    {
        var managed : CBetaGwentManagedAction;
        if (IsFaulted()) return;
        managed = (CBetaGwentManagedAction)action;
        if (!managed) { Fail(BG_ManagerUnsupportedAction); return; }
        ApplyAction(managed);
    }
    public function ApplyAction(action : CBetaGwentManagedAction) : bool
    {
        var request : CBetaGwentManagedRequest;
        var valid, deliver, sent : bool;
        var delay : SBetaGwentDelay64;
        if (IsFaulted()) return false;
        if (!initialized) return Fail(BG_ManagerNotInitialized);
        if (!action) return Fail(BG_ManagerUnsupportedAction);
        dispatches += 1;
        if (action.GetFireTriggers() && !action.HasFiredBefore()) services.EmitBeforeDiagnostic(action);
        if (action.GetNetworkId() > 0 && !action.IsPriorityAction())
        {
            if (action.GetNetworkId() < lastKnownNetworkId)
                if (!services.LogOutOfOrder(lastKnownNetworkId, action.GetNetworkId(), action)) return Fail(BG_ManagerServiceFailed);
            lastKnownNetworkId = action.GetNetworkId();
        }
        valid = action.IsValid();
        if (valid)
        {
            if (context.IsVerbose())
                if (!services.LogAction(true, action)) return Fail(BG_ManagerServiceFailed);
            request = (CBetaGwentManagedRequest)action;
            deliver = request && request.CanProcess();
            if (deliver)
                if (!services.AddRequest(request)) return Fail(BG_ManagerServiceFailed);
            if (action.IsStateChanging())
                if (!services.MarkDirty(context)) return Fail(BG_ManagerServiceFailed);
            // Deliberately re-read CanProcess. The registration callback can
            // change it, while 'deliver' retains the first read's result.
            if (!request || request.CanProcess())
                if (!action.Apply()) return Fail(BG_ManagerApplyFailed);
            if (deliver)
                if (!services.DeliverRequest(request.GetPlayerId(), request)) return Fail(BG_ManagerServiceFailed);
            if (context.IsMain())
            {
                if (!services.TrySend(action, sent)) return Fail(BG_ManagerServiceFailed);
                delay = action.GetDelay();
                if (BetaGwentDelay64Positive(delay))
                    if (!services.PushPause(action.GetDelay())) return Fail(BG_ManagerServiceFailed);
            }
        }
        else if (context.IsVerbose())
            if (!services.LogAction(false, action)) return Fail(BG_ManagerServiceFailed);
        if (!valid || !request)
            if (!services.DestroyAction(action)) return Fail(BG_ManagerServiceFailed);
        return true;
    }
}

// Bounded queue driver only. Ability/death/ExecutionStack interleaving is not
// implemented here. Stop before another queue removal once the sink faults.
class CBetaGwentActionDriver extends IScriptable
{
    private var context : CBetaGwentManagerContext;
    private var manager : CBetaGwentActionManager;
    private var queue : CBetaGwentActionQueue;
    public function Initialize(ownerContext : CBetaGwentManagerContext, ownerManager : CBetaGwentActionManager, localQueue : bool) : bool
    {
        if (queue || !ownerContext || !ownerManager || !ownerManager.IsInitialized() || ownerManager.IsFaulted()) return false;
        context = ownerContext; manager = ownerManager;
        queue = new CBetaGwentActionQueue in this;
        queue.Initialize(context.HasAuthority(), localQueue, manager);
        queue.BindAuthority(context); return true;
    }
    public function Push(action : CBetaGwentManagedAction, front : bool) : bool
    { if (!queue || manager.IsFaulted()) return false; return queue.Push(action, front); }
    public function Step() : bool
    { if (!queue || manager.IsFaulted()) return false; return queue.Step(); }
    public function PendingCount() : int { if (!queue) return 0; return queue.Count(); }
    public function RunBudget(maxSteps : int) : int
    {
        var steps : int;
        if (maxSteps <= 0 || maxSteps > 256) return 0;
        while (steps < maxSteps && Step()) steps += 1;
        return steps;
    }
}
