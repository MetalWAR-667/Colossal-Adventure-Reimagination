# CAR-CORE-001 / CUT B — Historical Travel Cycle

**Estado:** `CLOSED / PASS`. Fecha: 2026-10-25.
Baseline: `d95d508c731c61a133023fb439e92cf45a49cb17`, rama `main`, índice y
árbol inicialmente limpios. Autorización humana: CUT B únicamente.
Rectores: [Decision Gate](../car_core_001_decision_gate/CHANGE.md) y
[CUT A](../car_core_001_cut_a_global_data_contract/CHANGE.md), sin reescribirlos.

## Ciclo y correspondencia histórica

`Interpreter.submit()` conserva el único intérprete, parser, GameState y RNG.
Cada entrada aceptada consume un turno antes de ejecutarse, incluidos LOOK,
acciones, desconocidos y movimientos rechazados. Como en
`misc.c:get_command_input()` y `main.c:do_command()`, líneas vacías o con más de
dos palabras se rechazan antes de incrementar. La cuenta usa las palabras de
entrada, no elimina puntuación mediante el parser para decidir si hubo entrada.
Los comandos UI escritos también cuentan; TAB no pasa por submit y no cuenta.

`playermove()` de [main.c](../../../codigo_fuente_open_adventure/main.c)
(575–870) gobierna selección, alternativas, BACK e historial. El ciclo conserva
el orden fuente y la equivalencia de `traveleq()` (condición, tipo y destino):
fallar una condición salta solo entradas equivalentes, sin rematchear el verbo
de cada alternativa. BACK selecciona una ruta fuente y reevalúa sus condiciones
y especiales; ya no teletransporta a `previous_location`. NOBACK y los fallos
ordinarios conservan el orden histórico de actualización de historial.

`TravelRule` distingue GOTO, SPEAK y SPECIAL; los números 1/2/3 no se interpretan
como IDs de salas. `WorldLocation.is_forced()` deriva HERE implícito de verbos
vacíos, según `make_dungeon.py` e `init.c:initialise()` (46–52). Se verificó la
derivación contra los 185 registros fuente de CUT A, incluida la descripción
vacía de LOC_BUILDING1. No se consume simulation_graph desde código productivo.

El despacho sigue el orden `do_move()` → descripción → `do_command()`:
al admitir un GOTO se actualiza la ubicación y se describe. Si es FORCED se
evalúa HERE y continúa la cascada sin nueva entrada ni turno. SPEAK imprime un
mensaje y conserva ubicación. Un presupuesto de 64 despachos devuelve
`CYCLE_ERROR` con razón diagnóstica ante una cascada anómala; no declara éxito
ni omite silenciosamente eslabones. Alternativas ausentes o tipos desconocidos
también se diagnostican.

Estado nuevo mínimo: `previous_previous_location` (oldlc2), `pending_location`
(newloc), `travel_outcome` tipado y `travel_dependency`. `previous_location`
continúa representando oldloc. El historial se desplaza al solicitar movimiento,
incluido HERE, antes de resolverlo. `move_to(..., false)` evita duplicar ese
desplazamiento al confirmar la llegada; su forma existente conserva su valor
por defecto para llamadas explícitas. El reset mantiene la cadena vacía como
sentinela de historial inexistente.

## Especiales y dependencias explícitas

- **1, pasaje Plover/Alcove:** permite carga vacía o solo EMERALD; otra carga
  produce MUST_DROP sin desplazamiento. El destino sigue sujeto a la frontera.
- **2, transporte Plover:** con estado EMERALD disponible, lo deja en el origen
  y continúa desde la siguiente fila distinta, reevaluando condiciones. La
  prueba recorre PLOVER → FOOF6 → Y2 con un solo input. Si falta el objeto
  global requerido, devuelve `DEPENDENCY_PENDING`, sin fingir su estado.
- **3, puente del troll:** se reconoce, pero su ejecución completa permanece
  pendiente del estado de objetos globales con colocación múltiple/fija
  TROLL/TROLL2/CHASM/BEAR y de muerte. Devuelve `DEPENDENCY_PENDING` con la razón
  explícita, sin fabricar cruce, pago, destrucción de puente o mutaciones
  parciales. No se declara equivalencia funcional del puzzle del puente.
- **Muerte:** tras un transitorio FORCED autorizado que conduce a LOC_NOWHERE,
  `DEATH_PENDING` conserva la última ubicación ingresada, oldloc/oldlc2 y el
  destino pendiente NOWHERE. Suspende antes de consumar la muerte: no ejecuta
  croak, pierde objetos, resta puntuación, termina ni reincarna. Las nuevas
  entradas quedan suspendidas ante muerte, dependencia o error pendientes.
