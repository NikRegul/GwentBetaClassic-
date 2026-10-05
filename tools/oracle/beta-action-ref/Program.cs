using System.Collections;
using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text.Json;

// Loads only the isolated extraction. Five explicit delegates/fields supply
// validation, callbacks, dispatch, authority and exception text boundaries.
string root = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
string manifestPath = Path.Combine(root, "docs/evidence/beta-action-extraction.json");
using var manifest = JsonDocument.Parse(File.ReadAllText(manifestPath));
string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
string extractedPath = manifest.RootElement.GetProperty("extract").GetString()!;
if (Hash(extractedPath) != manifest.RootElement.GetProperty("extractSha256").GetString()
    || Hash(manifest.RootElement.GetProperty("source").GetString()!) != manifest.RootElement.GetProperty("sourceSha256").GetString()
    || manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean()))
    throw new Exception("Extraction provenance failed");
Assembly extracted = Assembly.LoadFrom(extractedPath);
const BindingFlags Flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
Type T(string name) => extracted.GetType("GwentGameplay." + name, true)!;
object New(string name) => FormatterServices.GetUninitializedObject(T(name));
object? Call(object obj, string method, params object[] values) => obj.GetType().GetMethod(method, Flags)!.Invoke(obj, values);
void Field(object obj, string name, object value)
{
    for (Type? type = obj.GetType(); type != null; type = type.BaseType)
    {
        var field = type.GetField(name, Flags | BindingFlags.DeclaredOnly);
        if (field != null) { field.SetValue(obj, value); return; }
    }
    throw new Exception("Missing field " + name);
}
var observations = new List<object>();
var failures = new List<string>();
var labels = new Dictionary<object, string>();
void Check(string id, object expected, object actual)
{
    bool passed = JsonSerializer.Serialize(expected) == JsonSerializer.Serialize(actual);
    observations.Add(new { id, expected, actual, passed });
    if (!passed) failures.Add(id);
}
(object manager, object controller, IList queue, List<string> trace, Action<object> dispatch) Context(bool authority = true)
{
    object controller = New("GameController"), manager = New("ActionManager");
    IList queue = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(T("AAction")))!;
    Call(manager, "set_Actions", queue); Call(controller, "set_ActionManager", manager);
    Field(manager, "<GameController>k__BackingField", controller);
    Field(controller, "_Oracleget_HasAuthority", authority);
    var trace = new List<string>();
    Action<object> dispatch = obj => trace.Add("dispatch:" + labels[obj]);
    Field(manager, "_OracleApplyAction", dispatch);
    return (manager, controller, queue, trace, dispatch);
}
object ActionCard(string label, List<string> trace, bool valid = true, bool fire = true, bool priority = false)
{
    object action = New(priority ? "OraclePriorityAction" : "AAction"); labels[action] = label;
    Field(action, "_OracleIsValid", new Func<bool>(() => valid));
    Field(action, "_OracleBeforeApplyTriggerImpl", new Action(() => trace.Add("before:" + label)));
    Call(action, "set_FireTriggers", fire);
    return action;
}
string[] Queue(IList queue) => queue.Cast<object>().Select(obj => labels[obj]).ToArray();
object Local(object controller, params object[] actions)
{
    object local = New("AbilityInstance");
    Field(local, "<GameController>k__BackingField", controller);
    IList queue = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(T("AAction")))!;
    foreach (object action in actions) queue.Add(action);
    Call(local, "set_Actions", queue);
    return local;
}

