# Sincronizacion manual, incremental y no destructiva hacia Google Drive.
# Guardar este archivo en la raiz de Colossal-Adventure-Reimagination-public.
# Uso: .\sync_to_drive.ps1 [-DryRun]
param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Source = $PSScriptRoot
$Destination = 'G:\Mi unidad\RPG_Archaeology_IF'

if (-not (Test-Path -LiteralPath (Split-Path -Path $Destination -Qualifier))) {
    throw 'La unidad G: no esta disponible. Comprueba que Google Drive esta montado.'
}
if (-not (Test-Path -LiteralPath (Join-Path $Source 'AGENTS.md'))) {
    throw "No se encontro AGENTS.md en el origen: $Source. Ejecuta el script desde la raiz correcta del repositorio."
}

if (-not (Test-Path -LiteralPath $Destination)) {
    if ($DryRun) {
        Write-Host "[SIMULACION] Se crearia la carpeta destino: $Destination"
    } else {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }
}

$RoboArgs = @(
    $Source,
    $Destination,
    '/E',            # Incluir subcarpetas, incluso vacias.
    '/XJ',           # No seguir junctions.
    '/R:2',          # Reintentar dos veces ante errores.
    '/W:2',          # Esperar dos segundos entre intentos.
    '/COPY:DAT',     # Datos, atributos y fechas; no ACL ni propietarios.
    '/DCOPY:DAT',    # Conservar fechas de directorios.
    '/XD', '.git', '.godot',
    '/NP'            # Sin porcentajes de progreso por archivo.
)
if ($DryRun) {
    $RoboArgs += '/L'
}

Write-Host "Origen : $Source"
Write-Host "Destino: $Destination"
Write-Host "Modo   : $(if ($DryRun) { 'SIMULACION' } else { 'COPIA INCREMENTAL' })"
Write-Host 'Sin borrados en destino. Se sobrescriben archivos existentes cuando difieren.'
Write-Host ''

& robocopy @RoboArgs
$Code = $LASTEXITCODE

# Robocopy: 0-7 son resultados correctos o advertencias; 8+ indican fallo.
if ($Code -ge 8) {
    throw "Robocopy termino con error (codigo $Code). Revisa el resumen anterior."
}
Write-Host "Sincronizacion finalizada (codigo Robocopy $Code)."