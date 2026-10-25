# CAR-CORE-002 / R1 — Canonical Room Inventory

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-25
**Baseline inspeccionado:** `1886fdcc87911d1252cb75bccfaa2c971939f672`
**Tipo:** Tooling, artefactos de inventario canónico, pruebas automatizadas y documentación
**Corte anterior:** `CAR-CORE-002 Complete Historical Room Reconstruction Decision Gate` (`1886fdcc87911d1252cb75bccfaa2c971939f672`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R2 — Complete Structural Data Projection` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Autorización Humana

Conforme al Decision Gate cerrado el 25 de octubre de 2026 (`project_state/changes/car_core_002_complete_room_reconstruction_decision_gate/CHANGE.md`) en estado `CLOSED / VIABLE WITH CONDITIONS`, la autoridad humana autorizó exclusivamente la ejecución del corte:

**CAR-CORE-002 / R1 — Canonical Room Inventory**

Alcance estricto autorizado:
- Creación de un inventario canónico determinista de ubicaciones, viajes, objetos y capítulos.
- Implementación de un generador y validador reproducible en tooling.
- Construcción de una matriz de dependencias estructurales estáticas.
- Suite de pruebas automatizadas con aserciones focales y fixtures negativos.
- **Límites inviolables:** No implementar R2, R3 ni R4. No habilitar nuevas salas jugables. No modificar el runtime de Godot (`godot/src/`, `WorldData`, `GameState`, `Interpreter`, `CommandParser`). No alterar el dataset jugable existente (`chapter_01_surface.json`). No modificar las fuentes históricas originales (`Open_Adventure.yaml`, `Open_Adventure_World_V3.drawio`).

---

## 2. Fuentes de Autoridad Reutilizadas

El inventario no inventa datos ni actúa como un segundo origen de verdad; se deriva deterministamente de las autoridades existentes:

1. **Datos históricos:** `06_reconstruccion_drawio/Open_Adventure.yaml` (SHA-256: `4ee2c6451a64591bacfcec890efa60e15324411897cce894a79eff01cdf35747`).
2. **Partición editorial de capítulos:** `06_reconstruccion_drawio/tools/oa_chapters.py` (definición canónica de 11 capítulos).
3. **Geometría y diagrama:** `06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio` (SHA-256: `a67521fd3d8addd04deda504926c715f5db0395c8adbb0414951f048199370e2`).
4. **Semántica C histórica:** Reglas de inicialización y derivación de `init.c` (p. ej. regla para salas forzadas `FORCED` y orden de precedencia de viajes).

---

## 3. Diseño del Inventario y Arquitectura

El inventario se estructura en artefactos modulares JSON deterministas (con claves ordenadas, sangrado de 2 espacios y terminación de línea `\n`) bajo `07_godot_open_adventure/canonical_inventory/`, acompañados de dos informes técnicos bajo `07_godot_open_adventure/reports/`:

- **`manifest.json`:** Raíz de metadatos con hashes SHA-256 de las fuentes, conteos de referencia verificados y sumas de comprobación de los artefactos.
- **`locations.json`:** 185 ubicaciones históricas en orden original (índices 0..184), clasificadas por rol estructural (`ordinary`, `special`, `transient`, `lethal`, `null`), banderas históricas, descripciones larga/corta, recuento de viajes salientes, objetos iniciales, hints y geometría draw.io completa (`x`, `y`, `width`, `height`, `cell_id`, `page_id`).
- **`travel.json`:** 623 registros de viajes en estricto orden de precedencia original, destinos tipados (`goto`, `speak`, `special`), condiciones normalizadas (`always`, `not`, `pct`, `carry`, `with`, `nodwarves`), resolución de destinos, 85 cruces de capítulo explícitos y dependencias de sistema.
- **`objects.json`:** 70 entradas originales (incluido el centinela `NO_OBJECT`), portabilidad, ubicaciones primarias y fijas múltiples, estados declarados, textos, condición de tesoro y relaciones con reglas de viaje.
- **`chapters.json`:** 11 capítulos canónicos con metadatos, páginas asociadas y miembros, con 100% de cobertura y cero fallback.
- **`structural_dependencies.json`:** Matriz epistémica que desglosa cruces, objetos en condiciones, destinos especiales, salas forzadas/letales, banderas y dependencias en runtime pospuestas.

---

## 4. Conteos Canónicos Verificados

| Elemento | Total verificado | Estado de validación |
|---|---:|---|
| Ubicaciones históricas | 185 | EXACT MATCH |
| Registros de viaje | 623 | EXACT MATCH |
| Entradas de objetos | 70 | EXACT MATCH |
| Capítulos editoriales | 11 | EXACT MATCH |
| Objetos portátiles | 36 | EXACT MATCH |
| Objetos inmóviles | 33 | EXACT MATCH |
| Centinela `NO_OBJECT` | 1 | EXACT MATCH |
| Objetos con colocación múltiple | 11 | EXACT MATCH |
| Objetos con varios estados | 26 | EXACT MATCH |
| Objetos inicialmente ausentes / NOWHERE | 18 | EXACT MATCH |
| Tesoros | 20 | EXACT MATCH |
| Cruces de viaje entre capítulos | 85 | EXACT MATCH |
| Ubicaciones con movimiento forzado (`is_forced`) | 22 | EXACT MATCH |

### Condiciones de viaje observadas
- `always`: 574
- `not`: 25
- `pct` (probabilística): 12
- `carry`: 7
- `with`: 4
- `nodwarves`: 1
- **Total:** 623

### Tipos de destino observados
- `goto`: 583
- `speak`: 34
- `special`: 6
- **Total:** 623

### Clasificación estructural de ubicaciones
- `ordinary` (jugable): 162
- `special`: 13
- `transient`: 5
- `lethal`: 4
- `null`: 1
- **Total:** 185

---

## 5. Archivos Creados y Modificados

### Archivos Creados
1. `07_godot_open_adventure/canonical_inventory/manifest.json` (2.015 bytes)
2. `07_godot_open_adventure/canonical_inventory/locations.json` (306.328 bytes)
3. `07_godot_open_adventure/canonical_inventory/travel.json` (413.241 bytes)
4. `07_godot_open_adventure/canonical_inventory/objects.json` (72.011 bytes)
5. `07_godot_open_adventure/canonical_inventory/chapters.json` (8.357 bytes)
6. `07_godot_open_adventure/canonical_inventory/structural_dependencies.json` (55.939 bytes)
7. `07_godot_open_adventure/reports/CANONICAL_ROOM_INVENTORY_REPORT.md` (informe de validación para humanos)
8. `07_godot_open_adventure/reports/STRUCTURAL_DEPENDENCY_MATRIX.md` (matriz de dependencias OBSERVED / INFERRED / PENDING)
9. `07_godot_open_adventure/tools/oa_canonical_inventory.py` (herramienta generadora y comprobadora determinista)
10. `07_godot_open_adventure/tools/test_canonical_inventory.py` (suite de 26 pruebas unitarias y fixtures negativos)
11. `project_state/changes/car_core_002_r1_canonical_room_inventory/CHANGE.md` (este registro de cierre)

### Archivos Modificados
12. `07_godot_open_adventure/tools/verify.ps1` (integración de la validación del inventario canónico y resolución automática del ejecutable Godot en `tools/`)
13. `project_state/CURRENT_STATE.md` (actualización del estado del proyecto)

---

## 6. Hashes SHA-256 de Artefactos Versionados

| Archivo | SHA-256 |
|---|---|
| `canonical_inventory/chapters.json` | `90bd9d39622d20e66b3f4b2a9965cddde6478ac89aeae12bb3cb6b89c5feac53` |
| `canonical_inventory/locations.json` | `8289888c62ddaf8ceaeb90ead05c6f3b22e74d6f5a03d9cbb6cd6b3b472afb95` |
| `canonical_inventory/manifest.json` | `d0961127509996e2396a6ac4ef897a1492788335e27440531ee3dd000e63b040` |
| `canonical_inventory/objects.json` | `cfa3588ab53822ed07d2f6939ab14d2aa0d3b099ef34f8458ad4f3cfdb5002e6` |
| `canonical_inventory/structural_dependencies.json` | `7d63c00879f3658ce4f0db20aec252c5c13e3649be2865bb7030163314e61519` |
| `canonical_inventory/travel.json` | `87d28a4b39c7900b0411b80b9e2caef13486deb5181c39cf998e36fb141218d4` |
| `reports/CANONICAL_ROOM_INVENTORY_REPORT.md` | `8f0c0c22b83c71a8fb743888e4ff52d2fbdb1ffb45c1838551b658b207c6a0da` |
| `reports/STRUCTURAL_DEPENDENCY_MATRIX.md` | `5ff817078f93a9197a526fcd8e604b144878efd9b03b84ca099b84b24e86a1e3` |
| `tools/oa_canonical_inventory.py` | `0d0c3eb1df30d5fc7c603b1e39eb14ca2f33f3885d519b7d8b3c6310eeef370b` |
| `tools/test_canonical_inventory.py` | `80d59c81c5e1f99a6670f2ff8e6696976e14fa9f65315d58b19e3b23e14daa4b` |

---

## 7. Pruebas y Validación Ejecutadas

### A. Pruebas Focales y Negativas de R1
`python 07_godot_open_adventure/tools/test_canonical_inventory.py`:
- 20 pruebas focales verificando exactamente las 20 aserciones obligatorias.
- 6 pruebas negativas verificando rechazo de ID duplicado, destino desconocido, asignación editorial errónea, índice de objeto duplicado, alteración de orden de viajes y ausencia en draw.io.
- **Resultado:** `Ran 26 tests in 2.909s — OK`.

### B. Comprobador Determinista
`python 07_godot_open_adventure/tools/oa_canonical_inventory.py --check`:
- Compara byte a byte los 6 archivos de disco contra la reconstrucción en memoria.
- **Resultado:** `PASS: all canonical inventory artifacts match regenerated authoritative source data`.

### C. Suite de Regresión Integral (`verify.ps1`)
Ejecutado con Godot `4.7.2.stable.official.ed1daf0bf`:
- **1/7 export determinism & canonical inventory:**
  - `oa_export_godot.py --check`: OK
  - `test_simulation_graph.py`: 10 tests OK
  - `oa_canonical_inventory.py --check`: PASS
  - `test_canonical_inventory.py`: 26 tests OK
- **2/7 godot import:** PASS
- **3/7 engine tests:**
  - Juego base: 448 checks PASS
  - CUT A isolation: 12 checks PASS (151 simulation-only IDs examinados)
  - CUT B travel: 54 checks PASS
  - CUT C darkness/lamp: 61 checks PASS
  - CUT D death/reincarnation: 34 checks PASS
- **4/7 illustration sheet:** 11 scenes rendered PASS
- **5/7 runtime illustration integration:** 62 checks PASS
- **6/7 CH_01 vector art:** 9 drawings deterministic PASS, 455 checks PASS
- **7/7 GRATE state art:** 2 state drawings deterministic PASS, 150 checks PASS
- **Resultado final:** `ALL CHECKS PASSED`.

---

## 8. Dependencias Pendientes Registradas

Se mantiene el registro explícito de subsistemas en estado `PENDING / NOT AUTHORIZED`:
1. `special_3_troll_bridge`: cruce interactivo del troll desde `LOC_SWCHASM` y `LOC_NECHASM`.
2. `dwarf_and_pirate_actors`: simulación global de actores (`dwarfmove`, `spotted_by_pirate`).
3. `cave_closing_and_endgame`: lógica de cierre (`closecheck`) y reubicación al repositorio.
4. `global_treasure_scoring`: evaluación de puntuación con los 20 tesoros.
5. `dynamic_hints`: sistema dinámico de pistas basado en turnos y salas.
6. `darkness_lamp_full_lifecycle`: ciclo global de oscuridad fuera de CH_01.

---

## 9. Riesgos Mitigados y Límites Respetados

- **Sin segundo origen de verdad:** El inventario se regenera deterministamente desde el YAML y draw.io.
- **Sin contaminación de runtime:** `WorldData`, `GameState`, `Interpreter` y `CommandParser` no fueron modificados.
- **Sin habilitación de salas:** Las 151 salas no pertenecientes a CH_01 permanecen no jugables.
- **Condiciones sin evaluar:** Ninguna condición pendiente fue resuelta silenciosamente como verdadera o falsa ni consumió RNG.
- **Fidelidad histórica:** Se preservó la descripción nula de `LOC_NOWHERE` y la descripción vacía `""` de `LOC_BUILDING1`.

---

## 10. Próximo Corte Propuesto

**CAR-CORE-002 / R2 — Complete Structural Data Projection**

**Estado obligatorio:** `PROPOSED / NOT AUTHORIZED`

*Nota:* R2 proyectará la estructura completa de forma aditiva y versionada, demostrando la equivalencia exacta del filtro jugable de CH_01. No debe iniciarse sin autorización humana expresa.
