# CAR-CORE-002 / R5B — Hall of Mists Vestibule (CH_ENTRY Safe Subgraph)

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-26
**Baseline de referencia:** `0a1f2de9d6757de4027bec90f94e04a34272ae12`
**Tipo:** Implementación de runtime, ampliación de subgrafo seguro, adaptación de pruebas y congelación contractual
**Corte anterior:** `CAR-CORE-002 / R5A-POST — Test Coverage & Structural Lighting Audit` (`0a1f2de9d6757de4027bec90f94e04a34272ae12`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R5C — Magic Transit & Word Connections` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Autorización y Alcance del Corte

Conforme a la autorización humana expresa, se implementó exclusivamente:

**`CAR-CORE-002 / R5B — Hall of Mists Vestibule (CH_ENTRY Safe Subgraph)`**

### Objetivos y Límites Contractuales
1. **Ampliación controlada del subgrafo de entrada:** Habilitación atómica en runtime de exactamente 6 ubicaciones adicionales pertenecientes a `CH_ENTRY`:
   - [`LOC_COBBLE`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L14) (*Crawlway* de guijarros, ordinaria, con luz natural permanente `LIT = true`).
   - [`LOC_DEBRIS`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L15) (*Debris room*, ordinaria, oscura).
   - [`LOC_AWKWARD`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L16) (*Awkward sloping canyon*, ordinaria, oscura).
   - [`LOC_BIRDCHAMBER`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L17) (*Bird chamber*, ordinaria, oscura).
   - [`LOC_PITTOP`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L18) (Cima del pozo de nieblas, ordinaria, oscura).
   - [`LOC_CRACK`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L19) (Grieta estrecha, forzada / transitoria, oscura, rebote inmediato a `LOC_PITTOP`).
2. **Total de ubicaciones en runtime:** Exactamente 41 ubicaciones habilitadas (34 de `CH_SURFACE` + 7 de `CH_ENTRY`, incluyendo `LOC_BELOWGRATE` de R5A).
3. **Catálogo estructural inerte:** Exactamente 144 ubicaciones históricas permanecen inactivas (`DISABLED`) en [`StructuralCatalog`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/structural_catalog.gd).
4. **Fronteras estrictas sin evasión:**
   - Hacia `LOC_MISTHALL`: bloqueada como frontera de capítulo (`world.ui("frontier")`).
   - Hacia `LOC_NECKBROKE` / descenso de `LOC_PITTOP`: interceptada de forma segura por [`DEPENDENCY_PENDING`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/game_state.gd#L20) al evaluar la condición sobre el lingote de oro (`NUGGET`), previniendo caídas a código no instanciado.
5. **Aislamiento de actores, puzles y objetos:** Cero actores enanos activos (enanos operan a partir de `LOC_MISTHALL` con `DEEP == true`), cero piratas, cero objetos mutables nuevos en runtime (exactamente 8 objetos funcionales preservados de `CH_01`), cero puzles posteriores activos (`BIRD`, `SNAKE`, `PLANT`, `TROLL`).
6. **Invarianza de datasets:**
   - [`chapter_01_surface.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/chapter_01_surface.json) (SHA-256 `afa33c8869ff32f91ebc569ff89f7f45a6dc724be3943343a41a4a15998f887b`).
   - [`structural_world.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/structural_world.json) (SHA-256 `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3`).

---

## 2. Modificaciones de Runtime en `WorldData`

En [`07_godot_open_adventure/godot/src/core/world_data.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd):

1. **Constante `AUTHORIZED_ADDITIONAL_LOCATIONS`:**
   ```gdscript
   const AUTHORIZED_ADDITIONAL_LOCATIONS: PackedStringArray = [
       "LOC_BELOWGRATE",
       "LOC_COBBLE",
       "LOC_DEBRIS",
       "LOC_AWKWARD",
       "LOC_BIRDCHAMBER",
       "LOC_PITTOP",
       "LOC_CRACK"
   ]
   ```
2. **Habilitación en `load_default()`:**
   ```gdscript
   for loc_id in AUTHORIZED_ADDITIONAL_LOCATIONS:
       world.enable_structural_location(loc_id)
   ```
