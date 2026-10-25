# CAR-CORE-002 / R2 — Complete Structural Data Projection

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-25
**Baseline inspeccionado:** `868cc6b868c8edbe06a3335cb5f46e4146993c83`
**Tipo:** Proyección estructural global, tooling de exportación, suite de pruebas automatizadas y documentación
**Corte anterior:** `CAR-CORE-002 / R1 — Canonical Room Inventory` (`868cc6b868c8edbe06a3335cb5f46e4146993c83`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R3 — Structural Loader & Enabled View` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Autorización Humana

Conforme al Decision Gate cerrado el 25 de octubre de 2026 (`project_state/changes/car_core_002_complete_room_reconstruction_decision_gate/CHANGE.md`) en estado `CLOSED / VIABLE WITH CONDITIONS` y al cierre satisfactorio de R1 (`project_state/changes/car_core_002_r1_canonical_room_inventory/CHANGE.md`), la autoridad humana autorizó exclusivamente la ejecución del corte:

**CAR-CORE-002 / R2 — Complete Structural Data Projection**

Alcance estricto autorizado:
- Creación de una proyección estructural global completa, versionada, inerte y determinista a partir de los datos canónicos de R1 y las fuentes históricas.
- Emisión del artefacto estructurado consumible por una futura ampliación de `WorldData` en R3.
- Tooling de regeneración y verificación estricta (`--check`).
- Pruebas focales automatizadas que validan las 28 aserciones de consistencia, integridad, inercia y regresión.
- Pruebas headless de aislamiento en Godot que garantizan que el límite jugable actual permanece inalterado.
- **Límites inviolables:** No habilitar habitaciones ni capítulos en runtime (CH_02 permanece inactivo). No modificar los scripts de runtime del juego (`WorldData.gd`, `GameState.gd`, `Interpreter.gd`, `CommandParser.gd`). No alterar el contrato jugable existente de CH_01 (`chapter_01_surface.json`). No simular actores (enanos ni pirata). No evaluar condiciones pendientes ni consumir RNG. No implementar R3 ni R4. No realizar push al repositorio remoto.

---

## 2. Decisión de Diseño Arquitectónico (Opción 3)

El dataset de Capítulo 01 (`07_godot_open_adventure/godot/data/chapter_01_surface.json`) está fuertemente protegido por las pruebas contractuales de CUT A (`test_simulation_graph.py`), las cuales exigen un digest SHA-256 exacto pre-corte (`a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f`) sobre todas las claves ajenas a `simulation_graph` y `historical_runtime`, y por pruebas de aislamiento en Godot (`test_simulation_graph_isolation.gd`) que rechazan narrativas en dicho archivo.

Para cumplir simultáneamente con la preservación estricta de CUT A–D y dotar al proyecto de la proyección estructural completa de las 185 ubicaciones históricas con descripciones completas, draw.io y viajes:
- Se adoptó la **Opción 3**: la emisión de un artefacto independiente y versionado:
  `07_godot_open_adventure/godot/data/structural_world.json`.
- `oa_export_godot.py` genera y verifica deterministamente tanto `chapter_01_surface.json` (manteniendo intacto su hash contractual) como `structural_world.json`.
- `res://data/structural_world.json` queda inmediatamente preparado en la ruta de recursos de Godot para ser cargado por el futuro loader modular de R3 (`WorldData`), sin romper ni modificar ningún consumidor existente.

---

## 3. Fuentes de Autoridad Reutilizadas

La proyección estructural no inventa datos; es una transformación determinista que integra:

1. **Datos históricos:** `06_reconstruccion_drawio/Open_Adventure.yaml` (SHA-256: `4ee2c6451a64591bacfcec890efa60e15324411897cce894a79eff01cdf35747`).
2. **Partición editorial de capítulos:** `06_reconstruccion_drawio/tools/oa_chapters.py` (definición canónica de 11 capítulos).
3. **Geometría y diagrama:** `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio` (SHA-256: `a67521fd3d8addd04deda504926c715f5db0395c8adbb0414951f048199370e2`).
4. **Inventario Canónico de R1:** Artefactos versionados en `07_godot_open_adventure/canonical_inventory/` (`manifest.json`, `locations.json`, `travel.json`, `objects.json`, `chapters.json`, `structural_dependencies.json`).

---

## 4. Estructura de `structural_world.json`

El documento emitido es un JSON determinista (claves ordenadas, sangrado de 2 espacios, terminación `\n`) con las siguientes claves raíz:

- **`meta`:**
  - `schema_version`: 1
  - `cut_id`: `"CAR-CORE-002-R2"`
  - `projection_type`: `"complete_historical_structural_world"`
  - `document_status`: `"INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE"`
  - `generator`: `"07_godot_open_adventure/tools/oa_export_godot.py"`
  - `canonical_inventory_source`: `"07_godot_open_adventure/canonical_inventory/manifest.json"`
  - `runtime_boundary`: Cláusula contractual declarando la inercia del archivo en R2.
  - `sources`: Hashes y rutas relativas de YAML y draw.io.
  - `counts`: Resumen completo de conteos canónicos.
- **`all_chapter_ids`:** Lista de los 11 IDs de capítulo en orden canónico.
- **`chapters`:** Lista de 11 objetos de capítulo con metadatos, páginas draw.io y listas de miembros.
- **`chapters_by_id`:** Diccionario `id -> capítulo` para acceso O(1).
- **`all_location_ids`:** Lista de los 185 IDs de ubicación en orden histórico de origen (0..184).
- **`locations`:** Lista de 185 objetos de ubicación en orden de origen. Cada ubicación incluye su rol estructural, banderas, descripciones completa y corta, coordenadas draw.io y su lista ordenada de reglas de salida `travel`.
- **`locations_by_id`:** Diccionario `id -> ubicación` para acceso O(1).
- **`travel`:** Lista global de 623 registros de viajes en estricto orden de precedencia original, con destinos tipados (`goto`, `speak`, `special`), condiciones y parámetros normalizados.
- **`all_object_ids`:** Lista de los 70 IDs de objetos en orden histórico de origen (0..69).
- **`objects`:** Lista de 70 objetos (incluyendo el centinela `NO_OBJECT` en índice 0).
- **`objects_by_id`:** Diccionario `id -> objeto` para acceso O(1).
- **`dwarflocs`:** Lista canónica de 6 salas de inicio de enanos (`LOC_KINGHALL`, `LOC_WESTBANK`, `LOC_Y2`, `LOC_ALIKE3`, `LOC_COMPLEX`, `LOC_MAZEEND12`).
- **`structural_dependencies`:** Matriz de dependencias estáticas derivada en R1.

---

## 5. Conteos y Estadísticas Verificadas

| Elemento | Total verificado | Estado de validación |
|---|---:|---|
| Ubicaciones históricas | 185 | EXACT MATCH |
| Registros de viaje | 623 | EXACT MATCH |
| Entradas de objetos | 70 | EXACT MATCH |
| Capítulos editoriales | 11 | EXACT MATCH |
| Posiciones de inicio de enanos (`dwarflocs`) | 6 | EXACT MATCH |
| Objetos portátiles | 36 | EXACT MATCH |
| Objetos inmóviles | 33 | EXACT MATCH |
| Centinela `NO_OBJECT` | 1 | EXACT MATCH |
| Objetos con colocación múltiple | 11 | EXACT MATCH |
| Objetos con varios estados | 26 | EXACT MATCH |
| Objetos inicialmente ausentes / NOWHERE | 18 | EXACT MATCH |
| Tesoros | 20 | EXACT MATCH |
| Cruces de viaje entre capítulos | 85 | EXACT MATCH |
| Ubicaciones forzadas (`is_forced`) | 22 | EXACT MATCH |
| Ubicaciones letales (`is_lethal`) | 4 | EXACT MATCH |

---

## 6. Archivos Creados y Modificados

### Archivos Creados
1. `07_godot_open_adventure/godot/data/structural_world.json` (2.211.261 bytes)
   - SHA-256: `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3`
2. `07_godot_open_adventure/tools/test_structural_projection.py` (17.580 bytes)
   - 34 pruebas automatizadas (28 focales y 6 negativas).
3. `07_godot_open_adventure/godot/tests/test_structural_projection_isolation.gd` (3.750 bytes)
   - 23 aserciones de aislamiento headless en Godot 4.7.2.
4. `project_state/changes/car_core_002_r2_complete_structural_data_projection/CHANGE.md`
   - Registro oficial del corte.

### Archivos Modificados
1. `07_godot_open_adventure/tools/oa_export_godot.py`
   - Implementación de `build_structural_projection()`, `validate_structural()`, `dump_structural()` y soporte dual en `main()` (generación y `--check` de ambos archivos).
2. `07_godot_open_adventure/tools/verify.ps1`
   - Inclusión de `test_structural_projection.py` en fase 1/7 y `test_structural_projection_isolation.gd` en fase 3/7.
3. `project_state/CURRENT_STATE.md`
   - Actualización del estado a `CLOSED / PASS` para R2 y propuesta de R3.

---

## 7. Resultados de Verificación

Se ejecutó la suite completa `tools/verify.ps1`, arrojando `ALL CHECKS PASSED`:

1. **Fase 1/7: Export determinism & canonical inventory:**
   - `oa_export_godot.py --check`: `chapter_01_surface.json` y `structural_world.json` coinciden byte a byte con la salida regenerada.
   - `test_simulation_graph.py`: 10 pruebas `PASS` (hash contractual `a49db669...` intacto).
   - `oa_canonical_inventory.py --check`: todos los artefactos canónicos coinciden.
   - `test_canonical_inventory.py`: 26 pruebas `PASS`.
   - `test_structural_projection.py`: 34 pruebas `PASS` en 1.44s.
2. **Fase 2/7: Godot import:** `PASS`.
3. **Fase 3/7: Engine tests:**
   - `run_tests.gd`: 448 checks `PASS`.
   - `test_simulation_graph_isolation.gd`: 12 CUT A isolation checks `PASS`.
   - `test_structural_projection_isolation.gd`: 23 R2 isolation checks `PASS` (151 ubicaciones inertes examinadas y excluidas).
   - `test_travel_cycle.gd`: 54 CUT B travel checks `PASS`.
   - `test_darkness_lamp.gd`: 61 CUT C darkness/lamp checks `PASS`.
   - `test_death_reincarnation.gd`: 34 CUT D death/reincarnation checks `PASS`.
4. **Fase 4/7: Illustration sheet:** 11 escenas renderizadas en `res://captures/scenes.png`.
5. **Fase 5/7: Runtime illustration integration:** 62 checks `PASS`.
6. **Fase 6/7: CH_01 vector art:** 9 dibujos deterministas, 455 checks `PASS`.
7. **Fase 7/7: GRATE state art:** 2 variantes deterministas, 150 checks `PASS`.

---

## 8. Protected Boundaries y Preservación de Límites

- **Inercia total en runtime:** Ninguna de las 151 nuevas ubicaciones fuera de CH_01 está habilitada en runtime. `WorldData.locations` mantiene exactamente 34 salas.
- **Scripts de runtime intactos:** `WorldData.gd`, `GameState.gd`, `Interpreter.gd` y `CommandParser.gd` no sufrieron modificación alguna.
- **Consumo de RNG nulo:** 0 llamadas a generadores pseudoaleatorios durante la exportación o validación estructural.
- **Actores no simulados:** Enanos y pirata se mantienen como datos estáticos inertes.
- **Cero push:** El trabajo permanece exclusivamente en commits locales y sincronización Drive bajo `CAR-AUTO-001`.

---

## 9. Próximo Corte Propuesto

**CAR-CORE-002 / R3 — Structural Loader & Enabled View**
*Estado:* `PROPOSED / NOT AUTHORIZED`
*Objetivo:* Diseñar un cargador desacoplado en Godot que pueda instanciar estructuras de datos a partir de `res://data/structural_world.json` manteniendo una "vista habilitada" que restrinja el espacio jugable a los capítulos explícitamente autorizados (actualmente CH_01), sin romper las interfaces existentes de `WorldData`.
