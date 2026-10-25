# CAR-CORE-001 / CUT C — Darkness, Lamp & Batteries

**Estado:** `CLOSED / PASS`. Fecha: 2026-10-25.
Baseline: `795df5fa0c73068671b1350588439f7de01bc925`, rama `main`, índice y
árbol inicialmente limpios. Autorización humana: CUT C únicamente.

Rectores: [Decision Gate](../car_core_001_decision_gate/CHANGE.md),
[CUT A](../car_core_001_cut_a_global_data_contract/CHANGE.md) y
[CUT B](../car_core_001_cut_b_historical_travel_cycle/CHANGE.md).

## Correspondencia histórica

La oscuridad reproduce `advent.h:IS_DARK_HERE()`: una sala sin `LIT` es
oscura salvo que `LAMP` esté `HERE` —en el suelo de la sala o transportada— y
en estado `LAMP_BRIGHT`. `DEEP` no participa en esa decisión. Los flags ya
exportados se consumen desde `WorldLocation`; `simulation_graph` continúa sin
ser leído por producción.

El ciclo de `main.c:do_command()` se conserva en una sola llamada a
`Interpreter.submit()`: tras aceptar una entrada de una o dos palabras captura
`was_dark` (`wzdark`), incrementa el turno y ejecuta `lampcheck()` antes de
interpretar la orden. Vacíos y entradas de más de dos palabras siguen
rechazándose antes del turno y del consumo. Una cascada HERE no crea otra
entrada, turno ni consumo de energía.

Estado mínimo incorporado a `GameState`:

- `lamp_energy = 330` (`GAMELIMIT`);
- `lamp_warned = false` (`lmwarn`);
- `was_dark = false` (`wzdark`);
- lugar/estado de `BATTERY` en los diccionarios de objetos existentes, con
  `LOC_NOWHERE` / `FRESH_BATTERIES` iniciales.

`BATTERY` no se añade a `WorldData`, al parser, al mapa ni al inventario
jugable de CH_01. Ese estado aislado permite reproducir `lampcheck()` sin abrir
el catálogo global ni CH_02. También se corrige `is_carried()` para que un ID
ausente no se confunda con el sentinela vacío de objeto transportado.

## Visibilidad, lectura y acciones de lámpara

`describe_location()` usa `PITCH_DARK` para una sala ordinaria oscura, no
enumera objetos y no avanza el estado de descripción visible. Una sala FORCED
conserva su descripción propia, aunque los objetos permanecen ocultos. LIGHT y
EXTINGUISH aceptan la lámpara transportada o presente en el suelo; encenderla
desde oscuridad vuelve a describir la sala y apagarla emite `PITCH_DARK` cuando
corresponde. Una lámpara agotada no se puede volver a encender.

`WorldObject` admite los textos por estado que ya posee la fuente. READ
intransitivo resuelve exactamente un objeto legible visible; READ transitivo
rechaza la lectura en oscuridad con `NO_SEE`. CH_01 no incorpora objetos
legibles nuevos: la cobertura usa el texto histórico de `VEND` en un fixture
aislado y no lo habilita en producción.

## Energía y baterías

Constantes verificadas en `advent.h` y `init.c`: aviso a **30** turnos
(`WARNTIME`), vida inicial **330** y recarga **2500** (`BATTERYLIFE`). Si la
lámpara está encendida, cada entrada procesada reduce energía antes de ejecutar
su comando, incluidos LOOK, acciones, órdenes desconocidas y movimientos
rechazados. LIGHT desde apagado no consume ese mismo turno; EXTINGUISH sí
consume antes de apagar.

Con energía menor o igual a 30, `main.c:lampcheck()`:

1. sustituye automáticamente baterías frescas HERE si la lámpara también está
   HERE, marca las baterías `DEAD_BATTERIES`, suma 2500 y limpia el aviso;
2. en otro caso avisa una sola vez con `MISSING_BATTERIES`, `LAMP_DIM` o
   `GET_BATTERIES`, según estado y ubicación;
3. al llegar exactamente a cero fija energía `-1`, apaga la lámpara y emite
   `LAMP_OUT` si está HERE.

