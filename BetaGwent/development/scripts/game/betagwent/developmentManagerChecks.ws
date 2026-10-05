// Synthetic callbacks. Generated scenarios bind to original56 observations.
struct SBetaGwentManagerCheckConfig
{
    var request, stateChanging, priority, valid, fire, before, main, verbose : bool;
    var networkId : int;
    var networkValues : array<int>;
    var delay : SBetaGwentDelay64;
    var delayValues : array<SBetaGwentDelay64>;
    var processValues : array<bool>;
    var addClearsProcess : bool;
    var effectMutation : int; //1 mainfalse,2 player1,3 valid/processfalse
    var receiveSetsMain, sendChangesDelay, sendResult : bool;
    var failAt : int; //1 effect,2 receive,3 send,4 pause,5 add,6 destroy,7 errorlog,8 debuglog,9 dirty
    var validationLosesAuthority : bool;
}
function BetaGwentManagerCheckDefaults() : SBetaGwentManagerCheckConfig
{
    var value : SBetaGwentManagerCheckConfig;
    value.valid = true; value.fire = true; value.before = true; value.sendResult = true;
    return value;
}
class CBetaGwentManagerCheckFixture extends IScriptable
{
    private var config : SBetaGwentManagerCheckConfig;
    private var context : CBetaGwentManagerContext;
    private var manager : CBetaGwentActionManager;
    private var expectedAction : CBetaGwentManagedAction;
    private var trace : string;
    private var beforeReads, networkReads, delayReads, processReads, lastSeen, pauseCount, playerId : int;
    private var processCleared : bool;
    private var lastPause : SBetaGwentDelay64;
    public function Initialize(value : SBetaGwentManagerCheckConfig, owner : CBetaGwentManagerContext, consumer : CBetaGwentActionManager)
    { config = value; context = owner; manager = consumer; playerId = 2; }
    public function Bind(action : CBetaGwentManagedAction) { expectedAction = action; }
    public function Matches(action : CBetaGwentManagedAction) : bool { return action == expectedAction; }
    public function Text() : string { return trace; }
    public function Append(value : string) { trace += value + "|"; }
    public function BeforeReads() : int { return beforeReads; }
    public function NetworkReads() : int { return networkReads; }
    public function DelayReads() : int { return delayReads; }
    public function LastSeen() : int { return lastSeen; }
    public function PauseCount() : int { return pauseCount; }
    public function LastPause() : SBetaGwentDelay64 { return lastPause; }
    public function StateChanging() : bool { return config.stateChanging; }
    public function Priority() : bool { return config.priority; }
    public function Fire() : bool { return config.fire; }
    public function ReadBefore(fire : bool) : bool { beforeReads += 1; return !fire || config.before; }
    public function ReadNetwork() : int
    {
        var index : int;
        index = networkReads; networkReads += 1;
        if (config.networkValues.Size() == 0) return config.networkId;
        if (index >= config.networkValues.Size()) index = config.networkValues.Size() - 1;
        return config.networkValues[index];
    }
    public function ReadDelay() : SBetaGwentDelay64
    {
        var index : int;
        index = delayReads; delayReads += 1;
        if (config.delayValues.Size() == 0) return config.delay;
        if (index >= config.delayValues.Size()) index = config.delayValues.Size() - 1;
        return config.delayValues[index];
    }
    public function Validate() : bool
    {
        Append("valid"); lastSeen = manager.GetLastKnownNetworkId();
        if (config.validationLosesAuthority) context.SetAuthority(false);
        return config.valid;
    }
    public function ReadProcess() : bool
    {
        var index : int;
        var value : bool;
        index = processReads; processReads += 1;
        if (processCleared) value = false;
        else if (config.processValues.Size() == 0) value = true;
        else
        {
            if (index >= config.processValues.Size()) index = config.processValues.Size() - 1;
            value = config.processValues[index];
        }
        if (value) Append("can:True"); else Append("can:False");
        return value;
    }
    public function PlayerId() : int { return playerId; }
    public function Before() { config.before = true; Append("before"); }
    public function Effect() : bool
    {
        Append("apply");
        if (config.effectMutation == 1) context.SetMain(false);
        if (config.effectMutation == 2) playerId = 1;
        if (config.effectMutation == 3) { config.valid = false; processCleared = true; }
        return config.failAt != 1;
    }
    public function Add() : bool
    { Append("add"); if (config.addClearsProcess) processCleared = true; return config.failAt != 5; }
    public function Dirty(owner : CBetaGwentManagerContext) : bool
    { owner.MarkDirty(); Append("dirty"); return config.failAt != 9; }
    public function Deliver(playerId : int) : bool
    {
        Append("player:" + playerId); Append("received");
        if (config.receiveSetsMain) { context.SetMain(true); config.delay = BetaGwentDelay64FromInt(7); }
        return config.failAt != 2;
    }
    public function Send(out sent : bool) : bool
    {
        Append("send"); sent = config.sendResult;
        if (config.sendChangesDelay) config.delay = BetaGwentDelay64FromInt(3);
        return config.failAt != 3;
    }
    public function Pause(value : SBetaGwentDelay64) : bool
    {
        lastPause = value; pauseCount += 1;
        if ((value.highWord == 0 && value.lowWord >= 0) || (value.highWord == -1 && value.lowWord < 0)) Append("pause:" + value.lowWord);
        else Append("pause64:" + value.highWord + ":" + value.lowWord);
        return config.failAt != 4;
    }
    public function Destroy() : bool { Append("destroy"); return config.failAt != 6; }
    public function ErrorLog() : bool { Append("log-error"); return config.failAt != 7; }
    public function DebugLog() : bool { Append("log-debug"); return config.failAt != 8; }
}
class CBetaGwentManagerCheckAction extends CBetaGwentManagedAction
{
    private var fixture : CBetaGwentManagerCheckFixture;
    public function Setup(value : CBetaGwentManagerCheckFixture, owner : CBetaGwentManagerContext)
    { fixture = value; Prepare(owner); SetFireTriggers(fixture.Fire()); SetPriorityAction(fixture.Priority()); SetStateChanging(fixture.StateChanging()); }
    public function HasFiredBefore() : bool { return fixture.ReadBefore(GetFireTriggers()); }
    public function GetNetworkId() : int { return fixture.ReadNetwork(); }
    public function GetDelay() : SBetaGwentDelay64 { return fixture.ReadDelay(); }
    public function IsValid() : bool { return fixture.Validate(); }
    protected function BeforeApplyImpl() { fixture.Before(); }
    protected function ApplyImpl() : bool { return fixture.Effect(); }
}
class CBetaGwentManagerCheckRequest extends CBetaGwentManagedRequest
{
    private var fixture : CBetaGwentManagerCheckFixture;
    public function Setup(value : CBetaGwentManagerCheckFixture, owner : CBetaGwentManagerContext)
    { fixture = value; Prepare(owner); SetFireTriggers(fixture.Fire()); SetPriorityAction(fixture.Priority()); SetStateChanging(fixture.StateChanging()); }
    public function HasFiredBefore() : bool { return fixture.ReadBefore(GetFireTriggers()); }
    public function GetNetworkId() : int { return fixture.ReadNetwork(); }
    public function GetDelay() : SBetaGwentDelay64 { return fixture.ReadDelay(); }
    public function IsValid() : bool { return fixture.Validate(); }
    public function CanProcess() : bool { return fixture.ReadProcess(); }
    public function GetPlayerId() : int { return fixture.PlayerId(); }
    protected function BeforeApplyImpl() { fixture.Before(); }
    protected function ApplyImpl() : bool { return fixture.Effect(); }
}
class CBetaGwentManagerCheckServices extends CBetaGwentActionServices
{
    private var fixture : CBetaGwentManagerCheckFixture;
    public function Bind(value : CBetaGwentManagerCheckFixture) { fixture = value; }
    public function EmitBeforeDiagnostic(action : CBetaGwentManagedAction) { fixture.Append("diagnostic"); }
    public function LogOutOfOrder(previousId : int, currentId : int, action : CBetaGwentManagedAction) : bool { return fixture.Matches(action) && fixture.ErrorLog(); }
    public function LogAction(valid : bool, action : CBetaGwentManagedAction) : bool { return fixture.Matches(action) && fixture.DebugLog(); }
    public function AddRequest(request : CBetaGwentManagedRequest) : bool { return fixture.Matches(request) && fixture.Add(); }
    public function MarkDirty(context : CBetaGwentManagerContext) : bool { return fixture.Dirty(context); }
    public function DeliverRequest(playerId : int, request : CBetaGwentManagedRequest) : bool { return fixture.Matches(request) && fixture.Deliver(playerId); }
    public function TrySend(action : CBetaGwentManagedAction, out sent : bool) : bool
    { if (!fixture.Matches(action)) { sent = false; return false; } return fixture.Send(sent); }
    public function PushPause(delay : SBetaGwentDelay64) : bool { return fixture.Pause(delay); }
    public function DestroyAction(action : CBetaGwentManagedAction) : bool { return fixture.Matches(action) && fixture.Destroy(); }
}
class CBetaGwentManagerChecks extends IScriptable
{
    private var checks, failures : int;
    private var context : CBetaGwentManagerContext;
    private var manager : CBetaGwentActionManager;
    private var fixture : CBetaGwentManagerCheckFixture;
    private var services : CBetaGwentManagerCheckServices;
    private var action : CBetaGwentManagedAction;
    private function Check(label : string, passed : bool)
    {
        checks += 1;
        if (passed) LogChannel('BetaGwent', "MANAGER_CHECK_PASS " + label);
        else { failures += 1; LogChannel('BetaGwent', "MANAGER_CHECK_FAIL " + label); }
    }
    private function Setup(config : SBetaGwentManagerCheckConfig)
    {
        var normal : CBetaGwentManagerCheckAction;
        var request : CBetaGwentManagerCheckRequest;
        context = new CBetaGwentManagerContext in this;
        context.SetAuthority(true); context.SetMain(config.main); context.SetVerbose(config.verbose);
        manager = new CBetaGwentActionManager in this;
        fixture = new CBetaGwentManagerCheckFixture in this;
        fixture.Initialize(config, context, manager);
        services = new CBetaGwentManagerCheckServices in this; services.Bind(fixture);
        manager.Initialize(context, services); manager.SetLastKnownNetworkId(10);
        if (config.request) { request = new CBetaGwentManagerCheckRequest in this; request.Setup(fixture, context); action = request; }
        else { normal = new CBetaGwentManagerCheckAction in this; normal.Setup(fixture, context); action = normal; }
        fixture.Bind(action);
    }
    public function GetDisplaySummary() : string
    { return "Обработчик: " + (checks - failures) + "/" + checks + ", ошибок: " + failures; }

