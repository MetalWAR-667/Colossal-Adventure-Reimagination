# CAR-CORE-002 / R1 — Matriz de Dependencias Estructurales

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-25
**Documento:** `STRUCTURAL_DEPENDENCY_MATRIX.md`
**Corte:** `CAR-CORE-002 / R1 — Canonical Room Inventory`

---

## 1. Guía de Clasificación Epistémica

Para evitar suposiciones especulativas y garantizar la separación estricta entre datos estáticos y lógica de runtime no autorizada, todas las relaciones estructurales se clasifican bajo tres categorías formales:

- **OBSERVED:** Relación directamente comprobable y atestiguada en las fuentes de autoridad (`Open_Adventure.yaml`, `Open_Adventure_World_V3.drawio`).
- **INFERRED:** Deducción técnica respaldada por reglas explícitas de código fuente histórico (p. ej. `init.c`, `dungeon.c`).
- **PENDING:** Semántica funcional o subsistema transversal demostrado como requisito para la jugabilidad completa, pero cuya implementación funcional queda pospuesta a cortes futuros expresamente autorizados.

---

## 2. Cruces entre Capítulos Editoriales (`OBSERVED`)

Existen exactamente **85 registros de viaje** de tipo `goto` que parten de una ubicación en un capítulo y tienen como destino una ubicación en un capítulo distinto.

### Resumen de cruces por pares de capítulos

| Capítulo origen | Capítulo destino | Cruces | Ejemplos de conexión |
|---|---|---:|---|
| `CH_SURFACE` | `CH_ENTRY` | 4 | `LOC_GRATE` -> `LOC_BELOWGRATE` (requiere `GRATE` abierta) |
| `CH_SURFACE` | `CH_CENTRAL` | 1 | `LOC_ROADEND` / conexiones remotas |
| `CH_ENTRY` | `CH_SURFACE` | 2 | `LOC_BELOWGRATE` -> `LOC_GRATE` (requiere `GRATE` abierta) |
| `CH_ENTRY` | `CH_CENTRAL` | 4 | `LOC_MISTHALL` -> `LOC_KINGHALL` |
| `CH_CENTRAL` | `CH_ENTRY` | 4 | `LOC_KINGHALL` -> `LOC_MISTHALL` |
| `CH_CENTRAL` | `CH_MAZE_ALIKE` | 3 | `LOC_WESTEND` -> `LOC_ALIKE1` |
| `CH_CENTRAL` | `CH_BEDQUILT` | 4 | `LOC_CROSSOVER` -> `LOC_COMPLEX` |
| `CH_CENTRAL` | `CH_REPOSITORY` | 2 | `LOC_IMMENSE` -> `LOC_BREATHTAKING` |
| `CH_MAZE_ALIKE` | `CH_CENTRAL` | 3 | `LOC_ALIKE1` -> `LOC_WESTEND` |
| `CH_MAZE_ALIKE` | `CH_BEDQUILT` | 2 | `LOC_MAZEEND12` -> `LOC_LOWROOM` |
| `CH_MAZE_ALIKE` | `CH_WITT_DIFFERENT` | 2 | `LOC_LONGWEST` -> `LOC_DIFFERENT1` (`nodwarves`) |
| `CH_BEDQUILT` | `CH_CENTRAL` | 4 | `LOC_COMPLEX` -> `LOC_CROSSOVER` |
| `CH_BEDQUILT` | `CH_MAZE_ALIKE` | 2 | `LOC_LOWROOM` -> `LOC_MAZEEND12` |
| `CH_BEDQUILT` | `CH_ORIENTAL_PLOVER` | 3 | `LOC_SWISSCHEESE` -> `LOC_SOFTROOM` |
| `CH_BEDQUILT` | `CH_REPOSITORY` | 2 | `LOC_SECRET4` -> `LOC_CORRIDOR` |
| `CH_ORIENTAL_PLOVER` | `CH_BEDQUILT` | 3 | `LOC_SOFTROOM` -> `LOC_SWISSCHEESE` |
| `CH_ORIENTAL_PLOVER` | `CH_RESERVOIR` | 2 | `LOC_CULDESAC` -> `LOC_RESERVOIR` |
| `CH_ORIENTAL_PLOVER` | `CH_Y2_WINDOWS` | 4 | `LOC_ALCOVE` -> `LOC_WINDOW1` |
| `CH_RESERVOIR` | `CH_ORIENTAL_PLOVER` | 2 | `LOC_RESERVOIR` -> `LOC_CULDESAC` |
| `CH_RESERVOIR` | `CH_REPOSITORY` | 3 | `LOC_CLIFFTOP` -> `LOC_BREATHTAKING` |
| `CH_REPOSITORY` | `CH_CENTRAL` | 2 | `LOC_BREATHTAKING` -> `LOC_IMMENSE` |
| `CH_REPOSITORY` | `CH_BEDQUILT` | 2 | `LOC_CORRIDOR` -> `LOC_SECRET4` |
| `CH_REPOSITORY` | `CH_RESERVOIR` | 3 | `LOC_BREATHTAKING` -> `LOC_CLIFFTOP` |
| `CH_WITT_DIFFERENT` | `CH_MAZE_ALIKE` | 2 | `LOC_DIFFERENT1` -> `LOC_LONGWEST` |
| `CH_WITT_DIFFERENT` | `CH_Y2_WINDOWS` | 3 | `LOC_ANTEROOM` -> `LOC_JUMBLE` |
| `CH_Y2_WINDOWS` | `CH_ENTRY` | 2 | `LOC_WINDOW1` -> `LOC_PITTOP` |
| `CH_Y2_WINDOWS` | `CH_CENTRAL` | 1 | `LOC_BROKEN` -> `LOC_NARROW` |
| `CH_Y2_WINDOWS` | `CH_ORIENTAL_PLOVER` | 4 | `LOC_WINDOW1` -> `LOC_ALCOVE` |
| `CH_Y2_WINDOWS` | `CH_WITT_DIFFERENT` | 3 | `LOC_JUMBLE` -> `LOC_ANTEROOM` |
| Varios capítulos | `CH_SPECIAL` (muertes / transitorios) | 8 | Caídas letales (`LOC_NECKBROKE`, etc.) |

