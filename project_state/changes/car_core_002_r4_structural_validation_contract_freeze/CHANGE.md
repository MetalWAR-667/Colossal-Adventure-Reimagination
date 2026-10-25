# CAR-CORE-002 / R4 — Structural Validation & Contract Freeze

**Estado:** `CLOSED / PASS`
**Fecha:** 2026-10-25
**Baseline inspeccionado:** `d856ef4986479d28df91a0674d0c3d4a8cfd0d71`
**Tipo:** Auditoría estructural, formalización contractual, congelación de invariantes, suite de tests en Godot y documentación
**Corte anterior:** `CAR-CORE-002 / R3 — Structural Loader & Enabled View` (`d856ef4986479d28df91a0674d0c3d4a8cfd0d71`)
**Siguiente corte propuesto:** `CAR-CORE-002 / R5 — Structural Navigation Enablement` (`PROPOSED / NOT AUTHORIZED`)

---

## 1. Autorización Humana

Conforme al Decision Gate de CAR-CORE-002 (`CLOSED / VIABLE WITH CONDITIONS`) y los cierres exitosos de R1, R2 y R3, la autoridad humana autorizó exclusivamente la ejecución de:

**CAR-CORE-002 / R4 — Structural Validation & Contract Freeze**

Alcance autorizado:
- Auditoría integral de los contratos observables derivados de la arquitectura R1–R3.
- Formalización contractual por escrito de la cadena de autoridad, esquema estructural v1, taxonomía de condiciones, modelo estático de objetos, separación arquitectónica `LOADED` vs. `ENABLED` y copias defensivas.
- Elaboración de una matriz de trazabilidad completa entre fuentes históricas, artefactos, cargador, runtime y pruebas.
- Suite de pruebas focales en Godot que implemente y verifique al menos 32 aserciones organizadas en cuatro grupos (Autoridad, Carga y Aislamiento, Robustez y Negativos, Regresión y Compatibilidad).
- Integración de la suite en la herramienta unificada de validación `07_godot_open_adventure/tools/verify.ps1`.
- **Límites estrictos respetados:** No implementar R5 ni habilitar nuevas salas en runtime (se mantienen exactamente las 34 salas de CH_01). No modificar las fuentes históricas YAML ni draw.io. No modificar `structural_world.json` ni `chapter_01_surface.json`. No alterar `GameState.gd`, `Interpreter.gd` ni `CommandParser.gd`. No implementar actores, puzles ni mecánicas complejas. No realizar push al repositorio remoto.

---

## 2. Auditoría y Formalización Contractual

Se auditaron y congelaron formalmente dos documentos contractuales vinculantes en `project_state/contracts/`:

1. **`CAR_CORE_002_STRUCTURAL_CONTRACT.md`:**
   - Define la cadena unívoca de autoridad (`Open_Adventure.yaml` -> R1 Canónico -> R2 Proyección -> R3 Cargador -> Runtime).
   - Congela el esquema estructural v1 (`res://data/structural_world.json`).
   - Sella las 185 ubicaciones históricas (`LOC_NOWHERE` a `LOC_FOOF6`), 623 viajes ordenados, 70 objetos (con centinela `NO_OBJECT`), 11 capítulos editoriales sin solapamientos ni huérfanas y las 6 posiciones de inicio de enanos.
   - Formaliza la separación `LOADED` (185 salas pasivas en `StructuralCatalog`) vs `ENABLED` (34 salas activas en `WorldData.enabled_location_ids`), y el comportamiento de las 151 salas `DISABLED` como frontera inerte.
   - Sella el contrato de copias defensivas profundas y la política de error fail-closed.
   - Establece las reglas de extensión para el corte R5.

2. **`CAR_CORE_002_TRACEABILITY_MATRIX.md`:**
   - Mapea exhaustivamente cada dimensión de datos (ubicaciones, viajes, condiciones, objetos, geometría, banderas, actores, puzles) con su fuente, artefacto, consumidor, invariante protegida, prueba verificadora, estado y la consecuencia directa si R5 vulnera la invariante.

---

## 3. Batería de Pruebas Focales de Congelación (34 Checks)

Se implementó la suite automatizada `07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd`, ejecutada de forma headless en Godot 4.7.2. La suite auditó 34 comprobaciones con cero fallos (`PASS: 34 CAR-CORE-002 / R4 structural freeze checks completed with 0 failures`):

