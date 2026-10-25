# CAR-ART-005 — State-Aware Illustration Selection I

**Estado final:** `CLOSED / PASS — WITH DOCUMENTED ARTISTIC FOLLOW-UP`.
`GRATE_CLOSED` y `GRATE_OPEN`: implementación, verificación técnica y aceptación
humana PASS el 2026-10-25. Alcance: únicamente la reja de CH_01.
[Galería](gallery.html) · [Métricas y resultados](evidence/metrics.json).

## Fuente y contrato comprobados antes de editar

Preflight: repositorio `C:\remake\Colossal-Adventure-Reimagination-public`, rama
`main`, HEAD `f1f8d6befc6c4079d39eefbf67a28a8c001d12e3`, índice y árbol
limpios. La referencia local `origin/main` estaba un commit por detrás; no se
consultó el remoto en vivo. CAR-ART-004 ya estaba cerrado para sus nueve piezas,
con GRATE diferida en ese corte.

- `06_reconstruccion_drawio/Open_Adventure.yaml` declara la localización
  `LOC_GRATE` y el objeto `GRATE` con estados `GRATE_CLOSED`/`GRATE_OPEN`. El
  dataset exportado conserva `initial_state: GRATE_CLOSED` y ambos estados.
- `GameState.reset()` inicializa `object_state` desde el objeto del mundo;
  `GameState.state_of("GRATE")` es la lectura no mutante autoritativa.
  `Interpreter._do_lock()` llama `state.set_state("GRATE", …)` tras aplicar su
  regla existente de llaves. Ninguna regla de apertura se trasladó a la UI.
- `main._on_command()` ya procesa `Interpreter.submit()` y llama siempre a
  `_refresh_status()`, incluso cuando no cambia la localización. Por ello el
  refresco tras `LOCK/UNLOCK GRATE` puede leer el estado vigente en la misma
  sala. `IllustrationView` antes solo identificaba la localización y omitía
  repeticiones de esa sala.
- `godot/data/art_ch01.json → scenes.LOC_GRATE` es la reja heredada estática.
  Permanece intacta como referencia y fallback cuando no hay una variante
  reconocida. No se convirtió en evidencia de apertura dinámica.

## Selección visual e integración

`main._refresh_status()` pasa a `IllustrationView.show_room()` la lectura
`state_of("GRATE")` solo cuando el jugador está en `LOC_GRATE`. El adaptador
acepta únicamente `GRATE_CLOSED` o `GRATE_OPEN` y elige el JSON de presentación
correspondiente. Su clave de escena recuerda sala **y variante**, por lo que
un cambio de estado en la misma sala cancela y oculta el playback anterior.
La caché conserva una vista por variante y no crea un segundo intérprete ni un
estado paralelo. Una lectura ausente o desconocida conserva el fallback
heredado en lugar de adivinar una imagen.

El flujo de `Tab`, «Omitir», preparación y revisita usa el ciclo existente del
consumidor LINE/FILL. El cambio de estado durante el dibujo invalida la vista
anterior; al salir y regresar se lee de nuevo `GameState`. En modo debug el
parser puede cerrar la reja sin cambiar de composición, y al volver con `Tab`
aparece la variante actual. No se modificaron `GameState`, `Interpreter`, el
parser, el YAML, el exportador, el renderer, la escena ni el layout.

## Dos dibujos originales

Los recursos nuevos `godot/data/vector_ch01/grate_closed.json` y
`grate_open.json` comparten cielo, árboles, cauce seco, laderas, borde de
hormigón y abertura. La variante cerrada cubre la abertura con barrotes y
travesaños; la abierta muestra la abertura y la hoja levantada junto a su
bisagra. Son **dos estados de una sola sala**, no rutas nuevas. El estilo es
C — Línea solar, 736 × 400, paleta/anchos existentes y 1,4 / 0,7 / 1,4 s.
La geometría se compila determinísticamente mediante
`tools/build_grate_variants.py`, reutilizando el compilador y vocabulario de
CAR-ART-004; no hay assets externos ni dependencias de ejecución nuevas.

| Variante | Trazos | Regiones | Preparación gráfica | Reproducción |
| --- | ---: | ---: | ---: | ---: |
| `GRATE_CLOSED` | 49 | 28 | 4,189422 s | 3,502407 s |
| `GRATE_OPEN` | 47 | 25 | 4,242553 s | 3,505492 s |

Mediciones de Godot 4.7.2 en Windows, OpenGL Compatibility, NVIDIA RTX 3070;
la preparación es adicional al dibujo y no es una garantía para otros equipos.
No se optimizó el renderer. Los polígonos de los barrotes se corrigieron durante
la autoría para evitar máscaras desconectadas y un borde se desplazó 0,0625 px
para evitar un empate de raster entre Python double y Godot Vector2 float.
Las máscaras finales coinciden con el raster Python independiente.

## Aceptación humana y seguimiento artístico

