// Raw SetPowerAndArmor seam: observes arguments, does not run clamp/events.
// Original40 numeric observations; CLR callback throws become false here.
function BetaGwentPowerFields(baseValue : int, permanent : int, current : int, armor : int) : SBetaGwentPower
{
    var value : SBetaGwentPower;
    value.basePower = baseValue; value.permanentPower = permanent;
    value.currentPower = current; value.armor = armor;
    return value;
}
function BetaGwentPowerFieldsEqual(a : SBetaGwentPower, b : SBetaGwentPower) : bool
{
    return a.basePower == b.basePower && a.permanentPower == b.permanentPower
        && a.currentPower == b.currentPower && a.armor == b.armor;
}
class CBetaGwentPowerNumberCheckFixture extends CBetaGwentPowerNumbers
{
    private var calls : int;
    private var rawPower, rawArmor : int;
    private var fieldsAtEntry : SBetaGwentPower;
    private var failSink, mutate : bool;
    private var mutation : SBetaGwentPower;
    public function Configure(fail : bool, rewrite : bool, value : SBetaGwentPower)
    { failSink = fail; mutate = rewrite; mutation = value; }
    public function CallCount() : int { return calls; }
    public function LastCallEquals(power : int, armor : int, fields : SBetaGwentPower) : bool
    { return calls > 0 && rawPower == power && rawArmor == armor && BetaGwentPowerFieldsEqual(fieldsAtEntry, fields); }
    protected function SetPowerAndArmor(power : int, armor : int) : bool
    {
        calls += 1; rawPower = power; rawArmor = armor; fieldsAtEntry = Snapshot();
        if (mutate)
        {
            WriteBasePower(mutation.basePower); WritePermanentPower(mutation.permanentPower);
            WriteCurrentPower(mutation.currentPower); WriteCurrentArmor(mutation.armor);
        }
        return !failSink;
    }
}
class CBetaGwentMissingPowerNumberHandler extends CBetaGwentPowerNumbers {}

class CBetaGwentPowerSetBaseCheckAction extends CBetaGwentManagedAction
{
    private var power : CBetaGwentPowerNumbers;
    private var applies : int;
    public function Bind(value : CBetaGwentPowerNumbers) { power = value; }
    public function ApplyCount() : int { return applies; }
    protected function ApplyImpl() : bool
    { applies += 1; if (!power) return false; return power.SetBasePower(2); }
}
class CBetaGwentPowerCheckActionServices extends CBetaGwentActionServices
{
    private var destroyed : int;
    public function DestroyedCount() : int { return destroyed; }
    public function DestroyAction(action : CBetaGwentManagedAction) : bool { destroyed += 1; return true; }
}

