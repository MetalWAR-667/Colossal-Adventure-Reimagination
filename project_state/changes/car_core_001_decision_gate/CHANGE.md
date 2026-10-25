# CAR-CORE-001 — Historical Runtime Dependencies / Decision Gate

Estado: **INVESTIGACIÓN COMPLETADA / IMPLEMENTACIÓN NO AUTORIZADA**
Repositorio observado: `C:\remake\Colossal-Adventure-Reimagination-public`, rama `main`, HEAD `8dd5b7d4c4a357620167e8f200aa87beca6cd261`.

## Decisión

Es viable mantener un subconjunto de salas jugables separado de un grafo histórico completo, generado desde el mismo YAML y usado solo por la simulación de actores. `dwarfmove()` necesita datos de habitaciones y viajes de capítulos posteriores para reproducir las elecciones de ruta de los enanos y el pirata; no necesita sus descripciones, parser, acciones ni interfaz. Por tanto, cargar ese grafo no hace jugables esos capítulos. El límite debe estar en las ubicaciones que el movimiento del jugador acepta, no en los datos que el subsistema de actores puede consultar.

Esta conclusión corrige el bloqueo arquitectónico del informe previo [RECONSTRUCTION_CH02.md](../../../07_godot_open_adventure/reports/RECONSTRUCTION_CH02.md:53): el grafo recortado no basta para simular los actores fielmente, pero la alternativa no es hacer jugable el grafo completo; es mantener dos proyecciones de datos con consumidores distintos.

## Hechos verificados

### Fuentes y tamaño

- **Observado:** `06_reconstruccion_drawio/Open_Adventure.yaml` contiene 185 ubicaciones, 623 registros de viaje, 70 objetos, una regla marcada `nodwarves` y tres obituarios. El YAML enumera seis posiciones iniciales en `dwarflocs` (líneas 2846–2852). `oa_chapters.py` define `CH_ENTRY` como partición editorial de 12 salas (líneas 23–25, 75–80); no es un límite de datos del juego.
- **Observado:** la única salida actual del exportador se recorta mediante `chapter_members(CHAPTER_ID)` y `build_locations(ir, member_ids)`; solo las ubicaciones miembro entran en el dataset ( [oa_export_godot.py](../../../07_godot_open_adventure/tools/oa_export_godot.py:185), [build_dataset](../../../07_godot_open_adventure/tools/oa_export_godot.py:299) ). Los objetos también se omiten si ninguno de sus lugares iniciales pertenece a ese subconjunto (líneas 162–182). Las condiciones se normalizan, pero `nodwarves` queda como condición de viaje genérica.
- **Observado:** `WorldData` guarda ubicaciones, objetos, viajes, mapa y frontera de un dataset; `is_in_chapter()` comprueba pertenencia a `locations` ([world_data.gd](../../../07_godot_open_adventure/godot/src/core/world_data.gd:18), [líneas 62–87 y 145–157](../../../07_godot_open_adventure/godot/src/core/world_data.gd:62)). `Interpreter._execute_move()` rechaza destinos fuera de ese diccionario antes de llamar `state.move_to()` ([interpreter.gd](../../../07_godot_open_adventure/godot/src/core/interpreter.gd:128)). Esta es una frontera existente reutilizable.
- **Observado:** el estado actual es de una partida por instancia de `Interpreter`: su constructor crea un `GameState`, reinicia desde `WorldData` y mantiene un único RNG; `GameState` contiene ubicación actual/anterior, objetos, turno y fin de partida, pero no actores, estados de oscuridad, vida de lámpara o flujo de reincarnación ([interpreter.gd](../../../07_godot_open_adventure/godot/src/core/interpreter.gd:9), [game_state.gd](../../../07_godot_open_adventure/godot/src/core/game_state.gd:8)). No hay motivo de arquitectura para crear un segundo intérprete o estado.

### Enanos y pirata

