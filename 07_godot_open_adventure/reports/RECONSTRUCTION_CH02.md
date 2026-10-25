# CAR-CH02-001 — Reconocimiento de Cave Entry

Estado: **BLOCKED / SOURCE AUDIT COMPLETED / NOT IMPLEMENTED**.

## Baseline y verificaciones

Repositorio: `C:\remake\Colossal-Adventure-Reimagination-public`, rama `main`,
HEAD `8dd5b7d4c4a357620167e8f200aa87beca6cd261`.
El archivo humano no rastreado `sync_to_drive.ps1` se conserva y queda fuera
del corte, conforme a autorización expresa del propietario.

Se ejecutó `tools/verify.ps1 -Godot` con el ejecutable absoluto
`C:\Program Files (x86)\Steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`.
Resultado: exportación determinista, importación, suite y captura de las 11
escenas existentes: `ALL CHECKS PASSED`.
Una ejecución adicional de `res://tests/run_tests.gd`, esperando la terminación
del proceso y leyendo su log, confirmó `PASS: 448 checks`, código de salida 0,
con Godot `4.7.2.stable.steam.ed1daf0bf`.
Esto verifica CH_01 actual; no verifica una implementación de CH_02.

## CUT A — Inventario observado en las fuentes

La extracción en memoria mediante el exportador existente confirmó 12 miembros
de `CH_ENTRY`, 51 entradas de viaje y 12 nodos con geometría en su página del
draw.io. No faltan IDs ni se modificaron las fuentes o el dataset.

Miembros: `LOC_BELOWGRATE`, `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`,
`LOC_BIRDCHAMBER`, `LOC_PITTOP`, `LOC_CRACK`, `LOC_MISTHALL`, `LOC_NUGGET`,
`LOC_EASTBANK`, `LOC_WESTBANK`, `LOC_FOOF1`.

Objetos con presencia inicial en CH_02: `GRATE`, `CAGE`, `ROD`, `STEPS`,
`BIRD`, `FISSURE`, `OBJ_47` (mud), `OBJ_48` (note), `NUGGET`, `OBJ_51`
(diamonds). `GRATE`, `STEPS` y `FISSURE` tienen presencia en dos ubicaciones.
El modelo actual conserva solo una ubicación mutable por objeto: requiere
completar esa representación para que las interacciones funcionen en ambas.

La unión editorial CH_01 + CH_02 abre la reja y ambos sentidos de XYZZY:
`LOC_BUILDING -> LOC_FOOF1 -> LOC_DEBRIS` y
`LOC_DEBRIS -> LOC_FOOF2 -> LOC_BUILDING`. FOOF1/2 son estados forzados.

Destinos externos detectados en la unión, clasificados:

| Tipo | Destinos |
| --- | --- |
| Fronteras geográficas / acceso a capítulos excluidos | `LOC_KINGHALL`, `LOC_JUMBLE`, `LOC_PARALLEL1`, `LOC_MISTWEST`, `LOC_FOOF3` (acceso a Y2) |
| Estado forzado con retorno interno | `LOC_DOME -> LOC_MISTHALL` |
| Estados letales | `LOC_NECKBROKE`, `LOC_NOMAKE`, ambos hacia `LOC_NOWHERE` |

`LOC_CRACK` también es forzado y vuelve a `LOC_PITTOP`.
Por tanto DOME, CRACK y los estados letales no deben tratarse como fronteras
geográficas ordinarias. No se detectó contradicción entre las fuentes leídas.

## Dependencia global que detiene el corte

Hechos observados:

- `codigo_fuente_open_adventure/main.c:dwarfmove()` (línea 312) activa
  `dflag` al alcanzar una sala `DEEP`, expresamente Hall of Mists. Visitas
  posteriores pueden producir el primer encuentro y el hacha; después hay
  movimiento, bloqueo, ataques y pirata.
- La misma función recorre las reglas del grafo histórico para mover esos
  actores. Sus ubicaciones iniciales (`adventure.yaml:dwarflocs`) incluyen
  capítulos fuera de CH_01 + CH_02. No basta simular el grafo jugable recortado.
