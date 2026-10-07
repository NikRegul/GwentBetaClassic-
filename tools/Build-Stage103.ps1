# Gwent Beta Classic 0.2.9 (stage 103): world pause in menu resources + original Beta board layout.
# Run:  powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage103.ps1
# Same flow as the 0.2.8 build, new stage/version (0.2.8 archives and release102 stay untouched).
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location 'D:\w3mod'
$Stage = 104; $Version = '0.2.10'

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

# 1. Current game scripts
Step 'prepare scripts' @('tools/ui/prepare_board_scripts.py')

# 2. RU compile
Step 'RU compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}ru-final",
    '--patch', 'BetaGwent/build/board-patch', '--timeout', '120', '--terms-already-accepted')

# 3-4. RU presentation -> RU package (package right after its own menus)
Step 'RU presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
if ((MenusOf 'ru') -ne 3) { throw "stage$Stage-completion.json: expected 3 RU menus" }
Step 'RU package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'ru',
    '--compiled', "BetaGwent/build/board-compile${Stage}ru-final")

# 5-7. EN presentation (+ localization) -> EN compile -> EN package
Step 'EN presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'en')
if ((MenusOf 'en') -ne 3) { throw "stage$Stage-completion.json: expected 3 EN menus" }
Step 'EN compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}en-final",
    '--patch', "BetaGwent/build/stage$Stage/en/en-source/scripts", '--timeout', '120', '--terms-already-accepted')
Step 'EN package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'en',
    '--compiled', "BetaGwent/build/board-compile${Stage}en-final")

# EN presentation runs last: restore RU menus into the REDkit project (development default).
Step 'RU presentation (restore project)' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
Write-Host "Done: BetaGwent\release\GwentBetaClassic-$Version-RU.zip and -EN.zip" -ForegroundColor Green
