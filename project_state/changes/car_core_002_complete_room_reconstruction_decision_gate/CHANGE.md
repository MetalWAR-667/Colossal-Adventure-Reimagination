# CAR-CORE-002 — Complete Historical Room Reconstruction / Decision Gate

**Estado:** CLOSED / DECISION GATE — VIABLE WITH CONDITIONS

**Fecha:** 2026-10-25

**Baseline inspeccionado:** `29359ffee6d50956ec3877cdffc93a618558c0dd`

**Tipo:** investigación y documentación; sin implementación

## A. Decisión

La reconstrucción estructural completa de las 185 localizaciones históricas es **VIABLE WITH CONDITIONS** antes de implementar todos los puzles y sistemas globales.

La viabilidad se limita a reconstruir y verificar la geografía, las rutas ordenadas, los tipos de destino, las condiciones sin resolver, las funciones estructurales de las salas y el catálogo estático de objetos. No implica que las salas queden jugables ni que una condición pendiente pueda evaluarse con un valor por defecto.

Condiciones obligatorias:

1. Mantener el YAML como autoridad y generar una única proyección canónica, sin copiar rutas manualmente.
2. Separar explícitamente el grafo histórico global de `enabled_location_ids`, el subconjunto jugable.
3. Preservar orden, tipo de destino y condición de cada ruta, aunque la dependencia funcional aún no exista.
4. Representar las dependencias no implementadas como `DEPENDENCY_PENDING`; nunca resolverlas silenciosamente como verdaderas o falsas.
5. Incorporar el catálogo estático completo de objetos —identidad, índice, ubicaciones iniciales y fijas, estados y vocabulario— antes de habilitar lotes de salas.
6. Mantener el vocabulario del parser y los objetos visibles derivados únicamente de la vista funcional habilitada.
7. Conservar la clasificación histórica de salas ordinarias, forzadas, transitorias, letales y nulas.
8. Mantener inactivos actores, RNG histórico, cierre y endgame hasta sus cortes expresamente autorizados.
9. Demostrar que la proyección actual de CH_01 equivale al filtro canónico y que CUT A–D continúan sin regresiones.

## B. Evidencia estructural verificada

### Capítulos y cobertura

`06_reconstruccion_drawio/tools/oa_chapters.py` define once capítulos canónicos. La asignación cubre las 185 localizaciones exactamente una vez, sin duplicados ni fallback:

| Capítulo | Localizaciones |
|---|---:|
| `CH_SURFACE` | 34 |
| `CH_ENTRY` | 12 |
| `CH_CENTRAL` | 18 |
| `CH_MAZE_ALIKE` | 33 |
| `CH_BEDQUILT` | 17 |
| `CH_ORIENTAL_PLOVER` | 12 |
| `CH_RESERVOIR` | 12 |
| `CH_REPOSITORY` | 13 |
| `CH_WITT_DIFFERENT` | 18 |
| `CH_Y2_WINDOWS` | 9 |
| `CH_SPECIAL` | 7 |
| **Total** | **185** |

Las páginas equivalentes de `Open_Adventure_World_V3.drawio` contienen el mismo reparto y su unión cubre los 185 identificadores. La geometría se almacena en elementos `object` con `source_id`; una búsqueda limitada a `mxCell` produciría un falso cero.

El dataset fuente contiene 623 registros de viaje. Sus condiciones son: 574 `always`, 25 `not`, 12 probabilísticas, 7 `carry`, 4 `with` y 1 `nodwarves`. Existen seis destinos especiales: cinco de clases ya modeladas por CUT B y dos apariciones de `special3` asociadas al cruce del troll, todavía dependientes de funcionalidad no implementada.

### Roles y descripciones

El grafo clasifica 162 localizaciones como jugables, 17 especiales, 5 transitorias y 1 nula. `LOC_NOWHERE` carece deliberadamente de descripción larga y `LOC_BUILDING1` conserva una descripción larga vacía procedente de la fuente. No se interpretan como pérdida accidental de datos.

Las banderas globales observadas son: 144 `DEEP`, 50 `NOBACK`, 37 `LIT`, 27 `ALLALIKE`, 22 `FOREST`, 18 `NOARRR`, 12 `ALLDIFFERENT`, 11 `ABOVE`, 10 `FLUID` y 1 `OILY`. Estas banderas forman parte del contrato estructural porque intervienen en iluminación, actores, retroceso y presentación.

### Objetos

La fuente define 70 entradas, incluido el centinela `NO_OBJECT`: 36 portátiles, 33 inmóviles y 1 centinela. Hay 11 objetos con colocación múltiple, 26 con varios estados, 18 inicialmente ausentes o en `LOC_NOWHERE` y 20 tesoros.

Las rutas condicionadas hacen referencia, entre otros, a `CHASM`, `CLAM`, `DOOR`, `DRAGON`, `EMERALD`, `FISSURE`, `GRATE`, `NUGGET`, `OGRE`, `OYSTER`, `PLANT`, `RABBITFOOT`, `RESER`, `SNAKE`, `TROLL` y `VEND`. Por ello no basta con importar nombres: deben preservarse índices estables, ubicaciones primarias y fijas, estados, cambios de descripción y condición de tesoro.

