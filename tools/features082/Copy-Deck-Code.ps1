param([string]$LogPath)
$ErrorActionPreference = 'Stop'
if (-not $LogPath) {
    $deckLogCandidates = @(
        (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'The Witcher 3\scriptslog.txt'),
        (Join-Path $env:USERPROFILE 'Documents\The Witcher 3\scriptslog.txt')
    ) | Select-Object -Unique
    $deckLogFile = $deckLogCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        ForEach-Object { Get-Item -LiteralPath $_ } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $deckLogFile) { throw 'scriptslog.txt not found. Launch the game with -debugscripts and export a deck first.' }
    $LogPath = $deckLogFile.FullName
}
$deckLogStream = [IO.File]::Open((Resolve-Path -LiteralPath $LogPath).Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
$deckLogReader = $null
try {
    $deckLogReader = New-Object IO.StreamReader($deckLogStream, [Text.Encoding]::UTF8, $true)
    $deckLogText = $deckLogReader.ReadToEnd()
} finally {
    if ($deckLogReader) { $deckLogReader.Dispose() } else { $deckLogStream.Dispose() }
}
$deckCodeMatches = [regex]::Matches($deckLogText, 'BG1_EXPORT[ \t]+([^\r\n]*)')
if ($deckCodeMatches.Count -eq 0) { throw 'No exported deck found. Use the updated mod, launch with -debugscripts, export a valid deck, and run this helper before restarting the game.' }
$deckCode = $deckCodeMatches[$deckCodeMatches.Count - 1].Groups[1].Value.Trim()
if ($deckCode -notmatch '\ABG1:(?:2|4|8|16|32):[1-9][0-9]*:[1-9][0-9]*(?:,[1-9][0-9]*){24,39}\z') { throw 'The latest export is incomplete or invalid. Export the deck again and retry; an older deck was not copied.' }
if ($deckCode.Length -gt 320) { throw 'Exported code exceeds the BG1 length limit.' }
Set-Clipboard -Value $deckCode
if ((Get-Clipboard -Raw).TrimEnd("`r", "`n") -ne $deckCode) { throw 'Windows clipboard verification failed. Run the helper again.' }
Write-Output 'The latest exported BG1 deck code is in the Windows clipboard. Paste it into your message with Ctrl+V.'
