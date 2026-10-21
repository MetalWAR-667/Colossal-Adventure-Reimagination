# Sala R001 — Fin del camino (LOC_START)

## Identidad y evidencias
- Juego / versión: Colossal Cave Adventure — Open Adventure (rama 2.5 / 430 pts)
- Fuentes (SOURCE_ID): OA-YAML — `adventure.yaml` de Open Adventure (BSD-2-Clause). Copia consultada: espejo github.com/AaronTraas/open-adventure (el repo oficial está en gitlab.com/esr/open-adventure). Pendiente de registrar en SOURCE_REGISTER.
- Referencia de tono: La Aventura Original (AD, 1989) — `material_referencia_no_redistribuible/reconstruccion.txt` (pantalla 1). Solo referencia, no se copia.
- Confianza: VERIFIED (texto y viajes leídos de la fuente)

## Diseño original
- Descripción factual propia: final de carretera ante un pequeño edificio de ladrillo; bosque alrededor; un arroyo sale del edificio y baja por un barranco.
- Qué aprende el jugador aquí: el mundo tiene un "centro" seguro (el edificio) y un hilo conductor (el arroyo).
- Salidas y condiciones:
  - O / ROAD / UP → LOC_HILL (colina, fuera del slice)
  - E / ENTER / BUILDING / IN → R002 Edificio
  - S / DOWN / DOWNSTREAM / GULLY → R003 Valle
  - N / FOREST → LOC_FOREST1 (bosque, fuera del slice)
  - DEPRESSION → R005 Reja (atajo por nombre)
- Objetos interactivos: ninguno.
- NPC / peligros: ninguno.
- Estado inicial y cambios: punto de inicio de la partida.
- Verbos y respuestas especiales: movimiento por nombre de lugar (BUILDING, GULLY, STREAM, DEPRESSION).
- Función en progresión y ritmo: arranque calmado; orientación.
- Pistas visuales / textuales: **el arroyo** (seguirlo lleva a la reja).

## Presentación original
- Composición: UNKNOWN para Open Adventure (solo texto). AD: ilustración en la parte superior; pendiente de analizar con las capturas de `material_referencia_no_redistribuible/secuencia/`.
- Paleta / técnica: — 
- Sonido / silencio: silencio.
- Elementos necesarios para resolver la sala: edificio y arroyo.

## Lectura crítica
- Qué funciona: tres frases y el jugador ya tiene centro, entorno y pista.
- Fricción / ambigüedad: el bosque al norte es un pequeño laberinto sin interés de juego; el atajo "DEPRESSION" es poco intuitivo.
- Qué conservar como función de diseño: edificio explorable + arroyo como pista.
- Qué NO es esencial: la carretera y la colina (decorado).

## Reinterpretación (propuesta, NO canon)
- Texto renovado:
  - **Original:** *"You are standing at the end of a road before a small brick building. Around you is a forest. A small stream flows out of the building and down a gully."* / corto: *"You're in front of building."*
  - **Función:** [inicio] [edificio al E, se puede entrar] [arroyo que sale del edificio y baja: pista hacia el S] [bosque alrededor]
  - **Nuestra versión — larga:** *Aquí se acaba la carretera y, por lo que parece, también la civilización. Frente a ti hay un pequeño edificio de ladrillo, rodeado de un bosque que no tiene pinta de acabarse pronto. Un arroyo sale de la casa y baja por un barranco, con más prisa que tú.*
  - **Nuestra versión — corta:** *Estás frente al edificio de ladrillo. El arroyo sigue bajando, tan decidido como siempre.*
  - **Respuestas especiales del parser:** ninguna por ahora.
- Arte nuevo: brief pendiente — carretera que muere en primer plano, casita al fondo a la derecha (E), arroyo serpenteando hacia abajo (S). El arroyo debe leerse con claridad.
- Música / ambiente: pájaros, viento suave, rumor de agua.
- Mecánica revisada: el parser tolerante acepta "seguir el arroyo", "entrar en la casa", etc.
- Invariantes jugables: mismas salidas y destinos.
- Tests: desde R001, `E` → R002; `S` → R003; `seguir arroyo` → R003.
