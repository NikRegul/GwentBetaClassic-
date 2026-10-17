$ErrorActionPreference = 'Stop'
$taskBuild = 'D:\w3mod\BetaGwent\build\classic081-guid-fix7'
$taskGame = 'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'
$taskMod = Join-Path $taskGame 'Mods\modBetaGwentClassic132'
$taskBundle = Join-Path $taskMod 'content\blob0.bundle'
$taskInfo = Join-Path $taskMod 'info.json'
$taskCandidate = Join-Path $taskBuild 'resources-classic\blob0.bundle'
$taskReceipt = Get-Content -LiteralPath (Join-Path $taskBuild 'verification.json') -Raw | ConvertFrom-Json
$taskVersion = '0.8.1-classic-bundle-guids-fix7'

if (@(Get-Process -Name witcher3 -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Игра запущена. Установка отменена без изменений; сначала закройте игру.'
}
if (Test-Path -LiteralPath (Join-Path $taskGame 'Mods\mod000BetaGwentClassic132Probe')) {
    throw 'Осталась диагностическая накладка. Установка отменена без изменений.'
}
$taskCurrent = Get-Content -LiteralPath $taskInfo -Raw | ConvertFrom-Json
$taskCurrentHash = (Get-FileHash -LiteralPath $taskBundle -Algorithm SHA256).Hash.ToLowerInvariant()
if ($taskCurrentHash -eq $taskReceipt.bundleSha256 -and $taskCurrent.version -eq $taskVersion) {
    Write-Output 'Fix7 уже установлен.'
    exit 0
}
if ($taskCurrent.version -ne '0.8.1-classic-dependencies-fix6') {
    throw 'Ожидалась установленная сборка fix6; файлы не изменены.'
}
$taskOldHash = '97db5e631cffff8a8466fff61d2853eaa35253d882706cae938cf87e265425c8'
if ($taskCurrentHash -ne $taskOldHash) { throw 'Исходный bundle отличается от fix6; файлы не изменены.' }
if ((Get-FileHash -LiteralPath $taskCandidate -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskReceipt.bundleSha256) {
    throw 'Подготовленный fix7 не совпадает с проверенным отчётом.'
}
foreach ($taskName in @('metadata.store', 'dep.cache')) {
    $taskActual = (Get-FileHash -LiteralPath (Join-Path $taskMod ('content\' + $taskName))).Hash
    $taskExpected = (Get-FileHash -LiteralPath (Join-Path $taskBuild ('resources-classic\' + $taskName))).Hash
    if ($taskActual -ne $taskExpected) { throw ('Не совпадает ' + $taskName + '; файлы не изменены.') }
}
$taskBackup = Join-Path $taskBuild 'installed-before'
$taskBackupResolved = [System.IO.Path]::GetFullPath($taskBackup)
if (-not $taskBackupResolved.StartsWith([System.IO.Path]::GetFullPath($taskBuild) + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Резервная копия должна быть внутри каталога fix7.'
}
if (Test-Path -LiteralPath $taskBackup) {
    if ((Get-FileHash -LiteralPath (Join-Path $taskBackup 'blob0.bundle')).Hash.ToLowerInvariant() -ne $taskOldHash) {
        throw 'Существующая резервная копия bundle не совпадает с fix6.'
    }
    $taskBackupInfo = Get-Content -LiteralPath (Join-Path $taskBackup 'info.json') -Raw | ConvertFrom-Json
    if ($taskBackupInfo.version -ne '0.8.1-classic-dependencies-fix6') { throw 'Неверная версия резервной копии.' }
}
else {
    New-Item -ItemType Directory -Path $taskBackup | Out-Null
    Copy-Item -LiteralPath $taskBundle -Destination (Join-Path $taskBackup 'blob0.bundle')
    Copy-Item -LiteralPath $taskInfo -Destination (Join-Path $taskBackup 'info.json')
}
$taskTempBundle = $taskBundle + '.fix7tmp'
$taskTempInfo = $taskInfo + '.fix7tmp'
if (Test-Path -LiteralPath $taskTempBundle) {
    if ((Get-FileHash -LiteralPath $taskTempBundle).Hash.ToLowerInvariant() -ne $taskReceipt.bundleSha256) {
        throw 'Существующий временный bundle отличается от fix7.'
    }
}
else { Copy-Item -LiteralPath $taskCandidate -Destination $taskTempBundle }
if (Test-Path -LiteralPath $taskTempInfo) {
    if ((Get-FileHash -LiteralPath $taskTempInfo).Hash -ne (Get-FileHash -LiteralPath (Join-Path $taskBuild 'info.json')).Hash) {
        throw 'Существующий временный info.json отличается от fix7.'
    }
}
else { Copy-Item -LiteralPath (Join-Path $taskBuild 'info.json') -Destination $taskTempInfo }
$taskReplaced = $false
try {
    [System.IO.File]::Replace($taskTempBundle, $taskBundle, (Join-Path $taskBackup 'blob0.bundle'))
    $taskReplaced = $true
    [System.IO.File]::Replace($taskTempInfo, $taskInfo, (Join-Path $taskBackup 'info.json'))
    if ((Get-FileHash -LiteralPath $taskBundle).Hash.ToLowerInvariant() -ne $taskReceipt.bundleSha256) {
        throw 'Установленный bundle не прошёл сверку SHA-256.'
    }
    @{
        version = $taskVersion
        game = $taskGame
        backup = $taskBackup
        bundleSha256 = $taskReceipt.bundleSha256
        metadataAndDependenciesUnchanged = $true
        gameLaunched = $false
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskBuild 'installation.json') -Encoding utf8
    Write-Output ('Fix7 установлен. Резервная копия: ' + $taskBackup)
    Write-Output 'Игра не запускалась.'
}
catch {
    if ($taskReplaced) {
        [System.IO.File]::Copy((Join-Path $taskBackup 'blob0.bundle'), $taskBundle, $true)
        [System.IO.File]::Copy((Join-Path $taskBackup 'info.json'), $taskInfo, $true)
    }
    throw
}
