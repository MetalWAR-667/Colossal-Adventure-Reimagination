# Plan — Capítulo 02 «Cave Entry» (`CH_ENTRY`)

> **Nota de licencia posterior:** las referencias AGPL de este plan describen
> el estado histórico en que fue redactado. El baseline público vigente usa
> **GPL-3.0-or-later** por decisión humana de `CAR-GIT-BASELINE-02`.

**Estado:** PROPUESTA — pendiente de autorización del corte.
**Predecesor:** `RECONSTRUCTION_CH01.md` (capítulo 01 verificado, 194 comprobaciones PASS).
**Alcance:** 12 salas del capítulo 02 de Open Adventure, montado sobre el motor ya existente.

## 1. Qué es el capítulo 02 en la fuente

12 salas, tomadas de `06_reconstruccion_drawio/tools/oa_chapters.py` → `CH_ENTRY`:

| Sala | Contenido | Reglas de salida (verbo → destino) |
| --- | --- | --- |
| `LOC_BELOWGRATE` | Chamber bajo la reja | `out`/`up` → `LOC_GRATE` (solo si la reja **no** está cerrada; si no, mensaje «reja cerrada con llave»), `crawl`/`cobble`/`inward`/`west` → `LOC_COBBLE`, `pit` → `LOC_PITTOP`, `debris` → `LOC_DEBRIS` |
| `LOC_COBBLE` | Pasillo bajo de guijarros | `out`/`surface`/`east` → `LOC_BELOWGRATE`, `inward`/`dark`/`west`/`debris` → `LOC_DEBRIS`, `pit` → `LOC_PITTOP` |
| `LOC_DEBRIS` | Sala de cascotes; barro con «MAGIC WORD XYZZY» | `depression` → `LOC_GRATE` (si la reja no está cerrada), `entrance` → `LOC_BELOWGRATE`, `crawl`/`cobble`/`pass`/`low`/`east` → `LOC_COBBLE`, `canyon`/`inward`/`up`/`west` → `LOC_AWKWARD`, **`xyzzy` → `LOC_FOOF2`** (vuelve a la casita, capítulo 01), `pit` → `LOC_PITTOP` |
| `LOC_AWKWARD` | Barranco inclinado | `depression` → `LOC_GRATE`, `entrance` → `LOC_BELOWGRATE`, `down`/`east`/`debris` → `LOC_DEBRIS`, `inward`/`up`/`west` → `LOC_BIRDCHAMBER`, `pit` → `LOC_PITTOP` |
| `LOC_BIRDCHAMBER` | Cámara de 30 pies; el pájaro | `canyon`/`east` → `LOC_AWKWARD`, `pass`/`pit`/`west` → `LOC_PITTOP`, más `depression`/`entrance`/`debris` |
| `LOC_PITTOP` | Brocal del pozo con niebla | `pass`/`east` → `LOC_BIRDCHAMBER`, **`down`/`pit`/`steps` → `LOC_NECKBROKE` si llevas el oro** (caída mortal) y `down` → `LOC_MISTHALL` si no, `crack`/`west` → `LOC_CRACK`, más `depression`/`entrance`/`debris` |
| `LOC_CRACK` | Grieta demasiado estrecha | solo retorno implícito → `LOC_PITTOP` |
| `LOC_MISTHALL` | Hall of Mists | `left`/`south` → `LOC_NUGGET`, `forward`/`hall`/`west` → `LOC_EASTBANK`, `stair`/`down`/`north` → `LOC_KINGHALL` (cap. 03), `up`/`pit`/`steps`/`dome`/`pass`/`east` → `LOC_DOME` **solo con el oro**, `up` → `LOC_PITTOP`, `y2` → `LOC_JUMBLE` (cap. 10) |
| `LOC_NUGGET` | Nota en la pared + el oro | `hall`/`out`/`north` → `LOC_MISTHALL` |
| `LOC_EASTBANK` | Orilla este de la grieta | `hall`/`east` → `LOC_MISTHALL`, `jump` → mensaje «pasa por el puente», `over`/`across`/`west`/`cross` → mensaje «no hay paso», `over` → `LOC_WESTBANK` |
| `LOC_WESTBANK` | Orilla oeste; diamantes | `north` → `LOC_PARALLEL1` (cap. 04), `west` → `LOC_MISTWEST` (cap. 04), `over` → `LOC_EASTBANK` |
| `LOC_FOOF1` | Pseudo-sala mágica | retorno implícito → `LOC_DEBRIS` |

