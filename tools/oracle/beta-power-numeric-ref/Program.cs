using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text.Json;

// Prepared, not executed yet. Expected values below are IL-derived hypotheses
// until the isolated original methods have actually produced the observations.
string root = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
string evidence = Path.Combine(root, "docs/evidence");
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(evidence, "beta-power-numeric-extraction.json")));
string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
string dll = manifest.RootElement.GetProperty("extract").GetString()!;
const string Baseline = "0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F";
if (manifest.RootElement.GetProperty("sourceSha256").GetString() != Baseline
    || Hash(manifest.RootElement.GetProperty("source").GetString()!) != Baseline
    || Hash(dll) != manifest.RootElement.GetProperty("extractSha256").GetString()
    || Hash(Path.Combine(root, "tools/oracle/extract_beta_power_numeric.ps1")) != manifest.RootElement.GetProperty("extractorSha256").GetString()
    || manifest.RootElement.GetProperty("methods").GetArrayLength() != 18
    || manifest.RootElement.GetProperty("shims").GetArrayLength() != 1
    || !manifest.RootElement.GetProperty("originalRuntimeReferencesAbsent").GetBoolean()
    || manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean()))
    throw new Exception("Numeric extraction provenance failed");
Assembly assembly = Assembly.LoadFrom(dll);
if (assembly.GetReferencedAssemblies().Any(a => a.Name == "Assembly-CSharp" || a.Name!.StartsWith("Unity")))
    throw new Exception("Original runtime reference");
const BindingFlags Flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
Type powerType = assembly.GetType("GwentGameplay.CardPower", true)!;
object? Call(object obj, string name, params object?[] values) => powerType.GetMethod(name, Flags)!.Invoke(obj, values);
int Get(object obj, string name) => (int)Call(obj, "get_" + name)!;
PowerFields Read(object obj) => new(Get(obj, "BasePower"), Get(obj, "PermanentPower"), Get(obj, "CurrentPower"), Get(obj, "CurrentArmor"));
void Write(object obj, PowerFields fields)
{
    Call(obj, "set_BasePower", fields.Base); Call(obj, "set_PermanentPower", fields.Permanent);
    Call(obj, "set_CurrentPower", fields.Current); Call(obj, "set_CurrentArmor", fields.Armor);
}
var scenarios = new List<Scenario>();
var normal = new PowerFields(8, -3, 4, 2);
void Setter(string id, string method, PowerFields before, int[] args, PowerFields after,
    int rawPower, int rawArmor, string? error = null, PowerFields? mutateInSetter = null)
{
    // Base/permanent mutations precede the callback; current/armor stay raw
    // because our seam observes arguments instead of implementing the setter.
    PowerFields atCall = mutateInSetter != null ? before : after;
    scenarios.Add(new(id, method, before, args, after, new[] { new SetterCall(rawPower, rawArmor, atCall) },
        null, error, mutateInSetter));
}
void NoSetter(string id, string method, PowerFields before, int[] args)
    => scenarios.Add(new(id, method, before, args, before, Array.Empty<SetterCall>(), null, null, null));
void Multiply(string id, int value, int multiplier, int expected)
    => scenarios.Add(new(id, "MultiplyValue", normal, new[] { value, multiplier }, normal,
        Array.Empty<SetterCall>(), expected, null, null));

