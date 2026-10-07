# Gwent Beta Classic 0.3.0 TEST 4 (stage 107): test3 + mandatory Beta targets (Warrior, Navigator, Hound frost) and request input logging.
# Run:  powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage107.ps1
# Test build only; the 0.3.0 release will be built as a later stage (stages freeze after packaging).
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location 'D:\w3mod'
$Stage = 107; $Version = '0.3.0-test4'
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

# 0. Menu resources must carry the vanilla Gwent pause (idempotent, fail-closed).
Step 'menu pause check' @('tools/ui/set_menu_pause.py',
    'GwentB/myproject1/workspace/betagwent/betagwent_board.menu',
    'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4gwint_game.menu',
    'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4deck_builder.menu')

# 0b. Packaging baselines (release87/89 were deleted on 07.10.2026): restore from shipped archives.
Step 'restore build base' @('tools/restore_build_base105.py')

# 1. Current game scripts
Step 'prepare scripts' @('tools/ui/prepare_board_scripts.py')

# 2. RU compile
Step 'RU compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}ru-$Run",
    '--patch', 'BetaGwent/build/board-patch', '--timeout', '240', '--terms-already-accepted')

# 3-4. RU presentation -> RU package (package right after its own menus)
Step 'RU presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
if ((MenusOf 'ru') -ne 3) { throw "stage$Stage-completion.json: expected 3 RU menus" }
Step 'RU package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'ru',
    '--compiled', "BetaGwent/build/board-compile${Stage}ru-$Run")

# 5-7. EN presentation (+ localization) -> EN compile -> EN package
Step 'EN presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'en')
if ((MenusOf 'en') -ne 3) { throw "stage$Stage-completion.json: expected 3 EN menus" }
Step 'EN compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}en-$Run",
    '--patch', "BetaGwent/build/stage$Stage/en/en-source/scripts", '--timeout', '240', '--terms-already-accepted')
Step 'EN package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'en',
    '--compiled', "BetaGwent/build/board-compile${Stage}en-$Run")

# EN presentation runs last: restore RU menus into the REDkit project (development default).
Step 'RU presentation (restore project)' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
Write-Host "Done: BetaGwent\release\GwentBetaClassic-$Version-RU.zip and -EN.zip" -ForegroundColor Green
