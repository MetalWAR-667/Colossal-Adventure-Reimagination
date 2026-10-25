# CAR-ART-004 — CH_01 Vector Illustration Production

**Estado final:** `CLOSED / PASS — WITH DOCUMENTED EXCEPTION`.
Nueve ilustraciones nuevas: `IMPLEMENTED / TECHNICAL PASS / HUMAN ACCEPTED`.
`LOC_START` conserva su aceptación previa. `GRATE: DEFERRED / STATE-DEPENDENT
ILLUSTRATION`, excluida y no contabilizada como completada. Fecha de cierre:
2026-10-25. Producción artística: Jack Burton / Codex; soporte técnico acotado:
selección de recursos, pruebas y captura.

[Galería de CH_01](gallery.html) · [Índice y fichas](REVIEW.md) ·
[Lámina del lote](evidence/contact_sheet.png) · [Métricas](evidence/metrics.json)

## Autorización, contrato y baseline

Preflight: repositorio `C:\remake\Colossal-Adventure-Reimagination-public`, `main`,
HEAD `1a869a18430367b528283ac63830840e29703b1d`, índice/árbol limpios y referencia
local `origin/main` coincidente. No se consultó el remoto en vivo. Se utilizó
acceso explícito al repositorio hermano, sin alterar permisos permanentes o Git.
Se revisaron Biblia Creativa, CAR-ART-001/002/003 y datos/evidencia de START.

Antes de producir se consolidó el
[contrato artístico](../../../03_reinterpretation/CH01_VECTOR_ART_CONTRACT.md):
C — Línea solar, 736 × 400, tinta/paleta de START, curvas suavizadas a polilíneas,
regiones cerradas, 1,4 / 0,7 / 1,4 s y resultado final idéntico a Omitir. Las
composiciones son originales de este lote; se reutiliza vocabulario de árboles,
rocas y materiales, no la escena de START completa. No hay assets externos.

El inventario detectó que GRATE necesita coherencia GRATE_CLOSED/GRATE_OPEN y el
adaptador no recibe estado. Se solicitó decisión antes de añadir esa capacidad.
El responsable eligió: **«Dejar GRATE como excepción bloqueada y producir las
otras nueve»**. No se implementa selector por estado, no se produce una pieza
nueva de GRATE y su respaldo heredado está excluido del PASS del lote.

## Inventario y resultado individual

Hay once dibujos heredados: START aceptado, nueve piezas producidas y GRATE
bloqueada. FOREST es un alias visual, no una sala inventada: se usa para las
22 salas canónicas LOC_FOREST1…LOC_FOREST22 con la misma descripción.
Cada ficha conserva descripción histórica literal, referencia heredada,
elementos imprescindibles, relaciones, estados y captura dentro de la UI.

| Dibujo / ficha | Trazos / regiones | Preparación gráfica | Playback | Estado |
| --- | --- | --- | --- | --- |
| [FOREST](scenes/LOC_FOREST.md) | 43 / 14 | 2,083880 s | 3,510644 s | TECHNICAL PASS / HUMAN PENDING |
| [BUILDING](scenes/LOC_BUILDING.md) | 39 / 9 | 2,493728 s | 3,515965 s | TECHNICAL PASS / HUMAN PENDING |
| [ROADEND](scenes/LOC_ROADEND.md) | 41 / 15 | 2,147747 s | 3,512597 s | TECHNICAL PASS / HUMAN PENDING |
| [HILL](scenes/LOC_HILL.md) | 35 / 18 | 2,410165 s | 3,516730 s | TECHNICAL PASS / HUMAN PENDING |
| [VALLEY](scenes/LOC_VALLEY.md) | 39 / 18 | 2,110927 s | 3,514499 s | TECHNICAL PASS / HUMAN PENDING |
| [SLIT](scenes/LOC_SLIT.md) | 22 / 10 | 3,271284 s | 3,514113 s | TECHNICAL PASS / HUMAN PENDING |
| [CLIFF](scenes/LOC_CLIFF.md) | 27 / 13 | 2,161316 s | 3,501062 s | TECHNICAL PASS / HUMAN PENDING |
| [LEDGE](scenes/LOC_LEDGE.md) | 32 / 15 | 2,645944 s | 3,515618 s | TECHNICAL PASS / HUMAN PENDING |
| [SEWER](scenes/LOC_SEWER.md) | 23 / 13 | 3,180843 s | 3,510946 s | TECHNICAL PASS / HUMAN PENDING |
| [GRATE](scenes/LOC_GRATE.md) | Sin pieza nueva | No medida | No medida | BLOCKED / EXCLUIDA |

Total nuevo: **301 trazos y 125 regiones**. Máscaras y semillas válidas,
sin celdas de fondo descubiertas; igualdad exacta final/Omitir en las nueve.
La revisión técnica de márgenes, siluetas, profundidad y fidelidad se realizó
sobre capturas reales. La tabla registra el estado de cada pieza al presentar
el lote; la aceptación humana posterior se registra en el cierre documental.

## Decisiones de representación