## C. Estado real de la arquitectura

El exportador actual genera dos vistas diferentes:

- `locations` y `objects`: proyección jugable filtrada a `CH_SURFACE`.
- `simulation_graph`: los 185 identificadores ordenados, banderas, 623 viajes y seis ubicaciones iniciales de enanos.

La segunda vista demuestra que los datos globales pueden transportarse sin habilitarlos, pero todavía no contiene descripciones completas, capítulo editorial, geometría Draw.io ni el catálogo completo de objetos.

En runtime, `WorldData.locations` funciona a la vez como catálogo cargado y conjunto habilitado; `is_in_chapter()` comprueba la presencia en ese diccionario. `Interpreter` trata como frontera cualquier destino que no esté en él. `CommandParser` construye el vocabulario de objetos desde `world.objects`. `GameState` crea una única posición mutable a partir de `locations[0]`, por lo que no representa aún la semántica histórica de ubicación fija o múltiple.

Conclusión: cargar directamente las 185 salas y los 70 objetos en los diccionarios actuales haría visibles destinos y palabras antes de tiempo. La ampliación necesita una vista estructural global separada de la vista funcional habilitada; no necesita un segundo `Interpreter` ni un segundo `GameState`.

## D. Dependencias funcionales globales

La inspección de las fuentes históricas confirma que una reconstrucción funcional completa depende de sistemas transversales:

- **Enanos y pirata:** `dwarfmove()` y `spotted_by_pirate()` necesitan rutas globales, `DEEP`, `FORCED`, `NOARRR`, condiciones `nodwarves`, seis posiciones iniciales, estado anterior/visto, tesoros y un RNG compartido.
- **Oscuridad y lámpara:** CUT C cubre el contrato actual, pero la equivalencia global exige banderas de sala, estados de la lámpara y persistencia entre comandos.
- **Muerte y reincarnación:** CUT D cubre las causas autorizadas; las salas letales deben conservarse estructuralmente sin activarse por su mera carga.
- **Movimientos forzados:** CUT B implementa el ciclo básico y `special1/2`; `special3` continúa pendiente.
- **Hints:** necesitan contadores, turnos y predicados sobre sala, actor y objetos.
- **Cierre y endgame:** `closecheck()` depende de relojes, tesoros, `DEEP`, Y2 y estados globales; además mueve al jugador y varios objetos a las salas de repositorio.
- **Puntuación:** depende del catálogo global de tesoros, muerte, cierre, bonus, hints, turnos y estado de Witts End.
- **Acciones entre salas:** dragón/alfombra, almeja/ostra/perla, vending/baterías, troll/puente, planta, urna y palabras mágicas mutan objetos o estados situados en capítulos distintos.

Estas dependencias no bloquean la reconstrucción estructural, pero sí impiden llamar “jugable” o “validado funcionalmente” a una sala solo porque su nodo y sus rutas estén presentes.

## E. Arquitectura mínima propuesta

1. **Proyección estructural canónica generada.** Extender de forma aditiva la proyección existente —o versionarla como `structural_world`— con localizaciones, descripciones, capítulo, rol, banderas, rutas ordenadas, referencias de objetos/hints y geometría. No crear una segunda autoridad paralela al YAML.
2. **Catálogo frente a habilitación.** Añadir un catálogo global (`all_locations`) y un conjunto explícito `enabled_location_ids`. Mantener temporalmente `locations` como vista derivada habilitada para compatibilidad.
3. **Objetos estáticos frente a estado mutable.** Añadir `all_objects` como catálogo estructural y conservar `objects` como vista habilitada del parser/runtime. Cada objeto lógico tendrá una sola identidad mutable en `GameState`; la semántica primaria/fija/múltiple debe modelarse antes de habilitar objetos afectados.
4. **Fronteras tipadas.** Conservar un único intérprete. Las consultas estructurales pueden ver todo el grafo, pero el movimiento solo acepta IDs habilitados y distingue `HISTORICAL_DISABLED`, `FORCED`, `LETHAL`, `SPEAK`, `SPECIAL` y `DEPENDENCY_PENDING`.
5. **Consumidores filtrados.** Parser, mapa jugable, presentación y objetos visibles consumen la vista habilitada. Un visor de depuración global futuro podrá consumir la vista estructural sin convertirla en mundo jugable.

## F. Cortes propuestos, ordenados por dependencia

