# NOTICE — alcance de la licencia y excepciones

## Licencia del proyecto

El trabajo original de este repositorio se publica bajo la **GNU General Public License v3.0 o posterior** (GPL-3.0-or-later).

- Texto íntegro y canónico: [LICENSE](LICENSE), copia de <https://www.gnu.org/licenses/gpl-3.0.txt>.
- Copyright: `Copyright (C) 2026 MetalWAR — <metalwar_coder@proton.me>`.
- Autoría humana y herramientas de asistencia: [AUTHORS.md](AUTHORS.md).

La GPL cubre únicamente el trabajo original de este proyecto. No cambia ni sustituye las licencias del material de terceros. Las versiones derivadas cubiertas que se distribuyan deben conservar las libertades y cumplir las condiciones de la GPL.

## Open Adventure

| Ruta | Material | Licencia | Tratamiento |
| --- | --- | --- | --- |
| `codigo_fuente_open_adventure/` salvo las nueve excepciones enumeradas debajo | Código, datos, pruebas y otros archivos de Open Adventure 2.5 que se declaran BSD-2-Clause | BSD-2-Clause; véase `codigo_fuente_open_adventure/COPYING` y los encabezados SPDX de cada archivo | Se conserva como fuente histórica y no se relicencia |
| `06_reconstruccion_drawio/Open_Adventure.yaml` | Datos de Open Adventure | BSD-2-Clause | Copia de trabajo utilizada como autoridad por el exportador |
| `06_reconstruccion_drawio/output/**` | Diagramas y vistas derivados del YAML | BSD-2-Clause como material derivado de esos datos | Se mantienen separados del trabajo original GPL |
| `07_godot_open_adventure/godot/data/chapter_01_surface.json` | Transformación determinista del YAML | BSD-2-Clause | Archivo generado; no editar manualmente |

### Documentación CC-BY-4.0

Los siguientes siete documentos AsciiDoc declaran
`SPDX-License-Identifier: CC-BY-4.0` y
`SPDX-FileCopyrightText: (C) Eric S. Raymond <esr@thyrsus.com>`:

- `codigo_fuente_open_adventure/advent.adoc`
- `codigo_fuente_open_adventure/hints.adoc`
- `codigo_fuente_open_adventure/history.adoc`
- `codigo_fuente_open_adventure/INSTALL.adoc`
- `codigo_fuente_open_adventure/NEWS.adoc`
- `codigo_fuente_open_adventure/notes.adoc`
- `codigo_fuente_open_adventure/README.adoc`

Se atribuyen a **Eric S. Raymond** conforme a sus encabezados originales. No se
modificaron durante `CAR-GIT-BASELINE-04`; mantienen sus avisos de autoría y
licencia. Texto legal oficial de Creative Commons Attribution 4.0 International:
<https://creativecommons.org/licenses/by/4.0/legalcode.en>.

### Utilidades MIT-0

Las siguientes dos utilidades declaran `SPDX-License-Identifier: MIT-0` y
`SPDX-FileCopyrightText: (C) Eric S. Raymond <esr@thyrsus.com>`:

- `codigo_fuente_open_adventure/tests/tapdiffer`
- `codigo_fuente_open_adventure/tests/tapview`

Sus encabezados originales no se modificaron durante `CAR-GIT-BASELINE-04`.
Ambos indican además que una versión más reciente puede encontrarse en
<https://gitlab.com/esr/tapview>.
Texto identificable de MIT No Attribution (`MIT-0`):
<https://spdx.org/licenses/MIT-0.html>.

Las nueve excepciones anteriores no se describen como BSD-2-Clause ni quedan
relicenciadas por su inclusión en este repositorio.

El motor GDScript reimplementa comportamiento documentado de Open Adventure, pero no copia el código C. Los textos españoles, ilustraciones y código original del proyecto se publican bajo GPL-3.0-or-later. La procedencia detallada se registra en [07_godot_open_adventure/PROVENANCE.md](07_godot_open_adventure/PROVENANCE.md).

## GUT 9.7.1

`07_godot_open_adventure/godot/addons/gut/` contiene GUT (Godot Unit Test)
9.7.1, de Tom "Butch" Wesley y sus contribuidores, obtenido del proyecto
<https://github.com/bitwes/Gut> para Godot 4.7. Se redistribuye sin
modificaciones intencionales como dependencia de desarrollo bajo licencia MIT;
el texto y aviso de copyright se conservan en
`07_godot_open_adventure/godot/addons/gut/LICENSE.md`.

El subdirectorio `fonts/` incluye las familias Anonymous Pro, Courier Prime y
Lobster Two. GUT las distribuye bajo SIL Open Font License 1.1 y conserva el
texto correspondiente en
`07_godot_open_adventure/godot/addons/gut/fonts/OFL.txt`, incluido su aviso y
Reserved Font Name para Anonymous Pro. Las fuentes no se presentan como trabajo
propio ni quedan relicenciadas por la GPL del proyecto.

GUT está activado en `project.godot` como plugin del editor y disponible para
pruebas futuras, pero no sustituye ni ejecuta la suite existente de 400
comprobaciones.

## Material excluido de la publicación

La copia pública se ha construido mediante lista positiva. No contiene:

- `material_referencia_no_redistribuible/`: capturas, transcripciones, guías, mapas y portadas de terceros utilizadas únicamente como referencia interna.
- WinAPE, ROM de Amstrad CPC, imágenes de disco, descompresores u otros binarios históricos de terceros.
- La distribución local de diagrams.net/draw.io.
- Los ejecutables locales de Godot y la distribución local de ripgrep bajo
  `tools/`; sus rutas concretas se excluyen en `.gitignore` sin excluir el
  directorio `tools/` de forma general.
- GDToolkit y sus dependencias instaladas en el entorno local de Python.
- `07_godot_open_adventure/logo/4mad.png`, cuya procedencia no está suficientemente documentada para redistribuirlo.
- Configuración local de agentes, sesiones, credenciales, cachés y artefactos temporales.

La ausencia de estos materiales es deliberada. No deben recuperarse desde otros árboles o historiales sin una revisión de derechos independiente.

## Avisos legales de la aplicación

La aplicación muestra avisos mediante:

- `AYUDA` / `HELP`, en la última línea.
- `LICENSES`, que presenta el aviso, la ubicación del código fuente y la distinción entre el trabajo GPL-3.0-or-later y los datos BSD-2-Clause consumidos por el juego.

Una distribución debe cumplir la GPL, facilitar el código fuente correspondiente cuando resulte exigible y conservar los avisos y condiciones BSD-2-Clause, CC-BY-4.0 y MIT-0 aplicables.

## Steamworks

**Estado: PENDING / NOT INTEGRATED.** Este baseline no contiene el SDK de
Steamworks, plugins, puentes, logros, DRM ni dependencias de servicios
externos. El juego debe poder ejecutarse sin Steam. Una posible integración
futura requerirá un corte separado y una revisión jurídica: que un puente sea
software abierto no garantiza por sí solo la compatibilidad de la combinación
o de su distribución con GPL-3.0-or-later y con las condiciones de Steamworks.

## Regla práctica

La disponibilidad de un archivo no equivale a permiso de redistribución. Todo material externo conserva su licencia y atribución; la licencia raíz no lo convierte en trabajo propio.