class CBetaGwentPowerNumberCheckRunner extends IScriptable
{
    private var checks, failures : int;
    private function Check(label : string, passed : bool)
    {
        checks += 1;
        if (passed) LogChannel('BetaGwent', "POWER_CHECK_PASS " + label);
        else { failures += 1; LogChannel('BetaGwent', "POWER_CHECK_FAIL " + label); }
    }
    public function Failures() : int { return failures; }
    private function RunGuards()
    {
        var fixture : CBetaGwentPowerNumberCheckFixture;
        var missing : CBetaGwentMissingPowerNumberHandler;
        var fields, changed : SBetaGwentPower;
        var result : int;
        var passed : bool;
        fields = BetaGwentPowerFields(8, -3, 4, 2);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        Check("guard/uninitialized-operations", !fixture.SetPower(1) && !fixture.SetArmor(1)
            && !fixture.SetBasePower(1) && !fixture.SetPermanentPower(1)
            && !fixture.SetBasePowerAndArmor(1, 1) && !fixture.SetPermanentPowerAndArmor(1, 1)
            && !fixture.RestorePower(1) && !fixture.AddArmor(1) && !fixture.MultiplyArmor(100)
            && fixture.CallCount() == 0 && !fixture.IsInitialized());
        fixture.InitFromFields(fields);
        Check("guard/initialize-once", !fixture.InitFromFields(BetaGwentPowerFields(99, 0, 99, 0))
            && BetaGwentPowerFieldsEqual(fixture.Snapshot(), fields));
        changed = fixture.Snapshot(); changed.currentPower = 999;
        Check("guard/snapshot-copy", BetaGwentPowerFieldsEqual(fixture.Snapshot(), fields));
        missing = new CBetaGwentMissingPowerNumberHandler in this; missing.InitFromFields(fields);
        Check("guard/missing-current-handler", !missing.SetPower(1) && BetaGwentPowerFieldsEqual(missing.Snapshot(), fields));
        Check("guard/missing-armor-handler", !missing.AddArmor(1) && BetaGwentPowerFieldsEqual(missing.Snapshot(), fields));
        Check("guard/missing-base-handler-keeps-mutation", !missing.SetBasePower(2)
            && BetaGwentPowerFieldsEqual(missing.Snapshot(), BetaGwentPowerFields(2, -2, 4, 2)));
        Check("guard/no-op-restore-needs-no-handler", missing.RestorePower(9)
            && BetaGwentPowerFieldsEqual(missing.Snapshot(), BetaGwentPowerFields(2, -2, 4, 2)));
        result = 91;
        Check("guard/positive-multiply-overflow", !fixture.MultiplyValue(2147483647, 100, result) && result == 91);
        result = 91;
        Check("guard/negative-multiply-overflow", !fixture.MultiplyValue((-2147483647 - 1), 200, result) && result == 91);
        Check("guard/multiply-largest-in-range", fixture.MultiplyValue(2147483520, 100, result) && result == 2147483520);
        Check("guard/multiply-min-value", fixture.MultiplyValue((-2147483647 - 1), 100, result) && result == (-2147483647 - 1));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        Check("guard/math-before-initialization", fixture.MultiplyValue(2147483647, 0, result) && result == 0
            && fixture.CallCount() == 0 && !fixture.IsInitialized());
    }
    private function RunManagedCase(mode : int)
    {
        var fixture : CBetaGwentPowerNumberCheckFixture;
        var missing : CBetaGwentMissingPowerNumberHandler;
        var power : CBetaGwentPowerNumbers;
        var context : CBetaGwentManagerContext;
        var services : CBetaGwentPowerCheckActionServices;
        var manager : CBetaGwentActionManager;
        var driver : CBetaGwentActionDriver;
        var action, following : CBetaGwentPowerSetBaseCheckAction;
        var fields : SBetaGwentPower;
        var steps : int;
        var passed : bool;
        fields = BetaGwentPowerFields(8, -3, 4, 2);
        if (mode == 2)
        { missing = new CBetaGwentMissingPowerNumberHandler in this; missing.InitFromFields(fields); power = missing; }
        else
        { fixture = new CBetaGwentPowerNumberCheckFixture in this; fixture.InitFromFields(fields);
          fixture.Configure(mode == 1, false, fields); power = fixture; }
        context = new CBetaGwentManagerContext in this; context.SetAuthority(true);
        services = new CBetaGwentPowerCheckActionServices in this;
        manager = new CBetaGwentActionManager in this; manager.Initialize(context, services);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, false);
        action = new CBetaGwentPowerSetBaseCheckAction in this; action.Prepare(context); action.Bind(power);
        action.SetFireTriggers(false); action.SetStateChanging(true); driver.Push(action, false);
        following = new CBetaGwentPowerSetBaseCheckAction in this; following.Prepare(context); following.Bind(power);
        following.SetFireTriggers(false);
        if (mode != 0) driver.Push(following, false);
        steps = driver.RunBudget(8);
        passed = steps == 1 && action.ApplyCount() == 1 && following.ApplyCount() == 0
            && context.IsDirty() && BetaGwentPowerFieldsEqual(power.Snapshot(), BetaGwentPowerFields(2, -2, 4, 2));
        if (mode == 0)
            Check("integration/managed-numeric-success", passed && !manager.IsFaulted()
                && driver.PendingCount() == 0 && services.DestroyedCount() == 1 && fixture.CallCount() == 1);
        else if (mode == 1)
            Check("integration/failed-numeric-preserves-following", passed && manager.GetFault() == BG_ManagerApplyFailed
                && driver.PendingCount() == 1 && services.DestroyedCount() == 0 && fixture.CallCount() == 1);
        else
            Check("integration/missing-numeric-handler-fails", passed && manager.GetFault() == BG_ManagerApplyFailed
                && driver.PendingCount() == 1 && services.DestroyedCount() == 0);
    }
    private function RunIntegration() { RunManagedCase(0); RunManagedCase(1); RunManagedCase(2); }

    private function RunOriginal0()
    {
        var fixture : CBetaGwentPowerNumberCheckFixture;
        var passed : bool;
        var result : int;
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetPower(11);
        Check("current/raw-positive", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(11, 2, BetaGwentPowerFields(8, -3, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetPower(-3);
        Check("current/raw-negative", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-3, 2, BetaGwentPowerFields(8, -3, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetArmor(-5);
        Check("armor/raw-negative", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, -5, BetaGwentPowerFields(8, -3, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetBasePower(12);
        Check("base/increase", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(12, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(8, 2, BetaGwentPowerFields(12, -3, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetBasePower(2);
        Check("base/reduce-clamps-permanent", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(2, -2, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-2, 2, BetaGwentPowerFields(2, -2, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetBasePower(-4);
        Check("base/negative-requested-delta", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(0, 0, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-8, 2, BetaGwentPowerFields(0, 0, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetBasePowerAndArmor(2, 19);
        Check("base/explicit-armor", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(2, -2, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-2, 19, BetaGwentPowerFields(2, -2, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetBasePower(8);
        Check("base/unchanged-still-calls-setter", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, 2, BetaGwentPowerFields(8, -3, 4, 2)));
    }
    private function RunOriginal1()
    {
        var fixture : CBetaGwentPowerNumberCheckFixture;
        var passed : bool;
        var result : int;
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(2147483647, 0, 5, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(2147483647, 0, 5, 2));
        passed = fixture.SetBasePower((-2147483647 - 1));
        Check("base/subtraction-wrap", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(0, 0, 5, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(6, 2, BetaGwentPowerFields(0, 0, 5, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(1, 0, 2147483647, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(1, 0, 2147483647, 2));
        passed = fixture.SetBasePower(2);
        Check("base/current-addition-wrap", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(2, 0, 2147483647, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals((-2147483647 - 1), 2, BetaGwentPowerFields(2, 0, 2147483647, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetPermanentPower(7);
        Check("permanent/increase", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, 7, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(14, 2, BetaGwentPowerFields(8, 7, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetPermanentPower(-20);
        Check("permanent/negative-requested-delta", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -8, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-13, 2, BetaGwentPowerFields(8, -8, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetPermanentPowerAndArmor(-20, -7);
        Check("permanent/explicit-armor", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -8, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-13, -7, BetaGwentPowerFields(8, -8, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetPermanentPower(-3);
        Check("permanent/unchanged-still-calls-setter", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, 2, BetaGwentPowerFields(8, -3, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, 2147483647, 7, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, 2147483647, 7, 2));
        passed = fixture.SetPermanentPower((-2147483647 - 1));
        Check("permanent/subtraction-wrap", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -8, 7, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(8, 2, BetaGwentPowerFields(8, -8, 7, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 2, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 2, 2));
        passed = fixture.RestorePower(2);
        Check("restore/partial", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 2, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, 2, BetaGwentPowerFields(8, -3, 2, 2)));
    }
    private function RunOriginal2()
    {
        var fixture : CBetaGwentPowerNumberCheckFixture;
        var passed : bool;
        var result : int;
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 2, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 2, 2));
        passed = fixture.RestorePower(99);
        Check("restore/caps-to-base-plus-permanent", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 2, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(5, 2, BetaGwentPowerFields(8, -3, 2, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 2, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 2, 2));
        passed = fixture.RestorePower(-3);
        Check("restore/negative-lowers-power", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 2, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-1, 2, BetaGwentPowerFields(8, -3, 2, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 2, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 2, 2));
        passed = fixture.RestorePower(0);
        Check("restore/zero-still-calls-setter", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 2, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(2, 2, BetaGwentPowerFields(8, -3, 2, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 5, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 5, 2));
        passed = fixture.RestorePower(2);
        Check("restore/equal-no-setter", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 5, 2)) && fixture.CallCount() == 0);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 9, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 9, 2));
        passed = fixture.RestorePower(2);
        Check("restore/boosted-no-setter", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 9, 2)) && fixture.CallCount() == 0);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(2147483647, 1, 0, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(2147483647, 1, 0, 2));
        passed = fixture.RestorePower(10);
        Check("restore/maximum-addition-wrap", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(2147483647, 1, 0, 2)) && fixture.CallCount() == 0);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(2147483647, 0, (-2147483647 - 1), 2));
        fixture.Configure(false, false, BetaGwentPowerFields(2147483647, 0, (-2147483647 - 1), 2));
        passed = fixture.RestorePower(10);
        Check("restore/difference-and-current-wrap", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(2147483647, 0, (-2147483647 - 1), 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(2147483647, 2, BetaGwentPowerFields(2147483647, 0, (-2147483647 - 1), 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.AddArmor(3);
        Check("armor/add-positive", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, 5, BetaGwentPowerFields(8, -3, 4, 2)));
    }
    private function RunOriginal3()
    {
        var fixture : CBetaGwentPowerNumberCheckFixture;
        var passed : bool;
        var result : int;
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.AddArmor(-9);
        Check("armor/add-negative", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, -7, BetaGwentPowerFields(8, -3, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2147483647));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2147483647));
        passed = fixture.AddArmor(1);
        Check("armor/add-wrap", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2147483647)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, (-2147483647 - 1), BetaGwentPowerFields(8, -3, 4, 2147483647)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 7));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 7));
        passed = fixture.MultiplyArmor(150);
        Check("armor/multiply-floor", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 7)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, 10, BetaGwentPowerFields(8, -3, 4, 7)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 7));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 7));
        passed = fixture.MultiplyArmor(-50);
        Check("armor/multiply-negative", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 7)) && fixture.CallCount() == 1 && fixture.LastCallEquals(4, -4, BetaGwentPowerFields(8, -3, 4, 7)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(3, 50, result);
        Check("multiply/positive-floor", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == 1);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(-3, 50, result);
        Check("multiply/negative-floor", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == -2);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(1, -50, result);
        Check("multiply/negative-percent", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == -1);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(-3, -50, result);
        Check("multiply/two-negatives", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == 1);
    }
    private function RunOriginal4()
    {
        var fixture : CBetaGwentPowerNumberCheckFixture;
        var passed : bool;
        var result : int;
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(3, 33, result);
        Check("multiply/fraction-below-one", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == 0);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(17, 100, result);
        Check("multiply/identity", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == 17);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(2147483647, 0, result);
        Check("multiply/zero-percent", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == 0);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue(16777217, 100, result);
        Check("multiply/float-integer-rounding", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == 16777216);
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.MultiplyValue((-2147483647 - 1), 100, result);
        Check("multiply/min-value-in-range", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -3, 4, 2)) && fixture.CallCount() == 0 && result == (-2147483647 - 1));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(true, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetBasePower(2);
        Check("boundary/throw-keeps-base-mutation", !passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(2, -2, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-2, 2, BetaGwentPowerFields(2, -2, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(true, false, BetaGwentPowerFields(8, -3, 4, 2));
        passed = fixture.SetPermanentPower(-20);
        Check("boundary/throw-keeps-permanent-mutation", !passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(8, -8, 4, 2)) && fixture.CallCount() == 1 && fixture.LastCallEquals(-13, 2, BetaGwentPowerFields(8, -8, 4, 2)));
        fixture = new CBetaGwentPowerNumberCheckFixture in this;
        fixture.InitFromFields(BetaGwentPowerFields(8, -3, 4, 2));
        fixture.Configure(false, true, BetaGwentPowerFields(1, -1, 100, 9));
        passed = fixture.SetPower(10);
        Check("boundary/callback-may-rewrite-fields", passed && BetaGwentPowerFieldsEqual(fixture.Snapshot(), BetaGwentPowerFields(1, -1, 100, 9)) && fixture.CallCount() == 1 && fixture.LastCallEquals(10, 2, BetaGwentPowerFields(8, -3, 4, 2)));
    }
    public function Run()
    {
        checks = 0; failures = 0;
        LogChannel('BetaGwent', "POWER_CHECK_BEGIN schema=1 fixture=power55 key=59af251c490c2f86");
        RunOriginal0();
        RunOriginal1();
        RunOriginal2();
        RunOriginal3();
        RunOriginal4();
        RunGuards(); RunIntegration();
        LogChannel('BetaGwent', "POWER_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);
    }
}

exec function bgpower_check()
{
    var runner : CBetaGwentPowerNumberCheckRunner;
    if (!thePlayer) { LogChannel('BetaGwent', "POWER_CHECK_SKIPPED no player"); return; }
    LogChannel('BetaGwent', "POWER_SUITE_BEGIN schema=1 key=59af251c490c2f86 manager=319abdd4f2a6cc31");
    BetaGwentRunManagerChecks();
    runner = new CBetaGwentPowerNumberCheckRunner in thePlayer;
    runner.Run();
    LogChannel('BetaGwent', "POWER_SUITE_END schema=1");
    theGame.GetGuiManager().ShowNotification("Сила/броня: " + (55 - runner.Failures()) + "/55, ошибок: " + runner.Failures(), 8.0);
}