- **Observado:** `dwarfmove()` retorna sin actividad si el jugador está en `LOC_NOWHERE`, en una ubicación forzada o si el destino tiene `NOARRR` (`main.c:312–331`). Con `dflag == 0`, alcanzar una ubicación `DEEP` fija `dflag=1` y retorna (`335–340`). El primer encuentro ocurre en una llamada posterior elegible: se aplican las tiradas 95% y, en `NOBACK`, 85%; el nivel pasa a 2, puede eliminar 0–2 de los primeros cinco actores, reubica solapamientos a `DALTLC` (`LOC_NUGGET`), anuncia la aparición y deja el hacha (`342–368`). `advent.h:198–204` documenta los niveles 0–3.
- **Observado:** el YAML inicializa cinco enanos y un sexto actor pirata en `LOC_KINGHALL`, `LOC_WESTBANK`, `LOC_Y2`, `LOC_ALIKE3`, `LOC_COMPLEX` y `LOC_MAZEEND12`. Solo `LOC_WESTBANK` está en `CH_ENTRY`; las otras posiciones están en particiones posteriores. La lista completa no puede sustituirse por un grafo CH_02 sin alterar su recorrido.
- **Observado:** cada actor examina, en orden, los viajes de su ubicación y considera únicamente destinos `goto` que sean `DEEP`, distintos del antiguo y actual, no duplicados contiguos, no forzados y no prohibidos al pirata; excluye además la regla `nodwarves` (`main.c:371–423`). La condición de viaje ordinaria no se evalúa en este algoritmo: el actor consume destinos estáticos de rutas, no la decisión del movimiento del jugador. Si no hay alternativa, usa su ubicación previa. Seen/co-localización, bloqueo, ataque, precisión creciente y muerte se procesan en `424–473`.
- **Observado:** la ruta y el resultado aleatorio dependen del orden de los registros, `DEEP`, `FORCED`, `NOARRR`, el marcador `nodwarves`, posiciones anterior/actual y una secuencia RNG compartida. El original usa LCG con `A=1093`, `C=221587`, `M=1048576`, inicializado en `misc.c:750–776`, y semilla inicial aleatoria desde `init.c:34–36`. Un RNG distinto o consumo distinto de tiradas no garantiza paridad histórica; el objetivo debe fijar explícitamente si se persigue reproducción exacta de secuencias o equivalencia estadística. No hay determinismo entre partidas en el binario fuente sin fijar semilla.
- **Observado:** el pirata usa estado global adicional. `spotted_by_pirate()` consulta `game.chloc/chloc2`, hallazgo del cofre, `tally`, ubicación y luz de lámpara, recorre **todos** los objetos marcados tesoro y sus ubicaciones/estados, y puede mover cofre, mensaje y pirata y robar tesoros cargados (`main.c:231–309`). `throwit()` también altera actor, `seen` y `dkill` (`actions.c:1268–1329`).
- **Inferencia:** es suficiente para el **movimiento** de actores exportar todas las ubicaciones con sus flags relevantes y la secuencia de destinos de viaje con tipo y `nodwarves`, más las seis posiciones iniciales. Para el comportamiento completo del pirata hace falta además un catálogo global estático de tesoros/ubicaciones de origen y estado mutable global de sus objetos, cofre y tally. No se requieren descripciones ni gramática de capítulos no jugables para ello.

### Oscuridad y lámpara

- **Observado:** `IS_DARK_HERE()` da oscuridad si la sala no tiene el bit `LIT` y la lámpara está apagada o no está `HERE` (`advent.h:123–125`). `describe_location()` sustituye la descripción por `PITCH_DARK` en sala oscura no forzada (`main.c:534–545`); `listobjects()` no lista objetos si hay oscuridad (`1048–1057`) y `actions.c:1175–1181` hace que lectura falle en oscuridad.
- **Observado:** antes de solicitar cada comando, el original guarda `wzdark` (`main.c:1291–1293`); `LOOK` lo pone falso para impedir que mirar en penumbra cause caída (`playermove`, `635–645`). Tras el movimiento, solo en ubicación no forzada, si el lugar actual sigue oscuro y el anterior también lo estaba, hay una probabilidad de caída del 35% (`do_move`, `1236–1243`; `PIT_KILL_PROB`, `advent.h:36`).
- **Observado:** `do_command()` incrementa turno por cada entrada procesada, antes de ejecutar la orden (`main.c:1302–1322`); `closecheck()` llama `lampcheck()` (`1044–1045`), que consume límite con la lámpara brillante, avisa/usa baterías y la apaga al agotarse (`872–920`). La ubicación y estado de lámpara, límite, avisos y `wzdark` persisten entre comandos. `DEEP` y `LIT` son condiciones diferentes: lo primero activa actores; no implica luz (`advent.h:96–104, 122–126`).
- **Inferencia:** CH_02 requiere el estado de iluminación y reloj de lámpara en el mismo estado de partida; recalcular oscuridad solo al describir salas no reproduce el riesgo ni el consumo temporal.

### Movimientos forzados