3. **Manejo defensivo de descripciones nulas:** En `enable_structural_location`, se protegió la asignación de `description_en` y `short_en` ante salas que no poseen descripción corta en el dataset estructural (como `LOC_AWKWARD` o `LOC_CRACK`), evitando llamadas inválidas al constructor `String(null)` de GDScript:
   ```gdscript
   loc.description_en = String(data.get("long_description", "") if data.get("long_description") != null else "")
   loc.short_en = String(data.get("short_description", "") if data.get("short_description") != null else "")
   ```
4. **Resolución de destinos intra-corte:** Se ajustó la bandera `rule.target_in_chapter` para considerar destinos dentro del conjunto autorizado:
   ```gdscript
   rule.target_in_chapter = is_location_enabled(rule.target) or AUTHORIZED_ADDITIONAL_LOCATIONS.has(rule.target)
   ```

---

## 3. Semántica Histórica Verificada

1. **Iluminación natural en `LOC_COBBLE` vs Oscuridad en salas contiguas:**
   - Conforme a la reconciliación R5A-POST y a las banderas de Open Adventure 1.22 (`LIT = true`), `LOC_COBBLE` goza de visibilidad permanente proveniente de la boca de la cueva. El jugador puede examinarla y moverse sin linterna encendida.
   - Las 5 salas restantes (`LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`, `LOC_CRACK`) carecen de `LIT` (`LIT = false`). Entrar sin linterna encendida produce el estado de oscuridad `PITCH_DARK` sin muerte súbita inmediata (conforme a las reglas CUT C). Encender la linterna restaura la visibilidad normal y re-describe la sala.
2. **Comportamiento forzado de `LOC_CRACK` y semántica de `BACK`:**
   - Al entrar a `LOC_CRACK` mediante el comando `CRACK` desde `LOC_PITTOP`, el motor describe el texto narrativo histórico de la grieta (*"The crack is far too small for you to follow..."*) e inmediatamente ejecuta la transición forzada automática `HERE` devolviendo al jugador a `LOC_PITTOP` dentro del mismo turno de entrada (1 turno consumido en total).
   - En Open Adventure 1.22 C (`main.c:588-601`), el rebote forzado actualiza el historial estableciendo `oldloc = LOC_CRACK` y `oldlc2 = LOC_PITTOP`. Al solicitar `BACK`, al ser `oldloc` forzada se evalúa `motion = oldlc2` (`LOC_PITTOP`). Dado que `motion == game.loc`, el motor histórico emite `FORGOT_PATH` (*"Perdona, ya no me acuerdo de cómo se llegaba aquí."*) y rechaza el movimiento sin cambiar de sala. El regreso a `LOC_BIRDCHAMBER` se realiza mediante movimiento explícito al este (`EAST`).
3. **Conexión de la palabra mágica `PLUGH`:**
   - La sala `LOC_DEBRIS` incluye la regla de viaje histórica `PLUGH -> LOC_FOOF2`. Dado que `LOC_FOOF2` es una sala forzada de la superficie que transita hacia `LOC_BUILDING`, la habilitación de `LOC_DEBRIS` abre por primera vez la conectividad legítima hacia `LOC_FOOF2`, pasando el número de salas no alcanzables desde `LOC_START` de 3 a 2 (`LOC_FOOF4` y `LOC_LEDGE`).
4. **Frontera dependiente de lingote de oro (`NUGGET`):**
   - El pozo en `LOC_PITTOP` posee reglas condicionales hacia abajo (`LOC_NECKBROKE`) sujetas a si el jugador transporta o no el lingote de oro. Al no existir `NUGGET` en runtime, la consulta se suspende de forma segura mediante `DEPENDENCY_PENDING`, evitando desbordamientos o caídas del motor.

---

## 4. Batería de Pruebas Focales R5B (`test_hall_of_mists_vestibule.gd`)

