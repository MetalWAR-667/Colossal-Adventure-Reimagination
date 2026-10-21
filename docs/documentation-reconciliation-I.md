# Documentation & Agent Reference Reconciliation I

Task: HARNESS-DOC-RECONCILIATION-I. Fecha: 2026-10-19. Ejecución: Ripley. Estado: **DOCUMENTATION RECONCILED / HUMAN REVIEW PENDING**. Auditoría documental separada de Deckard: PASS acotado, con límites registrados al final. No implica aceptación humana ni autorización de commit.

## Archivos inspeccionados y modificados

Inspeccionados: README, entrada universal, siete contratos de agentes y cuatro reglas enumerados abajo; informe de migración, manifiesto y evidencias históricas; .gitignore, configuración Rust e inventario del workspace. Correcciones exclusivamente documentales:

- `README.md`: corrige la copia temporal anunciada como presente; confirma Git; describe extracción realizada; separa historia/estado; explicita configuración Rust con origen ausente y capacidades pendientes.
- `docs/agent-contract-migration.md`: añade encuadre histórico y actualización posterior. Preserva el cuerpo histórico, sin convertir sus comprobaciones de entonces en comprobaciones actuales. Señala que la recuperación anterior no debe ejecutarse sobre el estado posterior.
- `AGENTS.md` raíz, nuevo: necesidad concreta de orientar el desarrollo del repositorio (arquitectura, estado y evidencias), mientras `contracts/AGENTS.md` sigue siendo la entrada universal distribuible. Reutiliza reglas mediante enlaces, sin duplicar contratos ni autoactivar roles.
- Este informe, nuevo: evidencia separada del corte actual. Su contenido completo se entrega en este archivo; no se incluye una copia recursiva de sí mismo en el diff.

No se modificó ninguno de los doce contratos. Personalidades, responsabilidades, autoridad y semántica de las cuatro reglas permanecen intactas. No se identificó conflicto semántico pendiente de autorización. No se accedió a G: ni a Lands of Folklore.

## Estado comprobado

`git rev-parse --show-toplevel`: C:/MetalLabs-Harness. Rama main sin commits (`git log -1 --oneline` informa rama sin historial). `Test-Path RPG_Archaeology_IF`: False. La ausencia local no demuestra quién eliminó la copia ni el estado del original en G:.

Inventario: ningún project.godot, plugin.cfg o archivo .gd. EditorPlugin, router GDScript, aplicación independiente, skills/templates propios y mecanismos técnicos de seguridad no están implementados. Las cuatro reglas ya identifican comandos, gates, aislamiento y enforcement como futuros/condicionales. La prueba Rust conserva una ruta al origen ausente; no se repara porque es historia inactiva, no carga operativa de contratos.

## Integridad y referencias

Los doce SHA-256 actuales coinciden con los hashes de destino del manifiesto histórico; esto acredita preservación exacta de los contratos, no una nueva comprobación del origen eliminado ni de sus 620 archivos:

| Contrato inspeccionado | SHA-256 actual = destino histórico |
| --- | --- |
| `contracts/agents/butch_architect/AGENT.md` | `7165da5bc89945a258b660a8ca95e56044eb6664b2e3895ef4eae934df9cff67` |
| `contracts/agents/deckard_auditor/AGENT.md` | `7bbaa221b2fe6f0cec029851c5c89457dac7254e0c369bb8d107ee6dfa1ec6f3` |
| `contracts/agents/doc_brown_the_researcher/AGENT.md` | `7a008832416c8200b2cee5e5b5606fc1fa1b9bf60e2b7a313507dcb38c3d811b` |
| `contracts/agents/gandulf_chronicler/AGENT.md` | `86aae158ddc3d3062ca0ca0a8b94a4c24819fe2408950d07cdddf8ba199f03e7` |
| `contracts/agents/jack_burton_the_artist/AGENT.md` | `ef99b272e7049385375c19436212e33fba57a8a61622de5ba87e52b1118a81bc` |
| `contracts/agents/mrwolf_tech_troubleshooter/AGENT.md` | `cd71924156c109f14a8e4c379ae3cc0b6b4a3a188b87a46954c985938b8a81cf` |
| `contracts/agents/ripley_engineer/AGENT.md` | `47d3faacfd2ef50e7b7d646263bcaa550dcee8fa4ba93d0e6d1e8c098a39591c` |
| `contracts/rules/scope-and-authority.md` | `7c11265d09b65de5e7d490882938a37d6748c538348dff7ef80ad5978fefc6db` |
| `contracts/rules/multi-agent-workflow.md` | `d5a64b781b86295985d3ea2072819d4a6105c39193baddfb26a8689be984ab16` |
| `contracts/rules/verification.md` | `f05aaa048cc64e7364cd91f58f86f5e56aa97f54a8fb5f48b18c0510106f4213` |
| `contracts/rules/documentation.md` | `7cc7b68476d08469f3511f5c0937cf2d700bee1039f0a3a15d2e453b32356c1e` |
| `contracts/AGENTS.md` | `586470f3542462530b342a1016255898dbde357137d524eac6884a86b397c2b5` |