Setter("current/raw-positive", "SetPower", normal, new[] { 11 }, normal, 11, 2);
Setter("current/raw-negative", "SetPower", normal, new[] { -3 }, normal, -3, 2);
Setter("armor/raw-negative", "SetArmor", normal, new[] { -5 }, normal, 4, -5);
Setter("base/increase", "SetBasePower", normal, new[] { 12 }, new(12, -3, 4, 2), 8, 2);
Setter("base/reduce-clamps-permanent", "SetBasePower", normal, new[] { 2 }, new(2, -2, 4, 2), -2, 2);
Setter("base/negative-requested-delta", "SetBasePower", normal, new[] { -4 }, new(0, 0, 4, 2), -8, 2);
Setter("base/explicit-armor", "SetBasePowerAndArmor", normal, new[] { 2, 19 }, new(2, -2, 4, 2), -2, 19);
Setter("base/unchanged-still-calls-setter", "SetBasePower", normal, new[] { 8 }, normal, 4, 2);
Setter("base/subtraction-wrap", "SetBasePower", new(int.MaxValue, 0, 5, 2), new[] { int.MinValue }, new(0, 0, 5, 2), 6, 2);
Setter("base/current-addition-wrap", "SetBasePower", new(1, 0, int.MaxValue, 2), new[] { 2 }, new(2, 0, int.MaxValue, 2), int.MinValue, 2);
Setter("permanent/increase", "SetPermanentPower", normal, new[] { 7 }, new(8, 7, 4, 2), 14, 2);
Setter("permanent/negative-requested-delta", "SetPermanentPower", normal, new[] { -20 }, new(8, -8, 4, 2), -13, 2);
Setter("permanent/explicit-armor", "SetPermanentPowerAndArmor", normal, new[] { -20, -7 }, new(8, -8, 4, 2), -13, -7);
Setter("permanent/unchanged-still-calls-setter", "SetPermanentPower", normal, new[] { -3 }, normal, 4, 2);
Setter("permanent/subtraction-wrap", "SetPermanentPower", new(8, int.MaxValue, 7, 2), new[] { int.MinValue }, new(8, -8, 7, 2), 8, 2);

var damaged = new PowerFields(8, -3, 2, 2);
Setter("restore/partial", "RestorePower", damaged, new[] { 2 }, damaged, 4, 2);
Setter("restore/caps-to-base-plus-permanent", "RestorePower", damaged, new[] { 99 }, damaged, 5, 2);
Setter("restore/negative-lowers-power", "RestorePower", damaged, new[] { -3 }, damaged, -1, 2);
Setter("restore/zero-still-calls-setter", "RestorePower", damaged, new[] { 0 }, damaged, 2, 2);
NoSetter("restore/equal-no-setter", "RestorePower", new(8, -3, 5, 2), new[] { 2 });
NoSetter("restore/boosted-no-setter", "RestorePower", new(8, -3, 9, 2), new[] { 2 });
NoSetter("restore/maximum-addition-wrap", "RestorePower", new(int.MaxValue, 1, 0, 2), new[] { 10 });
var differenceWrap = new PowerFields(int.MaxValue, 0, int.MinValue, 2);
Setter("restore/difference-and-current-wrap", "RestorePower", differenceWrap, new[] { 10 }, differenceWrap, int.MaxValue, 2);
Setter("armor/add-positive", "AddArmor", normal, new[] { 3 }, normal, 4, 5);
Setter("armor/add-negative", "AddArmor", normal, new[] { -9 }, normal, 4, -7);
var armorWrap = new PowerFields(8, -3, 4, int.MaxValue);
Setter("armor/add-wrap", "AddArmor", armorWrap, new[] { 1 }, armorWrap, 4, int.MinValue);
var armorSeven = new PowerFields(8, -3, 4, 7);
Setter("armor/multiply-floor", "MultiplyArmor", armorSeven, new[] { 150 }, armorSeven, 4, 10);
Setter("armor/multiply-negative", "MultiplyArmor", armorSeven, new[] { -50 }, armorSeven, 4, -4);

Multiply("multiply/positive-floor", 3, 50, 1);
Multiply("multiply/negative-floor", -3, 50, -2);
Multiply("multiply/negative-percent", 1, -50, -1);
Multiply("multiply/two-negatives", -3, -50, 1);
Multiply("multiply/fraction-below-one", 3, 33, 0);
Multiply("multiply/identity", 17, 100, 17);
Multiply("multiply/zero-percent", int.MaxValue, 0, 0);
Multiply("multiply/float-integer-rounding", 16777217, 100, 16777216);
Multiply("multiply/min-value-in-range", int.MinValue, 100, int.MinValue);

