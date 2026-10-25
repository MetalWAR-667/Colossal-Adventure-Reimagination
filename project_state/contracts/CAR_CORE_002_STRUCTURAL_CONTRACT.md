# Contrato Estructural Congelado — CAR-CORE-002

**Identificador:** `CAR_CORE_002_STRUCTURAL_CONTRACT`
**Estado:** `FROZEN / OBSERVABLE CONTRACT`
**Versión:** 1.0.0
**Baseline de congelación:** `d856ef4986479d28df91a0674d0c3d4a8cfd0d71` (cierre de R3)
**Corte autorizador:** `CAR-CORE-002 / R4 — Structural Validation & Contract Freeze`

---

## 1. Cadena de Autoridad y Fuentes de Verdad

La arquitectura del proyecto Colossal Adventure: Reimagination establece una jerarquía de autoridad estricta y unidireccional:

1. **Autoridad Histórica Primaria:**
   - `06_reconstruccion_drawio/Open_Adventure.yaml`: Autoridad canónica irrevocable para identificadores de salas, conexiones de viaje, textos descriptivos, banderas históricas, inventario de objetos y posiciones iniciales de enanos.
   - `07_godot_open_adventure/tools/oa_chapters.py`: Autoridad para la partición editorial en 11 capítulos sin solapamientos ni orfandad.
   - `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio`: Autoridad para la proyección espacial y geometría de celdas (`cell_id`, dimensiones y coordenadas).

2. **Proyecciones Canónicas Derivadas (Herramientas y Tooling):**
   - Manifiestos R1 en `07_godot_open_adventure/godot/data/canonical/*.json` generados determinísticamente por `oa_canonical_inventory.py`.
   - Proyección estructural global R2 en `07_godot_open_adventure/godot/data/structural_world.json`.
   - Dataset funcional de Capítulo 01 en `07_godot_open_adventure/godot/data/chapter_01_surface.json`.

Ninguna capa derivada puede contradecir ni sobreescribir los datos de la fuente histórica primaria. Cualquier discrepancia constituye un defecto de proyección y no una reinterpretación autorizada.

---

## 2. Versionado del Esquema e Identificación Canónica

### 2.1 Esquema Estructural v1
El artefacto `res://data/structural_world.json` se rige por las siguientes especificaciones invariantes:
- `meta.schema_version`: Entero `1`.
- `meta.cut_id`: `"CAR-CORE-002-R2"`.
- `meta.document_status`: `"INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE"`.
- Claves raíz obligatorias: `meta`, `all_chapter_ids`, `chapters`, `chapters_by_id`, `all_location_ids`, `locations`, `locations_by_id`, `travel`, `all_object_ids`, `objects`, `objects_by_id`, `dwarflocs`, `structural_dependencies`.

### 2.2 Convenciones de Identificadores
- **Ubicaciones (`LOC_*`):** Exactamente 185 registros. Índice 0 reservado a la ubicación centinela nula `LOC_NOWHERE`. Índice 1 asignado al inicio histórico `LOC_START`. Índice 184 asignado a `LOC_FOOF6`.
- **Objetos:** Cadenas en mayúsculas (p. ej. `KEYS`, `LAMP`, `GRATE`). Exactamente 70 registros con índice 0 reservado al centinela `NO_OBJECT`.
- **Capítulos (`CH_*`):** Exactamente 11 capítulos editoriales.

---

## 3. Precedencia de Viaje y Modelo de Condiciones

### 3.1 Total y Orden Histórico
- Total exacto de 623 registros de viaje ordenados globalmente en un rango secuencial `0..622` (`global_travel_index`).
- A nivel de ubicación, las reglas salientes preservan estrictamente su orden histórico original (`source_rule_index`), respetando la semántica *first-match-wins* del motor de Open Adventure.

### 3.2 Clasificación de Acciones y Destinos
- `goto` (583 reglas): Movimiento espacial hacia una sala válida existente (`destination_location_id` en las 185 ubicaciones).
- `speak` (34 reglas): Emisión de un mensaje textual arbitrario sin cambio de sala.
- `special` (6 reglas): Delegación a controladores especiales de motor (manejadores 1: puente, 2: plover/esmeralda, 3: puente del troll).

