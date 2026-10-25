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
      6. deterministic vector-art compilation and CH_01 batch regressions;
      7. deterministic GRATE variants and state-aware presentation regressions.

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

Write-Host "== 1/7 export determinism ==" -ForegroundColor Cyan
& $Python (Join-Path $here "oa_export_godot.py") --check
if ($LASTEXITCODE -ne 0) { Fail "the committed dataset does not match the regenerated one" }
& $Python (Join-Path $here "test_simulation_graph.py")
if ($LASTEXITCODE -ne 0) { Fail "the global simulation data contract failed" }

Write-Host "== 2/7 godot import ==" -ForegroundColor Cyan
& $Godot --headless --path $project --editor --quit | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "the Godot import reported errors" }

Write-Host "== 3/7 engine tests ==" -ForegroundColor Cyan
& $Godot --headless --path $project --script res://tests/run_tests.gd
if ($LASTEXITCODE -ne 0) { Fail "the engine tests failed" }
& $Godot --headless --path $project --script res://tests/test_simulation_graph_isolation.gd
if ($LASTEXITCODE -ne 0) { Fail "the simulation graph changed the playable boundary" }
& $Godot --headless --path $project --script res://tests/test_travel_cycle.gd
if ($LASTEXITCODE -ne 0) { Fail "the historical travel cycle tests failed" }

Write-Host "== 4/7 illustration sheet ==" -ForegroundColor Cyan
& $Godot --headless --path $project --script res://tools/capture_scenes.gd
if ($LASTEXITCODE -ne 0) { Fail "the illustration sheet could not be rendered" }

Write-Host "== 5/7 runtime illustration integration ==" -ForegroundColor Cyan
& $Godot --headless --path $project --script res://tests/test_runtime_illustration.gd
if ($LASTEXITCODE -ne 0) { Fail "the runtime illustration integration tests failed" }

Write-Host "== 6/7 CH_01 vector art ==" -ForegroundColor Cyan
& $Python (Join-Path $here "build_ch01_vector_art.py") --check
if ($LASTEXITCODE -ne 0) { Fail "the vector artwork differs from its authored geometry" }
& $Godot --headless --path $project --script res://tests/test_ch01_vector_art.gd
if ($LASTEXITCODE -ne 0) { Fail "the CH_01 vector-art batch tests failed" }

Write-Host "== 7/7 GRATE state art ==" -ForegroundColor Cyan
& $Python (Join-Path $here "build_grate_variants.py") --check
if ($LASTEXITCODE -ne 0) { Fail "the GRATE artwork differs from its authored geometry" }
& $Godot --headless --path $project --script res://tests/test_grate_state_art.gd
if ($LASTEXITCODE -ne 0) { Fail "the GRATE state-art tests failed" }

Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
