using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;

string root = args.Length > 0 ? Path.GetFullPath(args[0]) : @"D:\w3mod";
string evidence = Path.Combine(root, "docs", "evidence");
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(evidence, "beta-rng-extraction.json")));
string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
string dll = manifest.RootElement.GetProperty("extract").GetString()!;
if (Hash(dll) != manifest.RootElement.GetProperty("extractSha256").GetString() ||
    Hash(manifest.RootElement.GetProperty("source").GetString()!) != manifest.RootElement.GetProperty("sourceSha256").GetString() ||
    manifest.RootElement.GetProperty("methods").EnumerateArray().Any(m => !m.GetProperty("exactInstructionMatch").GetBoolean()))
    throw new Exception("Verified source/extract changed");
Assembly extracted = Assembly.LoadFrom(dll);
if (extracted.GetReferencedAssemblies().Any(a => a.Name == "Assembly-CSharp" || a.Name!.StartsWith("Unity")))
    throw new Exception("Forbidden original runtime reference");
Type type = extracted.GetType("GwentCore.MersenneTwisterRandom", true)!;
const BindingFlags All = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
object New(int seed) => Activator.CreateInstance(type, seed)!;
object? Call(object rng, string method, params object[] values)
{
    var types = values.Select(v => v.GetType()).ToArray();
    return type.GetMethod(method, All, null, types, null)!.Invoke(rng, values);
}
uint Count(object rng) => (uint)Call(rng, "get_NumTimesCalledSinceCreation")!;
uint[] Draw(object rng, int count) => Enumerable.Range(0, count).Select(_ => (uint)Call(rng, "NextUnsigned")!).ToArray();
var observations = new List<object>();
int failures = 0;
void Check(string id, bool passed, object actual)
{
    observations.Add(new { id, passed, actual });
    if (!passed) failures++;
}
var vectors = new List<object>();
foreach (int seed in new[] { 0, 1, 2, 3, -1, -2, 5489, 123456789 })
{
    object rng = New(seed);
    uint[] values = Draw(rng, 16);
    object same = New(seed);
    Check($"seed/{seed}/repeat", Draw(same, 16).SequenceEqual(values), values);
    Check($"seed/{seed}/counter", Count(rng) == 16, Count(rng));
    vectors.Add(new { seed, values, counter = Count(rng) });
}
foreach (var pair in new[] { (0, 1), (2, 3), (-2, -1) })
    Check($"odd-seed-alias/{pair}", Draw(New(pair.Item1), 12).SequenceEqual(Draw(New(pair.Item2), 12)), pair);
{
    object rng = New(7);
    Check("next-zero/no-draw", (int)Call(rng, "Next", 0)! == 0 && Count(rng) == 0, Count(rng));
    Check("equal-bounds/no-draw", (int)Call(rng, "Next", 5, 5)! == 5 && Count(rng) == 0, Count(rng));
    Check("next-one/one-draw", (int)Call(rng, "Next", 1)! == 0 && Count(rng) == 1, Count(rng));
}
{
    object unsigned = New(89), signed = New(89);
    uint[] raws = Draw(unsigned, 30);
    int[] actual = Enumerable.Range(0, 30).Select(_ => (int)Call(signed, "Next")!).ToArray();
    int[] expected = raws.Select(x => (int)x == int.MinValue ? int.MaxValue : Math.Abs((int)x)).ToArray();
    Check("next/absolute-signed-not-mask", actual.SequenceEqual(expected), new { raws, actual });
}
{
    object rng = New(10), integers = New(10);
    int[] expected = Enumerable.Range(0, 20).Select(_ => (int)Call(integers, "Next")! % 7 + 3).ToArray();
    int[] actual = Enumerable.Range(0, 20).Select(_ => (int)Call(rng, "Next", 3, 10)!).ToArray();
    Check("range/modulo", actual.SequenceEqual(expected) && Count(rng) == 20, actual);
}
{
    object rng = New(33), integers = New(33);
    double[] actual = Enumerable.Range(0, 10).Select(_ => (double)Call(rng, "NextDouble")!).ToArray();
    double[] expected = Enumerable.Range(0, 10).Select(_ => (double)((float)(int)Call(integers, "Next")! * 4.6566128730773926e-10f)).ToArray();
    Check("double/single-precision-intermediate", actual.SequenceEqual(expected), actual);
}
{
    object rng = New(77), reference = New(77);
    float[] actual = Enumerable.Range(0, 10).Select(_ => (float)Call(rng, "NextFloat", .125f, 1.275f)!).ToArray();
    float[] expected = Enumerable.Range(0, 10).Select(_ => (float)(int)Call(reference, "Next", 125, 1275)! / 1000f).ToArray();
    Check("float/millisteps", actual.SequenceEqual(expected), actual);
}
{
    object rng = New(101), doubles = New(101);
    byte[] actual = new byte[16];
    Call(rng, "NextBytes", actual);
    // Original IL uses rem, not mul. Preserve that observed behavior.
    byte[] expected = Enumerable.Range(0, 16).Select(_ => (byte)((double)Call(doubles, "NextDouble")! % 256.0)).ToArray();
    Check("bytes/double-remainder-256", actual.SequenceEqual(expected) && Count(rng) == 16,
        new { bytes = actual.Select(b => (int)b).ToArray(), counter = Count(rng) });
}
{
    object rng = New(123); Draw(rng, 700);
    object clone = Activator.CreateInstance(type, rng)!;
    Check("copy-constructor/count", Count(clone) == 700, Count(clone));
    Check("copy-constructor/next-block", Draw(rng, 40).SequenceEqual(Draw(clone, 40)), Count(rng));
    object copy = New(9); Call(copy, "Copy", rng);
    Check("copy/seed-counter", (int)Call(copy, "get_InitialSeed")! == 123 && Count(copy) == Count(rng), Count(copy));
    Check("copy/next-block", Draw(rng, 40).SequenceEqual(Draw(copy, 40)), Count(copy));
}
{
    object rng = New(123); Draw(rng, 20);
    Call(rng, "SetToNewSeededPosition", 123, (uint)3);
    object expected = New(123); Draw(expected, 3);
    Check("rewind/same-seed", Count(rng) == 3 && Draw(rng, 20).SequenceEqual(Draw(expected, 20)), Count(rng));
    Call(rng, "SetToNewSeededPosition", 55, (uint)1000);
    expected = New(55); Draw(expected, 1000);
    Check("restore/new-seed-large-position", Count(rng) == 1000 && Draw(rng, 20).SequenceEqual(Draw(expected, 20)), Count(rng));
}
{
    object a = New(17), b = New(17);
    uint[] first = Draw(a, 1248), second = Draw(b, 1248);
    Check("two-twist-boundaries/deterministic", first.SequenceEqual(second) && Count(a) == 1248,
        new { around624 = first.Skip(620).Take(10).ToArray(), around1248 = first.Skip(1238).Take(10).ToArray() });
}
foreach (var values in new[] { new object[] { -1 }, new object[] { 3, 2 }, new object[] { int.MinValue, int.MaxValue } })
{
    bool rejected = false;
    try { Call(New(1), "Next", values); }
    catch (TargetInvocationException ex) when (ex.InnerException is ArgumentOutOfRangeException) { rejected = true; }
    Check("invalid-range/" + string.Join(",", values), rejected, new { rejected, messageDecodersStubbed = true });
}
var report = new { sourceSha256 = manifest.RootElement.GetProperty("sourceSha256").GetString(), extractSha256 = Hash(dll),
    copiedMethods = 23, checks = observations.Count, passed = observations.Count - failures, failed = failures,
    vectors, observations,
    scope = "Executed exact copied seeded RNG bodies. Four exception-message decoders return default(T), so exception text is not verified. Default time seed, original module initializer, Unity, gameplay, shuffles and timeout action chains excluded." };
File.WriteAllText(Path.Combine(evidence, "beta-rng-fixtures.json"), JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine($"Copied RNG IL checks: {observations.Count - failures}/{observations.Count}");
return failures == 0 ? 0 : 1;
