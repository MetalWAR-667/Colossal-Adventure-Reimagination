# CAR-ART-002 — Vector Drawing Playback Prototype

Estado: **IMPLEMENTED / TECHNICAL VERIFICATION COMPLETE / MANUAL_VALIDATION PENDING**.
Resultado de entrega: **PARTIAL**, pendiente de que el responsable contemple y acepte la animación real. Prototipo experimental, sin integración productiva. Fecha: 2026-10-25. Agente: Sol, implementación asistida por Codex.

## Autorización y baseline

Encargo humano CAR-ART-002: implementar una única ilustración experimental `LOC_START` en Godot 4.7.2, con dirección **C — Línea solar**, contornos interpolados, rellenos espaciales y objetivo de 3,5 segundos a 1×. Se admite expresamente una escena de prueba si integrar la UI introduce riesgo. La elección humana procede de [CAR-ART-001](../car_art_001_vector_direction_gate/CHANGE.md); no se repite su investigación ni se modifican sus estudios.

Preflight: raíz `C:\remake\Colossal-Adventure-Reimagination-public`, rama `main`, HEAD `1d05575bea81c74babc2fc0ac586863cca8ef8de`, índice/árbol limpios. La referencia local `origin/main` coincide en ese preflight; no se consultó el remoto en vivo. Se utilizó acceso explícito al repositorio hermano por las restricciones del sandbox, sin cambiar permisos permanentes ni configuración Git.

## Arquitectura mínima y límites de integración

Se eligió una escena aislada dentro del proyecto existente. El juego continúa arrancando su escena original; no se cambia `main.gd`, `illustration_view.gd`, `room_illustration.gd`, `art_ch01.json`, configuración, parser, traducciones, YAML, exportador ni reglas. La escena experimental no instancia intérprete, GameState o terminal, ni captura Tab/Enter globalmente. Por tanto, **la disponibilidad del parser durante esta animación no está integrada ni validada**; la ausencia de regresiones del juego se respalda con la suite existente y con el inventario Git sin cambios productivos.

Los archivos están en [godot/experiments/vector_playback](../../../07_godot_open_adventure/godot/experiments/vector_playback/):

| Archivo | Responsabilidad |
| --- | --- |
| `build_loc_start.py` | Conversión acotada del generador original C/START a datos experimentales; biblioteca estándar Python. No es un importador SVG general. |
| `loc_start.json` | 43 polilíneas y 17 regiones cerradas a 640 × 400; colores/geometría derivados del concepto original. Casa, final de carretera, bosque y arroyo permanecen reconocibles. No es un asset final ni sustituye arte productivo. |
| `playback.gd` | Geometría, máscaras, cola BFS, reloj, progreso parcial, omisión/final y cancelación; no depende de nodos del juego. |
| `playback_view.gd` | Presentación CanvasItem, textura del relleno, trazos antialias, identidad de sala, visitas y reloj monotónico desde Replay. |
| `demo.tscn`, `demo.gd` | Escena ejecutable y controles locales de revisión. |
| `test_playback.gd` | 62 comprobaciones enfocadas de geometría, topología, continuidad temporal y presentación. |
| `capture_playback.gd` | Captura de frames reales con controlador gráfico y comparación exacta entre final animado y omitido. |
| `package_capture.py` | Empaquetado opcional de las capturas como GIF/lámina/métricas; utiliza Pillow ya instalado. No es dependencia del juego o del renderer. |

Se incluyen los cinco `.gd.uid` generados por Godot. Otros archivos del corte: este CHANGE, cuatro artefactos en `evidence/` y la reconciliación acotada de `CURRENT_STATE.md`. No se modifica el manifiesto histórico.

### Extensiones experimentales del dibujo

No se altera el contrato productivo LINE/FILL. El formato `CAR-ART-002-experimental-v1` introduce solo para este prototipo:

- Polilíneas con coordenadas decimales, grosor y fase `contour`/`detail`. Las cuadráticas del estudio original se aplanan con desviación máxima de 0,25 píxeles del lienzo; no hay Bézier runtime ni intérprete SVG.
- Regiones mediante polígonos cerrados, color, semilla interior y orden de pintura explícito. Las semillas conceptuales que estaban fuera o en un borde se convierten determinísticamente a la celda interior más próxima; se conserva la semilla original en los datos.
- Tres duraciones experimentales: 1,4 s estructura/contornos, 0,7 s detalles y 1,4 s rellenos. El total aprobado es 3,5 s; este reparto queda sujeto a revisión perceptual.

