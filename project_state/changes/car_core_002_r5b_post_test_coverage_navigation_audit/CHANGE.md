# CAR-CORE-002 / R5B-POST — Test Coverage & Navigation Verification Audit

**Estado:** `CLOSED / VERIFIED — R5B METRICS RECONCILED`
**Fecha:** 2026-10-26
**Baseline de referencia:** `b685ff1ad6fe65d9cc6d55380dda1b40fc8dda77`
**Tipo:** Auditoría técnica focal, reconciliación métrica exhaustiva y verificación de cobertura de navegación
**Corte auditado:** `CAR-CORE-002 / R5B — Hall of Mists Vestibule (CH_ENTRY Safe Subgraph)` (`b685ff1ad6fe65d9cc6d55380dda1b40fc8dda77`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R5C — Magic Transit & Word Connections` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Preflight y Estado de Integridad

- **Repositorio:** `C:\remake\Colossal-Adventure-Reimagination-public`
- **Rama:** `main`
- **HEAD verificado:** [`b685ff1ad6fe65d9cc6d55380dda1b40fc8dda77`](file:///C:/remake/Colossal-Adventure-Reimagination-public/project_state/changes/car_core_002_r5b_hall_of_mists_vestibule/CHANGE.md)
- **Árbol de trabajo:** Limpio (`working tree clean`, sin modificaciones no autorizadas).
- **Cumplimiento estricto de restricciones:** Cero modificaciones en código productivo de runtime, cero modificaciones en tests y cero alteraciones de datasets históricos. Cero habilitaciones de salas de R5C o posteriores.

---

## 2. Reconciliación Métrica Exhaustiva: 1.552 vs. 1.612

### Diagnóstico de la Discrepancia
En el informe de cierre de R5B se anotó la cifra de **1.552 checks globales**. La suma de los subtotales desglosados en dicho documento era:
- Fase 1: 70 checks
- Fase 3: 518 + 12 + 23 + 37 + 34 + 51 + 50 + 55 + 61 + 34 = 875 checks
- Fase 4: 11 escenas (capturas visuales, no checks formales)
- Fase 5: 62 checks
- Fase 6: 455 checks
- Fase 7: 150 checks
- **Suma aritmética real:** 70 + 875 + 62 + 455 + 150 = **1.612 checks**.

La diferencia matemática exacta es de **60 checks** (1.612 - 1.552 = 60).

### Causa Raíz de la Cifra 1.552
La auditoría determinó el origen exacto del número 1.552:
1. En el cierre de R5A-POST, el total auditado y reconciliado fue de **1.503 checks** (con 459 checks en `run_tests.gd`).
2. Al redactar R5B, el autor sumó al baseline de 1.503 checks únicamente los checks de la nueva suite focal de Fase 3:
   - 1.503 + 50 (de `test_hall_of_mists_vestibule.gd`) = **1.553 checks** (aproximado erróneamente en el texto a 1.552).
3. El autor omitió computar el incremento neto paralelo que experimentó [`run_tests.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/run_tests.gd) en Fase 3, el cual pasó de **459 a 518 checks (+59 checks netos)** al evaluar exhaustivamente los viajes, descripciones y salidas canónicas de las 6 nuevas salas habilitadas en el bucle integral.
4. Además, se produjo un desfase de 1 check en la estimación manual preliminar (+1 check = 60 de diferencia total).

### Desglose y Evidencia Ejecutable (Fase por Fase)

La ejecución real y reproducible de [`07_godot_open_adventure/tools/verify.ps1`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/tools/verify.ps1) arroja las siguientes salidas nominales exactas:

