# CAR-ART-003 — Runtime Illustration & UI Layout Integration I

**Estado:** `IMPLEMENTED / TECHNICAL VERIFICATION COMPLETE / MANUAL_VALIDATION PENDING`.
Fecha: 2026-10-25. Ejecución: Sol / Codex. Resultado técnico: PASS; aceptación humana de esta integración: PENDING.

## Baseline y autorización

Preflight en `C:\remake\Colossal-Adventure-Reimagination-public`: `main`, HEAD
`c15bc8227494893564e8ecd84aadae96191bc6c1`, índice/árbol limpios y referencia
local `origin/main` coincidente. No se consultó el remoto en vivo. Acceso
explícito al repositorio hermano, sin cambios de permisos permanentes ni Git.
El encargo humano autoriza integrar solo `LOC_START` y reorganizar la UI;
[CAR-ART-002](../car_art_002_vector_drawing_playback_prototype/CHANGE.md)
permanece cerrado para su prototipo aislado aceptado.

## Contrato mínimo de integración

- `IllustrationView.show_room(id)` es el único selector de representación.
  Un registro local asocia `LOC_START` al JSON progresivo existente. Las otras
  salas conservan `RoomIllustration` y la resolución de alias del bosque.
- Una vista de playback se crea una vez y conserva su preparación en memoria
  durante la sesión. Recibe `source_path`, `illustration_id` y la política de
  autoarranque; solo representa datos. No recibe intérprete, GameState,
  inventario, reglas o grafo. Se reutilizan modelo, geometría y datos de
  `experiments/vector_playback/`; no se duplican ni se migran los dibujos.
  Estas rutas son ahora dependencias del piloto y no deben retirarse como si
  fueran exclusivamente una demo descartable.
- El adaptador conserva las identidades presentadas de la sesión. La primera
  presentación prepara y reproduce; una revisita muestra el final, incluso
  si la salida anterior ocurrió durante la preparación. Refrescar el mismo ID
  no reinicia el dibujo. Salir cancela y oculta el consumidor progresivo antes
  de renderizar arte heredado. Su preparación puede terminar en segundo plano
  como caché; no puede reactivar una sala abandonada.
- `complete_pending()` solicita el final al abrir TAB o al presentar una sala
  desde debug. `skip()` recuerda esa solicitud si la preparación aún no terminó.
  La vista oculta no deja playback activo al volver a normal. No se añaden
  teclas ni controles al juego; el replay se invoca solo desde pruebas/demo.
- El juego conserva un único Interpreter/GameState, Terminal y MapView.
  La única instancia del terminal mantiene historial, selección, desplazamiento,
  texto parcial y señales. No se modifican sus métodos de foco ni el parser.

## Layout

Cabecera con capítulo/localización, región estable de ilustración, salida del
terminal, grafo con controles/salidas, entrada y estado inferior. Se aloja el
host normal del grafo entre `Terminal.output` y `Terminal.input`; la instancia
del terminal permanece completa al reparentarla. En debug el host normal vacío
se oculta y se restauran los mínimos/expansión del terminal y grafo anteriores.
No se modifica `MapView` ni su hit-test, navegación, zoom, pan o datos.

La región de ilustración responde a la altura disponible (180–360 px),
independientemente del avance LINE/FILL. La vista escala uniformemente y centra
736:400 sin recorte ni deformación. El fondo lateral pertenece a la UI, no al
lienzo. El historial tiene mínimo 80 px y recibe una cuarta parte del espacio
expandible frente a tres cuartas partes para el grafo, sujeto a sus mínimos.
Las respuestas largas desplazan el historial, no la entrada. La miniatura
anterior desaparece del panel derecho: hay una única región de ilustración.

## Archivos del corte

- Modificados: `godot/src/ui/main.gd`, `godot/src/ui/illustration_view.gd`,
  `godot/experiments/vector_playback/playback_view.gd` y `tools/verify.ps1`,
  todos bajo `07_godot_open_adventure/`; además `project_state/CURRENT_STATE.md`.
- Añadidos: `godot/tests/test_runtime_illustration.gd` y su `.uid`, este CHANGE,
  ocho PNG y `evidence/metrics.json`: **17 archivos en total**.
- Sin cambios en modelo de playback, geometría/JSON del piloto, arte heredado,
  terminal, grafo, escena principal, configuración, parser, datos históricos,
  YAML, exportador, traducciones, licencias o manifiesto histórico.

## Verificación ejecutada

Godot `4.7.2.stable.official.ed1daf0bf`, Windows; capturas OpenGL Compatibility
con NVIDIA GeForce RTX 3070. Desde raíz:

```powershell
$Godot = 'C:\remake\Colossal-Adventure-Reimagination-public\tools\Godot_v4.7.2-stable_win64_console.exe'
& ./07_godot_open_adventure/tools/verify.ps1 -Godot $Godot
& $Godot --headless --path 07_godot_open_adventure/godot --script res://experiments/vector_playback/test_playback.gd
& $Godot --path 07_godot_open_adventure/godot --max-fps 60 --script res://tests/test_runtime_illustration.gd -- --output C:/remake/Colossal-Adventure-Reimagination-public/project_state/changes/car_art_003_runtime_illustration_ui_integration_i/evidence
```

