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
