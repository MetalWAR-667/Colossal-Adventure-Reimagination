"""Package CAR-ART-005's real Godot frames into a local review gallery.

Uses the same already available optional Pillow packaging dependency as
CAR-ART-004. It never edits the accepted prior gallery or runtime artwork.
"""
from pathlib import Path
import argparse
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CUT = ROOT / "project_state/changes/car_art_005_state_aware_illustration_selection_i"
EVIDENCE = CUT / "evidence"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("frames", type=Path)
    args = parser.parse_args()
    metrics = json.loads((EVIDENCE / "metrics.json").read_text(encoding="utf-8"))
    assert not metrics["failures"]
    assert {row["variant"] for row in metrics["variants"]} == {"GRATE_CLOSED", "GRATE_OPEN"}
    cards = []
    for row in metrics["variants"]:
        variant = row["variant"]
        slug = variant.lower()
        assert len(row["samples"]) >= 8
        frames = [Image.open(args.frames / variant / name).convert("RGB") for name in row["samples"]]
        frames.append(Image.open(EVIDENCE / f"{slug}_final.png").convert("RGB"))
        frames[0].save(EVIDENCE / f"{slug}_playback.gif", save_all=True,
                       append_images=frames[1:], duration=[350] * (len(frames)-1) + [1200],
                       loop=0, disposal=2)
        name = "Cerrada" if variant == "GRATE_CLOSED" else "Abierta"
        cards.append(f'''<article><h2>GRATE — {name}</h2>
<p>Variante {variant} · técnica PASS · aceptación visual pendiente.</p>
<img src="evidence/{slug}_final.png" alt="Reja {name.lower()}, final">
<details><summary>Ver LINE/FILL muestreado</summary>
<img loading="lazy" src="evidence/{slug}_playback.gif" alt="Reproducción {variant}"></details>
<p><a href="evidence/runtime_{slug}.png">Vista dentro del juego</a> ·
preparación {row['prepare_seconds']:.3f} s · reproducción {row['playback_seconds']:.3f} s.</p></article>''')
    html = '''<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CAR-ART-005 · GRATE abierta y cerrada</title>
<style>body{margin:24px;background:#f8efdc;color:#333d37;font:16px/1.5 system-ui}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:20px}
article{background:#fffaf0;border:1px solid #92745a;border-radius:8px;padding:16px}
img{display:block;width:100%;height:auto}a{color:#265d60}summary{cursor:pointer}
footer{margin-top:24px}</style>
<h1>GRATE · C — Línea solar</h1><p>Dos estados de una misma sala, seleccionados desde
GameState. Técnica verificada; revisión artística humana pendiente. Los GIF son
frames reales muestreados con paleta y tiempos aproximados; los PNG y las métricas
son la evidencia de render.</p><main>'''
    html += "\n".join(cards)
    html += '''</main><h2>Transición en el juego</h2><p>Tras UNLOCK GRATE, la sala permanece
LOC_GRATE y la reproducción sustituye la variante cerrada. Las capturas muestran
el inicio del trazado y la reja abierta más avanzada:</p>
<main><article><img src="evidence/state_transition_open_contours.png" alt="Inicio del trazado abierto"></article>
<article><img src="evidence/state_transition_open_gate.png" alt="Contornos de la reja abierta"></article></main>
<footer><a href="CHANGE.md">Informe técnico</a> ·
<a href="evidence/metrics.json">Métricas</a> ·
<a href="../car_art_004_ch01_vector_illustration_production/gallery.html">Galería anterior aceptada</a> ·
<a href="../car_art_004_ch01_vector_illustration_production/evidence/LOC_GRATE/legacy.png">Referencia heredada conservada</a></footer></html>'''
    (CUT / "gallery.html").write_text(html + "\n", encoding="utf-8")
    print("PASS: two sampled GIFs and current GRATE review gallery; CAR-ART-004 evidence untouched")


if __name__ == "__main__":
    main()
