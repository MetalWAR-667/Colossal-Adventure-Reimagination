# Agent Contract Migration — extracción documental

> Registro histórico de la extracción documental. Las afirmaciones siguientes sobre ausencia de Git, presencia de la copia temporal, integridad del origen y recuperación describen el momento de aquella extracción; no son instrucciones operativas actuales. Se conserva el cuerpo histórico y su evidencia sin reescribirlos. Véase la actualización al final y la [reconciliación documental](documentation-reconciliation-I.md).

Task: HARNESS-CONTRACT-MIGRATION-001. Fecha: 2026-10-19. Implementación: Ripley, autorizada expresamente en esta sesión. Estado: REVIEW; auditoría documental de Deckard y validación de Butch: PASS, limitadas a esta extracción. Aceptación humana pendiente; ningún commit autorizado.

## Procedencia y alcance

Origen: C:/MetalLabs-Harness/RPG_Archaeology_IF/.agents/, bytes actuales del workspace, incluidos contratos no seguidos por Git. Destino: C:/MetalLabs-Harness/contracts/. No se asumió que HEAD contuviera la biblioteca completa. El Harness no tiene raíz Git; el origen tiene modificaciones previas conservadas.

Se escribieron doce contratos, README, este informe y evidencia. No se creó AGENTS.md raíz, plugin, proyecto Godot, integración, consumidor, dependencia ni distribución. No se modificó, borró ni movió el origen; no se accedió a G: ni LoF. La copia temporal RPG, Rust y ZIP permanecen intactos.

## Clasificación

