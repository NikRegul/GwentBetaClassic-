param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$sourcePath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if ((Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Original Beta baseline changed' }
$source = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($sourcePath)
$target = [Mono.Cecil.AssemblyDefinition]::CreateAssembly([Mono.Cecil.AssemblyNameDefinition]::new('BetaPowerNumericExtract', [version]'1.0.0.0'), 'BetaPowerNumericExtract.dll', [Mono.Cecil.ModuleKind]::Dll)
$selectedNames = @('get_BasePower','set_BasePower','get_PermanentPower','set_PermanentPower',
    'get_CurrentPower','set_CurrentPower','get_CurrentArmor','set_CurrentArmor',
    'SetPower','SetArmor','SetBasePower','SetPermanentPower','SetBasePowerAndArmor',
    'SetPermanentPowerAndArmor','RestorePower','AddArmor','MultiplyArmor','MultiplyValue')
$originalType = $source.MainModule.Types | Where-Object FullName -eq 'GwentGameplay.CardPower'
$copyType = [Mono.Cecil.TypeDefinition]::new('GwentGameplay', 'CardPower', [Mono.Cecil.TypeAttributes]::Public, $target.MainModule.TypeSystem.Object)
$target.MainModule.Types.Add($copyType)
$originalMethods = @($originalType.Methods | Where-Object { $_.Name -in $selectedNames })
if ($originalMethods.Count -ne 18) { throw 'Unexpected numeric method selection' }
$methods = @{}; $fields = @{}
function Convert-Type([Mono.Cecil.TypeReference]$Type) {
    if ($Type.FullName -eq $copyType.FullName) { return $copyType }
    if ($Type.FullName.StartsWith('System.')) { return $target.MainModule.ImportReference($Type) }
    throw "Unexpected type: $Type"
}
foreach ($method in $originalMethods) {
    $copy = [Mono.Cecil.MethodDefinition]::new($method.Name, $method.Attributes, (Convert-Type $method.ReturnType))
    foreach ($param in $method.Parameters) { $copy.Parameters.Add([Mono.Cecil.ParameterDefinition]::new($param.Name, $param.Attributes, (Convert-Type $param.ParameterType))) }
    $copyType.Methods.Add($copy); $methods[$method.FullName] = $copy
}
$referencedFields = @($originalMethods | ForEach-Object { $_.Body.Instructions } | Where-Object { $_.Operand -is [Mono.Cecil.FieldReference] } | ForEach-Object { $_.Operand.Resolve() })
foreach ($field in $referencedFields) {
    if ($fields.ContainsKey($field.FullName)) { continue }
    if ($field.DeclaringType.FullName -ne $copyType.FullName) { throw 'Unexpected external field' }
    $copy = [Mono.Cecil.FieldDefinition]::new($field.Name, $field.Attributes, (Convert-Type $field.FieldType))
    $copyType.Fields.Add($copy); $fields[$field.FullName] = $copy
}
# Single explicit seam: observe raw final-setter arguments; no clamping/events.
$callbackType = [System.Action[int,int]]
$callbackField = [Mono.Cecil.FieldDefinition]::new('_OracleSetPowerAndArmor', [Mono.Cecil.FieldAttributes]::Public, $target.MainModule.ImportReference($callbackType))
$copyType.Fields.Add($callbackField)
$shim = [Mono.Cecil.MethodDefinition]::new('SetPowerAndArmor', [Mono.Cecil.MethodAttributes]::Public, $target.MainModule.TypeSystem.Void)
$shim.Parameters.Add([Mono.Cecil.ParameterDefinition]::new('power', [Mono.Cecil.ParameterAttributes]::None, $target.MainModule.TypeSystem.Int32))
$shim.Parameters.Add([Mono.Cecil.ParameterDefinition]::new('armor', [Mono.Cecil.ParameterAttributes]::None, $target.MainModule.TypeSystem.Int32))
$copyType.Methods.Add($shim); $methods[$shim.FullName] = $shim
$shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_0))
$shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldfld, $callbackField))
$shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_1))
$shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_2))
$shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Callvirt, $target.MainModule.ImportReference($callbackType.GetMethod('Invoke'))))
$shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ret))
foreach ($method in $originalMethods) {
    $copy = $methods[$method.FullName]; $copy.Body.InitLocals = $method.Body.InitLocals; $copy.Body.MaxStackSize = $method.Body.MaxStackSize
    if ($method.Body.HasExceptionHandlers) { throw 'Unexpected exception handler' }
    foreach ($local in $method.Body.Variables) { $copy.Body.Variables.Add([Mono.Cecil.Cil.VariableDefinition]::new((Convert-Type $local.VariableType))) }
    $instructionMap = @{}
    foreach ($instruction in $method.Body.Instructions) {
        $cloned = [Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Nop); $cloned.OpCode = $instruction.OpCode
        $copy.Body.Instructions.Add($cloned); $instructionMap[$instruction.Offset] = $cloned
    }
    foreach ($instruction in $method.Body.Instructions) {
        $operand = $instruction.Operand
        if ($null -eq $operand) { continue }
        if ($operand -is [Mono.Cecil.Cil.Instruction]) { $operand = $instructionMap[$operand.Offset] }
        elseif ($operand -is [Mono.Cecil.Cil.VariableDefinition]) { $operand = $copy.Body.Variables[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.ParameterDefinition]) { $operand = $copy.Parameters[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.FieldReference]) { $operand = $fields[$operand.FullName] }
        elseif ($operand -is [Mono.Cecil.MethodReference]) {
            if ($methods.ContainsKey($operand.FullName)) { $operand = $methods[$operand.FullName] }
            elseif ($operand.DeclaringType.FullName.StartsWith('System.')) { $operand = $target.MainModule.ImportReference($operand) }
            else { throw "Unexpected method: $operand" }
        } elseif ($operand -is [Mono.Cecil.TypeReference]) { $operand = Convert-Type $operand }
        $instructionMap[$instruction.Offset].Operand = $operand
    }
}
$outDir = Join-Path $Workspace 'tools\oracle\beta-power-numeric-ref\reference'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir 'BetaPowerNumericExtract.dll'; $target.Write($outPath)
$verified = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($outPath)
if (@($verified.MainModule.AssemblyReferences | Where-Object { $_.Name -eq 'Assembly-CSharp' -or $_.Name -like 'Unity*' }).Count) { throw 'Unexpected original runtime reference' }
$checks = @(foreach ($method in $originalMethods) {
    $readBack = $verified.MainModule.Types | ForEach-Object Methods | Where-Object FullName -eq $method.FullName
    $before = ($method.Body.Instructions | ForEach-Object ToString) -join "`n"; $after = ($readBack.Body.Instructions | ForEach-Object ToString) -join "`n"
    if ($before -cne $after) { throw "Instruction mismatch: $($method.FullName)" }
    [ordered]@{signature=$method.FullName; instructions=$method.Body.Instructions.Count; exactInstructionMatch=$true}
})
[ordered]@{source=$sourcePath; sourceSha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash;
    extract=$outPath; extractSha256=(Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash;
    extractorSha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash;
    methods=$checks; shims=@($shim.FullName + ' -> raw argument callback, no state mutation');
    originalRuntimeReferencesAbsent=$true; originalCodeExecuted=$false;
    scope='18 exact CardPower numeric/accessor methods. One SetPowerAndArmor callback seam. No original Init/Reset, live card registry, armor absorption, events, death, banish or full power attack.'} |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-power-numeric-extraction.json') -Encoding utf8
$verified.Dispose(); $target.Dispose(); $source.Dispose()
Write-Output "Extracted and verified $($checks.Count) numeric methods, explicit seam1."
