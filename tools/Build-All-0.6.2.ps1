# Build all five voice packages, each containing all thirteen text languages.
[CmdletBinding()]
param(
    [ValidateSet('full','prepare','scripts','menus','package','verify')]
    [string]$Step = 'full',
    [switch]$RebuildExisting
)
$ErrorActionPreference = 'Stop'
$BuildOptions = @{ Step = $Step; Language = 'all' }
if ($RebuildExisting) { $BuildOptions.RebuildExisting = $true }
& (Join-Path $PSScriptRoot 'Build-0.6.2.ps1') @BuildOptions
