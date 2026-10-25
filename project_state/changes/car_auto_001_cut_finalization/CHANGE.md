# CAR-AUTO-001 — Automated Cut Finalization & Drive Synchronization

Estado: **IMPLEMENTADO / VALIDADO — commits locales y sincronización verificada; sin push**
Alcance: commits locales identificados por corte CAR y sincronización no destructiva del snapshot versionado a `G:\Mi unidad\RPG_Archaeology_IF`.

## Política y límites

El propietario autorizó de forma permanente, solo para este repositorio, crear commits locales de archivos de un corte expresamente autorizado y sincronizarlos a Drive después de cada commit correcto. Esta autorización cubre informes de investigación completada aunque las propuestas sigan pendientes. No autoriza iniciar cortes, ampliar sus archivos ni declarar un estado de aceptación que no se haya verificado.

No se autoriza push, merge, tags, releases, publicación, commits de cambios humanos ajenos, implementación de propuestas, cambios en otros repositorios ni eliminación de archivos de Drive. Los contratos compartidos permanecen intactos: esta política CAR precisa su autorización humana dentro del repositorio, no se distribuye a otros proyectos.

## Herramientas

### `tools/finalize_cut.ps1`

Uso normal, con rutas relativas y una lista exacta:

```powershell
.\tools\finalize_cut.ps1 `
  -CutId CAR-AUTO-001 `
  -CommitMessage "CAR-AUTO-001: automate local cut finalization" `
  -Files @(
    "AGENTS.md",
    "sync_to_drive.ps1",
    "tools/finalize_cut.ps1",
    "project_state/changes/car_auto_001_cut_finalization/CHANGE.md"
  )
