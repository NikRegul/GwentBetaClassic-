Add-Type -Path 'D:\w3mod\Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly('D:\w3mod\Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll')
try {
 $taskLines = @(foreach ($taskType in $taskAssembly.MainModule.Types | Where-Object { $_.FullName -eq 'GwentGameplay.BitArray' }) {
  'TYPE ' + $taskType.FullName
  $taskType.Fields | ForEach-Object { 'FIELD ' + $_.FullName }
  $taskType.Methods | ForEach-Object { 'METHOD ' + $_.FullName }
 })
 $taskLines | Set-Content -LiteralPath 'D:\w3mod\docs\evidence\beta-bitarray-metadata.txt' -Encoding utf8
 $taskLines
}
finally { $taskAssembly.Dispose() }
