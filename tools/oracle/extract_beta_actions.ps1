param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$sourcePath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$source = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($sourcePath)
if ((Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Original Beta baseline changed' }
$target = [Mono.Cecil.AssemblyDefinition]::CreateAssembly([Mono.Cecil.AssemblyNameDefinition]::new('BetaActionExtract', [version]'1.0.0.0'), 'BetaActionExtract.dll', [Mono.Cecil.ModuleKind]::Dll)
$selection = @{
    AAction = @('get_FireTriggers','set_FireTriggers','get_HasFiredBeforeApplyTrigger','set_HasFiredBeforeApplyTrigger','BeforeApplyTrigger')
    AGameManager = @('get_GameController')
    ActionManager = @('get_Actions','set_Actions','get_HasActions','get_BreakOnChange','set_BreakOnChange','Step','PushActionImpl')
    AbilityInstance = @('get_GameController','get_Actions','set_Actions','ExecuteNextAction')
    GameController = @('get_ActionManager','set_ActionManager','get_InDebugMode','set_InDebugMode')
    IPriorityAction = @()
    ExceptionHelper = @()
}
$types = @{}; $methods = @{}; $fields = @{}; $originalMethods = @()
foreach ($type in $source.MainModule.Types | Where-Object { $_.Namespace -eq 'GwentGameplay' -and $selection.ContainsKey($_.Name) }) {
    $attrs = [Mono.Cecil.TypeAttributes]::Public
    $base = $target.MainModule.TypeSystem.Object
    if ($type.IsInterface) {
        $attrs = [Mono.Cecil.TypeAttributes]([int][Mono.Cecil.TypeAttributes]::Public -bor [int][Mono.Cecil.TypeAttributes]::Interface -bor [int][Mono.Cecil.TypeAttributes]::Abstract)
        $base = $null
    }
    $copy = [Mono.Cecil.TypeDefinition]::new($type.Namespace, $type.Name, $attrs, $base)
    $target.MainModule.Types.Add($copy); $types[$type.FullName] = $copy
    $originalMethods += @($type.Methods | Where-Object { $_.Name -in $selection[$type.Name] })
}
$types['GwentGameplay.ActionManager'].BaseType = $types['GwentGameplay.AGameManager']

function Convert-Type([Mono.Cecil.TypeReference]$Type) {
    if ($types.ContainsKey($Type.FullName)) { return $types[$Type.FullName] }
    if ($Type -is [Mono.Cecil.GenericParameter]) { return $Type }
    if ($Type -is [Mono.Cecil.GenericInstanceType]) {
        $converted = [Mono.Cecil.GenericInstanceType]::new($target.MainModule.ImportReference($Type.ElementType))
        foreach ($argument in $Type.GenericArguments) { $converted.GenericArguments.Add((Convert-Type $argument)) }
        return $converted
    }
    if ($Type.FullName.StartsWith('System.')) { return $target.MainModule.ImportReference($Type) }
    throw "Unexpected external type: $Type"
}
foreach ($method in $originalMethods) {
    $copy = [Mono.Cecil.MethodDefinition]::new($method.Name, $method.Attributes, (Convert-Type $method.ReturnType))
    foreach ($param in $method.Parameters) { $copy.Parameters.Add([Mono.Cecil.ParameterDefinition]::new($param.Name, $param.Attributes, (Convert-Type $param.ParameterType))) }
    $types[$method.DeclaringType.FullName].Methods.Add($copy); $methods[$method.FullName] = $copy
}
foreach ($field in @($originalMethods | ForEach-Object { $_.Body.Instructions } | Where-Object { $_.Operand -is [Mono.Cecil.FieldReference] } | ForEach-Object { $_.Operand.Resolve() })) {
    if ($fields.ContainsKey($field.FullName)) { continue }
    $copy = [Mono.Cecil.FieldDefinition]::new($field.Name, $field.Attributes, (Convert-Type $field.FieldType))
    $types[$field.DeclaringType.FullName].Fields.Add($copy); $fields[$field.FullName] = $copy
}

# Explicit external-boundary shims. Step, Before guard and queue instructions
# are copied; validation, callback effects, ApplyAction and network authority
# are supplied by the harness and are NOT an original gameplay oracle.
$shimDescriptions = [System.Collections.Generic.List[string]]::new()
function Add-FieldShim([string]$Owner, [string]$Name, [type]$FieldType, [string]$ReturnName, [type[]]$Parameters) {
    $ownerType = $types['GwentGameplay.' + $Owner]
    $field = [Mono.Cecil.FieldDefinition]::new('_Oracle' + $Name, [Mono.Cecil.FieldAttributes]::Public, $target.MainModule.ImportReference($FieldType))
    $ownerType.Fields.Add($field)
    $returnType = $target.MainModule.TypeSystem.Void
    if ($ReturnName -eq 'Boolean') { $returnType = $target.MainModule.TypeSystem.Boolean }
    $attributes = [Mono.Cecil.MethodAttributes]([int][Mono.Cecil.MethodAttributes]::Public -bor [int][Mono.Cecil.MethodAttributes]::Virtual -bor [int][Mono.Cecil.MethodAttributes]::NewSlot)
    $shim = [Mono.Cecil.MethodDefinition]::new($Name, $attributes, $returnType)
    if ($Name -eq 'ApplyAction') { $shim.Parameters.Add([Mono.Cecil.ParameterDefinition]::new('action', [Mono.Cecil.ParameterAttributes]::None, $types['GwentGameplay.AAction'])) }
    $ownerType.Methods.Add($shim)
    $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_0))
    $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldfld, $field))
    if ($FieldType -ne [bool]) {
        if ($Name -eq 'ApplyAction') { $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldarg_1)) }
        $invoke = $target.MainModule.ImportReference($FieldType.GetMethod('Invoke'))
        $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Callvirt, $invoke))
    }
    $shim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ret))
    $methods[$shim.FullName] = $shim
    $shimDescriptions.Add($shim.FullName + ' -> harness field/delegate')
}
Add-FieldShim 'GameController' 'get_HasAuthority' ([bool]) 'Boolean' @()
Add-FieldShim 'AAction' 'IsValid' ([System.Func[bool]]) 'Boolean' @()
Add-FieldShim 'AAction' 'BeforeApplyTriggerImpl' ([System.Action]) 'Void' @()
Add-FieldShim 'ActionManager' 'ApplyAction' ([System.Action[object]]) 'Void' @([object])

