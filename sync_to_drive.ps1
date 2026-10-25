# Sincronización local -> Drive, limitada al snapshot comprometido de Git.
# No borra contenido del destino y se detiene ante ediciones divergentes en Drive.
# Uso: .\sync_to_drive.ps1 [-DryRun] | .\sync_to_drive.ps1 -SelfTest
param(
    [switch]$DryRun,
    [switch]$SelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-GitText {
    param([string]$Root, [string[]]$GitArgs)
    $output = & git -C $Root @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Falló git $($GitArgs -join ' ') (código $LASTEXITCODE): $($output -join [Environment]::NewLine)"
    }
    return @($output | ForEach-Object { [string]$_ })
}

function Assert-RobocopyCode {
    param([int]$Code)
    if ($Code -lt 0 -or $Code -ge 8) {
        throw "Robocopy terminó con error (código $Code)."
    }
}

function Assert-PathExists {
    param([bool]$Exists, [string]$Description)
    if (-not $Exists) { throw "$Description no está disponible." }
}

function Assert-NoTreeOverlap {
    param([string]$Source, [string]$Destination)
    $sourceFull = [IO.Path]::GetFullPath($Source).TrimEnd('\')
    $destinationFull = [IO.Path]::GetFullPath($Destination).TrimEnd('\')
    $sourcePrefix = $sourceFull + '\'
    $destinationPrefix = $destinationFull + '\'
    if ($sourceFull.Equals($destinationFull, [StringComparison]::OrdinalIgnoreCase) -or
        $sourceFull.StartsWith($destinationPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        $destinationFull.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'El origen y el destino no pueden ser iguales ni estar anidados.'
    }
}

function ConvertTo-SafeRelativePath {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or $Path.Contains("`n") -or $Path.Contains("`r")) {
        throw 'Git devolvió una ruta vacía o no representable de forma segura.'
    }
    $normal = $Path.Replace('\', '/')
    if ($normal.StartsWith('/') -or $normal -match '^[A-Za-z]:' -or
        @($normal.Split('/')) -contains '..' -or @($normal.Split('/')) -contains '.') {
        throw "Ruta Git fuera del formato relativo permitido: $Path"
    }
    if ($normal -match '(^|/)\.git(/|$)|(^|/)\.godot(/|$)|(^|/)\.agents(/|$)|(^|/)\.env(?:\.|$)|(^|/)(?:private|secrets?|credentials?)(?:/|$)|\.(?:pem|p12|pfx|key)$') {
        throw "Ruta excluida por contener material privado o temporal: $Path"
    }
    return $normal
}

function Test-SafeOverwrite {
    param([string]$DestinationHash, [string]$SourceHash, [string]$BaselineHash)
    if ($DestinationHash -eq $SourceHash) { return $true }
    return -not [string]::IsNullOrWhiteSpace($BaselineHash) -and $DestinationHash -eq $BaselineHash
}

function Get-FileSha256 {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-NoReparsePath {
    param([string]$Root, [string]$RelativePath)
    $cursor = [IO.Path]::GetFullPath($Root)
    if (Test-Path -LiteralPath $cursor) {
        $rootItem = Get-Item -LiteralPath $cursor -Force
        if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "La raíz de sincronización es un reparse point: $cursor"
        }
    }
    $parts = @($RelativePath.Replace('\', '/').Split('/'))
    foreach ($part in $parts) {
        $cursor = Join-Path $cursor $part
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "No se siguen junctions/symlinks durante la sincronización: $cursor"
            }
        }
    }
}

function Assert-NoSensitiveContent {
    param([string]$Path, [string]$RelativePath)
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes -contains 0) { return }
    $text = [Text.Encoding]::UTF8.GetString($bytes)
    $patterns = @(
        '-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        '\bAKIA[0-9A-Z]{16}\b',
        '\bgh[pousr]_[A-Za-z0-9]{30,}\b',
        '(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*["''][^"'']{12,}["'']'
    )
    foreach ($pattern in $patterns) {
        if ($text -match $pattern) { throw "Posible credencial detectada en el archivo versionado: $RelativePath" }
    }
}

function Test-SyncHelpers {
    $passed = 0
    foreach ($code in 0..7) { Assert-RobocopyCode -Code $code; $passed++ }
    $failedAsExpected = $false
    try { Assert-RobocopyCode -Code 8 } catch { $failedAsExpected = $true }
    if (-not $failedAsExpected) { throw 'La prueba del límite de fallo Robocopy no falló como se esperaba.' }
    $passed++
    $overlapRejected = $false
    try { Assert-NoTreeOverlap -Source 'C:\CAR' -Destination 'C:\CAR\nested' } catch { $overlapRejected = $true }
    if (-not $overlapRejected) { throw 'No se detectó un destino anidado.' }
    Assert-NoTreeOverlap -Source 'C:\CAR' -Destination 'G:\Drive\CAR'
    $passed += 2
    if (-not (Test-SafeOverwrite -DestinationHash 'same' -SourceHash 'same' -BaselineHash 'old')) {
        throw 'No se aceptó un archivo ya sincronizado.'
    }
    if (-not (Test-SafeOverwrite -DestinationHash 'old' -SourceHash 'new' -BaselineHash 'old')) {
        throw 'No se aceptó la versión base registrada.'
    }
    if (Test-SafeOverwrite -DestinationHash 'drive-edit' -SourceHash 'new' -BaselineHash 'old') {
        throw 'No se detectó una edición divergente en Drive.'
    }
    $passed += 3
    foreach ($bad in @('.env', 'docs/private/notes.txt', 'keys/service.pem', '.godot/imported.bin')) {
        $rejected = $false
        try { ConvertTo-SafeRelativePath -Path $bad | Out-Null } catch { $rejected = $true }
        if (-not $rejected) { throw "No se rechazó la ruta sensible: $bad" }
        $passed++
    }
    $existsRejected = $false
    try { Assert-PathExists -Exists $false -Description 'Unidad Drive de prueba' } catch { $existsRejected = $true }
    if (-not $existsRejected) { throw 'No se detectó la ausencia de la unidad de destino.' }
    $passed++
    $archiveProbe = Join-Path ([IO.Path]::GetTempPath()) ('CAR-archive-test-' + [guid]::NewGuid().ToString('N'))
    try {
        New-Item -ItemType Directory -Path $archiveProbe | Out-Null
        $archivePath = Join-Path $archiveProbe 'snapshot.zip'
        $archiveArgs = @('-C', $PSScriptRoot, 'archive', '--format=zip', "--output=$archivePath", 'HEAD', 'sync_to_drive.ps1')
        & git @archiveArgs
        if ($LASTEXITCODE -ne 0) { throw 'git archive no pudo seleccionar una ruta del snapshot.' }
        Expand-Archive -LiteralPath $archivePath -DestinationPath (Join-Path $archiveProbe 'out')
        if (-not (Test-Path -LiteralPath (Join-Path $archiveProbe 'out/sync_to_drive.ps1') -PathType Leaf)) {
            throw 'git archive no produjo el archivo seleccionado.'
        }
        $passed++
    } finally {
        $archiveFull = [IO.Path]::GetFullPath($archiveProbe)
        $archiveParent = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
        if ($archiveFull.StartsWith($archiveParent, [StringComparison]::OrdinalIgnoreCase) -and
            (Split-Path -Leaf $archiveFull) -match '^CAR-archive-test-[0-9a-f]{32}$') {
            Remove-Item -LiteralPath $archiveFull -Recurse -Force
        } else {
            throw "Ruta temporal inesperada; no se eliminó: $archiveFull"
        }
    }
    Write-Host "PASS: $passed comprobaciones internas de sync_to_drive.ps1"
}

function Invoke-Sync {
    param([switch]$ListOnly)
    $source = [IO.Path]::GetFullPath($PSScriptRoot)
    $destination = 'G:\Mi unidad\RPG_Archaeology_IF'
    Assert-NoTreeOverlap -Source $source -Destination $destination
    $driveRoot = [IO.Path]::GetPathRoot($destination)
    Assert-PathExists -Exists (Test-Path -LiteralPath $driveRoot -PathType Container) -Description "La unidad $driveRoot (Google Drive)"
    $destinationRelative = $destination.Substring($driveRoot.Length).TrimStart('\')
    Assert-NoReparsePath -Root $driveRoot -RelativePath $destinationRelative
    if (-not (Test-Path -LiteralPath (Join-Path $source 'AGENTS.md')) -or
        -not (Test-Path -LiteralPath (Join-Path $source 'README.md')) -or
        -not (Test-Path -LiteralPath (Join-Path $source '.git'))) {
        throw "El origen no parece ser la raíz CAR con Git: $source"
    }
    $gitRoot = (Invoke-GitText -Root $source -GitArgs @('rev-parse', '--show-toplevel') | Select-Object -First 1).Trim()
    if ([IO.Path]::GetFullPath($gitRoot).TrimEnd('\') -ne $source.TrimEnd('\')) {
        throw "Raíz Git inesperada: $gitRoot"
    }
    $dirty = & git -C $source diff --quiet HEAD --
    if ($LASTEXITCODE -ne 0) { throw 'Hay cambios tracked sin commit; sincroniza solo después de finalizar el corte.' }
    $staged = & git -C $source diff --cached --quiet --
    if ($LASTEXITCODE -ne 0) { throw 'El índice Git no está limpio; no se sincronizó Drive.' }
    $unmerged = @(Invoke-GitText -Root $source -GitArgs @('ls-files', '-u'))
    if ($unmerged.Count -gt 0) { throw 'Hay conflictos de merge en el índice.' }

    $files = @(Invoke-GitText -Root $source -GitArgs @('ls-files', '--cached'))
    if ($files.Count -eq 0) { throw 'No hay archivos versionados que sincronizar.' }
    $paths = @($files | ForEach-Object { ConvertTo-SafeRelativePath -Path $_ })
    $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ('CAR-sync-' + [guid]::NewGuid().ToString('N'))
    $stage = Join-Path $tempRoot 'snapshot'
    $gitDirText = (Invoke-GitText -Root $source -GitArgs @('rev-parse', '--git-common-dir') | Select-Object -First 1).Trim()
    $gitDir = if ([IO.Path]::IsPathRooted($gitDirText)) { $gitDirText } else { Join-Path $source $gitDirText }
    $statePath = Join-Path $gitDir 'car_drive_sync_state.json'
    $state = $null
    if (Test-Path -LiteralPath $statePath -PathType Leaf) {
        try { $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json } catch { throw "Estado local de sync ilegible: $statePath" }
        if ($state.schema -ne 1 -or $null -eq $state.files) { throw 'El estado local de sincronización tiene un esquema desconocido.' }
    }

    try {
        New-Item -ItemType Directory -Path $stage -Force | Out-Null
        $sourceHashes = @{}
        foreach ($index in 0..($paths.Count - 1)) {
            $relative = $paths[$index]
            Assert-NoReparsePath -Root $source -RelativePath $relative
            $from = Join-Path $source ($relative.Replace('/', '\'))
            if (-not (Test-Path -LiteralPath $from -PathType Leaf)) { throw "Falta archivo versionado: $relative" }
            $item = Get-Item -LiteralPath $from -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "No se copian enlaces o reparse points: $relative" }
            Assert-NoSensitiveContent -Path $from -RelativePath $relative
            $to = Join-Path $stage ($relative.Replace('/', '\'))
            $parent = Split-Path -Parent $to
            if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            Copy-Item -LiteralPath $from -Destination $to
            $sourceHashes[$relative] = Get-FileSha256 -Path $to
        }

        $destinationExists = Test-Path -LiteralPath $destination -PathType Container
        if (-not $destinationExists -and -not $DryRun) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
            $destinationExists = $true
        }
        if ($destinationExists) {
            $mismatches = [Collections.Generic.List[string]]::new()
            foreach ($relative in $paths) {
                $target = Join-Path $destination ($relative.Replace('/', '\'))
                if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { continue }
                Assert-NoReparsePath -Root $destination -RelativePath $relative
                $targetItem = Get-Item -LiteralPath $target -Force
                if (($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Destino es enlace/reparse point; parada segura: $relative" }
                $targetHash = Get-FileSha256 -Path $target
                $baseHash = ''
                if ($null -ne $state -and $null -ne $state.files) {
                    $stateProperty = $state.files.PSObject.Properties[$relative]
                    if ($null -ne $stateProperty) { $baseHash = [string]$stateProperty.Value }
                }
                if (-not (Test-SafeOverwrite -DestinationHash $targetHash -SourceHash $sourceHashes[$relative] -BaselineHash $baseHash)) {
                    $mismatches.Add($relative)
                }
            }
            if ($mismatches.Count -gt 0 -and $null -eq $state) {
                $commonAncestorFound = $false
                $ancestors = @(Invoke-GitText -Root $source -GitArgs @('rev-list', '--max-count=100', 'HEAD'))
                foreach ($ancestor in $ancestors) {
                    $candidateStage = Join-Path $tempRoot ('ancestor-' + $ancestor.Substring(0, 12))
                    $candidateArchive = Join-Path $tempRoot ('ancestor-' + $ancestor.Substring(0, 12) + '.zip')
                    New-Item -ItemType Directory -Path $candidateStage -Force | Out-Null
                    $archiveArgs = @('-C', $source, 'archive', '--format=zip', "--output=$candidateArchive", $ancestor.Trim()) + @($mismatches)
                    & git @archiveArgs
                    if ($LASTEXITCODE -ne 0) { continue }
                    Expand-Archive -LiteralPath $candidateArchive -DestinationPath $candidateStage -Force
                    $matchesAncestor = $true
                    foreach ($relative in $mismatches) {
                        $target = Join-Path $destination ($relative.Replace('/', '\'))
                        $oldVersion = Join-Path $candidateStage ($relative.Replace('/', '\'))
                        if (-not (Test-Path -LiteralPath $oldVersion -PathType Leaf) -or
                            (Get-FileSha256 -Path $target) -ne (Get-FileSha256 -Path $oldVersion)) {
                            $matchesAncestor = $false
                            break
                        }
                    }
                    if ($matchesAncestor) { $commonAncestorFound = $true; break }
                }
                if (-not $commonAncestorFound) {
                    throw "No se encontró una base Git común para las diferencias de Drive; no se sobrescribió: $($mismatches -join ', ')"
                }
            } elseif ($mismatches.Count -gt 0) {
                throw "Posible edición directa en Drive; no se sobrescribe: $($mismatches -join ', ')"
            }
        }

        if ($ListOnly) {
            Write-Host "Snapshot versionado: $($paths.Count) archivos; commit $(Invoke-GitText -Root $source -GitArgs @('rev-parse', '--short', 'HEAD') | Select-Object -First 1)"
            $global:LASTEXITCODE = 0
            return
        }
        if (-not $destinationExists -and $DryRun) {
            Write-Host "[DRY RUN] Se crearía el destino: $destination"
            $global:LASTEXITCODE = 0
            return
        }
        $robocopyArgs = @(
            $stage, $destination, '/E', '/XJ', '/R:2', '/W:2',
            '/COPY:DAT', '/DCOPY:DAT', '/NP'
        )
        if ($DryRun) { $robocopyArgs += '/L' }
        Write-Host "Origen comprometido: $(Invoke-GitText -Root $source -GitArgs @('rev-parse', '--short', 'HEAD') | Select-Object -First 1)"
        Write-Host "Archivos versionados: $($paths.Count); destino: $destination"
        Write-Host 'Modo unidireccional; sin /MIR, /PURGE ni borrados. Extras del destino se conservan.'
        & robocopy @robocopyArgs
        $code = [int]$LASTEXITCODE
        Assert-RobocopyCode -Code $code
        if ($DryRun) {
            Write-Host "DRY RUN completado (Robocopy $code); no se modificaron destino ni estado local."
            $global:LASTEXITCODE = 0
            return
        }
        foreach ($relative in $paths) {
            $target = Join-Path $destination ($relative.Replace('/', '\'))
            if (-not (Test-Path -LiteralPath $target -PathType Leaf) -or (Get-FileSha256 -Path $target) -ne $sourceHashes[$relative]) {
                throw "Verificación posterior a Robocopy fallida: $relative"
            }
        }
        $stateFiles = @{}
        if ($null -ne $state -and $null -ne $state.files) {
            foreach ($property in $state.files.PSObject.Properties) { $stateFiles[$property.Name] = [string]$property.Value }
        }
        foreach ($relative in $paths) { $stateFiles[$relative] = $sourceHashes[$relative] }
        $newState = [ordered]@{ schema = 1; head = (Invoke-GitText -Root $source -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1); files = $stateFiles }
        $stateTemp = "$statePath.tmp"
        $newState | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $stateTemp -Encoding utf8
        Move-Item -LiteralPath $stateTemp -Destination $statePath -Force
        Write-Host "PASS: $($paths.Count) versionados sincronizados y verificados (Robocopy $code)."
        $global:LASTEXITCODE = 0
    } finally {
        if (Test-Path -LiteralPath $tempRoot) {
            $tempFull = [IO.Path]::GetFullPath($tempRoot)
            $tempParent = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
            if (-not $tempFull.StartsWith($tempParent, [StringComparison]::OrdinalIgnoreCase) -or
                (Split-Path -Leaf $tempFull) -notmatch '^CAR-sync-[0-9a-f]{32}$') {
                throw "Ruta temporal inesperada; no se eliminó: $tempFull"
            }
            Remove-Item -LiteralPath $tempFull -Recurse -Force
        }
    }
}

if ($SelfTest) {
    Test-SyncHelpers
    return
}
Invoke-Sync