Setter("boundary/throw-keeps-base-mutation", "SetBasePower", normal, new[] { 2 }, new(2, -2, 4, 2), -2, 2, "InvalidOperationException");
Setter("boundary/throw-keeps-permanent-mutation", "SetPermanentPower", normal, new[] { -20 }, new(8, -8, 4, 2), -13, 2, "InvalidOperationException");
Setter("boundary/callback-may-rewrite-fields", "SetPower", normal, new[] { 10 }, new(1, -1, 100, 9), 10, 2,
    mutateInSetter: new(1, -1, 100, 9));

var observations = new List<object>(); var failures = new List<string>();
foreach (Scenario scenario in scenarios)
{
    object obj = FormatterServices.GetUninitializedObject(powerType);
    Write(obj, scenario.Before);
    var calls = new List<SetterCall>();
    powerType.GetField("_OracleSetPowerAndArmor", Flags)!.SetValue(obj, new Action<int, int>((power, armor) =>
    {
        calls.Add(new(power, armor, Read(obj)));
        if (scenario.MutateInSetter != null) Write(obj, scenario.MutateInSetter);
        if (scenario.ExpectedError != null) throw new InvalidOperationException("fixture");
    }));
    string? error = null; int? returned = null;
    try
    {
        object? value = Call(obj, scenario.Method, scenario.Arguments.Cast<object?>().ToArray());
        if (value is int number) returned = number;
    }
    catch (TargetInvocationException exception) { error = exception.InnerException!.GetType().Name; }
    var expected = new Outcome(scenario.ExpectedAfter, scenario.ExpectedCalls, scenario.ExpectedReturn, scenario.ExpectedError);
    var actual = new Outcome(Read(obj), calls.ToArray(), returned, error);
    bool passed = JsonSerializer.Serialize(expected) == JsonSerializer.Serialize(actual);
    observations.Add(new { id = scenario.Id, method = scenario.Method, before = scenario.Before,
        arguments = scenario.Arguments, mutateInSetter = scenario.MutateInSetter, expected, actual, passed });
    if (!passed) failures.Add(scenario.Id);
}
if (AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == "Assembly-CSharp"))
    throw new Exception("Original assembly unexpectedly loaded");
var result = new
{
    schema = 1, sourceSha256 = Baseline, extractSha256 = Hash(dll),
    harnessSha256 = Hash(Path.Combine(root, "tools/oracle/beta-power-numeric-ref/Program.cs")),
    copiedMethods = 18, explicitShims = 1, originalAssemblyLoaded = false,
    originalCodeExecuted = true, checks = observations.Count,
    passed = observations.Count - failures.Count, failed = failures.Count, observations, failures,
    scope = "Exact numeric/accessor IL with raw SetPowerAndArmor seam. No final-setter clamp/events, armor absorption, Card.Init/Reset, registry/death/banish or native WitcherScript evidence. Out-of-range floating conv.i4 excluded."
};
File.WriteAllText(Path.Combine(evidence, "beta-power-numeric-fixtures.json"), JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.WriteLine($"Original numeric boundary fixtures: {observations.Count - failures.Count}/{observations.Count}; seam1.");
return failures.Count == 0 ? 0 : 1;

record PowerFields(int Base, int Permanent, int Current, int Armor);
record SetterCall(int Power, int Armor, PowerFields FieldsAtEntry);
record Outcome(PowerFields After, SetterCall[] Calls, int? Return, string? Error);
record Scenario(string Id, string Method, PowerFields Before, int[] Arguments, PowerFields ExpectedAfter,
    SetterCall[] ExpectedCalls, int? ExpectedReturn, string? ExpectedError, PowerFields? MutateInSetter);
