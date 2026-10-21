# Informe del corte — Reconstrucción en Godot 4.7 del capítulo 01

> **Nota de licencia posterior:** este informe conserva las referencias AGPL
> del estado histórico que documentó. La decisión humana de
> `CAR-GIT-BASELINE-02` las ha sustituido para el baseline público por
> **GPL-3.0-or-later**. El estado vigente está en `LICENSE`, `NOTICE.md` y
> `07_godot_open_adventure/LICENSE`.

**Corte:** IF-GODOT-CH01
**Fecha:** 2026-10-20
**Petición humana:** «reconstruir el juego en Godot 4.7 y montar el primer capítulo 01-Surface World del .io».
**Resultado:** **PASS acotado** — capítulo 01 jugable, verificado en headless.
**Revisión humana:** pendiente. **Sin commits.**

## 1. Objetivo y alcance autorizado

Reconstruir en Godot 4.7 el capítulo 01 «Surface World» del diagrama
`Open_Adventure_World_V3.drawio` (página `CH_SURFACE`), tomando el código
fuente de Open Adventure y el YAML como autoridad de datos.

Dentro de alcance: motor de juego con parser, capítulo 01 completo, mapa en
juego a partir del `.io`, ilustraciones vectoriales propias, suite de tests
headless, exportador determinista y documentación de procedencia.

Fuera de alcance (no se ha hecho): capítulos 02-11, guardado de partida,
sonido, dirección de arte final, publicación, commits, plugin de editor,
router, skills o plantillas.

## 2. Estado comprobado antes de escribir

- El repositorio tenía un único commit (`2e5c9c5`) y trabajo sin confirmar en
  `.agents/`, `docs/`, `contracts/`, `experiments/` y `06_reconstruccion_drawio/`.
  Nada de eso se ha tocado.
- No existía ningún `project.godot`, `.gd` ni `plugin.cfg` en el repositorio.
- Las dos copias del YAML (`06_reconstruccion_drawio/Open_Adventure.yaml` y
  `codigo_fuente_open_adventure/adventure.yaml`) son estructuralmente idénticas
  y el SHA-256 queda registrado en el dataset.
- La página `CH_SURFACE` del `.drawio` V3 contiene 34 nodos de sala con
  geometría y **ninguna** celda de arista: las conexiones viven en el atributo
  `travel_rules` de cada nodo.
- Godot disponible en la máquina: **4.7.2-stable** (y 4.7.1 como copia de
  respaldo). Se usó 4.7.2.

## 3. Archivos creados

```
07_godot_open_adventure/
├── README.md
├── PROVENANCE.md
├── reports/RECONSTRUCTION_CH01.md
├── tools/oa_export_godot.py
├── tools/verify.ps1
└── godot/
    ├── project.godot
    ├── icon.svg
    ├── data/chapter_01_surface.json   (generado)
    ├── data/l10n_es.json
    ├── data/art_ch01.json
    ├── src/core/{travel_rule,world_location,world_object,world_data,game_state,command,command_parser,interpreter}.gd
    ├── src/render/room_illustration.gd
    ├── src/ui/{main,terminal,map_view,illustration_view}.gd
    ├── scenes/main.tscn
    ├── tests/run_tests.gd
    ├── tools/{capture,capture_scenes}.gd
    └── captures/{main,scenes}.png
```

Ningún archivo preexistente se ha modificado, salvo la adición de una sección
para el proyecto Godot en el `.gitignore` raíz.

## 4. Decisiones técnicas y su motivo

| Decisión | Motivo |
| --- | --- |
| Datos exportados a JSON generado, no escritos a mano | Mantener el YAML como única autoridad y poder regenerar y verificar byte a byte |
| Separar `l10n_es.json` del dataset generado | No sobrescribir el texto histórico con la reinterpretación, como pide el README del repositorio |
| El mapa usa la geometría del `.io` y las aristas del YAML | El diagrama aporta la forma; las reglas no pueden discrepar de la fuente |
| Movimientos reimplementados desde `playermove()` | Conservar la semántica de precedencia y el salto por condición fallida (reja cerrada) |
| Comparación de palabras por cinco letras | Es el comportamiento del original (`DOWNS` = *downstream*) |
| Puntuación según `score.c` | Evita inventar valores que la fuente no da; las clases salen de los umbrales del YAML |
| Frontiera de capítulo en vez de salas vacías | Permite ampliar el capítulo 02 sin tocar el 01 |
| Ilustraciones como datos `LINE`/`FILL` | Es la decisión registrada en `CREATIVE_BIBLE.md`: el renderer consume datos |

## 5. Comprobaciones ejecutadas y resultados

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `python tools/oa_export_godot.py --check` — el dataset comprometido coincide con el regenerado | PASS |
| 2 | Import de Godot 4.7.2 (`--editor --quit`), sin errores de script | PASS |
| 3 | Suite headless `res://tests/run_tests.gd` | **PASS — 194 comprobaciones** |
| 4 | Arranque de la escena principal en headless (`--quit-after 120`), sin errores | PASS |
| 5 | Captura de la ventana real (1440×860) | PASS — evidencia en `godot/captures/main.png` |
| 6 | Hoja de contacto de las 11 ilustraciones | PASS — `godot/captures/scenes.png` |
| 7 | `tools/verify.ps1` encadenando 1-4 y 6 | PASS |

