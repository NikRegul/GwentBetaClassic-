# Editable entry point for the ship/armour fixes following 0.3.4.
param(
    [ValidateSet('ru','en','both')][string]$Language='ru',
    [string]$Version='0.3.5-preview.1',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI
)
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 114 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