Los siete IDs del roster corresponden a carpetas existentes. Búsqueda de RPG, Gandalf, ID plural `troubleshooters` e IF-CUT-001 en contratos: sin coincidencias. Las referencias a Python/pytest, CURRENT_STATE, Drive o diagramas son ejemplos/condiciones, no requisitos de implementación. `../agents/<role>/AGENT.md` es una pauta parametrizada, no ruta literal.

Enlaces relativos comprobados (todos resuelven tras crear este informe):

- `README.md` → `contracts/AGENTS.md`
- `README.md` → `docs/agent-contract-migration.md`
- `README.md` → `docs/documentation-reconciliation-I.md`
- `AGENTS.md` → `contracts/AGENTS.md`
- `AGENTS.md` → `README.md`
- `AGENTS.md` → `docs/documentation-reconciliation-I.md`
- `AGENTS.md` → `docs/agent-contract-migration.md`
- `docs/agent-contract-migration.md` → `documentation-reconciliation-I.md`
- `docs/agent-contract-migration.md` → `migration-evidence/contract-manifest.json`
- `docs/agent-contract-migration.md` → `migration-evidence/contract-transformations.diff`
- `docs/agent-contract-migration.md` → `migration-evidence/README.before.md`
- `docs/agent-contract-migration.md` → `migration-evidence/workspace-before.json`
- `docs/agent-contract-migration.md` → `migration-evidence/workspace-existing-after.json`
- `docs/agent-contract-migration.md` → `migration-evidence/source-git-status-before.txt`
- `docs/agent-contract-migration.md` → `migration-evidence/source-git-status-after.txt`
- `docs/agent-contract-migration.md` → `documentation-reconciliation-I.md`
- `contracts/rules/multi-agent-workflow.md` → `../AGENTS.md`
- `contracts/rules/verification.md` → `../AGENTS.md`
- `contracts/rules/documentation.md` → `../AGENTS.md`
- `contracts/rules/documentation.md` → `../AGENTS.md`
- `contracts/AGENTS.md` → `rules/multi-agent-workflow.md`
- `contracts/AGENTS.md` → `rules/scope-and-authority.md`
- `contracts/AGENTS.md` → `rules/verification.md`
- `contracts/AGENTS.md` → `rules/documentation.md`
- `contracts/AGENTS.md` → `agents/butch_architect/AGENT.md`
- `contracts/AGENTS.md` → `agents/ripley_engineer/AGENT.md`
- `contracts/AGENTS.md` → `agents/mrwolf_tech_troubleshooter/AGENT.md`
- `contracts/AGENTS.md` → `agents/jack_burton_the_artist/AGENT.md`
- `contracts/AGENTS.md` → `agents/deckard_auditor/AGENT.md`
- `contracts/AGENTS.md` → `agents/doc_brown_the_researcher/AGENT.md`
- `contracts/AGENTS.md` → `agents/gandulf_chronicler/AGENT.md`

Las rutas RPG en evidencias y diff son procedencia histórica; no se exige que resuelvan hoy. No se editaron archivos de docs/migration-evidence/.

