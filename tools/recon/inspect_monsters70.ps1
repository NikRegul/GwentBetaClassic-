$ErrorActionPreference='Stop'
$taskAssemblyPath='D:\w3mod\Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if((Get-FileHash -LiteralPath $taskAssemblyPath).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F'){throw 'Original changed'}
Add-Type -Path 'D:\w3mod\Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll'
$taskAssembly=[Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskAssemblyPath)
$taskLines=foreach($taskType in $taskAssembly.MainModule.Types){
 if($taskType.Namespace -ne 'GwentGameplay'){continue}
 if($taskType.IsEnum -and $taskType.Name -in @('EAttackMethod','ECardCategory','EResetMode','EAvailability','EActionOnTrigger')){'ENUM '+$taskType.FullName;$taskType.Fields|Where-Object HasConstant|ForEach-Object{$_.Name+'='+$_.Constant}}
 foreach($taskMethod in $taskType.Methods){
  if($taskMethod.HasBody -and (($taskType.Name -in @('ACardAttack','CardDestroyAttack','CardDestroyAttackAction') -and $taskMethod.Name -match 'Add|OnApply|PrepareAttack') -or ($taskType.Name -in @('GetCardsDefinitionsNode','AGetDefinitionsNode','APassiveTrigger')) -or ($taskType.Name -eq 'AbilityManager' -and $taskMethod.Name -match 'Trigger|OnCardMoved|AddAbilityInstance|AbortFor|^Add$|^Step$') -or ($taskType.Name -eq 'CardData' -and $taskMethod.Name -match 'Attack|Destroyed|Banished'))){
   'METHOD '+$taskMethod.FullName;$taskMethod.Body.Instructions|ForEach-Object ToString
  }
 }
}
$taskLines|Set-Content -LiteralPath 'D:\w3mod\docs\evidence\monsters70-il.txt' -Encoding utf8
$taskAssembly.Dispose()