Los mensajes proceden del dataset generado; CUT C no inventa narración ni
añade traducciones.

## wzdark, caída y RNG

Como `playermove(LOOK)`, LOOK limpia el snapshot antes del chequeo y no puede
provocar caída. Tras una orden de movimiento, incluida una dirección rechazada
que históricamente todavía alcanza `do_move()`, se evalúa una única vez el
resultado final. Solo hay tirada cuando la ubicación final no es FORCED,
continúa oscura y el snapshot previo también era oscuro. La primera llegada
desde luz, una ubicación iluminada, LOOK, una orden no motriz y la exclusión
FORCED no consumen RNG.

La probabilidad es **35 %** (`PIT_KILL_PROB`). Se conserva el único
`RandomNumberGenerator` de la partida y las pruebas controlan su semilla; no se
introduce el LCG histórico ni se declara paridad exacta de trazas. Una caída
produce `DEATH_PENDING`, `pending_location = LOC_NOWHERE`, razón
`darkness_fall` y conserva la ubicación letal en `oldlc2`. No ejecuta
`croak()`, reincarnación, pérdida de objetos, puntuación ni final de partida;
las entradas posteriores quedan suspendidas para CUT D.

## Evidencia

Godot: `4.7.2.stable.official.ed1daf0bf`.

- `res://tests/test_darkness_lamp.gd`: **61 checks PASS**. Usa ubicaciones y
  viajes identificables de CUT A (`COBBLE`, `DEBRIS`, `AWKWARD`, `PITTOP`,
  `CRACK`, `MISTHALL`) y el texto fuente de `VEND`, todos aislados del mundo
  jugable. Las semillas localizan una muestra menor y otra mayor/igual que 35,
  y comparan el estado del RNG para comprobar tiradas y ausencias de tirada.
- Durante el desarrollo, una condición `LIT` mutada por una prueba contaminó
  fixtures posteriores porque compartían el diccionario JSON. Se aisló cada
  fixture mediante `duplicate(true)`; la ejecución final no conserva
  instrumentación temporal y termina 61/61.
- `verify.ps1`: **ALL CHECKS PASSED**. Exportación determinista e importación
  PASS; 10 tests Python CUT A, 12 checks de aislamiento, 54 CUT B, 61 CUT C,
  448 del juego, 62 de integración, 455 del lote artístico y 150 de GRATE,
  todos PASS. Las suites se informan separadas y no se suman como pruebas
  independientes.
- `git diff --check`: PASS; solo avisos normales LF/CRLF del checkout.
- No se realizó una validación gráfica humana nueva: el corte modifica
  semántica de núcleo y se validó headless con las regresiones existentes.

## Fronteras y dependencias pendientes

No se modifican YAML, dataset, exportador, parser, UI, arte, reglas históricas,
mapa ni fuentes C. `WorldData` conserva 34 salas y ocho objetos jugables; los
151 IDs globales no jugables siguen aislados. CH_02 permanece cerrado.

`CUT D — PROPOSED / NOT AUTHORIZED`: consumo de `DEATH_PENDING`, `croak()`,
obituarios, vidas, reincarnación, caída de inventario y puntuación. Enanos,
pirata y actores siguen reservados a CUT E; CH_02 jugable, a CUT F. La paridad
global de secuencias RNG continúa fuera de alcance.

## Inventario exacto

1. `07_godot_open_adventure/godot/src/core/game_state.gd`
2. `07_godot_open_adventure/godot/src/core/interpreter.gd`
3. `07_godot_open_adventure/godot/src/core/world_object.gd`
4. `07_godot_open_adventure/godot/tests/test_darkness_lamp.gd`
5. `07_godot_open_adventure/godot/tests/test_darkness_lamp.gd.uid`
6. `07_godot_open_adventure/tools/verify.ps1`
7. `project_state/CURRENT_STATE.md`
8. Este `CHANGE.md`.

Finalización CAR-AUTO-001: inventario explícito, commit local y sincronización
verificada a Drive. **NO PUSH.**