## Diff de cada corrección

Git está sin primer commit y los archivos están sin seguimiento; git diff no mostraría estas correcciones. Los diffs siguientes reconstruyen el contenido previo observado en la lectura inicial y revierten únicamente las inserciones conocidas del informe. Límite: el snapshot inicial de 26 archivos se guardó en un directorio temporal que resultó efímero entre invocaciones. Su lectura posterior falló con FileNotFoundError; no hay baseline independiente recuperable ni comparación general de 26 archivos que pueda declararse PASS. Los hashes de contratos sí son verificables contra el manifiesto histórico. No se afirma comparación byte a byte independiente de otros archivos preexistentes.

```diff
--- README.md (antes)
+++ README.md (después)
@@ -2,7 +2,7 @@
 
 Biblioteca central de siete contratos universales de agentes y cuatro reglas compartidas.
 
-La arquitectura elegida para el harness es un **EditorPlugin de Godot 4**, desarrollado en **GDScript tipado**, modular y distribuible entre proyectos Godot. El plugin todavía no está implementado. Este corte extrae y documenta los contratos; la distribución junto al plugin queda para su propio corte.
+La arquitectura elegida para el harness es un **EditorPlugin de Godot 4**, desarrollado en **GDScript tipado**, modular y distribuible entre proyectos Godot. El plugin todavía no está implementado. La extracción documental de los contratos ya está realizada; la distribución junto al plugin queda para su propio corte.
 
 ## Biblioteca actual
 
@@ -10,14 +10,14 @@
 
 Un operador puede leer explícitamente la entrada, las reglas aplicables, el contrato del rol seleccionado y el contexto de la tarea. La existencia de Markdown no concede permisos técnicos ni garantiza descubrimiento por una herramienta de IA. Skills y templates vacíos del origen se han excluido y no están disponibles.
 
-La [documentación de migración](docs/agent-contract-migration.md) registra procedencia, ajustes, exclusiones, hashes, verificaciones y reversibilidad.
+La [documentación de migración](docs/agent-contract-migration.md) conserva el registro histórico de procedencia, ajustes, exclusiones, hashes y verificaciones. La [reconciliación documental](docs/documentation-reconciliation-I.md) registra las comprobaciones del estado actual.
 
 ## Prueba Rust conservada
 
-`Cargo.toml`, `src/main.rs`, `config/roles.toml` y `MetalLabs-Harness-Foundation-I.zip` se conservan intactos como experimento histórico del router. No son el punto de entrada ni una dependencia o prerrequisito de la arquitectura elegida. No se ha portado ni ejecutado esa prueba durante esta extracción. Su configuración conserva sus rutas y aliases históricos; no carga la nueva biblioteca central.
+`Cargo.toml`, `src/main.rs`, `config/roles.toml` y `MetalLabs-Harness-Foundation-I.zip` se conservan intactos como experimento histórico del router. No son el punto de entrada ni una dependencia o prerrequisito de la arquitectura elegida. No se ha portado ni ejecutado esa prueba durante la extracción documental ni esta reconciliación. Su configuración conserva sus rutas y aliases históricos; la ruta a `RPG_Archaeology_IF/.agents` ya no existe en este workspace. Esta prueba no carga la biblioteca central y no es un punto de entrada operativo del Harness.
 
-La copia temporal `RPG_Archaeology_IF/` también permanece íntegra mientras se comprueba la extracción. No se ha migrado ningún consumidor ni implementado el plugin. No se han realizado commits.
+Git está inicializado en `C:\MetalLabs-Harness`, en la rama `main`, todavía sin commits. La copia temporal `RPG_Archaeology_IF/` ya no está presente. Estas comprobaciones locales no verifican el estado del proyecto original en `G:`. No se ha migrado ningún consumidor ni implementado el plugin.
 
 ## Estado
 
-Extracción documental ejecutada; revisión humana pendiente. Las verificaciones documentales y sus límites figuran en el informe. Runtime, interfaz gráfica, integración Godot y pruebas operativas del harness: **NOT_RUN / NOT_IMPLEMENTED**. La documentación no implica aceptación humana ni cierre automático.
+Biblioteca documental extraída; reconciliación actual en **HUMAN REVIEW PENDING**. No están implementados el EditorPlugin, el router GDScript, una aplicación independiente, skills/templates propios, la carga automática ni mecanismos técnicos de seguridad y enforcement. La prueba Rust conservada no demuestra esas capacidades. Runtime, interfaz gráfica, integración Godot y pruebas operativas del Harness: **NOT_RUN / NOT_IMPLEMENTED**. La documentación no implica aceptación humana ni cierre automático.
```