| Fase | Herramienta / Suite | Salida Exacta Registrada | Checks Formales |
|---|---|---|:---:|
| **Fase 1** | `test_simulation_graph.py` | `Ran 10 tests ... OK` | 10 |
| | `test_canonical_inventory.py` | `Ran 26 tests ... OK` | 26 |
| | `test_structural_projection.py` | `Ran 34 tests ... OK` | 34 |
| **Subtotal Fase 1** | Export e inventario canónico | | **70** |
| **Fase 2** | Godot editor import headless | Importación sin errores | 0 (puerta de enlace) |
| **Fase 3** | `run_tests.gd` | `PASS: 518 checks` | 518 |
| | `test_simulation_graph_isolation.gd` | `PASS: 12 CUT A isolation checks; 144 simulation-only IDs` | 12 |
| | `test_structural_projection_isolation.gd` | `PASS: 23 CAR-CORE-002 / R2 structural isolation checks; 144 inert locations` | 23 |
| | `test_structural_loader.gd` | `PASS: 37 CAR-CORE-002 / R3 tests` | 37 |
| | `test_structural_contract_freeze.gd` | `PASS: 34 CAR-CORE-002 / R4 structural freeze checks` | 34 |
| | `test_cave_mouth_pilot.gd` | `PASS: 51 CAR-CORE-002 / R5A checks` | 51 |
| | `test_hall_of_mists_vestibule.gd` | `PASS: 50 CAR-CORE-002 / R5B checks` | 50 |
| | `test_travel_cycle.gd` | `PASS: 55 CUT B travel checks` | 55 |
| | `test_darkness_lamp.gd` | `PASS: 61 CUT C darkness/lamp checks` | 61 |
| | `test_death_reincarnation.gd` | `PASS: 34 CUT D death/reincarnation checks` | 34 |
| **Subtotal Fase 3** | Suites de motor Godot | | **875** |
| **Fase 4** | `capture_scenes.gd` | `scene sheet written to res://captures/scenes.png (11 scenes)` | 0 (11 capturas visuales) |
| **Fase 5** | `test_runtime_illustration.gd` | `CAR-ART-003: 62 checks, 0 failures` | 62 |
| **Fase 6** | `build_ch01_vector_art.py` + `test_ch01_vector_art.gd` | `CAR-ART-004: 455 checks, 0 failures` | 455 |
| **Fase 7** | `build_grate_variants.py` + `test_grate_state_art.gd` | `CAR-ART-005: 150 checks, 0 failures` | 150 |
| **TOTAL GLOBAL RECONCILIADO** | **`verify.ps1` (todas las fases)** | **`ALL CHECKS PASSED`** | **1.612** |

### Comparación con el Baseline R5A-POST

- **Baseline R5A-POST:** 1.503 checks + 11 escenas capturadas.
- **Corte R5B auditado:** 1.612 checks + 11 escenas capturadas.
- **Incremento real de cobertura:** **+109 checks netos**, distribuidos exactamente en Fase 3:
  1. **+50 checks:** Suite focal nueva [`test_hall_of_mists_vestibule.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/test_hall_of_mists_vestibule.gd).
  2. **+59 checks:** Expansión de [`run_tests.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/run_tests.gd) (459 -> 518) debida a la cobertura sistemática de salidas, descripciones y conectividad de las 6 nuevas salas (`LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`, `LOC_CRACK`).

---

## 3. Verificación Funcional del Subgrafo R5B

La inspección del runtime y de las suites confirmó formalmente:

### Habilitación y Catálogo
- **185 ubicaciones estructurales:** Conservadas intactas en `StructuralCatalog` y validadas con SHA-256 inmutable de `structural_world.json`.
- **41 ubicaciones habilitadas:** Exactamente 34 de `CH_SURFACE` + 7 de `CH_ENTRY` (`LOC_BELOWGRATE`, `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`, `LOC_CRACK`).
- **144 ubicaciones inactivas:** Evaluadas individualmente en `test_simulation_graph_isolation.gd` y `test_structural_projection_isolation.gd`, confirmando que están excluidas de lookups, mapas y narración.
- **8 objetos funcionales:** `WorldData.objects` conserva exactamente 8 objetos. Objetos posteriores (`BIRD`, `SNAKE`, `PLANT`, `TROLL`, `DRAGON`, `NUGGET`) permanecen no instanciados.
- **0 actores:** Cero instancias de enanos o piratas.
- **Idempotencia:** Invocaciones repetidas de `enable_structural_location()` no mutan el catálogo ni duplican elementos.

