using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text.Json;

string root = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "docs/evidence/beta-apply-extraction.json")));
string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
string dll = manifest.RootElement.GetProperty("extract").GetString()!;
if (Hash(dll) != manifest.RootElement.GetProperty("extractSha256").GetString()
    || Hash(manifest.RootElement.GetProperty("source").GetString()!) != manifest.RootElement.GetProperty("sourceSha256").GetString()
    || !manifest.RootElement.GetProperty("originalRuntimeReferencesAbsent").GetBoolean()
    || manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean()))
    throw new Exception("Apply extraction provenance failed");
Assembly assembly = Assembly.LoadFrom(dll);
if (assembly.GetReferencedAssemblies().Any(a => a.Name == "Assembly-CSharp" || a.Name!.StartsWith("Unity"))) throw new Exception("Original runtime reference");
const BindingFlags Flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
Type T(string name) => assembly.GetType("GwentGameplay." + name, true)!;
object New(string name) => FormatterServices.GetUninitializedObject(T(name));
object? Call(object obj, string name, params object?[] values) => obj.GetType().GetMethod(name, Flags)!.Invoke(obj, values);
void Field(object obj, string name, object value) => obj.GetType().GetField(name, Flags)!.SetValue(obj, value);
var observations = new List<object>(); var failures = new List<string>();
void Check(string id, object expected, object actual)
{
    bool passed = JsonSerializer.Serialize(expected) == JsonSerializer.Serialize(actual);
    observations.Add(new { id, expected, actual, passed }); if (!passed) failures.Add(id);
}
(object action, object controller, List<string> trace) Context(bool initialized = true, bool authority = true, bool fire = true)
{
    object action = New("AAction"), controller = New("GameController"); var trace = new List<string>();
    Field(action, "m_Initialized", initialized); Call(action, "set_GameController", controller); Call(action, "set_FireTriggers", fire);
    Field(controller, "_Oracleget_HasAuthority", authority);
    Field(action, "_Oracleget_ActionID", Enum.ToObject(T("EActionID"), 0));
    Field(action, "_OracleApplyImpl", new Action(() => trace.Add("apply")));
    Field(action, "_OracleAfterApplyTriggers", new Action(() => trace.Add("after")));
    return (action, controller, trace);
}
string? ApplyError(object action)
{
    try { Call(action, "Apply"); return null; }
    catch (TargetInvocationException error) { return error.InnerException!.GetType().Name; }
}
{
    var (a, _, trace) = Context(initialized: false);
    Check("uninitialized/throws-before-effect", new { error = "Exception", trace = Array.Empty<string>() }, new { error = ApplyError(a), trace = trace.ToArray() });
}
foreach (bool authority in new[] { false, true }) foreach (bool fire in new[] { false, true })
{
    var (a, _, trace) = Context(authority: authority, fire: fire); string? error = ApplyError(a);
    Check($"apply/authority-{authority}-fire-{fire}", new { error = (string?)null, trace = authority && fire ? new[] { "apply", "after" } : new[] { "apply" } }, new { error, trace = trace.ToArray() });
}
foreach (bool starting in new[] { false, true })
{
    var (a, _, trace) = Context(fire: starting);
    Field(a, "_OracleApplyImpl", new Action(() => { trace.Add("apply"); Call(a, "set_FireTriggers", !starting); }));
    string? error = ApplyError(a);
    Check($"callback/fire-{starting}-to-{!starting}", new { error = (string?)null, trace = starting ? new[] { "apply" } : new[] { "apply", "after" } }, new { error, trace = trace.ToArray() });
}
foreach (bool starting in new[] { false, true })
{
    var (a, controller, trace) = Context(authority: starting);
    Field(a, "_OracleApplyImpl", new Action(() => { trace.Add("apply"); Field(controller, "_Oracleget_HasAuthority", !starting); }));
    string? error = ApplyError(a);
    Check($"callback/authority-{starting}-to-{!starting}", new { error = (string?)null, trace = starting ? new[] { "apply" } : new[] { "apply", "after" } }, new { error, trace = trace.ToArray() });
}
{
    var (a, _, trace) = Context();
    Field(a, "_OracleApplyImpl", new Action(() => { trace.Add("apply"); throw new InvalidOperationException("fixture"); }));
    Check("effect/throw-skips-after", new { error = "InvalidOperationException", trace = new[] { "apply" } }, new { error = ApplyError(a), trace = trace.ToArray() });
}
{
    var (a, _, trace) = Context();
    Field(a, "_OracleAfterApplyTriggers", new Action(() => { trace.Add("after"); throw new InvalidOperationException("fixture"); }));
    Check("after/throw-does-not-undo-effect", new { error = "InvalidOperationException", trace = new[] { "apply", "after" } }, new { error = ApplyError(a), trace = trace.ToArray() });
}
foreach (bool fire in new[] { false, true })
{
    var (a, _, trace) = Context(fire: fire); Call(a, "set_GameController", new object?[] { null });
    Check($"controller/null-fire-{fire}", new { error = "NullReferenceException", trace = new[] { "apply" } }, new { error = ApplyError(a), trace = trace.ToArray() });
}
{
    var (a, _, trace) = Context(initialized: false); Call(a, "set_GameController", new object?[] { null });
    Check("uninitialized/precedes-null-controller", new { error = "Exception", trace = Array.Empty<string>() }, new { error = ApplyError(a), trace = trace.ToArray() });
}
if (AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == "Assembly-CSharp")) throw new Exception("Original assembly unexpectedly loaded");
var result = new { sourceSha256 = manifest.RootElement.GetProperty("sourceSha256").GetString(), extractSha256 = Hash(dll),
    copiedMethods = manifest.RootElement.GetProperty("methods").GetArrayLength(), explicitShims = manifest.RootElement.GetProperty("shims").GetArrayLength(),
    originalAssemblyLoaded = false, checks = observations.Count, passed = observations.Count - failures.Count, failed = failures.Count,
    observations, failures, scope = "Copied AAction.Apply and accessor control flow with field/delegate seams. No ActionManager.ApplyAction, real effects, initialization procedure, network or cleanup parity." };
File.WriteAllText(Path.Combine(root, "docs/evidence/beta-apply-fixtures.json"), JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.WriteLine($"Original Apply boundary fixtures: {observations.Count - failures.Count}/{observations.Count}; explicit seams4.");
return failures.Count == 0 ? 0 : 1;