Se implementó [`07_godot_open_adventure/godot/tests/test_hall_of_mists_vestibule.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_hall_of_mists_vestibule.gd) con 50 comprobaciones formales en 6 grupos:

1. **Habilitación y Catálogo (Checks 1–10):**
   - 41 ubicaciones habilitadas en runtime (`locations.size() == 41`, `get_enabled_location_ids().size() == 41`).
   - Verificación individual de presencia de las 6 salas nuevas.
   - Exactamente 144 ubicaciones inertes en `StructuralCatalog`.
   - Idempotencia de llamadas a `enable_structural_location`.
   - Rechazo explícito de salas no autorizadas (`LOC_MISTHALL`, `LOC_EASTBANK`) o inexistentes.
2. **Topología de Navegación y Atajos (Checks 11–28):**
   - Cadena canónica bidireccional completa: `LOC_GRATE <-> LOC_BELOWGRATE <-> LOC_COBBLE <-> LOC_DEBRIS <-> LOC_AWKWARD <-> LOC_BIRDCHAMBER <-> LOC_PITTOP`.
   - Atajos directos históricos: `LOC_BELOWGRATE -> PIT -> LOC_PITTOP`, `LOC_BELOWGRATE -> DEBRI -> LOC_DEBRIS`, `LOC_COBBLE -> PIT -> LOC_PITTOP`, `LOC_PITTOP -> DEPRE -> LOC_GRATE` (con reja abierta) y retorno a `LOC_BELOWGRATE` si la reja está cerrada.
   - Frontera fail-closed en `LOC_PITTOP -> DOWN` con `DEPENDENCY_PENDING` sobre `NUGGET`.
3. **Iluminación y Oscuridad CUT C (Checks 29–35):**
   - `LOC_COBBLE` conserva `LIT = true` y visibilidad sin lámpara.
   - Las otras 5 salas son oscuras (`LIT = false`).
   - Entrada sin lámpara produce `PITCH_DARK`.
   - Encender lámpara restaura visibilidad y narración.
   - Consumo de energía de linterna (1 punto por turno) en el subgrafo.
   - Apagar la lámpara produce oscuridad inmediata.
4. **Transición Forzada de `LOC_CRACK` (Checks 36–41):**
   - Definición forzada con destino `LOC_PITTOP`.
   - Narración del texto histórico de la grieta.
   - Rebote forzado automático a `LOC_PITTOP`.
   - Consumo estricto de exactamente 1 turno de entrada.
   - `BACK` tras el rebote emite `FORGOT_PATH` conforme a la semántica histórica de Open Adventure 1.22.
5. **Aislamiento y Contratos (Checks 42–47):**
   - Integridad de hashes SHA-256 de los datasets de superficie y estructural.
   - Cero actores enanos activos en runtime.
   - Cero actores piratas activos.
   - Cero objetos o puzles posteriores (`BIRD`, `SNAKE`, `PLANT`, `TROLL`).
   - Parser sin contaminación de estado ni objetos de capítulos posteriores.
   - Cero números pseudoaleatorios (RNG) consumidos por consultas estructurales.
6. **Recorrido Integrado Legítimo (Checks 48–50):**
   - Viaje completo sin intervención manual: `LOC_START -> BUILDING (coger llaves y lámpara, encender lámpara) -> OUT -> DEPRESSION -> UNLOCK GRATE -> ENTER (LOC_BELOWGRATE) -> WEST (LOC_COBBLE) -> WEST (LOC_DEBRIS) -> WEST (LOC_AWKWARD) -> WEST (LOC_BIRDCHAMBER) -> WEST (LOC_PITTOP) -> CRACK (rebota a LOC_PITTOP) -> DEPRE (LOC_GRATE) -> BUILDING -> LOC_BUILDING`.
   - Culminación exitosa en `LOC_BUILDING` con exactamente 17 turnos consumidos, 0 muertes, linterna encendida y energía debitada proporcionalmente.

---

## 5. Reconciliación de Suites Existentes

Se actualizaron las suites de pruebas existentes para reflejar la ampliación a 41 ubicaciones y 144 salas inactivas:
- [`run_tests.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/run_tests.gd): Conteo de salas actualizado a 41; `WEST` desde `LOC_BELOWGRATE` accede a `LOC_COBBLE` y regresa con `EAST`; conectividad desde `LOC_START` ajustada a 39 salas alcanzables (al abrirse `LOC_FOOF2` vía `PLUGH` en `LOC_DEBRIS`). 518 checks pasados.
- [`test_simulation_graph_isolation.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd): 41 salas jugables, 144 de simulación aisladas. 12 checks pasados.
- [`test_structural_projection_isolation.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_projection_isolation.gd): 41 salas jugables, 144 inertes aisladas. 23 checks pasados.
- [`test_structural_loader.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_loader.gd): 41 salas habilitadas, 144 deshabilitadas; sonda de sala inerte trasladada a `LOC_MISTHALL`. 37 checks pasados.
- [`test_structural_contract_freeze.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd): 41 salas habilitadas, 144 deshabilitadas; lista autorizada actualizada; sonda inerte en `LOC_MISTHALL`. 34 checks pasados.
- [`test_cave_mouth_pilot.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd): 41 salas habilitadas, 144 deshabilitadas; salida `WEST` desde `LOC_BELOWGRATE` navega a `LOC_COBBLE` y regresa a la reja. 51 checks pasados.
- [`test_travel_cycle.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_travel_cycle.gd): `WEST` desde `LOC_BELOWGRATE` arriba a `LOC_COBBLE` con `ARRIVED`. 55 checks pasados.
- [`verify.ps1`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/tools/verify.ps1): Incorporada la ejecución de `test_hall_of_mists_vestibule.gd`.

