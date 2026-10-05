param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$sourcePath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$source = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($sourcePath)
$target = [Mono.Cecil.AssemblyDefinition]::CreateAssembly([Mono.Cecil.AssemblyNameDefinition]::new('BetaFlowExtract', [version]'1.0.0.0'), 'BetaFlowExtract.dll', [Mono.Cecil.ModuleKind]::Dll)
$selection = @{
    RoundInfo = @('.ctor','get_Id','set_Id','get_PlayerScores','set_PlayerScores','get_StartingPlayerId','set_StartingPlayerId','get_WinnerId','set_WinnerId','SetResult')
    RoundManager = @('GetWinner','HasWinner')
    Player = @('get_Id','set_Id','get_Crowns','set_Crowns','get_HasPassed','set_HasPassed','OnPass','OnRoundStart','OnTurnEnd')
    PlayerManager = @('AllPlayersPassed')
    GameController = @('get_PlayerManager')
    AGameManager = @('get_GameController')
    EPlayerId = @()
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
$types['GwentGameplay.RoundManager'].BaseType = $types['GwentGameplay.AGameManager']
function Convert-Type([Mono.Cecil.TypeReference]$Type) {
    if ($Type -is [Mono.Cecil.ArrayType]) { return [Mono.Cecil.ArrayType]::new((Convert-Type $Type.ElementType), $Type.Rank) }
    if ($types.ContainsKey($Type.FullName)) { return $types[$Type.FullName] }
    switch ($Type.FullName) {
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
$referencedFields += @($source.MainModule.Types | Where-Object { $_.FullName -eq 'GwentGameplay.EPlayerId' } | ForEach-Object Fields)
foreach ($field in $referencedFields) {
    if ($fields.ContainsKey($field.FullName)) { continue }
    $copy = [Mono.Cecil.FieldDefinition]::new($field.Name, $field.Attributes, (Convert-Type $field.FieldType))
    if ($field.HasConstant) { $copy.Constant = $field.Constant }
    $types[$field.DeclaringType.FullName].Fields.Add($copy); $fields[$field.FullName] = $copy
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
            elseif ($operand.FullName -eq 'System.Void System.Object::.ctor()') { $operand = $target.MainModule.ImportReference([object].GetConstructor([type[]]@())) }
            else { throw "Unexpected external method: $operand" }
        }
        elseif ($operand -is [Mono.Cecil.TypeReference]) { $operand = Convert-Type $operand }
        $instructionMap[$instruction.Offset].Operand = $operand
    }
}
$outDir = Join-Path $Workspace 'tools\oracle\beta-flow-ref\reference'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir 'BetaFlowExtract.dll'
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
    scope='Unmodified instruction bodies of selected pure methods, with minimal data-holder types. No original module initializer, Unity runtime, event bus, requests, scheduler or network. This is not a full client oracle.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-flow-extraction.json') -Encoding utf8
$verified.Dispose(); $target.Dispose(); $source.Dispose()
Write-Output "Extracted and verified $($checks.Count) methods: $outPath"
