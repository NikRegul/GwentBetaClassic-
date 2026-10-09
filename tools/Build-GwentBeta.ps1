# Editable build entry point for the current sources (Stage 119 / 0.4.0).
# powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-GwentBeta.ps1
[CmdletBinding()]
param(
    [ValidateSet('ru','en','both')][string]$Language = 'ru',
    [ValidatePattern('^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?$')][string]$Version = '0.4.0',
    [ValidateRange(113,999)][int]$Stage = 119,
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step = 'full',
    [string]$Compiled = '',
    [string]$KegVideo = '',
    [switch]$CheckAI
)
$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = 'utf-8'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$Run = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$Languages = if ($Language -eq 'both') { @('ru','en') } else { @($Language) }
$BuildRoot = Join-Path $Root 'BetaGwent\build'
$Evidence = Join-Path $Root 'docs\evidence'
$StateRoot = Join-Path $BuildRoot "stage$Stage\powershell"
New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null
$Transcript = Join-Path $StateRoot "$Run-$Step.log"

function PythonStep([string]$Title, [string[]]$Arguments) {
    Write-Host "=== $Title" -ForegroundColor Cyan
    & python -X utf8 @Arguments
    if ($LASTEXITCODE -ne 0) { throw "FAILED: $Title (exit $LASTEXITCODE). See $Transcript and docs\evidence." }
}
function StatePath([string]$Lang) { Join-Path $StateRoot "$Lang-compile.json" }
function SaveCompilation([string]$Lang, [string]$Path) {
    @{ stage=$Stage; language=$Lang; compiled=[IO.Path]::GetFullPath($Path); run=$Run } |
        ConvertTo-Json | Set-Content -LiteralPath (StatePath $Lang) -Encoding UTF8
}
function CompilationOf([string]$Lang) {
    if ($Compiled) {
        if ($Languages.Count -ne 1) { throw '-Compiled requires a single language.' }
        if ([IO.Path]::IsPathRooted($Compiled)) { return [IO.Path]::GetFullPath($Compiled) }
        return [IO.Path]::GetFullPath((Join-Path $Root $Compiled))
    }
    $state = StatePath $Lang
    if (-not (Test-Path -LiteralPath $state)) { throw "No $Lang compilation. Run -Step scripts first, or pass -Compiled." }
    $record = Get-Content -LiteralPath $state -Raw -Encoding UTF8 | ConvertFrom-Json
    return $record.compiled
}
function FreshPackage([string]$Lang) {
    $target = [IO.Path]::GetFullPath((Join-Path $BuildRoot "release$Stage\$Lang"))
    $allowed = [IO.Path]::GetFullPath((Join-Path $BuildRoot "release$Stage")) + '\'
    if (-not $target.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe package target.' }
    if (Test-Path -LiteralPath $target) {
        if ((Resolve-Path -LiteralPath $target).Path -ne $target) { throw 'Unexpected package path.' }
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    $release = Join-Path $Root 'BetaGwent\release'
    $archive = Join-Path $release "GwentBetaClassic-$Version-$($Lang.ToUpper()).zip"
    $old = Join-Path $release 'old'
    if (Test-Path -LiteralPath $archive) {
        New-Item -ItemType Directory -Force -Path $old | Out-Null
        Move-Item -LiteralPath $archive -Destination (Join-Path $old "GwentBetaClassic-$Version-$($Lang.ToUpper())-$Run.zip")
        if (Test-Path -LiteralPath "$archive.sha256") {
            Move-Item -LiteralPath "$archive.sha256" -Destination (Join-Path $old "GwentBetaClassic-$Version-$($Lang.ToUpper())-$Run.zip.sha256")
        }
    }
}
function RestoreRussianProject {
    $reportFile = Join-Path $Evidence "stage$Stage-completion.json"
    if (-not (Test-Path -LiteralPath $reportFile)) { return }
    $report = Get-Content -LiteralPath $reportFile -Raw -Encoding UTF8 | ConvertFrom-Json
    $allowed = [IO.Path]::GetFullPath((Join-Path $BuildRoot "stage$Stage\ru\resources"))+'\'
    foreach ($menu in @($report.menus | Where-Object { $_.language -eq 'ru' })) {
        $path = [IO.Path]::GetFullPath($menu.resource)
        if (-not $path.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe RU resource path.' }
        $name = [IO.Path]::GetFileName($path)
        if ($name -notin @('betagwent_board.redswf','betagwent_npc00.redswf','betagwent_decks.redswf','betagwent_kegop.redswf')) { throw 'Unexpected resource name.' }
        if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower() -ne $menu.sha256.ToLower()) { throw 'RU checksum mismatch.' }
        Copy-Item -LiteralPath $path -Destination (Join-Path $Root "GwentB\myproject1\workspace\betagwent\$name") -Force
    }
}
function PrepareSources {
    PythonStep 'font metrics' @('tools/ui/build_text_metrics112.py')
    if ($Stage -ge 120) { PythonStep 'camera-facing Beta boards and native dividers' @('tools/ui/build_board120.py') }
    if ($KegVideo) {
        PythonStep 'extract keg video' @('tools/ui/extract_keg111.py',$KegVideo)
    }
    PythonStep 'keg atlas and original emblems' @('tools/ui/build_keg109.py')
    PythonStep 'full card catalog' @('tools/build_full_catalog.py')
    PythonStep 'AI deck overrides and profiles' @('tools/build_ai_rules.py')
    PythonStep 'editable researched AI strategy tables' @('tools/build_research_strategy115.py')
    PythonStep 'duel card and deck definitions' @('tools/build_duel_catalog.py')
    PythonStep 'AI deep-copy generator' @('tools/ai/gen_clone.py')
    PythonStep 'menu pause flags' @('tools/ui/set_menu_pause.py',
        'GwentB/myproject1/workspace/betagwent/betagwent_board.menu',
        'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4gwint_game.menu',
        'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4deck_builder.menu',
        'GwentB/myproject1/workspace/betagwent/betagwent_kegop.menu')
    PythonStep 'packaging baselines' @('tools/restore_build_base105.py')
    PythonStep 'prepare WitcherScript' @('tools/ui/prepare_board_scripts.py')
    if ($CheckAI) {
        $snapshot = Join-Path $StateRoot "$Run-ai\snapshot"
        PythonStep 'freeze AI' @('tools/ai/snapshot.py',$snapshot)
        & node tools/ai/check_public_response113.js $snapshot
        if ($LASTEXITCODE -ne 0) { throw 'Native response regression failed.' }
        & node tools/ai/scenarios112.js $snapshot
        if ($LASTEXITCODE -ne 0) { throw 'Safe-row regression failed.' }
        & node tools/ai/scenarios114.js $snapshot
        if ($LASTEXITCODE -ne 0) { throw 'Ship placement / combined effect regression failed.' }
        & node tools/ai/scenarios115.js $snapshot
        if ($LASTEXITCODE -ne 0) { throw 'Researched roster / strategy / round economy regression failed.' }
        if ($Stage -ge 119) {
            & node tools/ai/scenarios111.js $snapshot
            if ($LASTEXITCODE -ne 0) { throw 'Ability / animation regression failed.' }
            & node tools/ai/scenarios118.js $snapshot
            if ($LASTEXITCODE -ne 0) { throw 'Created spy / empty duel regression failed.' }
            & node tools/ai/scenarios119.js $snapshot (Join-Path $snapshot 'checks119.json')
            if ($LASTEXITCODE -ne 0) { throw '46-archetype synergy regression failed.' }
            if ($Stage -ge 120) {
                & node tools/ai/scenarios120.js $snapshot (Join-Path $snapshot 'checks120.json')
                if ($LASTEXITCODE -ne 0) { throw 'Graveyard lock regression failed.' }
            }
        }
    }
}

$lock = $null
Start-Transcript -Path $Transcript | Out-Null
try {
    # Every menu export shares one working directory, regardless of stage.
    $lock = [IO.File]::Open((Join-Path $BuildRoot 'presentation-build.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
    if ($Step -in @('full','prepare','scripts')) { PrepareSources }
    foreach ($lang in $Languages) {
        if ($Step -in @('full','menus')) {
            PythonStep "$lang menus and script/UI bindings" @('tools/build_presentation94.py','--stage',"$Stage",'--language',$lang)
        } elseif ($Step -eq 'scripts' -and $lang -eq 'en') {
            PythonStep 'isolated English sources' @('tools/localization89.py','sources','--output-dir',"BetaGwent/build/stage$Stage/en")
            PythonStep 'English voice durations' @('tools/generate_en_audio_catalog.py')
            Copy-Item -LiteralPath (Join-Path $Root 'BetaGwent/audio/generated/duelAudioCatalog-en.ws') -Destination (Join-Path $Root "BetaGwent/build/stage$Stage/en/en-source/scripts/game/betagwent/duelAudioCatalog.ws") -Force
        }
        if ($Step -in @('full','scripts')) {
            $patch = if ($lang -eq 'ru') { 'BetaGwent/build/board-patch' } else { "BetaGwent/build/stage$Stage/en/en-source/scripts" }
            $out = "BetaGwent/build/board-compile${Stage}${lang}-$Run"
            PythonStep "$lang native compilation" @('tools/recon/run_redkit_compile.py','--out',$out,'--patch',$patch,'--timeout','300','--terms-already-accepted')
            SaveCompilation $lang $out
        }
        if ($Step -in @('full','package')) {
            $compile = CompilationOf $lang
            FreshPackage $lang
            PythonStep "$lang cook, strings, audio, dependencies, metadata, ZIP" @('tools/package_presentation94.py','--stage',"$Stage",'--version',$Version,'--language',$lang,'--compiled',$compile)
        }
    }
    Write-Host "Done: $Step, $Language, $Version. Archives: $Root\BetaGwent\release" -ForegroundColor Green
} finally {
    try { RestoreRussianProject } finally {
        if ($lock) { $lock.Dispose() }
        Stop-Transcript | Out-Null
    }
}
