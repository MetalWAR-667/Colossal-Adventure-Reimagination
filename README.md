# Colossal Adventure: Reimagination

Proyecto de investigación de **RPG Archaeology** dedicado a reconstruir, estudiar y reinterpretar *Colossal Cave Adventure* a partir de Open Adventure, manteniendo separadas la fuente histórica, las transformaciones reproducibles y el juego ejecutable.

**Estado:** el capítulo 01, «El Mundo de la Superficie», es jugable en Godot 4.7.2 y cuenta con una presentación visual original integrada. Las ilustraciones de CH_01 tienen aceptación humana; la revisión integral de la experiencia gráfica y de juego sigue pendiente. Los capítulos 02–11 no están implementados.

## Objetivos y límites

- Estudiar el mapa, el parser y las reglas de viaje con evidencia trazable.
- Mantener el YAML de Open Adventure como autoridad de los datos históricos.
- Construir una reinterpretación propia sin alterar silenciosamente las reglas de la fuente.
- Usar comandos escritos como canal principal de interacción.
- Comparar el trabajo asistido por IA mediante un protocolo reproducible.

Este repositorio no intenta completar todo el juego de una vez ni validar automáticamente la fidelidad de cada transición. El alcance implementado es un capítulo cerrado; las discrepancias o ausencias de la fuente se documentan, no se rellenan por intuición.

## Estado del experimento

- Reconstrucción cartográfica determinista del mundo de Open Adventure en diagrams.net.
- Exportador reproducible de YAML a los datos JSON consumidos por Godot.
- Aplicación independiente en Godot 4.7 con parser, estado e intérprete únicos.
- Overlay de depuración `IF-GODOT-DEBUG-01`: `Tab` alterna juego y grafo conservando el parser operativo, la cámara y la última transición observada.
- Dirección artística CAR V1: **C — Línea solar**, con ilustraciones vectoriales originales. La reproducción dibuja contornos `LINE` progresivamente y revela los rellenos `FILL` de forma espacial, en aproximadamente 3,5 segundos a velocidad 1×.
- Once escenas visuales de CH_01 están integradas y aceptadas: `LOC_START`, nueve ilustraciones producidas en CAR-ART-004 y `LOC_GRATE`, que cuenta con las variantes `GRATE_CLOSED` / `GRATE_OPEN`. No equivalen a once localizaciones jugables; varias salas comparten ilustración, como `LOC_FOREST`.
- En `LOC_GRATE`, la variante se selecciona leyendo el estado existente de `GameState`; no añade reglas de viaje ni un estado paralelo.
- Distribución de juego: ilustración → narración → grafo y salidas → entrada de comandos. `Tab` abre el modo de depuración con el grafo y sin ilustración; el terminal continúa disponible.
- La aceptación de las ilustraciones no equivale a una validación humana integral de la experiencia de juego, que sigue pendiente.

### Arte, interfaz y limitaciones actuales

La dirección **C — Línea solar** busca una presentación luminosa y legible que conserve el espíritu vectorial clásico con herramientas actuales. El trazado `LINE` muestra el avance de los contornos; `FILL` revela progresivamente las regiones. La duración observada ronda los 3,5 segundos; los tiempos de preparación previos al dibujo son adicionales.

La [galería de CH_01](project_state/changes/car_art_004_ch01_vector_illustration_production/gallery.html) reúne las nueve ilustraciones del lote CAR-ART-004. La [galería de las variantes de la reja](project_state/changes/car_art_005_state_aware_illustration_selection_i/gallery.html) muestra `GRATE_CLOSED` y `GRATE_OPEN`. Los informes de decisión y producción están en [CAR-ART-001](project_state/changes/car_art_001_vector_direction_gate/CHANGE.md), [CAR-ART-002](project_state/changes/car_art_002_vector_drawing_playback_prototype/CHANGE.md), [CAR-ART-003](project_state/changes/car_art_003_runtime_illustration_ui_integration_i/CHANGE.md), [CAR-ART-004](project_state/changes/car_art_004_ch01_vector_illustration_production/CHANGE.md) y [CAR-ART-005](project_state/changes/car_art_005_state_aware_illustration_selection_i/CHANGE.md).

El grafo principal permanece visible durante el desarrollo. Siguen pendientes su pulido final y ajustes de la interfaz. `GRATE_OPEN` está aceptada provisionalmente y queda pendiente de pulido artístico final. La preparación medida de las variantes de GRATE es de 4,189–4,243 s en el equipo de captura; es un coste anterior al dibujo y no una garantía para otros equipos. La expansión de la simulación necesaria para CH_02 también está pendiente.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `00_candidates/` | Selección histórica y criterios de candidatura |
| `01_sources/` | Registro de fuentes y derechos |
| `02_archaeology/` | Análisis de salas, parser, objetos y progresión |
| `03_reinterpretation/` | Biblia creativa y registro de assets |
| `04_agent_experiment/` | Protocolo del experimento asistido |
| `05_evaluation/` | Rúbrica de evaluación humana y técnica |
| `06_reconstruccion_drawio/` | YAML, herramientas, diagramas, informes y previsualizaciones |
| `07_godot_open_adventure/` | Juego Godot, exportador, pruebas, informes y procedencia |
| `codigo_fuente_open_adventure/` | Fuente histórica de Open Adventure; inventario BSD-2-Clause, CC-BY-4.0 y MIT-0 en `NOTICE.md` |
| `contracts/` | Contratos documentales de roles y verificación utilizados por MetalLabs |
| `docs/` | Evidencia histórica de extracción y reconciliación de contratos |

