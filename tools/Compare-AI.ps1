# Compare immutable AI snapshots; never train, install or modify game scripts.
[CmdletBinding()]
param(
    [string]$Baseline='BetaGwent/training/stage120-release/snapshot',
    [string]$Candidate='BetaGwent/training/stage121-release/snapshot',
    [ValidateRange(1,10000)][int]$Cycles=10,
    [int]$Seed=422,
    [string]$Output='',
    [string]$BaselineLabel='0.4.1',
    [string]$CandidateLabel='0.4.2',
    [ValidateRange(0,1840000)][int]$MaxGames=0,
    [switch]$Resume,
    [switch]$PrepareOnly
)
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
function AbsolutePath([string]$Value) {
    if([IO.Path]::IsPathRooted($Value)){return [IO.Path]::GetFullPath($Value)}
    return [IO.Path]::GetFullPath((Join-Path $Root $Value))
}
Get-Command python,node -ErrorAction Stop | Out-Null
if($Resume -and -not $Output){throw 'Resume requires the original -Output folder.'}
if(-not $Output){$Output=Join-Path $Root ('BetaGwent/training/comparison-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))}
$Output=AbsolutePath $Output
if(-not $Resume -and (Test-Path -LiteralPath $Output) -and (Get-ChildItem -LiteralPath $Output -Force | Select-Object -First 1)) {
    throw 'Use an empty output folder, or -Resume with an existing comparison.'
}
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$lock=$null
Push-Location -LiteralPath $Root
try {
    $lock=[IO.File]::Open((Join-Path $Output 'run.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
    $candidateCopy=Join-Path $Output 'candidate'
    $baselineCopy=Join-Path $Output 'baseline'
    if(-not $Resume) {
        if($Candidate -eq 'current') {
            & python -X utf8 tools/ai/snapshot.py $candidateCopy
            if($LASTEXITCODE -ne 0){throw 'Candidate snapshot failed.'}
        } else {
            $candidateSource=AbsolutePath $Candidate
            if(-not (Test-Path -LiteralPath (Join-Path $candidateSource 'manifest.json'))){throw "Snapshot not found: $candidateSource"}
            Copy-Item -LiteralPath $candidateSource -Destination $candidateCopy -Recurse
        }
        $baselineSource=AbsolutePath $Baseline
        & python -X utf8 tools/ai/prepare_comparison115.py $candidateCopy $baselineSource $baselineCopy
        if($LASTEXITCODE -ne 0){throw 'Baseline preparation failed; check snapshot integrity and compatibility.'}
        Copy-Item -LiteralPath (Join-Path $Root 'data/beta924/ai/researched115.json') -Destination (Join-Path $Output 'profiles.json')
        foreach($name in @('compare_ai.js','comparison_bridge119.js','replay119.js')) {
            Copy-Item -LiteralPath (Join-Path $Root "tools/ai/$name") -Destination (Join-Path $Output $name)
        }
        $config=[ordered]@{schema=1;baseline=$baselineSource;candidate=$Candidate;baselineLabel=$BaselineLabel;candidateLabel=$CandidateLabel;cycles=$Cycles;seed=$Seed}
        [IO.File]::WriteAllText((Join-Path $Output 'run.json'),($config|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
    }
    if(-not (Test-Path -LiteralPath (Join-Path $Output 'run.json'))){throw 'No prepared run.json; start a new comparison.'}
    $saved=Get-Content -LiteralPath (Join-Path $Output 'run.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Host "Comparison: $($saved.candidateLabel) vs $($saved.baselineLabel); $($saved.cycles*184) games. Output: $Output"
    if(-not $PrepareOnly) {
        $nodeArgs=@((Join-Path $Output 'compare_ai.js'),$Output)
        if($Resume -and (Test-Path -LiteralPath (Join-Path $Output 'report.json'))){$nodeArgs+='--resume'}
        if($MaxGames -gt 0){$nodeArgs+=@('--max-games',"$MaxGames")}
        & node @nodeArgs 2>&1 | Tee-Object -FilePath (Join-Path $Output 'compare.log') -Append
        if($LASTEXITCODE -ne 0){throw "Comparison has errors. See $Output/errors and REPORT_RU.md; do not use it as a strength verdict."}
        Write-Host "Report: $Output/REPORT_RU.md; per-deck statistics: $Output/archetypes.csv"
    }
} finally {
    if($lock){$lock.Dispose()}
    Pop-Location
}
