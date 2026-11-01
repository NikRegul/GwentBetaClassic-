"""Save probe v3 (Next-Gen): do non-saved fields and default-valued saved fields count toward the 45 limit?"""
from pathlib import Path
NX, NZ, NF = 20, 30, 40
L = []; w = L.append
w("// Gwent Beta Classic save probe v3 (diagnostic only).")
w("// Order: 20 non-saved ints (X), 30 saved ints left at 0 (Z), 40 saved ints filled (F).")
for j in range(NX): w(f"@addField(W3PlayerWitcher)\nprivate var bgs3X{j:02d} : int;")
for j in range(NZ): w(f"@addField(W3PlayerWitcher)\nprivate saved var bgs3Z{j:02d} : int;")
for j in range(NF): w(f"@addField(W3PlayerWitcher)\nprivate saved var bgs3F{j:02d} : int;")
w("@addMethod(W3PlayerWitcher)\nprivate function Bgs3Get(j : int) : int\n{\n    switch (j)\n    {")
for j in range(NF): w(f"        case {j}: return bgs3F{j:02d};")
w("    }\n    return -1;\n}")
w("@addMethod(W3PlayerWitcher)\nprivate function Bgs3Set(j : int, v : int)\n{\n    switch (j)\n    {")
for j in range(NF): w(f"        case {j}: bgs3F{j:02d} = v; break;")
w("    }\n}")
w(f"""function Bgs3Log(m : string) {{ LogChannel('BetaGwent', "SAVEPROBE3 " + m); }}
@addMethod(W3PlayerWitcher)
private function Bgs3Run()
{{
    var i, ok, first : int;
    ok = 0; first = -1;
    if (FactsQueryLatestValue("bgs3_filled") > 0)
    {{
        for (i = 0; i < {NF}; i += 1)
        {{
            if (Bgs3Get(i) == 5000 + i) ok += 1;
            else if (first < 0) first = i;
        }}
        // 40 = neither X nor Z counts; 25 = only X counts; 15 = only Z counts; 0 = both count.
        Bgs3Log("RESULT filled=" + ok + "/{NF} firstBad=" + first + " (40: X,Z free; 25: X counts; 15: Z counts; 0: both)");
    }}
    else Bgs3Log("START");
    for (i = 0; i < {NF}; i += 1) Bgs3Set(i, 5000 + i);
    FactsSet("bgs3_filled", 1);
    Bgs3Log("FILLED -> MANUAL save to a new slot, then load it");
}}
@wrapMethod(W3PlayerWitcher)
function OnSpawned(spawnData : SEntitySpawnData)
{{
    wrappedMethod(spawnData);
    Bgs3Run();
}}""")
out = Path("mod/modBetaGwentSaveProbe/content/scripts/local/betaGwentSaveProbe.ws")
out.write_text("\n".join(L) + "\n", encoding="ascii", newline="\r\n")
print(out, out.stat().st_size)
