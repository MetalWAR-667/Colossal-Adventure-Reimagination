# Matriz de selección

Puntuación exploratoria, **sin asignar notas hasta verificar fuentes**. Cada variable vale 0–5; la puntuación sirve para comparar candidaturas, no para confundir preferencias con certezas.

| Criterio | Peso | Qué verificar |
|---|---:|---|
| Material reconstruible | 25 % | Juego, walkthrough, mapa, texto, código o transcript |
| Viabilidad legal | 20 % | Derechos claros para la adaptación prevista, no solo acceso |
| Buen diseño para un slice | 15 % | 8–12 salas conectadas y arco jugable completo |
| Parser interesante | 15 % | Verbos, objetos, sinónimos, estados, conversación |
| Potencial audiovisual | 10 % | Escenas con identidad y función visual clara |
| Puzles entendibles | 10 % | Soluciones analizables, condiciones reproducibles |
| Singularidad | 5 % | Qué aporta al benchmark frente a otros juegos |

**Cálculo:** suma de (nota / 5 × peso). Si `LEGAL_GATE = BLOCKED`, no se aprueba la distribución de una adaptación aunque la nota sea alta. Si hay incertidumbre, marcar `PENDING`, no suponer permiso.

| Juego | Tipo | Documentación verificada | Derechos de adaptación | Idoneidad provisional |
|---|---|---|---|---|
| Colossal Cave Adventure (350 puntos) | Raíz histórica | Código y mapas/versiones disponibles | Situación histórica discutida; comprobar versión | **Alta para arqueología** |
| Open Adventure (430 puntos / rama 2.5) | Implementación autorizada | Código, historia, notas y documentación | Licencia del repositorio; verificar alcance de materiales | **Alta para trabajo técnico** |
| La Aventura Original (Aventuras AD, 1989) | Adaptación española ilustrada | Ficha, versiones ejecutables; estudiar recursos | **PENDING**: titularidad y permiso | **Alta como referencia, condicionada** |
| Bronze (Emily Short) | IF moderna | Fuente Inform 7 disponible | Verificar licencia concreta y obra base | Buena para estudiar UX y parser |
| Counterfeit Monkey (Emily Short) | IF moderna amplia | Código publicado y licencia CC BY-SA 4.0 | CC BY-SA, revisar assets excluidos | Referencia de parser; demasiado grande |

## Preguntas que pueden descartar un candidato

- ¿Podemos legalmente **distribuir** la reinterpretación pretendida?
- ¿Existe un segmento jugable que tenga principio, desarrollo y cierre?
- ¿Podemos reconstruir y verificar el grafo de estados sin adivinar?
- ¿Hay suficientes materiales para estudiar la intención sin copiar su expresión?
- ¿La complejidad del parser es asumible para un experimento pequeño?

## Pendiente de investigación

- Juegos de la escena española CAAD con permiso explícito de sus autores.
- Microaventuras con fuente y licencia claras, especialmente Inform 7.
- Juegos ilustrados con mapas y transcripciones de partidas para comparar intención visual.
