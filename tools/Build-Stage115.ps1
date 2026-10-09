# Researched 46-deck AI, compiled Russian preview for retail testing.
param(
    [ValidateSet('ru','en','both')][string]$Language='ru',
    [string]$Version='0.3.5-preview.2',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI
)
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 115 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