| Clase | Origen relativo a .agents salvo indicación | Destino/tratamiento |
| --- | --- | --- |
| COPY | Siete agents/*/AGENT.md | contracts/agents/; referencias corregidas |
| COPY | Cuatro reglas principales | contracts/rules/ |
| COPY | AGENTS.md | contracts/AGENTS.md universal |
| PROJECT_SPECIFIC | Identidad RPG §1, detalles de dominio §5; ejemplo documentation §3; detalles RPG verification §8 | Permanecen en origen; principios generales conservados abajo |
| DEFERRED | Tres skills/*/SKILL.md y tres templates/*.md | Seis archivos de 0 bytes: excluidos, no disponibles |
| DEFERRED | ruta.txt | Nota conceptual, no contrato de carga |
| KEEP | Seis *.backup-* | Historia conservada, no cargada |
| OBSOLETE | rules/__verification_stage__.md | Duplicado SHA-256 de verification.md, conservado sin distribuir |
| OBSOLETE | Dos *.empty-* | Vacíos, conservados sin distribuir |
| PROJECT_SPECIFIC | Material RPG fuera de .agents | Conservado y excluido |
| DEFERRED | Cargo.toml, src/main.rs, config/roles.toml y tests/ raíz | Prueba Rust histórica intacta, no ejecutada |
| KEEP | MetalLabs-Harness-Foundation-I.zip raíz | Snapshot intacto |

OBSOLETE no autoriza borrar. Distribución junto al plugin: DEFERRED para su propio corte.

## Completitud universal

| Fuente | Conservación en destino |
| --- | --- |
| AGENTS §1 | Identidad universal sustituye RPG; autoridad humana íntegra |
| AGENTS §2 | Prioridad, conflictos, carga explícita, ausente/vacío no concede permiso; skills/templates declarados no disponibles |
| AGENTS §3–4 | Siete roles/outputs, ID singular correcto, enlaces; protocolo seis pasos y defaults íntegros |
| AGENTS §5 apertura | Propósito autorizado; investigación no autoriza rediseño; inspección/transformación/reinterpretación separadas |
| AGENTS §5 bullets 1–2 | Significado, estructura, IDs, citas, procedencia, derechos, no inventar/corregir; fuente/revisión fijada con evidencia |
| AGENTS §5 bullets 3–4 | Separar fuente/derivados; semántica/condiciones y casos no resueltos; retirar enumeraciones de aventuras |
| AGENTS §5 bullets 5–6 | Derechos antes de traducir/parafrasear/republicar; diagramas editables con IDs, condiciones/enlaces; no sobrescribir ediciones. Retirar preferencia específica draw.io |
| AGENTS §5 bullets 7–8 | Esquema, determinismo, conteos, IDs, relaciones, integridad, reapertura, constructos no tratados; README/specs como contexto sin autorizar sugerencias |
| AGENTS §6–7 | Drive opcional: edición segura, sincronización/Git; reporting y paradas íntegros |
| documentation §3 | Fuente/revisión gobiernan hechos; diagramas y transformaciones derivados no sustituyen autoridad |
| verification §8 | Revisión, IDs, integridad, semántica/transiciones; sintaxis no equivale a abrir/renderizar; prosa de modelo no valida estado. Condicional, no mandato de parser |
| Resto de reglas | Conservado salvo rutas, IDs y ejemplo de task ID registrados |
| Siete agentes | Personalidades exactas; misión/responsabilidades/autoridad/procedimientos preservados salvo spelling Gandulf; colaboración corregida |

Ejemplos Python/pytest siguen hipotéticos, no dependencias. Salvaguardas históricas, CURRENT_STATE y Drive son condicionales; no exigen que un consumidor adopte herramientas.

## Origen, destino, hashes y cambios exactos

[Manifiesto](migration-evidence/contract-manifest.json) y [diff](migration-evidence/contract-transformations.diff) registran cada copia. Normalización común: UTF-8 sin BOM y LF.

| Origen relativo a .agents | Destino relativo a contracts | SHA-256 origen | SHA-256 destino |
| --- | --- | --- | --- |
| `agents/butch_architect/AGENT.md` | `agents/butch_architect/AGENT.md` | `c48e1b9f22bbee5a0dc88b7e5f13b680cd3d1175eb6eefbc39ecd5117e899b7a` | `7165da5bc89945a258b660a8ca95e56044eb6664b2e3895ef4eae934df9cff67` |
| `agents/deckard_auditor/AGENT.md` | `agents/deckard_auditor/AGENT.md` | `7a029d21b74476dfdb2a3ac4a6bdce8c9c49489b689d86726852f2c13e41c6ad` | `7bbaa221b2fe6f0cec029851c5c89457dac7254e0c369bb8d107ee6dfa1ec6f3` |
| `agents/doc_brown_the_researcher/AGENT.md` | `agents/doc_brown_the_researcher/AGENT.md` | `e1b7f6507dfa039311317836f0858aa5861903de0f51070be5b4676b0c9b2987` | `7a008832416c8200b2cee5e5b5606fc1fa1b9bf60e2b7a313507dcb38c3d811b` |
| `agents/gandulf_chronicler/AGENT.md` | `agents/gandulf_chronicler/AGENT.md` | `8dda59fa014ce87aee8a568a047db4f5dbdf69ea0833714f606f94d265d35578` | `86aae158ddc3d3062ca0ca0a8b94a4c24819fe2408950d07cdddf8ba199f03e7` |
| `agents/jack_burton_the_artist/AGENT.md` | `agents/jack_burton_the_artist/AGENT.md` | `ef99b272e7049385375c19436212e33fba57a8a61622de5ba87e52b1118a81bc` | `ef99b272e7049385375c19436212e33fba57a8a61622de5ba87e52b1118a81bc` |
| `agents/mrwolf_tech_troubleshooter/AGENT.md` | `agents/mrwolf_tech_troubleshooter/AGENT.md` | `0baadfe243e29cdce9a0019b35c8b8c288f8b7a2567dfe900cd153b0524baa11` | `cd71924156c109f14a8e4c379ae3cc0b6b4a3a188b87a46954c985938b8a81cf` |
| `agents/ripley_engineer/AGENT.md` | `agents/ripley_engineer/AGENT.md` | `f4753613136521525b5284fc24cb885c8757d2f3b8bfa3914aba627602d7bdc4` | `47d3faacfd2ef50e7b7d646263bcaa550dcee8fa4ba93d0e6d1e8c098a39591c` |
| `rules/scope-and-authority.md` | `rules/scope-and-authority.md` | `a5faea2b229aaf6feb3d2caf8f5b277fe144afddc138cc8995907e502b837a5e` | `7c11265d09b65de5e7d490882938a37d6748c538348dff7ef80ad5978fefc6db` |
| `rules/multi-agent-workflow.md` | `rules/multi-agent-workflow.md` | `bf636e504316026258e63235e1875ae42bb60f06fc3800cfa0f2b14e1ed33f9d` | `d5a64b781b86295985d3ea2072819d4a6105c39193baddfb26a8689be984ab16` |
| `rules/verification.md` | `rules/verification.md` | `15ba80bf6bf8b401d63ac2a1bc449595d91619d2a6515af3c94e65a95cc83f60` | `f05aaa048cc64e7364cd91f58f86f5e56aa97f54a8fb5f48b18c0510106f4213` |
| `rules/documentation.md` | `rules/documentation.md` | `d301a3f4822a6d32c08ee342f54da9b309f99cf7ed1a7bfe53f3fb9e40e51963` | `7cc7b68476d08469f3511f5c0937cf2d700bee1039f0a3a15d2e453b32356c1e` |
| `AGENTS.md` | `AGENTS.md` | `e2199c737d5c1a117b2fadf5f730ea9a6bf2f04706b73cf2149be8d167b0caeb` | `586470f3542462530b342a1016255898dbde357137d524eac6884a86b397c2b5` |

- `contracts/agents/butch_architect/AGENT.md`: Gandalf -> Gandulf (cross-role references only); Stale Jack Burton / Troubleshooter -> Mr. Wolf / Troubleshooter; Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/agents/deckard_auditor/AGENT.md`: Gandalf -> Gandulf (cross-role references only); Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/agents/doc_brown_the_researcher/AGENT.md`: Gandalf -> Gandulf (cross-role references only); Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/agents/gandulf_chronicler/AGENT.md`: Replace pending Jack reference with current Creative Director; Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/agents/jack_burton_the_artist/AGENT.md`: Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/agents/mrwolf_tech_troubleshooter/AGENT.md`: Gandalf -> Gandulf (cross-role references only); Replace pending Jack reference with current Creative Director; preserve troubleshooting boundary; Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/agents/ripley_engineer/AGENT.md`: Gandalf -> Gandulf (cross-role references only); Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/rules/scope-and-authority.md`: Resolve role path relative to rules/; Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/rules/multi-agent-workflow.md`: Resolve entrypoint reference relative to rules/: ../AGENTS.md; Neutralize illustrative task ID IF-CUT-001 -> HARNESS-CUT-001; Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/rules/verification.md`: Resolve entrypoint reference relative to rules/: ../AGENTS.md; Neutralize illustrative task ID IF-CUT-001 -> HARNESS-CUT-001; Generalize section 8: remove RPG/source-format/parser-project specifics; retain source revision, IDs, deterministic integrity, render honesty and semantic/state verification as conditional guidance; Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/rules/documentation.md`: Resolve entrypoint reference relative to rules/: ../AGENTS.md; Generalize RPG historical-source example while preserving source authority versus derived interpretation; Normalize mr_wolf and jack_burton examples to canonical existing folder IDs; Normalize UTF-8 without BOM and LF line endings; all other text retained.
- `contracts/AGENTS.md`: Replace source project identity with universal library identity; Keep sections 1 authority, 2 priority/discovery safety, 3 roster, 4 protocol, 6 optional Drive safeguards and 7 reporting/stopping; Generalize every section 5 safeguard; remove only source-specific names, examples, domain enumerations and format preference; Fix Mr. Wolf canonical ID; link four rules and seven roles; Mark empty source skills/templates unavailable; no dangling directory reference; Normalize UTF-8 without BOM and LF line endings.

README ahora describe Godot 4 / EditorPlugin modular / GDScript tipado; plugin no implementado y distribución pendiente. [README.before.md](migration-evidence/README.before.md) conserva sus bytes originales. No se cambian versiones de contratos porque no se redefine su semántica.

## Verificación propia de Ripley

- PASS documental: 12 documentos no vacíos, siete agentes y cuatro reglas más entrada.
- PASS documental: siete secciones Personality idénticas; rangos desde misión hasta sección 6 preservados salvo referencia Gandalf → Gandulf. Doc Brown conserva encabezados planos.
- PASS documental: enlaces Markdown relativos de contratos existentes; búsqueda negativa de RPG/rutas, adventure.yaml, Gandalf, ID plural, IF-CUT-001 y Jack pendiente/Troubleshooter.
- PASS integridad: 620 archivos preexistentes comparados por SHA-256 antes/después; únicamente README difiere. Todo el origen, Rust y ZIP intactos.
- PASS integridad: estado Git fuente idéntico antes/después. Comando: git -c safe.directory=C:/MetalLabs-Harness/RPG_Archaeology_IF -C C:/MetalLabs-Harness/RPG_Archaeology_IF status --porcelain=v1 --untracked-files=all. Sin configuración persistente ni cambios de índice.
- Método: Python estándar pathlib/hashlib/json/difflib y assertions; Get-Content y rg. Sin instalaciones.
- NOT_RUN: Cargo, Godot, GUI, runtime y tests operativos del harness. No se implementó código ejecutable.
- Estos checks son propios de Ripley; la auditoría posterior se registra por separado abajo.

[Baseline](migration-evidence/workspace-before.json), [post de preexistentes](migration-evidence/workspace-existing-after.json), [status antes](migration-evidence/source-git-status-before.txt) y [después](migration-evidence/source-git-status-after.txt). El post cubre los mismos 620 archivos preexistentes, no pretende incluirse a sí mismo ni congelar nuevos informes.

El comprobador inicial falló por asumir encabezados Markdown uniformes (Doc Brown usa texto plano), y después por encoding cp1252 implícito en una lectura. Se repitió con delimitadores adecuados y UTF-8 explícito; no se emitió PASS desde intentos fallidos ni se cambiaron contratos. Una búsqueda con glob literal Windows también falló y se repitió sobre directorio. Fallos de comprobación conservados en la sesión.

## Dependencias, riesgos y recuperación

Biblioteca sin dependencia RPG ni Rust. Rutas/aliases de config Rust permanecen históricos; no son registro canónico. Hasta existir adaptador el operador carga entrada, reglas, rol y contexto explícitamente; Markdown no garantiza descubrimiento ni enforcement.

Se fijan bytes de workspace, no un commit publicado. Licencia para distribuir contratos requiere decisión antes de publicación; MIT en Cargo no demuestra licencia de esta biblioteca. No se publica nada.

Recuperación propuesta, no ejecutada: verificar que nuevos archivos no recibieron ediciones posteriores; restaurar README desde bytes guardados y retirar exclusivamente archivos creados en este corte con autorización. El origen no necesita restaurarse. La carpeta temporal RPG permanece incluso tras auditoría favorable: no se borra en este corte.

## Aceptación y parada

Deckard comprobó fuentes, diff, completitud, referencias, integridad, alcance y ausencia de dependencias RPG. Butch validó el resultado posterior. Hallazgos futuros requieren corrección acotada y recheck. Parar ante nueva semántica de roles, conflicto de autoridad, cambios externos inesperados, publicación sin derechos o ampliación de alcance.

El siguiente límite es revisión/aceptación humana. No commit, borrado de copia, plugin ni distribución autorizados por esta extracción.

## Auditoría de Deckard y validación de Butch

Deckard emitió PASS documental en una pasada separada: siete agentes completos y equivalentes al origen tras las sustituciones autorizadas; cuatro reglas y entrada universal; salvaguardas universales conservadas; doce pares de hashes correctos; diff regenerado y coincidente; quince enlaces de contratos y enlaces de README/informe resueltos; 620 archivos preexistentes presentes, solo README modificado; estado Git del origen igual al baseline. Sin hallazgos materiales pendientes.

Hallazgo menor corregido y revisado por Deckard: el manifiesto y este informe atribuían a scope-and-authority.md una corrección de referencia al entrypoint que no existía. Se retiró esa atribución; el cambio real es la ruta relativa del rol. No cambió ningún contrato durante la corrección.

Butch reprodujo la comparación SHA-256 de los 620 archivos preexistentes (solo README difiere), los doce pares del manifiesto (cero discrepancias), la igualdad exacta de las siete secciones de personalidad y la coincidencia del README recuperable con el baseline. Revisó la entrada universal, las reglas generalizadas y el mapa de completitud. Confirmó veinte archivos nuevos, todos en contracts/ o docs/, y ningún project.godot. Resultado: PASS documental; listo para revisión humana, sin autorizar commit ni eliminar la copia temporal RPG.

La auditoría usa un agente separado con contexto compartido; no garantiza aislamiento técnico. Cargo, Godot, runtime, GUI e integración: NOT_RUN. Plugin, enforcement y distribución: NOT_IMPLEMENTED / DEFERRED. La licencia de distribución sigue pendiente antes de cualquier publicación.

## Actualización operativa posterior — 2026-10-19

Durante Documentation & Agent Reference Reconciliation I se verificó que `C:/MetalLabs-Harness` es ahora una raíz Git, en `main` sin commits, y que `RPG_Archaeology_IF/` ya no está presente. La inicialización y eliminación preceden a esta reconciliación; no se atribuyen a la extracción ni se ejecutaron de nuevo. No se inspeccionó el proyecto original en `G:` ni LoF.

Los doce contratos actuales conservan los hashes de destino del manifiesto histórico. Ese cotejo acredita que no han cambiado desde la extracción; no vuelve a verificar el origen eliminado ni sus 620 archivos. Las rutas de origen del manifiesto y del diff son procedencia histórica, no referencias que deban resolver actualmente.

La recuperación descrita arriba corresponde al momento de la extracción y ya no es un procedimiento operativo aprobado: el origen temporal no está disponible y el README ha recibido cambios posteriores. No ejecutar esa recuperación sobre el estado actual sin un corte y comprobación propios.

`config/roles.toml` conserva una ruta histórica al origen ausente. La prueba Rust permanece inactiva y fuera de la arquitectura; no se corrige su configuración en un corte documental. EditorPlugin, router GDScript, aplicación independiente, skills/templates propios, distribución y mecanismos técnicos de seguridad siguen sin implementar. Los PASS anteriores pertenecen únicamente a la extracción. La auditoría y el estado de esta reconciliación se registran por separado en [Documentation Reconciliation I](documentation-reconciliation-I.md); la revisión humana sigue pendiente.
