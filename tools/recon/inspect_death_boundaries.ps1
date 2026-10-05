param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$path = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
if ($hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Original baseline changed' }
$assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($path)
$methods = @(foreach ($type in $assembly.MainModule.Types) {
    if ($type.FullName -eq 'GwentGameplay.CardManager') { $type.Methods | Where-Object HasBody }
    elseif ($type.FullName -eq 'GwentGameplay.CardPosition') { $type.Methods | Where-Object { $_.Name -eq 'get_IsActive' -and $_.HasBody } }
    elseif ($type.FullName -eq 'GwentGameplay.Card') { $type.Methods | Where-Object { $_.Name -in @('CanDie','Kill','get_IsWaitingToDie','set_IsWaitingToDie') -and $_.HasBody } }
    elseif ($type.FullName -eq 'GwentGameplay.EnumExtensions') { $type.Methods | Where-Object { $_.Name -eq 'Contains' -and $_.Parameters[0].ParameterType.FullName -eq 'GwentGameplay.ELocation' -and $_.HasBody } }
})
$records = @(foreach ($method in $methods) {
    [ordered]@{signature=$method.FullName; il=@($method.Body.Instructions | ForEach-Object ToString);
        calls=@($method.Body.Instructions | Where-Object { $_.Operand -is [Mono.Cecil.MethodReference] } | ForEach-Object { $_.Operand.FullName })}
})
$evidence = Join-Path $Workspace 'docs\evidence'
$ilPath = Join-Path $evidence 'beta-death-boundaries-il.txt'
@($records | ForEach-Object { 'METHOD ' + $_.signature; $_.il }) | Set-Content -LiteralPath $ilPath -Encoding utf8
[ordered]@{source=$path; sourceSha256=$hash; originalCodeExecuted=$false; methodCount=$records.Count;
    methods=$records; ilPath=$ilPath; ilSha256=(Get-FileHash -LiteralPath $ilPath -Algorithm SHA256).Hash;
    scope='Static CardManager and Card death/position predicates; no executed death drain or registry acceptance.'} |
    ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $evidence 'beta-death-boundaries.json') -Encoding utf8
$assembly.Dispose()
Write-Output "Static death/manager methods: $($records.Count)."
