# 07 — Reconstrucción en Godot 4.7 (Capítulo 01: El Mundo de la Superficie)

**Estado:** CAPÍTULO 01 JUGABLE / VERIFICADO EN HEADLESS — revisión humana pendiente.
**Origen de los datos:** Open Adventure (Eric S. Raymond), BSD-2-Clause.
**Mapa de referencia:** `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio`, página `01 — Surface World` (`CH_SURFACE`).

Este corte reconstruye en Godot 4.7 el primer capítulo de la aventura, tomando
como única autoridad de datos el YAML de Open Adventure y como referencia
visual el diagrama `.io` ya publicado en el repositorio.

## Qué contiene

```
07_godot_open_adventure/
├── README.md                     este documento
├── PROVENANCE.md                 licencias, procedencia y trazabilidad
├── reports/
│   └── RECONSTRUCTION_CH01.md    informe del corte (estado, pruebas, límites)
├── tools/
│   ├── oa_export_godot.py        exportador determinista YAML → JSON de Godot
│   └── verify.ps1                verificación de un comando
└── godot/                        proyecto Godot 4.7
    ├── project.godot
    ├── data/
    │   ├── chapter_01_surface.json  GENERADO — no editar a mano
    │   ├── l10n_es.json             texto en español (reinterpretación)
    │   └── art_ch01.json            ilustraciones vectoriales (LINE + FILL)
    ├── src/core/                motor tipado (datos, parser, intérprete)
    ├── src/render/              rasterizador de ilustraciones
    ├── src/ui/                  terminal, mapa e ilustración
    ├── scenes/main.tscn
    ├── tests/run_tests.gd       suite headless
    └── tools/                   capturas de pantalla
```

## Cómo ejecutarlo

```powershell
# Ejecutar el juego
& "C:\ruta\Godot_v4.7.2-stable_win64.exe" --path 07_godot_open_adventure\godot

# Verificar todo (exportación, import, tests, ilustraciones)
powershell -ExecutionPolicy Bypass -File 07_godot_open_adventure\tools\verify.ps1
```

El binario usado en esta máquina es **Godot 4.7.2-stable**; el proyecto declara
`config/features=PackedStringArray("4.7", "GL Compatibility")`.

## Reglas de la reconstrucción

- **El YAML manda.** Las salas, las reglas de viaje, las condiciones, los
  objetos y los mensajes se exportan sin alterar su semántica. El movimiento
  reproduce `playermove()` de `codigo_fuente_open_adventure/main.c`: gana la
  primera regla cuyo verbo coincide y, si su condición falla, se salta a la
  siguiente regla con destino distinto (por eso «entrar en la reja» se
  convierte en «la reja está cerrada con llave»).
- **El parser conserva el vocabulario del original.** Las palabras se comparan
  por sus cinco primeras letras, igual que en la fuente (`DOWNS` = *downstream*,
  `INWAR` = *inwards*).
- **El diagrama aporta la forma, no las reglas.** Las posiciones de las salas
  del mapa en juego salen de la página `CH_SURFACE` del `.drawio`; las aristas
  se reconstruyen desde las reglas de viaje del YAML.
- **El texto en español es reinterpretación propia**, separado del archivo
  generado. No es la traducción de *La Aventura Original* ni de ninguna edición
  comercial: es una reescritura con la voz de `03_reinterpretation/CREATIVE_BIBLE.md`.
- **La puntuación es la del original** (`score.c`): supervivencia, tesoro
  encontrado, tesoro entregado a la casita y redondeo; las clases salen de los
  umbrales del YAML.

## Licencias

- El trabajo original de este proyecto: **GPL-3.0-or-later**, obra de
  **MetalWAR** (<metalwar_coder@proton.me>), con ayuda de Minimax, Gemini y
  OpenCode (ver [`AUTHORS.md`](../AUTHORS.md)). Texto íntegro en el
  [`LICENSE`](../LICENSE) de la raíz y aviso de excepciones en
  [`NOTICE.md`](../NOTICE.md); el juego muestra los avisos legales con la
  orden `LICENSES`.
- Datos del dungeon y textos en inglés: Open Adventure, **BSD-2-Clause**
  (Eric S. Raymond). No se relicencian: conservan su licencia y su aviso.
- Textos en español e ilustraciones: originales de este proyecto, GPL.
- Detalle en [PROVENANCE.md](PROVENANCE.md).

## Frontier de capítulo

El capítulo 01 es una rebanada cerrada. Cuatro reglas apuntan fuera:

| Destino | Desde | Qué ocurre |
| --- | --- | --- |
| `LOC_BELOWGRATE` | `LOC_GRATE` | entrar en la reja abre el capítulo 02 |
| `LOC_FOOF1` | `LOC_BUILDING` | «xyzzy» en la casita |
| `LOC_FOOF3` | `LOC_BUILDING` | «plugh» en la casita |
| `LOC_NOMAKE` | `LOC_CLIFF`, `LOC_LEDGE` | saltar al vacío |

El motor anuncia el límite y no cambia de sala, de modo que el capítulo se
puede ampliar más adelante sin tocar el capítulo 01.

## Bucle jugable del capítulo

1. `E` (o `ENTER`) — entrar en la casita.
2. `TAKE KEYS` — coger las llaves.
3. `OUT`, `DEPRESSION` — volver a la depresión de la reja.
4. `UNLOCK GRATE` — abrir la reja (el original solo la abre quien lleva las llaves).
5. `ENTER` — el paso al capítulo 02.

Además: la `LAMP` se puede encender y apagar, la `BOTTLE` se llena en el
arroyo y se vierte, y el zafiro de la cornisa (`LOC_LEDGE`) se puede llevar a
la casita para sumar puntos, aunque la cornisa todavía no tenga entrada desde
la superficie (el YAML no da ninguna regla de entrada: ver el informe).

## Limitaciones conocidas

- Solo el capítulo 01: 34 salas, 8 objetos, 4 mensajes arbitrarios y un puñado
  de acciones (coger, soltar, inventario, abrir/cerrar, encender/apagar, beber,
  llenar, verter, escuchar, puntuación, ayuda, salir). El resto del mundo no
  está exportado.
- `LOC_LEDGE` no tiene ninguna regla de entrada en el YAML entero, ni dentro
  del capítulo ni fuera de él; el zafiro queda por tanto inaccesible en este
  corte. Se deja como está en la fuente, sin inventar la regla que falta.
- `LOC_SEWER` es un callejón sin salida en el YAML (su única regla es el
  retorno implícito); así se comporta.
- Las ilustraciones son una primera pasada: 11 escenas en trazo vectorial con
  relleno por inundación, no una dirección de arte final.
- No hay guardado de partida ni sonido: el alcance del corte es la
  reconstrucción del capítulo y su verificación.

## Licencias

- Código de datos y lógica: trabajo original de este repositorio.
- Datos del dungeon: Open Adventure, BSD-2-Clause (Eric S. Raymond).
- Ilustraciones y textos en español: originales de este proyecto.
- Detalle en [PROVENANCE.md](PROVENANCE.md).
