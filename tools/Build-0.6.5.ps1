<#
.SYNOPSIS
Build or verify Gwent Beta Classic 0.6.5 from the prepared Stage 141 inputs.
.EXAMPLE
.\tools\Build-0.6.5.ps1 -Language ru
.EXAMPLE
.\tools\Build-0.6.5.ps1 -Language all
.EXAMPLE
.\tools\Build-0.6.5.ps1 -Step verify -Language ru
.NOTES
Full verifies existing archives and builds missing packages. It never overwrites
an existing release. Audio banks, snapshot and regression reports must be prepared.
#>
[CmdletBinding()]
param(
    [ValidateSet('full','scripts','menus','package','verify')]
    [string]$Step = 'full',
    [ValidateSet('all','ru','en','de','it','pt-br')]
    [string]$Language = 'ru',
    [string]$Python
)
$ErrorActionPreference = 'Stop'
$BuildRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) {
    $BundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if (Test-Path -LiteralPath $BundledPython -PathType Leaf) {
        $Python = $BundledPython
    } else {
        $PythonCommand = Get-Command python -CommandType Application -ErrorAction SilentlyContinue
        if (-not $PythonCommand) { throw 'Python is unavailable. Pass -Python with the path to python.exe.' }
        $Python = ($PythonCommand | Select-Object -First 1).Source
    }
}
function Invoke-GwentBuild {
    param([string]$BuildStep, [string]$Voice)
    & $Python -X utf8 tools/build_release141.py --step $BuildStep --language $Voice
    if ($LASTEXITCODE -ne 0) { throw "0.6.5 $BuildStep failed ($Voice); inspect BetaGwent/build/stage141/logs." }
}
$PreviousEncoding = $env:PYTHONIOENCODING
Push-Location -LiteralPath $BuildRoot
try {
    $env:PYTHONIOENCODING = 'utf-8'
    $Voices = @($Language)
    if ($Language -eq 'all') { $Voices = @('ru','en','de','it','pt-br') }
    if ($Step -eq 'full') {
        foreach ($Voice in $Voices) {
            $Archive = Join-Path $BuildRoot ("BetaGwent/release/GwentBetaClassic-0.6.5-{0}.zip" -f $Voice.ToUpperInvariant())
            if (Test-Path -LiteralPath $Archive -PathType Leaf) {
                Write-Host "Existing 0.6.5 archive: $Voice. Verifying."
                Invoke-GwentBuild -BuildStep verify -Voice $Voice
            } else {
                Invoke-GwentBuild -BuildStep full -Voice $Voice
            }
        }
        if ($Voices.Count -gt 1) { Invoke-GwentBuild -BuildStep verify -Voice all }
    } else {
        Invoke-GwentBuild -BuildStep $Step -Voice $Language
    }
    if ($Step -eq 'full' -or $Step -eq 'verify') {
        foreach ($Voice in $Voices) {
            Get-Item -LiteralPath ("BetaGwent/release/GwentBetaClassic-0.6.5-{0}.zip" -f $Voice.ToUpperInvariant()) |
                ForEach-Object { '{0}  {1:N0} bytes' -f $_.Name, $_.Length }
        }
        Write-Host 'Report: docs/evidence/validation141.json'
    }
} finally {
    $env:PYTHONIOENCODING = $PreviousEncoding
    Pop-Location
}
