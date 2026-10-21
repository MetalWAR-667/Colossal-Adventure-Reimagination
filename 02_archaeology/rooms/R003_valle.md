# Sala R003 — Valle del arroyo (LOC_VALLEY)

## Identidad y evidencias
- Juego / versión: Colossal Cave Adventure — Open Adventure (rama 2.5 / 430 pts)
- Fuentes (SOURCE_ID): OA-YAML (ver R001)
- Confianza: VERIFIED

## Diseño original
- Descripción factual propia: valle en el bosque, junto a un arroyo que baja por un lecho rocoso.
- Qué aprende el jugador aquí: seguir el agua es la dirección correcta.
- Salidas y condiciones:
  - N / UPSTREAM / BUILDING → R001
  - S / DOWN / DOWNSTREAM → R004 Hendidura
  - E / FOREST → LOC_FOREST6; O → LOC_FOREST12 (bosque, fuera del slice)
  - DEPRESSION → R005
  - STREAM → mensaje UPSTREAM_DOWNSTREAM (pregunta si río arriba o abajo)
- Objetos interactivos: ninguno.
- NPC / peligros: ninguno.
- Función en progresión y ritmo: transición; refuerza la pista del arroyo.
- Pistas visuales / textuales: el arroyo sigue bajando.

## Presentación original
- Composición: UNKNOWN (OA). AD: pendiente.
- Sonido: agua sobre roca.

## Lectura crítica
- Qué funciona: sala de paso corta; no distrae.
- Fricción: ninguna relevante; el bosque lateral puede despistar.
- Qué conservar: la continuidad del arroyo hacia el S.
- Qué NO es esencial: las salidas al bosque.

## Reinterpretación (propuesta, NO canon)
- Texto renovado:
  - **Original:** *"You are in a valley in the forest beside a stream tumbling along a rocky bed."* / corto: *"You're in valley."*
  - **Función:** [transición] [arroyo: río arriba = edificio (N), río abajo = S] [bosque a los lados]
  - **Nuestra versión — larga:** *Estás en un pequeño valle del bosque. El arroyo baja dando tumbos por un lecho de piedras, como si llegara tarde a algún sitio. Río arriba queda el edificio; río abajo, quién sabe.*
  - **Nuestra versión — corta:** *Estás en el valle. El arroyo sigue con sus prisas, río abajo.*
  - **Respuestas especiales del parser:** `seguir arroyo` (sin dirección) → *¿Río arriba o río abajo? El arroyo lo tiene claro; tú, por lo visto, no.*
- Arte nuevo: brief pendiente — arroyo en diagonal hacia el primer plano/abajo, árboles a los lados.
- Música / ambiente: agua más viva que en R001.
- Invariantes jugables: N → R001, S → R004.
- Tests: `río abajo` → R004; `río arriba` → R001.