1. **R1 — Canonical Room Inventory.** Validador determinista y manifiesto documental/tooling: 185 salas, 623 viajes, 70 objetos, once capítulos, cobertura Draw.io exacta, cero duplicados/fallback, destinos resueltos y clasificaciones estables. Sin consumo runtime ni cambios de comportamiento.
2. **R2 — Complete Structural Data Projection.** Exportación aditiva/versionada de la estructura completa y del catálogo estático de objetos; demostrar equivalencia exacta del filtro CH_01 actual.
3. **R3 — Structural Loader & Enabled View.** Cargar el catálogo global en `WorldData` y separar `enabled_location_ids`, manteniendo parser, mapa y juego restringidos a CH_01.
4. **R4 — Structural Validation & Contract Freeze.** Congelar el contrato con pruebas de orden, referencias, filtros y no filtración funcional.
5. **Lotes funcionales posteriores.** Habilitar capítulos solo cuando sus condiciones y objetos requeridos tengan semántica real. Los actores y el RNG histórico requieren su propio gate; cierre/endgame se mantiene posterior.

No se recomienda unir “cargar” y “habilitar” salas en un mismo corte: hacerlo convertiría una reconstrucción de datos en una ampliación jugable incompleta.

## G. Respuestas a los riesgos del gate

1. **¿Puede reconstruirse toda la geografía antes que los puzles?** Sí, como estructura inerte y verificable; no como contenido jugable completo.
2. **¿Pueden conservarse condiciones no implementadas?** Sí, como datos ordenados y tipados. No deben evaluarse.
3. **¿Qué debe existir desde el principio?** IDs e índices estables, orden de rutas, tipos de destino, banderas, roles, referencias de hints y objetos, colocación inicial/fija/múltiple y cruces entre capítulos.
4. **¿Qué bloquea hoy la carga global segura?** La identidad actual entre catálogo y conjunto habilitado, el filtro CH_01 del exportador, una `simulation_graph` incompleta, la primera ubicación única de `GameState`, el vocabulario del parser ligado a objetos cargados y el mapa ligado a CH_01.
5. **¿Qué información de objetos es imprescindible?** Identidad e índice fuente, palabras, portabilidad, ubicaciones primarias/fijas, estados, textos/cambios, tesoro y dependencias de puzles/actores/sistemas globales.
6. **¿Cómo evitar contaminación del parser?** Manteniendo el catálogo global fuera de la vista `objects` habilitada que consume `CommandParser`.
7. **¿Qué ocurre si una condición pendiente se trata como falsa o verdadera?** Falsa puede seleccionar indebidamente la siguiente regla; verdadera puede saltarse un cierre o puzle. Las probabilidades además consumirían RNG. Ambos casos inventan comportamiento.
8. **¿Puede añadirse cierre más tarde?** Sí, si desde ahora se conservan salas de repositorio, objetos afectados y colocaciones completas. De lo contrario exigiría rehacer el modelo.
9. **¿Puede añadirse actores después sin alterar la geografía?** Sí, preservando rutas globales, banderas, orden e IDs. El estado mutable de actores y la paridad exacta del RNG son contratos posteriores.
10. **¿Qué prueba la no regresión?** Conteos canónicos, round-trip y orden por registro, destinos exactos, equivalencia del filtro CH_01, rechazo de salas deshabilitadas, vocabulario y mapa sin cambios, ausencia de estado/RNG de actores y suites CH_01/CUT A–D verdes.

## H. Estado de cortes y verificación

- CAR-CORE-001 CUT A, B, C y D: `CLOSED / PASS` según sus registros y la revalidación actual.
- CUT E: `DEFERRED / NOT AUTHORIZED`; no se ha iniciado.
- CUT F: no existe implementación ni `CHANGE.md` de cierre. Aunque antecedentes de planificación lo mencionaron para CH_02 sin actores, el repositorio no aporta evidencia de comienzo o finalización; CAR-CORE-002 reordena la prioridad hacia el inventario estructural sin autorizar CUT F.
- CH_02: no jugable; su informe continúa siendo reconstrucción/investigación.

Verificación ejecutada con Godot `4.7.2.stable.official.ed1daf0bf` mediante `07_godot_open_adventure/tools/verify.ps1`:

- exportación determinista: PASS;
- CUT A: 10 comprobaciones Python y 12 comprobaciones Godot de aislamiento: PASS;
- suite del juego: 448 comprobaciones: PASS;
- CUT B: 54 comprobaciones: PASS;
- CUT C: 61 comprobaciones: PASS;
- CUT D: 34 comprobaciones: PASS;
- integración de ilustración: 62 comprobaciones: PASS;
- lote artístico: 455 comprobaciones: PASS;
- GRATE: 150 comprobaciones: PASS;
- resultado del script: `ALL CHECKS PASSED`.

Las cifras pertenecen a suites con posibles solapamientos y no se suman como pruebas independientes. No se realizó una nueva validación gráfica humana, porque este gate no cambia runtime ni presentación.

## Recomendación única siguiente

Proponer **CAR-CORE-002 / R1 — Canonical Room Inventory** como primer corte mínimo. Debe limitarse a validación determinista y evidencia generada, sin modificar runtime, habilitar salas, ampliar el parser ni activar sistemas históricos.

**Estado de R1:** `PROPOSED / NOT AUTHORIZED`.
