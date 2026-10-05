// Isolated queue fixtures. Most expectations come from exact copied original
// IL; empty local invocation uses a guarded false instead of a CLR exception.
class CBetaGwentActionCheckTrace extends CBetaGwentActionSink
{
    private var trace : string;
    private var count : int;
    public function Record(value : string) { trace += value + "|"; count += 1; }
    public function Text() : string { return trace; }
    public function Count() : int { return count; }
    public function DispatchAction(action : CBetaGwentQueuedAction)
    {
        var fixture : CBetaGwentActionCheckItem;
        fixture = (CBetaGwentActionCheckItem)action;
        Record("dispatch:" + fixture.Label());
    }
}

class CBetaGwentActionCheckItem extends CBetaGwentQueuedAction
{
    private var label : string;
    private var trace : CBetaGwentActionCheckTrace;
    private var validity : bool;
    private var validityCalls : int;
    private var beforeCalls : int;
    private var queue : CBetaGwentActionQueue;
    private var nested : CBetaGwentQueuedAction;
    private var insertOnValidation : bool;
    private var reentrant : bool;
    private var denySecond : bool;
    public function Initialize(value : string, output : CBetaGwentActionCheckTrace, valid : bool, fire : bool)
    { label = value; trace = output; validity = valid; SetFireTriggers(fire); }
    public function Label() : string { return label; }
    public function ValidityCalls() : int { return validityCalls; }
    public function BeforeCalls() : int { return beforeCalls; }
    public function InsertBefore(targetQueue : CBetaGwentActionQueue, action : CBetaGwentQueuedAction, onValidation : bool)
    { queue = targetQueue; nested = action; insertOnValidation = onValidation; }
    public function Reenter() { reentrant = true; }
    public function DenySecondValidation() { denySecond = true; }
    public function IsValid() : bool
    {
        validityCalls += 1;
        if (insertOnValidation) queue.Push(nested, true);
        if (denySecond) return validityCalls == 1;
        return validity;
    }
    protected function BeforeApplyImpl()
    {
        beforeCalls += 1; trace.Record("before:" + label);
        if (nested && !insertOnValidation) queue.Push(nested, true);
        if (reentrant) BeforeApply();
    }
}

