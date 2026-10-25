# LOC_ROADEND — Final del camino

**IMPLEMENTED / TECHNICAL PASS / MANUAL_VALIDATION PENDING**

- Identidad canónica: `LOC_ROADEND`.
- Fuente: `godot/data/chapter_01_surface.json → locations.LOC_ROADEND`, contrastada con el YAML por el exportador; descripción original:

> The road, which approaches from the east, ends here amid the trees.

- Elementos representados: Carretera que termina entre árboles y raíces, sin abertura oscura.
- Relaciones, estados y excepción de cámara: La carretera llega del este según la fuente; la cámara no codifica direcciones del parser.
- Referencia heredada conservada: `godot/data/art_ch01.json → scenes.LOC_ROADEND`.
- Recurso nuevo: `godot/data/vector_ch01/loc_roadend.json`; 41 trazos, 15 regiones; 736 × 400.
- Técnica: máscaras exactas respecto al raster Python, semillas interiores y regiones conectadas; sin celdas sin fondo. Playback completo y Omitir iguales píxel a píxel. Cancelación, revisita, selector runtime y TAB pasan. Los márgenes y la lectura final se inspeccionan visualmente; aceptación humana pendiente.
- Preparación gráfica: 2.147747 s. Dibujo: 3.512597 s. Las cifras corresponden al equipo de captura, no son garantías.

![Final](../evidence/LOC_ROADEND/final.png)

[Reproducción muestreada](../evidence/LOC_ROADEND/playback.gif) · [Dentro de la UI real](../evidence/LOC_ROADEND/runtime.png) · [Volver a la galería](../gallery.html)

GIF elaborado con frames reales, paleta/tiempos aproximados y pausa final añadida; no es prueba de FPS ni igualdad exacta. El PNG y las métricas conservan la evidencia gráfica completa. Los cambios de colocación para capturas son fixtures de prueba, no viajes añadidos al juego.
