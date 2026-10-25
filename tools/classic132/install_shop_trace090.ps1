$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\w3mod\BetaGwent\build\classic090-shop-trace1'
$taskInstalled = 'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt\Mods\modBetaGwentClassic132\content\scripts'
$taskCandidate = Join-Path $taskRoot 'Mods\modBetaGwentClassic132\content\scripts'
$taskResult = Get-Content -LiteralPath 'D:\w3mod\BetaGwent\build\universal081\classic-runtime\runs\shop-trace090-3\result.json' -Raw | ConvertFrom-Json
$taskBefore = Get-Content -LiteralPath (Join-Path $taskRoot 'installed-before.json') -Raw | ConvertFrom-Json
$taskPrepared = Get-Content -LiteralPath (Join-Path $taskRoot 'preparation.json') -Raw | ConvertFrom-Json
$taskFiles = @('game/gui/menus/inventoryMenu.ws', 'game/betagwent/developmentBoardMenu.ws')
if (Get-Process -Name witcher3 -ErrorAction SilentlyContinue) { throw 'Close the game before installing the diagnostic patch.' }
if (-not $taskResult.compilePassed -or $taskResult.errors.Count -ne 0) { throw 'Native compilation has not passed.' }
$taskPrepHash = (Get-FileHash -LiteralPath (Join-Path $taskRoot 'preparation.json')).Hash.ToLowerInvariant()
if ($taskPrepHash -ne $taskResult.preparationManifestSha256) { throw 'Compiled preparation changed.' }
foreach ($taskName in $taskFiles) {
    $taskSource = Join-Path $taskCandidate $taskName
    $taskTarget = Join-Path $taskInstalled $taskName
    if ((Get-FileHash -LiteralPath $taskSource).Hash.ToLowerInvariant() -ne $taskPrepared.outputScripts.$taskName) { throw ('Candidate changed: ' + $taskName) }
    if ((Get-FileHash -LiteralPath $taskTarget).Hash.ToLowerInvariant() -ne $taskBefore.$taskName) { throw ('Installed script changed: ' + $taskName) }
}
foreach ($taskName in $taskFiles) {
    $taskBackup = Join-Path (Join-Path $taskRoot 'installed-before') $taskName
    if (Test-Path -LiteralPath $taskBackup) { throw ('Backup already exists: ' + $taskName) }
    New-Item -ItemType Directory -Path (Split-Path -Parent $taskBackup) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $taskInstalled $taskName) -Destination $taskBackup
}
foreach ($taskName in $taskFiles) {
    Copy-Item -LiteralPath (Join-Path $taskCandidate $taskName) -Destination (Join-Path $taskInstalled $taskName)
    if ((Get-FileHash -LiteralPath (Join-Path $taskInstalled $taskName)).Hash.ToLowerInvariant() -ne $taskPrepared.outputScripts.$taskName) { throw ('Installation mismatch: ' + $taskName) }
}
Write-Output 'Shop trace installed: two scripts. Inventory and saves were not modified. Open the affected merchant, then close the game.'
