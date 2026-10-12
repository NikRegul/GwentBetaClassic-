# Editable 0.4.5 build. Defaults: RU + EN, full build, regression checks on.
# powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.4.5.ps1
[CmdletBinding()]
param(
    [ValidateSet('ru','en','both')][string]$Language='both',
    [ValidatePattern('^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?$')][string]$Version='0.4.5',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI=$true
)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 125 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
