[CmdletBinding()]
param(
    [string]$Version='',
    [int]$Stage=0,
    [string]$Python='python',
    [switch]$Verify,
    [switch]$ResumePackage,
    [int]$GuiLimitMiB=0,
    [switch]$CheckOnly
)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
$TaskLogDir=Join-Path $TaskBuildRoot 'BetaGwent\build\source-logs'
New-Item -ItemType Directory -Path $TaskLogDir -Force | Out-Null
$TaskLog=Join-Path $TaskLogDir ((Get-Date -Format 'yyyyMMdd-HHmmss')+'.log')
Push-Location -LiteralPath $TaskBuildRoot
try {
    Start-Transcript -Path $TaskLog | Out-Null
    $TaskArgs=@('-X','utf8','tools/build_from_source.py')
    if($Version){$TaskArgs+=@('--version',$Version)}
    if($Stage -gt 0){$TaskArgs+=@('--stage',[string]$Stage)}
    if($Verify){$TaskArgs+='--verify'}
    if($ResumePackage){$TaskArgs+='--resume-package'}
    if($GuiLimitMiB -gt 0){$TaskArgs+=@('--gui-limit-mib',[string]$GuiLimitMiB)}
    if($CheckOnly){$TaskArgs+='--check-only'}
    & $Python @TaskArgs
    if($LASTEXITCODE -ne 0){throw "Build failed. Log: $TaskLog"}
    Write-Host "Completed. Log: $TaskLog" -ForegroundColor Green
} finally {
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Pop-Location
}
