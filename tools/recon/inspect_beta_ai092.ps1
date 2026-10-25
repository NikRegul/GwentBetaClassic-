param([string]$Workspace='D:\w3mod',[string]$Output='BetaGwent\drafts\day-iteration-20261023\original-beta-ai')
$ErrorActionPreference='Stop'
$target=Join-Path $Workspace $Output
New-Item -ItemType Directory -Path $target -Force | Out-Null
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$source=Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$assembly=[Mono.Cecil.AssemblyDefinition]::ReadAssembly($source)
function All-Types($items){foreach($item in $items){$item;All-Types $item.NestedTypes}}
$types=@(All-Types $assembly.MainModule.Types | Where-Object {$_.FullName.StartsWith('GwentGameplay.AI.')})
$index=foreach($type in $types){
    $lines=[System.Collections.Generic.List[string]]::new()
    $lines.Add('TYPE '+$type.FullName)
    foreach($field in $type.Fields){$lines.Add('FIELD '+$field.FullName)}
    foreach($method in $type.Methods){
        $lines.Add('METHOD '+$method.FullName)
        if($method.HasBody){foreach($instruction in $method.Body.Instructions){$lines.Add([string]$instruction)}}
    }
    $name=($type.FullName -replace '[^A-Za-z0-9_.-]','_')+'.il.txt'
    $lines | Set-Content -LiteralPath (Join-Path $target $name) -Encoding utf8
    [ordered]@{type=$type.FullName;file=$name;methods=$type.Methods.Count;fields=$type.Fields.Count;lines=$lines.Count}
}
$index | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $target 'il-index.json') -Encoding utf8
$totalLines=0;foreach($entry in $index){$totalLines+=$entry['lines']}
[ordered]@{source=$source;sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash;types=$types.Count;ilLines=$totalLines;scope='Static original IL, including nested search iterators. No client or game code executed.'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $target 'provenance.json') -Encoding utf8
$assembly.Dispose()
Get-Content -LiteralPath (Join-Path $target 'provenance.json')
