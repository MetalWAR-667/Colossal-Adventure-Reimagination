# CAR-DOC-002 — CH_01 Public README Reconciliation

**Estado:** `CLOSED / PASS` — cierre documental. Fecha: 2026-10-25.
**Baseline:** `0bb51f6891017af2d2aa98a22ddc70675709daf1`.

## Alcance y fuentes

Se actualizó exclusivamente el README público de la raíz para resumir el estado
actual de CH_01 después de CAR-ART-001 a CAR-ART-005. La reconciliación se basó
en `project_state/CURRENT_STATE.md`, los cinco CHANGE artísticos y
`07_godot_open_adventure/README.md`. Este registro documenta el corte y no
sustituye esos informes técnicos ni modifica el estado operativo del proyecto.

## Cambios

El README ahora presenta la dirección C — Línea solar, la reproducción LINE/FILL,
las once escenas visuales integradas y aceptadas (con dos variantes de estado
para LOC_GRATE), la selección visual desde GameState y la composición actual
de la interfaz. Aclara que las escenas visuales no equivalen a localizaciones
jugables y conserva TAB como modo de depuración.

Se distinguen las 400 comprobaciones del baseline histórico de las 448 de la
suite actual, así como los resultados focalizados de los prototipos y lotes
artísticos; no se suman como pruebas independientes. También permanecen
explícitos la revisión integral de experiencia pendiente, el pulido diferido de
GRATE_OPEN, los costes de preparación, el trabajo final de interfaz/grafo y las
dependencias globales aún pendientes para CH_02. No se anuncian CH_02 ni
SAVE/LOAD como funciones implementadas.

Se añadieron enlaces relativos a las galerías de CAR-ART-004 y CAR-ART-005 y a
los informes CAR-ART-001 a CAR-ART-005. Se conservaron los apartados existentes
de objetivos, estructura, instalación, verificación, autoría, licencias,
procedencia y Steamworks.

## Verificación y límites

- `git diff --check`: PASS.
- Los enlaces relativos del README fueron comprobados contra archivos
  existentes y versionados.
- Las cifras y estados se contrastaron con los documentos de autoridad citados.
- No se repitieron las suites Godot: el corte solo modifica documentación y la
  autorización excluye esa repetición.
- Sin cambios en código, pruebas, recursos, manifiesto ni estado operativo.
- Finalización mediante CAR-AUTO-001 con inventario explícito; commit local y
  sincronización a Drive. **NO PUSH.**
