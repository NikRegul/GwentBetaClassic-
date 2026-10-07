param([int]$Stage = 108, [string]$Version = '0.3.0')
# Resume a test build after a failed/hung RU package step (default: stage 108, 0.3.0-test5).
# Reuses the last RU compile (board-compile<stage>ru-*), then runs RU package and the EN half.
# Run:  powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Resume-Stage.ps1
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location 'D:\w3mod'
$Run = Get-Date -Format 'MMddHHmm'

function Step([string]$Title, [string[]]$Arguments) {
    Write-Host "=== $Title" -ForegroundColor Cyan
    & python -X utf8 @Arguments
    if ($LASTEXITCODE -ne 0) { throw "FAILED: $Title (exit $LASTEXITCODE)" }
}
function MenusOf([string]$Lang) {
    $r = Get-Content "docs\evidence\stage$Stage-completion.json" -Raw | ConvertFrom-Json
    return @($r.menus | Where-Object { $_.language -eq $Lang }).Count
}

# A timed-out wcc_lite can survive and hold the cook database.
Get-Process wcc_lite -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# wcc jobs refuse existing job folders: park the previous attempt (never deleted).
foreach ($lang in @('ru','en')) {
    $base = "BetaGwent\build\release$Stage\$lang"
    foreach ($sub in @('jobs','cooked')) {
        $path = Join-Path $base $sub
        if (Test-Path $path) { Move-Item $path (Join-Path $base "$sub-attempt-$Run") }
    }
}

$ru = Get-ChildItem 'BetaGwent\build' -Directory -Filter "board-compile${Stage}ru-*" |
      Where-Object { $_.Name -ne "board-compile${Stage}ru-final" -and (Test-Path (Join-Path $_.FullName 'result.json')) } |
      Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $ru) { throw 'No RU compile found: run Build-Stage108.ps1' }
Write-Host "Using RU compile $($ru.Name)" -ForegroundColor Yellow
if ((MenusOf 'ru') -ne 3) { throw "stage$Stage-completion.json: expected 3 RU menus" }
Step 'RU package (resume)' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'ru',
    '--compiled', "BetaGwent/build/$($ru.Name)")

Step 'EN presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'en')
if ((MenusOf 'en') -ne 3) { throw "stage$Stage-completion.json: expected 3 EN menus" }
Step 'EN compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}en-$Run",
    '--patch', "BetaGwent/build/stage$Stage/en/en-source/scripts", '--timeout', '300', '--terms-already-accepted')
Step 'EN package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'en',
    '--compiled', "BetaGwent/build/board-compile${Stage}en-$Run")
Step 'RU presentation (restore project)' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
Write-Host "Done: BetaGwent\release\GwentBetaClassic-$Version-RU.zip and -EN.zip" -ForegroundColor Green
