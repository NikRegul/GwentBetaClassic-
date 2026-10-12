# Push the prepared 0.3.0 source commit to https://github.com/NikRegul/GwentBetaClassic-
# Run:  powershell -ExecutionPolicy Bypass -File D:\w3mod\BetaGwent\release\publish-0.3.0\Push-GitHub-0.3.0.ps1
# Needs Git for Windows (installed automatically via winget if missing). The first push opens a GitHub sign-in window.
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bundle = Join-Path $Here 'GwentBetaClassic-0.3.0.bundle'
$Repo = 'D:\w3mod\BetaGwent\build\github-0.3.0'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host 'Installing Git for Windows...' -ForegroundColor Cyan
    winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
}

if (-not (Test-Path "$Repo\.git")) { git clone https://github.com/NikRegul/GwentBetaClassic-.git $Repo }
Set-Location $Repo
git checkout main
git pull --ff-only origin main
git bundle verify $Bundle
git fetch $Bundle main:release-0.3.0
git merge --ff-only release-0.3.0
git log --oneline -2
git push origin main
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
Write-Host 'Pushed: https://github.com/NikRegul/GwentBetaClassic-' -ForegroundColor Green
