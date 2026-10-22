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