Objetos que entran: `CAGE` (en `LOC_COBBLE`), `ROD` (en `LOC_DEBRIS`), `BIRD`
(en `LOC_BIRDCHAMBER`, con tres estados), `NUGGET` (tesoro, en `LOC_NUGGET`),
`OBJ_51` diamantes (tesoro, en `LOC_WESTBANK`), `OBJ_47` barro legible,
`OBJ_48` nota legible, `STEPS` (inmóvil, dos estados), `FISSURE`
(inmóvil, `UNBRIDGED`/`BRIDGED`).

## 2. Qué desbloquea

1. **El paso por la reja.** Con la reja abierta, `ENTER` en `LOC_GRATE` mete
   al jugador en `LOC_BELOWGRATE`: la frontera actual desaparece en esa ruta.
2. **El atajo de la palabra mágica.** `xyzzy` en la casita → `LOC_FOOF1` →
   sala de cascotes. Es el atajo clásico y funciona en cuanto el capítulo 02
   está montado (hoy `LOC_FOOF1` es frontera).
3. **El puzle del pájaro.** Jaula (`CAGE`) en `LOC_COBBLE` + vara (`ROD`) en
   `LOC_DEBRIS`: para coger el pájaro hay que llevar la jaula y **no** llevar
   la vara (si la llevas, el pájaro esquiva). La lógica exacta está en
   `carry()` de `actions.c`.
4. **El primer tesoro.** `NUGGET`: +2 al encontrarlo, +14 al entregarlo en la
   casita. Con el oro entregado la puntuación pasa de 32 a 48 y la clase
   sube de «simple principiante» (umbral 45) a «aventurero de clase
   principiante» (umbral 120), según la fórmula de `score.c` ya implementada.
5. **Objetos con texto legible.** `READ` debe poder mostrar el texto de un
   objeto (`"MAGIC WORD XYZZY"`, `"You won't get it up the steps"`).
6. **Sonidos por estado.** El pájaro tiene seis textos de sonido según su
   estado; `LISTEN` debe usar el que corresponde, no uno fijo.

## 3. Cambios de motor (concretos, por archivo)

| Archivo | Cambio | Por qué |
| --- | --- | --- |
| `tools/oa_export_godot.py` | Generalizar `CHAPTER_ID` a una **lista** de capítulos (`--chapters CH_SURFACE,CH_ENTRY`); cada sala lleva su `chapter_id`; la frontera se calcula sobre la unión; la exportación del mapa pasa a ser una entrada por página del `.drawio` | El capítulo 01 solo no basta: hay reglas que cruzan el límite en ambos sentidos |
| `src/core/world_data.gd` | Cargar varias páginas de mapa y exponer `chapters: Array[String]` y `frontier: {destino → {mensaje, capítulo, es_muerte}}` | El mapa necesita poder cambiar de capítulo; la frontera necesita un mensaje por destino |
| `src/core/interpreter.gd` | Sustituir el mensaje único de frontera por uno **por destino**: frontera normal («esto pertenece al capítulo siguiente») y **frontera mortal** (salas de `CH_SPECIAL`: `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_GRUESOME`, `LOC_FOOTSLIP`, `LOC_SNAKEBLOCK`, `LOC_DOME`) | Meter el oro y «down» en el pozo no debe decir «capítulo siguiente»: es una muerte. Hay que distinguirlo |
| `src/core/interpreter.gd` | `READ`: si el objeto tiene `texts`, mostrarlo | `OBJ_47` y `OBJ_48` |
| `src/core/interpreter.gd` | `LISTEN`: usar el sonido **por estado del objeto** (el `sounds` del YAML es una lista alineada con los estados + variantes) | El pájaro canta distinto en cada estado |
| `src/core/interpreter.gd` | `CARRY` del pájaro: requerir `CAGE` en la mano, rechazar si llevas `ROD` (`BIRD_EVADES`), y mover `BIRD`+`CAGE` juntos al `BIRD_CAGED` | Regla de `actions.c` |
| `src/core/game_state.gd` | Estado por objeto con **lugar fijo** (`fixed`): las `STEPS` son `STEPS_UP` en `LOC_MISTHALL` y `STEPS_DOWN` en el resto (regla de `main.c`) | La descripción de las escaleras cambia según dónde estés |
| `src/core/world_object.gd` | Añadir `texts` (texto legible) y `sounds` (lista por estado) al modelo de objeto | Datos que hasta ahora no se exportaban |
| `src/ui/map_view.gd` | Selector de capítulo (o fusión de las dos páginas del `.drawio`) y marcado de las salas de frontera | El mapa pasa a tener dos páginas |
| `src/ui/main.gd` | Mostrar el capítulo actual en la barra de estado | — |

