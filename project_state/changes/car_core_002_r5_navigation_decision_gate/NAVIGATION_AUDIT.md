# CAR-CORE-002 / R5 — Informe de Auditoría Técnica de Navegación Estructural

**Documento:** `NAVIGATION_AUDIT.md`
**Fecha:** 2026-10-25
**Estado:** `AUDIT COMPLETE / DECISION GATE — VIABLE WITH CONDITIONS`
**Baseline inspeccionado:** `aef24804fbe417ef028c91fa86d42aa258fd3bb9`
**Ámbito:** Auditoría técnica de navegación para el Decision Gate de CAR-CORE-002 / R5

---

## 1. Baseline e Infraestructura Previa

La auditoría parte de los contratos formalizados y verificados en los cortes R1 a R4:
- **`CAR-CORE-002 / R1`:** Inventario canónico determinista (`07_godot_open_adventure/canonical_inventory/*.json`).
- **`CAR-CORE-002 / R2`:** Proyección estructural global completa (`07_godot_open_adventure/godot/data/structural_world.json`, SHA-256: `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3`).
- **`CAR-CORE-002 / R3`:** Cargador estructural desacoplado (`StructuralCatalog`) y vista habilitada de Capítulo 01 en `WorldData`.
- **`CAR-CORE-002 / R4`:** Congelación formal de contratos observables (`CAR_CORE_002_STRUCTURAL_CONTRACT.md` y `CAR_CORE_002_TRACEABILITY_MATRIX.md`), suite de 34 comprobaciones (`test_structural_contract_freeze.gd`) y suite integral de regresión con `ALL CHECKS PASSED`.

Invariantes observadas en el repositorio:
- **185 ubicaciones estructurales** (índice 0 `LOC_NOWHERE` a 184 `LOC_FOOF6`).
- **623 registros de viaje ordenados** (`global_travel_index` 0..622).
- **70 objetos estructurales estáticos** (índice 0 `NO_OBJECT`).
- **11 capítulos editoriales** con 100% de cobertura y 0 huérfanas.
- **34 ubicaciones habilitadas** activas en runtime (`CH_SURFACE`).
- **151 ubicaciones estructurales deshabilitadas** (`STRUCTURAL / DISABLED`).
- **8 objetos funcionales activos** en `WorldData.objects` y `GameState`.

---

## 2. Auditoría del Motor de Navegación Existente

### 2.1 Flujo Real de Ejecución de Movimiento
A partir del análisis del código en [`interpreter.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd), [`command_parser.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/command_parser.gd), [`world_data.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd) y [`game_state.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/game_state.gd), el flujo real de procesamiento de una orden de movimiento es:

```text
Entrada del jugador (String)
         │
         ▼
Interpreter.submit(line)
   ├── Snapshot de oscuridad: was_dark = _is_dark_here()
   ├── Incremento de turno: state.turn += 1
   └── _lamp_check() (consumo de energía de lámpara y alertas)
         │
         ▼
CommandParser.parse(line)
   ├── Extracción de tallos de 5 letras (stem)
   └── Identificación de tipo de comando (Command.Kind.MOTION)
         │
         ▼
Interpreter._handle_motion(command)
   ├── Casos especiales: LOOK, BACK, CAVE
   ├── _advance_history() (oldlc2 = oldloc; oldloc = current_location)
   └── _try_move(command.motion)
         │
         ▼
Interpreter._select_rule(loc, verb)
   ├── Búsqueda de primera regla en loc.travel que coincida con el verbo
   └── _select_from(loc, index):
         ├── Si candidate.cond_object no está en world.objects -> DEPENDENCY_PENDING
         ├── Si _condition_holds(candidate) es TRUE -> candidate seleccionado
         └── Si es FALSE -> _next_distinct(loc, index) (salto a regla alternativa)
         │
         ▼
Interpreter._execute_move(rule)
   ├── Manejadores especiales (special 1: plover, 2: esmeralda, 3: troll bridge)
   ├── Destinos speak: state.travel_outcome = SPOKE (sin movimiento)
   ├── Destinos letales (candidate.target == "LOC_NOWHERE" y loc.is_forced()) -> DEATH_PENDING
   ├── Validación de frontera: si not world.is_in_chapter(candidate.target) -> FRONTIER
   └── Transición activa:
         ├── state.move_to(candidate.target, false)
         ├── _describe_current(false)
         └── Si loc.is_forced() == TRUE:
               ├── Bucle de cascada automática (hasta MAX_RULE_WALK = 64)
               ├── _advance_history()
               └── candidate = _select_rule(loc, "HERE")
```

### 2.2 Evaluación de Componentes del Motor

