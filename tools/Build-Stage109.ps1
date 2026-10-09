# Gwent Beta Classic 0.3.1 (stage 109): scraps (craft/mill), duplicates, economy, keg strings recooked, AI deck thinning.
# Run:  powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage109.ps1
# Release build of 0.3.1.
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location 'D:\w3mod'
$Stage = 109; $Version = '0.3.1'
# Fresh compile directories per run (the compiler refuses to reuse an output folder).
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

# Package workspaces freeze their scripts on first packaging; drop the stale one so new scripts get packaged.
function FreshPackage([string]$Lang) {
    $dir = "BetaGwent\build\release$Stage\$Lang"
    if (Test-Path $dir) { Write-Host "Removing stale $dir"; Remove-Item -Recurse -Force $dir }
    # Test builds reuse the version number: move the previous archive aside instead of failing.
    $zip = "BetaGwent\release\GwentBetaClassic-$Version-$($Lang.ToUpper()).zip"
    if (Test-Path $zip) { $old = "BetaGwent\release\old"; New-Item -ItemType Directory -Force $old | Out-Null; Move-Item -Force $zip "$old\GwentBetaClassic-$Version-$($Lang.ToUpper())-$Run.zip"; Write-Host "Previous archive moved to $old" }
}

# 0. Menu resources must carry the vanilla Gwent pause (idempotent, fail-closed).
Step 'menu pause check' @('tools/ui/set_menu_pause.py',
    'GwentB/myproject1/workspace/betagwent/betagwent_board.menu',
    'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4gwint_game.menu',
    'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4deck_builder.menu',
    'GwentB/myproject1/workspace/betagwent/betagwent_kegop.menu')

# 0b. Packaging baselines (release87/89 were deleted on 07.10.2026): restore from shipped archives.
Step 'restore build base' @('tools/restore_build_base105.py')

# 0c. Stage 109: troll keg-opening lines into both sound banks (licensed Wwise 2023.1 console).
Step 'keg audio' @('tools/ui/add_keg_audio109.py')

# 1. Current game scripts
Step 'prepare scripts' @('tools/ui/prepare_board_scripts.py')

# 2. RU compile
Step 'RU compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}ru-$Run",
    '--patch', 'BetaGwent/build/board-patch', '--timeout', '300', '--terms-already-accepted')

# 3-4. RU presentation -> RU package (package right after its own menus)
Step 'RU presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
if ((MenusOf 'ru') -ne 4) { throw "stage$Stage-completion.json: expected 4 RU menus" }
FreshPackage 'ru'
Step 'RU package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'ru',
    '--compiled', "BetaGwent/build/board-compile${Stage}ru-$Run")

# 5-7. EN presentation (+ localization) -> EN compile -> EN package
Step 'EN presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'en')
if ((MenusOf 'en') -ne 4) { throw "stage$Stage-completion.json: expected 4 EN menus" }
Step 'EN compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}en-$Run",
    '--patch', "BetaGwent/build/stage$Stage/en/en-source/scripts", '--timeout', '300', '--terms-already-accepted')
FreshPackage 'en'
Step 'EN package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'en',
    '--compiled', "BetaGwent/build/board-compile${Stage}en-$Run")

# EN presentation runs last: restore RU menus into the REDkit project (development default).
Step 'RU presentation (restore project)' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
Write-Host "Done: BetaGwent\release\GwentBetaClassic-$Version-RU.zip and -EN.zip" -ForegroundColor Green
