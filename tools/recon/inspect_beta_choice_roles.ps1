$ErrorActionPreference = 'Stop'
Add-Type -Path 'D:\w3mod\Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly('D:\w3mod\Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll')
try {
 $taskLines = @(foreach ($taskType in $taskAssembly.MainModule.Types | Where-Object { $_.FullName -in @('GwentGameplay.Card','GwentGameplay.RequestCardChoicesAction','GwentGameplay.ARequestAction') }) {
  foreach ($taskMethod in $taskType.Methods | Where-Object { ($taskType.Name -eq 'Card' -and $_.Name -eq 'GetPlayerId') -or ($taskType.Name -ne 'Card' -and $_.Name -eq 'Init') }) {
   'METHOD ' + $taskMethod.FullName
   foreach ($taskParameter in $taskMethod.Parameters) { 'PARAM ' + $taskParameter.Index + ' ' + $taskParameter.Name + ' ' + $taskParameter.ParameterType }
   $taskMethod.Body.Instructions | ForEach-Object ToString
  }
 })
 $taskLines | Set-Content -LiteralPath 'D:\w3mod\docs\evidence\beta-choice-roles-il.txt' -Encoding utf8
 $taskLines
}
finally { $taskAssembly.Dispose() }
