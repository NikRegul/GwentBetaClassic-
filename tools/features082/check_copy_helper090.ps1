$ErrorActionPreference = 'Stop'
$deckTestRoot = Join-Path $PSScriptRoot '..\..\BetaGwent\build\release090-integrated\copy-helper-tests'
New-Item -ItemType Directory -Path $deckTestRoot -Force | Out-Null
$deckTestValid = 'BG1:32:200160:' + ((1..25 | ForEach-Object { '112102' }) -join ',')
$deckTestLast = 'BG1:32:200160:' + ((1..25 | ForEach-Object { '112105' }) -join ',')
$deckTestLog = Join-Path $deckTestRoot 'scriptslog.txt'
@(('[BetaGwent] BG1_EXPORT ' + $deckTestValid), ('[BetaGwent] BG1_EXPORT ' + $deckTestLast)) | Set-Content -LiteralPath $deckTestLog -Encoding UTF8
$script:deckCaptured = ''
function Set-Clipboard { param([string]$Value) $script:deckCaptured = $Value }
function Get-Clipboard { param([switch]$Raw) return $script:deckCaptured }
. (Join-Path $PSScriptRoot 'Copy-Deck-Code.ps1') -LogPath $deckTestLog | Out-Null
if ($script:deckCaptured -ne $deckTestLast) { throw 'Latest complete code was not copied.' }
$deckBadLog = Join-Path $deckTestRoot 'invalid.txt'
'[BetaGwent] BG1_EXPORT BG1:32:200160:112102,112105' | Set-Content -LiteralPath $deckBadLog -Encoding UTF8
$script:deckCaptured = ''
$deckRejected = $false
try { . (Join-Path $PSScriptRoot 'Copy-Deck-Code.ps1') -LogPath $deckBadLog | Out-Null } catch { $deckRejected = $true }
if (-not $deckRejected -or $script:deckCaptured) { throw 'Incomplete export was accepted.' }
$deckChecks = 2
foreach ($deckBadSuffix in @(
    'BG1:32:200160:112102,112105',
    ($deckTestLast + ',112105,112105,112105,112105,112105,112105,112105,112105,112105,112105,112105,112105,112105,112105,112105,112105'),
    ($deckTestLast + ' extra text'),
    ($deckTestLast.Replace('BG1:32:', 'BG1:99:')),
    ($deckTestLast.Replace(':200160:', ':0:')),
    ($deckTestLast + ',')
)) {
    @(('[BetaGwent] BG1_EXPORT ' + $deckTestValid), ('[BetaGwent] BG1_EXPORT ' + $deckBadSuffix)) | Set-Content -LiteralPath $deckBadLog -Encoding UTF8
    $script:deckCaptured = ''
    $deckRejected = $false
    try { . (Join-Path $PSScriptRoot 'Copy-Deck-Code.ps1') -LogPath $deckBadLog | Out-Null } catch { $deckRejected = $true }
    if (-not $deckRejected -or $script:deckCaptured) { throw 'Invalid latest export fell back to an older deck.' }
    $deckChecks++
}
$deckLiveLog = Join-Path $deckTestRoot 'live [writer].txt'
$deckWriter = [IO.File]::Open($deckLiveLog, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
try {
    $deckBytes = [Text.Encoding]::UTF8.GetBytes('[BetaGwent] BG1_EXPORT ' + $deckTestLast + "`r`n")
    $deckWriter.Write($deckBytes,0,$deckBytes.Length); $deckWriter.Flush()
    . (Join-Path $PSScriptRoot 'Copy-Deck-Code.ps1') -LogPath $deckLiveLog | Out-Null
    if ($script:deckCaptured -ne $deckTestLast) { throw 'Could not read an actively written game log.' }
    $deckChecks++
} finally { $deckWriter.Dispose() }
@{ checks=$deckChecks; latestExportValidated=$true; staleFallbackRejected=$true; liveWriterCompatible=$true; realWindowsClipboardModified=$false } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $deckTestRoot 'result.json') -Encoding UTF8
Write-Output "Helper checks passed: $deckChecks; active writer, malformed latest export and stale fallback covered; actual clipboard untouched."
