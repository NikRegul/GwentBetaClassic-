# Repeatable acceptance run. This never changes game scripts or installs a policy.
[CmdletBinding()]
param([string]$Baseline='BetaGwent/training/stage118-check/snapshot',
      [string]$Candidate='', [ValidateRange(1,10000)][int]$Cycles=1,
      [int]$Seed=119, [string]$Output='')
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$OutputEncoding=[Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING='utf-8'
if(-not $Output){$Output=Join-Path $Root ('BetaGwent/training/comparison-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))}
$Output=[IO.Path]::GetFullPath($Output)
if(Test-Path -LiteralPath (Join-Path $Output 'report.json')){throw 'Use a new output folder.'}
if(-not $Candidate){
    $Candidate=Join-Path $Output 'candidate'
    & python -X utf8 tools/ai/gen_clone.py
    if($LASTEXITCODE -ne 0){throw 'Clone generation failed.'}
    & python -X utf8 tools/ai/snapshot.py $Candidate
    if($LASTEXITCODE -ne 0){throw 'Candidate snapshot failed.'}
}
$BaselineOutput=Join-Path $Output 'baseline'
& python -X utf8 tools/ai/prepare_comparison115.py $Candidate $Baseline $BaselineOutput
if($LASTEXITCODE -ne 0){throw 'Baseline preparation failed.'}
& node tools/ai/compare119.js $Candidate $BaselineOutput $Output $Cycles $Seed
if($LASTEXITCODE -ne 0){throw "Comparison has failures: $Output/errors. A failed run is not a strength verdict."}
Write-Host "Report: $Output/REPORT.md; table: $Output/archetypes.csv; replays: $Output/matches"
