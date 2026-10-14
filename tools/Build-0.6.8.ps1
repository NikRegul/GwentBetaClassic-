# Gwent Beta Classic 0.6.8 (RU) from current sources: AI fixes (False Ciri, resilience,
# own spies, Scoia'tael self-targets, Radovid/Ciaran locks) + current animations.
# Uses the maintained from-source pipeline: snapshot, regressions (52 suites),
# native menus, WitcherScript compile, package and archive verification.
[CmdletBinding()]
param([switch]$CheckOnly,[string]$Python='python',[int]$GuiLimitMiB=65)
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
# wcc_lite hangs when another REDkit/game instance holds its service port 37000.
$busy=@(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @('wcc_lite','witcher3') -or ($_.Path -and $_.Path -like '*REDkit*') })
$listener=Get-NetTCPConnection -LocalPort 37000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if($listener){$busy+=Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue}
if($busy.Count -gt 0 -and -not $CheckOnly){
    $busy | Sort-Object Id -Unique | ForEach-Object { Write-Host ('Running: {0} (PID {1}) {2}' -f $_.Name,$_.Id,$_.Path) }
    throw 'Close The Witcher 3, REDkit and any wcc_lite.exe (Task Manager), then run the build again.'
}
$BuildArgs=@{Version='0.6.8';Python=$Python;GuiLimitMiB=$GuiLimitMiB}
if(-not $CheckOnly){
    # Rebuild the 13 text/font resources: new UI strings (e.g. the Yrden cue) need native dictionaries.
    & $Python -X utf8 (Join-Path $Root 'tools\ui\build_ui_languages138.py')
    if($LASTEXITCODE -ne 0){throw 'text138 language resources failed'}
}
if($CheckOnly){$BuildArgs.CheckOnly=$true}
& (Join-Path $PSScriptRoot 'Build-FromSource.ps1') @BuildArgs
if(-not $?){throw '0.6.8 build failed; see BetaGwent\build\source-logs'}
Get-ChildItem -LiteralPath (Join-Path $Root 'BetaGwent\release') -Filter 'GwentBetaClassic-0.6.8-RU.zip' -ErrorAction SilentlyContinue |
    ForEach-Object { '{0}  {1:N0} bytes' -f $_.FullName,$_.Length }