---

## 3. Dependencias de Viajes sobre Objetos (`OBSERVED`)

Se identifican **16 objetos históricos** que intervienen en las condiciones de viaje (`carry`, `with`, `not`):

| Objeto | Tipo de condición | Reglas afectadas | Ubicación(es) de origen | Efecto estructural observado |
|---|---|---:|---|---|
| `GRATE` | `not state GRATE_CLOSED` | 4 | `LOC_GRATE`, `LOC_BELOWGRATE` | Impide el paso a través de la reja si está cerrada. |
| `CHASM` | `not state CHASM_BRIDGED` | 2 | `LOC_SWCHASM`, `LOC_NECHASM` | Impide cruzar el abismo sin el puente tendido. |
| `DOOR` | `not state DOOR_RUSTED` | 2 | `LOC_IMMENSE` | Impide cruzar la puerta oxidada sin engrasarla. |
| `DRAGON` | `not state DRAGON_BLOCK` | 2 | `LOC_SOUTHSIDE` | Impide el acceso a la sala del dragón mientras bloquea el paso. |
| `SNAKE` | `not state SNAKE_BLOCK` | 3 | `LOC_KINGHALL` | Impide pasar a través del Hall del Rey de la Montaña con la serpiente activa. |
| `FISSURE` | `not state FISSURE_UNBRIDGED` | 2 | `LOC_EASTBANK`, `LOC_WESTBANK` | Impide cruzar la fisura sin tender el puente de cristal. |
| `PLANT` | `not state PLANT_THIRSTY` | 4 | `LOC_WESTPIT` | Impide trepar la enredadera gigante sin regarla. |
| `TROLL` | `not state TROLL_UNPAID` | 2 | `LOC_SWCHASM`, `LOC_NECHASM` | Controla el peaje y paso del troll sobre el puente. |
| `OGRE` | `not state OGRE_BLOCK` | 2 | `LOC_LARGE` | Impide entrar al almacén custodiado por el ogro. |
| `RESER` | `not state RESER_FULL` | 1 | `LOC_RESERVOIR` | Permite cruzar el fondo del embalse cuando está drenado. |
| `CLAM` | `carry` | 1 | `LOC_SHELLROOM` | Regla especial para abrir o mover la almeja gigante. |
| `OYSTER` | `carry` | 1 | `LOC_SHELLROOM` | Regla especial para abrir o mover la ostra con perla. |
| `EMERALD` | `carry` | 2 | `LOC_PLOVER`, `LOC_Y2` | Teletransporte especial `PLOVER` sólo permitido si se porta la esmeralda. |
| `NUGGET` | `with` | 1 | `LOC_NUGGET` | Presencia de la pepita de oro en la habitación. |
| `RABBITFOOT` | `with` | 1 | `LOC_ROUGHHEWN` | Interviene en la probabilidad de navegación en Witt's End. |
| `VEND` | `with` | 1 | `LOC_STOREROOM` | Presencia de la máquina expendedora de pilas. |

---

## 4. Destinos Especiales (`OBSERVED` & `PENDING`)

Existen 6 reglas de viaje con `action_type = "special"`:

| Origen | Verbos | Manejador | Semántica histórica | Estado de implementación |
|---|---|---:|---|---|
| `LOC_ALCOVE` | `EAST`, `PASSA` | 1 | Paso estrecho hacia Plover Room (comprueba si el inventario excede el límite permitido). | INFERRED / MODELADO EN TEST CUT B |
| `LOC_PLOVER` | `WEST`, `PASSA`, `OUT` | 1 | Retorno desde Plover Room hacia Alcove (comprueba si el inventario excede el límite). | INFERRED / MODELADO EN TEST CUT B |
| `LOC_Y2` | `PLOVE` | 2 | Teletransporte mágico a Plover Room portando la esmeralda. | INFERRED / MODELADO EN TEST CUT B |
| `LOC_PLOVER` | `PLOVE` | 2 | Retorno mágico de Plover Room a Y2 portando la esmeralda. | INFERRED / MODELADO EN TEST CUT B |
| `LOC_SWCHASM` | `OVER` | 3 | Cruce interactivo del puente del troll (demanda de tesoro, aparición del oso / troll). | **PENDING / NOT IMPLEMENTED** |
| `LOC_NECHASM` | `OVER` | 3 | Cruce opuesto del puente del troll (demanda de tesoro, peaje). | **PENDING / NOT IMPLEMENTED** |

---

## 5. Ubicaciones con Movimiento Forzado (`INFERRED`)

Se identifican **22 ubicaciones** donde `is_forced = true`:

```text
LOC_CRACK, LOC_NECKBROKE, LOC_NOMAKE, LOC_DOME, LOC_CLIMBSTALK, LOC_BUILDING1,
LOC_SNAKEBLOCK, LOC_PARALLEL1, LOC_PARALLEL2, LOC_SEWER, LOC_NOCLIMB, LOC_PLANTTOP,
LOC_BADDIRECTION, LOC_FOOTSLIP, LOC_CLIFFTOP, LOC_GRUESOME, LOC_FOOF1, LOC_FOOF2,
LOC_FOOF3, LOC_FOOF4, LOC_FOOF5, LOC_FOOF6
```

- **5 transitorias:** `LOC_CRACK`, `LOC_CLIMBSTALK`, `LOC_PARALLEL1`, `LOC_PARALLEL2`, `LOC_CLIFFTOP` (avanzan de inmediato a otra sala jugable).
- **4 letales:** `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_GRUESOME`, `LOC_FOOTSLIP` (ejecutan la secuencia de muerte por caída/trampa).
- **13 especiales:** 6 teletransportes `FOOF`, 6 mensajes de bloqueo/transición y 1 retorno de alcantarilla (`LOC_SEWER`).

---

## 6. Ubicaciones Letales (`INFERRED`)

- **Salas de muerte por caída/trampa:** `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_GRUESOME`, `LOC_FOOTSLIP`.
- **Centinela nulo:** `LOC_NOWHERE` (sala nula / limbo de objetos y muerte definitiva).
- **Mapeo de obituarios:** La fuente YAML define 3 obituarios históricos (`obituaries`), modelados e integrados en el runtime en `CAR-CORE-001 / CUT D`.

---

## 7. Banderas Globales y Actores (`OBSERVED`)

### Banderas estructurales
- `DEEP` (144 salas): Define la frontera subterránea donde operan enanos, pirata y oscuridad.
- `NOARRR` (18 salas): Zonas exentas de la aparición del pirata.
- `LIT` (37 salas): Habitaciones con luz natural permanente.
- `NOBACK` (50 salas): Habitaciones donde el comando `BACK` histórico no está disponible.
- `ALLALIKE` (27 salas) y `ALLDIFFERENT` (12 salas): Redes de laberintos.
- `FOREST` (22 salas): Región de bosque en la superficie.
- `FLUID` (10 salas) y `OILY` (1 sala): Salas con agua o petróleo (para llenar la botella).

### Datos para actores
- **Posiciones iniciales de los enanos (`dwarflocs`):**
  1. `LOC_KINGHALL`
  2. `LOC_WESTBANK`
  3. `LOC_Y2`
  4. `LOC_ALIKE3`
  5. `LOC_COMPLEX`
  6. `LOC_MAZEEND12`
- **Regla `nodwarves`:** Viaje 468 (`LOC_LONGWEST` -> `LOC_DIFFERENT1`), bloquea el paso de los enanos hacia el laberinto All Different.

---

## 8. Subsistemas en Estado PENDING (`PENDING / NOT AUTHORIZED`)

Los siguientes sistemas transversales se encuentran documentados e inventariados, pero su ejecución runtime **no está autorizada en R1** y queda formalmente pospuesta:

1. **Manejador `special 3` (Puente del Troll):** Requiere modelar la interacción con el troll, entrega de tesoros y el oso.
2. **Simulación de Enanos y Pirata:** Requiere implementar `dwarfmove()`, `spotted_by_pirate()`, persistencia de enanos vivos/muertos y generador pseudoaleatorio compartido.
3. **Cierre de Cueva y Endgame (`closecheck`):** Requiere contadores de turnos, verificación de tesoros depositados, reubicación de salas al repositorio y activación de los enanos finales.
4. **Puntuación Global:** Requiere cómputo de los 20 tesoros, estado de Witts End, bonificaciones y penalizaciones por hints.
5. **Hints Dinámicos:** Requiere temporizadores por sala y preguntas interactivas.
6. **Ciclo Global de Oscuridad y Lámpara:** Requiere extender el consumo y persistencia de baterías verificado en CUT C a los 10 capítulos restantes.
