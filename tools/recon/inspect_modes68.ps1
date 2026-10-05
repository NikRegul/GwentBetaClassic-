$ErrorActionPreference='Stop'
$taskAssemblyPath='D:\w3mod\Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if((Get-FileHash -LiteralPath $taskAssemblyPath).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F'){throw 'Original baseline changed'}
Add-Type -Path 'D:\w3mod\Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll'
$taskAssembly=[Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskAssemblyPath)
$taskLines=foreach($taskType in $taskAssembly.MainModule.Types){
 if($taskType.Namespace -ne 'GwentGameplay'){continue}
 foreach($taskMethod in $taskType.Methods){
  if(-not $taskMethod.HasBody){continue}
  if(($taskType.Name -eq 'Card' -and $taskMethod.Name -in @('Banish','Reset','CanDie')) -or
     ($taskType.Name -eq 'CardManager' -and $taskMethod.Name -eq 'KillWaitingToDie') -or
     ($taskType.Name -eq 'CardBanishAttack' -and $taskMethod.Name -in @('CanAttack','OnApply','OnAfter')) -or
     ($taskType.Name -eq 'CardPower' -and $taskMethod.Name -in @('AddBasePower','SetBasePowerAndArmor','TryUseArmor','Reset','RestorePower')) -or
     ($taskType.Name -eq 'FilterCardPowerStateNode') -or
     ($taskType.Name -eq 'FilterCardPowerNode')){
   'METHOD '+$taskMethod.FullName
   $taskMethod.Body.Instructions | ForEach-Object ToString
  }
 }
}
$taskLines | Set-Content -LiteralPath 'D:\w3mod\docs\evidence\modes68-il.txt' -Encoding utf8
$taskAssembly.Dispose()
Write-Output 'Original reset/heal/base/banish IL captured; read-only metadata.'
