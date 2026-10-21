# Procedencia y licencias — 07 Godot / Capítulo 01

Este corte mezcla tres materiales de origen distinto. Se mantienen separados
y trazables.

## 1. Datos del dungeon — Open Adventure

| Campo | Valor |
| --- | --- |
| Origen | `06_reconstruccion_drawio/Open_Adventure.yaml` (copia estructuralmente equivalente a `codigo_fuente_open_adventure/adventure.yaml`; difiere en finales de línea) |
| Autoría | Eric S. Raymond (Open Adventure 2.5), sobre el juego original de Will Crowther y Don Woods (1976) |
| Licencia | BSD-2-Clause (`codigo_fuente_open_adventure/COPYING`) |
| Uso | Reglas de viaje, condiciones, descripciones en inglés, mensajes, objetos, clases de puntuación, número de muertes |

Las dos copias del YAML se comparan en tiempo de importación: si divergen, el
exportador aborta en lugar de elegir una. Los SHA-256 de ambas quedan
registrados dentro del propio dataset generado
(`godot/data/chapter_01_surface.json` → `meta.source_yaml`).

### Qué se toma y qué no

- **Se toma:** la estructura de salas, las reglas de viaje y su orden de
  precedencia, las condiciones (`not OBJ STATE`, `pct`, `carry`, `with`), los
  objetos con sus estados, los mensajes arbitrarios, los verbos con sus raíces
  de cinco letras, las clases de puntuación y el número de muertes.
- **No se toma:** ninguna corrección ni completado. Donde el YAML es raro
  (la cloaca sin salida, la cornisa sin entrada) el comportamiento se mantiene
  y se documenta como límite, sin inventar reglas.

## 2. Geometría del mapa — diagrams.net

| Campo | Valor |
| --- | --- |
| Origen | `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio`, página `CH_SURFACE` |
| Autoría | Generada por `06_reconstruccion_drawio/tools/oa_world_v3.py` a partir del YAML anterior |
| Licencia | Derivada de la anterior (BSD-2-Clause) |
| Uso | Posición y tamaño de las 34 salas en el mapa del juego |

Las aristas del mapa **no** se leen del diagrama (la página V3 no contiene
celdas de arista): se reconstruyen desde las reglas de viaje del YAML. De este
modo el mapa y las reglas no pueden discrepar.

## 3. Partición en capítulos — editorial

| Campo | Valor |
| --- | --- |
| Origen | `06_reconstruccion_drawio/tools/oa_chapters.py` (importado, no reimplementado) |
| Naturaleza | Interpretación editorial, marcada como tal en `meta.editorial_note` |
| Uso | Decidir qué 34 salas forman el capítulo 01 |

## 4. Textos en español — reinterpretación original

| Campo | Valor |
| --- | --- |
| Origen | `godot/data/l10n_es.json`, redactado en este corte |
| Autoría | Original de este proyecto |
| Licencia | Misma que el resto del repositorio |
| Uso | Descripciones de sala, mensajes de parser, objetos, interfaz |

**No** es la traducción de *La Aventura Original* (CAAD, 1989) ni de ninguna
edición comercial. Es una reescritura con voz propia, conforme a
`03_reinterpretation/CREATIVE_BIBLE.md` (segunda persona, presente, 2-4 frases,
humor que no tapa pistas). El texto original en inglés permanece intacto en el
dataset generado y se usa como respaldo cuando falta traducción.

## 5. Ilustraciones — originales

| Campo | Valor |
| --- | --- |
| Origen | `godot/data/art_ch01.json` |
| Autoría | Original de este proyecto |
| Formato | Lista ordenada de comandos `LINE` y `FILL` con color, tal y como decide `CREATIVE_BIBLE.md` |
| Uso | Panel ilustrado de la sala actual |

El renderer (`godot/src/render/room_illustration.gd`) consume esos datos:
rasteriza las líneas y luego rellena las zonas con relleno por inundación. No
hay ni un solo asset binario de terceros en el proyecto.

## 6. Licencia del código del juego

El motor, la interfaz y las herramientas son trabajo original de este
repositorio, bajo **GPL-3.0-or-later** (ver `../LICENSE` y `../NOTICE.md`).
No se ha copiado código del C de Open Adventure: se ha reimplementado su
semántica documentada (`playermove()` en `main.c`, `lock()` en `actions.c`,
`score()` en `score.c`), citando siempre el archivo de origen.

Los datos del dungeon y los textos en inglés de Open Adventure siguen bajo
BSD-2-Clause: su inclusión no los convierte en trabajo GPL y **el material de
terceros no se relicencia**. El juego muestra la licencia y los avisos de
terceros mediante la orden `LICENSES`.

## 7. Verificaciones de procedencia ejecutadas

| Comprobación | Resultado |
| --- | --- |
| Las dos copias del YAML coinciden | PASS (comparación estructural en el exportador) |
| SHA-256 de ambas copias | PASS (registrados en `meta.source_yaml`) |
| Conjunto de salas del capítulo = nodos de la página `.drawio` | PASS (validador del exportador) |
| Todo destino de viaje existe en el capítulo o está declarado como frontera | PASS (validador del exportador + suite de tests) |
| Regeneración byte a byte del dataset | PASS (`oa_export_godot.py --check`) |
