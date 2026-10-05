using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text.Json;

// Load only the verified extracted methods. Unity/original module never loads.
string root = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
string evidence = Path.Combine(root, "docs", "evidence");
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(evidence, "beta-request-extraction.json")));
string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
string extractedPath = manifest.RootElement.GetProperty("extract").GetString()!;
if (Hash(extractedPath) != manifest.RootElement.GetProperty("extractSha256").GetString() ||
    Hash(manifest.RootElement.GetProperty("source").GetString()!) != manifest.RootElement.GetProperty("sourceSha256").GetString())
    throw new Exception("Source/extract hash mismatch");
if (manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean()))
    throw new Exception("Exact IL verification missing");
Assembly extracted = Assembly.LoadFrom(extractedPath);
const BindingFlags All = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
Type T(string name) => extracted.GetType("GwentGameplay." + name, true)!;
object? Call(object obj, string name, params object[] values) => obj.GetType().GetMethod(name, All)!.Invoke(obj, values);
string casesPath = Path.Combine(root, "tools", "oracle", "beta-request-ref", "limit-cases.json");
using var cases = JsonDocument.Parse(File.ReadAllText(casesPath));
var observations = new List<object>();
int failures = 0;
foreach (var fixture in cases.RootElement.EnumerateArray())
{
    string kind = fixture.GetProperty("kind").GetString()!;
    bool choice = kind == "choiceFinish";
    object request = FormatterServices.GetUninitializedObject(T(choice ? "RequestCardChoicesAction" : "ARequestTargetsAction"));
    string suffix = choice ? "Choices" : "Targets";
    int max = fixture.GetProperty("max").GetInt32();
    int selected = fixture.GetProperty("selected").GetInt32();
    Call(request, "set_Max" + suffix, max);
    Call(request, "set_Min" + suffix, fixture.TryGetProperty("min", out var min) ? min.GetInt32() : -999);
    Call(request, "set_PlayerFinishedTargeting", fixture.GetProperty("finished").GetBoolean());
    if (choice)
        Call(request, "set_SelectedChoices", Enumerable.Range(1, selected).Select(i => (ushort)i).ToList());
    else
    {
        T("ARequestTargetsAction").GetField("_OracleGetNumSelectedTargets", All)!.SetValue(request, selected);
        T("ARequestTargetsAction").GetField("_OracleGetNumValidTargets", All)!.SetValue(request,
            fixture.TryGetProperty("valid", out var valid) ? valid.GetInt32() : 5);
    }
    object? returned = Call(request, kind == "targetApply" ? "ApplyImpl" : choice ? "FinishChoiceSelection" : "FinishTargetSelection");
    bool finished = (bool)Call(request, "get_PlayerFinishedTargeting")!;
    int actualMin = (int)Call(request, "get_Min" + suffix)!;
    int actualMax = (int)Call(request, "get_Max" + suffix)!;
    bool passed = finished == fixture.GetProperty("expectedFinished").GetBoolean();
    if (kind == "targetApply")
        passed &= actualMin == fixture.GetProperty("expectedMin").GetInt32() && actualMax == fixture.GetProperty("expectedMax").GetInt32();
    if (choice) passed &= (bool)returned! == fixture.GetProperty("expectedReturn").GetBoolean();
    if (!passed) failures++;
    observations.Add(new { id = fixture.GetProperty("id").GetString(), passed, fixture = fixture.Clone(),
        actual = new { min = actualMin, max = actualMax, finished, returned } });
}
var report = new { sourceSha256 = manifest.RootElement.GetProperty("sourceSha256").GetString(),
    extractSha256 = Hash(extractedPath), fixtureSha256 = Hash(casesPath), copiedMethods = 18,
    checks = observations.Count, passed = observations.Count - failures, failed = failures, observations,
    scope = "Exact copied IL for target Apply limits/OnTargetAdded/Finish and choice Finish. Abstract counts and lists supplied by harness. No actual card selection, events, manager, scheduler, continuation, RNG, Unity or network." };
File.WriteAllText(Path.Combine(evidence, "beta-request-limit-fixtures.json"), JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine($"Copied request IL checks: {observations.Count - failures}/{observations.Count}");
return failures == 0 ? 0 : 1;
