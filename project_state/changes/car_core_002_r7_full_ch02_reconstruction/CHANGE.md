# CHANGE: CAR-CORE-002 / R7 — Full CH_02 Hall of Mists Reconstruction

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-26
**Proyecto:** Colossal Adventure: Reimagination
**Motor:** Godot 4.7.2

---

## 1. Contexto y Objetivos

Con el cierre de R5A (`LOC_BELOWGRATE`), R5B (Vestíbulo de 6 salas), R5C (`LOC_FOOF1`) y R6 (`MapView` multi-capítulo), el subgrafo seguro de entrada a la caverna estaba habilitado e inspeccionable. No obstante, las 4 salas nucleares de `CH_ENTRY` que culminan el Capítulo 02 permanecían deshabilitadas:
- `LOC_MISTHALL` (Gran Sala de la Niebla)
- `LOC_NUGGET` (Sala de la Pepita de Oro)
- `LOC_EASTBANK` (Orilla Este de la Fisura)
- `LOC_WESTBANK` (Orilla Oeste de la Fisura)

El objetivo de R7 ha sido:
1. Habilitar de forma canónica las 4 salas restantes desde `StructuralCatalog` en `WorldData`, completando íntegramente las **12 ubicaciones de CH_ENTRY** (46 ubicaciones habilitadas en total: 34 CH_SURFACE + 12 CH_ENTRY).
2. Resolver el ciclo histórico de navegación bidireccional en el Hall of Mists y la fisura sin romper las restricciones de aislamiento de actores/enanos (CUT E).
3. Habilitar el seguimiento de estado para las condiciones de viaje históricas de `NUGGET` y `FISSURE` en `GameState`, permitiendo que el evaluador `_select_from()` en `Interpreter` distinga entre objetos pendientes no instanciados y estados históricos de objetos de cueva (`UNBRIDGED` / `BRIDGED`).
4. Mantener estrictamente el aislamiento fail-closed de las fronteras hacia capítulos no autorizados:
   - `LOC_KINGHALL` (CH_CENTRAL / CH_03)
   - `LOC_DOME` y `LOC_NOMAKE` (CH_SPECIAL)
   - `LOC_JUMBLE` (CH_Y2_WINDOWS)
   - `LOC_PARALLEL1` y `LOC_MISTWEST` (CH_MAZE_ALIKE)
5. Preservar intactos los 8 objetos funcionales de `CH_01` y los 34 nodos / 118 aristas de `CH_SURFACE`.

---

## 2. Modificaciones realizadas

- **`07_godot_open_adventure/godot/src/core/world_data.gd`**:
  - `AUTHORIZED_ADDITIONAL_LOCATIONS` ampliado con `LOC_MISTHALL`, `LOC_NUGGET`, `LOC_EASTBANK`, `LOC_WESTBANK`.
- **`07_godot_open_adventure/godot/src/core/game_state.gd`**:
  - Incorporado el seguimiento inicial de estado de objetos para condiciones de cueva (`NUGGET` en `LOC_NUGGET`, `FISSURE` en `LOC_EASTBANK` con estado `UNBRIDGED`).
- **`07_godot_open_adventure/godot/src/core/interpreter.gd`**:
  - `_select_from`: comprueba `state.object_place.has(candidate.cond_object)` además de `world.objects.has()`. Si el objeto tiene estado tracked en la partida, evalúa la condición normalmente; si no está tracked ni instanciado, preserva el fail-closed como `DEPENDENCY_PENDING`.
- **Suites de Pruebas**:
  - Creado `test_full_ch02_reconstruction.gd` con 31 comprobaciones de habilitación, navegación, condiciones de fisura/pepita y aislamiento de fronteras.
  - Actualizados recuentos de aislamiento en `test_cave_mouth_pilot.gd`, `test_hall_of_mists_vestibule.gd`, `test_magic_transit_foof1.gd`, `test_simulation_graph_isolation.gd`, `test_structural_contract_freeze.gd`, `test_structural_loader.gd`, `test_structural_projection_isolation.gd` y `run_tests.gd` reflejando 46 ubicaciones habilitadas y 139 deshabilitadas.
  - Integrado en `verify.ps1`.

---

## 3. Resultados de Verificación

- Determinismo de exportación: `PASS`.
- Verificación de inventario canónico: `PASS` (26 tests).
- Verificación negativa estructural: `PASS` (8 tests).
- Pruebas de motor (Fase 3):
  - `run_tests.gd`: `PASS` (554 checks).
  - `test_full_ch02_reconstruction.gd`: `PASS` (31 checks).
  - Suites R1–R6: `PASS`.
- Total de comprobaciones: **1.689 checks + 11 escenas visuales**, 0 fallos.
