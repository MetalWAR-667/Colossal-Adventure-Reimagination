# CAR-CORE-001 / CUT A — Global Data Contract

**Estado:** `CLOSED / PASS`. Fecha: 2026-10-25.
Baseline observado: `f8796e603e779ca08895bb56864ca6506c311e07`, `main`,
índice y árbol inicialmente limpios. Autorización humana: CUT A únicamente.
Documento rector: [Decision Gate](../car_core_001_decision_gate/CHANGE.md).

## Contrato y procedencia

El exportador existente añade `simulation_graph` al mismo
`godot/data/chapter_01_surface.json`. Ambas proyecciones proceden del mismo IR
obtenido por `load_yaml_source()`, que conserva la comprobación estructural de
las dos copias del YAML. No hay una segunda carga de datos para construir el
grafo ni un catálogo manual de rutas.

Las claves jugables anteriores se conservan en la raíz, con su esquema v1.
No se envuelven en una nueva clave `playable_world`, porque eso exigiría cambiar
el consumidor. `WorldData.load_dataset()` sigue leyendo exclusivamente las
claves anteriores e ignora `simulation_graph`. Ningún runtime consume el nuevo
grafo; pertenecer a él no autoriza movimiento, descripciones ni nodos del mapa.

`simulation_graph` declara su propio `schema_version: 1` y contiene:

- `location_count: 185`, `travel_record_count: 623`.
- `locations`: array en orden YAML. Cada entrada tiene `id`, `source_index`
  (base cero), `source_conditions`, `flags` y `travel`.
- `flags`: conserva los flags fuente y explicita `DEEP`, `NOARRR` y `FORCED`.
  `FORCED` se deriva como en `init.c:initialise()` y
  `make_dungeon.py`: primer viaje con verbos vacíos, equivalente a HERE, y
  descripción larga no nula. Una cadena vacía sigue siendo no nula:
  `LOC_BUILDING1` también es forzada. Se obtienen 22 ubicaciones FORCED,
  144 DEEP y 18 NOARRR, sin ejecutar sus movimientos.
- `travel`: conserva orden y multiplicidad; índices locales `source_index`
  y globales `source_record_index`, `verbs`, `action_type`, `target`,
  `target_resolution`, `source_condition`, `condition` y `nodwarves`.
- `source_condition` conserva la lista YAML original o null. `condition`
  normaliza los predicados ordinarios (`always`, `pct`, `not_state`, `carry`,
  `with`). Para `nodwarves` es null: el marcador separado es true y no se
  convierte en un predicado ordinario del jugador. Existe una sola fila,
  `LOC_LONGWEST → LOC_DIFFERENT1`, con ese marcador.
- Destinos: 583 `goto` resueltos contra IDs globales, 34 `speak` contra IDs
  de mensajes fuente y seis `special` clasificados como `special_handler`.
  Los especiales mantienen sus números 1/2/3; no se convierten en ubicaciones.
- `dwarflocs`: `LOC_KINGHALL`, `LOC_WESTBANK`, `LOC_Y2`, `LOC_ALIKE3`,
  `LOC_COMPLEX`, `LOC_MAZEEND12`, en ese orden; el sexto es el pirata.

La exportación rechaza destinos o tipos desconocidos, referencias de objetos
inexistentes y una discrepancia en el inventario esperado. Los objetos usados
por condiciones siguen siendo referencias simbólicas: no se exporta ni activa
un catálogo mutable global. No se añaden descripciones ni vocabulario al grafo.
Los hashes fuente existentes se conservan en `meta.source_yaml`.

## Verificación ejecutada

Desde la raíz, con Godot `4.7.2.stable.official.ed1daf0bf`:

```powershell
python 07_godot_open_adventure/tools/oa_export_godot.py
python 07_godot_open_adventure/tools/test_simulation_graph.py
& ./tools/Godot_v4.7.2-stable_win64_console.exe --headless --path 07_godot_open_adventure/godot --script res://tests/test_simulation_graph_isolation.gd
& ./07_godot_open_adventure/tools/verify.ps1 -Godot "$PWD/tools/Godot_v4.7.2-stable_win64_console.exe"
```

- **10 tests Python PASS**: inventarios/IDs, todas las filas y su orden,
  condiciones, flags, seis posiciones, resolución de destinos, nodwarves,
  determinismo y rechazo de fixtures inválidos. Dos construcciones completas
  generan bytes canónicos idénticos; `--check` valida el archivo generado.
- Comparación con el dataset del baseline Git: todas las claves anteriores
  son iguales. Su serialización canónica, retirando solo `simulation_graph`,
  conserva SHA-256
  `a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f`.
  El test fija esa huella del contrato previo para detectar drift jugable.
- **12 checks Godot PASS**: se examinan los 151 IDs globales no jugables,
  comprobando ausencia en lookups, descripciones y mapa; solicitudes directas
  al límite de movimiento los rechazan. Una secuencia real de obtención de
  llaves, apertura y ENTER sigue detenida en LOC_GRATE. Las tablas del parser
  siguen procediendo exclusivamente del contrato jugable anterior.
- `verify.ps1`: **ALL CHECKS PASSED**. Exportación/importación PASS;
  **448 checks** del juego sin modificar, **62** de integración, **455** del
  lote artístico y **150** de GRATE. Hoja headless de once escenas generada.
  Los controles nuevos quedan integrados en las fases de datos y motor.
  No se suman estas aserciones como pruebas independientes.
- No se ejecutaron nuevas suites gráficas ni validación humana: no hay cambios
  de ilustraciones, interfaz o renderer. Las regresiones headless del arte son
  parte del verificador existente, no nueva aceptación visual.

## Inventario exacto

1. `07_godot_open_adventure/tools/oa_export_godot.py`
2. `07_godot_open_adventure/tools/test_simulation_graph.py`
3. `07_godot_open_adventure/tools/verify.ps1`
4. `07_godot_open_adventure/godot/data/chapter_01_surface.json` (regenerado)
5. `07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd`
6. `07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd.uid`
7. `project_state/CURRENT_STATE.md`
8. Este `CHANGE.md`.

## Límites y cierre

No se modifican YAML, fuentes históricas, intérprete, GameState, parser, reglas,
RNG, turnos, arte ni límites de capítulos. El grafo contiene filas YAML, no las
filas C expandidas por cada verbo. Su mayor tamaño añade lectura/parsing JSON;
no se ha realizado un benchmark nuevo ni se afirma coste cero.

**CUT B — PROPOSED / NOT AUTHORIZED.** CUT C–F tampoco están autorizados.
No se implementan actores, HERE automático, oscuridad, muerte ni CH_02.
El uso futuro de flags, RNG y estado global requiere sus propios cortes.

Finalización CAR-AUTO-001 con los ocho archivos explícitos, revisión del diff,
`git diff --check`, commit local y sincronización de hashes a Drive.
**NO PUSH.** Resultado Git/Drive entregado al finalizar; la sincronización no
ofrece bloqueo atómico ante ediciones simultáneas en Drive.
