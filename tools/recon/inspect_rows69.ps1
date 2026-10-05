$ErrorActionPreference='Stop'
$taskAssemblyPath='D:\w3mod\Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if((Get-FileHash -LiteralPath $taskAssemblyPath).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F'){throw 'Original baseline changed'}
Add-Type -Path 'D:\w3mod\Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll'
$taskAssembly=[Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskAssemblyPath)
$taskLines=foreach($taskType in $taskAssembly.MainModule.Types){
 if($taskType.Namespace -ne 'GwentGameplay'){continue}
 if($taskType.IsEnum -and $taskType.Name -in @('EMoveReason','ELocationToken')){
  'ENUM '+$taskType.FullName
  $taskType.Fields | Where-Object HasConstant | ForEach-Object { $_.Name+'='+$_.Constant }
 }
 foreach($taskMethod in $taskType.Methods){
  if(-not $taskMethod.HasBody){continue}
  if($taskType.Name -in @('AfterMovedTrigger','AfterChangedLocationTokenTrigger','AfterChangedCardTokenTrigger','APassiveTrigger','LocationTokenAbility','AfterPlayedTrigger') -or
     ($taskType.Name -eq 'AbilityManager' -and $taskMethod.Name -match 'Location|Trigger|AfterPlayed|AfterMoved') -or
     ($taskType.Name -eq 'PlayCardAction' -and $taskMethod.Name -match 'Apply|After') -or
     ($taskType.Name -eq 'RequestPlayCardAction' -and $taskMethod.Name -eq 'PlayCard') -or
     ($taskType.Name -eq 'Card' -and $taskMethod.Name -eq 'Play') -or
     ($taskType.Name -match 'Location.*Token' -and $taskMethod.Name -match 'Add|Set|Remove|Change') -or
     ($taskType.Name -in @('Location','ChangeLocationTokensAction','LocationTokensAttack') -and $taskMethod.Name -match 'Token|PrepareAttack|ApplyImpl|OnApply|OnAfter') -or
     ($taskType.Name -eq 'PlayCardsAction' -and $taskMethod.Name -match 'Apply|After') -or
     ($taskType.Name -eq 'ExecutionStack' -and $taskMethod.Name -match 'PopCard|ExecuteNext') -or
     ($taskType.Name -eq 'BoardManager' -and $taskMethod.Name -match 'Move|Token')){
   'METHOD '+$taskMethod.FullName
   $taskMethod.Body.Instructions | ForEach-Object ToString
  }
 }
}
$taskLines | Set-Content -LiteralPath 'D:\w3mod\docs\evidence\rows69-il.txt' -Encoding utf8
$taskAssembly.Dispose()
