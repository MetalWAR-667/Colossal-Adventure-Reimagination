# Protocolo de experimento reproducible

## Pregunta

¿En qué medida un agente puede construir una aventura de parser jugable, coherente y atractiva a partir de un expediente arqueológico, con intervención humana limitada y medible?

## Congelar antes de ejecutar

- **CANDIDATE_ID / versión / corpus hash:**
- **Scope (salas/puzles/verbos/objetos):**
- **Test fixtures y criterios de aceptación:**
- **Guía visual/sonora y assets proporcionados:**
- **Motor y plataforma objetivo:**
- **Modelo / versión / esfuerzo de razonamiento:**
- **Herramientas / permisos / límites:**
- **Presupuesto máximo (tiempo/coste/tokens):**
- **Fecha de ejecución:**

## Encargo al agente

1. Construir un juego ejecutable y completo dentro del slice congelado.
2. Preservar parser como entrada principal y mantener el estado del mundo determinista.
3. Seguir el mapa, las dependencias y el contrato de verbos.
4. Aplicar la biblia artística y sonora, con assets originales o autorizados.
5. Añadir pruebas del camino feliz, variantes razonables y bloqueos.
6. Documentar decisiones autónomas, supuestos y divergencias.
7. No añadir subsistemas no autorizados; detenerse ante un bloqueo jurídico o de alcance.

## Fases de la ejecución

`INPUT FROZEN → IMPLEMENTATION → SELF-TEST → BUILD → PLAYTEST HUMANO → REPORT`

## Registro de intervenciones

| Fecha/hora | Minuto de ejecución | Tipo | Solicitud humana | Causa | ¿Resuelto? | Coste / tiempo |
|---|---:|---|---|---|---|---|
| | | TECH / DESIGN / MISREAD / LEGAL / SCOPE | | | | |

## Para repetición futura

- Conservar el mismo corpus, alcance y rúbrica.
- Ejecutar un `baseline` con especificaciones mínimas **si hay presupuesto**, y uno con expediente arqueológico.
- Anotar cambios de modelo, herramientas y hardware; no atribuir toda mejora al modelo si cambian los demás factores.
- No cambiar reglas a mitad para mejorar artificialmente el resultado.
- Guardar ejecutable, hash, commit, logs, costes, informe y grabación de los primeros minutos de juego.