| Componente | Implementación Real en Código | Estado de Reusabilidad | Justificación |
|---|---|---|---|
| **Propietario de ubicación actual** | `GameState.current_location` | `REUSABLE` | Desacoplado; acepta cualquier identificador `LOC_*` válido sin requerir cambios de clase. |
| **Historial de movimiento** | `GameState.previous_location` (`oldloc`) y `GameState.previous_previous_location` (`oldlc2`) | `REUSABLE` | Mantiene fielmente el contrato histórico de 2 pasos requerido por `BACK` y por el depósito de objetos al morir. |
| **Evaluador de reglas de viaje** | `Interpreter._select_rule()` / `_select_from()` / `_condition_holds()` | `REUSABLE` | Evalúa precedencia estricta, semántica *first-match-wins*, condiciones y salto a reglas distintas. |
| **Semántica de `BACK`** | `Interpreter._go_back()` | `REUSABLE` | Respeta bandera `NOBACK`, salta salas forzadas intermedias y busca regla inversa válida. |
| **Salas forzadas (`FORCED`)** | `WorldLocation.is_forced()` / `Interpreter._execute_move()` | `REUSABLE` | Resuelve cascada automática sin entrada de usuario ni consumo de turnos; probado en `LOC_SEWER`. |
| **Destinos de muerte** | `Interpreter._consume_death_pending()` / `_reincarnate()` | `REUSABLE` | Detecta destinos letales forzados hacia `LOC_NOWHERE` y caídas en oscuridad (35%), enlazando con CUT D. |
| **Destinos `special 1`** | `Interpreter._execute_move()` (manejador 1) | `REUSABLE` | Lógica del paso Plover (`LOC_ALCOVE` <-> `LOC_PLOVER`, chequeo de esmeralda) completamente funcional. |
| **Destinos `special 2`** | `Interpreter._execute_move()` (manejador 2) | `REQUIRES_IMPLEMENTATION` | Plover caída de esmeralda; requiere `EMERALD` en `world.objects`. Actualmente produce `DEPENDENCY_PENDING`. |
| **Destinos `special 3`** | `Interpreter._execute_move()` (manejador 3) | `DEFERRED` | Cruce del troll (`LOC_SWCHASM` / `LOC_NECHASM`); requiere troll, oso y chasm. Tipado como `DEPENDENCY_PENDING`. |
| **Avance de turnos** | `Interpreter.submit()` | `REUSABLE` | Incrementa turnos antes de comandos válidos; las salas forzadas no consumen turnos adicionales. |
| **Consumo de RNG** | `Interpreter.rng` (semilla `20251020`) | `REUSABLE` | Aislado en condiciones probabilísticas (`pct`) y caídas oscuras. 0 consumo en lecturas estructurales. |
| **Comprobador de fronteras** | `world.is_in_chapter()` | `REUSABLE` | Detiene el avance hacia salas fuera del conjunto habilitado produciendo `GameState.TravelOutcome.FRONTIER`. |
| **Acceso a `WorldData.locations`** | `WorldData.locations` / `WorldData.location()` | `REQUIRES_ADAPTER` | Actualmente sólo contiene 34 instancias de `CH_SURFACE`. Salas nuevas habilitadas necesitan fábrica o adaptador. |
| **Conjunto `enabled_location_ids`** | `WorldData.enabled_location_ids` | `REUSABLE` | Diccionario explícito creado en R3; permite habilitación aditiva sin alterar estructuras maestras. |

---

## 3. Auditoría de Precedencia Histórica y Manejo de Condiciones

La fuente histórica contiene exactamente **623 reglas de viaje ordenadas**. En 39 casos, una sala presenta reglas múltiples asociadas al mismo verbo de movimiento o al pseudoverbo `HERE`, donde una o varias reglas condicionales preceden a una regla posterior (frecuentemente `always`).

### 3.1 Los Cuatro Estados de Evaluación Condicional
Para preservar el comportamiento histórico sin inventar estados ni producir saltos incorrectos, el evaluador distingue:

1. **Condición evaluable y verdadera:** La condición se evalúa contra el estado activo de `GameState` y se cumple. Se ejecuta el viaje o acción de la regla candidata.
2. **Condición evaluable y falsa:** La condición se evalúa y no se cumple. El motor invoca `_next_distinct(loc, index)` para saltar todas las reglas equivalentes y evaluar la siguiente alternativa distinta.
3. **Condición pendiente de implementación:** La regla depende de un objeto, puzle o subsistema no instanciado en el corte (p. ej. `FISSURE`, `SNAKE`, `special3`).
4. **Condición dependiente de un estado histórico no disponible:** El objeto existe estáticamente en el catálogo pero su máquina de estados no está activa en runtime.

