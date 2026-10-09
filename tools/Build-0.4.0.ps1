# Editable RU/EN release build. -Step full: generate, verify, export, compile, cook, ZIP.
[CmdletBinding()]
param(
    [ValidateSet('ru','en','both')][string]$Language='both',
    [string]$Version='0.4.0',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI
)
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 119 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