Fondos ambientales estables: no se fijan KEYS, LAMP, FOOD, BOTTLE o SAPPH en
una imagen que podría contradecir objetos recogidos. El terminal conserva su
descripción real. CLIFF muestra la silueta de la urna empotrada, sin afirmar
aceite o llama. Esto no implementa capas dinámicas ni elimina objetos del mundo.

Las composiciones distinguen casa/manantial, final del camino, loma, agua sobre
roca, grieta estrecha, abismo sin descenso, cornisa sin salida y dos tuberías
pequeñas. No se añaden puentes, escaleras o entradas. La cámara no traduce
izquierda/derecha de pantalla a puntos cardinales. SEWER conserva DEEP/ausencia
de LIT en datos; no se añade una lámpara ni lógica de oscuridad.

## Integración mínima y respaldo

El selector `IllustrationView` añade un registro de nueve fuentes nuevas,
alias FOREST y una vista preparada en caché por recurso. El consumidor y formato
LINE/FILL conservan su algoritmo y formato. Se cancela/oculta la vista anterior y se conserva
la política de revisita/finalización de CAR-ART-003. El cacheado es de recursos
visuales, no un nuevo estado de partida. El juego mantiene su único intérprete.

`art_ch01.json` y sus once dibujos permanecen intactos como referencia/fallback.
GRATE sigue por esa vía, con su limitación estática preexistente. START, su JSON,
modelo de raster/reproducción, demo y evidencia aceptada no se modifican. Tampoco cambian main.gd,
layout, terminal, grafo, parser, GameState, datos históricos, YAML o exportador.

La captura reveló un defecto preexistente del consumidor de presentación:
completar durante la preparación marcaba el modelo como final sin publicar
textura/contornos. Se añade `_update_picture()` tras ese `model.skip()` en
`playback_view._enter_start()`. Es soporte técnico mínimo de refresco, sin nuevas
primitivas o cambios al algoritmo. Se exige ahora la igualdad de textura y
contornos publicados para las nueve salas después de TAB durante preparación.
Las capturas anteriores de esta ejecución que estaban en blanco se regeneraron
tras el correctivo; no se alteró evidencia histórica aceptada.

La prueba de CAR-ART-003 fijaba explícitamente el piloto START + arte heredado.
Ahora declara ese registro de fixture en su preparación para conservar **todas
sus aserciones** del fallback. No se cambian expectativas a verde: la selección
productiva actual se prueba separadamente en `test_ch01_vector_art.gd`.

## Archivos

**62 archivos** del corte, inventario explícito al finalizar:

- Modificados: `godot/src/ui/illustration_view.gd`,
  `godot/tests/test_runtime_illustration.gd`, `tools/verify.ps1` bajo
  `07_godot_open_adventure/`, el refresco de
  `godot/experiments/vector_playback/playback_view.gd`, y `project_state/CURRENT_STATE.md`.
- Nuevos: nueve JSON en `godot/data/vector_ch01/`; prueba
  `godot/tests/test_ch01_vector_art.gd` y `.uid`; herramientas acotadas
  `tools/build_ch01_vector_art.py` y `tools/package_ch01_vector_review.py`.
- Documentación: contrato artístico, este CHANGE, REVIEW, galería y diez fichas.
- Evidencia: nueve finales PNG, nueve capturas de runtime, nueve GIFs muestreados,
  referencia heredada de GRATE, lámina y métricas: 30 archivos.

No se regenera el manifiesto histórico. No se añaden dependencias al runtime.
El autor usa biblioteca estándar Python y las primitivas ya versionadas; el
empaquetado opcional usa Pillow existente. Arial del sistema solo rotula la
lámina: no se redistribuye el archivo de fuente.

## Verificación y reproducción

Godot `4.7.2.stable.official.ed1daf0bf`, Windows, OpenGL Compatibility / RTX 3070.

```powershell
$Godot = 'C:\remake\Colossal-Adventure-Reimagination-public\tools\Godot_v4.7.2-stable_win64_console.exe'
python 07_godot_open_adventure/tools/build_ch01_vector_art.py --check
& ./07_godot_open_adventure/tools/verify.ps1 -Godot $Godot
& $Godot --headless --path 07_godot_open_adventure/godot --script res://experiments/vector_playback/test_playback.gd
$frames = Join-Path $env:TEMP 'CAR-ART-004-frames'
& $Godot --path 07_godot_open_adventure/godot --max-fps 60 --script res://tests/test_ch01_vector_art.gd -- --output "$PWD/project_state/changes/car_art_004_ch01_vector_illustration_production/evidence" --frames $frames
python 07_godot_open_adventure/tools/package_ch01_vector_review.py $frames
```

- Exportación histórica determinista, importación y hoja heredada de 11 escenas:
  PASS. **448 checks originales del juego**, **66 del prototipo START** y
  **62 del fixture de integración/fallback** se conservan y pasan.
- Suite específica del lote: **455 checks headless**; comparación con máscaras
  independientes Python, cobertura, semillas/conectividad, bounds, duración,
  final/Omitir desde tres momentos, cancelación y revisitas.