- `verify.ps1: ALL CHECKS PASSED`: exportación determinista, importación,
  **448 checks existentes sin cambios**, hoja de **11 escenas** y nueva etapa
  integrada de **62 checks headless**. No son tests GUT ni pruebas independientes
  por cada aserción. La suite de **66 checks del prototipo** también pasa intacta.
- La prueba integrada instancia la escena principal real en un SubViewport;
  envía eventos Enter/Tab a ese viewport (sin llamar directamente a los handlers
  de comandos), comprueba respuesta durante preparación/dibujo, movimiento,
  preservación de instancias/señales/cámara/texto parcial, revisitas, cancelación
  antes/después de preparar y ausencia de imagen antigua o duplicada.
- Se prueban todas las entradas de arte heredado; Vista Guía, Centrar,
  navegación por señal de botón y hit-test de nodo siguen conectados al mismo
  intérprete. Los dos últimos son invocaciones del callback/señal existente,
  no automatización física del ratón.
- **71 checks gráficos, 0 fallos:** los mismos 62 más ocho guardados PNG y
  comparación byte a byte del área renderizada de ilustración: final animado
  idéntico a Omitir. Captura de UI real a 1920×1080 y 1280×720, con entrada y
  estado dentro del viewport e historial largo sin desplazarlos.
- Se inspeccionaron capturas de trazado, final, sala heredada, transición y
  debug. La aceptación estética/ergonómica sigue reservada al responsable.
- Durante el desarrollo una nueva aserción suponía erróneamente que LOOK
  incrementaba turno: se contrastó `Interpreter._handle_motion()` y se corrigió
  solo la prueba nueva. Otro intento de contabilizar visitas pendientes en la
  vista compartida produjo dos fallos de los 66 checks: se restauró su semántica
  y se trasladó esa política al adaptador. Los resultados finales arriba
  corresponden al correctivo; no se cambiaron aserciones históricas para pasar.

## Mediciones y evidencia

Última captura gráfica, [métricas](evidence/metrics.json):

| Medida | Resultado | Alcance |
| --- | --- | --- |
| Preparación inicial | 1,570843 s | Pared, separada del reloj de dibujo; coste aún presente |
| Playback | 3,516495 s | Hasta final de vista; objetivo 3,5 s a 1× |
| LOOK durante preparación | 2,833 ms | Despacho síncrono Enter → parser/UI |
| Transición durante playback | 4,162 ms | Despacho síncrono a arte heredado |
| Transición hasta próximo render | 33,307 ms | Frame capturado tras la orden, incluye espera gráfica |

La preparación headless final fue 0,638639 s y el playback 3,503312 s; no se
equiparan al coste gráfico. No son garantías de rendimiento para otros equipos.
Las revisitas reutilizan máscaras/colas, no repiten la preparación inicial.

- [Trazado 1920](evidence/01_contours_1920.png).
- [Final, narración y grafo 1920](evidence/02_complete_text_graph_1920.png).
- [Sala heredada 1920](evidence/03_legacy_building_1920.png).
- [Transición durante playback](evidence/04_transition_during_playback_1920.png).
- [Debug sin ilustración 1920](evidence/05_debug_1920.png).
- [Final e historial largo 1280](evidence/06_complete_long_history_1280.png).
- [Sala heredada 1280](evidence/07_legacy_1280.png).
- [Debug 1280](evidence/08_debug_1280.png).

## Límites y revisión humana

El piloto ya funciona en el juego real (F5 o ejecutar la escena principal),
pero no se declara CLOSED. Revisar tamaño percibido de la ilustración y sus
márgenes, narración desplazable, selección/copia, foco al enviar órdenes,
transiciones rápidas y TAB durante preparación, contornos y rellenos.
El grafo de 720p es más compacto y presenta solapamientos con su política
de tamaño de tarjetas existente; zoom/pan y debug siguen disponibles. No se
ha rediseñado el algoritmo ni se da por aceptada esa legibilidad.
Los screenshots se renderizan en SubViewport: no acreditan interacción humana
con ventana maximizada, escalado de monitores o el portapapeles del sistema.

Se mantienen solo las capacidades del prototipo aceptado y el coste inicial
medido; no se optimiza globalmente ni se migran otras salas. CAR-CORE-001 y
CH_02 no cambian de estado. No se inicia un corte posterior.

`CURRENT_STATE_UPDATE: REQUIRED`: integración piloto entregada para revisión.
Finalización CAR-AUTO-001 con inventario explícito, commit local y sincronización
verificada a Drive; resultado operativo y SHA se comunican en la entrega.
**NO PUSH**. Drive no ofrece bloqueo atómico frente a ediciones simultáneas.
