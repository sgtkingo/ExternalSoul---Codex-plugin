param([switch]$Login)
$ErrorActionPreference = 'Stop'
$pluginRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
& codex plugin marketplace add $pluginRoot
if ($LASTEXITCODE -ne 0) { throw 'Could not register the local marketplace.' }
& codex plugin add 'esoul@externalsoul-local'
if ($LASTEXITCODE -ne 0) { throw 'Could not install ExternalSoul.' }
& codex mcp get esoul
if ($LASTEXITCODE -ne 0) { throw 'The bundled esoul MCP server is not available.' }
if ($Login) {
    & codex mcp login esoul
    if ($LASTEXITCODE -ne 0) { throw 'ExternalSoul sign-in did not complete.' }
}