### Grupo 1: Autoridad y Datos (Checks 1–10)
1. **Total de ubicaciones:** Exactamente 185 ubicaciones históricas, iniciadas en `LOC_NOWHERE` (0) y `LOC_START` (1), finalizadas en `LOC_FOOF6` (184).
2. **Total de viajes:** Exactamente 623 filas de viaje ordenadas globalmente (`0..622`).
3. **Total de objetos:** Exactamente 70 objetos, con centinela `NO_OBJECT` verificado en índice 0.
4. **Capítulos editoriales:** Exactamente 11 capítulos con 100% de cobertura, 0 duplicados y 0 salas huérfanas (suma exacta de miembros = 185).
5. **Dwarflocs históricas:** Conservación estricta de las 6 salas iniciales de generación (`LOC_KINGHALL`, `LOC_WESTBANK`, `LOC_Y2`, `LOC_ALIKE3`, `LOC_COMPLEX`, `LOC_MAZEEND12`).
6. **Orden histórico de reglas de viaje:** Conservación del orden relativo y global (`global_travel_index` 0..622) y orden saliente por sala (`source_rule_index`).
7. **Tipos de condición declarados:** 574 always, 25 not, 12 pct, 7 carry, 4 with, 1 nodwarves (suma exacta = 623).
8. **Destinos especiales:** 583 goto, 34 speak, 6 special (manejadores 1, 2, 3 válidos), 1 nodwarves verificado de `LOC_LONGWEST` a `LOC_DIFFERENT1`.
9. **Objetos multi-ubicación y multi-estado:** Exactamente 11 objetos con `has_multiple_locations` y 26 objetos con `has_multiple_states`.
10. **Resolución de referencias cruzadas:** 0 destinos `goto` rotos y 0 dependencias de objetos no resueltas.

### Grupo 2: Carga y Aislamiento (Checks 11–20)
11. **Carga y metadatos:** Esquema versión 1, cut_id `CAR-CORE-002-R2`, document_status `INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE`.
12. **Catálogo de solo lectura:** Las 185 salas y 70 objetos consultables estructuralmente vía `WorldData`.
13. **Copias defensivas:** Resistencia absoluta a mutaciones externas sobre salas, banderas, viajes, objetos y miembros de capítulos.
14. **Conjunto habilitado:** Restringido exactamente a las 34 salas de `CH_SURFACE`.
15. **Salas deshabilitadas:** Exactamente 151 salas permanecen no habilitadas en runtime (`is_location_enabled == false`).
16. **Preservación funcional:** `WorldData.locations` mantiene 34 salas y `WorldData.objects` 8 objetos; cero contaminación de objetos inertes (`CHEST`, `DRAGON`, etc.).
17. **Aislamiento del parser:** El analizador no incorpora vocabulario ni referencias a objetos de otros capítulos.
18. **Aislamiento cartográfico:** El mapa jugable conserva exactamente 34 nodos y 118 aristas.
19. **Inercia de estado y RNG:** Consultas estructurales no alteran ubicación, turno, objetos ni consumen números de RNG.
20. **Equivalencia de `is_in_chapter()`:** Identidad estricta entre `is_in_chapter()` e `is_location_enabled()` (34 true, 151 false).

### Grupo 3: Robustez y Negativos (Checks 21–26)
21. **Rechazo de sintaxis corrupta:** Diagnóstico explícito ante JSON malformado.
22. **Rechazo de esquema incompatible:** Rechazo ante `schema_version != 1`.
23. **Rechazo de duplicados:** Detección y rechazo de identificadores de sala duplicados.
24. **Rechazo de referencias desconocidas:** Detección de viajes hacia destinos inexistentes.
25. **Rechazo de claves raíz ausentes:** Verificación de presencia obligatoria de `locations`, `travel`, `objects`, `chapters` y `meta`.
26. **Política fail-closed estricta:** Ante cualquier error de carga, el catálogo se vacía por completo sin dejar estado parcial.

### Grupo 4: Regresión y Compatibilidad (Checks 27–32)
27. **Digest de Capítulo 01:** Hash de `chapter_01_surface.json` (`afa33c88...`) y digest contractual jugable (`a49db669...`) preservados.
28. **SHA-256 de `structural_world.json`:** Coincidencia exacta con el hash de referencia de R2 (`fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3`).
29. **Exportación determinista:** Integridad y validez de esquema de ambos artefactos JSON en disco.
30. **Garantías históricas CUT A–D:** Aislamiento de CUT A, viajes de CUT B, lámpara/oscuridad de CUT C y ciclo de muerte de CUT D intactos.
31. **Bucle de juego jugable:** Ejecución completa de la secuencia canónica de CH_01 (`UNLOCK GRATE`) con detención segura en frontera ante `ENTER`.
32. **Blindaje contra habilitación accidental:** El arreglo devuelto por `get_enabled_location_ids()` no permite mutar el conjunto habilitado interno.

