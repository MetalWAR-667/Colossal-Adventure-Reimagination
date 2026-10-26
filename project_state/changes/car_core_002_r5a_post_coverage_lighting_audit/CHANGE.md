# CAR-CORE-002 / R5A-POST — Test Coverage & Structural Lighting Audit

**Estado:** `CLOSED / VERIFIED / RECONCILED`
**Fecha:** 2026-10-26
**Baseline de referencia:** `fb5b0adb3f0ecbec3a2aa30c655a6d336e89c659`
**Tipo:** Auditoría técnica focalizada post-implementación y reconciliación documental reproducible
**Corte auditado:** [`CAR-CORE-002 / R5A — Cave Mouth Pilot (LOC_BELOWGRATE)`](file:///C:/remake/Colossal-Adventure-Reimagination-public/project_state/changes/car_core_002_r5a_cave_mouth_pilot/CHANGE.md) (`98de5f7bccfb6439af096db90fe2ba046a591145`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R5B — Hall of Mists Vestibule (CH_ENTRY Safe Subgraph)` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Resumen Ejecutivo y Objeto de la Auditoría

Tras el cierre de `CAR-CORE-002 / R5A — Cave Mouth Pilot`, se abrió esta auditoría focalizada con los siguientes objetivos:

1. **Reconciliación métrica y de cobertura:** Investigar y clarificar la discrepancia aparente entre las métricas históricas de verificación y las reportadas en el documento de cierre de R5A (10 vs. 11 escenas, 36 vs. 62 checks de UI, 19 vs. 455 checks de arte vectorial CH_01, 10 vs. 150 checks de variantes de reja, y 448 → 459 checks del motor).
2. **Integridad del harness de pruebas:** Determinar si [`07_godot_open_adventure/tools/verify.ps1`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/tools/verify.ps1) sufrió alguna omisión, eliminación o reducción de aserciones.
3. **Auditoría de iluminación histórica (`LIT`) y aislamiento:** Confirmar la procedencia histórica de la condición `LIT` en [`LOC_BELOWGRATE`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L40) respecto a Open Adventure 1.22 y descartar cualquier filtración de luz artificial en estancias oscuras.
4. **Verificación de frontera y autorización:** Auditar el mecanismo de habilitación de [`WorldData.enable_structural_location`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L262) y la seguridad de las fronteras hacia el interior de la cueva.
5. **Evaluación de viabilidad para R5B:** Establecer si el runtime y el harness se encuentran en estado seguro y verificado para autorizar el siguiente corte.

### Conclusión Principal
**No hubo regresión real, ni pérdida de cobertura, ni relajación de pruebas en R5A.** La discrepancia numérica obedeció exclusivamente a un error de transcripción documental en el apartado 5 del informe de cierre de R5A, donde se anotaron manualmente métricas resumidas en lugar de los registros reales emitidos por las herramientas. La suite completa ejecutó y superó **1503 checks** en el conjunto global de pruebas (+63 checks netos en el motor Godot de Fase 3 respecto al baseline de R4) y **11 escenas capturadas**, con 0 fallos.

---

## 2. Auditoría del Harness de Pruebas (`verify.ps1`)

El análisis de diferencias con Git entre el baseline previo (`d5f72679c512a903dee73d1e42bca735147aeb8d`) y el cierre de R5A (`98de5f7bccfb6439af096db90fe2ba046a591145`) sobre [`07_godot_open_adventure/tools/verify.ps1`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/tools/verify.ps1) arroja:

```diff
@@ -98,6 +98,7 @@ try {
     & $Godot --headless --path $project --script res://tests/test_structural_loader.gd
     & $Godot --headless --path $project --script res://tests/test_structural_projection_isolation.gd
     & $Godot --headless --path $project --script res://tests/test_structural_contract_freeze.gd
+    & $Godot --headless --path $project --script res://tests/test_cave_mouth_pilot.gd
     & $Godot --headless --path $project --script res://tests/test_travel_cycle.gd
     & $Godot --headless --path $project --script res://tests/test_darkness_lamp.gd
     & $Godot --headless --path $project --script res://tests/test_death_reincarnation.gd
```

### Hallazgos del Harness:
- **0 pruebas eliminadas:** Ningún script ni fase fue removido o comentado.
- **1 prueba agregada:** Se incorporó formalmente [`07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_cave_mouth_pilot.gd) (51 checks).
- **Todas las fases se ejecutan íntegramente:** Las 7 fases del script `verify.ps1` operan sin modificaciones estructurales.

---

## 3. Reconciliación Métrica Detallada

La siguiente matriz contrasta los valores históricos antes de R5A, el texto erróneo redactado en la documentación de R5A, la salida real ejecutada por las herramientas y la causa técnica de cada variación:

| Fase / Componente | Pre-R5A (Real) | Documentado en R5A | Ejecución Real en R5A | Clasificación | Diagnóstico y Causa Raíz |
|---|---|---|---|---|---|
| **Fase 3: Engine headless (`run_tests.gd`)** | 448 checks | 459 checks | 459 checks | `JUSTIFIED_EVOLUTION` | Aumento legítimo de +11 checks al evaluar las 4 nuevas reglas de viaje de `LOC_BELOWGRATE`, la nueva aserción del piloto de reja (+2) y bucles exhaustivos de alcance (+5). |
| **Fase 3: Batería piloto (`test_cave_mouth_pilot.gd`)** | 0 checks | 51 checks | 51 checks | `JUSTIFIED_EVOLUTION` | Suite nueva creada en R5A. Registró exactamente 51 aserciones reales ejecutadas en runtime (`PASS: 51 checks`). |
| **Fase 3: Ciclo de viajes (`test_travel_cycle.gd`)** | 54 checks | 55 checks | 55 checks | `JUSTIFIED_EVOLUTION` | Aumento legítimo de +1 check al comprobar la nueva frontera en `LOC_COBBLE` ante `WEST` desde `LOC_BELOWGRATE` (`turn == 11` y `pending_location == "LOC_COBBLE"`). |
| **Fase 4: Hoja de contactos (`capture_scenes.gd`)** | 11 escenas | 10 escenas | 11 escenas | `REPORTING_DIFFERENCE` | Error de transcripción humana en `CHANGE.md`. El script generó y emitió `11 scenes` en `res://captures/scenes.png` (9 vectoriales de CH_01 + 2 variantes de GRATE). |
| **Fase 5: Ilustraciones runtime (`test_runtime_illustration.gd`)** | 62 checks | 36 checks | 62 checks | `REPORTING_DIFFERENCE` | Error de transcripción humana en `CHANGE.md`. El script headless ejecutó y emitió `CAR-ART-003: 62 checks, 0 failures` (sin la bandera opcional `--output` que añade 9 capturas visuales para un total de 71). |
| **Fase 6: Arte vectorial CH_01 (`build_ch01_vector_art.py` + `test_ch01_vector_art.gd`)** | 455 checks | 19 tests | 455 checks | `REPORTING_DIFFERENCE` | Confusión de métricas en la redacción de `CHANGE.md`: se confundieron los 19 tests unitarios de Python de Fase 2 (`test_structural_projection.py`) con la fase de arte vectorial, la cual corrió sus 455 checks completos sin alteración. |
| **Fase 7: Variantes de reja (`build_grate_variants.py` + `test_grate_state_art.gd`)** | 150 checks | 10 tests | 150 checks | `REPORTING_DIFFERENCE` | Confusión de métricas en la redacción de `CHANGE.md`: se copiaron los 10 tests unitarios de Python de Fase 1 (`test_simulation_graph.py`) en lugar de los 150 checks de Godot para las variantes de reja. |

### Desglose del incremento neto en el motor Godot (Fase 3: 703 → 766 checks, +63 checks):
1. **+51 checks en `test_cave_mouth_pilot.gd`:** Suite de integración nueva con 51 aserciones focales.
2. **+11 checks en `run_tests.gd`:**
   - +4 checks en `_test_dataset` por destinos estructurales de `LOC_BELOWGRATE` (`LOC_GRATE`, `LOC_COBBLE`, `LOC_PITTOP`, `LOC_DEBRIS`).
   - +2 checks en `_test_grate_and_keys` por el descenso a `LOC_BELOWGRATE`, rechazo de `WEST` y retorno con `OUT`.
   - +1 check en `_test_deterministic_reproducibility` por `_get_exits_for("LOC_BELOWGRATE")`.
   - +4 checks en comprobaciones exhaustivas de conectividad y grafos para la nueva sala.
3. **+1 check en `test_travel_cycle.gd`:** Validación de la frontera hacia el interior de la cueva en `LOC_COBBLE`.

---

## 4. Análisis de Aserciones Modificadas en Suites Existentes

Se auditaron minuciosamente todas las aserciones modificadas en las suites de pruebas durante R5A:

1. [`run_tests.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/run_tests.gd):
   - El conteo de ubicaciones del dataset pasó de `34` a `35`. Las 34 salas originales de CH_SURFACE permanecen inalteradas.
   - La condición de validación de viajes aceptó `world.has_structural_location(rule.target)` además de `frontier` y `chapter`, garantizando que destinos hacia el catálogo histórico se validen sin falsos positivos.
   - La prueba de desbloqueo de la reja comprobó que ahora el jugador entra a `LOC_BELOWGRATE` en lugar de detenerse en `LOC_GRATE`.
2. [`test_simulation_graph_isolation.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_simulation_graph_isolation.gd):
   - Salas habilitadas actualizadas de `34` a `35`.
   - Conteo de salas inertes fuera de juego actualizado de `151` a `150` (185 - 35 = 150).
   - Aserción de aislamiento: se verificó que las 150 salas inertes sigan sin efectos secundarios.
3. [`test_structural_contract_freeze.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd):
   - Actualización de constantes contractuales: 35 habilitadas, 150 inertes.
   - Sonda de aislamiento inerte: se desplazó de `LOC_BELOWGRATE` a [`LOC_COBBLE`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L40) para mantener la misma aserción de que una sala inerte no puede ser accedida ni modificada.
4. [`test_structural_loader.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_loader.gd):
   - Actualizado el conteo de `get_enabled_location_ids()` a 35 y salas inertes a 150.
   - Verificación de consulta inerte desplazada a `LOC_COBBLE`.
5. [`test_structural_projection_isolation.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_structural_projection_isolation.gd):
   - Salas jugables actualizadas a 35; inertes actualizadas a 150.
   - Secuencia jugable adaptada para verificar que tras abrir la reja, `ENTER` desciende efectivamente a `LOC_BELOWGRATE`.
6. [`test_travel_cycle.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_travel_cycle.gd):
   - Descenso a `LOC_BELOWGRATE` validado con resultado `ARRIVED`.
   - Se añadió la verificación de que `WEST` desde `LOC_BELOWGRATE` choca con la frontera hacia `LOC_COBBLE` preservando `turn == 11` y `pending_location == "LOC_COBBLE"`.

**Conclusión:** Ninguna aserción fue relajada ni debilitada; todas las modificaciones preservan estrictamente el contrato y desplazan los invariantes de frontera al límite real autorizado.

---

## 5. Auditoría de Iluminación Estructural (`LIT`) y `LOC_BELOWGRATE`

### Procedencia Histórica:
En el código fuente original de Crowther & Woods ADVENT y Open Adventure 1.22 (`init.c`, `advent.h`, `advent.dat`):
- El bit `COND_LIT` (valor 1) está presente en la condición de `LOC_BELOWGRATE`:
  ```c
  cond[LOC_BELOWGRATE] = COND_LIT;
  ```
- En [`06_reconstruccion_drawio/Open_Adventure.yaml`](file:///C:/remake/Colossal-Adventure-Reimagination-public/06_reconstruccion_drawio/Open_Adventure.yaml):
  ```yaml
  - LOC_BELOWGRATE:
      conditions:
        LIT: true
  ```
- En [`07_godot_open_adventure/godot/data/structural_world.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/structural_world.json):
  `flags["LIT"] == true` y `raw_conditions["LIT"] == true`.

**Fundamento físico/narrativo histórico:** `LOC_BELOWGRATE` es una pequeña cámara situada directamente debajo de una reja de acero de 3x3 pies que da al exterior (*"You are in a small chamber beneath a 3x3 steel grate to the surface"*). La luz solar penetra de forma natural a través de la reja, por lo que el jugador no requiere lámpara en esta habitación.

### Recuento y Distribución Exacta del Inventario `LIT`:
El cotejo reproducible entre [`06_reconstruccion_drawio/Open_Adventure.yaml`](file:///C:/remake/Colossal-Adventure-Reimagination-public/06_reconstruccion_drawio/Open_Adventure.yaml), [`canonical_inventory/chapters.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/canonical_inventory/chapters.json) y [`structural_world.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/structural_world.json) arroja:

- **Total de ubicaciones en el mundo histórico:** 185
- **Total de ubicaciones con condición `LIT`:** exactamente **37**
- **Total de ubicaciones sin condición `LIT` (oscuras):** exactamente **148**
- **Comprobación de suma:** 37 + 148 = 185

#### Distribución de las 37 ubicaciones `LIT` por capítulo editorial:
1. **`CH_SURFACE` (Capítulo 01 — 31 ubicaciones `LIT` de 34 miembros):**
   - Iluminadas (31): `LOC_START`, `LOC_HILL`, `LOC_BUILDING`, `LOC_VALLEY`, `LOC_ROADEND`, `LOC_CLIFF`, `LOC_SLIT`, `LOC_GRATE`, `LOC_LEDGE` y `LOC_FOREST1` hasta `LOC_FOREST22`.
   - No iluminadas en superficie (3):
     - `LOC_SEWER`: túnel de alcantarilla estrecho de tuberías de 1 pie (`conditions: {DEEP: true}`).
     - `LOC_FOOF2`: punto de tránsito mágico (`conditions: {ABOVE: true}`).
     - `LOC_FOOF4`: punto de tránsito mágico (`conditions: {ABOVE: true}`).
2. **`CH_ENTRY` (Capítulo 02 — 2 ubicaciones `LIT` de 12 miembros):**
   - `LOC_BELOWGRATE`: iluminada por luz directa cenital a través de la reja.
   - `LOC_COBBLE`: iluminada por luz tenue filtrada desde el este (*"There is a dim light at the east end of the passage"*).
3. **`CH_REPOSITORY` (Capítulo 09 — 3 ubicaciones `LIT` de 13 miembros):**
   - `LOC_NE`: borde noreste de la fisura.
   - `LOC_SW`: borde suroeste de la fisura.
   - `LOC_BREATHTAKING`: vista panorámica cavernosa con luz natural.
4. **`CH_ORIENTAL_PLOVER` (Capítulo 06 — 1 ubicación `LIT` de 12 miembros):**
   - `LOC_PLOVER`: cámara del chorlito con iluminación de alcoba.
5. **Restantes 7 capítulos (0 ubicaciones `LIT`):**
   - `CH_BEDQUILT` (0/17), `CH_CENTRAL` (0/18), `CH_MAZE_ALIKE` (0/33), `CH_RESERVOIR` (0/12), `CH_SPECIAL` (0/7), `CH_WITT_DIFFERENT` (0/18), `CH_Y2_WINDOWS` (0/9).
   - `LOC_NOWHERE` (ubicación especial de limbo) carece de condición `LIT`.

#### Explicación de la Discrepancia Documental Previa:
La descripción preliminar anotaba *"34 ubicaciones iluminadas en superficie + 2 en entrada + 5 subterráneas = 41"*. Esta suma partía de la presunción errónea de que *todos* los 34 miembros de `CH_SURFACE` eran `LIT`. Al verificar sala por sala, en `CH_SURFACE` solo 31 son `LIT` (al excluirse `LOC_SEWER`, `LOC_FOOF2` y `LOC_FOOF4`). Al sumar las 6 ubicaciones `LIT` fuera de superficie (2 en `CH_ENTRY` + 3 en `CH_REPOSITORY` + 1 en `CH_ORIENTAL_PLOVER`), el total es exactamente **31 + 6 = 37 ubicaciones `LIT`**, en correspondencia exacta y sin discrepancia técnica con el código fuente histórico y el dataset exportado.

### Implementación en Godot:
En [`WorldData.enable_structural_location`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L262):
```gdscript
var conds: Dictionary = (data.get("raw_conditions", {}) as Dictionary).duplicate()
var flags: Dictionary = data.get("flags", {})
for flag_name: String in flags.keys():
    if bool(flags[flag_name]):
        conds[flag_name] = true
loc.conditions = conds
```
En [`Interpreter._is_dark_here()`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd#L376):
```gdscript
func _is_dark_here() -> bool:
    var loc := world.location(state.current_location)
    if loc == null or loc.has_condition("LIT"):
        return false
    return state.state_of("LAMP") != "LAMP_BRIGHT" or not _lamp_here()
```
- La propiedad `LIT` no está cableada de manera rígida: se lee dinámicamente de los datos estructurales.
- Cuando en el futuro se habiliten salas no iluminadas (como `LOC_DEBRIS`), `has_condition("LIT")` evaluará a `false`, activando la lógica estricta de oscuridad (`PITCH_DARK`, agotamiento de batería de la linterna y caídas mortales de CUT C).
- Por ende, la iluminación natural de `LOC_BELOWGRATE` es fidedigna, aislada y no filtra luz artificial a salas subsiguientes.

---

## 6. Frontera Estructural y Control de Habilitación

Se verificó el mecanismo de defensa en profundidad de `WorldData`:

1. **Lista blanca estricta:**
   [`AUTHORIZED_ADDITIONAL_LOCATIONS`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd#L39) contiene exclusivamente `"LOC_BELOWGRATE"`.
   Cualquier llamada para habilitar otra sala (e.g. `enable_structural_location("LOC_COBBLE")`) es rechazada con `push_warning` y devuelve `false`.
2. **Idempotencia:** Invocaciones sucesivas para una sala ya habilitada no duplican objetos ni alteran el estado.
3. **Inmutabilidad del catálogo:** `StructuralCatalog` entrega copias defensivas profundas, impidiendo cualquier polución o mutación del catálogo estático de 185 salas.
4. **Intercepción de fronteras:** Todas las salidas hacia el interior de la cueva desde `LOC_BELOWGRATE` (`WEST` a `LOC_COBBLE`, `DOWN` a `LOC_COBBLE`/`LOC_DEBRIS`, `PIT` a `LOC_PITTOP`) se encuentran rigurosamente bloqueadas por el manejador de frontera (`TravelOutcome.FRONTIER`), preservando el aislamiento del resto del mapa.

---

## 7. Evaluación de Riesgos y Recomendación para R5B

### Análisis de Viabilidad para R5B:
- El harness de pruebas está intacto, robusto y automatizado.
- El modelo de viajes respeta la semántica histórica de Open Adventure 1.22.
- El subsistema de iluminación y oscuridad está preparado para diferenciar salas naturalmente iluminadas de salas oscuras.
- `LOC_COBBLE` (la antesala inmediata en R5B) comparte iluminación natural con `LOC_BELOWGRATE`.
- La frontera con salas oscuras se presentará al cruzar desde `LOC_COBBLE` hacia `LOC_DEBRIS`.

### Condiciones para la Autorización de R5B:
1. **Autorización humana explícita:** R5B solo debe implementarse con autorización formal.
2. **Ampliación controlada de la lista blanca:** Añadir progresivamente salas a `AUTHORIZED_ADDITIONAL_LOCATIONS` verificando que cada nueva salida no autorizada permanezca protegida por `TravelOutcome.FRONTIER`.
3. **Validación de la transición a oscuridad:** Si R5B o un corte subsiguiente incluye `LOC_DEBRIS`, comprobar rigurosamente la activación de `PITCH_DARK` y el requisito de linterna encendida.

---

## 8. Confirmación de Sincronización a Google Drive

La sincronización del commit `fb5b0adb3f0ecbec3a2aa30c655a6d336e89c659` hacia `G:\Mi unidad\RPG_Archaeology_IF` fue contrastada en modo verificación/dry-run:

- **Herramienta:** `sync_to_drive.ps1` con Robocopy.
- **Archivos versionados examinados:** 846/846.
- **Resultado Robocopy:** Copiado: 0, Omitido (coincidencia íntegra): 846, Errores: 0.
- **Archivos extra preservados en destino:** 36 entradas preservadas intactas (sin eliminación ni sobreescritura destructiva).
- **Estado de sincronización:** `PASS — VERIFIED`.

---

## 9. Conclusión de la Auditoría

- **Estado:** `CLOSED / VERIFIED / RECONCILED`
- **Integridad de pruebas:** 100% preservada (1503 checks superados en la totalidad del harness, +63 checks en el motor Godot).
- **Integridad de iluminación:** 100% conforme con fuentes históricas (37 `LIT` / 148 oscuras; 31 en superficie + 6 subterráneas).
- **Sincronización:** Verificada y consistente en Google Drive.
- **Preparación técnica:** El repositorio se encuentra listo y en estado limpio para que la autoridad humana autorice, cuando lo estime oportuno, el corte `CAR-CORE-002 / R5B`.
