# Sala R005 — La reja (LOC_GRATE)

## Identidad y evidencias
- Juego / versión: Colossal Cave Adventure — Open Adventure (rama 2.5 / 430 pts)
- Fuentes (SOURCE_ID): OA-YAML (ver R001)
- Confianza: VERIFIED

## Diseño original
- Descripción factual propia: depresión de unos 6 m con suelo de tierra; en ella, una reja de acero sólida montada en hormigón; un cauce seco desemboca aquí.
- Qué aprende el jugador aquí: la entrada a la cueva existe y está cerrada; el primer "puzle" es volver con las llaves.
- Salidas y condiciones:
  - N / UPSTREAM / GULLY → R004
  - BUILDING → R001
  - E / FOREST → LOC_FOREST7; S → LOC_FOREST10; O → LOC_FOREST9 (fuera del slice)
  - DOWN / IN / ENTER → LOC_BELOWGRATE **solo si GRATE = GRATE_OPEN**; si no, mensaje GRATE_NOWAY
- Objetos interactivos:
  - GRATE — *"The grate is locked."* / *"The grate is open."* (estados GRATE_CLOSED / GRATE_OPEN; se abre con las KEYS de R002)
- Función en progresión y ritmo: **primer puzle y umbral** entre el mundo exterior y la cueva. Cierre natural del slice exterior.
- Pistas visuales / textuales: la reja cerrada + las llaves vistas en R002.

## Presentación original
- Composición: UNKNOWN (OA). AD: pendiente.
- Sonido: silencio; quizá aire que sube por la reja.

## Lectura crítica
- Qué funciona: el puzle de llave y cerradura más limpio posible; enseña el bucle "ver obstáculo → recordar objeto → volver".
- Fricción: si el jugador no cogió las llaves, toca volver andando (aceptable, el camino es corto).
- Qué conservar: reja cerrada, se abre con las llaves, da paso bajo tierra.
- Qué NO es esencial: las salidas al bosque.

## Reinterpretación (propuesta, NO canon)
- Texto renovado:
  - **Original:** *"You are in a 20-foot depression floored with bare dirt. Set into the dirt is a strong steel grate mounted in concrete. A dry streambed leads into the depression."* / corto: *"You're outside grate."*
  - **Función:** [hoyo en el terreno] [reja de acero en el suelo = entrada] [cerrada/abierta] [el cauce seco acaba aquí: confirma la pista]
  - **Nuestra versión — larga:** *Estás en el fondo de una hondonada de tierra desnuda, a unos seis metros por debajo del bosque. En el suelo hay una reja de acero sólida, encastrada en hormigón, de esas que alguien puso aquí con muchas ganas de que nadie pasara. El cauce seco termina justo aquí, como si también quisiera entrar.*
  - **Nuestra versión — corta:** *Estás en la hondonada, junto a la reja.*
  - **Estados de la reja (nuestra versión):** cerrada: *La reja está cerrada con llave.* / abierta: *La reja está abierta. Por el hueco sube un aire frío que huele a piedra.*
  - **Respuestas especiales del parser:** `bajar` / `entrar` con la reja cerrada → *La reja no opina lo mismo. Está cerrada con llave.* / `abrir reja` sin llaves → *Haría falta una llave. O un milagro, pero de esos no hay.*
- Arte nuevo: brief pendiente — vista cenital/picada de la reja; dos variantes de capa: cerrada y abierta (con oscuridad debajo).
- Música / ambiente: exterior apagándose; con la reja abierta, eco grave desde abajo. Primer cambio de ambiente por estado.
- Invariantes jugables: no se baja sin abrir; con llaves, `abrir reja` → GRATE_OPEN; abierta, `bajar` → LOC_BELOWGRATE.
- Tests: sin llaves, `bajar` → mensaje y sigue en R005; con llaves, `abrir reja` + `bajar` → bajo la reja.
