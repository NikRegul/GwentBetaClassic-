# Self-play training of the Beta Gwent AI on all 40 archetypes (headless, Node.js).
# Run:  powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\ai\Train-AI-JS.ps1 [-Generations 30] [-Pairs 200] [-Resume]
# Output: BetaGwent\training\js-<date>\ (summary.csv, gen-*.json, best.json, train.log).
# Send that folder (or train.log + best.json) back for analysis; apply with:
#   python tools\ai\apply_tunes.py BetaGwent\training\js-<date>\best.json
param([int]$Generations = 30, [int]$Pairs = 200, [int]$Strength = 4, [int]$Shards = 0, [string]$Output = '', [switch]$Resume)
$ErrorActionPreference = 'Stop'
Set-Location 'D:\w3mod'
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js not found. Install it once:  winget install OpenJS.NodeJS.LTS  (then open a new PowerShell window).'
}
if (-not $Output) { $Output = 'BetaGwent\training\js-' + (Get-Date -Format 'yyyy-MM-dd') }
New-Item -ItemType Directory -Force -Path $Output | Out-Null
New-Item -ItemType Directory -Force -Path 'BetaGwent\build\ai-js' | Out-Null
Write-Host '=== translating battle scripts (WS -> JS)' -ForegroundColor Cyan
& python -X utf8 tools/ai/gen_clone.py
if ($LASTEXITCODE -ne 0) { throw 'gen_clone failed' }
& python -X utf8 tools/ai/build_js.py BetaGwent/build/ai-js/rules.js
if ($LASTEXITCODE -ne 0) { throw 'build_js failed' }
$nodeArgs = @('tools/ai/jshost/train.js', '--rules', 'BetaGwent/build/ai-js/rules.js', '--out', $Output,
          '--generations', "$Generations", '--pairs', "$Pairs", '--strength', "$Strength")
if ($Shards -gt 0) { $nodeArgs += @('--shards', "$Shards") }
if ($Resume) { $nodeArgs += '--resume' }
Write-Host "=== training ($Generations generations x $($Pairs*2) games), log: $Output\train.log" -ForegroundColor Cyan
& node @nodeArgs 2>&1 | Tee-Object -FilePath (Join-Path $Output 'train.log') -Append
if ($LASTEXITCODE -ne 0) { throw "training exited with $LASTEXITCODE" }
Write-Host "=== done. Best tunes: $Output\best.json" -ForegroundColor Green
