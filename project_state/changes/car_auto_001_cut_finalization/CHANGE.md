# CAR-AUTO-001 — Automated Cut Finalization & Drive Synchronization

Estado: **IMPLEMENTADO / VERIFICACIÓN EN CURSO**
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

Un estado de sincronización local bajo `.git/car_drive_sync_state.json` recuerda la huella anterior. Si aún no existe, el primer sync permite sobrescribir contenido solo cuando los archivos divergentes coinciden, todos, con un mismo ancestro Git reconocido (hasta 100 commits); si no puede demostrar una base común, se detiene. Tras un sync correcto, el estado local se actualiza; no se añade al repositorio ni a Drive.

## Recuperación y límites

- **Índice contaminado / cambio inesperado:** detenerse; revisar manualmente Git. La herramienta no limpia staging ni descarta archivos.
- **Verificación fallida:** no se crea commit; preservar y diagnosticar el fallo dentro del corte.
- **Commit correcto, sync fallido:** conservar el commit y repetir la misma llamada; no usar amend ni crear commit vacío.
- **Diferencia en Drive no reconocida:** no sobrescribir. Comparar el archivo con el commit/base identificados y decidir manualmente qué contenido conservar antes de reintentar.
- **Drive ausente, archivo sensible o ruta/reparse point:** detenerse antes de copiar.
- **Dry run:** no modifica el índice ni los archivos de Drive; la ejecución normal de sync después de un commit es la que comprueba escritura real.

La comparación de destino reduce el riesgo de sobrescribir ediciones directas, pero no proporciona bloqueo atómico frente a una edición simultánea entre la comprobación y Robocopy. Para una garantía estricta durante edición concurrente, se debe detener la sincronización y acordar un mecanismo de bloqueo antes de continuar.

## Evidencia y estado previo

Preflight CAR observado en `main`: HEAD `b5623864d11e0081096df5e4a61900a5ef4bc4a6`; árbol e índice limpios; upstream configurado `origin/main` y referencia local alineada. No se hizo fetch, por lo que esa referencia no se presenta como consulta remota en vivo. Drive existe; antes de este corte, los 665 archivos rastreados coincidían por SHA-256 con sus destinos. El destino también contiene elementos no rastreados por Git, que el nuevo procedimiento preserva.

`project_state/CURRENT_STATE.md` todavía identifica `0484104` como estado observado. No se actualiza en este corte porque el alcance documental autorizado incluye este CHANGE y `AGENTS.md`; se registra aquí como discrepancia pendiente de reconciliación.

Las pruebas realizadas, commit local y resultado de la primera sincronización real se informan al cerrar la ejecución de CAR-AUTO-001. No se atribuye a este documento una validación que todavía no se haya ejecutado.
