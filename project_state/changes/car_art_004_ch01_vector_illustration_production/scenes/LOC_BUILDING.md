# LOC_BUILDING — Casa del manantial

**IMPLEMENTED / TECHNICAL PASS / MANUAL_VALIDATION PENDING**

- Identidad canónica: `LOC_BUILDING`.
- Fuente: `godot/data/chapter_01_surface.json → locations.LOC_BUILDING`, contrastada con el YAML por el exportador; descripción original:

> You are inside a building, a well house for a large spring.

- Elementos representados: Planos de ladrillo, suelo seco, gran manantial con pila y canal de salida.
- Relaciones, estados y excepción de cámara: Pila y sección del canal son interpretación geométrica. KEYS, LAMP, FOOD y BOTTLE no se fijan en el fondo; el terminal describe los objetos presentes.
- Referencia heredada conservada: `godot/data/art_ch01.json → scenes.LOC_BUILDING`.
- Recurso nuevo: `godot/data/vector_ch01/loc_building.json`; 39 trazos, 9 regiones; 736 × 400.
- Técnica: máscaras exactas respecto al raster Python, semillas interiores y regiones conectadas; sin celdas sin fondo. Playback completo y Omitir iguales píxel a píxel. Cancelación, revisita, selector runtime y TAB pasan. Los márgenes y la lectura final se inspeccionan visualmente; aceptación humana pendiente.
- Preparación gráfica: 2.493728 s. Dibujo: 3.515965 s. Las cifras corresponden al equipo de captura, no son garantías.

![Final](../evidence/LOC_BUILDING/final.png)

[Reproducción muestreada](../evidence/LOC_BUILDING/playback.gif) · [Dentro de la UI real](../evidence/LOC_BUILDING/runtime.png) · [Volver a la galería](../gallery.html)

GIF elaborado con frames reales, paleta/tiempos aproximados y pausa final añadida; no es prueba de FPS ni igualdad exacta. El PNG y las métricas conservan la evidencia gráfica completa. Los cambios de colocación para capturas son fixtures de prueba, no viajes añadidos al juego.