Contenido de la suite (194 comprobaciones): integridad del dataset (34 salas,
8 objetos, 34 nodos de mapa, 118 aristas, 3 muertes, 11 clases, índice del
cofre y del zafiro según el orden de objetos de la fuente), todo destino
de viaje conocido, alcanzabilidad de las 31 salas con entrada desde
`LOC_START` y las 3 sin ella (`LOC_FOOF2`, `LOC_FOOF4`, `LOC_LEDGE`),
análisis de raíces de palabras, movimientos cardinales, refusas de dirección
imposible, reja cerrada con llave, apertura con llaves y frontera al entrar,
palabras mágicas, cloaca como callejón sin salida, objetos (coger, soltar,
inmovilidad), puntuación, avisos legales de la licencia (AGPL §5/§13) y
render de ilustraciones.

**Inspección visual:** realizada sobre la captura real de la ventana (no solo
headless). Lo que se comprobó a ojo: maquetación del terminal, mapa del
capítulo con la sala actual resaltada e iluminación de las ilustraciones.

## 6. Desviaciones respecto del original

| Punto | Original | Aquí | Motivo |
| --- | --- | --- | --- |
| Textos de sala | Inglés | Español propio | Biblia creativa; el inglés se conserva como respaldo |
| Sala inalcanzable | — | `LOC_LEDGE` sin entrada | El YAML no define ninguna regla de entrada; no se inventa |
| Cloaca | Callejón según el YAML | Igual | Comportamiento de la fuente |
| Puntuación | Completa | Solo la parte del capítulo 01 | Los demás puntos dependen de capítulos no montados |
| Pistas (hints) | Temporizadas | No implementadas | Dependen de viscosity global y enanos; fuera del capítulo |
| Enanos, Treasure Valley, fin de partida | Implementados | No | Fuera del capítulo |

Ninguna de estas desviaciones altera las reglas de viaje del capítulo 01.

## 7. Riesgos y límites que siguen abiertos

1. **`LOC_LEDGE` es inalcanzable** tal y como está el YAML; el zafiro no se
   puede recoger en este corte. Si la intención del capítulo es incluirlo,
   hace falta una decisión humana sobre la regla que falta en la fuente
   (marcada como `UNKNOWN`, no rellenada).
2. **La frontera es una decisión de diseño**, no de la fuente: el juego no
   deja pasar al capítulo 02. Si se prefiere entrar en salas no montadas, hay
   que cambiar `_execute_move()`.
3. **Ilustraciones de primera pasada.** Son legibles y datos puros, pero no
   son dirección de arte; `Jack Burton` debería revisar el brief antes de
   invertirlas en escenas definitivas.
4. **Sin guardado ni sonido.** No estaba en la petición.
5. **El proyecto Godot no está en Git.** `.godot/` está ignorado; el resto de
   archivos son nuevos y esperan decisión de commit del responsable.

## 8. Decisiones que necesita el responsable

1. ¿Se commitea `07_godot_open_adventure/` (y el ajuste del `.gitignore`)?
2. ¿El capítulo 01 debe poder entrar en el capítulo 02 (salas vacías) o se
   mantiene la frontera cerrada?
3. ¿Se autoriza una segunda pasada de ilustraciones antes de ampliar al
   capítulo 02?
4. ¿El texto en español se mantiene como reinterpretación propia o se
   autoriza trabajar sobre la traducción de *La Aventura Original* (que exige
   revisión de derechos aparte)?

## 8.bis Licencia aplicada (decisión posterior al corte)

Tras este informe se aplicó **AGPL-3.0-or-later** al trabajo original del
repositorio, a petición del responsable y «de momento»:

- `LICENSE` (raíz): texto íntegro y canónico de AGPL-3.0, descargado de
  <https://www.gnu.org/licenses/agpl-3.0.txt> (661 líneas, SHA-256
  `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0`).
- `NOTICE.md` (raíz): alcance y excepciones; el material de terceros
  (`codigo_fuente_open_adventure/`, `material_encontrado/`) conserva su
  licencia y **no** se relicencia.
- `AUTHORS.md` (raíz): autoría humana y herramientas de asistencia.
- `07_godot_open_adventure/LICENSE`: aviso del subproyecto.
- El juego muestra los avisos legales exigidos por AGPL §5 y §13 con la
  orden `LICENSES` y en la última línea de `AYUDA`; hay dos comprobaciones
  de test que lo fijan.

Pendiente: ninguno. Titular y contacto confirmados por el responsable:
**MetalWAR — <metalwar_coder@proton.me>** (ver `AUTHORS.md`).

## 9. Siguiente paso acotado sugerido

Montar el capítulo 02 (`CH_ENTRY`, 12 salas) reutilizando el mismo exportador
—basta con cambiar el parámetro de capítulo— y resolver la entrada de
`LOC_LEDGE` con una decisión explícita sobre la regla ausente.
