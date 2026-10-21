# Sala R002 — Dentro del edificio (LOC_BUILDING)

## Identidad y evidencias
- Juego / versión: Colossal Cave Adventure — Open Adventure (rama 2.5 / 430 pts)
- Fuentes (SOURCE_ID): OA-YAML (ver R001)
- Confianza: VERIFIED

## Diseño original
- Descripción factual propia: interior de una caseta que protege un manantial grande (well house).
- Qué aprende el jugador aquí: este es el almacén de partida; aquí se equipa.
- Salidas y condiciones:
  - O / OUT → R001
  - DOWNSTREAM / STREAM → LOC_SEWER (tuberías demasiado estrechas: callejón)
  - XYZZY → LOC_FOOF1 / PLUGH → LOC_FOOF3 (palabras mágicas; solo funcionan una vez aprendidas — fuera del slice)
- Objetos interactivos (estado inicial):
  - KEYS — *"There are some keys on the ground here."* (abren la reja de R005)
  - LAMP — *"There is a shiny brass lamp nearby."* (estados: apagada / encendida; imprescindible bajo tierra)
  - FOOD — *"There is food here."*
  - BOTTLE — *"There is a bottle of water here."* (estados: agua / vacía / aceite)
- NPC / peligros: ninguno.
- Estado inicial y cambios: los objetos desaparecen de la descripción al cogerlos. Es también el lugar donde se depositan los tesoros para puntuar.
- Verbos y respuestas especiales: XYZZY, PLUGH (teletransporte); agua del manantial para rellenar la botella.
- Función en progresión y ritmo: equipamiento + base de operaciones (volverás muchas veces).
- Pistas visuales / textuales: las llaves → la reja; la lámpara → oscuridad futura.

## Presentación original
- Composición: UNKNOWN (OA solo texto). AD: pendiente de analizar capturas.
- Sonido / silencio: el manantial.
- Elementos necesarios: los 4 objetos deben ser visibles/legibles.

## Lectura crítica
- Qué funciona: equipar al jugador sin explicarlo; los objetos "se presentan" solos.
- Fricción: la descripción original es pobre (una frase) y no dice que es la base ni dónde dejar tesoros; eso solo se descubre jugando o leyendo el manual.
- Qué conservar: los 4 objetos, el manantial, la función de base/depósito de tesoros.
- Qué NO es esencial: la salida "downstream" a las tuberías (callejón sin juego).

## Reinterpretación (propuesta, NO canon)
- Texto renovado:
  - **Original:** *"You are inside a building, a well house for a large spring."* / corto: *"You're inside building."*
  - **Función:** [interior seguro] [manantial: fuente de agua] [salida al O] [aquí hay equipo] [futuro: depósito de tesoros]
  - **Nuestra versión — larga:** *Estás dentro de la caseta que alguien construyó para proteger un manantial. El agua brota del suelo con un murmullo constante y escapa por unas tuberías demasiado estrechas incluso para tus ambiciones. Para ser un lugar tan pequeño, alguien se ha dejado aquí bastantes cosas.*
  - **Nuestra versión — corta:** *Estás en la caseta del manantial. El agua sigue a lo suyo.*
  - **Objetos (nuestra versión):**
    - Llaves: *Hay un manojo de llaves en el suelo. Alguien va a pasar una mala tarde buscándolas.*
    - Lámpara: *Hay una lámpara de latón reluciente, de las que prometen aventuras.* / encendida: *Una lámpara encendida ilumina la zona.*
    - Comida: *Hay algo de comida. No es un banquete, pero tampoco te lo han pedido.*
    - Botella: *Hay una botella llena de agua.* / vacía: *Hay una botella vacía.* / aceite: *Hay una botella llena de aceite.*
  - **Respuestas especiales del parser:** `bajar por el arroyo` → *Las tuberías son demasiado estrechas. Tú no, pero ellas sí.*
- Arte nuevo: brief pendiente — interior pequeño, manantial en el centro, los 4 objetos con siluetas claras (cada objeto como capa de dibujo que se omite si ya no está).
- Música / ambiente: agua constante, eco ligero de interior.
- Mecánica revisada: en algún momento temprano (por ejemplo, al primer tesoro) el narrador debería insinuar que aquí se dejan los tesoros. **Propuesta para revisar, no decidida.**
- Invariantes jugables: los 4 objetos en el estado inicial; `O` → R001.
- Tests: `coger todo` recoge los 4; `encender lámpara` cambia el estado; `llenar botella` con la botella vacía la llena de agua.
