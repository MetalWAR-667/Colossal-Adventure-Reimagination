# CAR-CORE-002 / R5A — Cave Mouth Pilot (LOC_BELOWGRATE)

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-26
**Baseline de referencia:** `d5f72679c512a903dee73d1e42bca735147aeb8d`
**Tipo:** Implementación de runtime, adaptación estructural aditiva, suite de pruebas focales y preservación contractual
**Corte anterior:** `CAR-CORE-002 / R5-PRE — Historical Travel Semantics Crosscheck` (`d5f72679c512a903dee73d1e42bca735147aeb8d`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R5B — Hall of Mists Vestibule (CH_ENTRY Safe Subgraph)` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Autorización y Objetivos del Corte

Conforme a la resolución del Decision Gate de navegación estructural (`CAR-CORE-002 / R5 — Structural Navigation Decision Gate`: `CLOSED / VIABLE WITH CONDITIONS`) y a la verificación formal del evaluador de viajes (`CAR-CORE-002 / R5-PRE`: `CLOSED / VERIFIED — R5A READY`), la autoridad humana autorizó exclusivamente:

**`CAR-CORE-002 / R5A — Cave Mouth Pilot (LOC_BELOWGRATE)`**

### Objetivos Alcanzados
1. **Habilitación atómica de [`LOC_BELOWGRATE`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L262):** Incorporación de la boca de la cueva directamente desde [`StructuralCatalog`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/structural_catalog.gd) en [`WorldData.load_default()`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L45-L55) mediante un adaptador seguro e idempotente.
2. **Cruce bidireccional de la reja:**
   - La reja cerrada (`GRATE_CLOSED`) bloquea el paso tanto desde la superficie (`LOC_GRATE`) como desde el interior de la cueva (`LOC_BELOWGRATE`), emitiendo el mensaje histórico `GRATE_NOWAY`.
   - Con la reja abierta (`GRATE_OPEN`), el jugador puede descender mediante `ENTER` o `DOWN`, y regresar a la superficie mediante `OUT`, `UP` o `BACK`.
3. **Frontera estricta hacia el interior:** Todas las salidas salientes desde `LOC_BELOWGRATE` hacia el interior de la cueva (`LOC_COBBLE`, `LOC_PITTOP`, `LOC_DEBRIS`) son interceptadas y bloqueadas de forma transparente como fronteras no habilitadas (`world.ui("frontier")`), garantizando que el jugador no pueda entrar prematuramente en salas no autorizadas.
4. **Fallback transparente de narrativa en inglés:** Al no existir traducción española de capítulos posteriores en `l10n_es.json`, el adaptador presenta de forma fiel las cadenas históricas en inglés (`long_description` y `short_description`) proyectadas en `structural_world.json`.
5. **Preservación total de CUT A–D y datasets:**
   - Cero modificaciones en [`chapter_01_surface.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/chapter_01_surface.json) (digest protegido `a49db669...`, SHA-256 `afa33c88...`).
   - Cero modificaciones en [`structural_world.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/structural_world.json) (SHA-256 `fda199af...`).
   - Cero alteraciones en la lógica del analizador sintáctico ([`CommandParser.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/command_parser.gd)) o del evaluador de viajes ([`Interpreter.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd)).
   - El conjunto habilitado pasa exactamente de 34 a 35 salas (34 de `CH_SURFACE` + 1 de `CH_ENTRY`). Exactamente 150 salas históricas permanecen inactivas (`DISABLED`) en el catálogo estructural.

---

## 2. Modificaciones de Runtime en `WorldData`

En [`07_godot_open_adventure/godot/src/core/world_data.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd):

1. **Constante de autorización estricta:**
   ```gdscript
   const AUTHORIZED_ADDITIONAL_LOCATIONS: PackedStringArray = [
       "LOC_BELOWGRATE"
   ]
   ```
2. **Método de habilitación [`enable_structural_location(location_id: String) -> bool`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L262):**
   - Comprueba pertenencia a `AUTHORIZED_ADDITIONAL_LOCATIONS`, emitiendo advertencia (`push_warning`) y rechazando cualquier sala no autorizada (fail-closed).
   - Comportamiento idempotente: si la sala ya está habilitada, devuelve `true` de inmediato sin recrear instancias.
   - Extrae la definición de la sala desde `StructuralCatalog` y crea una instancia de [`WorldLocation`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_location.gd).
   - Hereda `long_description` en `description_en` y `short_description` en `short_en`.
   - Propaga condiciones crudas (`raw_conditions`) y banderas históricas booleanas (`flags`), asegurando iluminación natural (`LIT = true`).
   - Resuelve los verbos de viaje mapeándolos contra la tabla de nombres canónicos de movimiento (`motion_verbs`).
   - Registra la sala en `locations[location_id]` y en `enabled_location_ids[location_id] = true`.
3. **Carga por defecto ampliada:**
   En `WorldData.load_default()` se invoca:
   ```gdscript
   world.enable_structural_location("LOC_BELOWGRATE")
   ```
4. **Fallback robusto de descripciones:**
   [`describe()`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L328) y [`describe_short()`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L338) devuelven `loc.description_en` y `loc.short_en` respectivamente cuando no existe traducción localizada en español, preservando compatibilidad con fixtures de prueba.

---

## 3. Batería de Pruebas Focales R5A (`test_cave_mouth_pilot.gd`)

Se implementó [`07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd), que cubre 51 aserciones organizadas en 5 áreas funcionales:

1. **Habilitación y Catálogo (Checks 1–9):**
   - Total de 35 ubicaciones habilitadas en runtime (`locations.size() == 35` y `get_enabled_location_ids().size() == 35`).
   - Cobertura estricta de las 34 salas de `CH_SURFACE` más `LOC_BELOWGRATE` (perteneciente a `CH_ENTRY`).
   - Exactamente 150 salas históricas permanecen inactivas en el catálogo de solo lectura.
   - Idempotencia de `enable_structural_location("LOC_BELOWGRATE")`.
   - Rechazo explícito de salas no autorizadas (`LOC_COBBLE`) o inexistentes.
2. **Navegación y Frontera de la Reja (Checks 10–20):**
   - Reja cerrada bloquea el descenso con mensaje `GRATE_NOWAY`.
   - Reja abierta permite el descenso por `ENTER` o `DOWN`.
   - Descripciones históricas en inglés de `LOC_BELOWGRATE` visibles y fidedignas (larga: *steel grate*, corta: *below the grate*).
   - Regreso exitoso desde `LOC_BELOWGRATE` hacia `LOC_GRATE` por `OUT` y `UP` con la reja abierta.
   - Regreso bloqueado si la reja está cerrada desde el interior.
   - `BACK` desde `LOC_BELOWGRATE` regresa fielmente a `LOC_GRATE`.
   - Salidas hacia el interior (`WEST`, `PIT`, `DEBRI`) interceptadas como fronteras no habilitadas.
   - Determinismo estricto de giros e invariancia ante comandos repetidos.
3. **Aislamiento de Mecánicas y Objetos (Checks 21–30):**
   - Preservación del catálogo funcional de 8 objetos de CH_01 sin filtraciones.
   - Sin inventario inicial espurio en `LOC_BELOWGRATE`.
   - Consultas y habilitación no consumen números de RNG.
   - Cero actores enanos activos (`world.objects.has("DWARF") == false`).
   - Cero puzles de capítulos posteriores (`TROLL`, `SNAKE`, `PLANT`).
   - Integridad del ciclo de linterna CUT C (energía 330, estado oscuro).
   - Preservación de iluminación natural (`LIT = true`) en `LOC_BELOWGRATE`.
   - Integridad del subsistema de muertes y obituarios CUT D.
   - Preservación del subsistema de arte vectorial de CH_01.
4. **Contratos e Inmutabilidad (Checks 31–36):**
   - SHA-256 de `chapter_01_surface.json` (`afa33c88...`) intacto.
   - SHA-256 de `structural_world.json` (`fda199af...`) intacto.
   - Determinismo del catálogo estructural (185 salas).
   - Copias defensivas profundas previenen mutaciones del catálogo estructural.
   - Comportamiento fail-closed ante solicitudes inválidas.
5. **Recorrido Integrado Legítimo:**
   - Simulación de partida real: inicio en `LOC_START` → recoger llaves en `LOC_BUILDING` → caminar a `LOC_GRATE` → probar entrar bloqueado → abrir reja con llaves (`UNLOCK GRATE`) → descender a `LOC_BELOWGRATE` → observar descripciones corta y larga (`LOOK`) → probar avanzar a `WEST` (bloqueado como frontera) → regresar con `BACK` a la superficie → re-descender con `DOWN` → salir finalmente con `OUT`.

Resultado de ejecución:
```text
PASS: 51 CAR-CORE-002 / R5A checks completed with 0 failures
```

---

## 4. Evolución de Suites de Aislamiento y Regresión

Las suites de regresión existentes se actualizaron para reflejar formalmente la expansión controlada de 34 a 35 ubicaciones funcionales:

- [`07_godot_open_adventure/godot/tests/run_tests.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/run_tests.gd):
  - Actualizado conteo de ubicaciones a 35.
  - Regla de validación de viajes ampliada para aceptar destinos conocidos en `has_structural_location`.
  - Prueba de desbloqueo de la reja actualizada: `ENTER` desciende a `LOC_BELOWGRATE`, `WEST` choca con la frontera y `OUT` regresa a `LOC_GRATE`.
  - 459 checks pasados.
- [`07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd):
  - 35 salas jugables, 150 salas de simulación examinadas y aisladas.
  - 12 checks pasados.
- [`07_godot_open_adventure/godot/tests/test_structural_projection_isolation.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_projection_isolation.gd):
  - 35 salas jugables, 150 salas inertes examinadas y aisladas.
  - 23 checks pasados.
- [`07_godot_open_adventure/godot/tests/test_structural_loader.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_loader.gd):
  - 35 salas habilitadas (`CH_SURFACE` + `LOC_BELOWGRATE`), 150 deshabilitadas.
  - Verificación de consulta inerte desplazada a `LOC_COBBLE`.
  - 37 checks pasados.
- [`07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd):
  - 35 salas habilitadas, 150 deshabilitadas.
  - Bucle de juego adaptado al descenso a `LOC_BELOWGRATE`.
  - Blindaje contra habilitación accidental probado sobre `LOC_COBBLE`.
  - 34 checks pasados.
- [`07_godot_open_adventure/godot/tests/test_travel_cycle.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_travel_cycle.gd):
  - Descenso a `LOC_BELOWGRATE` tras abrir reja verificado con `ARRIVED`.
  - Nueva frontera verificada en `LOC_COBBLE` ante comando `WEST` desde `LOC_BELOWGRATE`.
  - 55 checks pasados.
- [`07_godot_open_adventure/tools/verify.ps1`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/tools/verify.ps1):
  - Registrado e integrado el paso de ejecución headless de `test_cave_mouth_pilot.gd`.

---

## 5. Verificación Integral (`verify.ps1`)

Ejecución completa de los 7 bloques del pipeline de verificación unificada:

1. **Fase 1 — Determinismo de exportación e inventario canónico:**
   - Regeneración y cotejo de datasets: `PASS`.
   - `test_simulation_graph.py`: 10/10 tests pasados.
   - `test_canonical_inventory.py`: 26/26 tests pasados.
   - `test_structural_projection.py`: 34/34 tests pasados.
2. **Fase 2 — Importación limpia en Godot 4.7.2:** `PASS`.
3. **Fase 3 — Suites del motor Godot (Headless):**
   - `run_tests.gd`: `PASS — 459 checks`.
   - `test_simulation_graph_isolation.gd`: `PASS — 12 checks (150 inertes)`.
   - `test_structural_projection_isolation.gd`: `PASS — 23 checks (150 inertes)`.
   - `test_structural_loader.gd`: `PASS — 37 checks`.
   - `test_structural_contract_freeze.gd`: `PASS — 34 checks`.
   - `test_cave_mouth_pilot.gd`: `PASS — 51 checks`.
   - `test_travel_cycle.gd`: `PASS — 55 checks`.
   - `test_darkness_lamp.gd`: `PASS — 61 checks`.
   - `test_death_reincarnation.gd`: `PASS — 34 checks`.
4. **Fase 4 — Hoja de contactos vectorial:** 10 escenas capturadas limpiamente.
5. **Fase 5 — Regresiones de ilustraciones en runtime:** `PASS — 36 checks`.
6. **Fase 6 — Compilador de arte vectorial:** `PASS — 19 tests`.
7. **Fase 7 — Variantes de reja:** `PASS — 10 tests`.

**Veredicto unificado:** `ALL CHECKS PASSED`.

---

## 6. Inventario de Archivos del Corte

### Archivo Creado
- `07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd`
- `07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd.uid`
- `project_state/changes/car_core_002_r5a_cave_mouth_pilot/CHANGE.md`

### Archivos Modificados
- `07_godot_open_adventure/godot/src/core/world_data.gd`
- `07_godot_open_adventure/godot/tests/run_tests.gd`
- `07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd`
- `07_godot_open_adventure/godot/tests/test_structural_projection_isolation.gd`
- `07_godot_open_adventure/godot/tests/test_structural_loader.gd`
- `07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd`
- `07_godot_open_adventure/godot/tests/test_travel_cycle.gd`
- `07_godot_open_adventure/tools/verify.ps1`
- `project_state/CURRENT_STATE.md`
