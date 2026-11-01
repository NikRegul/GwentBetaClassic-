"""Save probe v2 (Next-Gen): big array first, field-count limit, facts value/count limits."""
from pathlib import Path
NS = 64
VALUES = [1, 255, 256, 32767, 32768, 65535, 65536, 112103, 1000000, 16777216, 2147483647, -1, -32768]
L = []; w = L.append
w("// Gwent Beta Classic save probe v2 (diagnostic only). Order: stage, big array, strings, 64 small ints.")
w("@addField(W3PlayerWitcher)\nprivate saved var bgs2Stage : int;")
w("@addField(W3PlayerWitcher)\nprivate saved var bgs2Big : array<int>;")
w("@addField(W3PlayerWitcher)\nprivate saved var bgs2Str : array<string>;")
for j in range(NS): w(f"@addField(W3PlayerWitcher)\nprivate saved var bgs2N{j:02d} : int;")
w("@addMethod(W3PlayerWitcher)\nprivate function Bgs2GetSmall(j : int) : int\n{\n    switch (j)\n    {")
for j in range(NS): w(f"        case {j}: return bgs2N{j:02d};")
w("    }\n    return -1;\n}")
w("@addMethod(W3PlayerWitcher)\nprivate function Bgs2SetSmall(j : int, v : int)\n{\n    switch (j)\n    {")
for j in range(NS): w(f"        case {j}: bgs2N{j:02d} = v; break;")
w("    }\n}")
w("function Bgs2Value(k : int) : int\n{\n    switch (k)\n    {")
for k, v in enumerate(VALUES):
    w(f"        case {k}: return {v if v != -32768 else '0 - 32768'};" if v >= 0 or v == -32768 else f"        case {k}: return 0 - {-v};")
w("    }\n    return 0;\n}")
w(f"""// Big array: 1024, 16384, 262144 ints.
function Bgs2Size(s : int) : int {{ if (s == 1) return 1024; if (s == 2) return 16384; return 262144; }}
// Many small facts: 200, 1000, 5000.
function Bgs2FactCount(s : int) : int {{ if (s == 1) return 200; if (s == 2) return 1000; return 5000; }}
function Bgs2Val(s : int, i : int) : int {{ return (s * 7 + i * 7919) % 2147483647; }}
function Bgs2Log(m : string) {{ LogChannel('BetaGwent', "SAVEPROBE2 " + m); }}

@addMethod(W3PlayerWitcher)
private function Bgs2Fill(s : int)
{{
    var i, n : int;
    n = Bgs2Size(s);
    bgs2Big.Clear(); for (i = 0; i < n; i += 1) bgs2Big.PushBack(Bgs2Val(s, i));
    bgs2Str.Clear(); for (i = 0; i < 8; i += 1) bgs2Str.PushBack("bgs2-" + s + "-" + i + "-abcdefghijklmnopqrstuvwxyz");
    for (i = 0; i < {NS}; i += 1) Bgs2SetSmall(i, 100000 * s + i);
    for (i = 0; i < {len(VALUES)}; i += 1) FactsSet("bgs2_v_" + i, Bgs2Value(i));
    for (i = 0; i < Bgs2FactCount(s); i += 1) FactsSet("bgs2_c_" + i, 7);
    FactsSet("bgs2_end", s);
    bgs2Stage = s;
    Bgs2Log("FILLED stage=" + s + " big=" + n + " facts=" + Bgs2FactCount(s) + " -> MANUAL save to a new slot, then load it");
}}

@addMethod(W3PlayerWitcher)
private function Bgs2Report(s : int) : bool
{{
    var i, n, bad, smallOk, firstSmallBad, strOk, valuesOk, countOk, firstCountBad, got : int; var vals : string; var ok : bool;
    n = Bgs2Size(s); bad = -1; smallOk = 0; firstSmallBad = -1; strOk = 0; valuesOk = 0; countOk = 0; firstCountBad = -1; vals = "";
    if (bgs2Big.Size() != n) bad = Min(bgs2Big.Size(), n);
    for (i = 0; i < Min(bgs2Big.Size(), n) && bad < 0; i += 1) if (bgs2Big[i] != Bgs2Val(s, i)) bad = i;
    for (i = 0; i < bgs2Str.Size(); i += 1) if (bgs2Str[i] == "bgs2-" + s + "-" + i + "-abcdefghijklmnopqrstuvwxyz") strOk += 1;
    for (i = 0; i < {NS}; i += 1)
    {{
        if (Bgs2GetSmall(i) == 100000 * s + i) smallOk += 1;
        else if (firstSmallBad < 0) firstSmallBad = i;
    }}
    for (i = 0; i < {len(VALUES)}; i += 1)
    {{
        got = FactsQueryLatestValue("bgs2_v_" + i);
        if (got == Bgs2Value(i)) valuesOk += 1;
        vals += " " + Bgs2Value(i) + "->" + got;
    }}
    for (i = 0; i < Bgs2FactCount(s); i += 1)
    {{
        if (FactsQueryLatestValue("bgs2_c_" + i) == 7) countOk += 1;
        else if (firstCountBad < 0) firstCountBad = i;
    }}
    ok = bad < 0 && strOk == 8 && smallOk == {NS} && valuesOk == {len(VALUES)} && countOk == Bgs2FactCount(s);
    Bgs2Log("RESULT stage=" + s + " ok=" + ok + " big=" + bgs2Big.Size() + "/" + n + " bigFirstBad=" + bad
        + " strings=" + strOk + "/8 small=" + smallOk + "/{NS} firstSmallBad=" + firstSmallBad
        + " factCount=" + countOk + "/" + Bgs2FactCount(s) + " firstCountBad=" + firstCountBad + " factEnd=" + FactsQueryLatestValue("bgs2_end"));
    Bgs2Log("FACT_VALUES ok=" + valuesOk + "/{len(VALUES)}" + vals);
    return ok;
}}

@addMethod(W3PlayerWitcher)
private function Bgs2Run()
{{
    if (bgs2Stage <= 0)
    {{
        if (bgs2Big.Size() > 0 || FactsQueryLatestValue("bgs2_end") > 0) Bgs2Log("ANOMALY stage field lost");
        else Bgs2Log("START no probe data in this save");
        Bgs2Fill(1); return;
    }}
    if (bgs2Stage > 3) {{ Bgs2Log("ANOMALY stage=" + bgs2Stage); return; }}
    Bgs2Report(bgs2Stage);
    if (bgs2Stage == 3) {{ Bgs2Log("DONE"); return; }}
    Bgs2Fill(bgs2Stage + 1);
}}

@wrapMethod(W3PlayerWitcher)
function OnSpawned(spawnData : SEntitySpawnData)
{{
    wrappedMethod(spawnData);
    Bgs2Run();
}}""")
out = Path("mod/modBetaGwentSaveProbe/content/scripts/local/betaGwentSaveProbe.ws")
out.write_text("\n".join(L) + "\n", encoding="ascii", newline="\r\n")
print(out, out.stat().st_size)