La preparación rasteriza máscaras por scanlines y compila un recorrido real de **cuatro vecinos en amplitud (BFS)** desde cada semilla, no una máscara circular. Se conservan las 347.211 celdas de las 17 regiones, incluidos solapes. Una tabla de propietario visible respeta el orden de capas: cielo/suelo no colorean temporalmente la casa o los árboles pendientes. La propagación sigue el polígono completo, incluidas zonas ocultas; no reproduce el algoritmo histórico de relleno global por barreras de tinta.

LINE recorre la distancia acumulada de las polilíneas, incluidos segmentos intermedios. FILL revela prefijos de sus colas BFS, por región y en orden estable, con duración ponderada por raíz del área. No se utilizan imágenes intermedias precalculadas: se compilan topología y un único relleno final, y cada frame revela los píxeles correspondientes al tiempo real. CanvasItem dibuja los trazos encima del relleno. La vista final directa usa el relleno final y los mismos trazos completos; omitir no reproduce la secuencia.

Preparación: presupuesto de 8.192 celdas por callback; una scanline puede exceder el resto como máximo en el ancho del lienzo. Durante playback se procesan como máximo 16.000 entradas BFS por callback. La geometría de trazos es finita y está acotada por este dataset. Si el equipo acumula retraso, se conserva el trabajo pendiente y puede alargarse la secuencia; no se descartan píxeles ni se rebaja calidad para cumplir el cronómetro.

## Ejecutar y revisar

Desde la raíz del repositorio, con el ejecutable local excluido de Git:

```powershell
$Godot = 'C:\remake\Colossal-Adventure-Reimagination-public\tools\Godot_v4.7.2-stable_win64_console.exe'
& $Godot --path 07_godot_open_adventure/godot res://experiments/vector_playback/demo.tscn
```

Alternativamente, abrir `07_godot_open_adventure/godot/project.godot`, abrir `experiments/vector_playback/demo.tscn` y ejecutar **esa escena con F6**. F5 sigue ejecutando el juego original. Utilizar una sola ejecución para evitar confundir ventanas de juego y prototipo.

La primera apertura prepara las regiones antes de iniciar el reloj; los controles están desactivados durante esa preparación. Después:

1. **Reproducir / Replay:** reinicia voluntariamente desde el lienzo vacío, a 1×.
2. **Omitir:** muestra inmediatamente el mismo final estable.
3. **Salir de LOC_START / Cancelar:** limpia imagen y trazos, cancela la secuencia anterior. Es una identidad de presentación de prueba, no un movimiento del mundo.
4. **Volver a LOC_START:** muestra el final directamente después de la primera visita; Replay sigue disponible. Refrescar la misma identidad no reinicia la reproducción.

Revisar visualmente recorrido, ritmo, propagación, curvas/legibilidad y reconocimiento de casa/carretera/bosque/arroyo. Probar Omitir durante contornos y rellenos, cancelar a mitad y volver. La revisión humana de estos controles y del resultado artístico sigue **PENDING**.

[Animación de revisión](evidence/playback.gif), [lámina de seis frames](evidence/contact_sheet.png), [final PNG](evidence/final.png) y [métricas reales](evidence/metrics.json). El GIF contiene 35 muestras capturadas de Godot, cuantización de paleta/tiempos y una pausa final añadida de 1,5 s; sirve de revisión, no de prueba exacta de cronometraje o píxeles. No alimenta al renderer. La imagen estática por sí sola no demuestra la animación.

## Verificación ejecutada

Godot **4.7.2.stable.official.ed1daf0bf**, Windows; captura OpenGL Compatibility, NVIDIA GeForce RTX 3070. Comandos ejecutados desde raíz:

```powershell
python 07_godot_open_adventure/godot/experiments/vector_playback/build_loc_start.py
& $Godot --headless --path 07_godot_open_adventure/godot --script res://experiments/vector_playback/test_playback.gd
& ./07_godot_open_adventure/tools/verify.ps1 -Godot $Godot
$captureDir = Join-Path $env:TEMP 'CAR-ART-002-playback-capture'
& $Godot --path 07_godot_open_adventure/godot --resolution 800x600 --max-fps 60 --script res://experiments/vector_playback/capture_playback.gd -- --output $captureDir
python 07_godot_open_adventure/godot/experiments/vector_playback/package_capture.py $captureDir project_state/changes/car_art_002_vector_drawing_playback_prototype/evidence
```

