# Gwent Beta Classic 0.3.3: validated RU/EN native menus and current gameplay sources.
# Run:  powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage112.ps1
# Release build of 0.3.3.
param(
    [ValidateSet('ru','en','both')][string]$Language = 'both',
    [string]$KegVideo = ''
)
$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = 'utf-8'
Set-Location 'D:\w3mod'
$Stage = 112; $Version = '0.3.3'
# Fresh compile directories per run (the compiler refuses to reuse an output folder).
$Run = Get-Date -Format 'MMddHHmmss'

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
    if (Test-Path -LiteralPath $dir) {
        $resolved = (Resolve-Path -LiteralPath $dir).Path
        $expected = [IO.Path]::GetFullPath((Join-Path 'D:\w3mod' $dir))
        if ($resolved -ne $expected -or -not $resolved.StartsWith('D:\w3mod\BetaGwent\build\release112\')) { throw 'Unsafe package path' }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
    # Test builds reuse the version number: move the previous archive aside instead of failing.
    $zip = "BetaGwent\release\GwentBetaClassic-$Version-$($Lang.ToUpper()).zip"
    if (Test-Path $zip) { $old = "BetaGwent\release\old"; New-Item -ItemType Directory -Force $old | Out-Null; Move-Item -Force $zip "$old\GwentBetaClassic-$Version-$($Lang.ToUpper())-$Run.zip"; Write-Host "Previous archive moved to $old" }
}

# A shared exporter directory cannot be used by simultaneous builds.
$lockPath = 'D:\w3mod\BetaGwent\build\stage112-build.lock'
$lock = [IO.File]::Open($lockPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
function RestoreRussianProject {
    $file = 'docs/evidence/stage112-completion.json'
    if (-not (Test-Path -LiteralPath $file)) { return }
    $report = Get-Content -LiteralPath $file -Raw -Encoding UTF8 | ConvertFrom-Json
    $allowed = @('betagwent_board.redswf','betagwent_npc00.redswf','betagwent_decks.redswf','betagwent_kegop.redswf')
    foreach ($menu in @($report.menus | Where-Object { $_.language -eq 'ru' })) {
        $source = [IO.Path]::GetFullPath($menu.resource)
        $name = [IO.Path]::GetFileName($source)
        if (-not $source.StartsWith('D:\w3mod\BetaGwent\build\stage112\ru\resources\') -or $name -notin $allowed) { throw 'Unsafe resource path' }
        if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower() -ne $menu.sha256.ToLower()) { throw 'RU resource checksum mismatch' }
        Copy-Item -LiteralPath $source -Destination (Join-Path 'GwentB/myproject1/workspace/betagwent' $name) -Force
    }
}
try {
# The native Arabic text encoder needs this local build font, not a shipped asset.
if (-not (Test-Path -LiteralPath 'D:\GOG Galaxy\Games\The Witcher 3 REDkit\r4data\tmp\arial.ttf')) {
    throw 'Missing REDkit build font: copy C:\Windows\Fonts\arial.ttf to REDkit\r4data\tmp\arial.ttf. See docs/BUILD_033_RU.md.'
}
# Original extracted assets are inputs. An optional video re-extracts the 48 frames.
if ($KegVideo) {
    Step 'capture keg frames' @('tools/ui/extract_keg111.py', $KegVideo)
    Step 'updated keg atlas' @('tools/ui/build_keg109.py')
}
Step 'text metrics' @('tools/ui/build_text_metrics112.py')
# Keg textures unchanged from 0.3.2.
Step 'full catalog' @('tools/build_full_catalog.py')
Step 'AI clone' @('tools/ai/gen_clone.py')

# 0. Menu resources must carry the vanilla Gwent pause (idempotent, fail-closed).
Step 'menu pause check' @('tools/ui/set_menu_pause.py',
    'GwentB/myproject1/workspace/betagwent/betagwent_board.menu',
    'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4gwint_game.menu',
    'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4deck_builder.menu',
    'GwentB/myproject1/workspace/betagwent/betagwent_kegop.menu')

# 0b. Packaging baselines (release87/89 were deleted on 07.10.2026): restore from shipped archives.
Step 'restore build base' @('tools/restore_build_base105.py')

# 0c. Stage 109: troll keg-opening lines into both sound banks (licensed Wwise 2023.1 console).
# Reuse the licensed, validated RU/EN banks from 0.3.2.

# 1. Current game scripts
Step 'prepare scripts' @('tools/ui/prepare_board_scripts.py')

# 2. RU compile
if ($Language -ne 'en') {
Step 'RU compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}ru-$Run",
    '--patch', 'BetaGwent/build/board-patch', '--timeout', '300', '--terms-already-accepted')

# 3-4. RU presentation -> RU package (package right after its own menus)
Step 'RU presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'ru')
if ((MenusOf 'ru') -ne 4) { throw "stage$Stage-completion.json: expected 4 RU menus" }
FreshPackage 'ru'
Step 'RU package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'ru',
    '--compiled', "BetaGwent/build/board-compile${Stage}ru-$Run")

}

# 5-7. EN presentation (+ localization) -> EN compile -> EN package
if ($Language -ne 'ru') {
Step 'EN presentation' @('tools/build_presentation94.py', '--stage', "$Stage", '--language', 'en')
if ((MenusOf 'en') -ne 4) { throw "stage$Stage-completion.json: expected 4 EN menus" }
Step 'EN compile' @('tools/recon/run_redkit_compile.py', '--out', "BetaGwent/build/board-compile${Stage}en-$Run",
    '--patch', "BetaGwent/build/stage$Stage/en/en-source/scripts", '--timeout', '300', '--terms-already-accepted')
FreshPackage 'en'
Step 'EN package' @('tools/package_presentation94.py', '--stage', "$Stage", '--version', $Version, '--language', 'en',
    '--compiled', "BetaGwent/build/board-compile${Stage}en-$Run")

}
Write-Host "Done: requested $Version archive(s) in D:\w3mod\BetaGwent\release" -ForegroundColor Green
} finally {
    try { RestoreRussianProject } finally { $lock.Dispose() }
}