class CBetaGwentActionQueueChecks extends IScriptable
{
    private var checks : int;
    private var failures : int;
    private function Check(id : string, passed : bool)
    {
        checks += 1;
        if (passed) LogChannel('BetaGwent', "ACTION_CHECK_PASS " + id);
        else { failures += 1; LogChannel('BetaGwent', "ACTION_CHECK_FAIL " + id); }
    }
    private function Item(label : string, trace : CBetaGwentActionCheckTrace, valid : bool, fire : bool) : CBetaGwentActionCheckItem
    {
        var action : CBetaGwentActionCheckItem;
        action = new CBetaGwentActionCheckItem in this; action.Initialize(label, trace, valid, fire);
        return action;
    }
    private function Queue(trace : CBetaGwentActionCheckTrace, authority : bool, localQueue : bool) : CBetaGwentActionQueue
    {
        var queue : CBetaGwentActionQueue;
        queue = new CBetaGwentActionQueue in this; queue.Initialize(authority, localQueue, trace); return queue;
    }
    public function Run()
    {
        var trace : CBetaGwentActionCheckTrace;
        var queue : CBetaGwentActionQueue;
        var a : CBetaGwentActionCheckItem;
        var b : CBetaGwentActionCheckItem;
        var c : CBetaGwentActionCheckItem;
        checks = 0; failures = 0;
        LogChannel('BetaGwent', "ACTION_CHECK_BEGIN schema=1 fixture=queue39");
        LogChannel('BetaGwent', "ACTION_CHECK_BEGIN schema=1 fixture=queue39");
        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("a", trace, true, true); queue.Push(a, false); queue.Step();
        Check("global/before-keeps-action", queue.Count() == 1 && queue.At(0) == a && trace.Text() == "before:a|");
        queue.Step();
        Check("global/apply-next-step", queue.Count() == 0 && trace.Text() == "before:a|dispatch:a|");
        queue.Step(); Check("global/empty-no-op", trace.Count() == 2);

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("a", trace, true, true); b = Item("b", trace, true, true);
        queue.Push(a, false); a.InsertBefore(queue, b, false); queue.Step();
        Check("global/nested-front-order", queue.Count() == 2 && queue.At(0) == b && queue.At(1) == a);
        queue.Step(); queue.Step(); queue.Step();
        Check("global/nested-front-trace", trace.Text() == "before:a|before:b|dispatch:b|dispatch:a|");
        Check("global/nested-before-once", queue.Count() == 0 && a.BeforeCalls() == 1 && b.BeforeCalls() == 1);

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("a", trace, true, true); a.Reenter(); queue.Push(a, false); queue.Step();
        Check("before/reentrant-once", a.BeforeCalls() == 1);
        Check("before/flag-set-before-callback", a.HasFiredBefore());
        a.BeforeApply(); Check("before/repeated-no-op", a.BeforeCalls() == 1);

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("invalid", trace, false, true); queue.Push(a, false); queue.Step();
        Check("global/invalid-dispatched-without-before", trace.Text() == "dispatch:invalid|");
        Check("global/invalid-removed", queue.Count() == 0);
        Check("before/invalid-unfired", !a.HasFiredBefore());

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("a", trace, true, false); queue.Push(a, false);
        Check("before/no-fire-reports-fired", a.HasFiredBefore());
        queue.Step(); Check("global/no-fire-single-step", trace.Text() == "dispatch:a|");
        Check("global/no-fire-skips-step-validity", a.ValidityCalls() == 0);
        a.SetFireTriggers(true); Check("before/enabling-restores-unfired", !a.HasFiredBefore());

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, false, false);
        a = Item("a", trace, true, true); queue.Push(a, false); queue.Step();
        Check("global/non-authority-dispatch", trace.Text() == "dispatch:a|");
        Check("global/non-authority-skips-validity", a.ValidityCalls() == 0);

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("a", trace, true, true); b = Item("b", trace, true, true); c = Item("c", trace, true, true);
        queue.Push(a, false); queue.Push(b, false);
        Check("push/append-order", queue.Count() == 2 && queue.At(0) == a && queue.At(1) == b);
        queue.Push(c, true); Check("push/front-order", queue.Count() == 3 && queue.At(0) == c && queue.At(1) == a && queue.At(2) == b);

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, false, false);
        a = Item("a", trace, true, true); b = Item("p", trace, true, true); b.SetPriorityAction(true);
        Check("push/non-authority-front-guarded", !queue.Push(a, true) && queue.Count() == 0);
        queue.Push(b, true); Check("push/priority-front-permitted", queue.Count() == 1 && queue.At(0) == b);
        queue.Push(a, false); Check("push/non-authority-append-permitted", queue.Count() == 2 && queue.At(1) == a);

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("a", trace, false, true); b = Item("b", trace, true, true);
        queue.Push(a, false); a.InsertBefore(queue, b, true); queue.Step();
        Check("global/remove-captured-object-after-validity-front-insert", queue.Count() == 1 && queue.At(0) == b && trace.Text() == "dispatch:a|");

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, true);
        a = Item("a", trace, true, true); b = Item("b", trace, true, true);
        queue.Push(a, false); a.InsertBefore(queue, b, false); queue.Step();
        Check("local/before-front-order", queue.Count() == 2 && queue.At(0) == b && queue.At(1) == a);
        queue.Step(); queue.Step(); queue.Step();
        Check("local/nested-front-trace", trace.Text() == "before:a|before:b|dispatch:b|dispatch:a|");
        Check("local/queue-drained", queue.Count() == 0);
        Check("local/empty-call-guarded", !queue.Step());

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, true);
        a = Item("a", trace, false, true); b = Item("b", trace, true, true);
        queue.Push(a, false); a.InsertBefore(queue, b, true); queue.Step();
        Check("local/remove-index-zero-after-validity-front-insert", queue.Count() == 1 && queue.At(0) == a && trace.Text() == "dispatch:a|");

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, false, true);
        a = Item("a", trace, true, true); queue.Push(a, false); queue.Step();
        Check("local/non-authority-dispatch", trace.Text() == "dispatch:a|");
        Check("local/non-authority-still-validates", a.ValidityCalls() == 1);

        trace = new CBetaGwentActionCheckTrace in this; queue = Queue(trace, true, false);
        a = Item("a", trace, true, true); a.DenySecondValidation(); queue.Push(a, false); queue.Step();
        Check("before/second-validation-can-deny", a.ValidityCalls() == 2 && !a.HasFiredBefore() && queue.Count() == 1 && trace.Count() == 0);
        queue.Step(); Check("global/denied-before-next-invalid-dispatch", trace.Text() == "dispatch:a|");

        // Explicit local guards/differences, not original parity observations.
        queue = new CBetaGwentActionQueue in this;
        Check("guard/uninitialized-step", !queue.Step());
        Check("guard/uninitialized-push", !queue.Push(a, false));
        Check("guard/null-consumer", !queue.Initialize(true, false, NULL));
        Check("guard/initialize-once", queue.Initialize(true, false, trace) && !queue.Initialize(false, true, trace));
        Check("guard/null-action", !queue.Push(NULL, false));
        Check("guard/invalid-index", !queue.At(-1) && !queue.At(0));
        LogChannel('BetaGwent', "ACTION_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);
    }
    public function GetDisplaySummary() : string
    { return "Очередь: " + (checks - failures) + "/" + checks + ", ошибок: " + failures; }
}

exec function bgactions_check()
{
    var runner : CBetaGwentActionQueueChecks;
    if (!thePlayer)
    { LogChannel('BetaGwent', "ACTION_CHECK_SKIPPED no player"); return; }
    runner = new CBetaGwentActionQueueChecks in thePlayer;
    runner.Run();
    theGame.GetGuiManager().ShowNotification(runner.GetDisplaySummary(), 8.0);
}