- **Condiciones globales ausentes:** se señalan como dependencia; un objeto
  inexistente no se toma artificialmente como transportado por el sentinela
  vacío del estado actual.

El RNG existente conserva algoritmo y semilla; no se afirma paridad de trazas
con el LCG histórico. `nodwarves` usa la tirada PCT(100) del jugador, mientras
que su exclusión de actores sigue reservada a CUT E. Oscuridad/lámpara y sus
caídas son CUT C; croak/reincarnación, CUT D; estado global y actores, CUT E.
El especial 3 necesita esos contratos antes de poder completarse. CUT C sigue
**PROPOSED / NOT AUTHORIZED**; D–F tampoco se abren.

## Compatibilidad y frontera

WorldData sigue leyendo solo las ubicaciones jugables existentes. No se cambia
exportador, dataset ni grafo global de CUT A. La prueba de aislamiento mantiene
los 151 IDs globales no jugables excluidos de acceso, descripciones y mapa.
ENTER en la reja abierta sigue siendo frontera. No se añaden vocabulario,
objetos o localizaciones a la aplicación productiva.

Diferencias deliberadas frente al núcleo anterior: turnos por entrada en lugar
de por movimiento exitoso; SEWER retorna automáticamente a BUILDING; BACK
respeta rutas y restricciones. La expectativa antigua de SEWER en run_tests y
la expectativa de LOOK sin turno en el test de integración se actualizaron sin
eliminar comprobaciones: se mantienen sus conteos 448 y 62.

## Evidencia de pruebas

Godot: `4.7.2.stable.official.ed1daf0bf`.

- Caracterización previa a editar el núcleo: **6 checks PASS** (LOOK,
  desconocido, vacío y NE rechazado no incrementaban turno; E sí; SEWER
  esperaba otra orden). El primer borrador usó UP como rechazo; se corrigió
  porque la fuente sí permite esa ruta desde START.
- `res://tests/test_travel_cycle.gd`: **54 checks PASS**, con fixtures de CRACK,
  DOME, NECKBROKE, NOMAKE, WESTPIT/BUILDING1/NOCLIMB, PLOVER/ALCOVE/FOOF6/Y2,
  chasmas y LONGWEST. Se construyen únicamente en el test desde registros
  fuente del grafo, normalizando verbos como hace WorldData; nunca habilitan
  CH_02. Dos fixtures alteran deliberadamente una fila para probar equivalencia
  y ciclo anómalo, sin afirmar que esas mutaciones sean rutas históricas.
- Se corrigieron durante la ejecución la normalización omitida de los verbos
  de fixtures y un Array de respuesta sin tipo en la rama de dependencia.
  Los resultados finales focales no presentan SCRIPT ERROR.
- `verify.ps1` con ruta absoluta a Godot: exportación/importación PASS;
  **10 tests Python CUT A**, **12 checks de aislamiento**, **448 del juego**,
  **62 de integración**, **455 del lote artístico** y **150 de GRATE**, PASS.
  La nueva suite focal forma parte del mismo verificador. No se suman suites
  solapadas como pruebas independientes.
- `git diff --check`: PASS. Sin nuevas pruebas gráficas/humanas; no se modifica
  presentación y el verificador conserva las regresiones headless existentes.

## Inventario exacto y finalización

1. `07_godot_open_adventure/godot/src/core/interpreter.gd`
2. `07_godot_open_adventure/godot/src/core/game_state.gd`
3. `07_godot_open_adventure/godot/src/core/travel_rule.gd`
4. `07_godot_open_adventure/godot/src/core/world_location.gd`
5. `07_godot_open_adventure/godot/tests/run_tests.gd`
6. `07_godot_open_adventure/godot/tests/test_runtime_illustration.gd`
7. `07_godot_open_adventure/godot/tests/test_travel_cycle.gd`
8. `07_godot_open_adventure/godot/tests/test_travel_cycle.gd.uid`
9. `07_godot_open_adventure/tools/verify.ps1`
10. `project_state/CURRENT_STATE.md`
11. Este `CHANGE.md`.

CAR-AUTO-001: inventario explícito, preflight, commit local y sincronización
verificada a Drive. **NO PUSH.** El resultado Git/Drive se entrega al finalizar.
CH_02 permanece cerrado. Ninguna dependencia pendiente se presenta como
implementación de iluminación, muerte, actores o catálogo global mutable.
