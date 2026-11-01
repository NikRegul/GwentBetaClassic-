"""Save probe v4 (Next-Gen): load-time behaviour, no saving needed.
A: bgs3F00..F14 (in the v3 save, values 5000+i) declared WITHOUT 'saved'.
B: 50 empty saved dummies first, then bgs2N00..N41 (in the save, values 300000+i) as saved at positions 51+."""
from pathlib import Path
L = []; w = L.append
w("// Gwent Beta Classic save probe v4 (diagnostic only). Just load the latest v3 save.")
for j in range(50): w(f"@addField(W3PlayerWitcher)\nprivate saved var bgs4D{j:02d} : int;")
for j in range(42): w(f"@addField(W3PlayerWitcher)\nprivate saved var bgs2N{j:02d} : int;")
for j in range(15): w(f"@addField(W3PlayerWitcher)\nprivate var bgs3F{j:02d} : int;")
w("@addMethod(W3PlayerWitcher)\nprivate function Bgs4A(j : int) : int\n{\n    switch (j)\n    {")
for j in range(15): w(f"        case {j}: return bgs3F{j:02d};")
w("    }\n    return -1;\n}")
w("@addMethod(W3PlayerWitcher)\nprivate function Bgs4B(j : int) : int\n{\n    switch (j)\n    {")
for j in range(42): w(f"        case {j}: return bgs2N{j:02d};")
w("    }\n    return -1;\n}")
w("""function Bgs4Log(m : string) { LogChannel('BetaGwent', "SAVEPROBE4 " + m); }
@addMethod(W3PlayerWitcher)
private function Bgs4Run()
{
    var i, a, b, b2 : int; var sample : string;
    a = 0; b = 0; b2 = 0; sample = "";
    for (i = 0; i < 15; i += 1) if (Bgs4A(i) == 5000 + i) a += 1;
    for (i = 0; i < 42; i += 1)
    {
        if (Bgs4B(i) == 300000 + i) b += 1;
        if (Bgs4B(i) != 0) b2 += 1;
    }
    sample = " A0=" + Bgs4A(0) + " B0=" + Bgs4B(0) + " B41=" + Bgs4B(41);
    Bgs4Log("RESULT nonSavedRead=" + a + "/15 savedAfter50=" + b + "/42 nonzeroB=" + b2 + sample);
}
@wrapMethod(W3PlayerWitcher)
function OnSpawned(spawnData : SEntitySpawnData)
{
    wrappedMethod(spawnData);
    Bgs4Run();
}""")
out = Path("mod/modBetaGwentSaveProbe/content/scripts/local/betaGwentSaveProbe.ws")
out.write_text("\n".join(L) + "\n", encoding="ascii", newline="\r\n")
print(out, out.stat().st_size)
