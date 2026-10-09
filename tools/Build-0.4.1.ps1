# Editable release build: original Beta board bake, native menus, scripts and ZIPs.
[CmdletBinding()]
param(
    [ValidateSet('ru','en','both')][string]$Language='both',
    [string]$Version='0.4.1',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI
)
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 120 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
