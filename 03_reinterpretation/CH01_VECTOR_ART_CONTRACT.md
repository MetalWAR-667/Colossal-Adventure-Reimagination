# CH_01 — Contrato de producción vectorial

CAR-ART-004, 2026-10-25. Dirección vigente: **C — Línea solar**.
Autoridad: decisiones humanas de
[CAR-ART-001](../project_state/changes/car_art_001_vector_direction_gate/CHANGE.md),
[CAR-ART-002](../project_state/changes/car_art_002_vector_drawing_playback_prototype/CHANGE.md)
y [CAR-ART-003](../project_state/changes/car_art_003_runtime_illustration_ui_integration_i/CHANGE.md).
Contrato consolidado para producir el lote; su aceptación artística individual
permanece pendiente. LOC_START es la referencia cerrada y no se modifica.

## Identidad y composición

Base marfil cálida `#f8efdc`, tinta verde carbón `#333d37`, cielo `#d8e7e2`,
tierra `#d8bd83`, hojas `#86a875`/`#4c7863`, ladrillo `#cd8c64`, tejado/madera
`#92745a`, agua `#66a8ae`, piedra/acero `#bdc9ba`. Son los colores del estudio
C consumido por START; la paleta no convierte la ilustración en un código de puzles.

Contornos limpios de 2,6 px; detalle secundario de 1,35 px en el lienzo de
referencia. Curvas suaves aplanadas a polilíneas (error máximo 0,25 px mediante
el compilador existente), masas planas y pocos trazos de materia. Sin pintura,
tramas obligatorias, texturas, degradados, luces animadas o pixel art añadido.

Dar profundidad por solape, tamaño y diagonales, con un foco distinto por sala.
Casa/manantial, carretera, bosque, cauce, ranura, reja, acantilado y tuberías
deben poder distinguirse por sus siluetas. Reutilizar árboles y marcas de roca
con variación de escala y disposición; no clonar la composición de START.
Mantener al menos 24 px de margen para motivos aislados; suelo, paredes,
cielo, agua y carretera pueden continuar deliberadamente fuera del cuadro.
No añadir caminos, escaleras, puentes o portales que parezcan conexiones nuevas.

Exteriores: horizontes suaves y follaje por planos, agua siempre distinta del
camino. Interiores: planos de pared/suelo y materiales coherentes con la casa
de ladrillo; el manantial es el foco, no mobiliario inventado. Entornos rocosos
y la cloaca: grises/verdes de la misma paleta, sin cambiar de estilo ni colocar
una fuente artificial de luz. La ilustración no implementa oscuridad del motor.
No hay una nueva sala subterránea jugable en este lote.

## Datos y reproducción

Lienzo **736 × 400**, relación 1,84:1; UI con escala uniforme. El número físico
de píxeles del lienzo no impone el tamaño del control. Se conserva el formato
`CAR-ART-002-experimental-v1`, aunque su nombre histórico incluya experimental:
`room`, `grid`, `background`, `ink`, `seconds`, `lines` y `regions`. No se crea
un dialecto ni un algoritmo nuevos.

Cada línea declara puntos, grosor y fase `contour`/`detail`. Cada región es un
polígono cerrado con color y semilla interior; su posición en el array fija el
orden de pintura. Los contornos se revelan por longitud acumulada, los rellenos
por el recorrido BFS de cuatro vecinos ya implementado dentro de cada región.
Las máscaras, áreas y hashes se contrastan con el raster Python independiente.
No se trata de un relleno global delimitado por toda la tinta.

Objetivo **3,5 s a 1×**: 1,4 s contornos, 0,7 s detalles y 1,4 s regiones.
El final animado y Omitir deben coincidir exactamente. Se conservan presupuestos,
cancelación, revisitas inmediatas, parser operativo y política TAB del piloto.
El coste de preparación se mide aparte y sigue siendo una limitación admitida.

## Fidelidad, identidad y estado

El YAML y su dataset derivado gobiernan lugar, conexiones y objetos; la cámara
no es una brújula. `LOC_FOREST` es un **ID de dibujo heredado**, no una sala
canónica: sirve a `LOC_FOREST1`…`LOC_FOREST22`, que comparten descripción.
Las demás nueve escenas corresponden a IDs canónicos del dataset.

Los fondos representan el entorno estable. No incorporan KEYS, LAMP, FOOD,
BOTTLE o SAPPH como objetos pintados permanentes: pueden recogerse/trasladarse
y el terminal sigue describiendo su estado real. No se inventa un sistema de
capas de objetos. La urna empotrada de CLIFF puede conservar su silueta fija;
su contenido y llama no se afirman mediante el fondo.

GRATE exige coherencia abierta/cerrada. El adaptador del piloto solo recibe
sala: la selección por estado requiere soporte técnico acotado y decisión
expresa antes de cambiar ese contrato. No se integra una reja cerrada estática
que contradiga una apertura real. Registrar esa excepción hasta resolverla.
El responsable eligió expresamente en CAR-ART-004: **«Dejar GRATE como excepción
bloqueada y producir las otras nueve»**. Por tanto, este lote no autoriza ese
soporte técnico ni produce una pieza nueva de GRATE.

Conservar los once dibujos heredados como referencia y fallback. Las piezas
nuevas son originales del proyecto, sin assets externos. Cada ficha registra
la descripción inglesa literal, la interpretación geométrica y las excepciones.

## Gate de revisión

Una pieza pasa técnicamente si su identidad es correcta, máscaras y semillas
son válidas/conectadas, el final coincide con Omitir, no queda arte obsoleto y
se conserva la UI. Eso no declara aceptación artística. El lote se entrega
`TECHNICAL VERIFICATION COMPLETE / MANUAL_VALIDATION PENDING`; el responsable
valora fidelidad, composición, legibilidad, continuidad y secuencia visible.