### Navegación y Fronteras
- **Cruce de la reja:** `LOC_GRATE <-> LOC_BELOWGRATE` condicionado al estado `GRATE_OPEN`/`GRATE_CLOSED`.
- **Topología interna del subgrafo:** Navegación bidireccional continua verificada:
  `LOC_BELOWGRATE <-> LOC_COBBLE <-> LOC_DEBRIS <-> LOC_AWKWARD <-> LOC_BIRDCHAMBER <-> LOC_PITTOP`.
- **Atajos históricos operativos:** `LOC_BELOWGRATE -> PIT -> LOC_PITTOP`, `LOC_BELOWGRATE -> DEBRI -> LOC_DEBRIS`, `LOC_COBBLE -> PIT -> LOC_PITTOP`, y retornos mediante `DEPRE` a `LOC_GRATE` (o a `LOC_BELOWGRATE` si la reja está cerrada).
- **`LOC_CRACK`:** Confirmada como sala forzada (`is_forced() == true`). Al entrar, emite la narración histórica y rebota inmediatamente a `LOC_PITTOP` consumiendo exactamente 1 turno.
- **Semántica de `BACK` tras `LOC_CRACK`:** Emite `FORGOT_PATH` conforme al código C de Open Adventure 1.22 (`motion == game.loc`), permaneciendo en `LOC_PITTOP`. Regreso a `LOC_BIRDCHAMBER` requiere `EAST`.
- **Frontera de pozo en `LOC_PITTOP`:** El movimiento `DOWN` evalúa la condición de posesión de `NUGGET`; al estar ausente el objeto, se suspende fail-closed con `DEPENDENCY_PENDING`.
- **Fronteras hacia `LOC_MISTHALL` y salas inertes:** Bloqueadas como fronteras no habilitadas (`world.ui("frontier")`).

### Iluminación y Oscuridad (CUT C)
- **`LOC_COBBLE`:** Posee luz natural permanente (`LIT = true`). Total histórico reconciliado: 37 salas `LIT` (31 en CH_SURFACE, 2 en CH_ENTRY, 3 en CH_REPOSITORY, 1 en CH_ORIENTAL_PLOVER; 148 salas oscuras).
- **Galerías oscuras:** Las 5 salas restantes son oscuras (`LIT = false`). El ingreso sin lámpara encendida emite `PITCH_DARK` sin muerte fatal inmediata. Encender la linterna re-describe la sala y debita 1 punto de energía por turno de movimiento. Cero consumo espurio de RNG.

---

## 4. Matriz de Navegación y Cobertura Frente al Grafo Histórico

Para las 41 ubicaciones habilitadas en runtime existen un total de **159 reglas de viaje** proyectadas desde `Open_Adventure.yaml` / `structural_world.json`:
- **148 reglas internas:** Destino dentro de las 41 salas habilitadas (operativas).
- **6 reglas hacia fronteras (destinos `LOC_*` no habilitados):**
  1. `LOC_BUILDING -> XYZZY -> LOC_FOOF1` (bloqueado como frontera; previsto para R5C).
  2. `LOC_BUILDING -> PLUGH -> LOC_FOOF3` (bloqueado como frontera; previsto para R5C).
  3. `LOC_PITTOP -> DOWN -> LOC_NECKBROKE` (fail-closed por `DEPENDENCY_PENDING` sobre `NUGGET`).
  4. `LOC_PITTOP -> DOWN -> LOC_MISTHALL` (bloqueado como frontera de capítulo).
  5. `LOC_CLIFF -> JUMP -> LOC_NOMAKE` (bloqueado como frontera; caída suicida histórica pendiente de corte de letalidad).
  6. `LOC_LEDGE -> JUMP -> LOC_NOMAKE` (bloqueado como frontera; caída suicida histórica).
- **5 reglas de mensaje / especiales:** Mensajes de rechazo histórico (ej. reja cerrada `GRATE_NOWAY`).

