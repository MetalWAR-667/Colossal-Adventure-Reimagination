# CAR-CORE-001 / CUT D — Historical Death & Reincarnation

Estado: **CLOSED / PASS**
Baseline: `c6a01bade6c0efb57a66f93a7ff9a395a08d9a85`
Fecha: 2026-10-25

## Resultado

CUT D consume en el único `Interpreter` los resultados `DEATH_PENDING` que ya
producían CUT B y CUT C. La muerte entra en un estado explícito de diálogo, se
cuenta una sola vez, conserva causa y localización diagnósticas y no se trata
como un movimiento ordinario a `LOC_NOWHERE`. Mientras se espera la respuesta
de reincarnación no se ejecuta el parser normal ni se consumen turnos, energía
de lámpara o tiradas RNG.

La implementación se limita al ciclo histórico de muerte. No añade causas de
muerte, actores, salas jugables, cierre de cueva, SAVE/LOAD ni servicios
externos. CUT E y CUT F continúan sin autorización.

## Fuente histórica verificada

- `codigo_fuente_open_adventure/main.c:476-531`, `croak()`: selección del
  obituario por `game.numdie`, incremento único, rama `closng`, diálogo,
  destrucción de líquidos, tratamiento especial de la lámpara, depósito de
  objetos en `oldlc2` y retorno de `oldloc/loc/newloc` a `LOC_BUILDING`.
- `codigo_fuente_open_adventure/misc.c:275-375`, `silent_yes_or_no()` y
  `yes_or_no()`: la respuesta se lee fuera del parser de órdenes, no incrementa
  turnos, acepta el primer token por prefijo `y`/`yes` o `n`/`no`, y ante una
  entrada vacía o inválida emite `PLEASE_ANSWER` y repite la pregunta.
- `codigo_fuente_open_adventure/score.c:63-70`: contribución de supervivencia
  `(NDEATHS - game.numdie) * 10`.
- `codigo_fuente_open_adventure/advent.h:179-218`: `closng`, `numdie`, `loc`,
  `newloc`, `oldloc` y `oldlc2`.
- `06_reconstruccion_drawio/Open_Adventure.yaml:3943-3964`: tres obituarios en
  orden, con sus preguntas y respuestas afirmativas. `NDEATHS` resulta 3:
  existen como máximo dos reincarnaciones.

## Contrato runtime

`GameState.SessionPhase` distingue `PLAYING`, `REINCARNATION_PENDING` y
`FINISHED`. `death_count`, `last_death_cause` y `last_death_location` mantienen
el estado histórico y el diagnóstico. `cave_closing` es únicamente el contrato
booleano mínimo requerido para reproducir y probar la rama de `croak()`; CUT D
no implementa relojes ni cierre de la cueva.

Al consumir una muerte:

1. Se captura la causa tipada y la localización letal.
2. Se incrementa `death_count` una vez.
3. Si `cave_closing` está activo, se emite `DEATH_CLOSING` y termina la partida
   sin pregunta.
4. En otro caso se muestra el obituario correspondiente y se espera una
   respuesta fuera del parser ordinario.
5. Una respuesta negativa termina sin mutar el inventario. En la tercera
   muerte, incluso una respuesta afirmativa muestra la tercera respuesta y
   termina, como en `croak()`.

Una reincarnación aceptada antes del límite destruye WATER/OIL cuando existen,
vacía el estado equivalente de la botella de CH_01, apaga y deja una lámpara
transportada en `LOC_START`, y deposita los demás objetos transportados en
`oldlc2` sin cambiar sus propiedades. La energía y las baterías no se reinician.
El jugador vuelve a `LOC_BUILDING`; `oldloc`, `loc` y `newloc` quedan
representados por `previous_location`, `current_location` y `pending_location`
en BUILDING, mientras `previous_previous_location` conserva el punto de
depósito. Así BACK no escapa hacia la muerte anterior.

Los tres obituarios se exportan determinísticamente desde el YAML en una
proyección estática `historical_runtime`, separada de las salas y objetos
jugables y de `simulation_graph`. El test de aislamiento elimina ambas
proyecciones antes de comprobar el hash histórico del contrato jugable; dicho
hash permanece intacto. No se abrió el catálogo global mutable reservado a
CUT E.

## Puntuación

`Interpreter._score()` usa ahora `max(NDEATHS - death_count, 0) * 10`. Las
contribuciones de supervivencia verificadas son 30, 20, 10 y 0 puntos para
cero, una, dos y tres muertes. Las categorías existentes de tesoros y redondeo
no cambian. No se añadió clasificación, high score ni puntuación online.

## Verificación ejecutada

Godot: `4.7.2.stable.official.ed1daf0bf`.

- Exportación determinista y correspondencia YAML → JSON: PASS.
- CUT A Python: 10 tests PASS, incluido el hash jugable pre-CUT-A.
- Importación Godot: PASS.
- CUT A aislamiento: 12 checks PASS; 151 IDs solo de simulación.
- CUT B viaje histórico: 54 checks PASS.
- CUT C oscuridad/lámpara: 61 checks PASS.
- CUT D muerte/reincarnación: 34 checks PASS.
- Juego CH_01: 448 checks PASS.
- Integración de ilustración/runtime: 62 checks PASS.
- Arte CH_01: 455 checks PASS.
- GRATE: 150 checks PASS.
- `verify.ps1`: `ALL CHECKS PASSED`.
- `git diff --check`: PASS antes de finalizar.

Las cifras pertenecen a suites distintas y no se suman como pruebas
independientes. No se realizó una nueva validación gráfica humana: las suites
gráficas headless existentes sí pasaron, pero CUT D no añade interfaz ni arte.

## Inventario del corte

1. `07_godot_open_adventure/godot/data/chapter_01_surface.json`
2. `07_godot_open_adventure/godot/src/core/game_state.gd`
3. `07_godot_open_adventure/godot/src/core/interpreter.gd`
4. `07_godot_open_adventure/godot/src/core/world_data.gd`
5. `07_godot_open_adventure/godot/tests/test_death_reincarnation.gd`
6. `07_godot_open_adventure/godot/tests/test_death_reincarnation.gd.uid`
7. `07_godot_open_adventure/tools/oa_export_godot.py`
8. `07_godot_open_adventure/tools/test_simulation_graph.py`
9. `07_godot_open_adventure/tools/verify.ps1`
10. `project_state/CURRENT_STATE.md`
11. `project_state/changes/car_core_001_cut_d_historical_death_reincarnation/CHANGE.md`

## Límites y siguiente corte

- La rama de cueva cerrándose está representada y probada mediante fixture;
  los relojes y el endgame completo siguen fuera de alcance.
- Los obituarios se muestran con el texto histórico del YAML; no se añadió una
  traducción nueva en este corte.
- CUT E (enanos, pirata y actores) permanece **PROPOSED / NOT AUTHORIZED**.
- CUT F y CH_02 jugable permanecen **PROPOSED / NOT AUTHORIZED**.
- No se hizo push.