**Nada de esto rompe el capítulo 01:** el motor actual ya resuelve «la regla
apunta fuera del conjunto montado». Lo que cambia es *qué* conjunto está
montado y el matiz del mensaje.

## 4. Datos a exportar

El exportador debe emitir, para `CH_SURFACE + CH_ENTRY`:

- 46 salas (34 + 12) con su `chapter_id`.
- Objetos: los 8 actuales + `CAGE`, `ROD`, `BIRD`, `NUGGET`, `OBJ_47`,
  `OBJ_48`, `OBJ_51`, `STEPS`, `FISSURE` → **17 objetos**.
- frontier: `LOC_KINGHALL` (cap. 03), `LOC_JUMBLE` y `LOC_FOOF3` (cap. 10),
  `LOC_DOME`, `LOC_NECKBROKE`, `LOC_NOMAKE` (cap. 11), `LOC_PARALLEL1`,
  `LOC_MISTWEST` (cap. 04) → **7 destinos de frontera**, con `LOC_FOOF1`
  pasando a estar montado.
- Dos páginas de mapa: `CH_SURFACE` y `CH_ENTRY` (ya existen en el `.drawio`
  V3, con su geometría).
- Los mensajes usados: `CROSS_BRIDGE`, `NO_CROSS`, `BIRD_EVADES`,
  `CANNOT_CARRY`, `BIRD_CRAP`, más los sons del pájaro.

## 5. Contenido a redactar (reinterpretación, no traducción)

- **12 descripciones de sala en español** (2-4 frases, voz de la Biblia
  creativa). Se mapearían a `l10n_es.json`, en un bloque nuevo
  `locations` — el archivo ya separa texto y datos, así que solo crece.
- **Mensajes**: `CROSS_BRIDGE`, `NO_CROSS`, `BIRD_EVADES`, `CANNOT_CARRY`.
- **Frontera mortal**: un texto propio para las salas de muerte, distinto del
  aviso de «capítulo siguiente».
- **Ilustraciones**: 8-9 escenas nuevas (bajo la reja, guijarros, cascotes,
  barranco, cámara del pájaro, brocal del pozo, grieta, hall de niebla, sala
  del oro, orillas de la grieta). Siguen el mismo formato `LINE`/`FILL`; la
  hoja de contacto sirve de revisión (`tools/capture_scenes.gd`).

## 6. Pruebas a añadir

| Prueba | Qué fija |
| --- | --- |
| Entrar por la reja abierta | `LOC_GRATE` → `ENTER` → `LOC_BELOWGRATE` (ya no hay frontera) |
| Salir por la reja | `LOC_BELOWGRATE` → `out` → `LOC_GRATE` |
| Reja cerrada por arriba | con `LOCK GRATE`, `out` → mensaje de reja cerrada |
| Atajo mágico | `xyzzy` en la casita → `LOC_DEBRIS` |
| Puzle del pájaro | sin jaula → no se puede; con vara → esquiva; con jaula y sin vara → `BIRD_CAGED` |
| Oro | cogerlo suma 2; entregarlo en la casita suma 14; clase sube |
| Pozo con oro | `down` en `LOC_PITTOP` con el oro → frontera mortal, no sala jugable |
| Pozo sin oro | `down` → `LOC_MISTHALL` |
| Grieta | `west` en `LOC_PITTOP` → `LOC_CRACK`; `up` → `LOC_PITTOP` |
| Textos legibles | `READ NOTE` → «You won't get it up the steps» en español |
| Escaleras | descripción `STEPS_UP` en el hall, `STEPS_DOWN` en el brocal |
| Integridad | todo destino de viaje conocido; alcanzabilidad de las salas montadas desde `LOC_START` |

## 7. Riesgos y decisiones abiertas