- **Observado:** `initialise()` marca `FORCED` cuando una sala tiene descripción larga, tabla de viajes y su primera regla tiene movimiento `HERE` (`init.c:46–52`).
- **Observado:** el bucle principal ejecuta `do_move()` y luego `do_command()` (`main.c:1578–1589`). Si la ubicación actual es forzada, `do_command()` llama `playermove(HERE)` y retorna sin leer entrada (`1249–1263`); la siguiente iteración mueve y vuelve a describir. `playermove()` recorre reglas en orden, evalúa condiciones y ejecuta destinos `goto`, `speak` o las tres clases especiales de viaje (`575–870`). `do_move()` ejecuta después actores y muerte (`1199–1246`). Por tanto, una cadena forzada puede atravesar varios estados sin consumir un comando nuevo.
- **Observado:** en CH_02 `LOC_CRACK` y `LOC_DOME` son estados automáticos transitorios con retorno a sala ordinaria; `LOC_NECKBROKE` y `LOC_NOMAKE` son llegadas letales que su regla `HERE` manda a `LOC_NOWHERE`. `LOC_FOOF1/2` son otros estados transitorios de la frontera de palabras mágicas. La partición editorial clasifica estados especiales aparte ([oa_chapters.py](../../../06_reconstruccion_drawio/tools/oa_chapters.py:59), [líneas 129–138](../../../06_reconstruccion_drawio/tools/oa_chapters.py:129)); el informe CH_02 ya identifica estos destinos (se conserva como evidencia previa, no como autoridad de ejecución).
- **Inferencia:** el runtime necesita codificar el atributo `forced` desde la regla fuente y procesar el ciclo automático en orden. No debe convertir automáticamente todos los destinos fuera del capítulo en una frontera: transitorio, letal, mensaje y frontera geográfica tienen semánticas diferentes.

### Muerte y reincarnación

- **Observado:** causas del corte CH_02 incluyen `LOC_NECKBROKE`/`LOC_NOMAKE` que fuerzan `LOC_NOWHERE`, caída probabilística en oscuridad y acierto de cuchillo de enano (`Open_Adventure.yaml:603–604, 651–658, 693–709`; `main.c:1232–1243, 469–473`).
- **Observado:** `croak()` incrementa muertes; si la cueva está cerrando finaliza. En otro caso pregunta si se continúa, y termina ante respuesta negativa o al llegar a `NDEATHS`. Si continúa, destruye agua/aceite, apaga la lámpara si se llevaba, deja los objetos transportados en `oldlc2` (la lámpara en `LOC_START`) y pone `oldloc`, `loc`, `newloc` en `LOC_BUILDING` (`main.c:495–531`). El YAML tiene tres obituarios, por lo que como máximo hay dos reincarnaciones antes de terminar.
- **Observado:** el puntaje resta diez puntos de supervivencia por cada muerte: `(NDEATHS - game.numdie) * 10` (`score.c:63–70`). El intérprete Godot actual añade `world.num_deaths * 10` en `_score()` como puntos fijos de supervivencia, con comentario de que en CH_01 no hay muertes (`interpreter.gd:436–437`). Esto dejaría de ser válido al añadir muertes.
- **Inferencia:** la respuesta sí/no de reincarnación es parte del flujo de comando; mantener una única instancia requiere un estado pendiente en la misma sesión, no crear otra partida implícita. Los datos de inventario, lámpara, muerte y ubicación de retorno deben mutar en el mismo `GameState`.

## Datos posteriores necesarios sin hacer jugables esos capítulos

| Subsistema | Datos globales mínimos | Lo que no necesita para CH_02 |
| --- | --- | --- |
| Enanos: elección de movimiento | ID y flags `DEEP/FORCED/NOARRR` de las 185 salas; viajes ordenados con destino tipo/ID y `nodwarves`; seis posiciones iniciales | Descripciones, vocabulario, objetos o parser de esas salas |
| Pirata | Grafo anterior; catálogo estático de objetos/tesoros, ubicaciones declaradas, estados relevantes; `chloc/chloc2`, tally y estados mutables de objetos | Acciones y pantallas de capítulos posteriores |
| Luz/caída | flags `LIT/FORCED`, objeto lámpara y baterías, estados y límites temporales | Contenido editorial de salas inaccesibles |
| Viaje forzado | regla `HERE` ordenada, destino y condiciones; distinción entre goto/speak/special, pseudo-salas y marcadores de muerte | Que los pseudo-destinos sean seleccionables como habitaciones jugables |
| Muerte/puntuación | conteo de muertes, obituarios/prompt, `oldlc2`, objetos y sus lugares/estados, límites de vidas | Puzzles de reincarnación o endgame de capítulos posteriores, salvo que una ruta jugable los alcance |

