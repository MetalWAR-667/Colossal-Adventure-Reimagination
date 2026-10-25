# CAR-CORE-002 / R1 — Canonical Room Inventory Report

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-25
**Corte:** `CAR-CORE-002 / R1 — Canonical Room Inventory`
**Rama:** `main`
**Baseline:** `1886fdcc87911d1252cb75bccfaa2c971939f672`

---

## 1. Resumen Ejecutivo y Autorización

El 25 de octubre de 2026 se cerró el Decision Gate de reconstrucción completa de salas (`project_state/changes/car_core_002_complete_room_reconstruction_decision_gate/CHANGE.md`) en estado `CLOSED / VIABLE WITH CONDITIONS`. La autorización humana expresa para esta fase autorizó exclusivamente **R1 — Canonical Room Inventory**, prohibiendo la habilitación jugable de nuevas salas, puzles, actores o mecánicas (R2, R3 y R4 permanecen no autorizados).

R1 establece una referencia estructural única, determinista y auditable generada directamente desde las tres fuentes de autoridad del repositorio, sin introducir un segundo origen de verdad ni modificar el runtime de Godot:

- **YAML histórico:** `06_reconstruccion_drawio/Open_Adventure.yaml` (autoridad de datos históricos).
- **Asignación editorial de capítulos:** `06_reconstruccion_drawio/tools/oa_chapters.py` (partición humana navegable en 11 capítulos).
- **Geometría y diagrama:** `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio` (185 nodos estructurados en 11 páginas).

---

## 2. Conteos Canónicos Verificados

Todos los conteos verificados por el Decision Gate han sido reproducidos y contrastados de forma automatizada por el validador:

| Elemento | Total verificado | Estado de aserción |
|---|---:|---|
| Ubicaciones históricas | 185 | EXACT MATCH |
| Registros de viaje (travel rules) | 623 | EXACT MATCH |
| Entradas de objetos | 70 | EXACT MATCH |
| Capítulos editoriales | 11 | EXACT MATCH |
| Objetos portátiles | 36 | EXACT MATCH |
| Objetos inmóviles | 33 | EXACT MATCH |
| Centinela `NO_OBJECT` | 1 | EXACT MATCH |
| Objetos con colocación múltiple | 11 | EXACT MATCH |
| Objetos con varios estados | 26 | EXACT MATCH |
| Objetos inicialmente ausentes / NOWHERE | 18 | EXACT MATCH |
| Tesoros | 20 | EXACT MATCH |
| Cruces de viaje entre capítulos | 85 | EXACT MATCH |
| Ubicaciones con movimiento forzado (`is_forced`) | 22 | EXACT MATCH |

---

## 3. Asignación y Cobertura de Capítulos Canónicos

Las 185 ubicaciones históricas se encuentran asignadas con 100% de cobertura, exactamente una vez por ubicación, con cero duplicados y cero asignaciones por fallback:

| Capítulo ID | Título editorial | Salas | Cobertura | Fallback |
|---|---|---:|---|---|
| `CH_SURFACE` | 01 — Surface World | 34 | 100% | 0 |
| `CH_ENTRY` | 02 — Cave Entry | 12 | 100% | 0 |
| `CH_CENTRAL` | 03 — Hall of Mountain King & Twopit | 18 | 100% | 0 |
| `CH_MAZE_ALIKE` | 04 — Maze (All Alike) | 33 | 100% | 0 |
| `CH_BEDQUILT` | 05 — Bedquilt & Secret Canyons | 17 | 100% | 0 |
| `CH_ORIENTAL_PLOVER` | 06 — Oriental Room & Plover Passage | 12 | 100% | 0 |
| `CH_RESERVOIR` | 07 — Reservoir & Cliff Ascent | 12 | 100% | 0 |
| `CH_REPOSITORY` | 08 — Repository & Volcano | 13 | 100% | 0 |
| `CH_WITT_DIFFERENT` | 09 — Witt's End & Maze All-Different | 18 | 100% | 0 |
| `CH_Y2_WINDOWS` | 10 — Y2, Windows & Dusty Room | 9 | 100% | 0 |
| `CH_SPECIAL` | 11 — Special & Transient States | 7 | 100% | 0 |
| **Total** | **11 capítulos** | **185** | **100%** | **0** |

`CH_SPECIAL` se conserva como una agrupación editorial de estados especiales, pseudo-salas de muerte y ubicación nula, no como una región jugable ordinaria.

---