# Only the exception object/message seam is shimmed for the front-authority
# rejection. Original PushActionImpl still executes the guard and throw.
$exceptionRef = @($originalMethods | ForEach-Object { $_.Body.Instructions } | Where-Object { $_.Operand -is [Mono.Cecil.GenericInstanceMethod] -and $_.Operand.DeclaringType.Name -eq 'ExceptionHelper' } | ForEach-Object { $_.Operand })[0]
$element = $exceptionRef.ElementMethod
$exceptionShim = [Mono.Cecil.MethodDefinition]::new($element.Name, [Mono.Cecil.MethodAttributes]([int][Mono.Cecil.MethodAttributes]::Public -bor [int][Mono.Cecil.MethodAttributes]::Static), $target.MainModule.TypeSystem.Void)
$generic = [Mono.Cecil.GenericParameter]::new($element.GenericParameters[0].Name, $exceptionShim)
$exceptionShim.GenericParameters.Add($generic); $exceptionShim.ReturnType = $target.MainModule.ImportReference([System.Exception])
foreach ($param in $element.Parameters) { $exceptionShim.Parameters.Add([Mono.Cecil.ParameterDefinition]::new($param.Name, $param.Attributes, (Convert-Type $param.ParameterType))) }
$types['GwentGameplay.ExceptionHelper'].Methods.Add($exceptionShim)
$exceptionShim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ldstr, 'Oracle authority guard'))
$exceptionShim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Newobj, $target.MainModule.ImportReference([System.Exception].GetConstructor([type[]]@([string])))))
$exceptionShim.Body.Instructions.Add([Mono.Cecil.Cil.Instruction]::Create([Mono.Cecil.Cil.OpCodes]::Ret))
$exceptionInstance = [Mono.Cecil.GenericInstanceMethod]::new($exceptionShim)
foreach ($argument in $exceptionRef.GenericArguments) { $exceptionInstance.GenericArguments.Add((Convert-Type $argument)) }
$methods[$exceptionRef.FullName] = $exceptionInstance
$shimDescriptions.Add('ExceptionHelper.Create<Exception> -> exception message stub')
$priorityType = [Mono.Cecil.TypeDefinition]::new('GwentGameplay','OraclePriorityAction',[Mono.Cecil.TypeAttributes]::Public,$types['GwentGameplay.AAction'])
$priorityType.Interfaces.Add([Mono.Cecil.InterfaceImplementation]::new($types['GwentGameplay.IPriorityAction']))
$target.MainModule.Types.Add($priorityType)

