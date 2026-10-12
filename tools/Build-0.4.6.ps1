# Editable next-patch build. This file does nothing until you run it.
# 0.4.6 rebuild: single-sweep damage, hidden enemy ambush timers, deck deletion/reset, selection navigation,
# AI stage 127 (decisive order, longships, concession, tutors, weather, Draug), catalogue filters, history, AI pause, animations.
# powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.4.6.ps1
[CmdletBinding()]
param(
    [ValidateSet('ru','en','both')][string]$Language='both',
    [ValidatePattern('^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?$')][string]$Version='0.4.6',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI=$true
)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 126 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
