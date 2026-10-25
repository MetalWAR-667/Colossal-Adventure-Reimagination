<#
.SYNOPSIS
    Verifies the Godot reconstruction of chapter 01.

.DESCRIPTION
    Runs, in order:
      1. the deterministic export check (dataset vs. source YAML);
      2. the Godot import, which registers the global script classes;
      3. the headless test suite of the engine;
      4. the contact sheet of the vector illustrations.
      5. runtime illustration/layout integration regressions.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\verify.ps1
    powershell -ExecutionPolicy Bypass -File tools\verify.ps1 -Godot "C:\ruta\Godot_v4.7.2-stable_win64_console.exe"
#>
param(
    [string]$Godot = "",
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$cut = Split-Path -Parent $here
$project = Join-Path $cut "godot"

function Fail([string]$message) {
    Write-Host "FAIL: $message" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Godot)) {
    $commandNames = @(
        "godot",
        "godot4",
        "Godot_v4.7.2-stable_win64_console.exe"
    )
    $Godot = $commandNames |
        ForEach-Object { Get-Command $_ -ErrorAction SilentlyContinue } |
        Select-Object -First 1 -ExpandProperty Source
    if ([string]::IsNullOrWhiteSpace($Godot)) {
        Fail "No Godot executable found in PATH; pass -Godot <path>."
    }
}

Write-Host "== 1/5 export determinism ==" -ForegroundColor Cyan
& $Python (Join-Path $here "oa_export_godot.py") --check
if ($LASTEXITCODE -ne 0) { Fail "the committed dataset does not match the regenerated one" }

Write-Host "== 2/5 godot import ==" -ForegroundColor Cyan
& $Godot --headless --path $project --editor --quit | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "the Godot import reported errors" }

Write-Host "== 3/5 engine tests ==" -ForegroundColor Cyan
& $Godot --headless --path $project --script res://tests/run_tests.gd
if ($LASTEXITCODE -ne 0) { Fail "the engine tests failed" }

Write-Host "== 4/5 illustration sheet ==" -ForegroundColor Cyan
& $Godot --headless --path $project --script res://tools/capture_scenes.gd
if ($LASTEXITCODE -ne 0) { Fail "the illustration sheet could not be rendered" }

Write-Host "== 5/5 runtime illustration integration ==" -ForegroundColor Cyan
& $Godot --headless --path $project --script res://tests/test_runtime_illustration.gd
if ($LASTEXITCODE -ne 0) { Fail "the runtime illustration integration tests failed" }

Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
