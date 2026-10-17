$ErrorActionPreference = 'Stop'
$taskBuild = 'D:\w3mod\BetaGwent\build\classic081-subimages-fix12'
$taskGame = 'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'
$taskMod = Join-Path $taskGame 'Mods\modBetaGwentClassic132'
$taskCandidate = Join-Path $taskBuild 'package\Mods\modBetaGwentClassic132'
$taskBackup = Join-Path $taskBuild 'installed-before'
$taskManifest = Get-Content -LiteralPath (Join-Path $taskBuild 'install-manifest.json') -Raw | ConvertFrom-Json
$taskAudit = Get-Content -LiteralPath (Join-Path $taskBuild 'structural-audit.json') -Raw | ConvertFrom-Json
$taskFiles = @('content/blob0.bundle', 'content/metadata.store', 'content/dep.cache', 'info.json')
if (@(Get-Process -Name witcher3 -ErrorAction SilentlyContinue).Count) { throw 'Игра запущена. Файлы не изменены.' }
if ($taskManifest.sourceVersion -ne '0.8.1-classic-native-bitmap-fix11' -or
    $taskAudit.structuralIssues.Count -ne 0 -or $taskAudit.checks.Count -ne 16) { throw 'Нет успешной проверки кандидата.' }
$taskMods = @(Get-ChildItem -LiteralPath (Join-Path $taskGame 'Mods') -Directory)
if ($taskMods.Count -ne 1 -or $taskMods[0].Name -ne 'modBetaGwentClassic132') { throw 'Изменился набор модов.' }
foreach ($taskName in $taskFiles) {
    $taskCurrentHash = (Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant()
    if ($taskCurrentHash -ne $taskManifest.installedBefore.$taskName -and $taskCurrentHash -ne $taskManifest.installFiles.$taskName) {
        throw ('Установленный файл отличается от fix11/fix12: ' + $taskName)
    }
    if ((Get-FileHash -LiteralPath (Join-Path $taskCandidate $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.installFiles.$taskName) {
        throw ('Кандидат изменился: ' + $taskName)
    }
}
foreach ($taskProperty in $taskManifest.dlcFiles.PSObject.Properties) {
    $taskDLCFile = Join-Path (Join-Path $taskGame 'DLC\dlcBetaGwentClassic132Assets') $taskProperty.Name
    if ((Get-FileHash -LiteralPath $taskDLCFile).Hash.ToLowerInvariant() -ne $taskProperty.Value) { throw 'Изменился GUI DLC.' }
}
foreach ($taskName in $taskFiles) {
    $taskSaved = Join-Path $taskBackup $taskName
    if (Test-Path -LiteralPath $taskSaved) {
        if ((Get-FileHash -LiteralPath $taskSaved).Hash.ToLowerInvariant() -ne $taskManifest.installedBefore.$taskName) { throw 'Резервная копия изменилась.' }
    } else {
        if ((Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.installedBefore.$taskName) { throw 'Нет исходного fix11 для копии.' }
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($taskSaved)) -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $taskMod $taskName) -Destination $taskSaved
    }
}
$taskMutated = $false
try {
    foreach ($taskName in $taskFiles) {
        $taskTarget = Join-Path $taskMod $taskName
        if ((Get-FileHash -LiteralPath $taskTarget).Hash.ToLowerInvariant() -eq $taskManifest.installFiles.$taskName) { continue }
        $taskTemp = $taskTarget + '.fix12tmp'
        if (Test-Path -LiteralPath $taskTemp) {
            if ((Get-FileHash -LiteralPath $taskTemp).Hash.ToLowerInvariant() -ne $taskManifest.installFiles.$taskName) { throw 'Неизвестный временный файл.' }
            Remove-Item -LiteralPath $taskTemp
        }
        Copy-Item -LiteralPath (Join-Path $taskCandidate $taskName) -Destination $taskTemp
        $taskReplaced = Join-Path (Join-Path $taskBuild 'replaced-files') $taskName
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($taskReplaced)) -Force | Out-Null
        $taskMutated = $true
        [IO.File]::Replace($taskTemp, $taskTarget, $taskReplaced)
    }
    foreach ($taskName in $taskFiles) {
        if ((Get-FileHash -LiteralPath (Join-Path $taskMod $taskName)).Hash.ToLowerInvariant() -ne $taskManifest.installFiles.$taskName) { throw 'Установленный SHA отличается.' }
    }
    @{ version=$taskManifest.version; backup=$taskBackup; installedFiles=$taskManifest.installFiles; gameLaunched=$false } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskBuild 'installation.json') -Encoding utf8
    Write-Output 'Fix12 установлен и проверен по SHA. Игра не запускалась.'
} catch {
    if ($taskMutated) {
        foreach ($taskName in $taskFiles) { [IO.File]::Copy((Join-Path $taskBackup $taskName), (Join-Path $taskMod $taskName), $true) }
    }
    throw
}