```

`-DryRun` revisa raíz, ID, conjunto real de cambios, índice, rutas y whitespace, pero no hace staging ni commit. `-SkipSync` solo es para diagnóstico; no debe usarse para finalizar un corte ordinario. El mensaje debe incluir el `CutId`, y `-Files` debe incluir el CHANGE del corte. Se rechazan rutas fuera del repositorio, ignoradas, repetidas o con nombres de credenciales/caché; también se detiene si existe staging previo o cualquier cambio fuera de la lista.

El finalizador ejecuta `git diff --check`, las pruebas internas de las herramientas modificadas y, cuando el inventario incluye código/datos/tests Godot, exportador `--check` y `verify.ps1`. Después prepara únicamente `-Files`, comprueba el inventario staged y su diff, y crea un único commit. No contiene ni invoca `git push`.

Si el commit se creó y el sync falla, el resultado es **COMMITTED / SYNC FAILED**. Repetir la misma llamada identifica el commit por `CutId` y por su conjunto exacto de archivos; no crea commit duplicado y vuelve a intentar el sync. Si HEAD no coincide con ese corte, se detiene.

### `sync_to_drive.ps1`

```powershell
.\sync_to_drive.ps1 -DryRun
.\sync_to_drive.ps1 -SelfTest
```

El sincronizador verifica que se ejecuta en la raíz CAR, que Drive está montado, y que índice y archivos rastreados están limpios. Construye una carpeta temporal desde los archivos versionados de Git y pasa esa carpeta a Robocopy; los archivos no rastreados e ignorados del origen no entran en el conjunto. La lista de rutas y una inspección básica del contenido rechazan credenciales y material privado evidente.

La copia es local → Drive, incremental y no destructiva. Usa `/E` y `/XJ`; no usa `/MIR`, `/PURGE` ni opciones que muevan archivos. Los archivos exclusivos del destino —incluidos los `.agents` y `.git` observados en la carpeta actual de Drive— se conservan. Códigos Robocopy 0–7 se consideran finalización/advertencia; 8 o superior falla. Tras copiar, se comprueba SHA-256 de cada archivo versionado.

Un estado de sincronización local bajo `.git/car_drive_sync_state.json` recuerda la huella anterior. Las huellas de archivos de texto normalizan exclusivamente finales de línea LF/CRLF; no normalizan espacios ni contenido. Si aún no existe estado, el primer sync permite sobrescribir contenido solo cuando los archivos divergentes coinciden, todos, con un mismo ancestro Git reconocido (hasta 100 commits); si no puede demostrar una base común, se detiene. Tras un sync correcto, el estado local se actualiza; no se añade al repositorio ni a Drive.

## Recuperación y límites

- **Índice contaminado / cambio inesperado:** detenerse; revisar manualmente Git. La herramienta no limpia staging ni descarta archivos.
- **Verificación fallida:** no se crea commit; preservar y diagnosticar el fallo dentro del corte.
- **Commit correcto, sync fallido:** conservar el commit y repetir la misma llamada; no usar amend ni crear commit vacío.
- **Diferencia en Drive no reconocida:** no sobrescribir. Comparar el archivo con el commit/base identificados y decidir manualmente qué contenido conservar antes de reintentar.
- **Drive ausente, archivo sensible o ruta/reparse point:** detenerse antes de copiar.
- **Dry run:** no modifica el índice ni los archivos de Drive; la ejecución normal de sync después de un commit es la que comprueba escritura real.

La comparación de destino reduce el riesgo de sobrescribir ediciones directas, pero no proporciona bloqueo atómico frente a una edición simultánea entre la comprobación y Robocopy. Para una garantía estricta durante edición concurrente, se debe detener la sincronización y acordar un mecanismo de bloqueo antes de continuar.

## Evidencia y cierre

### Estado previo y trazabilidad

El preflight de este cierre confirmó la raíz `C:\remake\Colossal-Adventure-Reimagination-public`, rama `main`, HEAD `176492ab13f418414c18df6775ec28cabaa88122`, índice y working tree limpios, y cuatro commits locales por delante de la referencia local `origin/main` (`b5623864d11e0081096df5e4a61900a5ef4bc4a6`). No se consultó el remoto en vivo. El estado Git posterior al commit de reconciliación se informa en el resultado de ejecución.

Los cuatro commits CAR-AUTO-001 verificados en el historial local son:

- 1c77e491c5bff817560d350c324c7cd68d6c6d1d — automatización del cierre local de cortes.
- a5bf5f4fb90e5e043632404ed01cffdd2a223845 — corrección de reintento de sincronización.
- d0d820790e481730b001b89f32fc99ad399a1564 — corrección de detección de ancestro Git.
- 176492ab13f418414c18df6775ec28cabaa88122 — comparación de texto que normaliza solo LF/CRLF.

No se encontraron archivos de log independientes de la ejecución original. Por eso, el informe de ejecución anterior se trató como antecedente, no como revalidación. El estado local `.git/car_drive_sync_state.json` registra HEAD `176492ab13f418414c18df6775ec28cabaa88122` antes de esta reconciliación; la sincronización posterior al commit documental se comprueba durante el cierre actual.

### Verificaciones reejecutadas en el cierre

Entorno: PowerShell 7.6.5, 2026-10-25.

- `tools/finalize_cut.ps1 -SelfTest`: PASS — 9 comprobaciones internas. Incluye dry run, commit/reintento en un repositorio fixture temporal, rechazo de staging ajeno y ausencia de llamada a push. El commit fixture se creó y eliminó dentro de la carpeta temporal de prueba.
- `sync_to_drive.ps1 -SelfTest`: PASS — 21 comprobaciones internas. Comprueba códigos Robocopy, rutas/solapamiento, protección frente a divergencias y normalización LF/CRLF.
- Estas comprobaciones son pruebas de las herramientas CAR; no son los 448 checks de Godot. No se repitió Godot porque el cierre modifica solo documentación y el finalizador no requiere esa suite para este inventario.

La ejecución real de `tools/finalize_cut.ps1` para este registro verifica `git diff --check`, prepara solo los tres documentos autorizados, crea un commit local y después ejecuta el dry run y la sincronización a Drive. El resultado de copia, código Robocopy, cantidad de archivos y verificación posterior de hashes se confirma en el informe de ejecución de este cierre. Los extras del destino se preservan; ningún push se ejecuta.

### Reconciliación de estado

- La política CAR de commit local para cortes expresamente autorizados, seguida de sync no destructivo de archivos rastreados, está documentada en este repositorio. No autoriza push.
- `project_state/CURRENT_STATE.md` se actualiza en este corte: el estado anterior 0484104 estaba desfasado respecto del historial local. Se conserva f59c413550dd3566e63af0c98a8df17a96359768 como baseline histórico.
- CAR-CORE-001 queda como investigación/Decision Gate completado; implementación no autorizada. Su informe demuestra que la proyección de grafo completo para simulación puede separarse de las habitaciones jugables.
- CAR-CORE-001 CUT A queda PROPOSED / NOT AUTHORIZED. CH_02 sigue bloqueado para integración jugable hasta cubrir sus dependencias globales en cortes posteriores autorizados.
- La verificación gráfica/manual de Godot no forma parte de este corte documental.

### Riesgos residuales y límites

La comparación de hashes y la copia no mantienen un bloqueo atómico contra una edición concurrente en Drive entre la comprobación y Robocopy. La sincronización reduce el riesgo de sobrescritura accidental, pero no garantiza exclusión mutua; detenerla si hay edición simultánea. El estado de sync y la referencia local `origin/main` no prueban por sí mismos el estado remoto en vivo.

Estado de publicación: sin push. Los commits de CAR-AUTO-001 permanecen locales hasta una autorización y operación de publicación separadas.
