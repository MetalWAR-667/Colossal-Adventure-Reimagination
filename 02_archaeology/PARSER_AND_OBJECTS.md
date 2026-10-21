# Contrato de parser y objetos

## Entrada y gramática de la versión histórica

- Número de palabras / gramática:
- Verbos transitivos / intransitivos:
- Preposiciones y artículos:
- Pronombres, elipsis, conversación:
- Sinónimos y abreviaturas:
- Desambiguación:
- Errores y prioridad de respuesta:
- Comandos meta (LOOK, INVENTORY, SAVE, HELP, etc.):

## Comportamiento a preservar / mejorar

- **Invariante:** interpretar comandos escritos, no botones que sustituyan todas las acciones.
- **Mejora candidata:** aceptar variantes razonables sin inventar consecuencias.
- **Límite:** un modelo de lenguaje generativo no debe alterar la lógica canónica ni inventar objetos, rutas o soluciones. Si se ensaya comprensión flexible, convertir la intención a una acción validada por un motor determinista.

## Diccionario

| VERB_ID | Forma canónica | Alias | Argumentos | Precondición | Efecto | Respuesta | Evidencia |
|---|---|---|---|---|---|---|---|
| V001 | | | | | | | |

## Catálogo de objetos

| OBJECT_ID | Nombre | Alias | Sala inicial | Portátil | Estados | Usos | Puzzle | Evidencia |
|---|---|---|---|---|---|---|---|---|
| O001 | | | | | | | | |

## Pruebas de corpus

| TEST_ID | Sala + estado | Entrada del jugador | Intención esperada | Cambio de estado | Mensaje / clase de mensaje |
|---|---|---|---|---|---|
| T001 | | | | | |

Añadir pruebas para comandos incompletos, erratas, sinónimos, referentes ambiguos y órdenes físicamente imposibles.
