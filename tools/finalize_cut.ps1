# Local CAR cut finalizer. This tool never pushes, merges, tags or releases.
# Usage: .\tools\finalize_cut.ps1 -CutId CAR-AUTO-001 -CommitMessage "CAR-AUTO-001: ..." -Files @(...)
# Diagnostic: add -DryRun. Retry a committed-but-unsynced cut with the same inputs.
param(
    [string]$CutId,
    [string]$CommitMessage,
    [string[]]$Files = @(),
    [switch]$DryRun,
    [switch]$SkipSync,
    [switch]$SelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:GitOperations = [Collections.Generic.List[string]]::new()

function Invoke-GitText {
    param([string]$Root, [string[]]$GitArgs)
    $script:GitOperations.Add(($GitArgs -join ' '))
    $output = & git -C $Root @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Falló git $($GitArgs -join ' ') (código $LASTEXITCODE): $($output -join [Environment]::NewLine)"
    }
    return @($output | ForEach-Object { [string]$_ })
}

function Test-GitQuiet {
    param([string]$Root, [string[]]$GitArgs)
    $null = & git -C $Root @GitArgs 2>&1
    return $LASTEXITCODE -eq 0
}

function ConvertTo-SafeRelativePath {
    param([string]$Path, [string]$Root)
    if ([string]::IsNullOrWhiteSpace($Path) -or $Path.Contains("`n") -or $Path.Contains("`r")) {
        throw 'Lista de archivos vacía o con ruta no representable.'
    }
    $normal = $Path.Replace('\', '/')
    if ($normal.StartsWith('/') -or $normal -match '^[A-Za-z]:' -or
        @($normal.Split('/')) -contains '..' -or @($normal.Split('/')) -contains '.') {
        throw "Ruta fuera del repositorio: $Path"
    }
    if ($normal -match '(^|/)\.git(/|$)|(^|/)\.godot(/|$)|(^|/)\.agents(/|$)|(^|/)\.env(?:\.|$)|(^|/)(?:private|secrets?|credentials?)(?:/|$)|\.(?:pem|p12|pfx|key)$') {
        throw "Ruta excluida por material privado, credenciales o caché: $normal"
    }
    $fullRoot = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    $fullPath = [IO.Path]::GetFullPath((Join-Path $Root ($normal.Replace('/', '\'))))
    if (-not $fullPath.StartsWith($fullRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Ruta fuera de la raíz CAR: $Path"
    }
    return $normal
}

function Get-ChangedPaths {
    param([string]$Root)
    $tracked = @(Invoke-GitText -Root $Root -GitArgs @('diff', '--name-only', '--'))
    $untracked = @(Invoke-GitText -Root $Root -GitArgs @('ls-files', '--others', '--exclude-standard'))
    return @($tracked + $untracked | Sort-Object -Unique)
}

function Assert-CleanIndex {
    param([string]$Root)
    if (-not (Test-GitQuiet -Root $Root -GitArgs @('diff', '--cached', '--quiet', '--'))) {
        throw 'Índice Git contaminado: hay cambios staged previos. No se modificó.'
    }
    $unmerged = @(Invoke-GitText -Root $Root -GitArgs @('ls-files', '-u'))
    if ($unmerged.Count -gt 0) { throw 'Hay conflictos sin resolver en el índice.' }
}

function Assert-ChangeSetMatches {
    param([string[]]$Actual, [string[]]$Allowed)
    $actualSet = @($Actual | Sort-Object -Unique)
    $allowedSet = @($Allowed | Sort-Object -Unique)
    $difference = @(Compare-Object -ReferenceObject $actualSet -DifferenceObject $allowedSet)
    if ($difference.Count -gt 0) {
        $details = $difference | ForEach-Object { "$($_.SideIndicator) $($_.InputObject)" }
        throw "El conjunto real de cambios no coincide con -Files:`n$($details -join [Environment]::NewLine)"
    }
}

function Assert-CutIdentity {
    param([string]$Id, [string]$Message, [string[]]$Allowed)
    if ($Id -notmatch '^CAR-[A-Z0-9]+(?:-[A-Z0-9]+)*$') { throw "CutId no válido para CAR: $Id" }
    if ([string]::IsNullOrWhiteSpace($Message) -or $Message -notmatch [regex]::Escape($Id)) {
        throw 'CommitMessage debe identificar literalmente el CutId.'
    }
    $slug = $Id.ToLowerInvariant().Replace('-', '_')
    $changeDocs = @($Allowed | Where-Object { $_ -match ('^project_state/changes/' + [regex]::Escape($slug) + '[^/]*/CHANGE\.md$') })
    if ($changeDocs.Count -ne 1) { throw "-Files debe incluir un único CHANGE.md bajo project_state/changes/$slug..." }
}

function Assert-NoTrailingWhitespace {
    param([string]$Root, [string[]]$Paths)
    foreach ($relative in $Paths) {
        $path = Join-Path $Root ($relative.Replace('/', '\'))
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "No existe el archivo autorizado: $relative" }
        $item = Get-Item -LiteralPath $path -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "No se aceptan symlinks/reparse points: $relative" }
        if ($item.Length -gt 0 -and $item.Length -lt 20MB) {
            $bytes = [IO.File]::ReadAllBytes($path)
            if ($bytes -notcontains 0) {
                $lines = [Text.Encoding]::UTF8.GetString($bytes) -split "`n"
                for ($i = 0; $i -lt $lines.Count; $i++) {
                    if ($lines[$i] -match '[ \t]+\r?$') { throw "Whitespace final en $relative, línea $($i + 1)." }
                }
            }
        }
    }
}

function Invoke-CheckAction {
    param([string]$Name, [scriptblock]$Action)
    try {
        $global:LASTEXITCODE = 0
        & $Action
        if ($LASTEXITCODE -is [int] -and $LASTEXITCODE -ne 0) { throw "código de salida $LASTEXITCODE" }
        Write-Host "PASS: $Name"
    } catch {
        throw "Verificación fallida ($Name): $($_.Exception.Message)"
    }
}

function Invoke-ApplicableChecks {
    param([string]$Root, [string[]]$Paths)
    if ($Paths -contains 'tools/finalize_cut.ps1') {
        Invoke-CheckAction -Name 'finalize_cut.ps1 -SelfTest' -Action { & (Join-Path $Root 'tools/finalize_cut.ps1') -SelfTest }
    }
    if ($Paths -contains 'sync_to_drive.ps1') {
        Invoke-CheckAction -Name 'sync_to_drive.ps1 -SelfTest' -Action { & (Join-Path $Root 'sync_to_drive.ps1') -SelfTest }
    }
    $godotPaths = @($Paths | Where-Object { $_ -match '^07_godot_open_adventure/godot/(src|data|tests)/' -or $_ -eq '06_reconstruccion_drawio/Open_Adventure.yaml' })
    if ($godotPaths.Count -gt 0) {
        Invoke-CheckAction -Name 'Exportador determinista' -Action { & python (Join-Path $Root '07_godot_open_adventure/tools/oa_export_godot.py') --check }
        Invoke-CheckAction -Name 'verify.ps1' -Action { & (Join-Path $Root '07_godot_open_adventure/tools/verify.ps1') }
    }
}

function Invoke-FinalizeCutCore {
    param(
        [string]$Root,
        [string]$Id,
        [string]$Message,
        [string[]]$InputFiles,
        [switch]$Preview,
        [switch]$NoSync
    )
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    if (-not (Test-Path -LiteralPath (Join-Path $rootFull '.git')) -or
        -not (Test-Path -LiteralPath (Join-Path $rootFull 'AGENTS.md')) -or
        -not (Test-Path -LiteralPath (Join-Path $rootFull 'README.md'))) {
        throw "No es una raíz CAR reconocible: $rootFull"
    }
    $gitRoot = (Invoke-GitText -Root $rootFull -GitArgs @('rev-parse', '--show-toplevel') | Select-Object -First 1).Trim()
    if ([IO.Path]::GetFullPath($gitRoot).TrimEnd('\') -ne $rootFull) { throw "Raíz Git inesperada: $gitRoot" }
    Assert-CutIdentity -Id $Id -Message $Message -Allowed $InputFiles
    if ($InputFiles.Count -eq 0) { throw 'Debe proporcionarse una lista explícita -Files.' }
    $allowed = @($InputFiles | ForEach-Object { ConvertTo-SafeRelativePath -Path $_ -Root $rootFull } | Sort-Object -Unique)
    if ($allowed.Count -ne $InputFiles.Count) { throw 'La lista -Files contiene rutas repetidas.' }
    foreach ($relative in $allowed) {
        $full = Join-Path $rootFull ($relative.Replace('/', '\'))
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "No existe el archivo autorizado: $relative" }
        $ignored = & git -C $rootFull check-ignore -q -- $relative
        if ($LASTEXITCODE -eq 0) { throw "Git ignora el archivo autorizado: $relative" }
    }
    Assert-CleanIndex -Root $rootFull

    $actual = @(Get-ChangedPaths -Root $rootFull)
    if ($actual.Count -eq 0) {
        $lastMessage = (Invoke-GitText -Root $rootFull -GitArgs @('show', '-s', '--format=%B', 'HEAD') | ForEach-Object { $_ }) -join "`n"
        $lastFiles = if (Test-GitQuiet -Root $rootFull -GitArgs @('rev-parse', '--verify', 'HEAD^')) {
            @(Invoke-GitText -Root $rootFull -GitArgs @('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD^', 'HEAD'))
        } else {
            @(Invoke-GitText -Root $rootFull -GitArgs @('diff-tree', '--root', '--no-commit-id', '--name-only', '-r', 'HEAD'))
        }
        if ($lastMessage -notmatch [regex]::Escape($Id)) { throw 'No hay cambios y HEAD no identifica este corte; no se creará un commit vacío.' }
        Assert-ChangeSetMatches -Actual $lastFiles -Allowed $allowed
        Write-Host "El corte $Id ya está comprometido en HEAD; se omite un commit duplicado."
        if (-not $NoSync) {
            Invoke-CheckAction -Name 'reintento sync_to_drive.ps1 -DryRun' -Action { & (Join-Path $rootFull 'sync_to_drive.ps1') -DryRun }
            Invoke-CheckAction -Name 'reintento de sincronización' -Action { & (Join-Path $rootFull 'sync_to_drive.ps1') }
        }
        return
    }
    Assert-ChangeSetMatches -Actual $actual -Allowed $allowed
    Assert-NoTrailingWhitespace -Root $rootFull -Paths $allowed
    Invoke-CheckAction -Name 'git diff --check' -Action { & git -C $rootFull diff --check }
    Invoke-ApplicableChecks -Root $rootFull -Paths $allowed
    if ($Preview) {
        Write-Host "DRY RUN: se prepararían $($allowed.Count) archivos de ${Id}:"
        $allowed | ForEach-Object { Write-Host "  $_" }
        Write-Host "Mensaje: $Message"
        return
    }

    & git -C $rootFull add -- @allowed
    if ($LASTEXITCODE -ne 0) { throw 'git add explícito falló.' }
    $staged = @(Invoke-GitText -Root $rootFull -GitArgs @('diff', '--cached', '--name-only'))
    Assert-ChangeSetMatches -Actual $staged -Allowed $allowed
    Invoke-CheckAction -Name 'git diff --cached --check' -Action { & git -C $rootFull diff --cached --check }
    Write-Host 'Diff staged que se comprometerá:'
    & git -C $rootFull diff --cached --stat
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo revisar el diff staged.' }
    & git -C $rootFull commit -m $Message
    if ($LASTEXITCODE -ne 0) { throw 'git commit falló; el corte permanece staged para revisión.' }
    $commit = (Invoke-GitText -Root $rootFull -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
    Write-Host "COMMITTED: $commit"
    if (-not $NoSync) {
        try {
            Invoke-CheckAction -Name 'sync_to_drive.ps1 -DryRun' -Action { & (Join-Path $rootFull 'sync_to_drive.ps1') -DryRun }
            Invoke-CheckAction -Name 'sync_to_drive.ps1' -Action { & (Join-Path $rootFull 'sync_to_drive.ps1') }
        } catch {
            Write-Error "COMMITTED / SYNC FAILED: $commit — $($_.Exception.Message)"
            exit 2
        }
    }
    Write-Host "PASS: $Id; commit $commit; push no ejecutado."
}

function Test-FinalizerSelf {
    $checks = 0
    $temp = Join-Path ([IO.Path]::GetTempPath()) ('CAR-finalizer-test-' + [guid]::NewGuid().ToString('N'))
    try {
        New-Item -ItemType Directory -Path $temp | Out-Null
        $badPathRejected = $false
        try { ConvertTo-SafeRelativePath -Path '../outside.txt' -Root $temp | Out-Null } catch { $badPathRejected = $true }
        if (-not $badPathRejected) { throw 'No se rechazó una ruta fuera del repositorio.' }
        $checks++
        $privateRejected = $false
        try { ConvertTo-SafeRelativePath -Path '.env' -Root $temp | Out-Null } catch { $privateRejected = $true }
        if (-not $privateRejected) { throw 'No se rechazó una ruta de credenciales.' }
        $checks++
        $setRejected = $false
        try { Assert-ChangeSetMatches -Actual @('AGENTS.md') -Allowed @('CHANGE.md') } catch { $setRejected = $true }
        if (-not $setRejected) { throw 'No se rechazó un archivo no autorizado.' }
        $checks++
        $failedCheckRejected = $false
        try { Invoke-CheckAction -Name 'fixture failure' -Action { throw 'expected test failure' } } catch { $failedCheckRejected = $true }
        if (-not $failedCheckRejected) { throw 'No se propagó una verificación fallida.' }
        $checks++

        foreach ($name in @('AGENTS.md', 'README.md')) { Set-Content -LiteralPath (Join-Path $temp $name) -Value "fixture $name" -NoNewline }
        $docDir = Join-Path $temp 'project_state/changes/car_auto_001_cut_finalization'
        New-Item -ItemType Directory -Path $docDir -Force | Out-Null
        $changePath = Join-Path $docDir 'CHANGE.md'
        Set-Content -LiteralPath $changePath -Value 'baseline' -NoNewline
        & git -C $temp init --quiet
        & git -C $temp config user.name 'CAR Finalizer Test'
        & git -C $temp config user.email 'car-finalizer-test@example.invalid'
        & git -C $temp add -- AGENTS.md README.md project_state/changes/car_auto_001_cut_finalization/CHANGE.md
        & git -C $temp commit --quiet -m 'fixture baseline'
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el repositorio temporal de prueba.' }
        Set-Content -LiteralPath $changePath -Value 'CAR-AUTO-001 fixture delta' -NoNewline
        $fixtureFiles = @('project_state/changes/car_auto_001_cut_finalization/CHANGE.md')
        $before = (Invoke-GitText -Root $temp -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
        Invoke-FinalizeCutCore -Root $temp -Id 'CAR-AUTO-001' -Message 'CAR-AUTO-001: fixture' -InputFiles $fixtureFiles -Preview -NoSync
        $afterDryRun = (Invoke-GitText -Root $temp -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
        if ($before -ne $afterDryRun) { throw 'DryRun creó un commit.' }
        $checks++
        Invoke-FinalizeCutCore -Root $temp -Id 'CAR-AUTO-001' -Message 'CAR-AUTO-001: fixture' -InputFiles $fixtureFiles -NoSync
        $afterCommit = (Invoke-GitText -Root $temp -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
        if ($afterCommit -eq $before) { throw 'La prueba de finalización no creó su commit fixture.' }
        $checks++
        Invoke-FinalizeCutCore -Root $temp -Id 'CAR-AUTO-001' -Message 'CAR-AUTO-001: fixture' -InputFiles $fixtureFiles -NoSync
        $afterRetry = (Invoke-GitText -Root $temp -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
        if ($afterRetry -ne $afterCommit) { throw 'El reintento creó un commit duplicado.' }
        $checks++
        Set-Content -LiteralPath (Join-Path $temp 'AGENTS.md') -Value 'staged unrelated change' -NoNewline
        & git -C $temp add -- AGENTS.md
        $dirtyIndexRejected = $false
        try { Assert-CleanIndex -Root $temp } catch { $dirtyIndexRejected = $true }
        if (-not $dirtyIndexRejected) { throw 'No se rechazó un índice staged previamente.' }
        & git -C $temp reset --quiet HEAD -- AGENTS.md
        & git -C $temp checkout -- AGENTS.md
        $checks++
        $pushCalls = @($script:GitOperations | Where-Object { $_ -match '^push(?:\s|$)' })
        if ($pushCalls.Count -gt 0) { throw 'La prueba detectó una llamada Git push.' }
        $checks++
        Write-Host "PASS: $checks comprobaciones internas de finalize_cut.ps1"
    } finally {
        $tempFull = [IO.Path]::GetFullPath($temp)
        $tempParent = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
        if ($tempFull.StartsWith($tempParent, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $tempFull) -match '^CAR-finalizer-test-[0-9a-f]{32}$') {
            Remove-Item -LiteralPath $tempFull -Recurse -Force
        } else {
            throw "Ruta temporal inesperada; no se eliminó: $tempFull"
        }
    }
}

if ($SelfTest) {
    Test-FinalizerSelf
    return
}
if ([string]::IsNullOrWhiteSpace($CutId) -or [string]::IsNullOrWhiteSpace($CommitMessage) -or $Files.Count -eq 0) {
    throw 'Uso: -CutId CAR-... -CommitMessage "CAR-...: ..." -Files @("ruta", ...).'
}
$repositoryRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Invoke-FinalizeCutCore -Root $repositoryRoot -Id $CutId -Message $CommitMessage -InputFiles $Files -Preview:$DryRun -NoSync:$SkipSync