## Requisitos

- Godot 4.7.2 estable.
- Python 3.
- PyYAML 6.x (`python -m pip install PyYAML`).
- PowerShell para el verificador integral en Windows.

El juego no requiere Python para ejecutarse. PyYAML solo es necesario para
regenerar o verificar los datos derivados de Open Adventure.

Herramientas de desarrollo auditadas para este baseline:

- GDToolkit 4.5.0 (`gdlint` y `gdformat`), instalación local opcional mediante
  `python -m pip install gdtoolkit==4.5.0`; no se redistribuye en el repositorio.
- GUT 9.7.1 en `07_godot_open_adventure/godot/addons/gut/`, dependencia de
  pruebas vendorizada bajo MIT y activada como plugin del editor. Está
  disponible para pruebas futuras, pero no ejecuta ni sustituye la suite actual
  del proyecto.
- Los ejecutables locales de Godot 4.7.2 y la distribución local de ripgrep
  15.2.0 bajo `tools/` están excluidos mediante rutas específicas en
  `.gitignore`; cada colaborador debe obtenerlos de sus fuentes oficiales.

El diagnóstico de estilo se ejecuta, sin aplicar cambios, desde
`07_godot_open_adventure/godot/` con `gdlint src` y `gdformat --check src`.

## Ejecutar el juego

Desde la raíz del repositorio:

```powershell
& "C:\ruta\Godot_v4.7.2-stable_win64.exe" --path 07_godot_open_adventure\godot
```

En el juego, escribe comandos en el terminal. `Tab` abre o cierra el grafo de depuración sin abandonar el parser.

## Verificación reproducible

```powershell
# Exportación determinista YAML → JSON
python 07_godot_open_adventure/tools/oa_export_godot.py --check

# Exportación, importación Godot, tests headless y hoja de escenas
powershell -ExecutionPolicy Bypass -File 07_godot_open_adventure/tools/verify.ps1
```

El verificador necesita localizar Godot 4.7.2. Consulta [el README del corte](07_godot_open_adventure/README.md) y su [informe técnico](07_godot_open_adventure/reports/RECONSTRUCTION_CH01.md) para conocer la cobertura y las limitaciones.

Resultados comunicados en los cortes verificados; no representan una suma de
pruebas independientes y algunas aserciones se repiten entre modos y suites:

| Alcance | Resultado registrado |
| --- | ---: |
| Baseline público histórico | 400 comprobaciones |
| Suite actual del juego | 448 comprobaciones |
| Prototipo `LOC_START` | 66 comprobaciones |
| Integración/fallback | 62 comprobaciones |
| Lote artístico CAR-ART-004 | 455 headless y 582 gráficas |
| Variantes GRATE CAR-ART-005 | 150 headless y 180 gráficas |

Las aceptaciones humanas de las ilustraciones corresponden a sus cortes
artísticos. La revisión integral de la experiencia gráfica y de juego de CH_01
sigue pendiente; las comprobaciones automatizadas no la sustituyen.

## Autoría, licencias y procedencia

- [Autoría humana y asistencia](AUTHORS.md)
- [Licencia del trabajo original](LICENSE): GPL-3.0-or-later
- [Avisos y excepciones](NOTICE.md)
- [Procedencia del proyecto Godot](07_godot_open_adventure/PROVENANCE.md)
- `codigo_fuente_open_adventure/COPYING`: BSD-2-Clause para los archivos que así lo declaran; las excepciones CC-BY-4.0 y MIT-0 se enumeran en `NOTICE.md`

El material histórico sin autorización de redistribución, las herramientas
locales y los ejecutables externos no forman parte de este repositorio público.
GUT es la excepción documentada: una dependencia de desarrollo redistribuible
que conserva en su propio directorio los avisos MIT y SIL OFL aplicables.

## Steamworks

**Estado: PENDING / NOT INTEGRATED.** Una posible integración futura deberá ser
opcional: el juego debe seguir funcionando sin Steam, sin DRM y sin servicios
externos. Este baseline no incluye SDK, plugin ni puente de Steamworks. El hecho
de que un puente sea abierto no demuestra por sí solo que su combinación y
distribución sean jurídicamente compatibles; esa evaluación queda pendiente.
