# CAR-CORE-002 / R3 — Structural Loader & Enabled View

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-25
**Baseline inspeccionado:** `c18d26c3dd49af77594feaece8f358f4b7b81cd8`
**Tipo:** Cargador estructural en Godot, vista habilitada, suite de pruebas automatizadas y documentación
**Corte anterior:** `CAR-CORE-002 / R2 — Complete Structural Data Projection` (`c18d26c3dd49af77594feaece8f358f4b7b81cd8`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R4 — Structural Validation & Contract Freeze` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Autorización Humana

Conforme al cierre de R2 (`project_state/changes/car_core_002_r2_complete_structural_data_projection/CHANGE.md`), la autoridad humana autorizó exclusivamente la ejecución del corte:

**CAR-CORE-002 / R3 — Structural Loader & Enabled View**

Alcance estricto autorizado:
- Implementación de un cargador estructural desacoplado (`StructuralCatalog`) capaz de leer y validar `res://data/structural_world.json`.
- Exposición controlada del catálogo estructural histórico mediante consultas defensivas de solo lectura.
- Separación explícita e inequívoca entre el catálogo estructural global (`STRUCTURAL / LOADED`) y el conjunto de ubicaciones habilitadas (`FUNCTIONAL / ENABLED`).
- Preservación íntegra de la vista funcional de Capítulo 01 en `WorldData.locations` (34 salas) y `WorldData.objects` (8 objetos).
- Suite focal de pruebas en Godot que cubre 37 comprobaciones (las 35 requeridas más aserciones complementarias de robustez y negación).
- **Límites inviolables:** No habilitar CH_02 ni salas adicionales en runtime. No modificar `GameState.gd`, `Interpreter.gd` ni `CommandParser.gd`. No ampliar el vocabulario del parser. No instanciar actores (enanos ni pirata). No evaluar condiciones pendientes ni consumir RNG. No alterar los hashes contractuales de `chapter_01_surface.json` ni de `structural_world.json`. No implementar R4. No realizar push al repositorio remoto.

---

## 2. Arquitectura Seleccionada

Para evitar transformar `WorldData` en una clase monolítica con responsabilidades de deserialización global y mantener desacoplados el catálogo de consulta y el estado jugable:

1. **`StructuralCatalog` (`07_godot_open_adventure/godot/src/core/structural_catalog.gd`):**
   - Clase independiente `RefCounted` dedicada a la lectura, deserialización y validación segura de `res://data/structural_world.json`.
   - Valida estrictamente el esquema (`schema_version == 1`), metadatos (`cut_id == "CAR-CORE-002-R2"`, `document_status == "INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE"`), claves requeridas, recuentos exactos (185 salas, 623 viajes, 70 objetos, 11 capítulos, 6 dwarflocs) y consistencia referencial (destinos `goto` existentes, centinela `NO_OBJECT` en índice 0).
   - Ofrece consultas de solo lectura con copias defensivas profundas (`duplicate(true)`), impidiendo que cualquier consumidor externo mute el catálogo canónico interno.
   - En caso de fallo o datos inválidos, limpia completamente sus almacenes internos y expone un mensaje de diagnóstico descriptivo vía `get_last_error()`.

2. **Integración Aditiva en `WorldData` (`07_godot_open_adventure/godot/src/core/world_data.gd`):**
   - Incorpora `var structural_catalog: StructuralCatalog = null`.
   - Incorpora `var enabled_location_ids: Dictionary = {}`, poblado de forma determinista y exclusiva con las 34 salas de CH_01 al cargar el dataset jugable.
   - Proporciona métodos delegados de consulta (`is_location_enabled()`, `is_location_structural()`, `has_structural_location()`, `get_structural_location()`, `get_structural_travel_records()`, `get_structural_object()`, `get_structural_chapter()`, `get_structural_location_ids()`, `get_enabled_location_ids()`, `get_structural_dwarflocs()`, `get_structural_dependencies()`, `get_structural_meta()`, `get_structural_counts()`).
   - `WorldData.locations` continúa ofreciendo únicamente las 34 salas jugables de CH_01.
   - `WorldData.objects` continúa ofreciendo únicamente los 8 objetos jugables de CH_01.
   - `is_in_chapter(location_id)` conserva exactamente su comportamiento previo (`locations.has(location_id)`).

3. **Inercia en Runtime:**
   - `GameState.gd`, `Interpreter.gd` y `CommandParser.gd` permanecieron completamente intactos.

---

## 3. Distinción Contractual: LOADED vs. ENABLED

El corte formaliza la distinción entre:

| Concepto | Ámbito | Elementos | Estado en Runtime |
|---|---|---:|---|
| `STRUCTURAL / LOADED` | Catálogo global inerte | 185 ubicaciones, 623 viajes, 70 objetos, 11 capítulos | Consultable como datos de referencia; no jugable |
| `FUNCTIONAL / ENABLED` | Runtime jugable activo | 34 ubicaciones (`CH_SURFACE`), 8 objetos funcionales | Activo en `WorldData.locations`, `Interpreter` y `GameState` |
| `STRUCTURAL / DISABLED` | Salas globales fuera de CH_01 | 151 ubicaciones (CH_02 a CH_11) | `structural_exists = true`, `enabled = false`; bloqueadas como frontera |

---

## 4. Archivos Creados y Modificados

### Archivos Creados
1. `07_godot_open_adventure/godot/src/core/structural_catalog.gd` (13.780 bytes)
   - Clase de carga, validación e indexación del catálogo histórico global.
2. `07_godot_open_adventure/godot/src/core/structural_catalog.gd.uid` (uid registrado por Godot 4.7.2).
3. `07_godot_open_adventure/godot/tests/test_structural_loader.gd` (12.450 bytes)
   - Suite de 37 aserciones Godot cubriendo carga estructural, vista habilitada, aislamiento funcional y pruebas negativas con fixtures.
4. `07_godot_open_adventure/godot/tests/test_structural_loader.gd.uid` (uid registrado por Godot 4.7.2).
5. `project_state/changes/car_core_002_r3_structural_loader_enabled_view/CHANGE.md`
   - Registro oficial del corte.

### Archivos Modificados
1. `07_godot_open_adventure/godot/src/core/world_data.gd`
   - Incorporación aditiva de `structural_catalog`, `enabled_location_ids`, carga en `load_default()` y métodos de consulta estructural.
2. `07_godot_open_adventure/tools/verify.ps1`
   - Integración de `test_structural_loader.gd` en la fase 3/7 de pruebas de motor.
3. `project_state/CURRENT_STATE.md`
   - Actualización del estado general del proyecto a `CLOSED / PASS` para R3 y propuesta de R4.

---

## 5. Pruebas Focales y Cobertura (37 Checks)

La suite `test_structural_loader.gd` verificó con 0 fallos:

- **Carga estructural (Checks 1–12):**
  - Existencia y lectura de `structural_world.json`.
  - Esquema versión 1 y cut_id `CAR-CORE-002-R2`.
  - 185 ubicaciones, 623 viajes, 70 objetos, 11 capítulos y 6 posiciones de inicio de enanos.
  - Orden histórico global de viajes (0..622) y orden de reglas salientes por sala.
  - Condiciones declaradas históricas (574 always, 25 not, 12 pct, 7 carry, 4 with, 1 nodwarves).
  - Descripciones y flags históricos (`LOC_NOWHERE` null, `LOC_BUILDING1` cadena vacía, `DEEP`, `LIT`).
  - Geometría draw.io completa (`cell_id`, `page_id`, dimensiones positivas).
  - Integridad referencial de viajes a destinos `goto`.

- **Vista habilitada (Checks 13–20):**
  - Exactamente 34 ubicaciones habilitadas en `get_enabled_location_ids()`.
  - Las 34 pertenecen estrictamente a `CH_SURFACE`.
  - Las 151 restantes satisfacen `not is_location_enabled()`.
  - Salas no habilitadas (`LOC_BELOWGRATE`) son consultables estructuralmente pero no jugables (`location() == null`).
  - `WorldData.locations` conserva exactamente 34 salas.
  - `WorldData.objects` conserva exactamente 8 objetos.
  - `is_in_chapter()` conserva estricta equivalencia funcional.

- **Aislamiento funcional (Checks 21–30):**
  - El parser no registra objetos de otros capítulos (`CHEST`, `DRAGON`).
  - El mapa jugable conserva exactamente 34 nodos y 118 aristas.
  - El intérprete rechaza el movimiento a salas no habilitadas y genera estado `FRONTIER`.
  - No existen actores ni simulación de enanos en `GameState`.
  - Las condiciones estructurales se mantienen como datos inertes no evaluados.
  - Las consultas estructurales consumen 0 números pseudoaleatorios (estado de `rng` idéntico).
  - Las consultas estructurales no alteran el estado mutable de la partida (`current_location`, `turn`, `object_place`).
  - No se duplican objetos mutables en runtime.
  - El ciclo de turnos e inputs funciona idénticamente.
  - Reglas de energía de lámpara, oscuridad y ciclo de muerte permanecen intactas.

- **Robustez y pruebas negativas (Checks 31–35):**
  - Rechazo explícito y diagnóstico ante JSON sintácticamente corrupto.
  - Rechazo explícito ante identificadores de sala duplicados en fixtures.
  - Rechazo explícito ante referencias de viaje a salas inexistentes.
  - Rechazo explícito ante versión de esquema incompatible (`schema_version: 999`).
  - Aislamiento e inmutabilidad garantizados por copias defensivas (mutar el diccionario devuelto no afecta al catálogo interno).

---

## 6. Equivalencia Funcional y Hashes Relevantes

- **Digest de Capítulo 01 (playable contract):**
  `a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f` (INTACTO)
- **SHA-256 de `structural_world.json`:**
  `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3` (INTACTO)

---

## 7. Resultados de Regresión Integral (`verify.ps1`)

Se ejecutó la suite completa `verify.ps1` con Godot 4.7.2 headless arrojando `ALL CHECKS PASSED`:
1. Fase 1/7: Export determinism, CUT A (10 pruebas), inventario canónico R1 (26 pruebas) y proyección estructural R2 (34 pruebas) `PASS`.
2. Fase 2/7: Godot headless import `PASS`.
3. Fase 3/7: Engine suite (448 checks), CUT A isolation (12 checks), R2 structural isolation (23 checks), R3 structural loader (37 checks), CUT B travel cycle (54 checks), CUT C darkness/lamp (61 checks), CUT D death/reincarnation (34 checks) `PASS`.
4. Fase 4/7: Illustration sheet (11 escenas) `PASS`.
5. Fase 5/7: Runtime illustration integration (62 checks) `PASS`.
6. Fase 6/7: CH_01 vector art (455 checks) `PASS`.
7. Fase 7/7: GRATE state art (150 checks) `PASS`.

---

## 8. Siguiente Corte Propuesto

**CAR-CORE-002 / R4 — Structural Validation & Contract Freeze**
*Estado:* `PROPOSED / NOT AUTHORIZED`
*Objetivo:* Consolidar y congelar los contratos estructurales y de aislamiento antes de iniciar la reconstrucción funcional por capítulos, asegurando que las especificaciones de datos, el cargador y los límites jugables queden formalmente sellados.