## 4. Clasificación Estructural de Ubicaciones

Cada una de las 185 ubicaciones se clasifica explícitamente en una función estructural primaria, complementada con indicadores booleanos unívocos:

| Rol estructural | Cantidad | Descripción histórica y miembros representativos |
|---|---:|---|
| `ordinary` (jugable) | 162 | Habitaciones explorables con órdenes normales del jugador. |
| `special` | 13 | Destinos especiales: 6 teletransportes mágicos (`LOC_FOOF1`..`LOC_FOOF6`), 6 bloqueos o transitorios con mensaje (`LOC_DOME`, `LOC_SNAKEBLOCK`, `LOC_BUILDING1`, `LOC_NOCLIMB`, `LOC_PLANTTOP`, `LOC_BADDIRECTION`) y 1 retorno especial (`LOC_SEWER`). |
| `transient` | 5 | Salas de transición forzada inmediata vía cascada `goto` con verbos vacíos: `LOC_CRACK`, `LOC_CLIMBSTALK`, `LOC_PARALLEL1`, `LOC_PARALLEL2`, `LOC_CLIFFTOP`. |
| `lethal` | 4 | Salas de muerte histórica por caída o trampa: `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_GRUESOME`, `LOC_FOOTSLIP`. |
| `null` | 1 | Centinela nulo `LOC_NOWHERE` (índice 0, sin descripciones larga ni corta). |
| **Total** | **185** | |

### Casos especiales verificados
- `LOC_NOWHERE`: índice 0; `is_null = true`; sin descripciones (`long_description = null`, `short_description = null`); `maptag = "Nowhere"`.
- `LOC_BUILDING1`: índice 60; `is_forced = true`; conserva fielmente su descripción larga vacía de la fuente (`long_description = ""`), con `maptag = "Middle of plant."`.
- Ubicaciones forzadas (`is_forced = true`): exactamente 22 ubicaciones derivadas según la regla canónica de `init.c` (`source_index != 0`, `description.long is not None`, y regla inicial de viajes con `verbs == []`).

### Banderas históricas verificadas
- `DEEP`: 144 ubicaciones
- `NOBACK`: 50 ubicaciones
- `LIT`: 37 ubicaciones
- `ALLALIKE`: 27 ubicaciones
- `FOREST`: 22 ubicaciones
- `NOARRR`: 18 ubicaciones
- `ALLDIFFERENT`: 12 ubicaciones
- `ABOVE`: 11 ubicaciones
- `FLUID`: 10 ubicaciones
- `OILY`: 1 ubicación

---

## 5. Manifiesto de Viajes y Reglas de Movimiento

Se preservan los 623 registros de viaje en estricto orden de precedencia original:

### Tipos de destino (`action_type`)
- `goto`: 583 registros (resolución tipada: `location`; todos apuntan a ubicaciones válidas).
- `speak`: 34 registros (resolución tipada: `message`; todos apuntan a mensajes de `arbitrary_messages`).
- `special`: 6 registros (resolución tipada: `special_handler`; manejadores 1, 2 y 3).

### Tipos de condición (`condition_type`)
- `always`: 574 registros (incondicionales).
- `not`: 25 registros (verifican estado no igual a un valor de objeto).
- `pct`: 12 registros (probabilísticos, requieren RNG de simulación).
- `carry`: 7 registros (requieren portar el objeto indicado).
- `with`: 4 registros (requieren presencia del objeto en la habitación o inventario).
- `nodwarves`: 1 registro (predicado de bloqueo para actores enanos en `LOC_LONGWEST` -> `LOC_DIFFERENT1`).
- **Total:** 623 registros.

### Cruces entre capítulos
85 registros de viaje `goto` cruzan de un capítulo editorial a otro. Todos ellos quedan catalogados en la matriz de dependencias con su origen, destino, capítulos involucrados, verbos y condiciones originales.

---

## 6. Catálogo Estático de Objetos

Se inventarían las 70 entradas de objetos preservando su identidad histórica y propiedades estáticas:

