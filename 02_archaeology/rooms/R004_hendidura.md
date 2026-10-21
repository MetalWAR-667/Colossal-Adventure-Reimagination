# Sala R004 — Hendidura del arroyo (LOC_SLIT)

## Identidad y evidencias
- Juego / versión: Colossal Cave Adventure — Open Adventure (rama 2.5 / 430 pts)
- Fuentes (SOURCE_ID): OA-YAML (ver R001)
- Confianza: VERIFIED

## Diseño original
- Descripción factual propia: todo el arroyo se cuela por una grieta de unos 5 cm en la roca; aguas abajo, el cauce queda seco.
- Qué aprende el jugador aquí: el agua se mete bajo tierra → hay algo debajo. Y el cauce seco sigue: hay que continuar.
- Salidas y condiciones:
  - N / UPSTREAM → R003
  - S / DOWNSTREAM / BED / DEPRESSION → R005 Reja
  - BUILDING → R001
  - E / FOREST → LOC_FOREST6; O → LOC_FOREST10 (fuera del slice)
  - SLIT / STREAM / DOWN / IN / ENTER → mensaje DONT_FIT (no cabes)
- Objetos interactivos: ninguno.
- Función en progresión y ritmo: primer "misterio": insinúa la cueva sin mostrarla.
- Pistas visuales / textuales: la hendidura (hay un mundo debajo) + el cauce seco (sigue por aquí).

## Presentación original
- Composición: UNKNOWN (OA). AD: pendiente.
- Sonido: agua cayendo en un hueco.

## Lectura crítica
- Qué funciona: es una pista ambiental de manual.
- Fricción: el jugador intentará "entrar" en la hendidura; la respuesta original es seca y poco útil.
- Qué conservar: la hendidura, el cauce seco hacia el S, la negativa a entrar.
- Qué NO es esencial: las salidas al bosque.

## Reinterpretación (propuesta, NO canon)
- Texto renovado:
  - **Original:** *"At your feet all the water of the stream splashes into a 2-inch slit in the rock. Downstream the streambed is bare rock."* / corto: *"You're at slit in streambed."*
  - **Función:** [el agua desaparece bajo tierra: hay algo debajo] [cauce seco que continúa al S] [no se puede entrar por la grieta]
  - **Nuestra versión — larga:** *A tus pies, el arroyo entero se cuela por una grieta en la roca de apenas un par de dedos de ancho y desaparece con un gorgoteo satisfecho. Más abajo, el cauce sigue, seco y pedregoso, como un camino que alguien se olvidó de terminar.*
  - **Nuestra versión — corta:** *Estás junto a la grieta donde desaparece el arroyo. El cauce seco sigue hacia el sur.*
  - **Respuestas especiales del parser:** `entrar en la grieta` → *Ni metiendo tripa. Por ahí solo pasa el agua, y porque no tiene huesos.*
- Arte nuevo: brief pendiente — primer plano de roca con la grieta y el agua cayendo; al fondo, el cauce seco que se aleja. Es la primera imagen que debe sugerir "debajo hay algo".
- Música / ambiente: gorgoteo; primera nota de misterio, muy sutil.
- Invariantes jugables: S → R005; no se puede entrar por la grieta.
- Tests: `entrar` → mensaje de que no cabes, sin cambiar de sala; `sur` → R005.