foreach ($method in $originalMethods) {
    $copy = $methods[$method.FullName]
    $copy.Body.InitLocals = $method.Body.InitLocals; $copy.Body.MaxStackSize = $method.Body.MaxStackSize
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
        elseif ($operand -is [Mono.Cecil.Cil.Instruction[]]) { $operand = [Mono.Cecil.Cil.Instruction[]]@($operand | ForEach-Object { $instructionMap[$_.Offset] }) }
        elseif ($operand -is [Mono.Cecil.Cil.VariableDefinition]) { $operand = $copy.Body.Variables[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.ParameterDefinition]) { $operand = $copy.Parameters[$operand.Index] }
        elseif ($operand -is [Mono.Cecil.FieldReference]) { $operand = $fields[$operand.FullName] }
        elseif ($operand -is [Mono.Cecil.MethodReference]) {
            if ($methods.ContainsKey($operand.FullName)) { $operand = $methods[$operand.FullName] }
            elseif ($operand.DeclaringType.FullName.StartsWith('System.Collections.Generic.List`1<')) {
                $bound = [Mono.Cecil.MethodReference]::new($operand.Name, (Convert-Type $operand.ReturnType), (Convert-Type $operand.DeclaringType))
                $bound.HasThis = $operand.HasThis
                foreach ($param in $operand.Parameters) { $bound.Parameters.Add([Mono.Cecil.ParameterDefinition]::new((Convert-Type $param.ParameterType))) }
                $operand = $bound
            } else { throw "Unexpected external method: $operand" }
        } elseif ($operand -is [Mono.Cecil.TypeReference]) { $operand = Convert-Type $operand }
        $instructionMap[$instruction.Offset].Operand = $operand
    }
}
$outDir = Join-Path $Workspace 'tools\oracle\beta-action-ref\reference'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir 'BetaActionExtract.dll'; $target.Write($outPath)
$verified = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($outPath)
$checks = @(foreach ($method in $originalMethods) {
    $readBack = $verified.MainModule.Types | ForEach-Object Methods | Where-Object { $_.FullName -eq $method.FullName }
    $before = ($method.Body.Instructions | ForEach-Object ToString) -join "`n"
    $after = ($readBack.Body.Instructions | ForEach-Object ToString) -join "`n"
    if ($before -cne $after) { throw "Instruction mismatch: $($method.FullName)" }
    [ordered]@{signature=$method.FullName; instructions=$method.Body.Instructions.Count; exactInstructionMatch=$true}
})
[ordered]@{source=$sourcePath; sourceSha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash;
    extract=$outPath; extractSha256=(Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash;
    methods=$checks; shims=@($shimDescriptions);
    scope='Exact copied global/local queue Step, Before guard and front insertion IL. Five explicit boundary shims; no real ApplyAction, concrete effects, network authority, Update death drain, GameController.Step, active abilities or full scheduler oracle.'} |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-action-extraction.json') -Encoding utf8
$verified.Dispose(); $target.Dispose(); $source.Dispose()
Write-Output "Extracted and verified $($checks.Count) methods with $($shimDescriptions.Count) explicit shims: $outPath"
