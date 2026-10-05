param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$sourcePath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$source = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($sourcePath)
$target = [Mono.Cecil.AssemblyDefinition]::CreateAssembly([Mono.Cecil.AssemblyNameDefinition]::new('BetaRequestExtract', [version]'1.0.0.0'), 'BetaRequestExtract.dll', [Mono.Cecil.ModuleKind]::Dll)
$selection = @{
    ARequestTargetsAction = @('get_MinTargets','set_MinTargets','get_MaxTargets','set_MaxTargets','get_PlayerFinishedTargeting','set_PlayerFinishedTargeting','ApplyImpl','OnTargetAdded','FinishTargetSelection')
    RequestCardChoicesAction = @('get_MinChoices','set_MinChoices','get_MaxChoices','set_MaxChoices','get_PlayerFinishedTargeting','set_PlayerFinishedTargeting','get_SelectedChoices','set_SelectedChoices','FinishChoiceSelection')
}
$types = @{}; $methods = @{}; $fields = @{}; $originalMethods = @()
foreach ($type in $source.MainModule.Types | Where-Object { $_.Namespace -eq 'GwentGameplay' -and $selection.ContainsKey($_.Name) }) {
    $attrs = [Mono.Cecil.TypeAttributes]::Public
    $base = $target.MainModule.TypeSystem.Object
    if ($type.IsEnum) { $attrs = $type.Attributes; $base = $target.MainModule.ImportReference([System.Enum]) }
    $copy = [Mono.Cecil.TypeDefinition]::new($type.Namespace, $type.Name, $attrs, $base)
    $target.MainModule.Types.Add($copy); $types[$type.FullName] = $copy
    $originalMethods += @($type.Methods | Where-Object { $_.Name -in $selection[$type.Name] -and ($_.Name -ne 'SetResult' -or $_.Parameters.Count -eq 2) })
}

function Convert-Type([Mono.Cecil.TypeReference]$Type) {
    if ($Type -is [Mono.Cecil.ArrayType]) { return [Mono.Cecil.ArrayType]::new((Convert-Type $Type.ElementType), $Type.Rank) }
    if ($types.ContainsKey($Type.FullName)) { return $types[$Type.FullName] }
    switch ($Type.FullName) {
        'System.Collections.Generic.List`1<System.UInt16>' { return $target.MainModule.ImportReference([System.Collections.Generic.List[uint16]]) }
        'System.Int32' { return $target.MainModule.TypeSystem.Int32 }
        'System.Boolean' { return $target.MainModule.TypeSystem.Boolean }
        'System.Void' { return $target.MainModule.TypeSystem.Void }
        'System.Object' { return $target.MainModule.TypeSystem.Object }
        default { throw "Unexpected external type: $Type" }
    }
}
foreach ($method in $originalMethods) {
    $copy = [Mono.Cecil.MethodDefinition]::new($method.Name, $method.Attributes, (Convert-Type $method.ReturnType))
    foreach ($param in $method.Parameters) { $copy.Parameters.Add([Mono.Cecil.ParameterDefinition]::new($param.Name, $param.Attributes, (Convert-Type $param.ParameterType))) }
    $types[$method.DeclaringType.FullName].Methods.Add($copy); $methods[$method.FullName] = $copy
}
$referencedFields = @($originalMethods | ForEach-Object { $_.Body.Instructions } | Where-Object { $_.Operand -is [Mono.Cecil.FieldReference] } | ForEach-Object { $_.Operand.Resolve() })
foreach ($field in $referencedFields) {
    if ($fields.ContainsKey($field.FullName)) { continue }
    $copy = [Mono.Cecil.FieldDefinition]::new($field.Name, $field.Attributes, (Convert-Type $field.FieldType))
    if ($field.HasConstant) { $copy.Constant = $field.Constant }
    $types[$field.DeclaringType.FullName].Fields.Add($copy); $fields[$field.FullName] = $copy
}
# Explicit data-provider shims, not copied gameplay: abstract count methods
# return harness fields. They do not resolve real cards or invoke an event bus.
foreach ($shimName in @('GetNumValidTargets','GetNumSelectedTargets')) {
    $owner = $types['GwentGameplay.ARequestTargetsAction']
    $field = [Mono.Cecil.FieldDefinition]::new('_Oracle' + $shimName, [Mono.Cecil.FieldAttributes]::Public, $target.MainModule.TypeSystem.Int32)
    $owner.Fields.Add($field)
    $shim = [Mono.Cecil.MethodDefinition]::new($shimName, [Mono.Cecil.MethodAttributes]([int][Mono.Cecil.MethodAttributes]::Public -bor [int][Mono.Cecil.MethodAttributes]::Virtual -bor [int][Mono.Cecil.MethodAttributes]::NewSlot), $target.MainModule.TypeSystem.Int32)
    $owner.Methods.Add($shim)
    $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_0))
    $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldfld, $field))
    $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ret))
    $methods[$shim.FullName] = $shim
}