---

## 4. Archivos Creados y Modificados

### Archivos Creados
1. `project_state/contracts/CAR_CORE_002_STRUCTURAL_CONTRACT.md`
   - Documento contractual maestro de congelación estructural.
2. `project_state/contracts/CAR_CORE_002_TRACEABILITY_MATRIX.md`
   - Matriz de trazabilidad integral entre fuentes, modelos, pruebas y riesgos.
3. `07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd`
   - Suite formal de pruebas de congelación y regresión estructural (34 checks).
4. `07_godot_open_adventure/godot/tests/test_structural_contract_freeze.gd.uid`
   - UID asignado por Godot 4.7.2.
5. `project_state/changes/car_core_002_r4_structural_validation_contract_freeze/CHANGE.md`
   - Este registro de corte.

### Archivos Modificados
1. `07_godot_open_adventure/tools/verify.ps1`
   - Integración de `test_structural_contract_freeze.gd` en la fase 3/7 de pruebas de motor.
2. `project_state/CURRENT_STATE.md`
   - Actualización del estado a `CLOSED / PASS` para R4 y formalización de la propuesta R5.

---

## 5. Hashes y Firmas Invariantes Verificadas

- **Playable contract digest (pre-CUT A dataset):**
  `a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f` (INTACTO)
- **SHA-256 de `res://data/chapter_01_surface.json` (archivo en disco):**
  `afa33c8898049c5af53d06cc3550edbd8f7d58792c819e6224286e82533438c9` (INTACTO)
- **SHA-256 de `res://data/structural_world.json`:**
  `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3` (INTACTO)

---

## 6. Resultados de Regresión Integral (`verify.ps1`)

Se ejecutó la suite completa `verify.ps1` resultando en `ALL CHECKS PASSED`:
1. **Fase 1/7 (Exportación y Canónico):** Determinismo de datasets, simulación CUT A (10 pruebas), inventario canónico R1 (26 pruebas) y proyección estructural R2 (34 pruebas) `PASS`.
2. **Fase 2/7 (Godot Import):** Registro e importación headless de clases y UIDs `PASS`.
3. **Fase 3/7 (Tests de Motor):** Engine suite (448 checks), CUT A isolation (12 checks), R2 isolation (23 checks), R3 structural loader (37 checks), R4 structural contract freeze (34 checks), CUT B travel cycle (54 checks), CUT C darkness/lamp (61 checks), CUT D death/reincarnation (34 checks) `PASS`.
4. **Fase 4/7 (Contact Sheet):** Generación de hoja de ilustraciones (11 escenas) `PASS`.
5. **Fase 5/7 (Integración de Arte):** Integración de ilustraciones y layout (62 checks) `PASS`.
6. **Fase 6/7 (Vector Art CH_01):** Verificación vectorial determinista (455 checks) `PASS`.
7. **Fase 7/7 (Arte Reja):** Variantes de estado de la reja (150 checks) `PASS`.

---

## 7. Propuesta Detallada para el Siguiente Corte

**CAR-CORE-002 / R5 — Structural Navigation Enablement**
*Estado:* `PROPOSED / NOT AUTHORIZED`

### 7.1 Objetivo y Justificación
Con la proyección estructural global generada (R2), el catálogo cargado en solo lectura (R3), y los contratos observables auditados y congelados (R4), el siguiente paso natural es habilitar la navegación espacial entre salas sin activar todavía puzles complejos, actores ni mecánicas letales que requieran su propia fase de diseño.

### 7.2 Alcance Propuesto para R5
1. **Ampliación Controlada del Conjunto Habilitado:**
   - Habilitar gradualmente salas adicionales conectadas topológicamente mediante adición explícita a `enabled_location_ids`.
   - Permitir al jugador transitar por pasajes incondicionales (`always`) entre salas habilitadas.
2. **Tratamiento Seguro de Condiciones Pendientes:**
   - Tratar de forma determinista y segura los viajes cuyas condiciones dependan de objetos o estados aún no habilitados en runtime (p. ej. denegando el paso con mensaje descriptivo o manteniéndolo como frontera temporal).
3. **Manejo de Salas Forzadas y Especiales:**
   - Incorporar la resolución de salas con flag `FORCED` que encadenan movimiento automático sin input intermedio.
   - Preservar el bloqueo seguro de manejadores especiales complejos (`special3` / puente del troll).
4. **Protección de Aislamiento:**
   - Mantener desactivados los actores dinámicos (enanos, pirata).
   - Mantener inactivo el cierre de la cueva y la puntuación.
   - Verificar que no se introduce drift sobre el comportamiento jugable de Capítulo 01.
