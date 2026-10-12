# Source-only checks. Does not compile menus, invoke REDkit, install or package a release.
[CmdletBinding()]
param([string]$Snapshot = '')
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$env:PYTHONIOENCODING = 'utf-8'
if (-not $Snapshot) {
    $Snapshot = Join-Path $Root ('BetaGwent\build\source-check-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    & python -X utf8 tools/ai/snapshot.py $Snapshot
    if ($LASTEXITCODE -ne 0) { throw 'Failed to freeze source snapshot.' }
}
foreach ($Name in @('check_consume_self','check_followups126','check_no_targets127','check_decisive127','check_ships127','check_concede127','check_tutor127','check_preventive127','check_clearrisk127','check_draug127','check_combo127','check_deck_combos128','scenarios114','scenarios115','scenarios119','scenarios124','scenarios125')) {
    Write-Host "Checking AI: $Name"
    & node "tools/ai/$Name.js" $Snapshot "docs/evidence/$Name-source128.json"
    if ($LASTEXITCODE -ne 0) { throw "Failed: $Name" }
}
foreach ($Name in @('check_controller126','check_followups127','check_optional124','check_catalog123','check_card_presentation126','check_timing126')) {
    Write-Host "Checking UI: $Name"
    & node "tools/ui/$Name.js"
    if ($LASTEXITCODE -ne 0) { throw "Failed: $Name" }
}
foreach ($Name in @('tools/ai/check_rosters128.py','tools/ai/check_rewards121.py','tools/recon/check_release_build126.py','tools/recon/check_wcc_retry123.py')) {
    & python -X utf8 $Name $Snapshot
    if ($LASTEXITCODE -ne 0) { throw "Failed: $Name" }
}
Write-Host 'Source checks passed. Native game and controller verification still required.'
