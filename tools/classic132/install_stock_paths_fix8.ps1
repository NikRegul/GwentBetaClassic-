$ErrorActionPreference = 'Stop'
$taskBuild = 'D:\w3mod\BetaGwent\build\classic081-stock-paths-fix8'
$taskGame = 'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'
$taskMod = Join-Path $taskGame 'Mods\modBetaGwentClassic132'
$taskCandidate = Join-Path $taskBuild 'package\Mods\modBetaGwentClassic132'
$taskManifest = Get-Content -LiteralPath (Join-Path $taskBuild 'verification.json') -Raw | ConvertFrom-Json
$taskAudit = Get-Content -LiteralPath (Join-Path $taskBuild 'structural-audit.json') -Raw | ConvertFrom-Json
$taskFiles = @('content/blob0.bundle', 'content/metadata.store', 'content/dep.cache', 'info.json')
$taskBackup = Join-Path $taskBuild 'installed-before'

if (@(Get-Process -Name witcher3 -ErrorAction SilentlyContinue).Count) {
    throw 'Игра запущена. Файлы не изменены.'
}
if ($taskAudit.structuralIssues.Count -ne 0 -or $taskAudit.checks.Count -ne 14) {
    throw 'Нет успешной полной структурной проверки кандидата.'
}
$taskMods = @(Get-ChildItem -LiteralPath (Join-Path $taskGame 'Mods') -Directory)
if ($taskMods.Count -ne 1 -or $taskMods[0].Name -ne 'modBetaGwentClassic132') {
    throw 'Изменился набор модов; установка остановлена.'
}
if (-not ([System.IO.Path]::GetFullPath($taskBackup)).StartsWith(
        [System.IO.Path]::GetFullPath($taskBuild) + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Резервная копия должна находиться внутри каталога сборки.'
}
$taskAlreadyInstalled = $true
foreach ($taskName in $taskFiles) {
    $taskActual = (Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant()
    $taskOldHash = $taskManifest.installedBefore.$taskName
    $taskNewHash = $taskManifest.installFiles.$taskName
    if ($taskActual -ne $taskOldHash -and $taskActual -ne $taskNewHash) {
        throw ('Неожиданный установленный файл: ' + $taskName)
    }
    if ($taskActual -ne $taskNewHash) { $taskAlreadyInstalled = $false }
    if ((Get-FileHash -LiteralPath (Join-Path $taskCandidate $taskName)).Hash.ToLowerInvariant() -ne $taskNewHash) {
        throw ('Кандидат не совпадает с проверенным SHA: ' + $taskName)
    }
}
if ($taskAlreadyInstalled) {
    Write-Output 'Fix8 уже установлен и проверен по SHA.'
    exit 0
}
foreach ($taskName in $taskFiles) {
    $taskSaved = Join-Path $taskBackup $taskName
    if (Test-Path -LiteralPath $taskSaved) {
        if ((Get-FileHash -LiteralPath $taskSaved).Hash.ToLowerInvariant() -ne $taskManifest.installedBefore.$taskName) {
            throw ('Резервная копия отличается от fix7: ' + $taskName)
        }
    }
    else {
        $taskCurrentPath = Join-Path $taskMod $taskName
        if ((Get-FileHash -LiteralPath $taskCurrentPath).Hash.ToLowerInvariant() -ne $taskManifest.installedBefore.$taskName) {
            throw ('Нельзя восстановить исходную копию fix7 для ' + $taskName)
        }
        New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($taskSaved)) -Force | Out-Null
        Copy-Item -LiteralPath $taskCurrentPath -Destination $taskSaved
    }
}
$taskMutated = $false
try {
    foreach ($taskName in $taskFiles) {
        $taskTarget = Join-Path $taskMod $taskName
        $taskTemp = $taskTarget + '.fix8tmp'
        if (Test-Path -LiteralPath $taskTemp) {
            if ((Get-FileHash -LiteralPath $taskTemp).Hash.ToLowerInvariant() -ne $taskManifest.installFiles.$taskName) {
                throw ('Неожиданный временный файл: ' + $taskTemp)
            }
        }
        else { Copy-Item -LiteralPath (Join-Path $taskCandidate $taskName) -Destination $taskTemp }
        $taskMutated = $true
        [System.IO.File]::Replace($taskTemp, $taskTarget, (Join-Path $taskBackup $taskName))
    }
    $taskHashes = @{}
    foreach ($taskName in $taskFiles) {
        $taskHash = (Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant()
        if ($taskHash -ne $taskManifest.installFiles.$taskName) { throw ('Не прошёл установленный SHA: ' + $taskName) }
        $taskHashes[$taskName] = $taskHash
    }
    @{
        version = $taskManifest.version
        game = $taskGame
        backup = $taskBackup
        installedFiles = $taskHashes
        gameLaunched = $false
        sourceVersion = $taskManifest.sourceVersion
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskBuild 'installation.json') -Encoding utf8
    Write-Output ('Fix8 установлен и проверен. Резервная копия: ' + $taskBackup)
    Write-Output 'Игра не запускалась.'
}
catch {
    if ($taskMutated) {
        foreach ($taskName in $taskFiles) {
            [System.IO.File]::Copy((Join-Path $taskBackup $taskName), (Join-Path $taskMod $taskName), $true)
        }
    }
    throw
}