### Matriz Focal del Subgrafo de Entrada (`CH_ENTRY`)

| Origen | Verbo / Movimiento | Destino Canónico | Condición | Estado Destino | Resultado en Runtime | Cobertura de Tests |
|---|---|---|---|:---:|---|:---:|
| `LOC_GRATE` | `ENTER` / `DOWN` / `INWAR` | `LOC_BELOWGRATE` | `not GRATE_CLOSED` | Habilitado | Arriba a `LOC_BELOWGRATE` | `run_tests.gd:248`, `test_hall...:152` |
| `LOC_GRATE` | `ENTER` | Mensaje reja cerrada | `always` | Especial | Emite `GRATE_NOWAY` | `test_cave_mouth...:138` |
| `LOC_BELOWGRATE` | `OUT` / `UPWAR` | `LOC_GRATE` | `not GRATE_CLOSED` | Habilitado | Arriba a `LOC_GRATE` | `run_tests.gd:253`, `test_cave_mouth...:316` |
| `LOC_BELOWGRATE` | `WEST` / `CRAWL` / `COBBL` | `LOC_COBBLE` | `always` | Habilitado | Arriba a `LOC_COBBLE` (LIT) | `test_hall...:156`, `test_travel...:79` |
| `LOC_BELOWGRATE` | `PIT` | `LOC_PITTOP` | `always` | Habilitado | Atajo directo a `LOC_PITTOP` | `test_hall...:211` |
| `LOC_BELOWGRATE` | `DEBRI` | `LOC_DEBRIS` | `always` | Habilitado | Atajo directo a `LOC_DEBRIS` | `test_hall...:217` |
| `LOC_COBBLE` | `EAST` / `SURFA` / `OUT` | `LOC_BELOWGRATE` | `always` | Habilitado | Retorno a `LOC_BELOWGRATE` | `run_tests.gd:251`, `test_hall...:161` |
| `LOC_COBBLE` | `WEST` / `INWAR` / `DEBRI` | `LOC_DEBRIS` | `always` | Habilitado | Arriba a `LOC_DEBRIS` (oscura) | `test_hall...:167` |
| `LOC_COBBLE` | `PIT` | `LOC_PITTOP` | `always` | Habilitado | Atajo directo a `LOC_PITTOP` | `test_hall...:223` |
| `LOC_DEBRIS` | `DEPRE` | `LOC_GRATE` | `not GRATE_CLOSED` | Habilitado | Atajo a superficie | `test_hall...:234` |
| `LOC_DEBRIS` | `ENTRA` | `LOC_BELOWGRATE` | `always` | Habilitado | Retorno a boca de cueva | Cubierto en topología base |
| `LOC_DEBRIS` | `EAST` / `CRAWL` / `COBBL` | `LOC_COBBLE` | `always` | Habilitado | Retorno a guijarros | `test_hall...:172` |
| `LOC_DEBRIS` | `WEST` / `CANYO` / `UPWAR` | `LOC_AWKWARD` | `always` | Habilitado | Arriba a cañón inclinado | `test_hall...:178` |
| `LOC_DEBRIS` | `XYZZY` | `LOC_FOOF2` | `always` | Habilitado (transitoria) | Tránsito a `LOC_BUILDING` | Conectividad `run_tests.gd:127` |
| `LOC_DEBRIS` | `PIT` | `LOC_PITTOP` | `always` | Habilitado | Atajo directo a `LOC_PITTOP` | Topología estructural validada |
| `LOC_AWKWARD` | `DEPRE` | `LOC_GRATE` | `not GRATE_CLOSED` | Habilitado | Atajo a superficie | Topología estructural validada |
| `LOC_AWKWARD` | `ENTRA` | `LOC_BELOWGRATE` | `always` | Habilitado | Retorno a boca de cueva | Topología estructural validada |
| `LOC_AWKWARD` | `EAST` / `DOWN` / `DEBRI` | `LOC_DEBRIS` | `always` | Habilitado | Retorno a `LOC_DEBRIS` | `test_hall...:183` |
| `LOC_AWKWARD` | `WEST` / `INWAR` / `UPWAR` | `LOC_BIRDCHAMBER` | `always` | Habilitado | Arriba a cámara del pájaro | `test_hall...:189` |
| `LOC_AWKWARD` | `PIT` | `LOC_PITTOP` | `always` | Habilitado | Atajo directo a `LOC_PITTOP` | Topología estructural validada |
| `LOC_BIRDCHAMBER` | `DEPRE` | `LOC_GRATE` | `not GRATE_CLOSED` | Habilitado | Atajo a superficie | Topología estructural validada |
| `LOC_BIRDCHAMBER` | `ENTRA` | `LOC_BELOWGRATE` | `always` | Habilitado | Retorno a boca de cueva | Topología estructural validada |
| `LOC_BIRDCHAMBER` | `DEBRI` | `LOC_DEBRIS` | `always` | Habilitado | Retorno a escombros | Topología estructural validada |
| `LOC_BIRDCHAMBER` | `EAST` / `CANYO` | `LOC_AWKWARD` | `always` | Habilitado | Retorno a cañón inclinado | `test_hall...:194` |
| `LOC_BIRDCHAMBER` | `WEST` / `PASSA` / `PIT` | `LOC_PITTOP` | `always` | Habilitado | Arriba a cima del pozo | `test_hall...:200` |
| `LOC_PITTOP` | `DEPRE` | `LOC_GRATE` | `not GRATE_CLOSED` | Habilitado | Atajo a superficie abierta | `test_hall...:228` |
| `LOC_PITTOP` | `ENTRA` | `LOC_BELOWGRATE` | `always` | Habilitado | Atajo a `LOC_BELOWGRATE` | `test_hall...:241` |
| `LOC_PITTOP` | `DEBRI` | `LOC_DEBRIS` | `always` | Habilitado | Retorno a escombros | Topología estructural validada |
| `LOC_PITTOP` | `EAST` / `PASSA` | `LOC_BIRDCHAMBER` | `always` | Habilitado | Retorno a cámara pájaro | `test_hall...:205` |
| `LOC_PITTOP` | `DOWN` / `PIT` / `STEPS` | `LOC_NECKBROKE` | `carry NUGGET` | Inerte / Mecánica | `DEPENDENCY_PENDING` (fail-closed) | `test_hall...:248` |
| `LOC_PITTOP` | `DOWN` | `LOC_MISTHALL` | `always` | Inerte (Frontera) | Bloqueado como frontera | `test_hall...:122` (rechazo catálogo) |
| `LOC_PITTOP` | `WEST` / `CRACK` | `LOC_CRACK` | `always` | Habilitado (transitoria) | Rebote forzado a `LOC_PITTOP` | `test_hall...:330` |
| `LOC_CRACK` | *(forzada/HERE)* | `LOC_PITTOP` | `always` | Habilitado | Retorno automático inmediato | `test_hall...:338` |

