$ErrorActionPreference = 'Stop'
$taskBuild = 'D:\w3mod\BetaGwent\build\classic081-native-resources-fix10'
$taskGame = 'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'
$taskMod = Join-Path $taskGame 'Mods\modBetaGwentClassic132'
$taskPackage = Join-Path $taskBuild 'package'
$taskCandidate = Join-Path $taskPackage 'Mods\modBetaGwentClassic132'
$taskManifest = Get-Content -LiteralPath (Join-Path $taskBuild 'install-manifest.json') -Raw | ConvertFrom-Json
$taskAudit = Get-Content -LiteralPath (Join-Path $taskBuild 'structural-audit.json') -Raw | ConvertFrom-Json
$taskDLCAudit = Get-Content -LiteralPath (Join-Path $taskBuild 'dlc-audit.json') -Raw | ConvertFrom-Json
$taskBackup = Join-Path $taskBuild 'installed-before'
$taskFiles = @('content/blob0.bundle', 'content/metadata.store', 'content/dep.cache', 'info.json')
$taskDLCRoot = Join-Path $taskGame 'DLC'
$taskDLCTarget = Join-Path $taskDLCRoot $taskManifest.dlc
$taskDLCSource = Join-Path (Join-Path $taskPackage 'DLC') $taskManifest.dlc
$taskDLCFiles = @($taskManifest.dlcFiles.PSObject.Properties | ForEach-Object { $_.Name })

if (@(Get-Process -Name witcher3 -ErrorAction SilentlyContinue).Count) { throw 'Игра запущена. Файлы не изменены.' }
if ($taskAudit.structuralIssues.Count -ne 0 -or $taskAudit.checks.Count -ne 16 -or -not $taskDLCAudit.passed) {
    throw 'Нет успешной проверки мода и DLC.'
}
if ($taskManifest.sourceVersion -ne '0.8.1-classic-streaming-fix9' -or $taskManifest.dlc -ne 'dlcBetaGwentClassic132Assets') {
    throw 'Неожиданный установочный манифест.'
}
if (-not ([IO.Path]::GetFullPath($taskDLCTarget)).StartsWith([IO.Path]::GetFullPath($taskDLCRoot) + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'DLC находится вне разрешённого каталога.'
}
$taskMods = @(Get-ChildItem -LiteralPath (Join-Path $taskGame 'Mods') -Directory)
if ($taskMods.Count -ne 1 -or $taskMods[0].Name -ne 'modBetaGwentClassic132') { throw 'Изменился набор модов.' }
foreach ($taskName in $taskFiles) {
    $taskHash = (Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant()
    if ($taskHash -ne $taskManifest.installedBefore.$taskName -and $taskHash -ne $taskManifest.installFiles.$taskName) {
        throw ('Установленный файл отличается от fix9 и fix10: ' + $taskName)
    }
    if ((Get-FileHash -LiteralPath (Join-Path $taskCandidate $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.installFiles.$taskName) {
        throw ('Кандидат отличается от проверенного: ' + $taskName)
    }
}
$taskDLCNew = -not (Test-Path -LiteralPath $taskDLCTarget)
foreach ($taskName in $taskDLCFiles) {
    $taskPath = [IO.Path]::GetFullPath((Join-Path $taskDLCTarget $taskName))
    if (-not $taskPath.StartsWith([IO.Path]::GetFullPath($taskDLCTarget) + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Некорректный путь файла DLC.'
    }
    if ((Get-FileHash -LiteralPath (Join-Path $taskDLCSource $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.dlcFiles.$taskName) {
        throw ('Не прошёл SHA кандидата DLC: ' + $taskName)
    }
    if (-not $taskDLCNew -and (-not (Test-Path -LiteralPath $taskPath) -or
        (Get-FileHash -LiteralPath $taskPath).Hash.ToLowerInvariant() -ne $taskManifest.dlcFiles.$taskName)) {
        throw ('Существующий DLC отличается: ' + $taskPath)
    }
}
foreach ($taskName in $taskFiles) {
    $taskSaved = Join-Path $taskBackup $taskName
    if (Test-Path -LiteralPath $taskSaved) {
        if ((Get-FileHash -LiteralPath $taskSaved).Hash.ToLowerInvariant() -ne $taskManifest.installedBefore.$taskName) {
            throw ('Резервная копия отличается от fix9: ' + $taskName)
        }
    } else {
        if ((Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.installedBefore.$taskName) {
            throw ('Нет исходного fix9 для резервной копии: ' + $taskName)
        }
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($taskSaved)) -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $taskMod $taskName) -Destination $taskSaved
    }
}
$taskMutated = $false
try {
    if ($taskDLCNew) {
        foreach ($taskName in $taskDLCFiles) {
            $taskTarget = Join-Path $taskDLCTarget $taskName
            New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($taskTarget)) -Force | Out-Null
            Copy-Item -LiteralPath (Join-Path $taskDLCSource $taskName) -Destination $taskTarget
        }
    }
    foreach ($taskName in $taskFiles) {
        $taskTarget = Join-Path $taskMod $taskName
        if ((Get-FileHash -LiteralPath $taskTarget).Hash.ToLowerInvariant() -eq $taskManifest.installFiles.$taskName) { continue }
        $taskTemp = $taskTarget + '.fix10tmp'
        if (Test-Path -LiteralPath $taskTemp) { throw ('Уже существует временный файл: ' + $taskTemp) }
        Copy-Item -LiteralPath (Join-Path $taskCandidate $taskName) -Destination $taskTemp
        $taskMutated = $true
        [IO.File]::Replace($taskTemp, $taskTarget, (Join-Path $taskBackup $taskName))
    }
    foreach ($taskName in $taskFiles) {
        if ((Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.installFiles.$taskName) {
            throw ('Не прошёл установленный SHA: ' + $taskName)
        }
    }
    foreach ($taskName in $taskDLCFiles) {
        if ((Get-FileHash -LiteralPath (Join-Path $taskDLCTarget $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.dlcFiles.$taskName) {
            throw ('Не прошёл установленный SHA DLC: ' + $taskName)
        }
    }
    @{ version=$taskManifest.version; sourceVersion=$taskManifest.sourceVersion; backup=$taskBackup;
       installedFiles=$taskManifest.installFiles; dlc=$taskDLCTarget; dlcFiles=$taskManifest.dlcFiles;
       gameLaunched=$false } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskBuild 'installation.json') -Encoding utf8
    Write-Output 'Fix10 установлен. Мод и DLC проверены по SHA. Игра не запускалась.'
}
catch {
    if ($taskMutated) {
        foreach ($taskName in $taskFiles) { [IO.File]::Copy((Join-Path $taskBackup $taskName), (Join-Path $taskMod $taskName), $true) }
    }
    if ($taskDLCNew) {
        foreach ($taskName in $taskDLCFiles) {
            $taskPath = Join-Path $taskDLCTarget $taskName
            if ((Test-Path -LiteralPath $taskPath) -and
                (Get-FileHash -LiteralPath $taskPath).Hash.ToLowerInvariant() -eq $taskManifest.dlcFiles.$taskName) {
                Remove-Item -LiteralPath $taskPath
            }
        }
    }
    throw
}
