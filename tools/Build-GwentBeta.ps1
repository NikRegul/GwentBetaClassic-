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
    @{ stage=$Stage; language=$Lang; compiled=$(if ([IO.Path]::IsPathRooted($Path)) { [IO.Path]::GetFullPath($Path) } else { [IO.Path]::GetFullPath((Join-Path $Root $Path)) }); run=$Run } |
        ConvertTo-Json | Set-Content -LiteralPath (StatePath $Lang) -Encoding UTF8
}
function CompileScripts([string]$Lang, [string]$Patch) {
    for ($attempt = 0; $attempt -le 2; $attempt++) {
        $suffix = if ($attempt -eq 0) { '' } else { "-retry$attempt" }
        $out = "BetaGwent/build/board-compile${Stage}${Lang}-$Run$suffix"
        try {
            PythonStep "$Lang native compilation" @('tools/recon/run_redkit_compile.py','--out',$out,'--patch',$Patch,'--timeout','300','--terms-already-accepted')
            SaveCompilation $Lang $out
            return
        } catch {
            $resultPath = Join-Path $Root "$out/result.json"
            if ($attempt -ge 2 -or -not (Test-Path -LiteralPath $resultPath)) { throw }
            $result = Get-Content -LiteralPath $resultPath -Raw -Encoding UTF8 | ConvertFrom-Json
            # Retry REDkit's shutdown error 0xC0000008 and a compiler that hung during engine start-up
            # (timed out before compiling anything). A real script error is never retried.
            $log = Join-Path $Root "$out/stdout.txt"
            if ((Test-Path -LiteralPath $log) -and ((Get-Content -LiteralPath $log -Raw) -match '\[Script\]: Error \[')) { throw }
            $compiled = (Test-Path -LiteralPath $log) -and ((Get-Content -LiteralPath $log -Raw) -match "Starting commandlet 'compilescripts'")
            $hung = $result.timedOut -and -not $compiled
            if (-not $hung -and $result.processExitCode -ne 3221225480) { throw }
            Get-Process wcc_lite -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
            Write-Warning "$Lang compiler hung or hit REDkit shutdown error 0xC0000008; retrying in a fresh output directory."
        }
    }
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
    $restore = @()
    foreach ($menu in @($report.menus | Where-Object { $_.language -eq 'ru' })) {
        $path = [IO.Path]::GetFullPath($menu.resource)
        if (-not $path.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe RU resource path.' }
        $name = [IO.Path]::GetFileName($path)
        if ($name -notin @('betagwent_board.redswf','betagwent_npc00.redswf','betagwent_decks.redswf','betagwent_kegop.redswf')) { throw 'Unexpected resource name.' }
        if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower() -ne $menu.sha256.ToLower()) {
            if ($Step -in @('full','package')) { throw 'RU checksum mismatch. Rebuild menus before packaging.' }
            Write-Warning 'Interrupted menu build: keeping current workspace resources. Rebuild menus before packaging.'
            return
        }
        $restore += @{ path=$path; name=$name }
    }
    foreach ($item in $restore) {
        Copy-Item -LiteralPath $item.path -Destination (Join-Path $Root "GwentB\myproject1\workspace\betagwent\$($item.name)") -Force
    }
}
function PrepareSources {
    PythonStep 'font metrics' @('tools/ui/build_text_metrics112.py')
    if ($Stage -ge 120) { PythonStep 'camera-facing Beta boards and native dividers' @('tools/ui/build_board120.py') }
    if ($Stage -ge 121 -and (Test-Path -LiteralPath (Join-Path $Root 'Gwent 0.9.24.3.432\Gwent_Data\sharedassets8.assets'))) {
        $weatherPythonPath = $env:PYTHONPATH
        try {
            $env:PYTHONPATH = (Join-Path $Root 'tools\vendor\audio-python') + ';' + $weatherPythonPath
            PythonStep 'original Beta weather and 36-frame Golden Froth' @('tools/ui/build_weather107.py')
        } finally { $env:PYTHONPATH = $weatherPythonPath }
    }
    if ($KegVideo) {
        PythonStep 'extract keg video' @('tools/ui/extract_keg111.py',$KegVideo)
    }
    PythonStep 'keg atlas and original emblems' @('tools/ui/build_keg109.py')
    if ($Stage -ge 126) { PythonStep 'original Beta lock chains and clip timings' @('tools/ui/build_lock126.py') }
    PythonStep 'full card catalog' @('tools/build_full_catalog.py')
    PythonStep 'AI deck overrides and profiles' @('tools/build_ai_rules.py')
    PythonStep 'editable researched AI strategy tables' @('tools/build_research_strategy115.py')
    PythonStep 'starter collection progression' @('tools/build_progression.py')
    PythonStep 'duel card and deck definitions' @('tools/build_duel_catalog.py')
    PythonStep 'AI deep-copy generator' @('tools/ai/gen_clone.py')
    PythonStep 'menu pause flags' @('tools/ui/set_menu_pause.py',
        'GwentB/myproject1/workspace/betagwent/betagwent_board.menu',
        'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4gwint_game.menu',
        'GwentB/myproject1/workspace/gameplay/gui_new/guirsrc/r4deck_builder.menu',
        'GwentB/myproject1/workspace/betagwent/betagwent_kegop.menu')
    PythonStep 'packaging baselines' @('tools/restore_build_base105.py')
    if ($Stage -ge 135) {
        PythonStep 'RU/EN dialogue gain and bank inventory' @('tools/ui/build_voice_mix135.py')
        PythonStep 'base release excludes premium portraits' @('tools/check_base_release_portraits.py')
    }
    if ($Stage -ge 136) {
        PythonStep 'loop-only leader atlases' @('tools/prepare_release060.py','--part','leaders')
        PythonStep '21 native leader movies' @('tools/ui/build_leaders136.py')
        PythonStep 'RU/EN text display tables' @('tools/ui/build_text_language136.py')
        & node tools/ui/check_release136.js
        if ($LASTEXITCODE -ne 0) { throw 'Leader lifecycle and bilingual text regression failed.' }
        PythonStep 'native leader allowlist and loop-only provenance' @('tools/ui/check_leaders136.py')
    }
    PythonStep 'prepare WitcherScript' @('tools/ui/prepare_board_scripts.py')
    if ($CheckAI) {
        if ($Stage -ge 133) {
            PythonStep 'native local declaration order regression' @('tools/ai/check_locals133.py')
            PythonStep 'complete cooked resources and clean retry regression' @('tools/recon/check_cook_completion133.py')
        }
        $snapshot = Join-Path $StateRoot "$Run-ai\snapshot"
        PythonStep 'freeze AI' @('tools/ai/snapshot.py',$snapshot)
        if ($Stage -ge 123) {
            & node tools/ai/check_consume_self.js $snapshot (Join-Path $snapshot 'consume123.json')
            if ($LASTEXITCODE -ne 0) { throw 'Self-consumption regression failed.' }
            & node tools/ai/scenarios123.js $snapshot (Join-Path $snapshot 'checks123.json')
            if ($LASTEXITCODE -ne 0) { throw 'Target, spy, consume chain and roster regression failed.' }
            PythonStep 'saved opponent rotation' @('tools/ai/check_rotation123.py',$snapshot)
            & node tools/ui/check_controller123.js
            if ($LASTEXITCODE -ne 0) { throw 'Controller scope, row navigation and choice layout regression failed.' }
            & node tools/ui/check_catalog123.js
            if ($LASTEXITCODE -ne 0) { throw 'Persistent collection selection and Craft button regression failed.' }
            PythonStep 'craft event routing and save-profile economy' @('tools/ai/check_crafting123.py',$snapshot)
            PythonStep 'bounded REDkit shutdown retry' @('tools/recon/check_wcc_retry123.py')
        }
        if ($Stage -ge 124) {
            & node tools/ai/scenarios124.js $snapshot (Join-Path $Evidence 'optional124.json')
            if ($LASTEXITCODE -ne 0) { throw 'Optional card counts and Aard row movement regression failed.' }
            & node tools/ui/check_optional124.js
            if ($LASTEXITCODE -ne 0) { throw 'Optional choice controls regression failed.' }
        }
        if ($Stage -ge 125) {
            & node tools/ai/scenarios125.js $snapshot (Join-Path $Evidence 'spy125.json')
            if ($LASTEXITCODE -ne 0) { throw 'Draw-spy forecast, late-round recovery and RNG isolation regression failed.' }
            # Stage 126 supersedes these cases and exercises the current gridWrap contract.
            if ($Stage -lt 126) {
                & node tools/ui/check_controller125.js
                if ($LASTEXITCODE -ne 0) { throw 'Controller logical rows, column memory and focus restoration regression failed.' }
            }
        }
        if ($Stage -ge 126) {
            & node tools/ai/check_followups126.js $snapshot (Join-Path $Evidence 'followups126.json')
            if ($LASTEXITCODE -ne 0) { throw 'Contextual mulligan, whole-hand concession and spy activation regression failed.' }
            PythonStep 'native Skellige quest counter repair' @('tools/ai/check_quest126.py',$snapshot)
            & node tools/ui/check_halfcast126.js
            if ($LASTEXITCODE -ne 0) { throw 'Whole-half spell casting regression failed.' }
            & node tools/ai/check_engines126.js $snapshot (Join-Path $Evidence 'engines126.json')
            if ($LASTEXITCODE -ne 0) { throw 'Engine removal and lock priorities regression failed.' }
            & node tools/ai/check_weather_visual126.js $snapshot (Join-Path $Evidence 'weather-visual126.json')
            if ($LASTEXITCODE -ne 0) { throw 'Weather decisions, individual damage hits, Roach and resurrection regression failed.' }
            & node tools/ui/check_controller126.js
            if ($LASTEXITCODE -ne 0) { throw 'Controller footer, empty deck and match result navigation regression failed.' }
            & node tools/ui/check_timing126.js
            if ($LASTEXITCODE -ne 0) { throw 'Uniform weather timing and mass-consume presentation regression failed.' }
            & node tools/ui/check_card_presentation126.js
            if ($LASTEXITCODE -ne 0) { throw 'Complete placement card faces and victory crown regression failed.' }
            & node tools/ai/check_decisive127.js $snapshot (Join-Path $Evidence 'decisive127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Decisive-round ordering regression failed.' }
            & node tools/ai/check_ships127.js $snapshot (Join-Path $Evidence 'ships127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Longship engine targeting regression failed.' }
            & node tools/ai/check_concede127.js $snapshot (Join-Path $Evidence 'concede127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Round-one concession regression failed.' }
            & node tools/ai/check_tutor127.js $snapshot (Join-Path $Evidence 'tutor127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Empty tutor valuation regression failed.' }
            & node tools/ai/check_preventive127.js $snapshot (Join-Path $Evidence 'preventive127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Preventive weather regression failed.' }
            & node tools/ai/check_clearrisk127.js $snapshot (Join-Path $Evidence 'clearrisk127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Clear Skies reserve regression failed.' }
            & node tools/ai/check_draug127.js $snapshot (Join-Path $Evidence 'draug127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Draug resurrection and timing regression failed.' }
            & node tools/ai/check_combo127.js $snapshot (Join-Path $Evidence 'combo127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Fringilla and Draig Bon-Dhu combo regression failed.' }
            & node tools/ai/check_no_targets127.js $snapshot (Join-Path $Evidence 'no-targets127.json')
            if ($LASTEXITCODE -ne 0) { throw 'Empty mandatory ability feedback regression failed.' }
            & node tools/ui/check_followups127.js
            if ($LASTEXITCODE -ne 0) { throw 'Held piles, one-page choices, history and AI pause regression failed.' }
            & node tools/ai/check_deck_combos128.js $snapshot
            if ($LASTEXITCODE -ne 0) { throw 'Longship, Thunder and ambush preparation regression failed.' }
            PythonStep 'reviewed deck legality and protected starter rosters' @('tools/ai/check_rosters128.py')
            if ($Stage -ge 131) {
                & node tools/ai/check_losing131.js $snapshot (Join-Path $Evidence 'losing131.json')
                if ($LASTEXITCODE -ne 0) { throw 'Losing-play pass regression failed.' }
                & node tools/ai/check_cavalry131.js $snapshot (Join-Path $Evidence 'cavalry131.json')
                if ($LASTEXITCODE -ne 0) { throw 'Kaedweni Cavalry armor targeting regression failed.' }
                & node tools/ai/check_ciri131.js $snapshot (Join-Path $Evidence 'ciri131.json')
                if ($LASTEXITCODE -ne 0) { throw 'False Ciri return timing regression failed.' }
                & node tools/ai/check_assassin133.js $snapshot (Join-Path $Evidence 'assassin133.json')
                if ($LASTEXITCODE -ne 0) { throw 'Assassin victim placement regression failed.' }
            }
            if ($Stage -ge 133) {
                & node tools/ai/check_policy133.js $snapshot (Join-Path $Evidence 'policy133.json')
                if ($LASTEXITCODE -ne 0) { throw 'Public AI policy and Epidemic regression failed.' }
                & node tools/ai/check_hidden_information133.js $snapshot (Join-Path $Evidence 'hidden-information133.json')
                if ($LASTEXITCODE -ne 0) { throw 'Hidden-information invariance across all 46 profiles failed.' }
                & node tools/ui/check_presentation133.js (Join-Path $Evidence 'presentation133.json')
                if ($LASTEXITCODE -ne 0) { throw 'Replay retiming and introduction regression failed.' }
                PythonStep 'RU/EN leader intro queue regression' @('tools/ui/check_intro_audio133.py',$snapshot,(Join-Path $Evidence 'intro-audio133.json'))
                if ($Stage -ge 135) {
                    & node tools/ui/check_ux135.js (Join-Path $Evidence 'ux135.json')
                    if ($LASTEXITCODE -ne 0) { throw 'Tutorial layout, modal and controller regression failed.' }
                    PythonStep 'voice completion, music duck and opponent gate regression' @('tools/ui/check_audio135.py',$snapshot,(Join-Path $Evidence 'audio135.json'))
                }
            }
        }
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
                if ($Stage -ge 121) {
                    & node tools/ai/scenarios121.js $snapshot (Join-Path $snapshot 'checks121.json')
                    if ($LASTEXITCODE -ne 0) { throw 'Weather and consume regression failed.' }
                    PythonStep 'save reward ledger and starter migration' @('tools/ai/check_rewards121.py',$snapshot)
                    PythonStep 'profile mirror format 2: banks, checksum, staged restore, reward ledgers' @('tools/ai/check_profile136.py',$snapshot)
                    & node tools/ui/check_mulligan121.js
                    if ($LASTEXITCODE -ne 0) { throw 'Mulligan slot order and geometry regression failed.' }
                    PythonStep 'weather flipbook and seamless storm atlas' @('tools/ui/check_weather121.py')
                }
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
            CompileScripts $lang $patch
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
