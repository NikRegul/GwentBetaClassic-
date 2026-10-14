$ErrorActionPreference='Stop'
$TaskRoot=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Add-Type -Path (Join-Path $TaskRoot 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$TaskDll=Join-Path $TaskRoot 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$TaskBefore=(Get-FileHash -LiteralPath $TaskDll -Algorithm SHA256).Hash
$TaskAssembly=[Mono.Cecil.AssemblyDefinition]::ReadAssembly($TaskDll)
$TaskNames=@('CardPowerAttackVisualEffect','CardAttackVisualEffect','LocationAttackVisualEffect','BoardAttackVisualEffect','BezierProjectileVisualEffect','ProjectileVisualEffect','BezierProjectileSettings','VisualEffect','ParticleVisualEffect','ParticleSystemsWrapper','ParticleSystemVisualEffect')
$TaskTypes=@($TaskAssembly.MainModule.Types | Where-Object {$_.Name -in $TaskNames})
$TaskLines=[System.Collections.Generic.List[string]]::new()
foreach($TaskType in $TaskTypes){
 $TaskLines.Add('TYPE '+$TaskType.FullName+' BASE '+$TaskType.BaseType)
 foreach($TaskField in $TaskType.Fields){$TaskLines.Add('FIELD '+$TaskField.FullName)}
 foreach($TaskMethod in $TaskType.Methods){
  $TaskLines.Add('METHOD '+$TaskMethod.FullName)
  if($TaskMethod.HasBody){foreach($TaskInstruction in $TaskMethod.Body.Instructions){$TaskLines.Add([string]$TaskInstruction)}}
 }
}
$TaskAssembly.Dispose()
if((Get-FileHash -LiteralPath $TaskDll -Algorithm SHA256).Hash -ne $TaskBefore){throw 'Original assembly changed'}
$TaskLines | Set-Content -LiteralPath (Join-Path $TaskRoot 'docs/evidence/element-il164.txt') -Encoding utf8
Write-Output ('Extracted '+$TaskTypes.Count+' effect types, '+$TaskLines.Count+' IL lines')
