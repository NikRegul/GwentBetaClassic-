using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text.Json;

string root = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
string evidence = Path.Combine(root, "docs/evidence");
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(evidence, "beta-registry-id-extraction.json")));
string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
const string Baseline = "0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F";
string dll = manifest.RootElement.GetProperty("extract").GetString()!;
if (manifest.RootElement.GetProperty("sourceSha256").GetString() != Baseline
    || Hash(manifest.RootElement.GetProperty("source").GetString()!) != Baseline
    || Hash(dll) != manifest.RootElement.GetProperty("extractSha256").GetString()
    || Hash(Path.Combine(root, "tools/oracle/extract_beta_registry_ids.ps1")) != manifest.RootElement.GetProperty("extractorSha256").GetString()
    || manifest.RootElement.GetProperty("methods").GetArrayLength() != 4
    || manifest.RootElement.GetProperty("shims").GetArrayLength() != 0
    || !manifest.RootElement.GetProperty("originalRuntimeReferencesAbsent").GetBoolean()
    || manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean()))
    throw new Exception("Registry ID extraction provenance failed");
Assembly assembly = Assembly.LoadFrom(dll);
if (assembly.GetReferencedAssemblies().Any(a => a.Name == "Assembly-CSharp" || a.Name!.StartsWith("Unity"))) throw new Exception("Original runtime reference");
const BindingFlags Flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
Type managerType = assembly.GetType("GwentGameplay.CardManager", true)!;
Type cardType = assembly.GetType("GwentGameplay.Card", true)!;
object New(Type type) => FormatterServices.GetUninitializedObject(type);
object? Call(object obj, string method, params object?[] args) => managerType.GetMethod(method, Flags)!.Invoke(obj, args);
void Field(object obj, string name, object? value) => managerType.GetField(name, Flags)!.SetValue(obj, value);
ushort Next(object obj) => (ushort)managerType.GetField("m_NextInstanceId", Flags)!.GetValue(obj)!;
ushort Allocate(object obj) => (ushort)Call(obj, "AllocateInstanceId")!;
Array Cards(object obj) => (Array)Call(obj, "get_AllCards")!;
object? Lookup(object obj, ushort id) => Call(obj, "GetCard", id);
object Context(ushort next = 1, int size = 64, Stack<ushort>? recycled = null)
{
    object obj = New(managerType);
    Field(obj, "m_NextInstanceId", next);
    Field(obj, "m_RecycledInstanceIds", recycled ?? new Stack<ushort>());
    Call(obj, "set_AllCards", Array.CreateInstance(cardType, size));
    return obj;
}
string? Error(Action body)
{
    try { body(); return null; }
    catch (TargetInvocationException error) { return error.InnerException!.GetType().Name; }
}
var observations = new List<object>(); var failures = new List<string>();
void Check(string id, object expected, object actual)
{
    bool passed = JsonSerializer.Serialize(expected) == JsonSerializer.Serialize(actual);
    observations.Add(new { id, expected, actual, passed }); if (!passed) failures.Add(id);
}
{
    object obj = Context(); var ids = Enumerable.Range(0, 8).Select(_ => Allocate(obj)).ToArray();
    Check("allocate/initial-sequence", new { ids = Enumerable.Range(1, 8).Select(x => (ushort)x).ToArray(), next = (ushort)9, capacity = 64 },
        new { ids, next = Next(obj), capacity = Cards(obj).Length });
}
{
    object obj = Context(next: 63); object card = New(cardType); Cards(obj).SetValue(card, 2);
    ushort first = Allocate(obj); int capacityBefore = Cards(obj).Length;
    ushort second = Allocate(obj);
    Check("allocate/grow-at64-preserves-reference", new { first = (ushort)63, capacityBefore = 64, second = (ushort)64, capacityAfter = 128, preserved = true, next = (ushort)65 },
        new { first, capacityBefore, second, capacityAfter = Cards(obj).Length, preserved = ReferenceEquals(card, Lookup(obj, 2)), next = Next(obj) });
}
{
    object obj = Context(next: 128, size: 128); object card = New(cardType); Cards(obj).SetValue(card, 127);
    Check("allocate/grow-at128-preserves-reference", new { id = (ushort)128, capacity = 192, preserved = true, next = (ushort)129 },
        new { id = Allocate(obj), capacity = Cards(obj).Length, preserved = ReferenceEquals(card, Lookup(obj, 127)), next = Next(obj) });
}
{
    var recycled = new Stack<ushort>(); recycled.Push(9); recycled.Push(4);
    object obj = Context(recycled: recycled);
    Check("allocate/recycled-lifo-precedes-next", new { ids = new ushort[] { 4, 9, 1 }, next = (ushort)2, capacity = 64, recycledLeft = 0 },
        new { ids = new[] { Allocate(obj), Allocate(obj), Allocate(obj) }, next = Next(obj), capacity = Cards(obj).Length, recycledLeft = recycled.Count });
}
{
    var recycled = new Stack<ushort>(); recycled.Push(7); recycled.Push(7);
    object obj = Context(recycled: recycled);
    Check("allocate/duplicate-recycled-state-not-deduped", new { ids = new ushort[] { 7, 7 }, next = (ushort)1 },
        new { ids = new[] { Allocate(obj), Allocate(obj) }, next = Next(obj) });
}
{
    var recycled = new Stack<ushort>(); recycled.Push(5);
    object obj = Context(next: 64, recycled: recycled);
    Check("allocate/recycled-skips-growth", new { id = (ushort)5, next = (ushort)64, capacity = 64 },
        new { id = Allocate(obj), next = Next(obj), capacity = Cards(obj).Length });
}
{
    object obj = Context(next: ushort.MaxValue, size: 65536);
    Check("allocate/uint16-wrap-keeps-zero", new { ids = new ushort[] { 65535, 0, 1 }, next = (ushort)2, capacity = 65536 },
        new { ids = new[] { Allocate(obj), Allocate(obj), Allocate(obj) }, next = Next(obj), capacity = Cards(obj).Length });
}
{
    object obj = Context(); object card = New(cardType); Cards(obj).SetValue(card, 1);
    Check("lookup/existing-same-reference", true, ReferenceEquals(card, Lookup(obj, 1)));
    Check("lookup/null-slot", true, Lookup(obj, 2) == null);
    Check("lookup/zero-slot", true, Lookup(obj, 0) == null);
    Check("lookup/at-capacity", true, Lookup(obj, 64) == null);
    Check("lookup/above-capacity", true, Lookup(obj, ushort.MaxValue) == null);
}
{
    object obj = Context(); Call(obj, "set_AllCards", new object?[] { null });
    Check("lookup/null-array-throws", "NullReferenceException", Error(() => Lookup(obj, 1))!);
    Check("allocate/null-array-throws", "NullReferenceException", Error(() => Allocate(obj))!);
}
{
    var recycled = new Stack<ushort>(); recycled.Push(5);
    object obj = Context(recycled: recycled); Call(obj, "set_AllCards", new object?[] { null });
    Check("allocate/recycled-does-not-read-null-array", new { id = (ushort)5, next = (ushort)1 }, new { id = Allocate(obj), next = Next(obj) });
}
{
    object obj = Context(); Field(obj, "m_RecycledInstanceIds", null);
    Check("allocate/null-recycle-stack-throws", "NullReferenceException", Error(() => Allocate(obj))!);
}
if (AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == "Assembly-CSharp")) throw new Exception("Original assembly loaded");
var report = new { schema = 1, sourceSha256 = Baseline, extractSha256 = Hash(dll),
    harnessSha256 = Hash(Path.Combine(root, "tools/oracle/beta-registry-id-ref/Program.cs")),
    originalAssemblyLoaded = false, originalCodeExecuted = true, copiedMethods = 4, explicitShims = 0,
    checks = observations.Count, passed = observations.Count - failures.Count, failed = failures.Count, observations, failures,
    scope = "Exact AllocateInstanceId/GetCard and AllCards accessors only. Initial state/recycled IDs assigned directly, Card opaque reference. No constructor/Register/Unregister/event/copy/full registry acceptance."
};
File.WriteAllText(Path.Combine(evidence, "beta-registry-id-fixtures.json"), JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.WriteLine($"Original registry ID fixtures: {observations.Count - failures.Count}/{observations.Count}; no shims.");
return failures.Count == 0 ? 0 : 1;