---

## 5. Inspección Específica de Conexiones Especiales

### Tránsito de la Palabra Mágica `PLUGH` vs. `XYZZY`
- En `Open_Adventure.yaml` y `structural_world.json`:
  - En `LOC_DEBRIS`: la regla histórica es `XYZZY -> LOC_FOOF2`. En la narración histórica figura: *"In the mud someone has scrawled, 'MAGIC WORD XYZZY'"*. Al pronunciar `XYZZY`, el jugador viaja a `LOC_FOOF2` y rebota automáticamente a `LOC_BUILDING` (superficie).
  - En `LOC_BUILDING`: `XYZZY -> LOC_FOOF1` (que conduce a `LOC_DEBRIS`) y `PLUGH -> LOC_FOOF3` (que conduce a `LOC_Y2`).
- **Estado en R5B:** `LOC_FOOF2` ya pertenecía a `CH_SURFACE` como sala transitoria de retorno hacia `LOC_BUILDING`. La habilitación de `LOC_DEBRIS` en R5B conectó operativamente la salida `XYZZY` hacia la superficie.
- **Diferenciación con R5C:** El futuro corte R5C corresponde a la habilitación formal de `LOC_FOOF1` (para permitir el viaje bidireccional desde `LOC_BUILDING` hacia `LOC_DEBRIS`), así como la resolución integral de las palabras mágicas canónicas (`XYZZY` y `PLUGH`) entre superficie y cueva profunda. La semántica mágica no fue alterada ni ampliada prematuramente en este corte.

