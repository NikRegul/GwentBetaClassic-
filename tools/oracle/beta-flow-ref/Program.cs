using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text.Json;

// Only the extracted assembly is loaded. Original Unity assembly/module initializer
// is never loaded by this harness. Gameplay bodies are copied, not reimplemented.
string workspace = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
string toolDir = Path.Combine(workspace, "tools", "oracle", "beta-flow-ref");
string extractedPath = Path.Combine(toolDir, "reference", "BetaFlowExtract.dll");
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(workspace, "docs", "evidence", "beta-flow-extraction.json")));
string extractedHash = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(extractedPath)));
if (extractedHash != manifest.RootElement.GetProperty("extractSha256").GetString()) throw new Exception("Extraction hash mismatch");
string sourcePath = manifest.RootElement.GetProperty("source").GetString()!;
if (Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(sourcePath))) != manifest.RootElement.GetProperty("sourceSha256").GetString()) throw new Exception("Source hash mismatch");
if (manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean())) throw new Exception("Instruction verification missing");
Assembly extracted = Assembly.LoadFrom(extractedPath);
Type T(string name) => extracted.GetType("GwentGameplay." + name, throwOnError: true)!;
const BindingFlags AllInstance = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
object New(string name) => FormatterServices.GetUninitializedObject(T(name));
object? Call(object obj, string method, params object[] values) => obj.GetType().GetMethod(method, AllInstance)!.Invoke(obj, values);
object Id(int value) => Enum.ToObject(T("EPlayerId"), value);
void Field(object obj, string name, object value)
{
    for (Type? type = obj.GetType(); type != null; type = type.BaseType)
    {
        var field = type.GetField(name, AllInstance | BindingFlags.DeclaredOnly);
        if (field != null) { field.SetValue(obj, value); return; }
    }
    throw new Exception("Field not found: " + name);
}
(object[], object, object) Context(int[] crowns)
{
    object[] players = { New("Player"), New("Player") };
    for (int i = 0; i < 2; i++) { Call(players[i], "set_Id", Id(i + 1)); Call(players[i], "set_Crowns", crowns[i]); }
    Array playerArray = Array.CreateInstance(T("Player"), 2);
    playerArray.SetValue(players[0], 0); playerArray.SetValue(players[1], 1);
    object manager = New("PlayerManager"); Field(manager, "Players", playerArray);
    object controller = New("GameController"); Field(controller, "<PlayerManager>k__BackingField", manager);
    object roundManager = New("RoundManager"); Field(roundManager, "<GameController>k__BackingField", controller);
    return (players, manager, roundManager);
}
var observations = new List<object>();
var failures = new List<string>();
void Check(string id, bool passed, object expected, object actual)
{
    observations.Add(new { id, passed, expected, actual });
    if (!passed) failures.Add(id);
}
using var fixtures = JsonDocument.Parse(File.ReadAllText(Path.Combine(toolDir, "round-cases.json")));
foreach (var fixture in fixtures.RootElement.EnumerateArray())
{
    string id = fixture.GetProperty("id").GetString()!;
    int[] Ints(JsonElement value) => value.EnumerateArray().Select(v => v.GetInt32()).ToArray();
    var (players, manager, roundManager) = Context(Ints(fixture.GetProperty("initialCrowns")));
    int index = 0;
    foreach (var expected in fixture.GetProperty("rounds").EnumerateArray())
    {
        index++;
        int[] scores = Ints(expected.GetProperty("scores"));
        object round = Activator.CreateInstance(T("RoundInfo"), index, 2)!;
        Call(round, "SetResult", manager, scores);
        // The round must snapshot scores rather than retaining our input array.
        scores[0] = 987654321;
        int[] stored = (int[])Call(round, "get_PlayerScores")!;
        int[] crowns = players.Select(p => (int)Call(p, "get_Crowns")!).ToArray();
        int winner = Convert.ToInt32(Call(round, "get_WinnerId"));
        int match = Convert.ToInt32(Call(roundManager, "GetWinner"));
        bool hasWinner = (bool)Call(roundManager, "HasWinner")!;
        bool passed = stored.SequenceEqual(Ints(expected.GetProperty("scores"))) &&
            crowns.SequenceEqual(Ints(expected.GetProperty("crowns"))) &&
            winner == expected.GetProperty("roundWinner").GetInt32() &&
            match == expected.GetProperty("matchWinner").GetInt32() && hasWinner == (match != 0);
        Check(id + "/round-" + index, passed, expected.Clone(), new { scores = stored, crowns, roundWinner = winner, matchWinner = match, hasWinner });
    }
}
foreach (var first in new[] { false, true }) foreach (var second in new[] { false, true })
{
    var (players, manager, _) = Context(new[] { 0, 0 });
    Call(players[0], "OnPass", first); Call(players[1], "OnPass", second);
    bool actual = (bool)Call(manager, "AllPlayersPassed")!;
    Check($"pass-{first}-{second}", actual == (first && second), first && second, actual);
}
{
    var (players, manager, _) = Context(new[] { 0, 0 });
    Call(players[0], "OnPass", true); Call(players[1], "OnPass", true);
    foreach (object player in players) Call(player, "OnRoundStart");
    bool actual = (bool)Call(manager, "AllPlayersPassed")!;
    bool[] individual = players.Select(p => (bool)Call(p, "get_HasPassed")!).ToArray();
    Check("round-start-clears-both-passes", !actual && individual.All(v => !v), new[] { false, false }, individual);
    Field(players[0], "HasMadeInitialMoveForCurrentTurn", true);
    Call(players[0], "OnTurnEnd");
    bool move = (bool)T("Player").GetField("HasMadeInitialMoveForCurrentTurn", AllInstance)!.GetValue(players[0])!;
    Check("turn-end-clears-initial-move", !move, false, move);
}
var report = new
{
    sourceSha256 = manifest.RootElement.GetProperty("sourceSha256").GetString(), extractedSha256 = extractedHash,
    fixtureSha256 = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(toolDir, "round-cases.json")))),
    copiedMethods = manifest.RootElement.GetProperty("methods").GetArrayLength(), checks = observations.Count,
    passed = failures.Count == 0, failures, observations,
    scope = "Executed exact copied IL for RoundInfo.SetResult(scores), RoundManager winner/HasWinner and player pass/reset. Data holders initialized by harness. No original client, board score calculation, scheduler, triggers, UI or network executed."
};
File.WriteAllText(Path.Combine(workspace, "docs", "evidence", "beta-flow-fixtures.json"), JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine($"Copied IL checks: {observations.Count - failures.Count}/{observations.Count} passed");
return failures.Count == 0 ? 0 : 1;