{
    var (manager, _, queue, trace, _) = Context();
    var a = ActionCard("a", trace); queue.Add(a);
    Call(manager, "Step");
    Check("global/before-keeps-action", new { queue = new[] { "a" }, trace = new[] { "before:a" } }, new { queue = Queue(queue), trace = trace.ToArray() });
    Call(manager, "Step");
    Check("global/apply-next-step", new { queue = Array.Empty<string>(), trace = new[] { "before:a", "dispatch:a" } }, new { queue = Queue(queue), trace = trace.ToArray() });
    Call(manager, "Step"); Check("global/empty-no-op", 2, trace.Count);
}
{
    var (manager, _, queue, trace, _) = Context();
    var a = ActionCard("a", trace); var b = ActionCard("b", trace); queue.Add(a);
    Field(a, "_OracleBeforeApplyTriggerImpl", new Action(() => { trace.Add("before:a"); Call(manager, "PushActionImpl", b, true); }));
    Call(manager, "Step"); Check("global/nested-front-order", new[] { "b", "a" }, Queue(queue));
    Call(manager, "Step"); Call(manager, "Step"); Call(manager, "Step");
    Check("global/nested-front-trace", new[] { "before:a", "before:b", "dispatch:b", "dispatch:a" }, trace.ToArray());
    Check("global/nested-before-once", 0, queue.Count);
}
{
    var (manager, _, queue, trace, _) = Context();
    var a = ActionCard("a", trace); queue.Add(a); int calls = 0;
    Field(a, "_OracleBeforeApplyTriggerImpl", new Action(() => { calls++; Call(a, "BeforeApplyTrigger"); }));
    Call(manager, "Step"); Check("before/reentrant-once", 1, calls);
    Check("before/flag-set-before-callback", true, Call(a, "get_HasFiredBeforeApplyTrigger")!);
    Call(a, "BeforeApplyTrigger"); Check("before/repeated-no-op", 1, calls);
}
{
    var (manager, _, queue, trace, _) = Context();
    var a = ActionCard("invalid", trace, valid: false); queue.Add(a); Call(manager, "Step");
    Check("global/invalid-dispatched-without-before", new[] { "dispatch:invalid" }, trace.ToArray());
    Check("global/invalid-removed", 0, queue.Count);
    Check("before/invalid-unfired", false, Call(a, "get_HasFiredBeforeApplyTrigger")!);
}
{
    var (manager, _, queue, trace, _) = Context();
    var a = ActionCard("a", trace, fire: false); queue.Add(a); int validations = 0;
    Field(a, "_OracleIsValid", new Func<bool>(() => { validations++; return true; }));
    Check("before/no-fire-reports-fired", true, Call(a, "get_HasFiredBeforeApplyTrigger")!);
    Call(manager, "Step"); Check("global/no-fire-single-step", new[] { "dispatch:a" }, trace.ToArray());
    Check("global/no-fire-skips-step-validity", 0, validations);
    Call(a, "set_FireTriggers", true); Check("before/enabling-restores-unfired", false, Call(a, "get_HasFiredBeforeApplyTrigger")!);
}
{
    var (manager, _, queue, trace, _) = Context(false);
    var a = ActionCard("a", trace); queue.Add(a); int validations = 0;
    Field(a, "_OracleIsValid", new Func<bool>(() => { validations++; return true; }));
    Call(manager, "Step"); Check("global/non-authority-dispatch", new[] { "dispatch:a" }, trace.ToArray());
    Check("global/non-authority-skips-validity", 0, validations);
}
{
    var (manager, controller, queue, trace, _) = Context();
    var a = ActionCard("a", trace); var b = ActionCard("b", trace);
    Call(manager, "PushActionImpl", a, false); Call(manager, "PushActionImpl", b, false);
    Check("push/append-order", new[] { "a", "b" }, Queue(queue));
    var c = ActionCard("c", trace); Call(manager, "PushActionImpl", c, true);
    Check("push/front-order", new[] { "c", "a", "b" }, Queue(queue));
    Call(manager, "set_BreakOnChange", true); Call(manager, "Step");
    Check("debug/before-break", true, Call(controller, "get_InDebugMode")!);
    Call(controller, "set_InDebugMode", false); Call(manager, "Step");
    Check("debug/dispatch-break", true, Call(controller, "get_InDebugMode")!);
    Call(controller, "set_InDebugMode", false); Call(manager, "PushActionImpl", c, false);
    Check("debug/push-break", true, Call(controller, "get_InDebugMode")!);
}
{
    var (manager, _, queue, trace, _) = Context(false);
    var a = ActionCard("a", trace); bool thrown = false;
    try { Call(manager, "PushActionImpl", a, true); } catch (TargetInvocationException ex) when (ex.InnerException?.GetType() == typeof(Exception)) { thrown = true; }
    Check("push/non-authority-front-rejected", new { thrown = true, count = 0 }, new { thrown, count = queue.Count });
    var p = ActionCard("p", trace, priority: true); Call(manager, "PushActionImpl", p, true);
    Check("push/priority-front-permitted", new[] { "p" }, Queue(queue));
    Call(manager, "PushActionImpl", a, false); Check("push/non-authority-append-permitted", new[] { "p", "a" }, Queue(queue));
}
{
    var (manager, _, queue, trace, _) = Context();
    var a = ActionCard("a", trace); var b = ActionCard("b", trace); queue.Add(a);
    Field(a, "_OracleIsValid", new Func<bool>(() => { Call(manager, "PushActionImpl", b, true); return false; }));
    Call(manager, "Step");
    Check("global/remove-captured-object-after-validity-front-insert", new { queue = new[] { "b" }, trace = new[] { "dispatch:a" } }, new { queue = Queue(queue), trace = trace.ToArray() });
}
{
    var (manager, controller, _, trace, _) = Context();
    var a = ActionCard("a", trace); var b = ActionCard("b", trace); object local = Local(controller, a);
    IList queue = (IList)Call(local, "get_Actions")!;
    Field(a, "_OracleBeforeApplyTriggerImpl", new Action(() => { trace.Add("before:a"); queue.Insert(0, b); }));
    Call(local, "ExecuteNextAction"); Check("local/before-front-order", new[] { "b", "a" }, Queue(queue));
    Call(local, "ExecuteNextAction"); Call(local, "ExecuteNextAction"); Call(local, "ExecuteNextAction");
    Check("local/nested-front-trace", new[] { "before:a", "before:b", "dispatch:b", "dispatch:a" }, trace.ToArray());
    Check("local/queue-drained", 0, queue.Count);
    bool thrown = false;
    try { Call(local, "ExecuteNextAction"); } catch (TargetInvocationException ex) when (ex.InnerException is ArgumentOutOfRangeException) { thrown = true; }
    Check("local/empty-call-throws", true, thrown);
}
{
    var (_, controller, _, trace, _) = Context(); var a = ActionCard("a", trace); var b = ActionCard("b", trace);
    object local = Local(controller, a); IList queue = (IList)Call(local, "get_Actions")!;
    Field(a, "_OracleIsValid", new Func<bool>(() => { queue.Insert(0, b); return false; }));
    Call(local, "ExecuteNextAction");
    Check("local/remove-index-zero-after-validity-front-insert", new { queue = new[] { "a" }, trace = new[] { "dispatch:a" } }, new { queue = Queue(queue), trace = trace.ToArray() });
}
{
    var (_, controller, _, trace, _) = Context(false); var a = ActionCard("a", trace); int validations = 0;
    Field(a, "_OracleIsValid", new Func<bool>(() => { validations++; return true; }));
    object local = Local(controller, a); Call(local, "ExecuteNextAction");
    Check("local/non-authority-dispatch", new[] { "dispatch:a" }, trace.ToArray());
    Check("local/non-authority-still-validates", 1, validations);
}
{
    var (manager, _, queue, trace, _) = Context(); var a = ActionCard("a", trace); int validations = 0; queue.Add(a);
    Field(a, "_OracleIsValid", new Func<bool>(() => ++validations == 1));
    Call(manager, "Step");
    Check("before/second-validation-can-deny", new { validations = 2, fired = false, count = 1, trace = Array.Empty<string>() },
          new { validations, fired = (bool)Call(a, "get_HasFiredBeforeApplyTrigger")!, count = queue.Count, trace = trace.ToArray() });
    Call(manager, "Step"); Check("global/denied-before-next-invalid-dispatch", new[] { "dispatch:a" }, trace.ToArray());
}

var result = new { sourceSha256 = manifest.RootElement.GetProperty("sourceSha256").GetString(),
    extractSha256 = Hash(extractedPath), copiedMethods = manifest.RootElement.GetProperty("methods").GetArrayLength(),
    explicitShims = manifest.RootElement.GetProperty("shims").GetArrayLength(), checks = observations.Count,
    passed = observations.Count - failures.Count, failed = failures.Count, observations, failures,
    scope = "Copied global/local queue instructions and Before guard with synthetic delegates. Dispatch observations do not execute original ApplyAction, effects, network, death drain or complete scheduler." };
File.WriteAllText(Path.Combine(root, "docs/evidence/beta-action-fixtures.json"), JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.WriteLine($"Original queue boundary fixtures: {observations.Count - failures.Count}/{observations.Count}; explicit shims5.");
return failures.Count == 0 ? 0 : 1;