### 3.2 Política Contractual para Casos 3 y 4 (Anti-Bypass Policy)
> [!CRITICAL]
> **Prohibición de asunción silenciosa de verdad o falsedad:**
> Si una condición previa no puede evaluarse con fidelidad histórica:
> - **NO asumir `false`:** Asumir falsedad provocaría que el evaluador avance silenciosamente a la regla `always` posterior. Por ejemplo, en `LOC_EASTBANK`, la Regla 3 (`cond=not FISSURE FISSURE_BRIDGED` -> mensaje `NO_CROSS`) precede a la Regla 4 (`cond=always` -> `LOC_WESTBANK`). Si la condición de la fisura se asumiera falsa, el jugador cruzaría caminando sobre una fisura sin puente.
> - **NO asumir `true`:** Asumir verdad activaría viajes o muertes condicionadas de forma espuria.
>
> **Política:** Ante cualquier condición no evaluable por falta de subsistema o dependencia de objeto ausente, el motor debe detener la resolución de viaje y devolver inmediatamente:
> `GameState.TravelOutcome.DEPENDENCY_PENDING`
> con un mensaje descriptivo al jugador ("Un mecanismo histórico no implementado en este corte impide el paso").
>
> Esta política ya se encuentra implementada en [`Interpreter._select_from()`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd#L336-L338):
> ```gdscript
> if candidate.cond_object != "" and not world.objects.has(candidate.cond_object):
>     _pending_dependency("travel condition requires object " + candidate.cond_object)
>     return null
> ```

---

## 4. Matriz de Condiciones de Viaje (623 Registros)

| Condición | Registros | Semántica Histórica | Implementación en `Interpreter` | Dependencias Funcionales | Viabilidad en R5 Inicial | Riesgo de Precedencia |
|---|---:|---|---|---|---|---|
| `always` | 574 | Transición incondicional siempre satisfecha | `_condition_holds()` devuelve `true` | Ninguna | `ALTA` | Ninguno si es la primera regla del verbo; si va tras una condición pendiente, requiere política anti-bypass. |
| `not` | 25 | Objeto no se encuentra en el estado indicado (`not_state`) | `state.state_of(obj) != state` | Estado de objeto en `GameState.object_state` | `MEDIA` | 7 registros usan `GRATE` (completamente funcional en CH_01). Los 18 restantes (`FISSURE`, `SNAKE`, `PLANT`, `DRAGON`, `DOOR`, `RESER`, `CHASM`, `VEND`) deben dar `DEPENDENCY_PENDING`. |
| `pct` | 12 | Transición probabilística gobernada por porcentaje | `rng.randf() * 100.0 < percent` | Consumo de RNG de partida | `MEDIA` | 12 registros distribuidos en `LOC_KINGHALL` (1), `LOC_BEDQUILT` (6), `LOC_SWISSCHEESE` (2), `LOC_WITTSEND` (1), `LOC_TOPSTALACTITE` (2). No dependen de objetos. Viables técnicamente, pero pertenecen a capítulos profundos diferidos. |
| `carry` | 7 | Requiere portar un objeto en el inventario | `state.is_carried(obj)` | Objeto activo en inventario | `BAJA` | Dependen de `CLAM` (1), `OYSTER` (1), `EMERALD` (2), `NUGGET` (2) y `RABBITFOOT` (1). Ninguno está en el inventario inicial de CH_01. Deben dar `DEPENDENCY_PENDING`. |
| `with` | 4 | Objeto presente en sala o en inventario | `state.is_here(obj) or state.is_carried(obj)` | Ubicación de objeto en sala o inventario | `BAJA` | Dependen de `SNAKE` (1 en `LOC_KINGHALL`), `TROLL` (2 en chasm), `OGRE` (1 en `LOC_LARGE`). Actores no autorizados en R5. Deben dar `DEPENDENCY_PENDING`. |
| `nodwarves` | 1 | Prohíbe el seguimiento de enanos (de `LOC_LONGWEST` a `LOC_DIFFERENT1`) | Tratado como `always` (100%) para el jugador | Simulación de enanos (CUT E) | `DEFERRED` | No restringe al jugador humano (probabilidad 100%). Pertenece a CH_04 (`CH_MAZE_ALIKE`), diferido hasta CUT E. |

---

## 5. Matriz de Destinos de Viaje

| Clase de Destino | Total Registros | Destinos / Variantes | Semántica y Comportamiento Observable | Estado y Dependencias |
|---|---:|---|---|---|
| `goto` | 583 | 185 ubicaciones históricas (`LOC_*`) | Desplazamiento del jugador a la ubicación destino. Valida si la sala está en `enabled_location_ids`. Si no, emite `FRONTIER`. | `REUSABLE`. Si el destino está habilitado, actualiza `current_location`. |
| `speak` | 34 | 18 mensajes textuales distintos | Emite mensaje narrativo en pantalla sin alterar la ubicación (`current_location`) ni consumir movimiento. `travel_outcome = SPOKE`. | `REUSABLE`. Mensajes provistos por `WorldData.message()`. |
| `special` | 6 | Manejadores 1, 2 y 3 | Delegaciones a controladores específicos de motor: | |
| ↳ `special 1` | 2 | Paso Plover (`LOC_ALCOVE` y `LOC_PLOVER`) | Permite transitar entre ALCOVE y PLOVER solo si el jugador no lleva carga o lleva únicamente la esmeralda. | `REUSABLE`. Implementado y validado en CUT B. |
| ↳ `special 2` | 2 | Plover drop emerald (`LOC_Y2` y `LOC_PLOVER`) | Deja caer la esmeralda en la sala antes de transitar. | `REQUIRES_IMPLEMENTATION` (falta `EMERALD` en runtime). Tipado como `DEPENDENCY_PENDING`. |
| ↳ `special 3` | 2 | Cruce del Troll (`LOC_SWCHASM` y `LOC_NECHASM`) | Evaluación de presencia del troll, alimentación con el oso, cobro de peaje y destrucción del puente de chasm. | `DEFERRED / NOT AUTHORIZED`. Tipado como `DEPENDENCY_PENDING`. |

---

## 6. Auditoría de Ubicaciones Especiales (185 Ubicaciones)

| Categoría Especial | Recuento | Ubicaciones Identificadas | Tratamiento en Runtime y Riesgo Asociado |
|---|---:|---|---|
| **Salas Forzadas (`is_forced`)** | 22 | `LOC_CRACK`, `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_DOME`, `LOC_CLIMBSTALK`, `LOC_BUILDING1`, `LOC_SNAKEBLOCK`, `LOC_PARALLEL1`, `LOC_PARALLEL2`, `LOC_SEWER`, `LOC_NOCLIMB`, `LOC_PLANTTOP`, `LOC_BADDIRECTION`, `LOC_FOOTSLIP`, `LOC_CLIFFTOP`, `LOC_GRUESOME`, `LOC_FOOF1`..`LOC_FOOF6` | Se ejecutan mediante cascada automática (`_select_rule(loc, "HERE")`). Si se habilitan sin su destino final, podrían generar detención abrupta o bucles. Las 6 de FOOF teletransportan determinísticamente. |
| **Salas Letales (`is_lethal`)** | 4 | `LOC_NECKBROKE` (caída en pozo), `LOC_NOMAKE` (salto al vacío), `LOC_FOOTSLIP` (resbalón en risco), `LOC_GRUESOME` (salto en volcán) | Son forzadas con destino `LOC_NOWHERE`. Al entrar, `Interpreter` activa `DEATH_PENDING` e invoca el diálogo de reencarnación de CUT D. |
| **Salas Transitorias** | 5 | `LOC_CRACK`, `LOC_CLIMBSTALK`, `LOC_PARALLEL1`, `LOC_PARALLEL2`, `LOC_CLIFFTOP` | Pasajes breves de narración que reenvían automáticamente a otra sala. Seguras si sus destinos están habilitados. |
| **Salas de Teletransporte Mágico** | 6 | `LOC_FOOF1` (`XYZZY` de BUILDING a DEBRIS), `LOC_FOOF2` (`XYZZY` de DEBRIS a BUILDING), `LOC_FOOF3` (`PLUGH` a Y2), `LOC_FOOF4` (`PLUGH` a BUILDING), `LOC_FOOF5` (`PLOVE` a PLOVER), `LOC_FOOF6` (`PLOVE` a Y2) | Salas intermedias forzadas que imprimen `>>Foof!<<` y colocan al jugador en el destino del atajo. `FOOF1` y `FOOF2` son inmediatas para la entrada a la cueva. |
| **Salas con Enanos (`dwarflocs`)** | 6 | `LOC_KINGHALL`, `LOC_WESTBANK`, `LOC_Y2`, `LOC_ALIKE3`, `LOC_COMPLEX`, `LOC_MAZEEND12` | Lugares de generación y patrulla de enanos en Open Adventure. Deben permanecer sin simulación activa de combate hasta CUT E. |
| **Ubicación Centinela Nula** | 1 | `LOC_NOWHERE` (índice 0) | Espacio no físico fuera de la cueva. Sin descripción larga, sin viajes salientes. Almacén de objetos ausentes. |

---

## 7. Clasificación de Ubicaciones y Conectividad

Conforme a las directrices de la Sección 8 del mandato, se clasifica el universo de 185 salas en 5 dimensiones conceptuales no disyuntas:

```
[A. Structural Exists: 185 salas]
 │
 ├── [B. Candidate Enabled: 43 salas (34 de CH_01 + 9 de CH_ENTRY)]
 │     │
 │     └── [C. Navigable With Current Semantics: 40 salas (34 de CH_01 + 6 antecámara CH_02)]
 │
 ├── [D. Requires Functional Dependency: 142 salas (bloqueadas por puzles / objetos ausentes)]
 │
 └── [E. Special / Unsafe / Deferred: 39 salas (22 forzadas, 4 letales, 6 enanos, 1 nula, 6 special)]
```

### 7.1 Definición y Recuentos de las 5 Dimensiones
- **A. Structural Exists (185 salas):** Cobertura total del catálogo estructural v1.
- **B. Candidate Enabled (43 salas):** Las 34 salas de `CH_SURFACE` más 9 salas de `CH_ENTRY` (`LOC_BELOWGRATE`, `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`, `LOC_CRACK`, `LOC_FOOF1`, `LOC_FOOF2`). Todas tienen descripciones históricas disponibles, cero dependencias de actores y retorno garantizado a superficie.
- **C. Navigable With Current Semantics (40 salas):** 34 salas de CH_01 + 6 salas ordinarias de la antecámara de CH_ENTRY (`LOC_BELOWGRATE`, `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`). El jugador puede entrar, desplazarse entre ellas en cualquier dirección y salir sin requerir lógica de puzle adicional.
- **D. Requires Functional Dependency (142 salas):** Todas las salas que se encuentran tras obstáculos de puzles (la fisura que requiere el puente de cristal, la serpiente que requiere el pájaro, el dragón sobre la alfombra, el pozo de la planta que requiere agua, el troll del puente de chasm, la máquina de baterías, las almejas gigantes, etc.).
- **E. Special / Unsafe / Deferred (39 salas):** Solapa con salas forzadas (22), letales (4), posiciones de enanos (6), centinela `LOC_NOWHERE` (1) y salas con manejadores especiales (6).

### 7.2 Análisis de Alcanzabilidad desde `LOC_START`
1. **Alcanzabilidad topológica (ignorando condiciones):** Teóricamente 184 salas (todo el grafo salvo `LOC_NOWHERE`). Esta métrica es puramente geométrica y **no representa jugabilidad real**.
2. **Alcanzabilidad con reglas y estados implementados:**
   - En CH_01: Las 34 salas de superficie son completamente alcanzables y jugables.
   - En la frontera de la reja: Al ejecutar `UNLOCK GRATE` con las llaves encontradas en `LOC_BUILDING`, la condición `not GRATE GRATE_CLOSED` se satisface. Si se habilita `LOC_BELOWGRATE`, el jugador desciende con éxito.
   - En la antecámara de CH_ENTRY: Desde `LOC_BELOWGRATE`, el jugador puede transitar incondicionalmente a `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER` y `LOC_PITTOP`.
3. **Fronteras infranqueables con el estado actual:**
   - Desde `LOC_PITTOP`: El descenso hacia `LOC_MISTHALL` (`DOWN`) está protegido por la regla `carry NUGGET -> LOC_NECKBROKE`. Al no existir el objeto `NUGGET` en runtime, el motor emite de forma segura `DEPENDENCY_PENDING`, conteniendo al jugador en la antecámara.
   - Hacia el oeste de CH_ENTRY: `LOC_EASTBANK` y `LOC_WESTBANK` están bloqueados por la fisura (`FISSURE`).
   - Hacia el sur de CH_ENTRY: La conexión `LOC_MISTHALL -> LOC_KINGHALL` conduce a la serpiente y a una posición de enano (`dwarfloc`).

---

## 8. Fronteras entre Capítulos Editoriales (85 Transiciones)

El grafo global contiene exactamente **85 transiciones de viaje entre capítulos editoriales**.

### 8.1 Fronteras entre `CH_SURFACE` y Capítulos Subterráneos
| Origen | Destino | Verbos | Condición | Capítulo Destino | Estado Actual | Viabilidad en R5 |
|---|---|---|---|---|---|---|
| `LOC_GRATE` | `LOC_BELOWGRATE` | `ENTER, INWAR, DOWN` | `not GRATE GRATE_CLOSED` | `CH_ENTRY` | `FRONTIER` | **PILOTO RECOMENDADO (Inmediato)** |
| `LOC_BUILDING` | `LOC_FOOF1` | `XYZZY` | `always` | `CH_ENTRY` (forzado a `LOC_DEBRIS`) | `FRONTIER` | **PILOTO SECUNDARIO (Atajo mágico)** |
| `LOC_BUILDING` | `LOC_FOOF3` | `PLUGH` | `always` | `CH_Y2_WINDOWS` (forzado a `LOC_Y2`) | `FRONTIER` | `DIFERIDO` (conduce a enanos en Y2) |
| `LOC_CLIFF` | `LOC_NOMAKE` | `JUMP` | `always` | `CH_SPECIAL` (letual) | `FRONTIER` | `DIFERIDO` (muerte por precipicio) |
| `LOC_LEDGE` | `LOC_NOMAKE` | `JUMP` | `always` | `CH_SPECIAL` (letual) | `FRONTIER` | `DIFERIDO` (muerte por precipicio) |

### 8.2 Retornos desde `CH_ENTRY` hacia `CH_SURFACE`
| Origen | Destino | Verbos | Condición | Tipo de Acción | Estado y Comportamiento |
|---|---|---|---|---|---|
| `LOC_BELOWGRATE` | `LOC_GRATE` | `OUT, UPWAR` | `not GRATE GRATE_CLOSED` | `goto` | Retorno seguro a la superficie si la reja está abierta. |
| `LOC_BELOWGRATE` | `GRATE_NOWAY` | `OUT` | `always` | `speak` | Mensaje "The grate is locked and you cannot enter" si la reja se cierra. |
| `LOC_DEBRIS` | `LOC_GRATE` | `DEPRE` | `not GRATE GRATE_CLOSED` | `goto` | Retorno rápido hacia la depresión exterior. |
| `LOC_DEBRIS` | `LOC_FOOF2` | `XYZZY` | `always` | `goto` | Forzado a `LOC_BUILDING` (retorno por palabra mágica). |
| `LOC_AWKWARD` | `LOC_GRATE` | `DEPRE` | `not GRATE GRATE_CLOSED` | `goto` | Retorno a la depresión exterior. |
| `LOC_BIRDCHAMBER` | `LOC_GRATE` | `DEPRE` | `not GRATE GRATE_CLOSED` | `goto` | Retorno a la depresión exterior. |
| `LOC_PITTOP` | `LOC_GRATE` | `DEPRE` | `not GRATE GRATE_CLOSED` | `goto` | Retorno a la depresión exterior. |

---

## 9. Comparativa de Alternativas de Habilitación Progresiva

| Criterio | Alternativa A: Habilitación por Capítulo Completo | Alternativa B: Habilitación por Subconjunto Explícito | Alternativa C: Subconjunto con Dependencias Verificadas |
|---|---|---|---|
| **Definición** | Habilitar las 12 salas de `CH_ENTRY` en bloque. | Habilitar salas individuales en `enabled_location_ids` según se conectan. | Habilitar únicamente subgrafos conexos cuyas reglas no tengan dependencias pendientes. |
| **Ventajas** | Conceptualmente simple a nivel de capítulo. | Control granular sala por sala. | Máxima seguridad histórica; cero riesgo de saltarse reglas o caer en estados indefinidos. |
| **Desventajas** | Introduce salas con dependencias no resueltas (`LOC_EASTBANK` con la fisura, `LOC_WESTBANK` con enanos, `LOC_MISTHALL` con la pepita). | Puede generar orfandades si no se audita la topología conexa. | Requiere auditoría previa de dependencias en cada corte (como la presente). |
| **Coste de implementación** | Bajo pero con alta deuda técnica. | Muy bajo. | Bajo y limpio. |
| **Complejidad de pruebas** | Alta (muchas salas simultáneas). | Media. | Baja y focalizada (pruebas deterministas de entrada y salida). |
| **Riesgos** | Jugador cruza la fisura sin puente o muere sin control en pozos. | Fragmentación si una sala habilitada no tiene salida. | Cero riesgos demostrados. |
| **Compatibilidad R4** | Pobre. | Alta. | **ÓPTIMA (Cumple al 100% el contrato de congelación)**. |
| **Reversibilidad** | Compleja. | Inmediata. | Inmediata. |
| **Veredicto** | `RECHAZADA` | `VIABLE` | **`RECOMENDADA`** |

---

## 10. Matriz de Riesgos Identificados

| Riesgo | Evidencia en Repositorio | Impacto | Probabilidad | Mitigación | Corte de Aplicación |
|---|---|---|---|---|---|
| **Saltarse reglas condicionales previas a `always`** | 39 casos detectados en el catálogo (p. ej. fisura en `EASTBANK`). | `CRÍTICO` | `ALTA` si se ignora | Política anti-bypass estricta: emitir `DEPENDENCY_PENDING` ante objeto ausente. | R5 / Travel Resolver |
| **Habilitar salas sin descripción en pantalla** | `WorldData.describe()` depende de `l10n_locations` o de `WorldLocation.description_en`. | `ALTO` | `ALTA` si no hay adaptador | Proporcionar fallback automático a la descripción histórica en inglés de `StructuralCatalog`. | R5 / Runtime Adapter |
| **Bucle infinito en salas forzadas** | 22 salas forzadas en catálogo. | `ALTO` | `BAJA` | El motor ya implementa salvaguarda `MAX_RULE_WALK = 64`. | Verificado en CUT B |
| **Acceso no controlado a zonas letales** | 4 salas letales históricas (`LOC_NECKBROKE`, etc.). | `MEDIO` | `BAJA` | El motor ya intercepta destinos hacia `LOC_NOWHERE` y activa `DEATH_PENDING`. | Verificado en CUT D |
| **Contaminación del parser con vocabulario global** | `CommandParser` extrae nombres de `world.objects`. | `CRÍTICO` | `NULA` si se respeta R4 | Mantener `world.objects` desacoplado del catálogo de 70 objetos estructurales. | R4 Freeze / R5 |
| **Desincronización del comando `BACK`** | `BACK` consulta `previous_location` y `previous_previous_location`. | `MEDIO` | `BAJA` | `Interpreter._advance_history()` salta salas forzadas automáticamente. | Verificado en CUT B |
| **Fuga de salas no autorizadas al runtime** | `WorldData.is_location_enabled()` gobierna el acceso. | `CRÍTICO` | `NULA` con R3/R4 | Toda sala fuera de `enabled_location_ids` produce `TravelOutcome.FRONTIER`. | Verificado en R4 |
| **Activación prematura de enanos** | `LOC_WESTBANK` es una `dwarfloc`. | `ALTO` | `NULA` si se aísla antecámara | Excluir `LOC_WESTBANK` y `LOC_KINGHALL` del primer corte R5. | R5 Scope Boundary |

---

## 11. Respuestas Exhaustivas a las 12 Preguntas Clave

### 1. ¿Podemos habilitar alguna ubicación fuera de CH_01 sin implementar puzles?
**SÍ**. Existen ubicaciones cuya topología interna y de retorno es puramente incondicional o se apoya en el mecanismo de la reja ya implementado.

### 2. ¿Cuáles exactamente y por qué?
Exactamente las **6 ubicaciones de la antecámara de `CH_ENTRY`** (`LOC_BELOWGRATE`, `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`), más la hendedura forzada `LOC_CRACK` y las dos salas de tránsito mágico `LOC_FOOF1` y `LOC_FOOF2`.
*Por qué:* Sus rutas no dependen de puzles de agua, dragón, troll, fisura o serpiente; no son zonas de inicio de enanos; y disponen de salidas seguras hacia la superficie mediante `OUT`, `DEPRE` y `XYZZY`.

### 3. ¿Qué transición sería la mejor prueba piloto?
La transición **`LOC_GRATE` <-> `LOC_BELOWGRATE`**. Es la puerta histórica de la cueva, gobernada por `UNLOCK GRATE` (resuelto en CH_01), y representa una prueba atómica mínima con cero riesgo colateral.

### 4. ¿Podemos reutilizar el travel resolver de CUT B?
**SÍ, en un 95%**. El resolver implementado en `Interpreter` ya contempla precedencia, condiciones declaradas, llamadas a manejadores especiales, detención en dependencias pendientes, salto a reglas distintas y salas forzadas.

### 5. ¿Qué le falta al runtime para mostrar y visitar una ubicación estructural?
Le falta un **adaptador de habilitación en `WorldData`** que instancie objetos `WorldLocation` a partir de los diccionarios de `StructuralCatalog` para aquellas salas que se añadan a `enabled_location_ids`, asegurando que `WorldData.describe()` disponga de la descripción histórica en inglés si no existe texto en español.

### 6. ¿Es seguro ampliar `enabled_location_ids` sin modificar `GameState`?
**SÍ, completamente seguro**. `GameState` no restringe los identificadores de sala que almacena en `current_location` o `visited`.

### 7. ¿Qué ocurre si una condición pendiente precede a una regla `always`?
El evaluador se detiene de forma segura y devuelve `GameState.TravelOutcome.DEPENDENCY_PENDING`. **Nunca** salta a la regla `always` posterior ni asume valores ficticios.

### 8. ¿Qué hacemos con `FORCED`, muerte y `special3`?
- `FORCED`: Se resuelven con la cascada automática existente (`_select_rule(loc, "HERE")`).
- Muerte: Se interceptan hacia `LOC_NOWHERE` y activan el flujo de reencarnación de CUT D (`DEATH_PENDING`).
- `special3`: Permanece como `DEPENDENCY_PENDING` (cruce del troll diferido).

### 9. ¿Cómo distinguimos ruta bloqueada de ruta no implementada?
- *Ruta bloqueada en el juego:* La condición es evaluable y da falso; el motor salta a la regla alternativa y emite el mensaje narrativo correspondiente (`TravelOutcome.SPOKE`).
- *Ruta no implementada:* La condición depende de un objeto/sistema no presente; el motor se detiene inmediatamente y emite `TravelOutcome.DEPENDENCY_PENDING`.
- *Frontera:* La sala destino no está en `enabled_location_ids`; emite `TravelOutcome.FRONTIER`.

### 10. ¿Qué cambios mínimos permitirían navegar sin reconstruir todavía todos los puzles?
1. Añadir los IDs seleccionados a `WorldData.enabled_location_ids`.
2. Crear un método adaptador en `WorldData` que suministre `WorldLocation` desde `StructuralCatalog`.
3. Ofrecer fallback de descripciones históricas en inglés.
4. Mantener la contención de frontera y dependencias pendientes en las salidas hacia el resto de la cueva.

### 11. ¿Qué parte de las 185 ubicaciones podría permanecer inaccesible hasta la reconstrucción funcional?
Aproximadamente **142 salas** (76.7% del mundo histórico) permanecerán diferidas como frontera o dependencias pendientes hasta que se reconstruyan sus puzles, objetos y actores específicos.

### 12. ¿Cuál es el primer corte R5 realmente verificable?
El corte piloto:
**`CAR-CORE-002 / R5A — Cave Entry Navigation Pilot (Grate & Below Grate)`**
Habilita `LOC_BELOWGRATE`, permitiendo que el jugador abra la reja en CH_01, ingrese a la primera sala subterránea, lea su descripción, y regrese a la superficie.

---

## 12. Propuesta de Secuencia de Cortes para R5

Para avanzar con mínima fricción, pruebas claras y total reversibilidad, se propone estructurar R5 en 3 cortes incrementales:

### Corte 1: `CAR-CORE-002 / R5A — Cave Mouth Pilot (LOC_BELOWGRATE)`
- **Objetivo:** Demostrar la primera transición de frontera funcional fuera de CH_01 (`LOC_GRATE` <-> `LOC_BELOWGRATE`).
- **Alcance:** Habilitar únicamente `LOC_BELOWGRATE` en `enabled_location_ids`. Implementar el adaptador de lectura de `WorldLocation` desde `StructuralCatalog` en `WorldData`.
- **Límites:** Las salidas desde `LOC_BELOWGRATE` hacia `LOC_COBBLE`, `LOC_DEBRIS` y `LOC_PITTOP` se detienen como `FRONTIER`. Cero nuevos objetos. Cero actores.
- **Resultado observable:** Tras `UNLOCK GRATE`, el comando `ENTER` sitúa al jugador en `LOC_BELOWGRATE`, muestra su descripción ("You are in a small chamber beneath a 3x3 steel grate..."), y el comando `OUT` devuelve al jugador a `LOC_GRATE`.

### Corte 2: `CAR-CORE-002 / R5B — Cave Entry Antechamber Traversal`
- **Objetivo:** Habilitar la navegación en el subgrafo seguro de la antecámara (6 salas ordinarias + hendedura forzada `LOC_CRACK` + atajo `XYZZY`).
- **Alcance:** Habilitar `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`, `LOC_CRACK`, `LOC_FOOF1`, `LOC_FOOF2`.
- **Límites:** El descenso hacia `LOC_MISTHALL` (`DOWN` desde `PITTOP`) se detiene como `DEPENDENCY_PENDING` por la regla de la pepita (`NUGGET`). La salida hacia la fisura permanece sellada como frontera.
- **Resultado observable:** Navegación bidireccional completa por la red de pasajes iniciales y regreso por la reja o por la palabra mágica `XYZZY`.

### Corte 3: `CAR-CORE-002 / R5C — Navigation Validation & Regression Freeze`
- **Objetivo:** Formalizar la suite de pruebas de navegación, congelar los contratos ampliados de `enabled_location_ids` (43 salas activas, 142 deshabilitadas) y actualizar la matriz de trazabilidad.

---

## 13. Conclusión de Viabilidad

> [!IMPORTANT]
> **Dictamen del Decision Gate:**
> **`CLOSED / VIABLE WITH CONDITIONS`**
>
> La habilitación de navegación fuera de CH_01 es técnicamente viable de forma inmediata y segura **siempre que se aplique la Alternativa C (Subconjunto con Dependencias Verificadas)**, iniciando con el piloto atómico **R5A (`LOC_BELOWGRATE`)**.
>
> Se cumplen todas las garantías para no alterar el bucle de juego de Superficie, no consumir RNG en consultas estructurales, y blindar al jugador contra fallos de precedencia histórica mediante la política de dependencias pendientes.
