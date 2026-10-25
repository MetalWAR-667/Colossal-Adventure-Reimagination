# Matriz de Trazabilidad Estructural — CAR-CORE-002

**Identificador:** `CAR_CORE_002_TRACEABILITY_MATRIX`
**Fecha:** 2026-10-25
**Corte autorizador:** `CAR-CORE-002 / R4 — Structural Validation & Contract Freeze`
**Baseline:** `d856ef4986479d28df91a0674d0c3d4a8cfd0d71`

---

## 1. Alcance y Metodología

Esta matriz establece el mapa de trazabilidad bidireccional entre las fuentes de autoridad históricas, las proyecciones canónicas intermedias (R1/R2), los cargadores de motor (R3), el runtime activo de Godot, y la batería de pruebas de regresión y congelación (R4).

### Estados de Contrato
- **`VERIFIED`:** Invariante verificada activamente en tests automatizados (`test_structural_contract_freeze.gd`, `test_structural_loader.gd`, etc.) con resultado `PASS`.
- **`DOCUMENTED`:** Contrato de diseño y arquitectura formalizado en la especificación contractual sin código activo dependiente.
- **`DEFERRED`:** Funcionalidad identificada y preservada estáticamente, diferida a cortes posteriores (p. ej. puzles complejos, enanos).
- **`NOT AUTHORIZED`:** Capacidad expresamente excluida del corte actual (p. ej. habilitación de CH_02, Steamworks, push remoto).

---

## 2. Matriz de Trazabilidad por Dimensión de Datos

