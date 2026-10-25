# LOC_VALLEY — Vaguada rocosa

**IMPLEMENTED / TECHNICAL PASS / MANUAL_VALIDATION PENDING**

- Identidad canónica: `LOC_VALLEY`.
- Fuente: `godot/data/chapter_01_surface.json → locations.LOC_VALLEY`, contrastada con el YAML por el exportador; descripción original:

> You are in a valley in the forest beside a stream tumbling along a rocky bed.

- Elementos representados: Arroyo curvo, lecho y orillas con rocas de escala variable, bosque.
- Relaciones, estados y excepción de cámara: Rocas junto al cauce; sin pasos, puentes o rutas nuevas. Agua y carretera tienen colores distintos.
- Referencia heredada conservada: `godot/data/art_ch01.json → scenes.LOC_VALLEY`.
- Recurso nuevo: `godot/data/vector_ch01/loc_valley.json`; 39 trazos, 18 regiones; 736 × 400.
- Técnica: máscaras exactas respecto al raster Python, semillas interiores y regiones conectadas; sin celdas sin fondo. Playback completo y Omitir iguales píxel a píxel. Cancelación, revisita, selector runtime y TAB pasan. Los márgenes y la lectura final se inspeccionan visualmente; aceptación humana pendiente.
- Preparación gráfica: 2.110927 s. Dibujo: 3.514499 s. Las cifras corresponden al equipo de captura, no son garantías.

![Final](../evidence/LOC_VALLEY/final.png)

[Reproducción muestreada](../evidence/LOC_VALLEY/playback.gif) · [Dentro de la UI real](../evidence/LOC_VALLEY/runtime.png) · [Volver a la galería](../gallery.html)

GIF elaborado con frames reales, paleta/tiempos aproximados y pausa final añadida; no es prueba de FPS ni igualdad exacta. El PNG y las métricas conservan la evidencia gráfica completa. Los cambios de colocación para capturas son fixtures de prueba, no viajes añadidos al juego.
