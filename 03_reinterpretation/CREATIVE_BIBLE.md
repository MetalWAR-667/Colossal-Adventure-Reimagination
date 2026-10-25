# Biblia de reinterpretación — propuesta

- **Título provisional:**
- **Premisa nueva (3–5 líneas):**
- **Qué preserva del original:**
- **Qué modifica y por qué:**
- **Qué NO debe incluir:**
- **Público / duración objetivo:**

## Arte
- Referencias de técnicas y sensaciones (no reproducción directa de capturas): **[DECIDIDO 2026-10-15]** ilustración por sala que recrea el dibujado vectorial de las aventuras de 8 bits: se trazan líneas y después se rellenan zonas con flood fill, visible en tiempo real para el jugador.
  - Nota de arquitectura: la ilustración se guarda como **datos** (lista ordenada de comandos: `LINE`, `FILL`, color…) y el renderer los reproduce. El renderer consume datos, no dicta nada.
- **[ALCANCE HUMANO APROBADO — CAR-ART-001, 2026-10-25]** CAR V1 explora una aventura vectorial contemporánea con contornos progresivos y rellenos posteriores; no está obligada a reproducir las limitaciones técnicas de los primeros microordenadores. Pixel art moderno, pintura digital y una reinterpretación visual completa quedan reservados a una posible V2.
  - **[DECISIÓN HUMANA — CAR-ART-001, 2026-10-25]** Dirección seleccionada: **C — Línea solar**, por su luminosidad, legibilidad, curvas suaves y continuidad vectorial. Los estudios son conceptuales, no assets definitivos.
  - **Objetivos para prototipo CAR-ART-002:** duración completa de 3,5 s a 1×; trazado interpolado por longitud; relleno progresivo por región con propagación espacial perceptible; omisión con resultado final idéntico; parser disponible durante la secuencia y sin espera obligatoria en visitas repetidas. Estos objetivos no constituyen un contrato implementado ni evidencia de viabilidad en Godot.
  - [CAR-ART-001: decisión, estudios y diagnóstico técnico](../project_state/changes/car_art_001_vector_direction_gate/CHANGE.md) conserva propuestas alternativas, evidencia y limitaciones. Pixel art moderno, pintura digital, música y reinterpretación narrativa más elaborada quedan fuera de CAR V1 y reservados como posibilidades futuras para V2.
- Paleta / iluminación / textura:
- Perspectiva / encuadre / aspect ratio:
- Elementos visuales que comunican pistas:
- Consistencia de personajes y escenarios:
- Criterios para aceptar/rechazar un asset:

## Audio
- Temas funcionales (exploración, tensión, revelación, desenlace):
- Instrumentos / síntesis / tempo orientativo:
- Cómo cambiar por estado sin distraer del texto:
- Identidad melódica original, no paráfrasis de melodías protegidas:

## Literatura
- Voz, tono, tiempo verbal y nivel de detalle: **[DECIDIDO 2026-10-15]**
  - Segunda persona, presente, con un narrador descriptivo que tiene **sentido del humor**.
  - Descripciones **cortas pero suficientes** para que la escena se entienda bien (orientativo: 2–4 frases).
  - El humor nunca tapa una pista: la función de la sala va antes que la gracia.
  - Con ilustración, el texto prioriza lo que la imagen no muestra (sonido, olor, sensación, pistas).
- Método de reescritura por texto: `ORIGINAL (Open Adventure) → FUNCIÓN (info imprescindible) → NUESTRA VERSIÓN`.
- Información imprescindible en la descripción de sala:
- Feedback de parser (breve, útil, variado):
- Palabras y recursos estilísticos a evitar:

## UX y parser
- Ubicación y prioridad de la línea de comandos:
- Accesibilidad, historial y autocompletado opcional:
- Cómo distinguir información visual decorativa de pistas reales:
- Qué asistencias activables no sustituyen la resolución:

## Semillas futuras (NO en alcance)
- Movimiento ligero y/o parallax en algunas escenas (agua, antorchas, profundidad). Se evaluará después del slice estático.

## Libertad del agente
- **Conservar exactamente (función):**
- **Puede proponer variantes, con justificación:**
- **No autorizado sin revisión humana:**