El responsable probó y validó ambas variantes y aceptó el 2026-10-25 la
selección desde el estado autoritativo, el refresco en la misma sala, la
cancelación del playback anterior, la integración LINE/FILL y la conservación
del arte heredado como respaldo. CAR-ART-005 queda **`CLOSED / PASS — WITH
DOCUMENTED ARTISTIC FOLLOW-UP`**. La aceptación incluye las dos variantes; no
reabre ni altera el corte histórico CAR-ART-004.

La ilustración `GRATE_OPEN` funciona y queda aceptada provisionalmente, con
calidad visual inferior a la deseada. Su pulido se conserva como deuda para la
revisión artística final del proyecto. La preparación medida de **4,189–4,243 s**
se conserva como limitación conocida; esta decisión no autoriza optimizaciones.
Ambas observaciones quedan diferidas y no invalidan la aceptación funcional y
artística provisional de CAR-ART-005.

## Verificación y evidencia

Comandos usados desde la raíz del repositorio:

```powershell
$Godot = 'C:\remake\Colossal-Adventure-Reimagination-public\tools\Godot_v4.7.2-stable_win64_console.exe'
& ./07_godot_open_adventure/tools/verify.ps1 -Godot $Godot
& $Godot --headless --path 07_godot_open_adventure/godot --script res://experiments/vector_playback/test_playback.gd
& $Godot --headless --path 07_godot_open_adventure/godot --script res://tests/test_grate_state_art.gd
$frames = Join-Path $env:TEMP 'CAR-ART-005-frames'
& $Godot --path 07_godot_open_adventure/godot --max-fps 60 --script res://tests/test_grate_state_art.gd -- --output "$PWD/project_state/changes/car_art_005_state_aware_illustration_selection_i/evidence" --frames $frames
python 07_godot_open_adventure/tools/package_grate_review.py $frames
```

- Exportación determinista e importación: PASS. Suite histórica del juego:
  **448 checks**. Prototipo START: **66 checks**. Fixture integrado:
  **62 checks**. Lote CAR-ART-004: **455 checks**, con su fallback histórico de
  GRATE comprobado mediante un registro de fixture explícito; no se cambió
  ninguna aserción para obtener PASS.
- CAR-ART-005: **150 checks headless y 180 gráficos**, cero fallos. Son
  aserciones, varias repetidas entre modos; no son 330 pruebas independientes
  ni tests GUT. Se comprobaron máscaras/semillas, cobertura del lienzo,
  selección inicial, `UNLOCK` sin llaves, obtención real de llaves, apertura,
  cierre, cambio durante LINE/FILL, `LOOK`, salida/regreso, `Tab`, reutilización
  de vistas, y snapshot completo de `GameState` antes/después del refresco de
  presentación. Las órdenes se enviaron al `LineEdit` de la escena principal.
- El resultado final animado y «Omitir» coincidió en datos/contornos en ambos
  modos y en píxeles renderizados durante la ejecución gráfica. La textura GPU
  se valida en modo gráfico; el servidor dummy headless no acredita readback.
- [Final cerrada](evidence/grate_closed_final.png),
  [final abierta](evidence/grate_open_final.png),
  [reproducción cerrada](evidence/grate_closed_playback.gif),
  [reproducción abierta](evidence/grate_open_playback.gif),
  [runtime cerrado](evidence/runtime_grate_closed.png),
  [runtime abierto](evidence/runtime_grate_open.png) y
  [transición de estado](evidence/state_transition_open_gate.png).
  Los GIF usan frames reales muestreados, paleta reducida, intervalos
  aproximados y pausa final; los PNG y métricas son la evidencia exacta.
  La [galería previa de CAR-ART-004](../car_art_004_ch01_vector_illustration_production/gallery.html)
  y todos sus archivos siguen intactos.

## Archivos y límites

- Presentación: `godot/src/ui/main.gd` y `illustration_view.gd`.
- Datos artísticos: dos JSON nuevos en `godot/data/vector_ch01/`.
- Autoría y galería: `tools/build_grate_variants.py`,
  `tools/package_grate_review.py`, este CHANGE, `gallery.html` y nueve
  evidencias del corte.
- Pruebas/verificador: `godot/tests/test_grate_state_art.gd` y `.uid`,
  `godot/tests/test_ch01_vector_art.gd` (solo registro del fixture de fallback)
  y `tools/verify.ps1` (séptimo paso focal).
- Estado del proyecto: `project_state/CURRENT_STATE.md`.

La preparación inicial de **4,189–4,243 s** es una limitación técnica conocida.
La calidad visual de `GRATE_OPEN` requiere pulido durante la revisión artística
final del proyecto. El arte heredado se conserva para referencia/fallback.
CH_02, SAVE/LOAD y otros estados visuales no se abren.

La excepción de GRATE registrada en CAR-ART-004 queda resuelta funcionalmente
por las dos variantes de este corte, sin cambiar el inventario histórico de sus
nueve piezas aceptadas y su excepción original. La deuda de pulido de
`GRATE_OPEN` permanece visible en `CURRENT_STATE.md`.

Finalización CAR-AUTO-001: inventario explícito, commit local y sincronización
verificada a Drive. **NO PUSH**. El resultado Git/Drive se comunica al entregar.
