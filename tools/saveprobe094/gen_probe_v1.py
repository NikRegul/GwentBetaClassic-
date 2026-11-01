"""Generates the save-capacity probe script (Next-Gen 4.0+/5.x annotations)."""
from pathlib import Path
NS, NA, NSTR, STAGES = 64, 16, 16, 5
L = []
w = L.append
w("// Gwent Beta Classic: save capacity probe (diagnostic only, no gameplay).")
w("// Each load: report what came back from the save, then fill the next stage.")
w("// Declaration order matters: small ints, then arrays, mid marker, strings, end marker.")
w("@addField(W3PlayerWitcher)\nprivate saved var bgspStage : int;")
for j in range(NS): w(f"@addField(W3PlayerWitcher)\nprivate saved var bgspN{j:02d} : int;")
for k in range(NA): w(f"@addField(W3PlayerWitcher)\nprivate saved var bgspA{k:02d} : array<int>;")
w("@addField(W3PlayerWitcher)\nprivate saved var bgspMid : int;")
w("@addField(W3PlayerWitcher)\nprivate saved var bgspStr : array<string>;")
w("@addField(W3PlayerWitcher)\nprivate saved var bgspEnd : int;")
# small get/set
w("@addMethod(W3PlayerWitcher)\nprivate function BgspGetSmall(j : int) : int\n{\n    switch (j)\n    {")
for j in range(NS): w(f"        case {j}: return bgspN{j:02d};")
w("    }\n    return -1;\n}")
w("@addMethod(W3PlayerWitcher)\nprivate function BgspSetSmall(j : int, v : int)\n{\n    switch (j)\n    {")
for j in range(NS): w(f"        case {j}: bgspN{j:02d} = v; break;")
w("    }\n}")
w("@addMethod(W3PlayerWitcher)\nprivate function BgspGetArr(k : int, out a : array<int>)\n{\n    switch (k)\n    {")
for k in range(NA): w(f"        case {k}: a = bgspA{k:02d}; break;")
w("    }\n}")
w("@addMethod(W3PlayerWitcher)\nprivate function BgspSetArr(k : int, a : array<int>)\n{\n    switch (k)\n    {")
for k in range(NA): w(f"        case {k}: bgspA{k:02d} = a; break;")
w("    }\n}")
w(f"""function BgspPow4(e : int) : int
{{
    var r, i : int;
    r = 1; for (i = 0; i < e; i += 1) r = r * 4;
    return r;
}}
// Ints per array: 64, 256, 1024, 4096, 16384 (x{NA} arrays).
function BgspArraySize(s : int) : int {{ return 64 * BgspPow4(s - 1); }}
// Facts: 100, 400, 1600, 6400, 25600.
function BgspFactCount(s : int) : int {{ return 100 * BgspPow4(Min(s, 5) - 1); }}
function BgspVal(s : int, k : int, i : int) : int {{ return (s * 7 + k * 1000003 + i * 7919) % 2147483647; }}
function BgspText(s : int, k : int) : string {{ return "bgsp-" + s + "-" + k + "-abcdefghijklmnopqrstuvwxyz"; }}
function BgspLog(m : string) {{ LogChannel('BetaGwent', "SAVEPROBE " + m); }}

@addMethod(W3PlayerWitcher)
private function BgspFill(s : int)
{{
    var a : array<int>; var k, i, n, f : int;
    n = BgspArraySize(s); f = BgspFactCount(s);
    for (i = 0; i < {NS}; i += 1) BgspSetSmall(i, 100000 * s + i);
    for (k = 0; k < {NA}; k += 1)
    {{
        a.Clear();
        for (i = 0; i < n; i += 1) a.PushBack(BgspVal(s, k, i));
        BgspSetArr(k, a);
    }}
    bgspMid = 777000 + s;
    bgspStr.Clear(); for (k = 0; k < {NSTR}; k += 1) bgspStr.PushBack(BgspText(s, k));
    bgspEnd = 999000 + s;
    for (i = 0; i < f; i += 1) FactsSet("bgsp_f_" + i, s * 1000000 + i + 1);
    FactsSet("bgsp_f_end", s);
    bgspStage = s;
    BgspLog("FILLED stage=" + s + " perArray=" + n + " totalInts=" + ({NA} * n) + " facts=" + f
        + " -> now make a MANUAL save, then load that save");
}}

// Returns true when everything written for stage s came back intact.
@addMethod(W3PlayerWitcher)
private function BgspReport(s : int) : bool
{{
    var a : array<int>; var k, i, n, f, smallOk, firstSmallBad, arraysOk, firstBadArray, intactInts, strOk, factsOk, firstFactBad, bad : int;
    var ok : bool;
    n = BgspArraySize(s); f = BgspFactCount(s);
    firstSmallBad = -1; firstBadArray = -1; firstFactBad = -1;
    smallOk = 0; arraysOk = 0; intactInts = 0; strOk = 0; factsOk = 0;
    for (i = 0; i < {NS}; i += 1)
    {{
        if (BgspGetSmall(i) == 100000 * s + i) smallOk += 1;
        else if (firstSmallBad < 0) firstSmallBad = i;
    }}
    for (k = 0; k < {NA}; k += 1)
    {{
        BgspGetArr(k, a); bad = -1;
        if (a.Size() != n) bad = Min(a.Size(), n);
        for (i = 0; i < Min(a.Size(), n) && bad < 0; i += 1) if (a[i] != BgspVal(s, k, i)) bad = i;
        if (bad < 0) {{ arraysOk += 1; intactInts += n; }}
        else
        {{
            if (firstBadArray < 0) firstBadArray = k;
            BgspLog("ARRAY A" + k + " size=" + a.Size() + "/" + n + " firstBad=" + bad);
        }}
    }}
    for (k = 0; k < bgspStr.Size(); k += 1) if (bgspStr[k] == BgspText(s, k)) strOk += 1;
    for (i = 0; i < f; i += 1)
    {{
        if (FactsQueryLatestValue("bgsp_f_" + i) == s * 1000000 + i + 1) factsOk += 1;
        else if (firstFactBad < 0) firstFactBad = i;
    }}
    ok = smallOk == {NS} && arraysOk == {NA} && bgspMid == 777000 + s && strOk == {NSTR} && bgspEnd == 999000 + s && factsOk == f;
    BgspLog("RESULT stage=" + s + " ok=" + ok + " perArray=" + n
        + " small=" + smallOk + "/{NS} firstSmallBad=" + firstSmallBad
        + " arrays=" + arraysOk + "/{NA} firstBadArray=" + firstBadArray + " intactInts=" + intactInts + "/" + ({NA} * n)
        + " mid=" + (bgspMid == 777000 + s) + " strings=" + strOk + "/{NSTR} end=" + (bgspEnd == 999000 + s)
        + " facts=" + factsOk + "/" + f + " firstFactBad=" + firstFactBad + " factEnd=" + FactsQueryLatestValue("bgsp_f_end"));
    return ok;
}}

@addMethod(W3PlayerWitcher)
private function BgspRun()
{{
    var found : bool; var k : int; var a : array<int>;
    found = false;
    if (bgspStage <= 0)
    {{
        for (k = 0; k < {NA}; k += 1) {{ BgspGetArr(k, a); if (a.Size() > 0) found = true; }}
        if (found || bgspEnd != 0 || FactsQueryLatestValue("bgsp_f_end") > 0)
            BgspLog("ANOMALY stage field lost: end=" + bgspEnd + " factEnd=" + FactsQueryLatestValue("bgsp_f_end"));
        else BgspLog("START no probe data in this save");
        BgspFill(1); return;
    }}
    if (bgspStage > {STAGES}) {{ BgspLog("ANOMALY stage=" + bgspStage); return; }}
    if (!BgspReport(bgspStage))
    {{
        BgspLog("LOSS at stage=" + bgspStage + " -> refilled the same stage; save and load once more to confirm");
        BgspFill(bgspStage); return;
    }}
    if (bgspStage == {STAGES}) {{ BgspLog("DONE all {STAGES} stages intact"); return; }}
    BgspFill(bgspStage + 1);
}}

@wrapMethod(W3PlayerWitcher)
function OnSpawned(spawnData : SEntitySpawnData)
{{
    wrappedMethod(spawnData);
    BgspRun();
}}""")
out = Path("mod/modBetaGwentSaveProbe/content/scripts/local/betaGwentSaveProbe.ws")
out.write_text("\n".join(L) + "\n", encoding="ascii", newline="\r\n")
print(out, out.stat().st_size)
