# AGENTS.md — Colossal Adventure: Reimagination

Esta entrada orienta el trabajo asistido en el repositorio público. Consulta primero [README.md](README.md), la tarea humana vigente y las reglas enlazadas desde [contracts/AGENTS.md](contracts/AGENTS.md). Carga únicamente el contrato del rol asignado; la presencia de varios contratos no activa agentes ni autoriza delegaciones.

El producto ejecutable es una aplicación independiente de Godot 4.7 situada en `07_godot_open_adventure/`. No es un plugin de editor. El YAML de Open Adventure es la autoridad de los datos históricos; los diagramas, informes, JSON exportado y la aplicación Godot son transformaciones o consumidores derivados con responsabilidades distintas.

Antes de modificar el proyecto Godot:

1. Revisa `07_godot_open_adventure/README.md` y `07_godot_open_adventure/PROVENANCE.md`.
2. Preserva parser, reglas de viaje, IDs estables, licencias y separación entre fuente y reinterpretación.
3. Ejecuta `07_godot_open_adventure/tools/verify.ps1` y registra los resultados reales.

No inventes conexiones, condiciones, textos históricos ni autorizaciones de redistribución. El material privado de referencia y las herramientas locales están excluidos deliberadamente del repositorio público. Una ausencia no debe reconstruirse desde documentación histórica sin una fuente autorizada.

El trabajo original se distribuye bajo GPL-3.0-or-later y los materiales de
Open Adventure conservan BSD-2-Clause. Steamworks permanece `PENDING / NOT
INTEGRATED`: no incorpores SDK, plugins, puentes, DRM ni dependencias de
servicios externos sin un corte y una revisión jurídica expresamente
autorizados. El juego debe seguir funcionando sin Steam.

Los documentos de `docs/` conservan evidencia histórica de la extracción de contratos. Sus rutas y estados antiguos no son instrucciones operativas actuales. `contracts/` contiene contratos documentales reutilizables; no constituye por sí solo un harness ejecutable.

Inspecciona Git y los archivos reales antes de escribir. Preserva ediciones humanas. Los commits, remotos y la publicación requieren autorización humana expresa.

## Project routing — Local workspaces

Los proyectos siguientes son independientes. Antes de ejecutar una tarea, identificar el proyecto solicitado y comprobar que existe su raíz local.

| Proyecto | Ruta local |
|---|---|
| Lands of Folklore | `C:\LoF-GIT` |
| Colossal Adventure: Reimagination | `C:\remake\Colossal-Adventure-Reimagination-public` |

### Reglas de enrutamiento

1. Seleccionar el repositorio según el proyecto indicado en la tarea, no según el directorio de trabajo inicial del agente.
2. Verificar que la ruta existe y corresponde al repositorio esperado.
3. Leer el `AGENTS.md` y los contratos aplicables del proyecto seleccionado antes de trabajar.
4. Ejecutar Git, pruebas y modificaciones únicamente dentro del repositorio autorizado.
5. No modificar archivos de otro proyecto ni trasladar cambios entre repositorios.
6. Si la ruta no existe, el repositorio no coincide o las instrucciones entran en conflicto, detenerse y solicitar aclaración.
7. Una ruta conocida no constituye autorización para realizar commits, push ni cambios fuera del alcance de la tarea.

### Colossal Adventure: Reimagination

Las tareas identificadas como `CAR-*`, incluida `CAR-QOL-001`, corresponden a:

`C:\remake\Colossal-Adventure-Reimagination-public`

No ejecutarlas desde `C:\LoF-GIT`.

## CAR — Local Commit & Drive Sync Policy

La autorización permanente del propietario registrada en `CAR-AUTO-001` se
aplica únicamente a este repositorio. Permite crear commits **locales** de los
archivos pertenecientes a un corte CAR expresamente autorizado, incluidos
informes de investigación completada aunque sus propuestas sigan pendientes,
y ejecutar la sincronización local → Drive después de cada commit correcto.
Esta regla concreta la aprobación humana exigida por los contratos compartidos;
no concede autoridad para iniciar un corte ni ampliar su alcance.

Usa `tools/finalize_cut.ps1` con `-CutId`, mensaje identificable y una lista
explícita `-Files`. El finalizador solo prepara esos archivos, rechaza un índice
previamente preparado o cambios ajenos, ejecuta las verificaciones aplicables,
crea como máximo un commit y sincroniza su snapshot versionado. Si un commit
ya existe y la sincronización falló, repetir la misma invocación reintenta la
sincronización sin duplicar el commit. `-DryRun` no prepara ni confirma cambios;
`-SkipSync` queda reservado al diagnóstico.

`sync_to_drive.ps1` solo copia archivos rastreados en el commit actual. No
sincroniza archivos no versionados, no elimina nada del destino y preserva
extras de Drive. Si una ruta de destino difiere tanto de su última huella
sincronizada como de una base Git reconocida, se detiene antes de sobrescribir.
Los conflictos deben revisarse manualmente; no se resuelven con espejo ni
force. El estado de huellas local vive bajo `.git` y no se publica.

La autorización permanente **no** incluye push, merge, tags, releases,
publicación, cierre `CLOSED / PASS` sin sus pruebas, commits de cambios humanos
ajenos, implementación de cortes solo propuestos, modificación de otros
repositorios ni eliminación de archivos de Drive. Nunca usar `git add .` ni
`git add -A` en este flujo. Los cambios fallidos o bloqueados se preservan para
revisión y no se convierten automáticamente en commits de implementación.