**Límite propuesto (inferencia):** `WorldData.locations` continúa siendo el conjunto de ubicaciones accesibles al jugador y del mapa de capítulos habilitados. Se añade una proyección `simulation_graph` generada desde el mismo IR/YAML con las 185 ubicaciones y filas necesarias para actores, pero ningún método de `Interpreter` debe tratar esa proyección como autorización de movimiento del jugador. El catálogo global de objetos puede proveer estado a sistemas globales, mientras vocabulario, descripciones y acciones ejecutables siguen filtrados al contenido jugable. Cualquier cruce de frontera del jugador conserva semántica explícita; no se auto-habilita por existir el destino en el grafo de simulación.

## Arquitectura mínima propuesta

1. **Un único dataset determinista** producido por el exportador existente, con dos secciones tipadas: `playable_world` (locations, objetos y vocabulario permitidos actualmente) y `simulation_graph` (IDs, flags y travel ordenado completo). Ambos provienen del mismo parseo del YAML; no copiar reglas manualmente ni implementar lógica de viaje en el grafo.
2. **Un único `Interpreter` y un único `GameState` persistentes.** Ampliar el estado con campos globales requeridos conforme se implementen las mecánicas: actores (`loc`, `oldloc`, `seen`), `dflag/dkill/dtotal`, RNG con política documentada, `oldloc/oldlc2`, oscuridad previa, límite/avisos de lámpara, muertes y respuesta pendiente de reincarnación, y estado global de tesoros/cofre.
3. **Separación en consumo:** el movimiento del jugador consulta solo `playable_world`; el movimiento de actores consulta exclusivamente `simulation_graph`; objetos globales conservan un estado autoritativo compartido. Los IDs transitorios/letales se modelan con tipo de destino o rasgos semánticos, no se dibujan automáticamente como habitaciones de usuario.
4. **Orden de runtime con límites claros:** un solo ciclo procesa comando/turno, movimiento elegido, cascada `HERE`, actores, oscuridad/muerte y respuesta. No paralelizar la simulación ni añadir un manager genérico de capítulos.

**Coste comparado:** (A) recortar el grafo a CH_02 y sembrar rutas/posiciones artificiales parece barato, pero falsea el algoritmo de actores y se descarta. (B) cargar todas las salas como jugables es inicialmente simple, pero rompe la frontera editorial y permite llegar a capítulos no implementados; se descarta. (C) separar proyección jugable y grafo estático desde una fuente es un cambio moderado del exportador/esquema y exige pruebas de frontera, pero conserva fidelidad y evita duplicar reglas; es la opción mínima segura. La separación de datos sí es viable; la fidelidad de RNG de una sesión requiere una decisión sobre semilla y secuencia.

## Cortes de implementación por dependencia

Todos son propuestas; ninguno queda autorizado por este informe.

1. **CUT A — Contrato de datos global.** Extender exportador/esquema para emitir el grafo histórico ordenado y sus flags, además del subconjunto jugable. Validar los 185 IDs, las 623 entradas de viaje, destinos y posiciones `dwarflocs` contra la fuente. Sin efectos en runtime.
2. **CUT B — Ciclo de viaje.** Implementar turnos de entrada, `HERE` automático en cascada, destinos `goto/speak/special`, historial `oldloc/oldlc2` y frontera explícita. Añadir casos CH_01/CH_02, estados transitorios y muerte por destino.
3. **CUT C — Oscuridad/lámpara.** Integrar descripción/visibilidad, estado de lámpara, baterías, consumo/avisos, snapshot `wzdark`, exención LOOK y caída reproducible con RNG inyectable.
4. **CUT D — Muerte y reincarnación.** Añadir prompt pendiente, vidas, mutación de objetos/inventario, posición de retorno y puntuación por muertes; probar cierre y última vida por separado.
5. **CUT E — Actores completos.** Implementar activación y movimiento usando el grafo global, el orden original, filtros de actor y política RNG; después interacciones del jugador con enanos y pirata, con ledger de tesoros global.
6. **CUT F — CH_02 jugable.** Habilitar solo los 12 miembros de `CH_ENTRY`, objetos con colocación múltiple, acciones de capítulo y cruces autorizados; mantener fuera contenidos descriptivos y comandos de capítulos posteriores. Verificar límites antes y después de cada cruce.