foreach ($method in $originalMethods) {
    $copy = $methods[$method.FullName]
    $copy.Body.InitLocals = $method.Body.InitLocals; $copy.Body.MaxStackSize = $method.Body.MaxStackSize
    if ($method.Body.HasExceptionHandlers) { throw 'Unexpected exception handler' }
    foreach ($local in $method.Body.Variables) { $copy.Body.Variables.Add([Mono.Cecil.Cil.VariableDefinition]::new((Convert-Type $local.VariableType))) }
    $instructionMap = @{}
    foreach ($instruction in $method.Body.Instructions) {
        $cloned = [Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Nop)
        $cloned.OpCode = $instruction.OpCode
        $copy.Body.Instructions.Add($cloned); $instructionMap[$instruction.Offset] = $cloned
    }
    foreach ($instruction in $method.Body.Instructions) {
        $operand = $instruction.Operand
        if ($null -eq $operand) { continue }
        if ($operand -is [Mono.Cecil.Cil.Instruction]) { $operand = $instructionMap[$operand.Offset] }
        elseif ($operand -is [Mono.Cecil.Cil.Instruction[]]) { $operand = [Mono.Cecil.Cil.Instruction[]]@($operand | ForEach-Object { $instructionMap[$_.Offset] }) }
        elseif ($operand -is [Mono.Cecil.Cil.VariableDefinition]) { $operand = $copy.Body.Variables[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.ParameterDefinition]) { $operand = $copy.Parameters[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.FieldReference]) { $operand = $fields[$operand.FullName] }
        elseif ($operand -is [Mono.Cecil.MethodReference]) {
            if ($methods.ContainsKey($operand.FullName)) { $operand = $methods[$operand.FullName] }
            elseif ($operand.FullName -eq 'System.Int32 System.Math::Min(System.Int32,System.Int32)') { $operand = $target.MainModule.ImportReference([math].GetMethod('Min', [type[]]@([int],[int]))) }
            elseif ($operand.FullName -eq 'System.Int32 System.Collections.Generic.List`1<System.UInt16>::get_Count()') { $operand = $target.MainModule.ImportReference([System.Collections.Generic.List[uint16]].GetProperty('Count').GetMethod) }
            elseif ($operand.FullName -eq 'System.Void System.Object::.ctor()') { $operand = $target.MainModule.ImportReference([object].GetConstructor([type[]]@())) }
            else { throw "Unexpected external method: $operand" }
        }
        elseif ($operand -is [Mono.Cecil.TypeReference]) { $operand = Convert-Type $operand }
        $instructionMap[$instruction.Offset].Operand = $operand
    }
}
$outDir = Join-Path $Workspace 'tools\oracle\beta-request-ref\reference'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir 'BetaRequestExtract.dll'
$target.Write($outPath)
$verified = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($outPath)
$checks = @(foreach ($method in $originalMethods) {
    $readBack = $verified.MainModule.Types | ForEach-Object Methods | Where-Object { $_.FullName -eq $method.FullName }
    $before = ($method.Body.Instructions | ForEach-Object ToString) -join "`n"
    $after = ($readBack.Body.Instructions | ForEach-Object ToString) -join "`n"
    if ($before -cne $after) { throw "Instruction mismatch: $($method.FullName)" }
    [ordered]@{signature=$method.FullName; instructions=$method.Body.Instructions.Count; exactInstructionMatch=$true}
})
[ordered]@{
    source=$sourcePath; sourceSha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
    extract=$outPath; extractSha256=(Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash
    methods=$checks
    scope='Exact copied request limit/finish IL. Abstract valid/selected counts supplied by two harness field shims; choices List<ushort> supplied by harness. No Init, actual cards, Unity, event bus, manager, continuation, timeout RNG or network. Not a full client oracle.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-request-extraction.json') -Encoding utf8
$verified.Dispose(); $target.Dispose(); $source.Dispose()
Write-Output "Extracted and verified $($checks.Count) methods: $outPath"