---

## 6. Resultados de Verificación Integral (`verify.ps1`)

Ejecución de los 7 bloques del pipeline unificado de verificación:

1. **Determinismo de exportación e inventario canónico:**
   - Cotejo de datasets deterministas: `PASS`.
   - `test_simulation_graph.py`: 10 tests pasados.
   - `test_canonical_inventory.py`: 26 tests pasados.
   - `test_structural_projection.py`: 34 tests pasados.
2. **Importación limpia en Godot 4.7.2:** `PASS`.
3. **Suites de motor Godot (Headless):**
   - `run_tests.gd`: `PASS — 518 checks`.
   - `test_simulation_graph_isolation.gd`: `PASS — 12 checks`.
   - `test_structural_projection_isolation.gd`: `PASS — 23 checks`.
   - `test_structural_loader.gd`: `PASS — 37 checks`.
   - `test_structural_contract_freeze.gd`: `PASS — 34 checks`.
   - `test_cave_mouth_pilot.gd`: `PASS — 51 checks`.
   - `test_hall_of_mists_vestibule.gd`: `PASS — 50 checks`.
   - `test_travel_cycle.gd`: `PASS — 55 checks`.
   - `test_darkness_lamp.gd`: `PASS — 61 checks`.
   - `test_death_reincarnation.gd`: `PASS — 34 checks`.
4. **Hoja de contactos de ilustraciones:** `PASS — 11 escenas`.
5. **Integración de ilustraciones en runtime:** `PASS — 62 checks`.
6. **Compilador de arte vectorial CH_01:** `PASS — 455 checks`.
7. **Variantes de arte de la reja:** `PASS — 150 checks`.

**Total checks unificados:** 1.552 checks ejecutados, 0 fallos.
**Veredicto unificado:** `ALL CHECKS PASSED`.

---

## 7. Inventario de Archivos del Corte

### Archivos Creados
- `07_godot_open_adventure/godot/tests/test_hall_of_mists_vestibule.gd`
- `07_godot_open_adventure/godot/tests/test_hall_of_mists_vestibule.gd.uid`
- `project_state/changes/car_core_002_r5b_hall_of_mists_vestibule/CHANGE.md`

### Archivos Modificados
- `07_godot_open_adventure/godot/src/core/world_data.gd`
- `07_godot_open_adventure/godot/tests/run_tests.gd`
- `07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd`
- `07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd`
- `07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd`
- `07_godot_open_adventure/godot/tests/test_structural_loader.gd`
- `07_godot_open_adventure/godot/tests/test_structural_projection_isolation.gd`
- `07_godot_open_adventure/godot/tests/test_travel_cycle.gd`
- `07_godot_open_adventure/tools/verify.ps1`
- `project_state/CURRENT_STATE.md`
