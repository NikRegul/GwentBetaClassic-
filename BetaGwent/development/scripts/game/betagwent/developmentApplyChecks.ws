class CBetaGwentApplyCheckAction extends CBetaGwentApplicableAction
{
    private var trace : string;
    private var effectOK : bool;
    private var afterOK : bool;
    private var flipFire : bool;
    private var flipAuthority : bool;
    private var clearContext : bool;
    private var replacement : CBetaGwentActionContext;
    default effectOK = true;
    default afterOK = true;
    public function Text() : string { return trace; }
    public function FailEffect() { effectOK = false; }
    public function FailAfter() { afterOK = false; }
    public function FlipFire() { flipFire = true; }
    public function FlipAuthority() { flipAuthority = true; }
    public function ClearContextInEffect() { clearContext = true; }
    public function ReplaceContextInEffect(value : CBetaGwentActionContext) { replacement = value; }
    protected function ApplyImpl() : bool
    {
        trace += "apply|";
        if (flipFire) SetFireTriggers(!GetFireTriggers());
        if (flipAuthority) GetContext().SetAuthority(!GetContext().HasAuthority());
        if (replacement) SetContext(replacement);
        if (clearContext) SetContext(NULL);
        return effectOK;
    }
    protected function AfterApplyImpl() : bool
    { trace += "after|"; return afterOK; }
}

class CBetaGwentApplyChecks extends IScriptable
{
    private var checks : int;
    private var failures : int;
    private function Check(label : string, passed : bool)
    {
        checks += 1;
        if (passed) LogChannel('BetaGwent', "APPLY_CHECK_PASS " + label);
        else { failures += 1; LogChannel('BetaGwent', "APPLY_CHECK_FAIL " + label); }
    }
    private function Context(authority : bool) : CBetaGwentActionContext
    {
        var value : CBetaGwentActionContext;
        value = new CBetaGwentActionContext in this; value.SetAuthority(authority); return value;
    }
    private function Item(authority : bool, fire : bool) : CBetaGwentApplyCheckAction
    {
        var value : CBetaGwentApplyCheckAction;
        value = new CBetaGwentApplyCheckAction in this;
        value.Prepare(Context(authority)); value.SetFireTriggers(fire); return value;
    }
    public function Run()
    {
        var a : CBetaGwentApplyCheckAction;
        var other : CBetaGwentActionContext;
        checks = 0; failures = 0;
        LogChannel('BetaGwent', "APPLY_CHECK_BEGIN schema=1 fixture=apply20");
        a = new CBetaGwentApplyCheckAction in this;
        Check("uninitialized/throws-before-effect", !a.Apply() && a.Text() == "");
        a = Item(false, false);
        Check("apply/authority-False-fire-False", a.Apply() && a.Text() == "apply|");
        a = Item(false, true);
        Check("apply/authority-False-fire-True", a.Apply() && a.Text() == "apply|");
        a = Item(true, false);
        Check("apply/authority-True-fire-False", a.Apply() && a.Text() == "apply|");
        a = Item(true, true);
        Check("apply/authority-True-fire-True", a.Apply() && a.Text() == "apply|after|");
        a = Item(true, false); a.FlipFire();
        Check("callback/fire-False-to-True", a.Apply() && a.Text() == "apply|after|");
        a = Item(true, true); a.FlipFire();
        Check("callback/fire-True-to-False", a.Apply() && a.Text() == "apply|");
        a = Item(false, true); a.FlipAuthority();
        Check("callback/authority-False-to-True", a.Apply() && a.Text() == "apply|after|");
        a = Item(true, true); a.FlipAuthority();
        Check("callback/authority-True-to-False", a.Apply() && a.Text() == "apply|");
        a = Item(true, true); a.FailEffect();
        Check("effect/throw-skips-after", !a.Apply() && a.Text() == "apply|");
        a = Item(true, true); a.FailAfter();
        Check("after/throw-does-not-undo-effect", !a.Apply() && a.Text() == "apply|after|");
        a = Item(true, false); a.SetContext(NULL);
        Check("controller/null-fire-False", !a.Apply() && a.Text() == "apply|");
        a = Item(true, true); a.SetContext(NULL);
        Check("controller/null-fire-True", !a.Apply() && a.Text() == "apply|");
        a = new CBetaGwentApplyCheckAction in this;
        Check("uninitialized/precedes-null-controller", !a.Apply() && a.Text() == "");

        // Native-only guards/integration observations, not copied IL claims.
        a = Item(true, true);
        Check("guard/prepare-once", !a.Prepare(Context(false)) && a.GetContext().HasAuthority());
        a = Item(true, true); a.ClearContextInEffect();
        Check("guard/clear-context-after-effect", !a.Apply() && a.Text() == "apply|");
        a = Item(false, true); other = Context(true); a.ReplaceContextInEffect(other);
        Check("guard/replacement-context-read-after-effect", a.Apply() && a.Text() == "apply|after|" && a.GetContext() == other);
        a = Item(true, true); a.FailEffect(); a.FlipFire();
        Check("guard/failed-effect-preserves-flag-mutation", !a.Apply() && !a.GetFireTriggers() && a.Text() == "apply|");
        a = Item(true, true); a.Apply();
        Check("guard/apply-is-not-one-shot", a.Apply() && a.Text() == "apply|after|apply|after|");
        a = new CBetaGwentApplyCheckAction in this; a.Prepare(NULL);
        Check("guard/null-prepare-effect-then-failure", !a.Apply() && a.Text() == "apply|");
        LogChannel('BetaGwent', "APPLY_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);
    }
    public function GetDisplaySummary() : string
    { return "Применение: " + (checks - failures) + "/" + checks + ", ошибок: " + failures; }
}

exec function bgapply_check()
{
    var runner : CBetaGwentApplyChecks;
    if (!thePlayer) { LogChannel('BetaGwent', "APPLY_CHECK_SKIPPED no player"); return; }
    runner = new CBetaGwentApplyChecks in thePlayer; runner.Run();
    theGame.GetGuiManager().ShowNotification(runner.GetDisplaySummary(), 8.0);
}
