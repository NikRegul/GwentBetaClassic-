# Explicitly re-import the edited researched Markdown, then regenerate game data.
param()
$ErrorActionPreference='Stop'
$OutputEncoding=[System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING='utf-8'
$TaskRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskRoot
try {
    foreach ($script in @('tools/import_researched_ai115.py','tools/build_ai_rules.py',
        'tools/build_research_strategy115.py','tools/build_duel_catalog.py','tools/ai/gen_clone.py',
        'tools/export_researched_ai115.py')) {
        & python -X utf8 $script
        if ($LASTEXITCODE -ne 0) { throw "AI import failed: $script" }
    }
    Write-Host 'Imported 46 decks. Build: powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage115.ps1 -CheckAI'
} finally { Pop-Location }
