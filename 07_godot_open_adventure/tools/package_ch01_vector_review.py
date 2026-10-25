"""Package real Godot frames for human review, never generate runtime artwork.

Pillow is the already available optional evidence-packaging tool, not a game
dependency. GIF palette/timing is approximate; full PNG and metrics are proof.
"""
from pathlib import Path
from html import escape
import argparse
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
CUT = ROOT / "project_state/changes/car_art_004_ch01_vector_illustration_production"
DATA = ROOT / "07_godot_open_adventure/godot/data"
INFO = {
    "LOC_FOREST": ("Bosque sin hitos", "Seis árboles de escala y profundidad distintas, hojarasca y suelo continuo.", "Dibujo compartido por LOC_FOREST1…LOC_FOREST22; no es un nuevo ID de sala. No hay senda, flechas o hitos que resuelvan el bosque."),
    "LOC_BUILDING": ("Casa del manantial", "Planos de ladrillo, suelo seco, gran manantial con pila y canal de salida.", "Pila y sección del canal son interpretación geométrica. KEYS, LAMP, FOOD y BOTTLE no se fijan en el fondo; el terminal describe los objetos presentes."),
    "LOC_ROADEND": ("Final del camino", "Carretera que termina entre árboles y raíces, sin abertura oscura.", "La carretera llega del este según la fuente; la cámara no codifica direcciones del parser."),
    "LOC_HILL": ("Loma del camino", "Lomo del terreno, camino que baja al otro lado, bosque y casita lejana.", "La casa conserva ladrillo/tejado de START a menor escala. No se añade humo, puente ni una conexión nueva."),
    "LOC_VALLEY": ("Vaguada rocosa", "Arroyo curvo, lecho y orillas con rocas de escala variable, bosque.", "Rocas junto al cauce; sin pasos, puentes o rutas nuevas. Agua y carretera tienen colores distintos."),
    "LOC_SLIT": ("Ranura de dos pulgadas", "Agua que converge en una grieta estrecha, roca desnuda aguas abajo y piedras para escala.", "La abertura no es una puerta ni una cueva transitable; su ancho se expresa por un hueco delgado, sin inventar una escala métrica absoluta de cámara."),
    "LOC_CLIFF": ("Acantilado y cornisa opuesta", "Borde rocoso abrupto, bosque que se aclara, abismo, pequeña cornisa al otro lado y urna empotrada.", "No hay descenso dibujado. Se muestra solo la silueta fija de URN, sin afirmar contenido o llama. La cornisa está al oeste según la fuente, no según el eje de pantalla."),
    "LOC_LEDGE": ("Cornisa aislada", "Repisa en primer plano y pared vertical; enfrente, un claro rodeado de bosque.", "No se añade senda de salida. SAPPH es transportable y queda en la descripción real del terminal, no pintado permanentemente. La fuente no ofrece una entrada jugable nueva en este corte."),
    "LOC_SEWER": ("Dos tuberías de un pie", "Par de bocas pequeñas en un muro amplio, cauces de agua y roca.", "No se dibuja un túnel humano ni una salida nueva. DEEP y ausencia de LIT se conservan en datos: no se añade lámpara, fuego o lógica de iluminación."),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("frames",type=Path)
    args = parser.parse_args()
    evidence = CUT / "evidence"
    metrics = json.loads((evidence/"metrics.json").read_text(encoding="utf-8"))
    assert not metrics["failures"], metrics["failures"]
    records = {r["room"]:r for r in metrics["rooms"]}
    assert set(records) == set(INFO)
    world = json.loads((DATA/"chapter_01_surface.json").read_text(encoding="utf-8"))
    scenes = CUT / "scenes"
    scenes.mkdir(exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",17)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",13)
    sheet = Image.new("RGB",(1120,735),"#f8efdc")
    draw = ImageDraw.Draw(sheet)
    draw.text((16,8),"CAR-ART-004 · C — Línea solar · 9 piezas nuevas · revisión humana pendiente",fill="#333d37",font=font)
    cards = []
    index = ["# CAR-ART-004 — Índice de revisión\n", "Nueve piezas nuevas: **IMPLEMENTED / TECHNICAL PASS / MANUAL_VALIDATION PENDING**. GRATE: **BLOCKED**, excluida por decisión humana. START conserva su aceptación y evidencia anterior.\n", "[Galería HTML](gallery.html) · [Lámina](evidence/contact_sheet.png) · [Métricas reales](evidence/metrics.json)\n"]
    for n,(room,(title,elements,note)) in enumerate(INFO.items()):
        record = records[room]
        assert record["rendered_skip_equal"]
        folder = evidence/room
        frames = [Image.open(args.frames/room/name).convert("RGB") for name in record["samples"]]
        frames.append(Image.open(folder/"final.png").convert("RGB"))
        frames[0].save(folder/"playback.gif",save_all=True,append_images=frames[1:],duration=[350]*(len(frames)-1)+[1200],loop=0,disposal=2)
        canonical = "LOC_FOREST1" if room=="LOC_FOREST" else room
        desc = world["locations"][canonical]["description_en"]
        source = DATA/"vector_ch01"/(room.lower()+".json")
        data = json.loads(source.read_text(encoding="utf-8"))
        text = f"""# {room} — {title}

**IMPLEMENTED / TECHNICAL PASS / MANUAL_VALIDATION PENDING**

- Identidad canónica: `{canonical}`{' y los otros 21 IDs FOREST; alias de dibujo LOC_FOREST' if room=='LOC_FOREST' else ''}.
- Fuente: `godot/data/chapter_01_surface.json → locations.{canonical}`, contrastada con el YAML por el exportador; descripción original:

> {' '.join(desc.split())}

- Elementos representados: {elements}
- Relaciones, estados y excepción de cámara: {note}
- Referencia heredada conservada: `godot/data/art_ch01.json → scenes.{room}`.
- Recurso nuevo: `godot/data/vector_ch01/{room.lower()}.json`; {len(data['lines'])} trazos, {len(data['regions'])} regiones; 736 × 400.
- Técnica: máscaras exactas respecto al raster Python, semillas interiores y regiones conectadas; sin celdas sin fondo. Playback completo y Omitir iguales píxel a píxel. Cancelación, revisita, selector runtime y TAB pasan. Los márgenes y la lectura final se inspeccionan visualmente; aceptación humana pendiente.
- Preparación gráfica: {record['prepare_seconds']:.6f} s. Dibujo: {record['playback_seconds']:.6f} s. Las cifras corresponden al equipo de captura, no son garantías.

![Final](../evidence/{room}/final.png)

[Reproducción muestreada](../evidence/{room}/playback.gif) · [Dentro de la UI real](../evidence/{room}/runtime.png) · [Volver a la galería](../gallery.html)

GIF elaborado con frames reales, paleta/tiempos aproximados y pausa final añadida; no es prueba de FPS ni igualdad exacta. El PNG y las métricas conservan la evidencia gráfica completa. Los cambios de colocación para capturas son fixtures de prueba, no viajes añadidos al juego.
"""
        (scenes/(room+".md")).write_text(text,encoding="utf-8")
        index.append(f"- [{room} — {title}](scenes/{room}.md): TECHNICAL PASS / HUMAN REVIEW PENDING.\n")
        image = Image.open(folder/"final.png").convert("RGB")
        image.thumbnail((352,192))
        x=16+(n%3)*370; y=45+(n//3)*228
        sheet.paste(image,(x,y))
        draw.text((x,y+195),room,fill="#333d37",font=small)
        cards.append(f'<article><h2>{room} — {escape(title)}</h2><p class="pending">Revisión humana pendiente · técnica PASS</p><img src="evidence/{room}/final.png" alt="Final {room}"><p>{escape(elements)}</p><details><summary>Ver reproducción real muestreada</summary><img loading="lazy" src="evidence/{room}/playback.gif" alt="Secuencia {room}"></details><p><a href="scenes/{room}.md">Ficha</a> · <a href="evidence/{room}/runtime.png">UI real</a></p><p>{escape(note)}</p></article>')
    (evidence/"contact_sheet.png").parent.mkdir(exist_ok=True)
    sheet.save(evidence/"contact_sheet.png")
    (CUT/"REVIEW.md").write_text('\n'.join(index)+"\n- LOC_GRATE: BLOCKED / no pieza nueva; selector por estado no autorizado.\n",encoding="utf-8")
    (scenes/"LOC_GRATE.md").write_text("""# LOC_GRATE — Excepción bloqueada

**BLOCKED / NOT PRODUCED**. El responsable eligió excluir esta pieza y producir las otras nueve. La reja requiere representar GRATE_CLOSED/GRATE_OPEN; el adaptador solo recibe sala. No se implementa selección por estado ni se produce una reja cerrada nueva que pudiera contradecir una apertura real.

La descripción histórica exige una depresión de veinte pies, tierra, hormigón, reja de acero horizontal y cauce seco. El fondo heredado continúa como respaldo y referencia; conserva su limitación estática anterior. No se incluye en el PASS del lote. Reanudar únicamente tras autorización del soporte técnico y revisión de los dos estados.

![Referencia heredada, no pieza CAR-ART-004](../evidence/LOC_GRATE/legacy.png)

[Volver a la galería](../gallery.html)
""",encoding="utf-8")
    html = '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CAR CH_01 — revisión vectorial</title><style>body{margin:24px;background:#f8efdc;color:#333d37;font:16px/1.5 system-ui}h1{font-size:26px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:20px}article{border:1px solid #92745a;border-radius:8px;padding:16px;background:#fffaf0}h2{font-size:19px}img{width:100%;height:auto;object-fit:contain}a{color:#265d60}.pending{color:#7c4d1c}.blocked{color:#962f26}summary{cursor:pointer}footer{margin-top:24px}</style>'
    html += '<h1>CH_01 · C — Línea solar</h1><p>1 referencia aceptada · 9 piezas nuevas pendientes de aceptación humana · 1 excepción bloqueada. Sin cambios de geografía, reglas, layout ni renderer.</p><p>GIF: muestreo de frames reales con pausa final; paleta/tiempos aproximados. PNG y métricas son la evidencia exacta. La cámara no codifica los puntos cardinales.</p><main>'
    html += '<article><h2>LOC_START — referencia aceptada</h2><p>CAR-ART-002/003 CLOSED / PASS. Evidencia anterior intacta.</p><img src="../car_art_002_vector_drawing_playback_prototype/evidence/lateral_fix_01/final.png" alt="START aceptado"><a href="../car_art_003_runtime_illustration_ui_integration_i/CHANGE.md">Registro de aceptación</a></article>'
    html += ''.join(cards)
    html += '<article><h2>LOC_GRATE — excepción</h2><p class="blocked">BLOCKED / NOT PRODUCED por decisión humana.</p><img style="image-rendering:pixelated" src="evidence/LOC_GRATE/legacy.png" alt="Reja heredada"><p>Referencia heredada estática; selección abierta/cerrada pendiente de soporte técnico autorizado.</p><a href="scenes/LOC_GRATE.md">Ficha del bloqueo</a></article></main><footer><a href="CHANGE.md">Informe del corte</a> · <a href="evidence/metrics.json">Métricas</a></footer></html>'
    (CUT/"gallery.html").write_text(html,encoding="utf-8")
    print('PASS: nine review cards, blocked GRATE card, GIFs, contact sheet and 11-entry gallery; no runtime assets edited')


if __name__=="__main__":
    main()