- **582 checks gráficos, 0 fallos**: los anteriores más 90 guardados de muestras,
  nueve finales, nueve medidas de reloj, nueve igualdades de píxeles, nueve
  capturas de UI y una referencia heredada de GRATE. Son aserciones, no 573
  pruebas independientes ni tests GUT. No se suman como casos únicos las mismas
  comprobaciones repetidas en ambos modos.
- Escena principal real: cada fuente y los 22 alias pasan por el selector;
  Enter/LOOK durante preparación y TAB se envían al viewport. El consumidor
  anterior se oculta y no continúa dibujando. Intérprete/objetos se preservan.
  La colocación directa del jugador en capturas es un fixture de inspección;
  no se añade una ruta de viaje ni se afirma accesibilidad nueva de LEDGE.
- Primer intento: dos bordes de agua discrepaban entre el raster Python double
  y Vector2 float de Godot al coincidir con semipíxeles. Se desplazaron esos
  dos motivos y sus contornos 0,0625 px; todas las máscaras vuelven a coincidir.
  Se corrigieron solapes de tinta por autoría de contornos, no por cambios al
  renderer. Un error de lista de duraciones del empaquetador GIF se corrigió
  antes de generar la galería final. Las pruebas no ocultan esos intentos.
- El readback de `ImageTexture.update()` no acredita píxeles en el servidor
  dummy headless: una sonda temporal 2 × 2 devuelve azul inicial tras actualizar
  a rojo, mientras las capturas gráficas reales sí pasan. La comprobación nueva
  dio nueve fallos por esa limitación; ahora headless exige contornos publicados
  y la ejecución gráfica exige además la textura actualizada. No se declara
  validación de píxeles headless ni se rebaja la comparación gráfica exacta.

## Límites, revisión y finalización

La preparación gráfica varía entre **2,084 y 3,271 s**, separada del dibujo:
no se presenta como resuelta la limitación inicial de START (~1,571 s). Las
nuevas escenas contienen otras áreas/regiones; no se optimizó el renderer.
El playback observado queda entre **3,501 y 3,517 s**. Son mediciones de este
equipo, sin garantía para otros ni benchmark de cambios rápidos por todas las
salas; la caché por recurso puede aumentar memoria y preparación concurrente.

Los GIFs usan frames reales, cuantización de paleta, intervalos aproximados y
una pausa final añadida. Los PNG y métricas acreditan igualdad/render, no la
aceptación artística. Las capturas SubViewport no acreditan portapapeles,
monitores o interacción física humana. El layout y su límite de legibilidad
del grafo a 720p siguen siendo los aceptados/documentados en CAR-ART-003.

El responsable revisó y probó las nueve ilustraciones nuevas y otorgó
**CAR-ART-004 — HUMAN ACCEPTANCE / PASS (9 SCENES)** el 2026-10-25. La aceptación
cubre exclusivamente estas nueve piezas; no completa las diez ilustraciones
inicialmente inventariadas. `LOC_START` mantiene su aceptación previa y no forma
parte del lote nuevo. La galería, fichas, capturas y métricas enlazadas arriba
son las evidencias existentes del lote.

### Cierre humano y estado documental

- Las nueve piezas quedan `IMPLEMENTED / TECHNICAL PASS / HUMAN ACCEPTED`.
- CAR-ART-004 queda `CLOSED / PASS — WITH DOCUMENTED EXCEPTION`.
- `GRATE` queda `DEFERRED / STATE-DEPENDENT ILLUSTRATION`: requiere representar
  GRATE_CLOSED/GRATE_OPEN; no se produjo ni aceptó una ilustración nueva y no se
  cuenta como completada. El respaldo heredado conserva su compatibilidad y su
  limitación estática preexistente.
- Las ilustraciones heredadas restantes siguen disponibles mediante el
  consumidor/fallback existente; el registro del corte confirma que no se
  cambió `art_ch01.json` ni el formato del renderer.
- Se conservan los resultados ya ejecutados: exportador determinista e
  importación PASS; 448 checks originales, 66 del prototipo START, 62 del
  fixture de integración/fallback, 455 checks headless del lote y 582 checks
  gráficos. No se repitieron suites para este cierre documental. Los checks
  gráficos incluyen pruebas de render y equivalencia final/Omitir; no se
  describen como 582 pruebas independientes ni como tests GUT.
- La preparación gráfica medida para las nueve piezas sigue siendo una
  limitación documentada de **2,084–3,271 s** en el equipo de prueba. No se
  afirma que se haya optimizado ni que esas cifras se generalicen a otros equipos.
- El cierre es documental y no cambia CH_02 ni CAR-CORE-001. La limitación de
  reproducción HTML conceptual y los pendientes generales de revisión gráfica
  del proyecto no se convierten en aceptación de todo CH_01.

La reconciliación se limita a este CHANGE y `project_state/CURRENT_STATE.md`.
CAR-AUTO-001 se aplica con inventario explícito para un commit local y
sincronización verificada a Drive. **NO PUSH**. La sincronización preserva extras
y no ofrece bloqueo atómico ante ediciones simultáneas en Drive.