- `main.c:do_move()` (línea 1199) ejecuta esa actividad y las caídas en
  oscuridad; `croak()` (línea 495) gobierna muerte, pregunta de reincarnación,
  vidas, reposición de objetos, lámpara y posición del jugador.
- `advent.h:IS_DARK_HERE()` distingue luz de sala y lámpara presente/encendida.
  `DEEP` activa otras reglas; no es sinónimo de oscuridad.
- El `GameState` actual carece de actores, vidas, estado previo de oscuridad,
  pregunta pendiente y temporizador de lámpara. `Interpreter._execute_move()`
  solo mueve al destino si pertenece al dataset; `_describe_current()` no
  filtra por oscuridad. `_score()` concede supervivencia sin descontar muertes.
- El original cuenta las entradas de comandos en `do_command()`; el motor
  actual incrementa turnos al mover. Incorporar el ciclo global requiere
  resolver esta diferencia y sus regresiones expresamente.

Conclusión técnica: la fidelidad completa desde Hall of Mists exige ampliar el
ciclo global de la partida y decidir cómo conservar el grafo de simulación de
actores fuera del mundo accesible. Es una ampliación sustancial respecto al
intérprete de CH_01. Omitir los actores, congelarlos en la frontera o sustituir
la muerte por un mensaje alteraría el comportamiento original.

Se aplica la condición de parada de CAR-CH02-001 para mecánicas globales
imprescindibles que exceden una ampliación local segura. CUT B–E no se han
implementado. No se declara CH_02 jugable ni pendiente solo de validación manual.

## Clasificación preliminar de comportamientos

| Comportamiento | Resultado de inspección |
| --- | --- |
| Precedencia y condiciones de viaje, reja | Infraestructura reutilizable; falta integrar destinos y presencia doble de objetos |
| XYZZY, CRACK, DOME | Ampliación local de resolución de viajes forzados |
| Pepita y escalones | Condiciones ya representables; desenlaces forzados/letales ausentes |
| Pájaro y jaula | Ampliación local de captura, restricción por vara y transporte/soltado conjunto (`actions.c:carry/drop`) |
| Fisura y vara | Ampliación local de `wave()` y estado compartido en ambas orillas |
| Objeto JADE | Dependencia adicional: `actions.c:wave()` puede hacerlo aparecer junto a STEPS; su ubicación inicial es NOWHERE y el filtro actual no lo exporta |
| Oscuridad, muerte, reincarnación, actividad DEEP y temporización | Mecánicas globales ausentes; requieren resolver el bloqueo antes de integración |
| CH_03–CH_11, cierre de cueva y final | No implementados; no abrir accesos por esta investigación |

## Continuación mínima propuesta

Autorizar primero un corte de dependencias del intérprete: ciclo de turnos y
oscuridad, viajes forzados, muerte/reincarnación y alcance explícito de actores
DEEP con grafo de simulación separado de los destinos accesibles. Debe conservar
el mismo `Interpreter` y `GameState`, IDs y reglas fuente, con pruebas de estado
y regresión de CH_01.

Alternativa: autorizar explícitamente una reconstrucción parcial que difiera
los actores DEEP. Esa variante tendría que declararse limitada, con las reglas
omitidas enumeradas; no cumpliría la fidelidad completa del encargo vigente.

Recomendación: resolver primero el corte de dependencias y después reanudar
CH_02. Para entonces, un dataset combinado es la opción propuesta más sencilla:
un solo estado jugable y ninguna recarga al cruzar capítulos; debe distinguir
las salas, estados forzados y fronteras y conservar la geometría de cada página.

## Entrega y validación pendiente

Único archivo añadido: este informe. Código, datos generados, localización,
ilustraciones, README y CURRENT_STATE no se modificaron. No hubo commit ni push.

No se ejecutaron recorridos de CH_02 ni validación gráfica: el capítulo aún no
está integrado. No hay rutas de prueba presentadas como resultados reales.
Tras resolver las dependencias se deben verificar reja, ambos XYZZY, capturas
de pájaro/jaula, escalones con oro, fisura, oscuridad, muertes, regreso a la
superficie, fronteras y persistencia del estado y del foco.