### 3.3 Taxonomía Declarativa de Condiciones
- `always` (574): Transición incondicional siempre satisfecha.
- `not` (25): Condición dependiente del estado de un objeto (`not_state`).
- `pct` (12): Condición probabilística gobernada por RNG.
- `carry` (7): Requiere que el jugador porte un objeto en su inventario.
- `with` (4): Requiere la presencia del objeto en la sala o en el inventario.
- `nodwarves` (1): Predicado especial de sistema que prohíbe el seguimiento de enanos (de `LOC_LONGWEST` a `LOC_DIFFERENT1`). No es evaluable como condición de jugador.

---

## 4. Modelo de Objetos: Estático vs. Runtime

### 4.1 Catálogo Estructural Estático (70 Objetos)
- Centinela: `NO_OBJECT` (índice 0, `is_sentinel = true`, inerte).
- Portabilidad: 36 objetos portables (`is_portable = true`), 33 objetos inmóviles (`immovable = true`), 1 centinela.
- Objetos multi-ubicación (11): Declarados con `has_multiple_locations = true` (`GRATE`, `STEPS`, `FISSURE`, `PLANT2`, `OBJ_27`, `DRAGON`, `CHASM`, `TROLL`, `TROLL2`, `RESER`, `RUG`).
- Objetos multi-estado (26): Declarados con `has_multiple_states = true` (`LAMP`, `GRATE`, `STEPS`, `BIRD`, `DOOR`, `SNAKE`, `FISSURE`, `BOTTLE`, `MIRROR`, `PLANT`, `AXE`, `DRAGON`, `CHASM`, `TROLL`, `BEAR`, `VEND`, `BATTERY`, `URN`, `CAVITY`, `RESER`, `SIGN`, `EGGS`, `VASE`, `RUG`, `CHAIN`, `AMBER`).
- Tesoros (20): Declarados con `treasure = true`.
- Inicialmente ausentes (18): Objetos que comienzan en `LOC_NOWHERE`.

### 4.2 Runtime Jugable Activo (8 Objetos de CH_01)
- `WorldData.objects` y `GameState.object_place` contienen exclusivamente los 8 objetos funcionales de Capítulo 01 (`KEYS`, `LAMP`, `GRATE`, `CAGE`, `ROD`, `ROD2`, `BIRD`, `DOOR`) más `BATTERY` en reserva.
- Ningún objeto de capítulos posteriores entra en las estructuras mutables ni en el vocabulario del parser en este corte.

---

## 5. Partición Editorial y Cobertura Espacial

### 5.1 Los 11 Capítulos Editoriales
| Identificador | Nombre Editorial | Salas | Rango de Índices |
|---|---|---:|---|
| `CH_SURFACE` | Capítulo 01: Superficie y exteriores | 34 | 1–34 |
| `CH_ENTRY` | Capítulo 02: Entrada y antesala de la cueva | 17 | 35–51 |
| `CH_HALL_MISTS` | Capítulo 03: Sala de las nieblas | 15 | 52–66 |
| `CH_COMPLEX_JUNCTION` | Capítulo 04: Cruce complejo y pasajes | 13 | 67–79 |
| `CH_ANTEROOM_COMPLEX` | Capítulo 05: Complejo de antecámaras | 15 | 80–94 |
| `CH_MAZE_ALL_ALIKE` | Capítulo 06: Laberinto de pasajes similares | 16 | 95–110 |
| `CH_WEST_SIDE` | Capítulo 07: Lado oeste y fisura | 16 | 111–126 |
| `CH_EAST_SIDE` | Capítulo 08: Lado este y pozo | 17 | 127–143 |
| `CH_MAZE_ALL_DIFFERENT` | Capítulo 09: Laberinto de pasajes diferentes | 12 | 144–155 |
| `CH_ORIENTAL_ROOM` | Capítulo 10: Sala oriental y cavernas profundas | 16 | 156–171 |
| `CH_WITT_DIFFERENT` | Capítulo 11: Fin de Witt y áreas secretas | 14 | 0, 172–184 |

- **Cobertura:** 185/185 salas (100%). Cero duplicados, cero salas huérfanas, cero asignaciones fallback.
- **Geometría Draw.io:** 100% de salas cuentan con correspondencia exacta de celda (`cell_id`), página (`page_id`) y dimensiones positivas.

---

## 6. Separación Arquitectónica: LOADED vs. ENABLED

El principio rector de la arquitectura es la separación entre el conocimiento topológico global y el ámbito de jugabilidad activo:

