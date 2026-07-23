# restore_env_sandbox.ps1
# Restaura las credenciales de Flow en backend/.env a SANDBOX, para que cualquier
# prueba LOCAL no cobre de verdad. Toca SOLO 3 variables (FLOW_API_KEY, FLOW_API_SECRET,
# FLOW_API_BASE); el resto del .env queda intacto. Las de producción viven en Railway.
#
# Pide la key/secret de sandbox por teclado (no quedan en el historial) -> por eso
# corre este script en TU terminal, no con el prefijo "!" de Claude.
#
# Uso (PowerShell, en la carpeta backend):
#     .\restore_env_sandbox.ps1
#
# Las credenciales de sandbox se obtienen en el panel de Flow sandbox:
#     https://sandbox.flow.cl  ->  tu cuenta  ->  API Keys.

$ErrorActionPreference = 'Stop'
$envPath = Join-Path $PSScriptRoot '.env'
if (-not (Test-Path $envPath)) { Write-Error "No existe $envPath"; exit 1 }

# 1. Respaldo del .env actual (que hoy tiene credenciales de PRODUCCION).
#    El patron .env.* esta gitignored -> el respaldo NO se commitea.
$stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = Join-Path $PSScriptRoot ".env.prod.bak.$stamp"
Copy-Item $envPath $backup
Write-Host "Respaldo del .env actual (prod) -> $backup"

# 2. Pedir credenciales de sandbox.
$key    = Read-Host 'FLOW_API_KEY de SANDBOX'
$secret = Read-Host 'FLOW_API_SECRET de SANDBOX'
if ([string]::IsNullOrWhiteSpace($key) -or [string]::IsNullOrWhiteSpace($secret)) {
    Write-Error 'Key/Secret vacios. Aborto (el .env NO se modifico).'; exit 1
}

# 3. Reescribir solo las 3 variables de Flow.
$sandboxBase = 'https://sandbox.flow.cl/api'
$set  = [ordered]@{ FLOW_API_KEY = $key; FLOW_API_SECRET = $secret; FLOW_API_BASE = $sandboxBase }
$seen = @{}
$lines = Get-Content -Path $envPath
$out = foreach ($line in $lines) {
    $m = [regex]::Match($line, '^\s*([A-Za-z0-9_]+)\s*=')
    if ($m.Success -and $set.Contains($m.Groups[1].Value)) {
        $name = $m.Groups[1].Value
        $seen[$name] = $true
        "$name=$($set[$name])"
    } else {
        $line
    }
}
# Si alguna variable no existia en el archivo, agregarla al final.
foreach ($name in $set.Keys) {
    if (-not $seen.ContainsKey($name)) { $out += "$name=$($set[$name])" }
}

# 4. Escribir UTF-8 SIN BOM (evita que python-dotenv mal-parsee la primera linea en Win PowerShell 5.1).
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($envPath, $out, $utf8NoBom)

# 5. Guardar tambien una copia .env.sandbox para futuros toggles (gitignored).
Copy-Item $envPath (Join-Path $PSScriptRoot '.env.sandbox') -Force

Write-Host ''
Write-Host "OK: FLOW_API_KEY / FLOW_API_SECRET -> SANDBOX; FLOW_API_BASE=$sandboxBase."
Write-Host "El resto del .env quedo intacto. Prod respaldado en: $backup"
Write-Host ''
Write-Host 'Verificacion rapida (no imprime secretos):'
Write-Host '  ./.venv/Scripts/python.exe scripts/flow_update_plan_callback.py --verify'
Write-Host '  -> el "Flow base URL" debe decir https://sandbox.flow.cl/api'
