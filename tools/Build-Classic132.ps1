param(
    [Parameter(Mandatory=$true)][int]$SourceStage,
    [Parameter(Mandatory=$true)][string]$SourceVersion,
    [string]$Game = 'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt',
    [string]$OutputDirectory,
    [string]$PreviousManifest
    ,[int]$TestRevision = 1
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputDirectory) {
    $buildLabel = 'classic132-stage' + $SourceStage + '-ru-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
    $OutputDirectory = Join-Path $projectRoot ('BetaGwent\build\' + $buildLabel)
}
$buildArguments = @('-X', 'utf8', (Join-Path $PSScriptRoot 'classic132\build.py'), '--source-stage', $SourceStage, '--version', $SourceVersion, '--game', $Game, '--out', $OutputDirectory)
$buildArguments += @('--test-revision', $TestRevision)
if ($PreviousManifest) { $buildArguments += @('--previous', $PreviousManifest) }
& python @buildArguments
if ($LASTEXITCODE -ne 0) { throw 'Classic 1.32 build failed. Read the last phase report.' }
