param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$sourcePath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if ((Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Original baseline changed' }
$source = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($sourcePath)
$target = [Mono.Cecil.AssemblyDefinition]::CreateAssembly([Mono.Cecil.AssemblyNameDefinition]::new('BetaDeathEntryExtract', [version]'1.0.0.0'), 'BetaDeathEntryExtract.dll', [Mono.Cecil.ModuleKind]::Dll)
$types = @{}; $methods = @{}; $fields = @{}
foreach ($name in @('Card','CardTemplate','CardPosition','CardData','CardPower','CardManager','ECardType','ELocation')) {
    $old = $source.MainModule.Types | Where-Object FullName -eq "GwentGameplay.$name"
    if ($null -eq $old) { throw "Missing type $name" }
    $base = $target.MainModule.TypeSystem.Object
    $attributes = [Mono.Cecil.TypeAttributes]::Public
    if ($old.IsEnum) { $base = $target.MainModule.ImportReference([System.Enum]); $attributes = $old.Attributes }
    elseif ($old.IsValueType) { $base = $target.MainModule.ImportReference([System.ValueType]); $attributes = $old.Attributes }
    $copy = [Mono.Cecil.TypeDefinition]::new($old.Namespace, $old.Name, $attributes, $base)
    $types[$old.FullName] = $copy; $target.MainModule.Types.Add($copy)
}
function Convert-Type([Mono.Cecil.TypeReference]$Type) {
    if ($types.ContainsKey($Type.FullName)) { return $types[$Type.FullName] }
    if ($Type.FullName.StartsWith('System.')) { return $target.MainModule.ImportReference($Type) }
    throw "Unexpected type $Type"
}
$originalMethods = @($source.MainModule.Types | ForEach-Object Methods | Where-Object {
    ($_.DeclaringType.FullName -eq 'GwentGameplay.Card' -and $_.Name -in @('CanDie','Kill','get_IsWaitingToDie','set_IsWaitingToDie')) -or
    ($_.DeclaringType.FullName -eq 'GwentGameplay.CardPosition' -and $_.Name -eq 'get_IsActive')
})
if ($originalMethods.Count -ne 5) { throw 'Expected death entry methods5' }
function Add-Method([Mono.Cecil.MethodDefinition]$Old) {
    $copy = [Mono.Cecil.MethodDefinition]::new($Old.Name, $Old.Attributes, (Convert-Type $Old.ReturnType))
    foreach ($param in $Old.Parameters) { $copy.Parameters.Add([Mono.Cecil.ParameterDefinition]::new($param.Name, $param.Attributes, (Convert-Type $param.ParameterType))) }
    $types[$Old.DeclaringType.FullName].Methods.Add($copy); $methods[$Old.FullName] = $copy
    return $copy
}
foreach ($method in $originalMethods) { Add-Method $method | Out-Null }
$referencedFields = @($originalMethods | ForEach-Object { $_.Body.Instructions } | Where-Object { $_.Operand -is [Mono.Cecil.FieldReference] } | ForEach-Object { $_.Operand.Resolve() })
$referencedFields += @($source.MainModule.Types | Where-Object { $_.FullName -in @('GwentGameplay.ECardType','GwentGameplay.ELocation') } | ForEach-Object Fields)
foreach ($old in $referencedFields) {
    if ($fields.ContainsKey($old.FullName)) { continue }
    $copy = [Mono.Cecil.FieldDefinition]::new($old.Name, $old.Attributes, (Convert-Type $old.FieldType))
    if ($old.HasConstant) { $copy.Constant = $old.Constant }
    $types[$old.DeclaringType.FullName].Fields.Add($copy); $fields[$old.FullName] = $copy
}
# Exactly ten callback seams. They observe dependency calls, not manager/power behavior.
$seamSpecs = @(
    @('Card','get_Template'), @('Card','get_Position'), @('Card','get_IsInExecutionStack'),
    @('Card','get_Data'), @('Card','get_CardManager'), @('CardData','get_Card'),
    @('CardData','get_Power'), @('CardPower','get_CurrentPower'),
    @('CardPower','SetPower'), @('CardManager','MarkAsWaitingToDie')
)
$shims = @(foreach ($spec in $seamSpecs) {
    $old = $source.MainModule.Types | Where-Object FullName -eq ('GwentGameplay.' + $spec[0]) | ForEach-Object Methods | Where-Object Name -eq $spec[1]
    if (@($old).Count -ne 1) { throw "Ambiguous seam $spec" }
    $copy = Add-Method $old
    if ($copy.ReturnType.FullName -eq 'System.Boolean') { $delegate = [System.Func[bool]] }
    elseif ($copy.ReturnType.FullName -eq 'System.Int32') { $delegate = [System.Func[int]] }
    elseif ($copy.ReturnType.FullName -ne 'System.Void') { $delegate = [System.Func[object]] }
    elseif ($copy.Parameters.Count -eq 1 -and $copy.Parameters[0].ParameterType.FullName -eq 'System.Int32') { $delegate = [System.Action[int]] }
    elseif ($copy.Parameters.Count -eq 1 -and $copy.Parameters[0].ParameterType.FullName -eq 'GwentGameplay.Card') { $delegate = [System.Action[object]] }
    else { throw "Unsupported seam $($old.FullName)" }
    $field = [Mono.Cecil.FieldDefinition]::new(('_Oracle_' + $copy.Name), [Mono.Cecil.FieldAttributes]::Public, $target.MainModule.ImportReference($delegate))
    $types[$old.DeclaringType.FullName].Fields.Add($field)
    $copy.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_0))
    $copy.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldfld, $field))
    if ($copy.Parameters.Count -eq 1) { $copy.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_1)) }
    $copy.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Callvirt, $target.MainModule.ImportReference($delegate.GetMethod('Invoke'))))
    if ($delegate -eq [System.Func[object]]) {
        $op = [Mono.Cecil.Cil.OpCodes]::Castclass
        if ($copy.ReturnType.IsValueType) { $op = [Mono.Cecil.Cil.OpCodes]::Unbox_Any }
        $copy.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create($op, $copy.ReturnType))
    }
    $copy.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ret))
    [ordered]@{signature=$copy.FullName; callback=$field.Name; scope='Dependency callback only; original dependency body not copied.'}
})
foreach ($method in $originalMethods) {
    $copy = $methods[$method.FullName]; $copy.Body.InitLocals = $method.Body.InitLocals; $copy.Body.MaxStackSize = $method.Body.MaxStackSize
    if ($method.Body.HasExceptionHandlers) { throw 'Unexpected exception handler' }
    foreach ($local in $method.Body.Variables) { $copy.Body.Variables.Add([Mono.Cecil.Cil.VariableDefinition]::new((Convert-Type $local.VariableType))) }
    $map = @{}
    foreach ($instruction in $method.Body.Instructions) {
        $cloned = [Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Nop); $cloned.OpCode = $instruction.OpCode
        $copy.Body.Instructions.Add($cloned); $map[$instruction.Offset] = $cloned
    }
    foreach ($instruction in $method.Body.Instructions) {
        $operand = $instruction.Operand
        if ($null -eq $operand) { continue }
        if ($operand -is [Mono.Cecil.Cil.Instruction]) { $operand = $map[$operand.Offset] }
        elseif ($operand -is [Mono.Cecil.Cil.VariableDefinition]) { $operand = $copy.Body.Variables[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.ParameterDefinition]) { $operand = $copy.Parameters[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.FieldReference]) { $operand = $fields[$operand.FullName] }
        elseif ($operand -is [Mono.Cecil.MethodReference]) {
            if (!$methods.ContainsKey($operand.FullName)) { throw "Unexpected method $operand" }
            $operand = $methods[$operand.FullName]
        } elseif ($operand -is [Mono.Cecil.TypeReference]) { $operand = Convert-Type $operand }
        $map[$instruction.Offset].Operand = $operand
    }
}
$outDir = Join-Path $Workspace 'tools\oracle\beta-death-entry-ref\reference'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir 'BetaDeathEntryExtract.dll'; $target.Write($outPath)
$verified = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($outPath)
if (@($verified.MainModule.AssemblyReferences | Where-Object { $_.Name -eq 'Assembly-CSharp' -or $_.Name -like 'Unity*' }).Count) { throw 'Unexpected original runtime reference' }
$checks = @(foreach ($method in $originalMethods) {
    $readBack = $verified.MainModule.Types | ForEach-Object Methods | Where-Object FullName -eq $method.FullName
    $before = ($method.Body.Instructions | ForEach-Object ToString) -join "`n"; $after = ($readBack.Body.Instructions | ForEach-Object ToString) -join "`n"
    if ($before -cne $after) { throw "Instruction mismatch $($method.FullName)" }
    [ordered]@{signature=$method.FullName; instructions=$method.Body.Instructions.Count; exactInstructionMatch=$true}
})
[ordered]@{source=$sourcePath; sourceSha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash;
    extract=$outPath; extractSha256=(Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash;
    extractorSha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash;
    methods=$checks; shims=$shims; originalRuntimeReferencesAbsent=$true; originalCodeExecuted=$false;
    scope='Five exact Card CanDie/Kill/waiting accessors and CardPosition.IsActive methods. Ten dependency callback seams. No real power setter, MarkAsWaitingToDie ordering/authority, drain, unregister or full death acceptance.'} |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-death-entry-extraction.json') -Encoding utf8
$verified.Dispose(); $target.Dispose(); $source.Dispose()
Write-Output 'Extracted death entry5; verified exact IL; dependency seams10.'