- **Centinela:** `NO_OBJECT` (índice 0; `is_sentinel = true`; sin vocabulario ni descripción).
- **Portabilidad:** 36 objetos portátiles (`immovable = false`), 33 objetos inmóviles (`immovable = true`).
- **Tesoros:** exactamente 20 objetos identificados con bandera `treasure = true`.
- **Colocación múltiple:** 11 objetos que poseen más de una ubicación inicial (`GRATE`, `STEPS`, `FISSURE`, `MIRROR`, `DRAGON`, `CHASM`, `TROLL`, `TROLL2`, `BEAR`, `RESER`, `PLANT2`).
- **Varios estados declarados:** 26 objetos poseen más de un estado funcional (`LAMP`, `GRATE`, `STEPS`, `BIRD`, `DOOR`, `SNAKE`, `FISSURE`, `BOTTLE`, `MIRROR`, `PLANT`, `AXE`, `DRAGON`, `CHASM`, `TROLL`, `BEAR`, `VEND`, `BATTERY`, `URN`, `CAVITY`, `RESER`, `SIGN`, `EGGS`, `VASE`, `RUG`, `CHAIN`, `AMBER`).
- **Inicialmente ausentes / NOWHERE:** 18 objetos que comienzan sin sala asignada o en `LOC_NOWHERE`.
- **Referencias en viajes condicionados:** 16 objetos son requeridos en condiciones de viaje (`CHASM`, `CLAM`, `DOOR`, `DRAGON`, `EMERALD`, `FISSURE`, `GRATE`, `NUGGET`, `OGRE`, `OYSTER`, `PLANT`, `RABBITFOOT`, `RESER`, `SNAKE`, `TROLL`, `VEND`).

---

## 7. Correspondencia con Open_Adventure_World_V3.drawio

Se validó contra `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio`:
- 12 diagramas en total: 1 página índice (`INDEX`) y 11 páginas de capítulos (`CH_SURFACE` a `CH_SPECIAL`).
- Los 185 identificadores `source_id` están presentes en elementos `object`.
- Cero identificadores desconocidos, cero duplicados en el diagrama.
- Cada ubicación se encuentra exactamente en la página correspondiente a su capítulo editorial.
- Se extrajeron con precisión las coordenadas (`x`, `y`), dimensiones (`width`, `height`), ID de celda (`cell_id`) y etiqueta HTML para cada ubicación.

---

## 8. Artefactos Versionados Producidos

Bajo `07_godot_open_adventure/canonical_inventory/`:

1. `manifest.json`: Metadatos, hashes SHA-256 de fuentes, conteos canónicos y sumas de verificación.
2. `locations.json`: Inventario de 185 ubicaciones con roles, flags, descripciones y geometría.
3. `travel.json`: 623 registros de viajes ordenados con destinos tipados, condiciones y dependencias.
4. `objects.json`: Catálogo de 70 objetos con portabilidad, colocaciones, estados y referencias.
5. `chapters.json`: 11 capítulos editoriales con metadatos y listado de miembros.
6. `structural_dependencies.json`: Matriz de cruces, dependencias de objetos, destinos especiales y dependencias pendientes.

Informes documentales bajo `07_godot_open_adventure/reports/`:
- `CANONICAL_ROOM_INVENTORY_REPORT.md`: Este informe de validación.
- `STRUCTURAL_DEPENDENCY_MATRIX.md`: Matriz estructural de dependencias.

---

## 9. Pruebas y Validación de No Regresión

### Pruebas focales y negativas
La suite `07_godot_open_adventure/tools/test_canonical_inventory.py` ejecuta 26 pruebas (20 aserciones focales del pliego + 6 pruebas negativas sobre fixtures aislados):
- Resultado: **26 tests PASS, 0 failures, 0 errors**.

### Comprobador determinista
`python 07_godot_open_adventure/tools/oa_canonical_inventory.py --check`:
- Compara los artefactos en disco contra los generados en memoria byte a byte.
- Resultado: **PASS: all canonical inventory artifacts match regenerated authoritative source data**.

### Flujo de verificación integral
Ejecución de `07_godot_open_adventure/tools/verify.ps1` con Godot 4.7.2:
- Export determinism & canonical inventory: PASS (10 Python + oa_canonical_inventory check + 26 Python canonical tests)
- Godot import: PASS
- Engine tests: 448 checks PASS
- CUT A isolation: 12 checks PASS
- CUT B travel: 54 checks PASS
- CUT C darkness/lamp: 61 checks PASS
- CUT D death/reincarnation: 34 checks PASS
- Illustration contact sheet: 11 scenes PASS
- Runtime illustration integration (CAR-ART-003): 62 checks PASS
- CH_01 vector art batch (CAR-ART-004): 455 checks PASS
- GRATE state art (CAR-ART-005): 150 checks PASS
- Resultado global: **ALL CHECKS PASSED**.
