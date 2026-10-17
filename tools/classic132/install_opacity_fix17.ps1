$ErrorActionPreference = 'Stop'
$taskBuild = 'D:\w3mod\BetaGwent\build\classic081-opacity-fix17'
$taskGame = 'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'
$taskBackup = Join-Path $taskBuild 'installed-before'
$taskManifest = Get-Content -LiteralPath (Join-Path $taskBuild 'install-manifest.json') -Raw | ConvertFrom-Json
$taskAudit = Get-Content -LiteralPath (Join-Path $taskBuild 'structural-audit.json') -Raw | ConvertFrom-Json
$taskDLCAudit = Get-Content -LiteralPath (Join-Path $taskBuild 'dlc-audit.json') -Raw | ConvertFrom-Json
if (@(Get-Process -Name witcher3 -ErrorAction SilentlyContinue).Count) { throw 'Game is running; files unchanged.' }
if ($taskManifest.sourceVersion -ne '0.8.1-classic-effect-state-leaders-fix16' -or
    $taskAudit.structuralIssues.Count -ne 0 -or $taskAudit.checks.Count -ne 16 -or -not $taskDLCAudit.passed) { throw 'Candidate audit missing.' }
$taskMods = @(Get-ChildItem -LiteralPath (Join-Path $taskGame 'Mods') -Directory)
if ($taskMods.Count -ne 1 -or $taskMods[0].Name -ne 'modBetaGwentClassic132') { throw 'Active mods changed.' }
foreach ($taskProperty in $taskManifest.preservedFiles.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path (Join-Path $taskGame 'Mods/modBetaGwentClassic132') $taskProperty.Name)).Hash.ToLowerInvariant() -ne $taskProperty.Value) { throw 'Accepted audio changed.' }
}
$taskFiles = @()
foreach ($taskProperty in $taskManifest.installFiles.PSObject.Properties) {
    $taskFiles += @{ path=('Mods/modBetaGwentClassic132/' + $taskProperty.Name); before=$taskManifest.installedBefore.($taskProperty.Name); after=$taskProperty.Value }
}
foreach ($taskProperty in $taskManifest.dlcFiles.PSObject.Properties) {
    $taskFiles += @{ path=('DLC/dlcBetaGwentClassic132Assets/' + $taskProperty.Name); before=$taskManifest.dlcInstalledBefore.($taskProperty.Name); after=$taskProperty.Value }
}
if ($taskFiles.Count -ne 7) { throw 'Unexpected install coverage.' }
foreach ($taskFile in $taskFiles) {
    $taskTarget = Join-Path $taskGame $taskFile.path
    $taskCandidate = Join-Path (Join-Path $taskBuild 'package') $taskFile.path
    $taskCurrent = (Get-FileHash -LiteralPath $taskTarget).Hash.ToLowerInvariant()
    if ($taskCurrent -ne $taskFile.before -and $taskCurrent -ne $taskFile.after) { throw ('Installed file changed: '+$taskFile.path) }
    if ((Get-FileHash -LiteralPath $taskCandidate).Hash.ToLowerInvariant() -ne $taskFile.after) { throw ('Candidate changed: '+$taskFile.path) }
    $taskSaved = Join-Path $taskBackup $taskFile.path
    if (Test-Path -LiteralPath $taskSaved) {
        if ((Get-FileHash -LiteralPath $taskSaved).Hash.ToLowerInvariant() -ne $taskFile.before) { throw 'Backup changed.' }
    } else {
        if ($taskCurrent -ne $taskFile.before) { throw 'Original version required for backup.' }
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($taskSaved)) -Force | Out-Null
        Copy-Item -LiteralPath $taskTarget -Destination $taskSaved
    }
}
$taskMutated = $false
try {
    foreach ($taskFile in $taskFiles) {
        $taskTarget = Join-Path $taskGame $taskFile.path
        if ((Get-FileHash -LiteralPath $taskTarget).Hash.ToLowerInvariant() -eq $taskFile.after) { continue }
        $taskTemp = $taskTarget + '.fix17tmp'
        if (Test-Path -LiteralPath $taskTemp) { throw 'Unexpected temporary file; no overwrite.' }
        Copy-Item -LiteralPath (Join-Path (Join-Path $taskBuild 'package') $taskFile.path) -Destination $taskTemp
        $taskReplaced = Join-Path (Join-Path $taskBuild 'replaced-files') $taskFile.path
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($taskReplaced)) -Force | Out-Null
        $taskMutated = $true
        [IO.File]::Replace($taskTemp, $taskTarget, $taskReplaced)
    }
    foreach ($taskFile in $taskFiles) {
        if ((Get-FileHash -LiteralPath (Join-Path $taskGame $taskFile.path)).Hash.ToLowerInvariant() -ne $taskFile.after) { throw 'Installed SHA mismatch.' }
    }
    @{ version=$taskManifest.version; backup=$taskBackup; installedFiles=$taskFiles; gameLaunched=$false } |
        ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskBuild 'installation.json') -Encoding utf8
    Write-Output 'Fix17 installed; Mods and GUI DLC verified by SHA. Game not launched.'
} catch {
    if ($taskMutated) {
        foreach ($taskFile in $taskFiles) { [IO.File]::Copy((Join-Path $taskBackup $taskFile.path), (Join-Path $taskGame $taskFile.path), $true) }
    }
    throw
}
