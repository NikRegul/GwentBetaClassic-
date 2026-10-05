using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text.Json;

string root = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "docs/evidence/beta-manager-apply-extraction.json")));
string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
string dll = manifest.RootElement.GetProperty("extract").GetString()!;
if (Hash(dll) != manifest.RootElement.GetProperty("extractSha256").GetString()
    || Hash(manifest.RootElement.GetProperty("source").GetString()!) != manifest.RootElement.GetProperty("sourceSha256").GetString()
    || !manifest.RootElement.GetProperty("originalRuntimeReferencesAbsent").GetBoolean()
    || manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean()))
    throw new Exception("Manager extraction provenance failed");
foreach (var dependency in manifest.RootElement.GetProperty("metadataDependencies").EnumerateArray())
    if (Hash(dependency.GetProperty("path").GetString()!) != dependency.GetProperty("sha256").GetString())
        throw new Exception("Metadata dependency changed");
Assembly assembly = Assembly.LoadFrom(dll);
if (assembly.GetReferencedAssemblies().Any(a => a.Name == "Assembly-CSharp" || a.Name!.StartsWith("Unity"))) throw new Exception("Original runtime reference");
const BindingFlags Flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;
Type T(string name) => assembly.GetType(name.Contains('.') ? name : "GwentGameplay." + name, true)!;
object New(string name) => FormatterServices.GetUninitializedObject(T(name));
object? Call(object obj, string name, params object?[] values) => obj.GetType().GetMethod(name, Flags)!.Invoke(obj, values);
void Shim(object? obj, string owner, string name, Func<object[], object?> callback)
{
    var entry = manifest.RootElement.GetProperty("shims").EnumerateArray().Single(s => s.GetProperty("owner").GetString() == owner && s.GetProperty("name").GetString() == name);
    T(owner).GetField(entry.GetProperty("field").GetString()!, Flags)!.SetValue(obj, callback);
}
var observations = new List<object>(); var failures = new List<string>();
void Check(string id, object expected, object actual)
{
    bool passed = JsonSerializer.Serialize(expected) == JsonSerializer.Serialize(actual);
    observations.Add(new { id, expected, actual, passed }); if (!passed) failures.Add(id);
}
Fixture Context(string kind = "AAction")
{
    var f = new Fixture { Action = New(kind), Manager = New("ActionManager"), Controller = New("GameController") };
    object requestManager = New("RequestManager"), playerManager = New("PlayerManager"), player = New("Player"), timeManager = New("TimeManager"), logger = New("RedLogger.IRedLogger");
    // This writes the original copied base getter's field; no original Init is run.
    var getterField = T("AGameManager").GetFields(Flags).Single(field => field.FieldType == T("GameController"));
    getterField.SetValue(f.Manager, f.Controller);
    Call(f.Manager, "set_LastKnownNetworkID", 10);
    Shim(f.Action, "GwentGameplay.AAction", "get_FireTriggers", _ => f.Fire);
    Shim(f.Action, "GwentGameplay.AAction", "get_HasFiredBeforeApplyTrigger", _ => { f.BeforeReads++; return f.Before; });
    Shim(null, "GwentGameplay.ExceptionHelper", "Create", _ => { f.Trace.Add("diagnostic"); return new ArgumentException("fixture"); });
    Shim(f.Action, "GwentGameplay.AAction", "get_NetworkId", _ => { int index = f.NetworkReads++; return f.NetworkValues == null ? f.NetworkId : f.NetworkValues[Math.Min(index, f.NetworkValues.Length - 1)]; });
    Shim(f.Action, "GwentGameplay.AAction", "IsValid", _ => { f.Trace.Add("valid"); f.LastSeenAtValidation = (int)Call(f.Manager, "get_LastKnownNetworkID")!; return f.Valid; });
    Shim(f.Action, "GwentGameplay.AAction", "Apply", _ => { f.Trace.Add("apply"); f.ApplyCallback?.Invoke(f); return null; });
    Shim(f.Action, "GwentGameplay.AAction", "get_Delay", _ => { int index = f.DelayReads++; return f.DelayValues == null ? f.Delay : f.DelayValues[Math.Min(index, f.DelayValues.Length - 1)]; });
    Shim(f.Manager, "GwentGameplay.AGameManager", "get_Logger", _ => logger);
    Shim(f.Controller, "GwentGameplay.GameController", "get_LogVerbose", _ => f.Verbose);
    Shim(logger, "RedLogger.IRedLogger", "LogError", _ => { f.Trace.Add("log-error"); return null; });
    Shim(logger, "RedLogger.IRedLogger", "LogDebug", _ => { f.Trace.Add("log-debug"); return null; });
    Shim(f.Controller, "GwentGameplay.GameController", "get_RequestManager", _ => requestManager);
    Shim(requestManager, "GwentGameplay.RequestManager", "AddRequest", a => { if (!ReferenceEquals(a[0], f.Action)) throw new Exception("Wrong added action"); f.Trace.Add("add"); f.AddCallback?.Invoke(f); return null; });
    Shim(f.Controller, "GwentGameplay.GameController", "set_IsDirty", a => { f.Dirty = (bool)a[0]; f.Trace.Add("dirty"); return null; });
    Shim(f.Controller, "GwentGameplay.GameController", "get_PlayerManager", _ => playerManager);
    Shim(playerManager, "GwentGameplay.PlayerManager", "GetPlayer", a => { f.Trace.Add("player:" + Convert.ToInt32(a[0])); return player; });
    Shim(player, "GwentGameplay.Player", "OnRequestReceived", a => { if (!ReferenceEquals(a[0], f.Action)) throw new Exception("Wrong delivered action"); f.Trace.Add("received"); f.ReceiveCallback?.Invoke(f); return null; });
    Shim(f.Controller, "GwentGameplay.GameController", "get_IsMainController", _ => f.Main);
    Shim(f.Manager, "GwentGameplay.ActionManager", "TrySendAction", a => { if (!ReferenceEquals(a[0], f.Action)) throw new Exception("Wrong sent action"); f.Trace.Add("send"); f.SendCallback?.Invoke(f); return f.SendResult; });
    Shim(f.Controller, "GwentGameplay.GameController", "get_TimeManager", _ => timeManager);
    Shim(timeManager, "GwentGameplay.TimeManager", "PushPause", a => { f.Trace.Add("pause:" + a[0]); f.PauseCallback?.Invoke(f); return null; });
    Shim(f.Manager, "GwentGameplay.ActionManager", "DestroyAction", a => { if (!ReferenceEquals(a[0], f.Action)) throw new Exception("Wrong destroyed action"); f.Trace.Add("destroy"); return null; });
    if (T("ARequestAction").IsAssignableFrom(f.Action.GetType()))
    {
        Shim(f.Action, "GwentGameplay.ARequestAction", "get_CanProcess", _ => { int index = f.ProcessReads++; bool value = index < f.ProcessValues.Length ? f.ProcessValues[index] : f.ProcessValues[^1]; f.Trace.Add("can:" + value); return value; });
        Shim(f.Action, "GwentGameplay.ARequestAction", "get_PlayerId", _ => Enum.ToObject(T("EPlayerId"), f.PlayerId));
    }
    return f;
}
string? Run(Fixture f)
{
    try { Call(f.Manager, "ApplyAction", f.Action); return null; }
    catch (TargetInvocationException error) { return error.InnerException!.GetType().Name; }
}
void TraceCheck(string id, Fixture f, string[] expected, string? expectedError = null)
{
    string? error = Run(f);
    Check(id, new { error = expectedError, trace = expected }, new { error, trace = f.Trace.ToArray() });
}
TraceCheck("normal/valid-apply-destroy", Context(), new[] { "valid", "apply", "destroy" });
{
    var f = Context(); f.Valid = false;
    TraceCheck("normal/invalid-destroy-without-effect", f, new[] { "valid", "destroy" });
}
{
    var f = Context(); f.Before = false;
    TraceCheck("before/unfired-diagnostic-is-not-throw", f, new[] { "diagnostic", "valid", "apply", "destroy" });
}
{
    var f = Context(); f.Fire = false; f.Before = false;
    TraceCheck("before/no-fire-skips-diagnostic", f, new[] { "valid", "apply", "destroy" });
    Check("before/no-fire-short-circuits-getter", 0, f.BeforeReads);
}
foreach (int network in new[] { -1, 0, 5, 10, 12 })
{
    var f = Context(); f.NetworkId = network; f.Valid = false;
    string? error = Run(f);
    int expectedLast = network > 0 ? network : 10;
    Check("network/invalid-id-" + network, new { error = (string?)null, last = expectedLast, seen = expectedLast, trace = network > 0 && network < 10 ? new[] { "log-error", "valid", "destroy" } : new[] { "valid", "destroy" } },
        new { error, last = (int)Call(f.Manager, "get_LastKnownNetworkID")!, seen = f.LastSeenAtValidation, trace = f.Trace.ToArray() });
}
{
    var f = Context("OraclePriorityAction"); f.NetworkId = 5;
    TraceCheck("network/priority-skips-last-update", f, new[] { "valid", "apply", "destroy" });
    Check("network/priority-last-preserved", 10, (int)Call(f.Manager, "get_LastKnownNetworkID")!);
}
TraceCheck("state/dirty-precedes-effect", Context("OracleChangingAction"), new[] { "valid", "dirty", "apply", "destroy" });
{
    var f = Context("OracleChangingAction"); f.Valid = false;
    TraceCheck("state/invalid-not-dirty", f, new[] { "valid", "destroy" });
    Check("state/invalid-dirty-flag-false", false, f.Dirty);
}
TraceCheck("request/process-register-apply-deliver-retain", Context("ARequestAction"), new[] { "valid", "can:True", "add", "can:True", "apply", "player:2", "received" });
TraceCheck("request/state-dirty-between-register-and-apply", Context("OracleChangingRequest"), new[] { "valid", "can:True", "add", "dirty", "can:True", "apply", "player:2", "received" });
{
    var f = Context("ARequestAction"); f.ProcessValues = new[] { false };
    TraceCheck("request/not-processable-still-retained", f, new[] { "valid", "can:False", "can:False" });
}
{
    var f = Context("OracleChangingRequest"); f.ProcessValues = new[] { false };
    TraceCheck("request/not-processable-still-dirty", f, new[] { "valid", "can:False", "dirty", "can:False" });
}
{
    var f = Context("ARequestAction"); f.ProcessValues = new[] { true, false };
    TraceCheck("request/can-true-to-false-delivers-without-apply", f, new[] { "valid", "can:True", "add", "can:False", "player:2", "received" });
}
{
    var f = Context("ARequestAction"); f.ProcessValues = new[] { false, true };
    TraceCheck("request/can-false-to-true-applies-without-register-or-delivery", f, new[] { "valid", "can:False", "can:True", "apply" });
}
{
    var f = Context("ARequestAction"); f.AddCallback = x => x.ProcessValues = new[] { false };
    TraceCheck("request/register-callback-changes-second-read", f, new[] { "valid", "can:True", "add", "can:False", "player:2", "received" });
}
{
    var f = Context("ARequestAction"); f.Valid = false;
    TraceCheck("request/invalid-destroyed", f, new[] { "valid", "destroy" });
}
{
    var f = Context("OracleChangingAction"); f.ApplyCallback = _ => throw new InvalidOperationException("fixture"); f.Main = true;
    TraceCheck("effect/throw-skips-send-and-destroy", f, new[] { "valid", "dirty", "apply" }, "InvalidOperationException");
}
{
    var f = Context("ARequestAction"); f.Main = true; f.ApplyCallback = _ => throw new InvalidOperationException("fixture");
    TraceCheck("request/effect-throw-leaves-register-and-skips-delivery", f, new[] { "valid", "can:True", "add", "can:True", "apply" }, "InvalidOperationException");
}
{
    var f = Context("ARequestAction"); f.Main = true; f.ReceiveCallback = _ => throw new InvalidOperationException("fixture");
    TraceCheck("request/delivery-throw-skips-send", f, new[] { "valid", "can:True", "add", "can:True", "apply", "player:2", "received" }, "InvalidOperationException");
}
foreach (long delay in new[] { -1L, 0L, 25L })
{
    var f = Context(); f.Main = true; f.Delay = delay;
    TraceCheck("main/send-pause-delay-" + delay, f, delay > 0 ? new[] { "valid", "apply", "send", "pause:25", "destroy" } : new[] { "valid", "apply", "send", "destroy" });
    Check("main/delay-read-count-" + delay, delay > 0 ? 2 : 1, f.DelayReads);
}
{
    var f = Context(); f.Main = true; f.Delay = 25; f.SendResult = false;
    TraceCheck("main/send-false-still-pauses", f, new[] { "valid", "apply", "send", "pause:25", "destroy" });
}
{
    var f = Context(); f.Main = false; f.Delay = 25;
    TraceCheck("non-main/skips-send-pause", f, new[] { "valid", "apply", "destroy" });
    Check("non-main/delay-not-read", 0, f.DelayReads);
}
{
    var f = Context(); f.Main = true; f.Delay = 25; f.SendCallback = _ => throw new InvalidOperationException("fixture");
    TraceCheck("main/send-throw-skips-pause-destroy", f, new[] { "valid", "apply", "send" }, "InvalidOperationException");
}
{
    var f = Context(); f.Main = true; f.Delay = 25; f.PauseCallback = _ => throw new InvalidOperationException("fixture");
    TraceCheck("main/pause-throw-skips-destroy", f, new[] { "valid", "apply", "send", "pause:25" }, "InvalidOperationException");
}
{
    var f = Context(); f.Main = true; f.ApplyCallback = x => x.Main = false;
    TraceCheck("callback/main-read-after-effect", f, new[] { "valid", "apply", "destroy" });
}
{
    var f = Context("ARequestAction"); f.ReceiveCallback = x => { x.Main = true; x.Delay = 7; };
    TraceCheck("callback/main-read-after-delivery", f, new[] { "valid", "can:True", "add", "can:True", "apply", "player:2", "received", "send", "pause:7" });
}
foreach (bool valid in new[] { false, true })
{
    var f = Context(); f.Valid = valid; f.Verbose = true;
    TraceCheck("verbose/valid-" + valid, f, valid ? new[] { "valid", "log-debug", "apply", "destroy" } : new[] { "valid", "log-debug", "destroy" });
}
{
    var f = Context(); f.NetworkValues = new[] { 5, 5, 5, 12 }; f.Valid = false;
    TraceCheck("network/getter-repeated-through-error-and-write", f, new[] { "log-error", "valid", "destroy" });
    Check("network/last-uses-final-read", new { reads = 4, last = 12, seen = 12 }, new { reads = f.NetworkReads, last = (int)Call(f.Manager, "get_LastKnownNetworkID")!, seen = f.LastSeenAtValidation });
}
{
    var f = Context(); f.Main = true; f.DelayValues = new[] { 25L, -7L };
    TraceCheck("delay/positive-test-then-repeated-argument-read", f, new[] { "valid", "apply", "send", "pause:-7", "destroy" });
}
{
    var f = Context("ARequestAction"); f.ApplyCallback = x => x.PlayerId = 1;
    TraceCheck("request/recipient-read-after-effect", f, new[] { "valid", "can:True", "add", "can:True", "apply", "player:1", "received" });
}
{
    var f = Context(); f.Main = true; f.Delay = 25; f.SendCallback = x => x.Delay = 3;
    TraceCheck("delay/read-after-send-callback", f, new[] { "valid", "apply", "send", "pause:3", "destroy" });
}
{
    var f = Context("ARequestAction"); f.ApplyCallback = x => { x.Valid = false; x.ProcessValues = new[] { false }; };
    TraceCheck("request/effect-mutation-does-not-recheck-validity-or-delivery-snapshot", f,
        new[] { "valid", "can:True", "add", "can:True", "apply", "player:2", "received" });
}
{
    var f = Context(); f.Valid = false; f.Main = true; f.Delay = 25;
    TraceCheck("main/invalid-skips-send-and-pause", f, new[] { "valid", "destroy" });
}
{
    var f = Context("ARequestAction"); f.Main = true; f.Delay = 25; f.ProcessValues = new[] { false };
    TraceCheck("main/unprocessable-valid-request-still-sends-and-pauses", f,
        new[] { "valid", "can:False", "can:False", "send", "pause:25" });
}
if (AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == "Assembly-CSharp")) throw new Exception("Original assembly unexpectedly loaded");
foreach (long delay in new[] { 2147483648L, 4294967295L, 4294967296L, long.MaxValue, long.MinValue, -4294967296L, -2147483649L })
{
    var f = Context(); f.Main = true; f.Delay = delay;
    TraceCheck("delay64/value-" + delay, f, delay > 0 ? new[] { "valid", "apply", "send", "pause:" + delay, "destroy" } : new[] { "valid", "apply", "send", "destroy" });
}
var result = new { sourceSha256 = manifest.RootElement.GetProperty("sourceSha256").GetString(), extractSha256 = Hash(dll),
    copiedMethods = manifest.RootElement.GetProperty("methods").GetArrayLength(), explicitShims = manifest.RootElement.GetProperty("shims").GetArrayLength(),
    originalAssemblyLoaded = false, checks = observations.Count, passed = observations.Count - failures.Count, failed = failures.Count,
    observations, failures, scope = "Original ApplyAction control flow only. Apply/validity/register/delivery/logger/send/pause/destroy callbacks are harness seams; no actual effect/network/cleanup/scheduler parity." };
File.WriteAllText(Path.Combine(root, "docs/evidence/beta-manager-apply-fixtures.json"), JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.WriteLine($"Original manager Apply fixtures: {observations.Count - failures.Count}/{observations.Count}; explicit seams24.");
foreach (string failure in failures) Console.WriteLine("FAILED " + failure);
return failures.Count == 0 ? 0 : 1;

class Fixture
{
    public object Action = null!, Manager = null!, Controller = null!;
    public List<string> Trace = new();
    public bool Fire = true, Before = true, Valid = true, Main, Dirty, Verbose, SendResult = true;
    public int NetworkId, BeforeReads, LastSeenAtValidation, ProcessReads, PlayerId = 2, DelayReads, NetworkReads;
    public long Delay;
    public int[]? NetworkValues;
    public long[]? DelayValues;
    public bool[] ProcessValues = new[] { true };
    public Action<Fixture>? AddCallback, ApplyCallback, ReceiveCallback, SendCallback, PauseCallback;
}
