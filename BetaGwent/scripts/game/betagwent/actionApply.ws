// Direct AAction.Apply boundary only. No ActionManager policy or card effect.
// See beta-apply-fixtures.json (14 exact copied IL observations).
class CBetaGwentActionContext extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var authority : bool;
    public function SetAuthority(value : bool) { authority = value; }
    public function HasAuthority() : bool { return authority; }
}

abstract class CBetaGwentApplicableAction extends CBetaGwentQueuedAction
{
    public var prepared : bool;
    public var context : CBetaGwentActionContext;

    // Local setup boundary: marks the state field that the oracle sets directly.
    // This does not port original Init, action allocator or registry binding.
    public function Prepare(ownerContext : CBetaGwentActionContext) : bool
    {
        if (prepared) return false;
        context = ownerContext; prepared = true; return true;
    }
    public function SetContext(value : CBetaGwentActionContext) { context = value; }
    public function GetContext() : CBetaGwentActionContext { return context; }
    public function Apply() : bool
    {
        if (!prepared) return false;
        if (!ApplyImpl()) return false;
        // Read context/authority/fire after the effect callback. A cached flag
        // would lose callback mutations in the original control flow.
        if (!context) return false;
        if (context.HasAuthority() && GetFireTriggers()) return AfterApplyImpl();
        return true;
    }
    protected function ApplyImpl() : bool { return true; }
    protected function AfterApplyImpl() : bool { return true; }
}
