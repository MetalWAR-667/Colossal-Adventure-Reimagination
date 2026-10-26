# CHANGE: CAR-CORE-002 / R6 — Visual Debug Graph in Godot (MapView multi-chapter projection)

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-26
**Proyecto:** Colossal Adventure: Reimagination
**Motor:** Godot 4.7.2

---

## 1. Contexto y Objetivos

Con el cierre de R5A, R5B y R5C, la frontera jugable se extendió con seguridad desde `LOC_BELOWGRATE` hasta `LOC_FOOF1` (42 ubicaciones habilitadas en runtime). No obstante, el visualizador de mapa (`MapView`) estaba hardcodeado para consumir únicamente `world.map_nodes` y `world.map_edges` de `chapter_01_surface.json`, que están congelados contractualmente en 34 nodos y 118 aristas.

El objetivo de R6 ha sido:
1. Permitir que `MapView` renderice interactivamente las salas de capítulos subterráneos habilitados (`CH_ENTRY`) con su geometría visual auténtica extraída de `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio` preservada en `structural_world.json`.
2. Incluir dinámicamente nodos frontera y portales de transición entre superficie y cueva (por ejemplo `LOC_GRATE` desde `LOC_BELOWGRATE`) con marcado `is_frontier=true` y estilo diferenciado (`COLOR_EDGE_FRONTIER`).
3. Ampliar el diccionario de resolución semántica de verbos y palabras de viaje históricas (`CRAWL`, `DEBRI`, `COBBL`, `PIT`, `STEPS`, `HALL`, `CRACK`, `JUMP`, `CROSS`, `ENTRA`, `SURFA`, `DARK`, etc.) para tarjetas y guías de walkthrough.
4. **Preservar al 100% el congelamiento contractual de CH_SURFACE**: `world.map_nodes` (34) y `world.map_edges` (118) permanecen estrictamente intactos e idénticos a la línea base.

---

## 2. Modificaciones realizadas

- **`07_godot_open_adventure/godot/src/ui/map_view.gd`**:
  - Implementación de `_is_in_surface(location_id)` distinguiendo las salas de superficie de las de catálogo/subterráneas.
  - Implementación de `_get_active_nodes()` y `_get_active_edges()`. Si el jugador está en superficie, retorna de forma transparente los nodos y aristas estáticos de CH_01. Si está en una ubicación subterránea, genera dinámicamente los nodos del grafo activo con su geometría Draw.io real y proyecta los portales fronterizos.
  - Ampliación de `_resolve_verbs` para los 32 verbos y atajos de `CH_ENTRY`.
  - Adaptación de `_calculate_bounds`, `_node_bounds`, `_node_center`, `_get_node`, `_handle_click_at` y `_update_hover_at` para operar sobre el grafo activo sin tocar `WorldData`.
- **`07_godot_open_adventure/godot/tests/test_map_view_ch_entry.gd`**:
  - Nueva suite con 22 comprobaciones cubriendo:
    - Invariante estricto de 34 nodos y 118 aristas en `WorldData`.
    - Modo superficie conservado.
    - Grafo activo de `CH_ENTRY` (8 salas seguras).
    - Presencia y tipado de nodos frontera (`LOC_GRATE`).
    - Exactitud de geometría Draw.io (`LOC_DEBRIS` x=1400, y=660) y cálculo de límites.
- **`07_godot_open_adventure/tools/verify.ps1`**:
  - Registro de `test_map_view_ch_entry.gd` en la Fase 3/7.

---

## 3. Resultados de Verificación

- Determinismo de exportación: `PASS`.
- Verificación de inventario canónico: `PASS` (26 tests).
- Verificación negativa estructural: `PASS` (8 tests).
- Preservación y aislamiento R1/R2/R3/R4/R5A/R5B/R5C: `PASS`.
- Suite `MapView` CH_ENTRY: `22 checks, 0 failures`.
- Total de comprobaciones: **1.658 checks + 11 escenas visuales**, 0 fallos.