1. **Frontera mortal vs. frontera de capítulo.** Hay que decidir el texto y
   si la muerte debe reiniciar la partida (como en el original) o solo
   avisar. *Propuesta:* avisar y dejar al jugador donde estaba, sin
   reinicio; el reinicio con obituario pertenece a un corte posterior.
2. **`LOC_LEDGE` sigue sin entrada** en toda la fuente. Montar el capítulo 02
   no lo arregla: el zafiro (tesoro de 16) sigue inaccesible. Hay que
   decidir si se acepta o si se consulta la fuente original en inglés para
   ver si el YAML perdió una regla.
3. **Los enanos y el ojo del diablo** no están modelados. En el original el
   oro del capítulo 02 está custodiado por enanos; sin ellos, el oro es
   simplemente cogible. *Propuesta:* aceptar el oro sin enanos en este corte
   y documentarlo, o implementar el sistema de enanos (mucho más trabajo,
   toca `dflag`, `dwarflocs` y el reloj).
4. **`LOC_WESTBANK` y los diamantes** quedan al otro lado de la grieta, que
   solo se cruza con puente (capítulo 03 en adelante). El diamante es
   inaccesible en el capítulo 02: es correcto, pero conviene que el jugador
   no lo espere.
5. **El mapa**: ¿dos páginas con selector, o una vista conjunta? Propuesta:
   selector de capítulo, reutilizando la geometría del `.drawio`.
6. **Licencia**: con AGPL ya aplicada, publicar implica acompañar el código
   fuente; el plan no cambia eso.

## 8. Secuencia propuesta (cada paso verificable)

| # | Paso | Entregable | Verificación |
| --- | --- | --- | --- |
| 1 | Exportador multi-capítulo | `--chapters` + frontier por destino + páginas de mapa | `oa_export_godot.py --check` sigue dando PASS con el mismo dataset de un solo capítulo |
| 2 | Frontier con matiz y mensaje por destino | `interpreter.gd` | Test: entrar en la reja ya no es frontera; el pozo con oro avisa de muerte |
| 3 | Objetos legibles y sonidos por estado | modelo de objeto + `READ`/`LISTEN` | Test del barro y de la nota |
| 4 | Puzle del pájaro | `CARRY` con jaula/vara | Test de los tres casos |
| 5 | Escaleras con lugar fijo | `STEPS_UP`/`STEPS_DOWN` | Test de la descripción según sala |
| 6 | Textos en español de las 12 salas + mensajes | `l10n_es.json` | Revisión editorial (Gandulf) |
| 7 | Ilustraciones de las salas nuevas | `art_ch01.json` → `art_ch02.json` | Hoja de contacto revisada (Jack Burton) |
| 8 | Mapa con selector de capítulo | `map_view.gd` | Captura de pantalla |
| 9 | Suite de pruebas del capítulo 02 | `tests/run_tests.gd` | PASS integral |
| 10 | Informe del corte 02 | `reports/RECONSTRUCTION_CH02.md` | Revisión humana |

Los pasos 1-5 y 9 son de motor y datos; 6-8 son de contenido. Se pueden hacer
en dos oleadas: primero el motor con textos provisionales (para no bloquear),
después el contenido definitivo.

## 9. Criterios de aceptación

1. `tools/verify.ps1` da PASS completo (exportación, import, tests, hojas).
2. El capítulo 01 sigue jugando igual: la suite anterior no se toca salvo
   para añadir casos.
3. Se puede entrar por la reja, recorrer el capítulo 02 y volver.
4. El atajo `xyzzy` funciona en ambos sentidos.
5. El puzle del pájaro y el del oro funcionan según la fuente.
6. Ninguna sala o regla de la frontera se presenta como parte del capítulo.
7. Informe de corte con desviaciones, límites y decisiones pendientes.
8. Revisión humana y autorización antes de commit.

## 10. Decisiones que pide el responsable

1. ¿Se autoriza el corte del capítulo 02 con el alcance de este documento?
2. ¿Los enanos se implementan en este corte o se acepta el oro sin custodia?
3. ¿La muerte en la frontera reinicia la partida o solo avisa?
4. ¿El mapa se presenta por capítulos o en una vista conjunta?
5. ¿Se consulta la fuente original en inglés para intentar recuperar la regla
   de entrada de `LOC_LEDGE`?