---

## 6. Observación Manual: `LOC_START / WEST`

Se auditó minuciosamente la observación reportada sobre el movimiento hacia el oeste desde el punto de inicio:

1. **Regla en `Open_Adventure.yaml` (línea 393):**
   ```yaml
   - LOC_START:
       travel: [
         {verbs: [ROAD, WEST, UPWAR], action: [goto, LOC_HILL]},
         {verbs: [ENTER, BUILD, INWAR, EAST], action: [goto, LOC_BUILDING]},
         ...
       ]
   ```
2. **Código C original de Open Adventure 1.22:**
   La primera regla de viaje de `LOC_START` vincula los verbos `ROAD`, `WEST` y `UPSTREAM/UPWARD` con el destino `LOC_HILL`.
3. **Comportamiento en Runtime de Godot:**
   Desde `LOC_START`, ingresar `WEST` (o `W`) desplaza al jugador a `LOC_HILL` ("Colina").
4. **Cobertura en suites existentes:**
   Cubierto explícitamente en [`run_tests.gd:204-205`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/tests/run_tests.gd#L204-L205):
   ```gdscript
   _play(interpreter, ["W"])
   _equal(interpreter.state.current_location, "LOC_HILL", "west climbs the hill")
   ```
5. **Veredicto:** **`VERIFIED HISTORICAL`**. El comportamiento es 100% canónico, fiel al original y está plenamente cubierto por las pruebas de regresión.

---

## 7. Clasificación de Riesgos y Cobertura Ausente

| Asunto | Clasificación | Justificación / Mitigación |
|---|:---:|---|
| Descenso en `LOC_PITTOP -> LOC_MISTHALL` | `CRITICAL` (mitigado) | `LOC_MISTHALL` es la puerta de entrada a los enanos (`DEEP == true`). El motor Godot la mantiene bloqueada fail-closed como frontera no habilitada. Verificado en R5B. |
| Invocación de `XYZZY` desde `LOC_BUILDING` hacia `LOC_FOOF1` | `IMPORTANT` (mitigado) | `LOC_FOOF1` está deshabilitada en runtime; el intento de tránsito es rechazado como frontera hasta que R5C establezca el contrato de tránsito bidireccional. |
| Interacción `OPEN GRATE` vs `UNLOCK GRATE` | `USABILITY` | En la gramática de dos palabras, si la reja está cerrada con llave, el jugador debe escribir `UNLOCK GRATE` (o `ABRIR REJA` que en español activa el desbloqueo con llaves). Se mantiene como asunto de interacción pendiente de revisión UX humana. |
| Caída letal en pozos no habilitados (`LOC_NOMAKE`) | `DEFERRED` | Mecánicas de muerte profunda y resolución completa de caídas postergadas a capítulos posteriores o ampliaciones de CUT D. |

---

## 8. Conclusiones y Recomendaciones para R5C

1. **Veredicto de R5B:** El corte R5B mantiene plenamente su estado **`CLOSED / PASS`**. No existen regresiones de motor, filtraciones de datos ni desbordamientos de frontera.
2. **Reconciliación métrica final:** El total exacto, reproducible e íntegro del harness es **1.612 checks formales** (y 11 escenas vectoriales capturadas).
3. **Recomendación para R5C:**
   - La frontera entre superficie y el vestíbulo de la niebla es estable y hermética.
   - R5C puede proceder cuando sea autorizado para formalizar el tránsito bidireccional de palabras mágicas (`LOC_FOOF1`, `LOC_FOOF2`, etc.) sin riesgo de desestabilizar la navegación estructural.
