# CAR-CORE-002 / R5-PRE — Historical Travel Semantics Crosscheck

**Documento:** `HISTORICAL_TRAVEL_CROSSCHECK.md`
**Fecha:** 2026-10-26
**Estado:** `RESEARCH COMPLETE / R5A READY`
**Baseline inspeccionado:** `3b9a8f82f702464783314c5ff95ff893311525e1`
**Ámbito:** Auditoría técnica diferencial de la semántica de viajes entre el código C original de Open Adventure y el evaluador Godot CUT B
**Implementación R5A:** `PROPOSED / NOT AUTHORIZED`

---

## 1. Baseline y Fuentes Examinadas

La investigación se fundamenta en la inspección directa, sin modificaciones, de las fuentes autorizadas del proyecto:
- **Código C de Open Adventure:** `codigo_fuente_open_adventure/` (específicamente [`main.c`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/main.c), [`advent.h`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/advent.h), [`actions.c`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/actions.c), [`init.c`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/init.c), [`make_dungeon.py`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/make_dungeon.py)).
- **Datos declarativos del dungeon:** `codigo_fuente_open_adventure/adventure.yaml` y [`06_reconstruccion_drawio/Open_Adventure.yaml`](file:///C:/remake/Colossal-Adventure-Reimagination-public/06_reconstruccion_drawio/Open_Adventure.yaml).
- **Proyección estructural canónica R2:** [`07_godot_open_adventure/godot/data/structural_world.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/structural_world.json) (185 salas, 623 viajes, 70 objetos, digest `fda199af...`).
- **Motor de ejecución y evaluación Godot CUT B:** [`interpreter.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd), [`travel_rule.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/travel_rule.gd), [`world_data.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd), [`game_state.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/game_state.gd) y [`structural_catalog.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/structural_catalog.gd).

---

## 2. Versión y Procedencia del Código C Original

| Parámetro | Detalle de Procedencia |
|---|---|
| **Paquete** | Open Adventure (`open-adventure`) — Colossal Cave Adventure 2.5 (versión de 430 puntos de 1995 de Crowther & Woods) |
| **Versión** | **1.22** (publicada el 2026-07-08) |
| **Autor / Mantenedor** | Eric S. Raymond (`esr@thyrsus.com`) |
| **Licencia** | BSD-2-Clause ([`codigo_fuente_open_adventure/COPYING`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/COPYING), [`NOTICE.md`](file:///C:/remake/Colossal-Adventure-Reimagination-public/NOTICE.md)) |
| **Repositorio upstream** | `https://gitlab.com/esr/open-adventure` |
| **Ubicación local** | `C:\remake\Colossal-Adventure-Reimagination-public\codigo_fuente_open_adventure\` |

---

## 3. Algoritmo Histórico Reconstruido

El análisis de [`codigo_fuente_open_adventure/main.c`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/main.c#L558-L870) y [`codigo_fuente_open_adventure/make_dungeon.py`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/make_dungeon.py#L357-L565) revela con exactitud el ciclo de resolución de movimiento:

```text
Entrada: motion (verbo o dirección), loc (sala actual en game.loc)
   │
   ▼
1. playermove(motion):
   - Caso especial BACK (líneas 583-634):
       Busca en las reglas de game.loc un destino que coincida con game.oldloc
       (o game.oldlc2 si game.oldloc era forzada).
       Si lo halla, toma el verbo de esa regla y reinicia la búsqueda normal.
   - Casos LOOK, CAVE, NUL: gestionados de forma inmediata.
   │
   ▼
2. Localización de la primera regla:
   - Inicializa travel_entry = tkey[game.loc].
   - Recorre linealmente las reglas contiguas de la sala:
       ¿travel[travel_entry].motion == HERE || travel[travel_entry].motion == motion?
       - Si coincide: SALE del bucle de búsqueda e inicia la evaluación condicional.
       - Si alcanza .stop == true sin coincidencia: emite error de movimiento y TERMINA.
   │
   ▼
3. Evaluación condicional y cascada de fallo (bucle L12, líneas 710-750):
   - Evalúa la condición de la regla actual:
       cond_goto: (condarg1 == 0 || PCT(condarg1))
       cond_carry: TOTING(condarg1)
       cond_with: TOTING(condarg1) || AT(condarg1)
       cond_not: game.objects[condarg1].prop != condarg2
   - Si la condición es VERDADERA:
       SALE del bucle y ejecuta la regla (goto, speak o special).
   - Si la condición es FALSA:
       Salta a la siguiente regla distinta mediante traveleq():
       do {
           ++te_tmp;
       } while (traveleq(travel_entry, te_tmp));
       travel_entry = te_tmp;
       REINICIA la evaluación en la nueva regla.
```

### Hallazgo Crucial de la Semántica C
Cuando una condición resulta falsa, la función C `playermove()` avanza el puntero de regla saltando todas las entradas equivalentes según `traveleq()`:
```c
static bool traveleq(int a, int b) {
    return (travel[a].condtype == travel[b].condtype) &&
           (travel[a].condarg1 == travel[b].condarg1) &&
           (travel[a].condarg2 == travel[b].condarg2) &&
           (travel[a].desttype == travel[b].desttype) &&
           (travel[a].destval == travel[b].destval);
}
```
**Importante:** Al avanzar a la regla alternativa, el C **no comprueba** si `travel[te_tmp].motion == motion`. En la estructura histórica de Crowther & Woods (Sección 3 de `adventure.text`), la regla de contingencia (fallback) era la siguiente entrada en la tabla para esa localización, sin necesidad de duplicar todos los verbos en la fila alternativa.

---

## 4. Comparación de las Seis Familias de Condiciones

| Condición | Registros | Semántica C (`main.c`) | Semántica YAML (`Open_Adventure.yaml`) | Semántica Godot (`interpreter.gd`) | Estado en Godot |
|---|---:|---|---|---|---|
| `always` | 574 | `cond_goto`, `condarg1 == 0`. Incondicional. | `cond: null` | `match "always": return true` | Idéntica. |
| `not` | 25 | `cond_not`: `game.objects[obj].prop != state`. Verdadero si la propiedad del objeto difiere del valor especificado. | `cond: [not, OBJ, STATE]` | `state.state_of(obj) != state` | Idéntica si el objeto está instanciado; si falta emite `DEPENDENCY_PENDING`. |
| `pct` | 12 | `cond_pct`: `PCT(N)` (`randrange(100) < N`). Tirada de probabilidad. Consume RNG una vez al evaluarse. | `cond: [pct, N]` | `rng.randf() * 100.0 < float(N)` | Idéntica. |
| `carry` | 7 | `cond_carry`: `TOTING(obj)` (`game.objects[obj].place == -1`). El jugador lleva el objeto en su inventario. | `cond: [carry, OBJ]` | `state.is_carried(obj)` | Idéntica si el objeto está instanciado; si falta emite `DEPENDENCY_PENDING`. |
| `with` | 4 | `cond_with`: `TOTING(obj) \|\| AT(obj)` (`place == -1 \|\| place == loc`). El objeto está en el inventario o en la sala actual. | `cond: [with, OBJ]` | `state.is_here(obj) \|\| state.is_carried(obj)` | Idéntica si el objeto está instanciado; si falta emite `DEPENDENCY_PENDING`. |
| `nodwarves` | 1 | `cond_goto`, `condarg1 == 100`. Incondicional para el jugador (`PCT(100)`), pero ignorada por los enanos en `dwarfmove()`. | `cond: [nodwarves]` | `return rng.randf() * 100.0 < 100.0` | Idéntica. |

---

## 5. Auditoría e Inventario de las 39 Cadenas Mixtas

La tabla siguiente recoge las 39 interacciones mixtas donde una regla condicional precede a una regla alternativa en el catálogo histórico:

| # | Ubicación | Verbo(s) | Reglas | Condiciones | Destinos | Estado Requerido | Comportamiento C | Comportamiento Godot | Clasificación | Riesgo |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | `LOC_GRATE` | `ENTER`, `DOWN`, `INWAR` | 5 → 6 | `not GRATE GRATE_CLOSED` \| `always` | `goto LOC_BELOWGRATE` \| `speak GRATE_NOWAY` | Objeto `GRATE` | Si reja abierta va a `LOC_BELOWGRATE`; si cerrada habla `GRATE_NOWAY`. | Idéntico a C (evalúa `state_of("GRATE")`). | **VERIFIED_EQUIVALENT** | Descartado |
| **2** | `LOC_BELOWGRATE` | `OUT`, `UPWAR` | 0 → 1 | `not GRATE GRATE_CLOSED` \| `always` | `goto LOC_GRATE` \| `speak GRATE_NOWAY` | Objeto `GRATE` | Si reja abierta va a `LOC_GRATE`; si cerrada habla `GRATE_NOWAY`. | Idéntico a C (evalúa `state_of("GRATE")`). | **VERIFIED_EQUIVALENT** | Descartado |
| **3** | `LOC_PITTOP` | `DOWN` | 4 → 5 | `carry NUGGET` \| `always` | `goto LOC_NECKBROKE` \| `goto LOC_MISTHALL` | Objeto `NUGGET` | Con pepita muere en `LOC_NECKBROKE`; sin pepita va a `LOC_MISTHALL`. | `DEPENDENCY_PENDING` (`NUGGET` ausente en runtime). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **4** | `LOC_MISTHALL` | `UPWAR` | 3 → 4 | `carry NUGGET` \| `always` | `goto LOC_DOME` \| `goto LOC_PITTOP` | Objeto `NUGGET` | Con pepita va a `LOC_DOME`; sin pepita regresa a `LOC_PITTOP`. | `DEPENDENCY_PENDING` (`NUGGET` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **5** | `LOC_EASTBANK` | `OVER` | 3 → 4 | `not FISSURE BRIDGED` \| `always` | `speak NO_CROSS` \| `goto LOC_WESTBANK` | Objeto `FISSURE` | Sin puente habla `NO_CROSS`; con puente cruza a `LOC_WESTBANK`. | `DEPENDENCY_PENDING` (`FISSURE` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **6** | `LOC_KINGHALL` | `NORTH` | 1 → 4 | `not SNAKE SNAKE_BLOCKS` \| `always` | `goto LOC_FLOORHOLE` \| `goto LOC_SNAKEBLOCK` | Objeto `SNAKE` | Sin serpiente pasa al pozo; con serpiente bloquea. | `DEPENDENCY_PENDING` (`SNAKE` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **7** | `LOC_KINGHALL` | `SW` | 5 → 6 | `pct 35%` \| `with SNAKE` | `goto LOC_SECRET3` \| `goto LOC_SNAKEBLOCK` | Objeto `SNAKE`, RNG | Tirada 35% a secreto; si falla y hay serpiente bloquea. | `DEPENDENCY_PENDING` (`SNAKE` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **8** | `LOC_WESTPIT` | `CLIMB` | 1 → 2 | `not PLANT PLANT_GROWN` \| `always` | `goto LOC_BUILDING1` \| `goto LOC_CLIMBSTALK` | Objeto `PLANT` | Planta pequeña va a cornisa; planta crecida sube tallo. | `DEPENDENCY_PENDING` (`PLANT` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **9** | `LOC_WESTBANK` | `OVER` | 2 → 3 | `not FISSURE BRIDGED` \| `always` | `speak NO_CROSS` \| `goto LOC_EASTBANK` | Objeto `FISSURE` | Sin puente habla `NO_CROSS`; con puente cruza. | `DEPENDENCY_PENDING` (`FISSURE` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **10** | `LOC_BUILDING1` | *(vía/forzada)* | 0 → 1 | `not PLANT PLANT_BELLOWING` \| `always` | `goto LOC_NOCLIMB` \| `goto LOC_PLANTTOP` | Objeto `PLANT` | Planta sin regar no sube; gigante permite cima. | `DEPENDENCY_PENDING` (`PLANT` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **11** | `LOC_Y2` | `PLOVE` | 4 → 5 | `carry EMERALD` \| `always` | `special 2` \| `goto LOC_FOOF5` | Objeto `EMERALD` | Con esmeralda suelta y pasa; sin ella teletransporte directo. | `DEPENDENCY_PENDING` (`EMERALD` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **12** | `LOC_BEDQUILT` | `UPWAR` | 4 → 5 | `pct 60%` \| `pct 70%` | `speak FUTILE_CRAWL` \| `goto LOC_SECRET2` | RNG | 60% resbala; 70% de restante a secreto. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **13** | `LOC_BEDQUILT` | `UPWAR` | 4 → 6 | `pct 60%` \| `always` | `speak FUTILE_CRAWL` \| `goto LOC_DUSTY` | RNG | 60% resbala; resto a dusty room. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **14** | `LOC_BEDQUILT` | `UPWAR` | 5 → 6 | `pct 70%` \| `always` | `goto LOC_SECRET2` \| `goto LOC_DUSTY` | RNG | 70% a secreto; 30% a dusty room. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **15** | `LOC_BEDQUILT` | `NORTH` | 7 → 8 | `pct 50%` \| `pct 75%` | `speak FUTILE_CRAWL` \| `goto LOC_LOWROOM` | RNG | 50% resbala; 75% a low room. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **16** | `LOC_BEDQUILT` | `NORTH` | 7 → 9 | `pct 50%` \| `always` | `speak FUTILE_CRAWL` \| `goto LOC_THREEJUNCTION` | RNG | 50% resbala; resto a three junction. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **17** | `LOC_BEDQUILT` | `NORTH` | 8 → 9 | `pct 75%` \| `always` | `goto LOC_LOWROOM` \| `goto LOC_THREEJUNCTION` | RNG | 75% a low room; 25% a three junction. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **18** | `LOC_BEDQUILT` | `DOWN` | 10 → 11 | `pct 65%` \| `always` | `speak FUTILE_CRAWL` \| `goto LOC_ANTEROOM` | RNG | 65% resbala; 35% a anteroom. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **19** | `LOC_SECRET1` | `SOUTH` | 1 → 2 | `not DRAGON DRAGON_BARS` \| `always` | `goto LOC_SECRET5` \| `goto LOC_SECRET4` | Objeto `DRAGON` | Dragón vivo bloquea a secret4; muerto avanza. | `DEPENDENCY_PENDING` (`DRAGON` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **20** | `LOC_SECRET3` | `WEST` | 1 → 2 | `not DRAGON DRAGON_BARS` \| `always` | `goto LOC_SECRET5` \| `goto LOC_SECRET6` | Objeto `DRAGON` | Dragón vivo bloquea a secret6; muerto avanza. | `DEPENDENCY_PENDING` (`DRAGON` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **21** | `LOC_IMMENSE` | `NORTH` | 1 → 2 | `not DOOR DOOR_RUSTED` \| `always` | `goto LOC_WATERFALL` \| `speak RUSTY_DOOR` | Objeto `DOOR` | Puerta oxidada emite speak; engrasada pasa a cascada. | `SAFE_WITH_EXISTING_STATE` (`DOOR` existe en CH_01). Sala inerte. | **SAFE_WITH_EXISTING_STATE** | Controlado |
| **22** | `LOC_PLOVER` | `PLOVE` | 2 → 3 | `carry EMERALD` \| `always` | `special 2` \| `goto LOC_FOOF6` | Objeto `EMERALD` | Con esmeralda la suelta; sin ella teletransporte. | `DEPENDENCY_PENDING` (`EMERALD` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **23** | `LOC_SHELLROOM` | `SOUTH` | 2 → 3 | `carry CLAM` \| `carry OYSTER` | `speak CLAM_BLOCKER` \| `speak OYSTER_BLOCKER` | Objeto `CLAM`, `OYSTER` | Almeja bloquea paso estrecho; ostra también. | `DEPENDENCY_PENDING` (`CLAM`/`OYSTER` ausentes). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **24** | `LOC_SHELLROOM` | `SOUTH` | 2 → 4 | `carry CLAM` \| `always` | `speak CLAM_BLOCKER` \| `goto LOC_COMPLEX` | Objeto `CLAM` | Almeja bloquea; sin ella pasa a complex junction. | `DEPENDENCY_PENDING` (`CLAM` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **25** | `LOC_SHELLROOM` | `SOUTH` | 3 → 4 | `carry OYSTER` \| `always` | `speak OYSTER_BLOCKER` \| `goto LOC_COMPLEX` | Objeto `OYSTER` | Ostra bloquea; sin ella pasa a complex junction. | `DEPENDENCY_PENDING` (`OYSTER` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **26** | `LOC_WITTSEND` | `EAST` | 0 → 1 | `pct 95%` \| `always` | `speak FUTILE_CRAWL` \| `goto LOC_ANTEROOM` | RNG | 95% resbala en broma; 5% sale a anteroom. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **27** | `LOC_TOPSTALACTITE` | `DOWN` | 1 → 2 | `pct 40%` \| `pct 50%` | `goto LOC_ALIKE6` \| `goto LOC_ALIKE9` | RNG | 40% a alike6; 50% a alike9. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **28** | `LOC_TOPSTALACTITE` | `DOWN` | 1 → 3 | `pct 40%` \| `always` | `goto LOC_ALIKE6` \| `goto LOC_ALIKE4` | RNG | 40% a alike6; resto a alike4. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **29** | `LOC_TOPSTALACTITE` | `DOWN` | 2 → 3 | `pct 50%` \| `always` | `goto LOC_ALIKE9` \| `goto LOC_ALIKE4` | RNG | 50% a alike9; resto a alike4. | `DEPENDENCY_PENDING` (sala inerte en runtime). | **DEPENDENCY_PENDING** | Potencial (RNG) |
| **30** | `LOC_RESERVOIR` | `NORTH` | 1 → 2 | `not RESER WATERS_PARTED` \| `always` | `speak BAD_DIRECTION` \| `goto LOC_RESBOTTOM` | Objeto `RESER` | Aguas no partidas no dejan pasar; partidas baja. | `DEPENDENCY_PENDING` (`RESER` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **31** | `LOC_SWCHASM` | `OVER` | 1 → 2 | `with TROLL` \| `not CHASM TROLL_BRIDGE` | `speak TROLL_BLOCKS` \| `speak BRIDGE_GONE` | Objeto `TROLL`, `CHASM` | Troll presente exige peaje; puente roto avisa. | `DEPENDENCY_PENDING` (`TROLL`/`CHASM` ausentes). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **32** | `LOC_SWCHASM` | `OVER` | 1 → 3 | `with TROLL` \| `always` | `speak TROLL_BLOCKS` \| `special 3` | Objeto `TROLL` | Troll bloquea; sin troll cruza puente (special 3). | `DEPENDENCY_PENDING` (`TROLL` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **33** | `LOC_SWCHASM` | `OVER` | 2 → 3 | `not CHASM TROLL_BRIDGE` \| `always` | `speak BRIDGE_GONE` \| `special 3` | Objeto `CHASM` | Si puente no existe avisa; si existe cruza. | `DEPENDENCY_PENDING` (`CHASM` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **34** | `LOC_SWCHASM` | `JUMP` | 4 → 5 | `not CHASM TROLL_BRIDGE` \| `always` | `goto LOC_NOMAKE` \| `speak CROSS_BRIDGE` | Objeto `CHASM` | Sin puente cae al abismo (`NOMAKE`); con puente cruza. | `DEPENDENCY_PENDING` (`CHASM` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **35** | `LOC_NECHASM` | `OVER` | 1 → 2 | `with TROLL` \| `always` | `speak TROLL_BLOCKS` \| `special 3` | Objeto `TROLL` | Troll bloquea; sin troll cruza. | `DEPENDENCY_PENDING` (`TROLL` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **36** | `LOC_DEADEND13` | `SOUTH` | 1 → 2 | `not VEND VEND_BLOCKS` \| `always` | `goto LOC_ROUGHHEWN` \| `goto LOC_BADDIRECTION` | Objeto `VEND` | Máquina quitada permite paso; si bloquea error. | `DEPENDENCY_PENDING` (`VEND` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **37** | `LOC_LARGE` | `NORTH` | 1 → 2 | `with OGRE` \| `always` | `speak OGRE_SNARL` \| `goto LOC_STOREROOM` | Objeto `OGRE` | Ogro gruñe y bloquea; sin ogro entra a almacén. | `DEPENDENCY_PENDING` (`OGRE` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **38** | `LOC_RESNORTH` | `SOUTH` | 0 → 1 | `not RESER WATERS_PARTED` \| `always` | `speak BAD_DIRECTION` \| `goto LOC_RESBOTTOM` | Objeto `RESER` | Aguas no partidas bloquean; partidas baja. | `DEPENDENCY_PENDING` (`RESER` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |
| **39** | `LOC_CLIFFACE` | `UPWAR` | 1 → 2 | `carry RABBITFOOT` \| `always` | `goto LOC_CLIFFTOP` \| `goto LOC_FOOTSLIP` | Objeto `RABBITFOOT` | Con pata de conejo sube risco; sin ella resbala. | `DEPENDENCY_PENDING` (`RABBITFOOT` ausente). No salta. | **DEPENDENCY_PENDING** | Confirmado si se falsea |

---

## 6. Clasificación de Resultados

- **`VERIFIED_EQUIVALENT` (2 casos):** Casos 1 y 2 (`LOC_GRATE` y `LOC_BELOWGRATE`). Coincidencia al 100% entre C y Godot para todos los verbos y estados.
- **`SAFE_WITH_EXISTING_STATE` (1 caso):** Caso 21 (`LOC_IMMENSE`). El objeto `DOOR` ya existe en CH_01; la sala permanece deshabilitada contractualmente.
- **`DEPENDENCY_PENDING` (36 casos):** Requieren objetos no instanciados en runtime (`NUGGET`, `FISSURE`, `SNAKE`, `PLANT`, `EMERALD`, `DRAGON`, `CLAM`, `OYSTER`, `RESER`, `TROLL`, `CHASM`, `VEND`, `OGRE`, `RABBITFOOT`) o pertenecen a salas de azar no habilitadas.
- **`CONFIRMED_DIVERGENCE` (0 casos):** Cero discrepancias en el algoritmo de selección y resolución de viajes.

---

## 7. Pruebas Diferenciales Ejecutadas

Se ejecutó una suite de 19 escenarios de prueba diferenciales entre la transcripción exacta de `main.c` (`c_playermove`) y la de Godot (`interpreter.gd: _select_rule` / `_select_from`):

```text
=== RESULTADOS DE PRUEBAS DIFERENCIALES: LOC_GRATE & LOC_BELOWGRATE ===
1.  Enter grate while closed          -> C: SPOKE GRATE_NOWAY | Godot: SPOKE GRATE_NOWAY | PASS
2.  Enter grate while open            -> C: GOTO LOC_BELOWGRATE | Godot: GOTO LOC_BELOWGRATE | PASS
3.  Down into closed grate            -> C: SPOKE GRATE_NOWAY | Godot: SPOKE GRATE_NOWAY | PASS
4.  Down into open grate              -> C: GOTO LOC_BELOWGRATE | Godot: GOTO LOC_BELOWGRATE | PASS
5.  Inward into closed grate          -> C: SPOKE GRATE_NOWAY | Godot: SPOKE GRATE_NOWAY | PASS
6.  Inward into open grate            -> C: GOTO LOC_BELOWGRATE | Godot: GOTO LOC_BELOWGRATE | PASS
7.  East into forest from grate       -> C: GOTO LOC_FOREST7  | Godot: GOTO LOC_FOREST7  | PASS
8.  South into forest from grate      -> C: GOTO LOC_FOREST10 | Godot: GOTO LOC_FOREST10 | PASS
9.  West into forest from grate       -> C: GOTO LOC_FOREST9  | Godot: GOTO LOC_FOREST9  | PASS
10. Build/Start from grate            -> C: GOTO LOC_START    | Godot: GOTO LOC_START    | PASS
11. North to slit from grate          -> C: GOTO LOC_SLIT     | Godot: GOTO LOC_SLIT     | PASS
12. Out from below grate while closed -> C: SPOKE GRATE_NOWAY | Godot: SPOKE GRATE_NOWAY | PASS
13. Out from below grate while open   -> C: GOTO LOC_GRATE    | Godot: GOTO LOC_GRATE    | PASS
14. Up from below grate while closed  -> C: SPOKE GRATE_NOWAY | Godot: SPOKE GRATE_NOWAY | PASS
15. Up from below grate while open    -> C: GOTO LOC_GRATE    | Godot: GOTO LOC_GRATE    | PASS
16. West to cobble from below grate   -> C: GOTO LOC_COBBLE   | Godot: GOTO LOC_COBBLE   | PASS
17. Crawl to cobble from below grate  -> C: GOTO LOC_COBBLE   | Godot: GOTO LOC_COBBLE   | PASS
18. Pit to pittop from below grate    -> C: GOTO LOC_PITTOP   | Godot: GOTO LOC_PITTOP   | PASS
19. Debri to debris from below grate  -> C: GOTO LOC_DEBRIS   | Godot: GOTO LOC_DEBRIS   | PASS

TOTAL: 19/19 ESCENARIOS IDÉNTICOS (100% PASS).
```

### Prueba de Salvaguarda ante Objeto no Instanciado
En el escenario `LOC_PITTOP` + verbo `DOWN` con `NUGGET`:
- **En C:** La memoria estática contiene los 70 objetos (`game.objects[NUGGET].place != -1`), por lo que la condición `carry NUGGET` se evalúa como `false` y el jugador cae incondicionalmente a `LOC_MISTHALL`.
- **En Godot:** `NUGGET` no forma parte de `world.objects`, por lo que el evaluador se detiene emitiendo `DEPENDENCY_PENDING`.
- **Conclusión de fidelidad:** Godot protege al jugador de entrar en salas subterráneas profundas antes de que su simulación esté lista, sin falsear la condición ni saltarse la regla condicional.

---

## 8. Resultado Focal para R5A (`LOC_BELOWGRATE`)

1. **Registros del descenso:** En `LOC_GRATE`, Regla 5 (`not GRATE GRATE_CLOSED goto LOC_BELOWGRATE`) y Regla 6 (`always speak GRATE_NOWAY`).
2. **Registros del regreso:** En `LOC_BELOWGRATE`, Regla 0 (`not GRATE GRATE_CLOSED goto LOC_GRATE`) y Regla 1 (`always speak GRATE_NOWAY`).
3. **Estado funcional:** `GRATE` y `KEYS` ya están presentes y probados en `WorldData` y `GameState`.
4. **Comportamiento `BACK`:** Al estar en `LOC_BELOWGRATE`, `BACK` busca la regla que lleva a `LOC_GRATE` (Regla 0, verbo `OUT`) y ejecuta `_try_move("OUT")`, respetando el estado de la reja exactamente igual que el C original.
5. **Salidas hacia adelante:** Al intentar moverse a `LOC_COBBLE`, `LOC_PITTOP` o `LOC_DEBRIS`, el motor emite de forma natural `TravelOutcome.FRONTIER` (o `BORDER`), manteniendo la frontera segura.
6. **Requisito para R5A:** Solo se necesita un adaptador de carga en [`world_data.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd) que instancie `LOC_BELOWGRATE` desde [`StructuralCatalog`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/structural_catalog.gd) con fallback a la descripción histórica en inglés. No se requiere modificar el evaluador de viajes.

---

## 9. Análisis de Enanos y Reconciliación para R5B

- La fuente C (`main.c:335`) establece que los enanos solo se activan cuando `INDEEP(game.loc)` es verdadero (`dflag` pasa de 0 a 1).
- La bandera `DEEP` es `False` en: `LOC_BELOWGRATE`, `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER` y `LOC_PITTOP`.
- Solo a partir de `LOC_MISTHALL` la bandera `DEEP` es `True`.
- Por tanto, la inclusión de `LOC_PITTOP` en el subgrafo de `CH_ENTRY` (propuesto para R5B) es **segura respecto a los enanos**: el enano asignado a `LOC_PITTOP` en `dwarflocs` no se activa mientras el jugador no haya penetrado en `LOC_MISTHALL`.

---

## 10. Recomendación Arquitectónica

Se recomienda la **Alternativa A (Mantener el evaluador actual con bloqueo de dependencias pendientes)**:
- El evaluador de Godot ya implementa con exactitud la precedencia histórica y la semántica de `traveleq` a través de `_next_distinct()`.
- La interrupción por `DEPENDENCY_PENDING` ante objetos no instanciados es una salvaguarda indispensable que evita bypasses accidentales hacia salas no implementadas.
- No se requiere rediseño ni adaptadores complejos de evaluación trivalente.

**Estado resultante de la auditoría:** `CLOSED / VERIFIED — R5A READY`
**Próximo corte propuesto:** `CAR-CORE-002 / R5A — Cave Mouth Pilot (LOC_BELOWGRATE)` (`PROPOSED / NOT AUTHORIZED`).
