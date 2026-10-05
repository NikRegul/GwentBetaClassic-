param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$sourcePath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if ((Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Original baseline changed' }
$resolver = [Mono.Cecil.DefaultAssemblyResolver]::new()
$resolver.AddSearchDirectory((Split-Path -Parent $sourcePath))
$reader = [Mono.Cecil.ReaderParameters]::new(); $reader.AssemblyResolver = $resolver
$source = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($sourcePath, $reader)
$target = [Mono.Cecil.AssemblyDefinition]::CreateAssembly([Mono.Cecil.AssemblyNameDefinition]::new('BetaManagerApplyExtract', [version]'1.0.0.0'), 'BetaManagerApplyExtract.dll', [Mono.Cecil.ModuleKind]::Dll)
$selection = @{
    'GwentGameplay.ActionManager' = @('ApplyAction','get_LastKnownNetworkID','set_LastKnownNetworkID')
    'GwentGameplay.AGameManager' = @('get_GameController')
    'GwentGameplay.AAction' = @()
    'GwentGameplay.ARequestAction' = @()
    'GwentGameplay.GameController' = @()
    'GwentGameplay.RequestManager' = @()
    'GwentGameplay.PlayerManager' = @()
    'GwentGameplay.Player' = @()
    'GwentGameplay.TimeManager' = @()
    'GwentGameplay.TimePause' = @()
    'GwentGameplay.EPlayerId' = @()
    'GwentGameplay.IPriorityAction' = @()
    'GwentGameplay.IStateChangingAction' = @()
    'GwentGameplay.ExceptionHelper' = @()
    'RedLogger.IRedLogger' = @()
    'RedLogger.LC' = @()
}
$types = @{}; $methods = @{}; $fields = @{}; $originalMethods = @()
$selectedTypes = @($source.MainModule.Types | Where-Object { $selection.ContainsKey($_.FullName) })
foreach ($name in $selection.Keys | Where-Object { $_ -notin $selectedTypes.FullName }) {
    $reference = $source.MainModule.GetTypeReferences() | Where-Object FullName -eq $name | Select-Object -First 1
    if (!$reference) { throw "Missing type reference: $name" }
    $selectedTypes += $reference.Resolve()
}
foreach ($type in $selectedTypes) {
    $attrs = [Mono.Cecil.TypeAttributes]::Public; $base = $target.MainModule.TypeSystem.Object
    if ($type.IsEnum) { $attrs = $type.Attributes; $base = $target.MainModule.ImportReference([System.Enum]) }
    # Marker interfaces preserve original isinst behavior. Logger is a concrete
    # delegate boundary: none of the copied code tests its interface identity.
    if ($type.Name -in @('IPriorityAction','IStateChangingAction')) {
        $attrs = [Mono.Cecil.TypeAttributes]([int][Mono.Cecil.TypeAttributes]::Public -bor [int][Mono.Cecil.TypeAttributes]::Interface -bor [int][Mono.Cecil.TypeAttributes]::Abstract); $base = $null
    }
    $copy = [Mono.Cecil.TypeDefinition]::new($type.Namespace, $type.Name, $attrs, $base)
    $target.MainModule.Types.Add($copy); $types[$type.FullName] = $copy
    $originalMethods += @($type.Methods | Where-Object { $_.Name -in $selection[$type.FullName] })
}
if ($types.Count -ne $selection.Count) { throw 'Missing selected types' }
$types['GwentGameplay.ActionManager'].BaseType = $types['GwentGameplay.AGameManager']
$types['GwentGameplay.ARequestAction'].BaseType = $types['GwentGameplay.AAction']
function Convert-Type([Mono.Cecil.TypeReference]$Type) {
    if ($types.ContainsKey($Type.FullName)) { return $types[$Type.FullName] }
    if ($Type -is [Mono.Cecil.ArrayType]) { return [Mono.Cecil.ArrayType]::new((Convert-Type $Type.ElementType)) }
    if ($Type -is [Mono.Cecil.GenericParameter]) { return $Type }
    if ($Type.FullName.StartsWith('System.')) { return $target.MainModule.ImportReference($Type) }
    throw "Unexpected type: $Type"
}
foreach ($method in $originalMethods) {
    $copy = [Mono.Cecil.MethodDefinition]::new($method.Name, $method.Attributes, (Convert-Type $method.ReturnType))
    foreach ($param in $method.Parameters) { $copy.Parameters.Add([Mono.Cecil.ParameterDefinition]::new($param.Name, $param.Attributes, (Convert-Type $param.ParameterType))) }
    $types[$method.DeclaringType.FullName].Methods.Add($copy); $methods[$method.FullName] = $copy
}
$referencedFields = @($originalMethods | ForEach-Object { $_.Body.Instructions } | Where-Object { $_.Operand -is [Mono.Cecil.FieldReference] } | ForEach-Object { $_.Operand.Resolve() })
$referencedFields += @($selectedTypes | Where-Object IsEnum | ForEach-Object Fields)
foreach ($field in $referencedFields) {
    if ($fields.ContainsKey($field.FullName)) { continue }
    $copy = [Mono.Cecil.FieldDefinition]::new($field.Name, $field.Attributes, (Convert-Type $field.FieldType))
    if ($field.HasConstant) { $copy.Constant = $field.Constant }
    $types[$field.DeclaringType.FullName].Fields.Add($copy); $fields[$field.FullName] = $copy
}
$shims = [System.Collections.Generic.List[object]]::new()
$callbackRuntime = [System.Func[object,object]].GetGenericTypeDefinition().MakeGenericType([type[]]@([object[]],[object]))
$callbackType = $target.MainModule.ImportReference($callbackRuntime)
$callbackInvoke = $target.MainModule.ImportReference($callbackRuntime.GetMethod('Invoke'))
$references = @($originalMethods | ForEach-Object { $_.Body.Instructions } | Where-Object { $_.Operand -is [Mono.Cecil.MethodReference] } | ForEach-Object Operand)
foreach ($reference in $references) {
    if ($methods.ContainsKey($reference.FullName) -or $reference.DeclaringType.FullName.StartsWith('System.')) { continue }
    $element = $reference
    if ($reference -is [Mono.Cecil.GenericInstanceMethod]) { $element = $reference.ElementMethod }
    $owner = $types[$element.DeclaringType.FullName]
    if (!$owner) { throw "Unexpected shim owner: $element" }
    $isStatic = !$element.HasThis
    $attrs = [int][Mono.Cecil.MethodAttributes]::Public
    if ($isStatic) { $attrs = $attrs -bor [int][Mono.Cecil.MethodAttributes]::Static }
    else { $attrs = $attrs -bor [int][Mono.Cecil.MethodAttributes]::Virtual -bor [int][Mono.Cecil.MethodAttributes]::NewSlot }
    $shim = [Mono.Cecil.MethodDefinition]::new($element.Name, [Mono.Cecil.MethodAttributes]$attrs, (Convert-Type $element.ReturnType))
    foreach ($generic in $element.GenericParameters) { $shim.GenericParameters.Add([Mono.Cecil.GenericParameter]::new($generic.Name, $shim)) }
    foreach ($param in $element.Parameters) { $shim.Parameters.Add([Mono.Cecil.ParameterDefinition]::new($param.Name, $param.Attributes, (Convert-Type $param.ParameterType))) }
    $owner.Methods.Add($shim)
    $fieldAttrs = [int][Mono.Cecil.FieldAttributes]::Public
    if ($isStatic) { $fieldAttrs = $fieldAttrs -bor [int][Mono.Cecil.FieldAttributes]::Static }
    $field = [Mono.Cecil.FieldDefinition]::new('_Oracle' + $shims.Count, [Mono.Cecil.FieldAttributes]$fieldAttrs, $callbackType)
    $owner.Fields.Add($field)
    $il = $shim.Body.GetILProcessor()
    if ($isStatic) { $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldsfld, $field) }
    else { $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldarg_0); $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldfld, $field) }
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldc_I4, $shim.Parameters.Count)
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Newarr, $target.MainModule.TypeSystem.Object)
    for ($i = 0; $i -lt $shim.Parameters.Count; $i += 1) {
        $param = $shim.Parameters[$i]
        $il.Emit([Mono.Cecil.Cil.OpCodes]::Dup); $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldc_I4, $i)
        $il.Emit([Mono.Cecil.Cil.OpCodes]::Ldarg, $param)
        if ($param.ParameterType.IsValueType) { $il.Emit([Mono.Cecil.Cil.OpCodes]::Box, $param.ParameterType) }
        $il.Emit([Mono.Cecil.Cil.OpCodes]::Stelem_Ref)
    }
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Callvirt, $callbackInvoke)
    if ($shim.ReturnType.FullName -eq 'System.Void') { $il.Emit([Mono.Cecil.Cil.OpCodes]::Pop) }
    elseif ($shim.ReturnType.IsValueType) { $il.Emit([Mono.Cecil.Cil.OpCodes]::Unbox_Any, $shim.ReturnType) }
    else { $il.Emit([Mono.Cecil.Cil.OpCodes]::Castclass, $shim.ReturnType) }
    $il.Emit([Mono.Cecil.Cil.OpCodes]::Ret)
    $mapped = $shim
    if ($reference -is [Mono.Cecil.GenericInstanceMethod]) {
        $mapped = [Mono.Cecil.GenericInstanceMethod]::new($shim)
        foreach ($argument in $reference.GenericArguments) { $mapped.GenericArguments.Add((Convert-Type $argument)) }
    }
    $methods[$reference.FullName] = $mapped
    $shims.Add([ordered]@{signature=$reference.FullName; owner=$owner.FullName; name=$element.Name; field=$field.Name; static=$isStatic; boundary='Harness callback, not original implementation'})
}
foreach ($variant in @(
    @{name='OraclePriorityAction'; base='AAction'; markers=@('IPriorityAction')},
    @{name='OracleChangingAction'; base='AAction'; markers=@('IStateChangingAction')},
    @{name='OracleChangingRequest'; base='ARequestAction'; markers=@('IStateChangingAction')})) {
    $type = [Mono.Cecil.TypeDefinition]::new('GwentGameplay',$variant.name,[Mono.Cecil.TypeAttributes]::Public,$types['GwentGameplay.' + $variant.base])
    foreach ($marker in $variant.markers) { $type.Interfaces.Add([Mono.Cecil.InterfaceImplementation]::new($types['GwentGameplay.' + $marker])) }
    $target.MainModule.Types.Add($type)
}
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
$outDir = Join-Path $Workspace 'tools\oracle\beta-manager-apply-ref\reference'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir 'BetaManagerApplyExtract.dll'; $target.Write($outPath)
$verified = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($outPath)
if (@($verified.MainModule.AssemblyReferences | Where-Object { $_.Name -eq 'Assembly-CSharp' -or $_.Name -like 'Unity*' }).Count) { throw 'Original runtime dependency' }
$checks = @(foreach ($method in $originalMethods) {
    $readBack = $verified.MainModule.Types | ForEach-Object Methods | Where-Object FullName -eq $method.FullName
    $before = ($method.Body.Instructions | ForEach-Object ToString) -join "`n"; $after = ($readBack.Body.Instructions | ForEach-Object ToString) -join "`n"
    if ($before -cne $after) { throw "Instruction mismatch: $($method.FullName)" }
    [ordered]@{signature=$method.FullName; instructions=$method.Body.Instructions.Count; exactInstructionMatch=$true}
})
$dependencies = @(foreach ($path in @($selectedTypes | ForEach-Object { $_.Module.FileName } | Sort-Object -Unique)) {
    [ordered]@{path=$path; sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash; use='Read-only type/enum metadata; never loaded as executable runtime'}
})
[ordered]@{source=$sourcePath; sourceSha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash;
    extract=$outPath; extractSha256=(Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash; methods=$checks; shims=@($shims);
    metadataDependencies=$dependencies;
    typeBoundaryNotes='ActionManager inherits AGameManager; ARequestAction inherits AAction; priority/state marker interfaces preserved. Other types flattened; logger interface becomes a delegate-backed class. Enums copied with constants. Constructors/Init never run.';
    extractedAssemblyReferences=@($verified.MainModule.AssemblyReferences | ForEach-Object FullName);
    originalRuntimeReferencesAbsent=$true;
    scope='Exact ActionManager.ApplyAction, networkID accessors, base controller getter. Delegate seams for all external operations including validity/Apply/request/logger/send/pause/destroy. No effects, serialization, actual network, pool or full scheduler.'} |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-manager-apply-extraction.json') -Encoding utf8
$verified.Dispose(); $target.Dispose(); $source.Dispose()
Write-Output "Extracted and verified $($checks.Count) manager Apply methods, explicit seams $($shims.Count)."
