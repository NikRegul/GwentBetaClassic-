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
