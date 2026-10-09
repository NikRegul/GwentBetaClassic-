# Single-screen mulligan, ability choices and own-deck viewer.
param(
    [ValidateSet('ru','en','both')][string]$Language='ru',
    [string]$Version='0.3.5-preview.5',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI
)
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 118 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