```
[Fuentes Históricas: Open_Adventure.yaml / draw.io]
                    │
                    ▼
       [structural_world.json]
                    │
                    ▼
         [StructuralCatalog]
        (185 salas / 623 viajes)
         [STRUCTURAL / LOADED]
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
[enabled_location_ids]  [Inert Structural Data]
     (34 salas)               (151 salas)
 [FUNCTIONAL/ENABLED]    [STRUCTURAL/DISABLED]
          │                   │
          ▼                   ▼
 [WorldData / Runtime]   [Frontier Blocker]
```

1. **`STRUCTURAL / LOADED`:**
   - Accesible a través de `StructuralCatalog` y métodos `get_structural_*()` de `WorldData`.
   - Contiene el universo de 185 salas históricas.
   - Puramente pasivo: no consume RNG, no incrementa turnos, no instancia actores ni enanos, no evalúa condiciones.

2. **`FUNCTIONAL / ENABLED`:**
   - Restringido estrictamente a las 34 salas de `CH_SURFACE`.
   - Accesible a través de `WorldData.locations`, `WorldData.location()` y `WorldData.describe()`.
   - Gobernable por el bucle de juego activo, parser y `Interpreter`.

3. **`STRUCTURAL / DISABLED`:**
   - 151 salas pertenecientes a CH_02 hasta CH_11.
   - Son conocidas estructuralmente (`has_structural_location == true`), pero inactivas en juego (`is_location_enabled == false`, `location() == null`).
   - Todo intento de movimiento hacia una sala deshabilitada produce inmediatamente `GameState.TravelOutcome.FRONTIER` y es bloqueado sin alterar el turno ni la ubicación del jugador.

---

## 7. Contrato de Inmutabilidad, Copias Defensivas y Fail-Closed

1. **Copias Defensivas:**
   - Todos los métodos de consulta de `StructuralCatalog` (`get_location()`, `get_object()`, `get_chapter()`, `get_all_travel_records()`, `get_travel_records()`) devuelven duplicados profundos (`duplicate(true)`).
   - Ninguna mutación externa sobre los diccionarios o arreglos devueltos puede alterar el estado interno del catálogo.

2. **Política Fail-Closed:**
   - Cualquier error de sintaxis JSON, incompatibilidad de versión de esquema (`schema_version != 1`), identificador duplicado, clave raíz ausente o destino `goto` desconocido causa el fallo inmediato de `load_from_string()` o `load_from_file()`.
   - Ante cualquier fallo, el catálogo ejecuta `_clear()`, garantizando que `is_loaded() == false` y que no queda ningún dato parcial, huérfano o corrupto expuesto a los consumidores.

---

## 8. Hashes SHA-256 de Referencia e Invariantes Congeladas

| Artefacto | Tipo de Hash | Valor Hexadecimal SHA-256 |
|---|---|---|
| `07_godot_open_adventure/godot/data/structural_world.json` | Hash del archivo completo | `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3` |
| `07_godot_open_adventure/godot/data/chapter_01_surface.json` | Hash contractual jugable (pre-CUT A) | `a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f` |
| `07_godot_open_adventure/godot/data/chapter_01_surface.json` | Hash del archivo en disco | `afa33c8898049c5af53d06cc3550edbd8f7d58792c819e6224286e82533438c9` |

---

## 9. Reglas de Compatibilidad y Requisitos de Extensión para R5

Cualquier futuro corte (incluido el propuesto `CAR-CORE-002 / R5 — Structural Navigation Enablement`) debe acatar estrictamente las siguientes reglas:

1. **Ampliación Aditiva de Salas Habilitadas:**
   - La habilitación de salas adicionales debe realizarse extendiendo de forma controlada el conjunto `enabled_location_ids` en `WorldData`.
   - No está permitido modificar las definiciones estáticas de salas, viajes u objetos en `structural_world.json` para facilitar la navegación.

2. **Preservación del Orden de Viaje:**
   - Cuando dos salas habilitadas estén conectadas, la resolución de viaje debe evaluar las reglas respetando el orden canónico histórico (`source_rule_index`).
   - Las conexiones hacia salas no habilitadas deben seguir produciendo `GameState.TravelOutcome.FRONTIER`.

3. **Aislamiento de Mecánicas Complejas en R5:**
   - R5 autoriza exclusivamente navegación estructural. No autoriza la implementación de puzles de capítulos profundos, combate con enanos, el pirata, el puente del troll (`special3`), el cierre de la cueva ni el sistema de puntuación.
   - Las condiciones no implementadas o que dependan de actores/puzles futuros deben mantener un tratamiento explícito y seguro sin corromper el bucle de juego.