La secuencia C/D/E depende del ciclo B; F puede preparar datos en paralelo conceptualmente, pero no debe declararse jugable hasta que B–E cubran las mecánicas globales activables en las salas de entrada.

## Pruebas necesarias

- **Exportador:** determinismo byte a byte; conteos y hash de IDs/rutas; comparación en orden con YAML; todos los targets resueltos o tipados explícitamente; `nodwarves`, `DEEP`, `FORCED`, `NOARRR` preservados; ningún campo narrativo de sala no jugable filtrado al parser.
- **Límite de capítulo:** demostrar que la existencia de una sala en `simulation_graph` no la hace destino accesible, describible ni seleccionable por el jugador; los actores sí pueden recorrerla desde las posiciones iniciales históricas.
- **Actores:** activación retrasada; primera aparición; candidatos y fallback; rutas excluidas por flags; movimiento/ataque/seen/bloqueo; secuencias reproducibles con semilla controlada; pirata moviendo cofre y tomando tesoros sin depender de exposición de habitaciones posteriores.
- **Oscuridad:** luz por sala/lámpara, visibilidad de descripciones/objetos, `READ`, consumo/aviso/batería, `LOOK` sin caída y caída en movimiento bajo oscuridad con RNG controlado.
- **Forzados/muerte:** cadenas `HERE` no consumen entrada adicional; DOME/CRACK retornan; estados letales alcanzan croak; reincarnación conserva propiedades no destruidas y reposiciona objetos exactamente; límites y puntaje de tres muertes.
- **Regresión:** mantener los checks existentes del intérprete CH_01; el baseline reportado previamente es 448 checks con Godot 4.7.2, pero esta investigación no los volvió a ejecutar.
- **Validación manual pendiente:** jugar secuencias CH_02 con terminal real: entrar al Hall of Mists, activar enanos tras la condición correspondiente, observar ataques/bloqueos, probar lámpara y caída, rechazar/aceptar reincarnación, y confirmar que la frontera impide interactuar con capítulos aún cerrados. Validar mensajes y legibilidad de cascadas forzadas.

## Riesgos y condiciones de parada

- **RNG:** fuente arranca con semilla de reloj; una sesión Godot determinista no equivale a paridad exacta salvo semilla y orden de consumo controlados. Acordar si el objetivo es traza exacta o distribución/comportamiento equivalente antes de fijar criterios.
- **Reglas de actores:** omitir orden de viaje, el fallback a `oldloc`, `nodwarves`, `FORCED` o `NOARRR` altera rutas aunque todos los destinos existan.
- **Límite jugable:** reusar `WorldData.is_in_chapter()` es útil, pero unificar listas jugables y de simulación haría accesibles inadvertidamente salas futuras.
- **Objetos:** el modelo actual inicializa un objeto en `locations[0]` y pierde la segunda ubicación de objetos como `STEPS` y `FISSURE` (`game_state.gd:27–30`); el pirata requiere catálogo de tesoros más amplio que los objetos visibles en CH_02.
- **Semántica temporal:** actualmente el intérprete Godot aumenta `turn` al moverse (`interpreter.gd:128–143`), frente a cada línea procesada en el original (`main.c:1302–1322`). Cambiarlo impacta lámpara, actores y acciones incluso sin movimiento; no debe hacerse como arreglo local sin regresiones definidas.
- **Parada obligatoria:** si exportador no puede preservar grafo ordenado con procedencia verificable, si una ruta de actor requiere ejecutar lógica especial que no esté representada en el grafo o si el estado global de tesoros no puede compartirse sin habilitar acciones de capítulos futuros, detener el corte y presentar esa dependencia. No aproximar rutas ni convertir incertidumbre en validación automática.

## Estado y alcance

- **Hechos observados:** se obtuvieron por inspección de `main.c`, `advent.h`, `init.c`, `misc.c`, `actions.c`, `score.c`, YAML y clases Godot citadas. No se editaron esas fuentes ni se ejecutaron pruebas.
- **Inferencias:** viabilidad de la proyección `simulation_graph`, partición de objetos y orden de cortes son propuesta arquitectónica derivada de esos hechos; requieren autorización y pruebas antes de darse por implementadas.
- **Validación manual pendiente:** toda secuencia interactiva de CH_02 y fidelidad visual/mensajes.
- **Límites de esta entrega:** no se modificaron código, pruebas, YAML, draw.io, datos generados ni archivos preexistentes. `sync_to_drive.ps1` y `07_godot_open_adventure/reports/RECONSTRUCTION_CH02.md` permanecen intactos. No se ejecutó staging, commit ni push.