```diff
--- docs/agent-contract-migration.md (antes)
+++ docs/agent-contract-migration.md (después)
@@ -1,4 +1,6 @@
 # Agent Contract Migration — extracción documental
+
+> Registro histórico de la extracción documental. Las afirmaciones siguientes sobre ausencia de Git, presencia de la copia temporal, integridad del origen y recuperación describen el momento de aquella extracción; no son instrucciones operativas actuales. Se conserva el cuerpo histórico y su evidencia sin reescribirlos. Véase la actualización al final y la [reconciliación documental](documentation-reconciliation-I.md).
 
 Task: HARNESS-CONTRACT-MIGRATION-001. Fecha: 2026-10-19. Implementación: Ripley, autorizada expresamente en esta sesión. Estado: REVIEW; auditoría documental de Deckard y validación de Butch: PASS, limitadas a esta extracción. Aceptación humana pendiente; ningún commit autorizado.
 
@@ -119,3 +121,13 @@
 Butch reprodujo la comparación SHA-256 de los 620 archivos preexistentes (solo README difiere), los doce pares del manifiesto (cero discrepancias), la igualdad exacta de las siete secciones de personalidad y la coincidencia del README recuperable con el baseline. Revisó la entrada universal, las reglas generalizadas y el mapa de completitud. Confirmó veinte archivos nuevos, todos en contracts/ o docs/, y ningún project.godot. Resultado: PASS documental; listo para revisión humana, sin autorizar commit ni eliminar la copia temporal RPG.
 
 La auditoría usa un agente separado con contexto compartido; no garantiza aislamiento técnico. Cargo, Godot, runtime, GUI e integración: NOT_RUN. Plugin, enforcement y distribución: NOT_IMPLEMENTED / DEFERRED. La licencia de distribución sigue pendiente antes de cualquier publicación.
+
+## Actualización operativa posterior — 2026-10-19
+
+Durante Documentation & Agent Reference Reconciliation I se verificó que `C:/MetalLabs-Harness` es ahora una raíz Git, en `main` sin commits, y que `RPG_Archaeology_IF/` ya no está presente. La inicialización y eliminación preceden a esta reconciliación; no se atribuyen a la extracción ni se ejecutaron de nuevo. No se inspeccionó el proyecto original en `G:` ni LoF.
+
+Los doce contratos actuales conservan los hashes de destino del manifiesto histórico. Ese cotejo acredita que no han cambiado desde la extracción; no vuelve a verificar el origen eliminado ni sus 620 archivos. Las rutas de origen del manifiesto y del diff son procedencia histórica, no referencias que deban resolver actualmente.
+
+La recuperación descrita arriba corresponde al momento de la extracción y ya no es un procedimiento operativo aprobado: el origen temporal no está disponible y el README ha recibido cambios posteriores. No ejecutar esa recuperación sobre el estado actual sin un corte y comprobación propios.
+
+`config/roles.toml` conserva una ruta histórica al origen ausente. La prueba Rust permanece inactiva y fuera de la arquitectura; no se corrige su configuración en un corte documental. EditorPlugin, router GDScript, aplicación independiente, skills/templates propios, distribución y mecanismos técnicos de seguridad siguen sin implementar. Los PASS anteriores pertenecen únicamente a la extracción. La auditoría y el estado de esta reconciliación se registran por separado en [Documentation Reconciliation I](documentation-reconciliation-I.md); la revisión humana sigue pendiente.
```