    private function RunOriginal0()
    {
        var config : SBetaGwentManagerCheckConfig;
        var delay : SBetaGwentDelay64;
        var passed : bool;
        config = BetaGwentManagerCheckDefaults();
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("normal/valid-apply-destroy", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("normal/invalid-destroy-without-effect", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.before = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("before/unfired-diagnostic-is-not-throw", passed && !manager.IsFaulted() && fixture.Text() == "diagnostic|valid|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.fire = false;
        config.before = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("before/no-fire-skips-diagnostic", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.fire = false;
        config.before = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("before/no-fire-short-circuits-getter", passed && !manager.IsFaulted() && fixture.BeforeReads() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.networkId = -1;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/invalid-id--1", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0 && manager.GetLastKnownNetworkId() == 10 && fixture.LastSeen() == 10);
        config = BetaGwentManagerCheckDefaults();
        config.networkId = 0;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/invalid-id-0", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0 && manager.GetLastKnownNetworkId() == 10 && fixture.LastSeen() == 10);
        config = BetaGwentManagerCheckDefaults();
        config.networkId = 5;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/invalid-id-5", passed && !manager.IsFaulted() && fixture.Text() == "log-error|valid|destroy|" && fixture.PauseCount() == 0 && manager.GetLastKnownNetworkId() == 5 && fixture.LastSeen() == 5);
    }
    private function RunOriginal1()
    {
        var config : SBetaGwentManagerCheckConfig;
        var delay : SBetaGwentDelay64;
        var passed : bool;
        config = BetaGwentManagerCheckDefaults();
        config.networkId = 10;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/invalid-id-10", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0 && manager.GetLastKnownNetworkId() == 10 && fixture.LastSeen() == 10);
        config = BetaGwentManagerCheckDefaults();
        config.networkId = 12;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/invalid-id-12", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0 && manager.GetLastKnownNetworkId() == 12 && fixture.LastSeen() == 12);
        config = BetaGwentManagerCheckDefaults();
        config.priority = true;
        config.networkId = 5;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/priority-skips-last-update", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.priority = true;
        config.networkId = 5;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/priority-last-preserved", passed && !manager.IsFaulted() && manager.GetLastKnownNetworkId() == 10);
        config = BetaGwentManagerCheckDefaults();
        config.stateChanging = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("state/dirty-precedes-effect", passed && !manager.IsFaulted() && fixture.Text() == "valid|dirty|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.stateChanging = true;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("state/invalid-not-dirty", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.stateChanging = true;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("state/invalid-dirty-flag-false", passed && !manager.IsFaulted() && !context.IsDirty());
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/process-register-apply-deliver-retain", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:True|apply|player:2|received|" && fixture.PauseCount() == 0);
    }
    private function RunOriginal2()
    {
        var config : SBetaGwentManagerCheckConfig;
        var delay : SBetaGwentDelay64;
        var passed : bool;
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.stateChanging = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/state-dirty-between-register-and-apply", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:True|add|dirty|can:True|apply|player:2|received|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.processValues.PushBack(false);
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/not-processable-still-retained", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:False|can:False|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.stateChanging = true;
        config.processValues.PushBack(false);
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/not-processable-still-dirty", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:False|dirty|can:False|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.processValues.PushBack(true);
        config.processValues.PushBack(false);
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/can-true-to-false-delivers-without-apply", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:False|player:2|received|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.processValues.PushBack(false);
        config.processValues.PushBack(true);
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/can-false-to-true-applies-without-register-or-delivery", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:False|can:True|apply|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.addClearsProcess = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/register-callback-changes-second-read", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:False|player:2|received|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/invalid-destroyed", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.stateChanging = true;
        config.failAt = 1;
        config.main = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("effect/throw-skips-send-and-destroy", !passed && manager.IsFaulted() && fixture.Text() == "valid|dirty|apply|" && fixture.PauseCount() == 0);
    }
    private function RunOriginal3()
    {
        var config : SBetaGwentManagerCheckConfig;
        var delay : SBetaGwentDelay64;
        var passed : bool;
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.failAt = 1;
        config.main = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/effect-throw-leaves-register-and-skips-delivery", !passed && manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:True|apply|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.failAt = 2;
        config.main = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/delivery-throw-skips-send", !passed && manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:True|apply|player:2|received|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = -1;
        config.delay.lowWord = -1;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("main/send-pause-delay--1", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = -1;
        config.delay.lowWord = -1;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("main/delay-read-count--1", passed && !manager.IsFaulted() && fixture.DelayReads() == 1);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 0;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("main/send-pause-delay-0", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 0;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("main/delay-read-count-0", passed && !manager.IsFaulted() && fixture.DelayReads() == 1);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("main/send-pause-delay-25", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause:25|destroy|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == 25);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("main/delay-read-count-25", passed && !manager.IsFaulted() && fixture.DelayReads() == 2);
    }
    private function RunOriginal4()
    {
        var config : SBetaGwentManagerCheckConfig;
        var delay : SBetaGwentDelay64;
        var passed : bool;
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        config.sendResult = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("main/send-false-still-pauses", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause:25|destroy|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == 25);
        config = BetaGwentManagerCheckDefaults();
        config.main = false;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("non-main/skips-send-pause", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = false;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("non-main/delay-not-read", passed && !manager.IsFaulted() && fixture.DelayReads() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        config.failAt = 3;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("main/send-throw-skips-pause-destroy", !passed && manager.IsFaulted() && fixture.Text() == "valid|apply|send|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        config.failAt = 4;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("main/pause-throw-skips-destroy", !passed && manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause:25|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == 25);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.effectMutation = 1;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("callback/main-read-after-effect", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.receiveSetsMain = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("callback/main-read-after-delivery", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:True|apply|player:2|received|send|pause:7|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == 7);
        config = BetaGwentManagerCheckDefaults();
        config.valid = false;
        config.verbose = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("verbose/valid-False", passed && !manager.IsFaulted() && fixture.Text() == "valid|log-debug|destroy|" && fixture.PauseCount() == 0);
    }
    private function RunOriginal5()
    {
        var config : SBetaGwentManagerCheckConfig;
        var delay : SBetaGwentDelay64;
        var passed : bool;
        config = BetaGwentManagerCheckDefaults();
        config.valid = true;
        config.verbose = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("verbose/valid-True", passed && !manager.IsFaulted() && fixture.Text() == "valid|log-debug|apply|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.networkValues.PushBack(5);
        config.networkValues.PushBack(5);
        config.networkValues.PushBack(5);
        config.networkValues.PushBack(12);
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/getter-repeated-through-error-and-write", passed && !manager.IsFaulted() && fixture.Text() == "log-error|valid|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.networkValues.PushBack(5);
        config.networkValues.PushBack(5);
        config.networkValues.PushBack(5);
        config.networkValues.PushBack(12);
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("network/last-uses-final-read", passed && !manager.IsFaulted() && manager.GetLastKnownNetworkId() == 12 && fixture.LastSeen() == 12 && fixture.NetworkReads() == 4);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        delay.highWord = 0;
        delay.lowWord = 25;
        config.delayValues.PushBack(delay);
        delay.highWord = -1;
        delay.lowWord = -7;
        config.delayValues.PushBack(delay);
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("delay/positive-test-then-repeated-argument-read", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause:-7|destroy|" && fixture.PauseCount() == 1 && delay.highWord == -1 && delay.lowWord == -7);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.effectMutation = 2;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/recipient-read-after-effect", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:True|apply|player:1|received|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        config.sendChangesDelay = true;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("delay/read-after-send-callback", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause:3|destroy|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == 3);
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.effectMutation = 3;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("request/effect-mutation-does-not-recheck-validity-or-delivery-snapshot", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:True|add|can:True|apply|player:2|received|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        config.valid = false;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("main/invalid-skips-send-and-pause", passed && !manager.IsFaulted() && fixture.Text() == "valid|destroy|" && fixture.PauseCount() == 0);
    }
    private function RunOriginal6()
    {
        var config : SBetaGwentManagerCheckConfig;
        var delay : SBetaGwentDelay64;
        var passed : bool;
        config = BetaGwentManagerCheckDefaults();
        config.request = true;
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = 25;
        config.processValues.PushBack(false);
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("main/unprocessable-valid-request-still-sends-and-pauses", passed && !manager.IsFaulted() && fixture.Text() == "valid|can:False|can:False|send|pause:25|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == 25);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = (-2147483647 - 1);
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("delay64/value-2147483648", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause64:0:-2147483648|destroy|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == (-2147483647 - 1));
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 0;
        config.delay.lowWord = -1;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("delay64/value-4294967295", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause64:0:-1|destroy|" && fixture.PauseCount() == 1 && delay.highWord == 0 && delay.lowWord == -1);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 1;
        config.delay.lowWord = 0;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("delay64/value-4294967296", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause64:1:0|destroy|" && fixture.PauseCount() == 1 && delay.highWord == 1 && delay.lowWord == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = 2147483647;
        config.delay.lowWord = -1;
        Setup(config);
        passed = manager.ApplyAction(action);
        delay = fixture.LastPause();
        Check("delay64/value-9223372036854775807", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|pause64:2147483647:-1|destroy|" && fixture.PauseCount() == 1 && delay.highWord == 2147483647 && delay.lowWord == -1);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = (-2147483647 - 1);
        config.delay.lowWord = 0;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("delay64/value--9223372036854775808", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = -1;
        config.delay.lowWord = 0;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("delay64/value--4294967296", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|destroy|" && fixture.PauseCount() == 0);
        config = BetaGwentManagerCheckDefaults();
        config.main = true;
        config.delay.highWord = -1;
        config.delay.lowWord = 2147483647;
        Setup(config);
        passed = manager.ApplyAction(action);
        Check("delay64/value--2147483649", passed && !manager.IsFaulted() && fixture.Text() == "valid|apply|send|destroy|" && fixture.PauseCount() == 0);
    }
    public function Run()
    {
        checks = 0; failures = 0;
        LogChannel('BetaGwent', "MANAGER_CHECK_BEGIN schema=1 fixture=manager86 key=319abdd4f2a6cc31");
        RunOriginal0();
        RunOriginal1();
        RunOriginal2();
        RunOriginal3();
        RunOriginal4();
        RunOriginal5();
        RunOriginal6();
        RunExtra();
        LogChannel('BetaGwent', "MANAGER_CHECK_DONE checks=" + checks + " passed=" + (checks - failures) + " failed=" + failures);
    }
    private function SetupIntegration(config : SBetaGwentManagerCheckConfig)
    {
        var realBefore : CBetaGwentManagerIntegrationAction;
        Setup(config);
        realBefore = new CBetaGwentManagerIntegrationAction in this;
        realBefore.Setup(fixture, context); action = realBefore; fixture.Bind(action);
    }
    private function RunExtra()
    {
        var config : SBetaGwentManagerCheckConfig;
        var driver : CBetaGwentActionDriver;
        var next : CBetaGwentManagerIntegrationAction;
        var emptyManager : CBetaGwentActionManager;
        var bareAction : CBetaGwentQueuedAction;
        var missingServices : CBetaGwentMissingActionServices;
        var missingEffect : CBetaGwentMissingEffectAction;
        var value : SBetaGwentDelay64;
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        emptyManager = new CBetaGwentActionManager in this;
        Check("guard/not-initialized", !emptyManager.ApplyAction(action) && emptyManager.GetFault() == BG_ManagerNotInitialized);
        emptyManager = new CBetaGwentActionManager in this;
        Check("guard/null-context-services", !emptyManager.Initialize(NULL, services) && !emptyManager.Initialize(context, NULL));
        Check("guard/initialize-once", emptyManager.Initialize(context, services) && !emptyManager.Initialize(context, services));
        Check("guard/null-action", !emptyManager.ApplyAction(NULL) && emptyManager.GetFault() == BG_ManagerUnsupportedAction);
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        bareAction = new CBetaGwentQueuedAction in this; manager.DispatchAction(bareAction);
        Check("guard/unsupported-queued-action", manager.GetFault() == BG_ManagerUnsupportedAction && manager.GetDispatchCount() == 0);
        config = BetaGwentManagerCheckDefaults(); config.failAt = 1; Setup(config); manager.ApplyAction(action);
        Check("guard/fault-latches-without-second-effect", !manager.ApplyAction(action) && manager.GetDispatchCount() == 1 && fixture.Text() == "valid|apply|");
        config = BetaGwentManagerCheckDefaults(); config.request = true; config.failAt = 5; Setup(config);
        Check("guard/add-failure-stops-before-effect", !manager.ApplyAction(action) && fixture.Text() == "valid|can:True|add|");
        config = BetaGwentManagerCheckDefaults(); config.failAt = 6; Setup(config);
        Check("guard/destroy-failure-keeps-effect", !manager.ApplyAction(action) && fixture.Text() == "valid|apply|destroy|");
        config = BetaGwentManagerCheckDefaults(); config.networkId = 5; config.failAt = 7; Setup(config);
        Check("guard/errorlog-failure-stops-network-write", !manager.ApplyAction(action) && manager.GetLastKnownNetworkId() == 10 && fixture.Text() == "log-error|");
        config = BetaGwentManagerCheckDefaults(); config.verbose = true; config.failAt = 8; Setup(config);
        Check("guard/debuglog-failure-skips-effect", !manager.ApplyAction(action) && fixture.Text() == "valid|log-debug|");
        config = BetaGwentManagerCheckDefaults(); config.stateChanging = true; config.failAt = 9; Setup(config);
        Check("guard/dirty-failure-keeps-dirty-before-effect", !manager.ApplyAction(action) && context.IsDirty() && fixture.Text() == "valid|dirty|");
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        missingServices = new CBetaGwentMissingActionServices in this;
        emptyManager = new CBetaGwentActionManager in this; emptyManager.Initialize(context, missingServices);
        Check("guard/default-services-fail-closed", !emptyManager.ApplyAction(action) && emptyManager.GetFault() == BG_ManagerServiceFailed);
        config = BetaGwentManagerCheckDefaults(); Setup(config);
        missingEffect = new CBetaGwentMissingEffectAction in this; missingEffect.Prepare(context); missingEffect.SetFireTriggers(false);
        fixture.Bind(missingEffect);
        Check("guard/missing-effect-fails-closed", !manager.ApplyAction(missingEffect) && manager.GetFault() == BG_ManagerApplyFailed && fixture.Text() == "");

        value.highWord = 0; value.lowWord = 0;
        Check("guard/delay64-zero", !BetaGwentDelay64Positive(value));
        value.highWord = 0; value.lowWord = -2147483647 - 1;
        Check("guard/delay64-positive-unsigned-low-word", BetaGwentDelay64Positive(value));
        value.highWord = 1; value.lowWord = 0;
        Check("guard/delay64-positive-high-word", BetaGwentDelay64Positive(value));
        value.highWord = -1; value.lowWord = 0;
        Check("guard/delay64-negative-high-word", !BetaGwentDelay64Positive(value));

        config = BetaGwentManagerCheckDefaults(); config.before = false; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this;
        Check("integration/uninitialized-driver", !driver.Step() && !driver.Push(action, false) && driver.RunBudget(1) == 0);
        emptyManager = new CBetaGwentActionManager in this;
        Check("integration/null-or-uninitialized-manager", !driver.Initialize(NULL, manager, false) && !driver.Initialize(context, emptyManager, false));
        Check("integration/driver-initialize-once", driver.Initialize(context, manager, false) && !driver.Initialize(context, manager, false));
        driver.Push(action, false);
        Check("integration/budget-guards-preserve-queue", driver.RunBudget(0) == 0 && driver.RunBudget(257) == 0 && driver.PendingCount() == 1);
        Check("integration/before-only-first-budget", driver.RunBudget(1) == 1 && driver.PendingCount() == 1 && manager.GetDispatchCount() == 0 && fixture.Text() == "valid|valid|before|");
        Check("integration/apply-second-budget", driver.RunBudget(1) == 1 && driver.PendingCount() == 0 && manager.GetDispatchCount() == 1 && fixture.Text() == "valid|valid|before|valid|apply|destroy|");
        Check("integration/drained-queue-no-op", driver.RunBudget(1) == 0 && !manager.IsFaulted());

        config = BetaGwentManagerCheckDefaults(); config.before = false; config.validationLosesAuthority = true; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, false); driver.Push(action, false); driver.Step();
        Check("integration/global-authority-read-before-validation", driver.PendingCount() == 1 && manager.GetDispatchCount() == 0 && !context.HasAuthority() && fixture.Text() == "valid|valid|before|");
        config = BetaGwentManagerCheckDefaults(); config.before = false; config.validationLosesAuthority = true; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, true); driver.Push(action, false); driver.Step();
        Check("integration/local-authority-read-after-validation", driver.PendingCount() == 0 && manager.GetDispatchCount() == 1 && !context.HasAuthority() && fixture.Text() == "valid|diagnostic|valid|apply|destroy|");
        config = BetaGwentManagerCheckDefaults(); config.before = false; SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, false); context.SetAuthority(false);
        Check("integration/front-gate-reads-current-authority", !driver.Push(action, true) && driver.Push(action, false));
        config = BetaGwentManagerCheckDefaults(); SetupIntegration(config);
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, true); context.SetAuthority(false);
        Check("integration/local-front-has-no-authority-gate", driver.Push(action, true));

        config = BetaGwentManagerCheckDefaults(); config.failAt = 1; SetupIntegration(config);
        // Integration action starts unfired; queue sends Before first.
        driver = new CBetaGwentActionDriver in this; driver.Initialize(context, manager, false); driver.Push(action, false);
        next = new CBetaGwentManagerIntegrationAction in this; next.Setup(fixture, context); driver.Push(next, false);
        driver.RunBudget(2);
        Check("integration/fault-preserves-following-action", manager.IsFaulted() && driver.PendingCount() == 1 && manager.GetDispatchCount() == 1);
        Check("integration/fault-blocks-step-push-and-budget", !driver.Step() && !driver.Push(next, false) && driver.RunBudget(256) == 0 && driver.PendingCount() == 1);
    }
}
// Uses the real inherited HasFiredBefore/BeforeApply guard, without fixture override.
class CBetaGwentManagerIntegrationAction extends CBetaGwentManagedAction
{
    private var fixture : CBetaGwentManagerCheckFixture;
    public function Setup(value : CBetaGwentManagerCheckFixture, owner : CBetaGwentManagerContext)
    { fixture = value; Prepare(owner); SetFireTriggers(value.Fire()); }
    public function IsValid() : bool { return fixture.Validate(); }
    protected function BeforeApplyImpl() { fixture.Before(); }
    protected function ApplyImpl() : bool { return fixture.Effect(); }
}
class CBetaGwentMissingActionServices extends CBetaGwentActionServices {}
class CBetaGwentMissingEffectAction extends CBetaGwentManagedAction {}

function BetaGwentRunManagerChecks()
{
    var runner : CBetaGwentManagerChecks;
    var queueChecks : CBetaGwentActionQueueChecks;
    var applyChecks : CBetaGwentApplyChecks;
    if (!thePlayer) { LogChannel('BetaGwent', "MANAGER_CHECK_SKIPPED no player"); return; }
    LogChannel('BetaGwent', "MANAGER_SUITE_BEGIN schema=1 key=319abdd4f2a6cc31");
    queueChecks = new CBetaGwentActionQueueChecks in thePlayer; queueChecks.Run();
    applyChecks = new CBetaGwentApplyChecks in thePlayer; applyChecks.Run();
    runner = new CBetaGwentManagerChecks in thePlayer; runner.Run();
    LogChannel('BetaGwent', "MANAGER_SUITE_END schema=1");
    theGame.GetGuiManager().ShowNotification(runner.GetDisplaySummary(), 8.0);
}

exec function bgmanager_check() { BetaGwentRunManagerChecks(); }
