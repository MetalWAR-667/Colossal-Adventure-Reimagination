# CAR-CORE-002 / R5 — Structural Navigation Decision Gate

**Estado:** `CLOSED / DECISION GATE — VIABLE WITH CONDITIONS`

**Fecha:** 2026-10-25

**Baseline inspeccionado:** `aef24804fbe417ef028c91fa86d42aa258fd3bb9`

**Tipo:** Auditoría técnica y documentación previa a implementación; sin modificaciones en código runtime ni datasets

**Implementación R5:** `PROPOSED / NOT AUTHORIZED`

---

## 1. Decisión del Decision Gate

La habilitación de navegación hacia salas históricas fuera de Capítulo 01 (`CH_SURFACE`) es **VIABLE WITH CONDITIONS** bajo la **Alternativa C (Subconjunto con dependencias verificadas)**.

La viabilidad está estrictamente condicionada al cumplimiento de los principios arquitectónicos y garantías observables formalizados en los cortes R1 a R4:

1. **Separación contractual LOADED vs. ENABLED:** Las 185 ubicaciones históricas continúan residiendo de forma inerte en [`StructuralCatalog`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/structural_catalog.gd). Una sala sólo se vuelve navegable si se añade explícitamente a `WorldData.enabled_location_ids` y sus dependencias han sido verificadas.
2. **Regla de oro anti-bypass (Precedencia estricta):** En las 39 cadenas mixtas donde una regla condicional precede a una incondicional (`always`) para el mismo verbo de movimiento, el motor **no debe** evaluar la condición como `false` por defecto ante dependencias no instanciadas. Si el objeto, actor o variable no existe en el estado de ejecución, la navegación debe detenerse con `TravelOutcome.DEPENDENCY_PENDING`. Tratarlo como `false` constituiría un salto espurio a la regla incondicional posterior, alterando la semántica histórica original.
3. **Fallback transparente de textos y localización:** Las salas de capítulos 02 a 11 carecen de traducción española en `ui_text.es.translation`. El adaptador en `WorldData` debe presentar la descripción histórica original en inglés (`description_long` / `description_short`) almacenada en `structural_world.json`, sin requerir una campaña previa de localización ni alterar el catálogo de textos de CH_01.
4. **Acotamiento estricto al subgrafo seguro de CH_ENTRY:** No habilitar las 151 salas restantes en bloque. El primer corte funcional debe limitarse exclusivamente a la boca de la cueva (`LOC_BELOWGRATE`) y a las salas seguras de `CH_ENTRY`, aislando las fronteras letales (`LOC_PITTOP` hacia `MISTHALL` sin pepita de oro), mecánicas bloqueantes (`FISSURE`, `TROLL`, `DRAGON`, `PLANT`) y actores enanos (`CH_ENTRY` posee la sala de spawn `LOC_PITTOP` del enano 1).
5. **Preservación íntegra de CUT A–D:** Cero alteraciones en el dataset jugable de superficie ([`chapter_01_surface.json`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/data/chapter_01_surface.json), digest `a49db669...`), los esquemas de persistencia ni el bucle de viaje ya verificado.
6. **No implementación:** Este corte cierra exclusivamente la auditoría técnica. Cualquier cambio en [`world_data.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd) u otros componentes para habilitar salas queda diferido a cortes de implementación expresamente autorizados (propuesto: `CAR-CORE-002 / R5A`).

---

## 2. Respuestas a las 12 Preguntas de la Auditoría

El informe técnico exhaustivo [`project_state/changes/car_core_002_r5_navigation_decision_gate/NAVIGATION_AUDIT.md`](file:///C:/remake/Colossal-Adventure-Reimagination-public/project_state/changes/car_core_002_r5_navigation_decision_gate/NAVIGATION_AUDIT.md) documenta las siguientes respuestas:

### 1. Infraestructura existente para navegar entre ubicaciones históricas
[`GameState`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/game_state.gd) gestiona de forma probada la posición del jugador (`current_location`), la historia de movimiento (`oldloc`, `oldlc2`) y las salas visitadas (`visited`). [`Interpreter`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/interpreter.gd) implementa la resolución ordenada de viajes, evaluación de condiciones (`_condition_holds`), cascadas de salas forzadas (`_resolve_forced_transits` con límite de 64 pasos), retroceso (`BACK`), turnos y ciclo de oscuridad. [`StructuralCatalog`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/structural_catalog.gd) proporciona acceso de solo lectura y copia defensiva a las 185 salas y 623 viajes.

### 2. Impedimentos para utilizar directamente las 151 ubicaciones adicionales
1. `WorldData.locations` sólo contiene 34 salas; intentar moverse a una sala estructural no registrada en `locations` activa la barrera de frontera `TravelOutcome.BORDER`.
2. Las descripciones dependen de claves de traducción inexistentes en `ui_text.es.translation`.
3. Existen 39 cadenas de viaje mixtas que saltarían a destinos erróneos si no se comprueba la presencia de los objetos requeridos.
4. Hay 22 salas con comportamiento forzado (`is_forced`) y 4 letales que carecen de los gestores de interacción y muerte fuera del alcance de CUT D.
5. Faltan en el estado mutable los 62 objetos restantes (sólo hay 8 en runtime).

### 3. Reglas de viaje implementadas completamente
574 de los 623 registros de viaje son incondicionales (`always`) hacia destinos numéricos de sala. De ellos, 126 pertenecen a CH_01 y están activos. En el resto del mundo, los viajes `always` entre salas ordinarias funcionan inmediatamente si las salas de origen y destino están en `WorldData.locations`. Asimismo, las reglas de tránsito de texto (`SPEAK`, tipo 3) están modeladas en el catálogo.

### 4. Reglas que dependen de puzles, objetos, actores o estados pendientes
- 49 reglas con condición: 25 `not`, 12 probabilísticas (`%`), 7 `carry`, 4 `with`, 1 `nodwarves`.
- Dependencias de objetos: `GRATE` (estado abierto/cerrado), `FISSURE` (puente de cristal), `TROLL` (presencia y peaje), `SNAKE` (bloqueo en King of Hall), `DRAGON`, `PLANT`, `DOOR`, `CLAM`, `EMERALD`, `NUGGET`, `BIRD`, `ROD`.
- Destinos especiales: `special_handler` (troll bridge, special 3).

### 5. Ubicaciones que pueden habilitarse sin introducir lógica nueva
Exactamente **6 salas ordinarias** de `CH_ENTRY` (`LOC_BELOWGRATE`, `LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`), **1 sala forzada transitoria** (`LOC_CRACK`) y **2 salas de tránsito de palabra mágica** (`LOC_FOOF1`, `LOC_FOOF2` para el comando `XYZZY`).

### 6. Ubicaciones que requieren semántica adicional antes de ser navegables
- `LOC_MISTHALL`: Requiere evaluación segura de la condición letal de `NUGGET` (caída en pozo) y soporte de oscuridad extendida.
- `LOC_EASTBANK` / `LOC_WESTBANK`: Requieren el puzle de `FISSURE` / `ROD` para cruzar el abismo.
- `LOC_HMK` (Hall of Mountain King): Requiere el actor/puzle de la serpiente (`SNAKE`).
- 142 salas adicionales de capítulos 03 a 11 con múltiples dependencias de tesoros, pirata, enanos y endgame.

### 7. Cambios mínimos necesarios en el runtime
1. Adaptador en [`world_data.gd`](file:///C:/remake/Colossal-Adventure-Reimagination-public/07_godot_open_adventure/godot/src/core/world_data.gd): método `enable_structural_location(id: String) -> bool` que instancie la sala en `locations` extrayéndola de `StructuralCatalog` y configurando el fallback de texto en inglés.
2. Interacción con `GRATE`: `LOC_BELOWGRATE` exige que la reja esté abierta (`GRATE.state == 1`) para viajar entre `LOC_GRATE` y `LOC_BELOWGRATE`, lo cual ya está modelado en `objects` de CH_01.
3. Tratamiento de `DEPENDENCY_PENDING`: el intérprete ya contiene la detección en `_select_from()`; únicamente debe garantizarse que los mensajes devueltos al usuario sean diagnósticos y respetuosos.

### 8. Primer corte R5 seguro, pequeño y verificable
`CAR-CORE-002 / R5A — Cave Mouth Pilot (LOC_BELOWGRATE)`:
Habilitar una única localización (`LOC_BELOWGRATE`). Permite descender por la reja abierta desde `LOC_GRATE`, observar la descripción histórica de la cámara bajo la reja y regresar a la superficie mediante `OUT` o `UP`.

### 9. Análisis de precedencia y prevención de bypass
En 39 bifurcaciones históricas, una regla condicional precede a una incondicional para el mismo verbo (ej. en `LOC_PITTOP`: `DOWN` con condición `carry NUGGET` va a `LOC_NECK`, mientras que `DOWN` incondicional va a `LOC_MISTHALL`).
Si el objeto `NUGGET` no está instanciado en runtime, evaluar `cond_holds == false` provocaría que el jugador caiga forzosamente a `LOC_MISTHALL` (y muera) aunque llevase la pepita conceptualmente.
**Garantía R5:** Si `cond_object` no existe en `WorldData.objects`, el selector de reglas interrumpe la búsqueda y emite `TravelOutcome.DEPENDENCY_PENDING`, impidiendo saltar a la regla incondicional posterior.

### 10. Retroceso, salas forzadas y transitorias
- `BACK`: Funciona correctamente utilizando `oldloc` en salas ordinarias. En salas con bandera `NOBACK` (50 en el catálogo), emite `TravelOutcome.FORBIDDEN` con mensaje histórico.
- `is_forced`: El intérprete ejecuta transiciones forzadas en cascada preservando `oldlc2` y `oldloc`. `LOC_CRACK` en `CH_ENTRY` es una transición forzada transitoria que desemboca de inmediato en `LOC_DEBRIS`.

### 11. Matriz de dependencias bloqueantes por subsistema y capítulo
- **Enanos:** Afecta a 6 posiciones iniciales (`dwarflocs`: `LOC_PITTOP`, `LOC_HMK`, `LOC_WESTBANK`, `LOC_FLOOR`, `LOC_LONGWEST`, `LOC_SHELL`), requiriendo que los enanos no se activen o que sus salas de spawn no ejecuten el ciclo de combate hasta CUT E.
- **Oscuridad:** El catálogo marca con `LIT` las salas iluminadas; todas las salas de cueva sin `LIT` dependen del estado encendido de la linterna (`LAMP`).
- **Muerte:** 4 salas letales (`LOC_PITTOP` precipicio, `LOC_WINDOW1` caída, `LOC_WESTWINDOW` caída, `LOC_BRIDGE` caída al abismo).

### 12. Comparativa de alternativas arquitectónicas
- **Alternativa A (Habilitación global indiscriminada):** ❌ Rechazada. Habilitar las 185 salas rompería la semántica histórica por colapso de condiciones no resueltas y desorientación del jugador en salas incompletas.
- **Alternativa B (Habilitación por capítulos completos):** ❌ Rechazada. CH_02 no puede habilitarse completo porque contiene `FISSURE` y `SNAKE`, que bloquearían la progresión.
- **Alternativa C (Subconjunto con dependencias verificadas):** ✅ **SELECCIONADA.** Habilitar salas de forma incremental bajo el control estricto de dependencias y pruebas de regresión.
- **Alternativa D (Modo fantasma / sólo grafo):** ❌ Rechazada. No aporta valor a la jugabilidad y mezcla conceptos de depuración con la experiencia principal.

---

## 3. Hoja de Ruta Propuesta para Cortes R5

Se propone estructurar la implementación de R5 en tres micro-cortes incrementales:

| Corte | Identificador | Alcance | Dependencias |
|---|---|---|---|
| **R5A** | `CAR-CORE-002 / R5A` | **Cave Mouth Pilot (`LOC_BELOWGRATE`)**<br>Habilitar `LOC_BELOWGRATE`. Probar transición bidireccional desde `LOC_GRATE` (reja abierta/cerrada) y visualización de descripción histórica en inglés. | `WorldData` adapter, fallback de traducción. |
| **R5B** | `CAR-CORE-002 / R5B` | **Hall of Mists Vestibule (`CH_ENTRY` Safe Subgraph)**<br>Habilitar 5 salas ordinarias (`LOC_COBBLE`, `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`, `LOC_PITTOP`) y 1 forzada (`LOC_CRACK`). Bloquear salidas letales y no implementadas con `DEPENDENCY_PENDING`. | R5A, regla anti-bypass verificada. |
| **R5C** | `CAR-CORE-002 / R5C` | **Magic Transit & Word Connections**<br>Habilitar `LOC_FOOF1` y `LOC_FOOF2`. Verificar el transporte bidireccional con la palabra mágica `XYZZY` entre `LOC_START` / `LOC_BUILDING` y `LOC_DEBRIS`. | R5B, soporte de transit rooms en intérprete. |

**Nota contractual:** Ninguno de estos cortes está autorizado. Su ejecución requerirá autorización humana explícita.

---

## 4. Estado de los Contratos y Regresiones

- **Código de producto:** 0 archivos modificados en `07_godot_open_adventure/godot/src/`.
- **Datos de runtime:** 0 archivos modificados en `07_godot_open_adventure/godot/data/`.
- **Suite de pruebas:** Se mantiene 100% verde en las 7 fases de `verify.ps1`.
- **Digests congelados:**
  - `chapter_01_surface.json`: `a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f` (intacto).
  - `structural_world.json`: `fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3` (intacto).
  - `chapter_01_surface.manifest.sha256`: `afa33c8801d0a514d021c326e3c0a46979ce4253fa89d46d03d3c8c7fca539aa` (intacto).

---

## 5. Política CAR-AUTO-001

Este corte corresponde exclusivamente a un Decision Gate de investigación y auditoría documental.
Conforme a la política permanente `CAR-AUTO-001`:
1. Los archivos auditados y creados se registran mediante commit local.
2. Se sincroniza el snapshot hacia Google Drive.
3. **No se realiza push** a repositorios remotos.