```diff
--- /dev/null
+++ AGENTS.md (después)
@@ -0,0 +1,9 @@
+# AGENTS.md — Desarrollo de MetalLabs-Harness
+
+Esta entrada orienta el trabajo en este repositorio. [contracts/AGENTS.md](contracts/AGENTS.md) es la entrada universal de la biblioteca distribuible; no contiene el estado operativo de este proyecto.
+
+Antes de editar, consulta [README.md](README.md), la tarea humana vigente y las reglas enlazadas en la entrada universal. Carga únicamente el contrato del rol asignado cuando la tarea lo requiera; la existencia de siete contratos no activa siete agentes ni autoriza delegaciones.
+
+La arquitectura elegida es un EditorPlugin de Godot 4 en GDScript tipado; su implementación aún está pendiente. La biblioteca documental es el resultado disponible. Rust y su configuración son evidencia histórica inactiva, no infraestructura a reutilizar automáticamente. No crees plugin, router, skills, templates ni mecanismos de seguridad salvo autorización del corte correspondiente.
+
+Para el estado comprobado después de la extracción consulta [docs/documentation-reconciliation-I.md](docs/documentation-reconciliation-I.md). [docs/agent-contract-migration.md](docs/agent-contract-migration.md) y `docs/migration-evidence/` documentan la extracción histórica; sus rutas de origen no implican disponibilidad actual. Preserva esas evidencias y las ediciones existentes. Inspecciona Git y los archivos reales antes de escribir; commits y publicación requieren autorización humana expresa.
```

## Estado Git final, límites y parada

Salida observada antes de escribir este informe (el informe queda bajo ?? docs/):

```text
?? .gitignore
?? AGENTS.md
?? Cargo.toml
?? MetalLabs-Harness-Foundation-I.zip
?? README.md
?? config/
?? contracts/
?? docs/
?? src/

```

Todos los elementos anteriores ya estaban sin seguimiento al iniciar salvo AGENTS.md raíz y este informe nuevos. No se hizo stage, commit, reset ni configuración Git. No se borraron/movieron archivos. Scripts de verificación efímeros, sin introducir código, tests, plugins, skills o templates en el repositorio.

Comprobaciones propias de Ripley: doce hashes coincidentes, enlaces resueltos, roster/carpetas, búsquedas de identificadores y dependencias, inspección de estado y funcionalidades. Cargo, Godot, runtime, GUI y tests operativos: NOT_RUN, fuera del corte documental. Licencia/distribución continúan pendientes para su propio corte.

Condición de parada: entregar para auditoría separada y validación del responsable; no iniciar plugin ni nuevos cortes. Resultado esperado tras revisión: **DOCUMENTATION RECONCILED / HUMAN REVIEW PENDING**.

## Auditoría separada y validación final

Deckard: **PASS documental acotado**, sin hallazgos materiales pendientes. Reprodujo el cotejo de los doce contratos contra los hashes de destino del manifiesto, la resolución de los 31 enlaces operativos, la correspondencia de IDs/carpetas y el estado Git (main sin commits ni entradas de índice). Confirmó la ausencia de la copia temporal RPG y de archivos .gd, project.godot y plugin.cfg. Revisó las correcciones frente a problemas reales, los diffs documentados, la justificación del AGENTS.md raíz y la separación entre historia y estado actual. No modificó archivos.

**NOTE — límite de evidencia:** el baseline temporal perdido impide certificar de forma independiente la preservación byte a byte de las siete evidencias históricas o de todo el workspace preexistente durante este corte. Tampoco se ha vuelto a inspeccionar el origen eliminado. El cotejo de los doce contratos sí se reprodujo. La auditoría separada comparte contexto y no garantiza aislamiento técnico.

El responsable reprodujo doce hashes sin discrepancias, Git inicializado en la raíz y rama main sin entradas de índice, ausencia local de RPG y ausencia de archivos de implementación Godot; revisó README, entrada raíz e informe. Se registra el resultado de Deckard sin modificar contratos ni evidencias históricas. Sin commits. Condición de parada alcanzada: **DOCUMENTATION RECONCILED / HUMAN REVIEW PENDING**. No se inicia otro corte.
