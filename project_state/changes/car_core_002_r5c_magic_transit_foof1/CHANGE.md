# CAR-CORE-002 / R5C — Magic Transit & Word Connections (LOC_FOOF1)

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-26
**Baseline de referencia:** `c1f82bbbfcfa04e9bb8882c28323140a0ab3df5e`
**Tipo:** Implementación de runtime, habilitación de sala mágica forzada, batería de pruebas y congelación contractual
**Corte anterior:** `CAR-CORE-002 / R5B-POST — Test Coverage & Navigation Verification Audit` (`c1f82bbbfcfa04e9bb8882c28323140a0ab3df5e`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R6 — Visual Debug Graph in Godot (MapView)` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Autorización y Alcance del Corte

Conforme a la instrucción humana ("vamos con r5c pasamos test y continuamos en orden propuesto"), se autorizó e implementó exclusivamente:

**`CAR-CORE-002 / R5C — Magic Transit & Word Connections (LOC_FOOF1)`**

### Objetivos y Límites Contractuales
1. **Habilitación controlada de `LOC_FOOF1`:** Habilitación atómica en runtime de la ubicación especial de teletransporte `LOC_FOOF1` perteneciente a `CH_ENTRY`:
   - [`LOC_FOOF1`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L22): Sala especial forzada de llegada de teletransporte, con destino implícito incondicional hacia `LOC_DEBRIS` (`CH_ENTRY`).
2. **Cierre del bucle bidireccional `XYZZY`:**
   - Desde la casita (`LOC_BUILDING`): El comando `XYZZY` transporta al jugador a través de `LOC_FOOF1` (forzada) desembocando en `LOC_DEBRIS` en un único turno de entrada y narrando la transición *">>Foof!<<"*.
   - Desde la cueva (`LOC_DEBRIS`): El comando de retorno `XYZZY` transporta al jugador a través de `LOC_FOOF2` (forzada de superficie) devolviéndolo a `LOC_BUILDING` en un único turno de entrada.
3. **Total de ubicaciones en runtime:** Exactamente 42 ubicaciones habilitadas (34 de `CH_SURFACE` + 8 de `CH_ENTRY`, incluyendo las 7 de R5A/R5B + `LOC_FOOF1`).
4. **Catálogo estructural inerte:** Exactamente 143 ubicaciones históricas permanecen inactivas (`DISABLED`) en [`StructuralCatalog`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/structural_catalog.gd).
5. **Aislamiento estricto de otras salas mágicas:** Las salas mágicas no habilitadas (`LOC_FOOF3`, `LOC_FOOF4`, `LOC_FOOF5`, `LOC_FOOF6`) permanecen fuera de runtime. Por ejemplo, `PLUGH` desde `LOC_BUILDING` hacia `LOC_FOOF3` sigue interceptado limpiamente como frontera de capítulo (`world.ui("frontier")`).
6. **Invarianza de datasets:**
   - [`chapter_01_surface.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/chapter_01_surface.json) intacto.
   - [`structural_world.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/structural_world.json) intacto.

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
       "LOC_CRACK",
       "LOC_FOOF1"
   ]
   ```
2. **Carga e integración:** `LOC_FOOF1` se inicializa automáticamente en `load_default()` y sus reglas de viaje quedan resueltas dentro del conjunto de salas habilitadas.

---

## 3. Semántica de Teletransporte e Historial

1. **Resolución forzada en un turno:**
   - Al ejecutar `XYZZY` en `LOC_BUILDING`, el intérprete transita a `LOC_FOOF1`, describe su texto forzado histórico (*">>Foof!<<"*) y ejecuta de inmediato la regla incondicional implícita hacia `LOC_DEBRIS`.
   - Se consume exactamente 1 turno de entrada del jugador.
2. **Preservación del historial de salas (`previous_location` y `previous_previous_location`):**
   - El motor actualiza el historial en cascada (`_advance_history()`), dejando `previous_location = "LOC_FOOF1"` y `previous_previous_location = "LOC_BUILDING"`.

---

## 4. Batería de Pruebas Focales R5C (`test_magic_transit_foof1.gd`)

Se implementó [`07_godot_open_adventure/godot/tests/test_magic_transit_foof1.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_magic_transit_foof1.gd) con 20 comprobaciones formales:
- Verificación de catálogo estructural (185 ubicaciones) y presencia de `LOC_FOOF1`.
- Exactamente 42 ubicaciones habilitadas en runtime y 143 inertes.
- Idempotencia de llamadas a `enable_structural_location("LOC_FOOF1")`.
- Rechazo de otras salas mágicas (`LOC_FOOF3`, `LOC_FOOF5`).
- Teletransporte bidireccional completo `LOC_BUILDING <-> LOC_DEBRIS` vía `XYZZY`.
- Consumo exacto de turnos (1 por salto) y narración de la transición.
- Aislamiento de frontera para `PLUGH` hacia `LOC_FOOF3`.

---

## 5. Resultados de Verificación Global (`verify.ps1`)

La ejecución de [`07_godot_open_adventure/tools/verify.ps1`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/tools/verify.ps1) arroja:
- **Fase 1 (Export & Canonical):** 10 + 26 + 34 = 70 checks Python superados.
- **Fase 2 (Godot Import):** PASS.
- **Fase 3 (Engine Tests):**
  - `run_tests.gd`: 522 checks (+4 checks netos).
  - `test_simulation_graph_isolation.gd`: 12 checks.
  - `test_structural_projection_isolation.gd`: 23 checks.
  - `test_structural_loader.gd`: 37 checks.
  - `test_structural_contract_freeze.gd`: 34 checks.
  - `test_cave_mouth_pilot.gd`: 51 checks.
  - `test_hall_of_mists_vestibule.gd`: 50 checks.
  - `test_magic_transit_foof1.gd`: 20 checks (nueva suite focal R5C).
  - `test_travel_cycle.gd`: 55 checks.
  - `test_darkness_lamp.gd`: 61 checks.
  - `test_death_reincarnation.gd`: 34 checks.
  - **Total Fase 3:** 899 checks formales.
- **Fase 4 (Scenes):** 11 escenas capturadas.
- **Fase 5 (Runtime Art):** 62 checks.
- **Fase 6 (CH_01 Vector Art):** 455 checks.
- **Fase 7 (Grate Art):** 150 checks.
- **Métrica global:** **1.636 checks formales + 11 escenas visuales**, 0 fallos (`ALL CHECKS PASSED`).
