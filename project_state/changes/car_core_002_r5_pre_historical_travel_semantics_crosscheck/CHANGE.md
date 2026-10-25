# CAR-CORE-002 / R5-PRE — Historical Travel Semantics Crosscheck

**Estado:** `CLOSED / VERIFIED — R5A READY`

**Fecha:** 2026-10-26

**Baseline inspeccionado:** `3b9a8f82f702464783314c5ff95ff893311525e1`

**Tipo:** Auditoría técnica y contrastación histórica de semántica de viajes; sin modificaciones en código runtime ni datasets

**Implementación R5A:** `PROPOSED / NOT AUTHORIZED`

---

## 1. Decisión y Veredicto

La auditoría técnica y contrastación diferencial contra el código C original de Open Adventure 1.22 (`codigo_fuente_open_adventure/`) concluye con **`CLOSED / VERIFIED — R5A READY`**:

1. **Fidelidad Demostrada:** El evaluador de Godot CUT B ([`interpreter.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd)) reproduce fielmente el algoritmo histórico de viaje implementado en [`main.c:558-865`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/main.c#L558-L865).
2. **Semántica de Cascada y Fallback:** En Open Adventure C, cuando una condición resulta falsa, la búsqueda avanza saltando todas las entradas idénticas (`traveleq`) y evaluando la siguiente regla distinta sin re-comprobar si el verbo coincide. En Godot, [`Interpreter._select_from()`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd#L333-L345) y [`_next_distinct()`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd#L326-L330) replican con precisión milimétrica este comportamiento.
3. **Validación de R5A:** Para la frontera de la reja ([`LOC_GRATE`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd) ↔ [`LOC_BELOWGRATE`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd)), los 19 escenarios de prueba diferenciales (descenso y retorno con reja abierta/cerrada, verbos `ENTER`, `DOWN`, `INWAR`, `OUT`, `UPWAR`, `UP`, `BACK` y salidas colindantes) obtuvieron **100% de coincidencia exacta** entre C y Godot.
4. **Política Anti-Bypass Confirmada:** Ante dependencias no instanciadas en runtime (ej. `NUGGET`), el evaluador actual se detiene emitiendo `DEPENDENCY_PENDING`, impidiendo que el jugador caiga a salas no implementadas (como `LOC_MISTHALL`). Tratar condiciones desconocidas como `false` introduciría graves saltos espurios.
5. **Reconciliación de Enanos:** Se demostró mediante [`main.c:335`](file:///C:/remake/Colossal-Adventure-Reimagination-public/codigo_fuente_open_adventure/main.c#L335) que los enanos permanecen inactivos (`dflag == 0`) hasta que el jugador entra en una sala con bandera `DEEP`. `LOC_PITTOP` no posee la bandera `DEEP`, por lo que su inclusión en el futuro subgrafo seguro de R5B es viable y segura.
6. **No Modificación:** No se modificó ningún archivo ejecutable, dataset ni script de pruebas del repositorio.

El informe técnico exhaustivo con el inventario completo se encuentra en:
[`project_state/changes/car_core_002_r5_pre_historical_travel_semantics_crosscheck/HISTORICAL_TRAVEL_CROSSCHECK.md`](file:///C:/remake/Colossal-Adventure-Reimagination-public/project_state/changes/car_core_002_r5_pre_historical_travel_semantics_crosscheck/HISTORICAL_TRAVEL_CROSSCHECK.md).

---

## 2. Clasificación de las 39 Cadenas Mixtas

De las 39 interacciones mixtas analizadas en el catálogo estructural:
- **`VERIFIED_EQUIVALENT` (2 casos):** Casos 1 y 2 (`LOC_GRATE` y `LOC_BELOWGRATE`). Coincidencia demostrada mediante ejecución diferencial.
- **`SAFE_WITH_EXISTING_STATE` (1 caso):** Caso 21 (`LOC_IMMENSE` con `DOOR`). Objeto instanciado; sala inerte.
- **`DEPENDENCY_PENDING` (36 casos):** Requieren objetos no instanciados en runtime o pertenecen a salas probabilísticas no habilitadas.
- **`CONFIRMED_DIVERGENCE` (0 casos):** Cero discrepancias en la lógica del motor de navegación.

---

## 3. Hoja de Ruta y Próximo Paso

El corte preparatorio R5-PRE concluye con éxito. El siguiente corte propuesto es:

**`CAR-CORE-002 / R5A — Cave Mouth Pilot (LOC_BELOWGRATE)`**
- **Alcance:** Habilitar de forma aislada `LOC_BELOWGRATE` en [`WorldData`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd), proporcionando adaptador de carga e integración de descripción histórica en inglés como fallback.
- **Estado:** `PROPOSED / NOT AUTHORIZED` (requiere autorización humana expresa).

---

## 4. Estado de los Contratos y Baseline

- **Código de producto:** 0 archivos modificados en `07_godot_open_adventure/godot/src/`.
- **Datos de runtime:** 0 archivos modificados en `07_godot_open_adventure/godot/data/`.
- **Digests de referencia:**
  - `chapter_01_surface.json`: `a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f` (intacto).
  - `structural_world.json`: `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3` (intacto).
- **Verificación:** Suite de verificación `verify.ps1` ejecutada con éxito (7/7 fases).
