// Queue boundary port, source: beta-resolution-il.txt and beta-action-fixtures.json.
// Concrete validity and full ActionManager.ApplyAction policy belong to a sink.
// No controller scheduler, death drain, requests/network or effect handlers here.
class CBetaGwentQueuedAction extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var fireTriggers : bool;
    public var beforeFired : bool;
    public var priorityAction : bool;
    default fireTriggers = true;

    public function SetFireTriggers(value : bool) { fireTriggers = value; }
    public function GetFireTriggers() : bool { return fireTriggers; }
    public function SetPriorityAction(value : bool) { priorityAction = value; }
    public function IsPriorityAction() : bool { return priorityAction; }
    public function HasFiredBefore() : bool
    {
        // Original getter treats FireTriggers=false as already fired without
        // changing the stored flag. Enabling triggers can expose an unfired flag.
        return !fireTriggers || beforeFired;
    }
    public function IsValid() : bool { return true; }
    public function BeforeApply()
    {
        if (HasFiredBefore() || !IsValid()) return;
        beforeFired = true; // Must precede callback, including reentrant calls.
        BeforeApplyImpl();
    }
    protected function BeforeApplyImpl() {}
}

abstract class CBetaGwentActionSink extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    // Dispatch is not AAction.Apply: validity, initialization, event delivery,
    // cache destruction and effects remain the consumer's responsibility.
    public function DispatchAction(action : CBetaGwentQueuedAction) {}
}

class CBetaGwentActionQueue extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var actions : array<CBetaGwentQueuedAction>;
    public var sink : CBetaGwentActionSink;
    public var initialized : bool;
    public var authority : bool;
    public var authorityContext : CBetaGwentActionContext;
    public var abilityLocal : bool;

    public function Initialize(hasAuthority : bool, localQueue : bool, consumer : CBetaGwentActionSink) : bool
    {
        if (initialized || !consumer) return false;
        initialized = true; authority = hasAuthority; abilityLocal = localQueue; sink = consumer;
        return true;
    }
    public function Count() : int { return actions.Size(); }
    public function BindAuthority(value : CBetaGwentActionContext) : bool
    { if (!initialized || !value) return false; authorityContext = value; return true; }
    private function HasAuthority() : bool
    { if (authorityContext) return authorityContext.HasAuthority(); return authority; }
    public function At(index : int) : CBetaGwentQueuedAction
    {
        if (index < 0 || index >= actions.Size()) return NULL;
        return actions[index];
    }
    public function Push(action : CBetaGwentQueuedAction, front : bool) : bool
    {
        var i : int;
        if (!initialized || !action) return false;
        // The authority/priority restriction is global PushActionImpl only;
        // an AbilityInstance's own front insertion has no such restriction.
        if (!abilityLocal && front && !HasAuthority() && !action.IsPriorityAction()) return false;
        actions.PushBack(action);
        if (front)
        {
            for (i = actions.Size() - 1; i > 0; i -= 1) actions[i] = actions[i - 1];
            actions[0] = action;
        }
        return true;
    }
    private function RemoveObject(action : CBetaGwentQueuedAction)
    {
        var i : int;
        for (i = 0; i < actions.Size(); i += 1)
            if (actions[i] == action) { actions.Erase(i); return; }
    }
    public function Step() : bool
    {
        var action : CBetaGwentQueuedAction;
        var sendBefore : bool;
        if (!initialized || actions.Size() == 0) return false;
        action = actions[0];
        // Preserve evaluation order as well as the two-phase decision. The
        // local original validates before checking authority; global does not.
        if (abilityLocal) sendBefore = !action.HasFiredBefore() && action.IsValid() && HasAuthority();
        else sendBefore = HasAuthority() && !action.HasFiredBefore() && action.IsValid();
        if (sendBefore) action.BeforeApply();
        else
        {
            if (abilityLocal) actions.Erase(0);
            else RemoveObject(action);
            sink.DispatchAction(action);
        }
        return true;
    }
}