- **62 checks propios, 0 fallos**. Son aserciones, no 62 pruebas de juego independientes: incluyen 17 comparaciones exactas de área/SHA de máscaras con rasterización independiente Python y 17 comprobaciones de continuidad desde semilla. Comprueban recorrido parcial multisegmento, ausencia de relleno inicial, oclusión, omisión en cuatro momentos, igualdad de geometría/fill, límite de trabajo, recuperación de backlog, cancelación, mismo ID sin reinicio, revisita directa y replay.
- Reloj por deltas sintéticos: 24 FPS → 3,541667 s; 60 FPS → 3,516667 s; 144 FPS → 3,500000 s. Desviación máxima: un intervalo de callback por cuantización numérica/temporal. Estos son tiempos simulados, separados de la medición gráfica.
- Preparación headless con presupuesto de 4.096: 0,227 s CPU agregado en 166 llamadas; máximo 4.166 µs por llamada. Avance headless: máximo 2.587 µs por llamada en esa ejecución. Son mediciones de este equipo, sin garantía para otros.
- **Captura gráfica real:** finalización de vista a **3,516845 s**, desviación +16,845 ms sobre 3,5 s. Preparación previa separada: **1,390019 s** de pared, no incluida en el reloj de dibujo. 212 frames; máximo intervalo medido 17,021 ms incluyendo capturas; máximo CPU prepare/update/envío de dibujo: **5.361 / 2.162 / 1.132 µs**. No son tiempos GPU. El trabajo de captura terminó a 3,557708 s por los readbacks/esperas de frames posteriores al final.
- **Final renderizado completo = final omitido: igualdad byte a byte** en el SubViewport 640 × 400, con trazos antialias y relleno; además de la igualdad headless de fill/geometría. Se inspeccionaron final y frames intermedios capturados. Esto acredita reproducción técnica, no aceptación artística humana.
- **`verify.ps1: ALL CHECKS PASSED`**: exportación determinista, importación, **448 checks existentes** y hoja de **11 escenas**. La baseline de 448 no fue reemplazada por los checks del prototipo. Los once dibujos productivos permanecen intactos, incluido el START original.
- Comprobación final de inventario, referencias locales, regeneración determinista del JSON y `git diff --check` antes de finalizar mediante CAR-AUTO-001. El estado posterior al commit/sync se comunica en la entrega.

La primera ejecución de la prueba encontró un array temporal compartido que vaciaba la última región al liberarse; se corrigió antes de estas verificaciones finales. También se comprobó el bloqueo de color de fondo en regiones de primer plano aún no rellenadas. No se mantiene instrumentación en código productivo.

## Pendientes y condiciones de parada

- **MANUAL_VALIDATION:** el responsable debe contemplar la animación real y valorar ritmo, propagación y fidelidad a C. No se declara aprobación definitiva por capturas o checks.
- **NO INTEGRADO:** parser durante playback, lifecycle de UI/Tab y uso del estado único de partida requerirán un corte autorizado posterior. Este prototipo no permite afirmar que LOOK u otras órdenes del juego ya convivan con su reproducción; solo verifica que el mismo ID no la reinicia y que el juego original no presenta regresiones en la suite.
- La preparación previa de ~1,39 s, memoria de máscaras/colas y llenado raster a 640 × 400 son límites conocidos. No se afirma 60 FPS universal ni calidad validada al escalar a cualquier tamaño. No se añadieron controles de aceleración; 1× es la referencia.
- CAR-ART-003, migración de once dibujos, CH_02 y CAR-CORE-001 CUT A–F siguen sin autorización adicional. No iniciar otro corte tras esta entrega.
- Parar y revisar si se pierde una pista, cambia la geografía, aparecen fugas, divergencia del final o sala obsoleta; no ocultar esos fallos mediante un fundido.

`CURRENT_STATE_UPDATE: REQUIRED`: prototipo técnico entregado para revisión humana, sin integración productiva. Finalización autorizada con CAR-AUTO-001, lista explícita, commit local y sincronización verificada a Drive. **Sin push**. La sincronización no ofrece bloqueo atómico frente a ediciones simultáneas en Drive.