| Dimensión | Fuente de Autoridad | Artefacto R1/R2 | Consumidor Godot R3/R4 | Invariante Protegida | Prueba Verificadora | Estado | Consecuencia si R5 la rompe |
|---|---|---|---|---|---|---|---|
| **Ubicaciones Totales** | `Open_Adventure.yaml` (`locations`) | `locations.json`, `structural_world.json` | `StructuralCatalog`, `WorldData` | 185 ubicaciones históricas (0..184), `LOC_NOWHERE` a `LOC_FOOF6` | `test_01` (R1), `test_01` (R2), Check 1 (R4) | `VERIFIED` | Desincronización del mapa canónico; rotura de índices históricos en travel |
| **Viajes Totales** | `Open_Adventure.yaml` (`travel`) | `travel_records.json`, `structural_world.json` | `StructuralCatalog.get_all_travel_records()` | Exactamente 623 filas de viaje ordenadas globalmente (`0..622`) | `test_02` (R1), `test_02` (R2), Check 2, 6 (R4) | `VERIFIED` | Alteración de la precedencia *first-match-wins*; caminos inalcanzables o bucles espurios |
| **Objetos Totales** | `Open_Adventure.yaml` (`objects`) | `objects.json`, `structural_world.json` | `StructuralCatalog.get_object_ids()` | Exactamente 70 objetos; índice 0 reservado a `NO_OBJECT` | `test_03` (R1), `test_03` (R2), Check 3 (R4) | `VERIFIED` | Colapso del índice de objetos; referencias de condiciones inválidas |
| **Capítulos Editoriales** | `oa_chapters.py` (11 capítulos) | `chapters.json`, `structural_world.json` | `StructuralCatalog.get_chapter_ids()` | 11 capítulos; 100% cobertura de salas; 0 duplicados; 0 huérfanas | `test_04..07` (R1), `test_04` (R2), Check 4 (R4) | `VERIFIED` | Imposibilidad de habilitación modular por fases en R5+; fragmentación de grafo |
| **Posiciones de Enanos** | `Open_Adventure.yaml` (`dwarflocs`) | `canonical_inventory.json`, `structural_world.json` | `StructuralCatalog.get_dwarflocs()` | Exactamente 6 posiciones históricas de generación | `test_dwarf_start_positions` (CUT A), `test_21` (R2), Check 5 (R4) | `VERIFIED` | Despliegue erróneo de enanos al habilitar actores en cortes futuros |
| **Orden Local de Reglas** | `Open_Adventure.yaml` | `travel_records.json`, `structural_world.json` | `StructuralCatalog.get_travel_records(loc_id)` | Orden de `source_rule_index` preservado para cada sala | `test_09` (R1), `test_07` (R2), Check 6 (R4) | `VERIFIED` | Reglas condicionales evaluarían antes que reglas incondicionales previas, alterando juego |
| **Tipos de Condición** | `Open_Adventure.yaml` (`cond`) | `travel_records.json`, `structural_world.json` | `StructuralCatalog` | 574 always, 25 not, 12 pct, 7 carry, 4 with, 1 nodwarves | `test_11` (R1), `test_08` (R2), Check 7 (R4) | `VERIFIED` | Falsos positivos/negativos en evaluación de viajes en salas ampliadas |
| **Destinos Especiales** | `Open_Adventure.yaml` | `structural_world.json` | `StructuralCatalog` | 583 goto, 34 speak, 6 special (handlers 1, 2, 3), 1 nodwarves | `test_10` (R1), `test_09` (R2), Check 8 (R4) | `VERIFIED` | Fallos de ejecución al invocar controladores especiales en el puente o plover |
| **Objetos Multi-Lugar** | `Open_Adventure.yaml` | `objects.json`, `structural_world.json` | `StructuralCatalog.get_object()` | 11 objetos con `has_multiple_locations = true` | `test_14` (R1), `test_16` (R2), Check 9 (R4) | `VERIFIED` | Objetos compartidos (p. ej. fisura, reja) duplicados o desaparecidos en salas remotas |
| **Objetos Multi-Estado** | `Open_Adventure.yaml` | `objects.json`, `structural_world.json` | `StructuralCatalog.get_object()` | 26 objetos con `has_multiple_states = true` | `test_16` (R1), `test_17` (R2), Check 9 (R4) | `VERIFIED` | Transiciones de estado bloqueadas o no reconocidas en puzles de capítulos R5+ |
| **Integridad Referencial** | `Open_Adventure.yaml` | `structural_world.json` | `StructuralCatalog.load_from_string()` | Cero destinos `goto` rotos; cero dependencias de objetos inexistentes | `test_12` (R1), `test_10` (R2), Check 10, 24 (R4) | `VERIFIED` | Crashes en runtime al intentar resolver destinos no existentes |
| **Geometría Draw.io** | `Open_Adventure_World_V3.drawio` | `structural_world.json` | `StructuralCatalog.get_location()` | 185 salas con celda válida, página y dimensiones positivas | `test_08` (R1), `test_15` (R2), Check 11 (R3) | `VERIFIED` | Distorsión o rotura de visualización en herramientas cartográficas o minimapa |
| **Separación LOADED/ENABLED** | Decisión de Arquitectura | `world_data.gd` | `WorldData.is_location_enabled()`, `enabled_location_ids` | Exactamente 34 salas habilitadas en CH_01; 151 deshabilitadas | `test_structural_loader.gd`, Check 14, 15 (R4) | `VERIFIED` | Fuga de salas no preparadas al entorno jugable activo; rotura de frontera |
| **Aislamiento Funcional CH_01** | CUT A Decision Gate | `chapter_01_surface.json` | `WorldData.locations`, `Interpreter` | Exactamente 34 salas y 8 objetos jugables; hash `a49db669...` | `test_simulation_graph_isolation.gd`, Check 16, 27 (R4) | `VERIFIED` | Corrupción de la experiencia jugable de referencia de Superficie |
| **Aislamiento del Parser** | Principio de Menor Privilegio | `command_parser.gd` | `CommandParser.parse()` | Objetos de otros capítulos (`CHEST`, `DRAGON`) no forman vocabulario activo | Check 21 (R3), Check 17 (R4) | `VERIFIED` | Comandos con objetos ausentes procesados incorrectamente en lugar de ser rechazados |
| **Inercia de GameState y RNG** | Especificación CAR-CORE-002 | `structural_catalog.gd` | `StructuralCatalog`, `Interpreter` | Consultas estructurales no alteran turnos, ubicación ni RNG | Check 26, 27 (R3), Check 19 (R4) | `VERIFIED` | Determinismo roto; partidas desincronizadas por simples lecturas cartográficas |
| **Inmutabilidad Defensiva** | Seguridad de Software | `structural_catalog.gd` | `StructuralCatalog` | Todas las consultas devuelven copias profundas (`duplicate(true)`) | Check 35 (R3), Check 13 (R4) | `VERIFIED` | Contaminación del catálogo maestro por modificaciones accidentales en runtime |
| **Política Fail-Closed** | Robustez y Tolerancia a Fallos | `structural_catalog.gd` | `StructuralCatalog.load_from_string()` | Cualquier anomalía vacía el catálogo por completo (`is_loaded = false`) | Check 31..34 (R3), Check 21..26 (R4) | `VERIFIED` | Ejecución en estado corrupto o parcialmente inicializado con comportamiento indefinido |
| **Digest Contractual CH_01** | Baseline CUT A (`f8796e6`) | `chapter_01_surface.json` | `verify.ps1`, `test_simulation_graph.py` | Hash `a49db669...` (pre-CUT A playable); file hash `afa33c88...` | `test_simulation_graph.py`, Check 27 (R4) | `VERIFIED` | Modificación no autorizada de la fuente jugable histórica de Capítulo 01 |
| **Digest Proyección Global** | Artefacto R2 | `structural_world.json` | `verify.ps1`, `StructuralCatalog` | Hash exacto `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3` | Check 28 (R4), `test_structural_projection.py` | `VERIFIED` | Drift no controlado en la proyección estructural completa |
| **Actores y Enanos** | `Open_Adventure.yaml` | `structural_world.json` (`dwarflocs`) | Ninguno (inactivo) | Cero simulación de actores en `GameState` en el corte actual | Check 24 (R3), `test_22` (R2) | `DEFERRED` | Si R5 activa actores sin corte específico, causará bucles de combate y muertes no controladas |
| **Puzles Complejos** | `Open_Adventure.yaml` | `structural_world.json` (`state_dependencies`) | Ninguno (inactivo) | Puzles (oso, dragón, troll, máquina expendedora) inertes en catálogo | Check 25 (R3) | `DEFERRED` | Puzles a medio implementar generarán bloqueos insolubles para el jugador |
| **Habilitación de CH_02..11** | CAR-CORE-002 Decision Gate | `structural_world.json` | Ninguno (bloqueado como `FRONTIER`) | Prohibida la navegación y habilitación de salas fuera de CH_01 | Check 23 (R3), Check 31, 32 (R4) | `NOT AUTHORIZED` | Vulneración del Decision Gate; ampliación de alcance sin corte autorizado |

---

## 3. Conclusiones y Salvaguardas para R5

1. **Blindaje de la Superficie:**
   Cualquier modificación en R5 debe garantizar que los tests de Capítulo 01 (Fases 1 a 7 de `verify.ps1`) continúen ejecutándose con `ALL CHECKS PASSED`.

2. **Proceso de Habilitación en R5:**
   La transición de salas de `STRUCTURAL / DISABLED` a `FUNCTIONAL / ENABLED` debe ser aditiva mediante el registro de sus IDs en `WorldData.enabled_location_ids`.

3. **Inalterabilidad de Fuentes:**
   `structural_world.json` y `chapter_01_surface.json` no deben ser editados manualmente para ajustar mecánicas; deben regenerarse únicamente mediante los exportadores autorizados.
